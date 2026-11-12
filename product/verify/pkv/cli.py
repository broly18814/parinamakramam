# SPDX-License-Identifier: Apache-2.0
"""The `pkv` command.

    pkv affected [--repo PATH] [--base REF] [--json]
        Which tests could my change break, and why?
    pkv check [--repo PATH] [--base REF] [--json FILE] [--md FILE] [--no-run] ...
        The full check: pick the affected tests, run them, look for signs the
        tests were weakened, and print a receipt with one verdict.
    pkv fresh EVIDENCE.json [--repo PATH] [--rerun]
        Has the receipt been edited, and does it still match the code on disk now?
        --rerun repeats its tests in a clean copy and compares every outcome.
    pkv fingerprint [--repo PATH]
        The exact fingerprint (tree hash) of the code on disk right now.
    pkv hook install [--scope project|local|user] / pkv hook uninstall
        Add (or remove) pkv as a Claude Code Stop hook (A4). Claude Code then runs
        `pkv hook claude-stop`, which checks the work whenever Claude says it's done.

Exit codes:
    affected / fingerprint: 0 = worked, 2 = could not do the job.
    check: 0 VERIFIED, 1 FAILED, 3 UNVERIFIED, 4 SUSPICIOUS, 2 could not do the job.
        --mutate adds the mutation check: mistakes in the changed lines that the old tests
        caught but the new tests don't make the verdict SUSPICIOUS.
        --clean runs the tests in a clean copy of exactly the fingerprinted files (A3).
    fresh: 0 still matches (and reproduced, with --rerun), 1 out of date (stale),
        2 could not do the job, 3 the receipt was edited (tampered), 4 not reproduced.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .affected import Selection, select_tests
from .gitdiff import GitError, changed_files, comparison_point, repo_root, tree_hash
from .imports import build_graph
from .mutate import MAX_MUTANTS, MutationReport, mutation_check
from .report import EXIT_CODES, build_evidence, decide, render, seal, seal_status
from .runner import describe_python, run_tests
from .tamper import find_not_run, find_tampering


def _print_affected(sel: Selection, base: str | None) -> None:
    out = print
    out(f"Parinama Verify {__version__}: which tests could this change affect?")
    out(f"Compared with: {base or 'your last commit (HEAD)'}\n")
    if not sel.changes:
        out("No changes found. Nothing to check.")
        return
    out(f"Changed files ({len(sel.changes)}):")
    for c in sel.changes:
        extra = f" (from {c['old_path']})" if c.get("old_path") else ""
        out(f"  {c['status']:<9} {c['path']}{extra}")
    out("")
    if sel.run_all:
        out("Every test must run, because:")
        for r in sel.run_all_reasons:
            out(f"  - {r}")
        out("")
    out(f"Tests to run: {len(sel.tests)} of {len(sel.all_tests)}")
    if not sel.run_all:
        for t in sel.tests:
            out(f"  {t}")
            out(f"      why: {sel.reasons[t]}")
    if sel.tests:
        cmd = "python -m pytest " + " ".join(shlex.quote(t) for t in sel.tests)
        out(f"\nTo run them yourself:\n  {cmd}")
    warnings = []
    for t in sel.removed_tests:
        warnings.append(f"test file deleted: {t} (check this was intended)")
    for f, err in sel.unreadable.items():
        warnings.append(f"could not read {f} ({err})")
    for f in sel.dynamic_imports:
        warnings.append(f"{f} loads code by name at run time; links from it may be missed")
    if warnings:
        out("\nWarnings:")
        for w in warnings:
            out(f"  ! {w}")
    if sel.no_effect:
        out(f"\nIgnored (cannot change what code does): {', '.join(sel.no_effect)}")
    out("\nNothing was run. This version only selects tests.")


def _check(args: argparse.Namespace) -> int:
    root = repo_root(args.repo)
    # Receipt files we are about to write are not part of the user's change.
    receipts = [r for r in (_inside(root, f) for f in (args.json, args.md) if f) if r]
    ref = comparison_point(root, args.base)
    changes = [c for c in changed_files(root, args.base) if c.path not in receipts]
    graph = build_graph(root)  # one map of the code, shared by every step below
    sel = select_tests(root, changes, graph)
    findings = find_tampering(root, changes, ref, graph)
    run = None
    if sel.tests and not args.no_run:
        run = run_tests(root, sel.tests, timeout=args.timeout, python=args.python,
                        keep_env=args.keep_env, exclude=tuple(receipts), clean=args.clean)
        # Only meaningful if pytest collected and ran tests normally. With "no tests
        # collected" pytest writes no per-file entries, and that case is already
        # UNVERIFIED for its own, more accurate reason.
        if run.outcome in ("passed", "failed"):
            findings += find_not_run(root, sel.tests, run.executed, changes, ref, graph)
    mutation: MutationReport | None = None
    if args.mutate and run is not None and run.outcome == "passed":
        mutation = mutation_check(root, ref, changes, sel, python=args.python, keep_env=args.keep_env,
                                  max_mutants=args.mutants)
        findings += mutation.findings()
    verdict, reasons = decide(sel, run, findings, ran_requested=not args.no_run)
    ev = build_evidence(root=root, base=args.base, ref=ref, version=__version__, sel=sel,
                        run=run, findings=findings, verdict=verdict, reasons=reasons,
                        tree_hash_now=run.tree_hash_after if run
                        else tree_hash(root, exclude=tuple(receipts)))
    ev["receipt_files"] = receipts
    ev["mutation"] = mutation.to_dict() if mutation else None
    ev["environment"] = describe_python(run.python) if run else None
    seal(ev)  # last: every field above is covered by the seal
    text = render(ev)
    print(text, end="")
    for f in (args.json, args.md):
        if f:
            Path(f).parent.mkdir(parents=True, exist_ok=True)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(ev, fh, indent=2, sort_keys=True)
    if args.md:
        with open(args.md, "w", encoding="utf-8") as fh:
            fh.write(text)
    return EXIT_CODES[verdict]


def _inside(root: Path, f: str) -> str | None:
    """f as a path relative to the project, or None if it's outside."""
    try:
        return Path(f).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return None


def _fresh(args: argparse.Namespace) -> int:
    try:
        with open(args.evidence, encoding="utf-8") as fh:
            ev = json.load(fh)
        recorded = ev["tree_hash"]
    except (OSError, ValueError, KeyError) as e:
        print(f"pkv: cannot read the receipt {args.evidence}: {e}", file=sys.stderr)
        return 2
    status = seal_status(ev)
    if status == "tampered":
        print("TAMPERED: this receipt was changed after pkv wrote it (its seal doesn't match its contents). "
              "Don't trust it; run pkv check again.")
        return 3
    if status == "unsealed":
        print("Note: this receipt has no seal (made by pkv 0.2 or older), so edits to it can't be detected.")
    root = repo_root(args.repo)
    skip = list(ev.get("receipt_files", []))
    own = _inside(root, args.evidence)
    if own:
        skip.append(own)
    now = tree_hash(root, exclude=tuple(skip))
    if now != recorded:
        print(f"STALE: the code has changed since this receipt was made ({ev.get('created_at')}). "
              f"Its verdict ({ev.get('verdict')}) no longer applies. Run pkv check again.")
        return 1
    print(f"FRESH: the receipt ({ev.get('verdict')}, made {ev.get('created_at')}) "
          "matches the code exactly as it is now" + (", and its seal is intact." if status == "intact" else "."))
    if not args.rerun:
        return 0
    return _rerun(args, root, ev, tuple(skip))


def _rerun(args: argparse.Namespace, root: Path, ev: dict[str, Any], skip: tuple[str, ...]) -> int:
    """Repeat the receipt's tests in a clean copy of the recorded code; compare every outcome (A3)."""
    old = ev.get("run")
    tests = ev.get("selection", {}).get("tests", [])
    if not old or not tests:
        print("Nothing to re-run: this receipt records no test run.")
        return 0
    python = args.python or (old.get("python") if old.get("python") and Path(old["python"]).exists() else None)
    new = run_tests(root, tests, timeout=args.timeout, python=python, keep_env=args.keep_env,
                    exclude=skip, clean=True)
    before = {(c, n): o for c, n, o in old.get("executed", [])}
    after = {(c, n): o for c, n, o in new.executed}
    differ = sorted(k for k in before.keys() | after.keys() if before.get(k) != after.get(k))
    where = old.get("where", "working folder")
    print(f"Re-ran {len(tests)} test file(s) in a clean copy (recorded run: {where}): "
          f"recorded {old.get('outcome')}, now {new.outcome}.")
    if not differ and new.outcome == old.get("outcome") and not new.changed_during_run:
        print(f"REPRODUCED: all {len(after)} test outcomes are the same.")
        return 0
    print(f"NOT REPRODUCED: {len(differ)} test(s) ended differently"
          + (" (and files changed during the re-run)" if new.changed_during_run else "") + ":")
    for c, n in differ[:20]:
        print(f"  {c}::{n}: recorded {before.get((c, n), 'not run')}, now {after.get((c, n), 'not run')}")
    return 4


def _hook(args: argparse.Namespace) -> int:
    from . import hook

    if args.hook_command == "claude-stop":
        code, out = hook.claude_stop(sys.stdin.read(), base=args.base, timeout=args.timeout, python=args.python)
        if out:
            print(out)
        return code
    path = hook.settings_path(args.scope, hook.install_root(args.repo))
    if args.hook_command == "install":
        changed = hook.install(path)
        print(f"pkv's Stop hook {'added to' if changed else 'is already in'} {path}. "
              "Claude Code will now check the work with pkv whenever Claude says it's done.")
    else:
        changed = hook.uninstall(path)
        print(f"pkv's Stop hook {'removed from' if changed else 'was not in'} {path}.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pkv", description="Independent checks for AI-written (or any) code changes."
    )
    parser.add_argument("--version", action="version", version=f"pkv {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("affected", help="which tests could this change break?")
    a.add_argument("--repo", default=".", help="project folder (default: current)")
    a.add_argument("--base", default=None,
                   help="compare with this branch or commit (default: your last commit)")
    a.add_argument("--json", action="store_true", help="machine-readable output")
    c = sub.add_parser("check", help="run the affected tests, look for tampering, give a verdict")
    c.add_argument("--repo", default=".")
    c.add_argument("--base", default=None)
    c.add_argument("--json", metavar="FILE", help="save the receipt as JSON (for pkv fresh)")
    c.add_argument("--md", metavar="FILE", help="save the receipt as Markdown")
    c.add_argument("--no-run", action="store_true", help="select and inspect only; don't run tests")
    c.add_argument("--timeout", type=float, default=600, help="seconds before tests are stopped")
    c.add_argument("--python", default=None, help="Python to run the tests with")
    c.add_argument("--keep-env", action="append", default=[], metavar="NAME",
                   help="pass this environment variable to the tests (repeatable)")
    c.add_argument("--clean", action="store_true",
                   help="run the tests in a clean copy of exactly the fingerprinted files, outside the project")
    c.add_argument("--mutate", action="store_true",
                   help="also check the tests still catch small mistakes in the changed lines (slower)")
    c.add_argument("--mutants", type=int, default=MAX_MUTANTS, metavar="N",
                   help=f"at most N mistakes to try with --mutate (default {MAX_MUTANTS})")
    fr = sub.add_parser("fresh", help="does a saved receipt still match the code?")
    fr.add_argument("evidence")
    fr.add_argument("--repo", default=".")
    fr.add_argument("--rerun", action="store_true",
                    help="also repeat the receipt's tests in a clean copy and compare every outcome")
    fr.add_argument("--python", default=None, help="Python to re-run the tests with")
    fr.add_argument("--timeout", type=float, default=600, help="seconds before the re-run is stopped")
    fr.add_argument("--keep-env", action="append", default=[], metavar="NAME",
                    help="pass this environment variable to the tests (repeatable)")
    f = sub.add_parser("fingerprint", help="fingerprint of the code on disk now")
    f.add_argument("--repo", default=".")
    h = sub.add_parser("hook", help="use pkv as a Claude Code hook (A4)")
    hsub = h.add_subparsers(dest="hook_command", required=True)
    for name, text in (("install", "add pkv's Stop hook to Claude Code's settings"),
                       ("uninstall", "remove pkv's Stop hook from Claude Code's settings")):
        hp = hsub.add_parser(name, help=text)
        hp.add_argument("--scope", choices=["project", "local", "user"], default="project",
                        help="project: .claude/settings.json (shared); local: .claude/settings.local.json; "
                             "user: ~/.claude/settings.json")
        hp.add_argument("--repo", default=".")
    cs = hsub.add_parser("claude-stop", help="what Claude Code runs when Claude stops (reads its JSON on stdin)")
    cs.add_argument("--base", default=None)
    cs.add_argument("--timeout", type=float, default=300)
    cs.add_argument("--python", default=None)
    args = parser.parse_args(argv)
    if args.command == "hook":
        return _hook(args)

    try:
        if args.command == "fingerprint":
            print(tree_hash(args.repo))
            return 0
        if args.command == "check":
            return _check(args)
        if args.command == "fresh":
            return _fresh(args)
        root = repo_root(args.repo)
        sel = select_tests(root, changed_files(root, args.base))
    except GitError as e:
        print(f"pkv: {e}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(sel.to_dict(), indent=2, sort_keys=True))
    else:
        _print_affected(sel, args.base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

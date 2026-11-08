"""The `pkv` command.

    pkv affected [--repo PATH] [--base REF] [--json]
        Which tests could my change break, and why?
    pkv check [--repo PATH] [--base REF] [--json FILE] [--md FILE] [--no-run] ...
        The full check: pick the affected tests, run them, look for signs the
        tests were weakened, and print a receipt with one verdict.
    pkv fresh EVIDENCE.json [--repo PATH]
        Does a saved receipt still match the code on disk now?
    pkv fingerprint [--repo PATH]
        The exact fingerprint (tree hash) of the code on disk right now.

Exit codes:
    affected / fingerprint: 0 = worked, 2 = could not do the job.
    check: 0 VERIFIED, 1 FAILED, 3 UNVERIFIED, 4 SUSPICIOUS, 2 could not do the job.
    fresh: 0 still matches, 1 out of date (stale), 2 could not do the job.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path

from . import __version__
from .affected import Selection, select_tests
from .gitdiff import GitError, changed_files, comparison_point, repo_root, tree_hash
from .report import EXIT_CODES, build_evidence, decide, render
from .runner import run_tests
from .tamper import find_tampering


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
    sel = select_tests(root, changes)
    findings = find_tampering(root, changes, ref)
    run = None
    if sel.tests and not args.no_run:
        run = run_tests(root, sel.tests, timeout=args.timeout, python=args.python,
                        keep_env=args.keep_env, exclude=tuple(receipts))
    verdict, reasons = decide(sel, run, findings, ran_requested=not args.no_run)
    ev = build_evidence(root=root, base=args.base, ref=ref, version=__version__, sel=sel,
                        run=run, findings=findings, verdict=verdict, reasons=reasons,
                        tree_hash_now=run.tree_hash_after if run
                        else tree_hash(root, exclude=tuple(receipts)))
    ev["receipt_files"] = receipts
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
    root = repo_root(args.repo)
    skip = list(ev.get("receipt_files", []))
    own = _inside(root, args.evidence)
    if own:
        skip.append(own)
    now = tree_hash(root, exclude=tuple(skip))
    if now == recorded:
        print(f"FRESH: the receipt ({ev.get('verdict')}, made {ev.get('created_at')}) "
              "matches the code exactly as it is now.")
        return 0
    print(f"STALE: the code has changed since this receipt was made ({ev.get('created_at')}). "
          f"Its verdict ({ev.get('verdict')}) no longer applies. Run pkv check again.")
    return 1


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
    fr = sub.add_parser("fresh", help="does a saved receipt still match the code?")
    fr.add_argument("evidence")
    fr.add_argument("--repo", default=".")
    f = sub.add_parser("fingerprint", help="fingerprint of the code on disk now")
    f.add_argument("--repo", default=".")
    args = parser.parse_args(argv)

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

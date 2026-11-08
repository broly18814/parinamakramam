"""The `pkv` command.

    pkv affected [--repo PATH] [--base REF] [--json]
        Which tests could my change break, and why?
    pkv fingerprint [--repo PATH]
        The exact fingerprint (tree hash) of the code on disk right now.

Exit codes: 0 = worked, 2 = could not do the job (for example, not a git repo).
Running the tests and catching tampering come in the next versions.
"""

from __future__ import annotations

import argparse
import json
import shlex
import sys

from . import __version__
from .affected import select_tests
from .gitdiff import GitError, changed_files, repo_root, tree_hash


def _print_affected(sel, base: str | None) -> None:
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
    f = sub.add_parser("fingerprint", help="fingerprint of the code on disk now")
    f.add_argument("--repo", default=".")
    args = parser.parse_args(argv)

    try:
        if args.command == "fingerprint":
            print(tree_hash(args.repo))
            return 0
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

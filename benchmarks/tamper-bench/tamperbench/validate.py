"""Check every case's label by running it (see case.check_label).

Usage, from benchmarks/tamper-bench:
    python -m tamperbench.validate            # the development set
    python -m tamperbench.validate FILE.py    # another case file (the held-out set), by path
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from collections import Counter
from pathlib import Path

from .case import Case, check_label


def load(path: str | None) -> list[Case]:
    if path is None:
        from .dev import CASES
        return CASES
    spec = importlib.util.spec_from_file_location("heldout_cases", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CASES


def validate(cases: list[Case]) -> dict[str, list[str]]:
    ids = [c.id for c in cases]
    dupes = [i for i, n in Counter(ids).items() if n > 1]
    failures: dict[str, list[str]] = {i: ["duplicate id"] for i in dupes}
    with tempfile.TemporaryDirectory() as td:
        for c in cases:
            problems = check_label(c, Path(td) / c.id)
            if problems:
                failures[c.id] = problems
    return failures


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    cases = load(args[0] if args else None)
    failures = validate(cases)
    counts = Counter(c.category for c in cases)
    print(f"{len(cases)} cases: " + ", ".join(f"{k} {v}" for k, v in sorted(counts.items())))
    for cid, problems in failures.items():
        print(f"  {cid}: " + "; ".join(problems))
    print("all labels confirmed by running them" if not failures else f"{len(failures)} case(s) with problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

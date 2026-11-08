"""Run EXP-005 (docs/research/EXP-005-design.md): building blocks from real code history.

Reads each project's code only through git (`git ls-tree`, `git show`):
nothing is checked out, installed or executed. Writes one JSON file per
project with every test function's size before and after rewriting with each
library, plus the most-used blocks in normalised form.

Usage (WORK holds clones made by product/verify/realworld/run_real.py setup):
    python3 run_exp005.py --set calibration --work WORK --other-calibration PATH --out DIR
    python3 run_exp005.py --set evaluation  --work WORK --out DIR
"""
from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path, PurePosixPath

from pevo.codeblocks import build_corpus, functions, learn, random_library, rewrite_size, size

PROJECTS = json.loads((Path(__file__).resolve().parents[2] / "product/verify/realworld/projects.json").read_text())
PINNED = {p["name"]: p["commit"] for p in PROJECTS}
# Registered split commits (EXP-005-design.md, section 2).
EVALUATION = {"click": "8c1a0a7abb", "more-itertools": "51c42ff83f", "boltons": "6cac49ce4e"}
CALIBRATION = "tomli"
CALIBRATION_MIN_NEW = 15
EVAL_MIN_NEW = 50


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True).stdout


def included(path: str) -> bool:
    """The registered rule: .py files, except tests and docs/benchmark/scripts folders."""
    p = PurePosixPath(path)
    if p.suffix != ".py":
        return False
    if any(part in ("test", "tests") for part in p.parts[:-1]) or p.name.startswith("test_"):
        return False
    first = p.parts[0] if p.parts else ""
    return not (first == "docs" or first.startswith("benchmark") or first == "scripts")


def snapshot(repo: Path, rev: str) -> dict:
    """{(path, qualified name): normalised tree} for every included function."""
    out = {}
    for path in git(repo, "ls-tree", "-r", "--name-only", rev).split():
        if not included(path):
            continue
        try:
            for qual, tree in functions(git(repo, "show", f"{rev}:{path}")):
                out[(path, qual)] = tree
        except SyntaxError:
            continue
    return out


def find_split(repo: Path, pin: str, min_new: int) -> str:
    """The registered rule: walk first-parent history back 10 commits at a time to the
    first point with at least `min_new` functions added after it."""
    revs = git(repo, "rev-list", "--first-parent", pin).split()
    now = snapshot(repo, pin)
    for i in range(10, len(revs), 10):
        if sum(1 for k in now if k not in snapshot(repo, revs[i])) >= min_new:
            return revs[i]
    raise SystemExit(f"{repo.name}: never reaches {min_new} new functions")


def evaluate(name: str, repo: Path, split: str, other_trees: list, k: int, max_size: int) -> dict:
    t0 = time.perf_counter()
    split = git(repo, "rev-parse", split).strip()
    past, now = snapshot(repo, split), snapshot(repo, PINNED[name])
    test = {key: t for key, t in now.items() if key not in past}
    train_trees = list(past.values())
    own_corpus = build_corpus(train_trees, max_size)
    libraries = {
        "OWN": learn(own_corpus, k),
        "RANDOM": random_library(own_corpus, k, seed=0),
        "OTHER": learn(build_corpus(other_trees, max_size), k),
        "ORACLE": learn(build_corpus(list(test.values()), max_size), k),
    }
    rows = []
    for (path, qual), tree in sorted(test.items()):
        row = {"path": path, "function": qual, "size": size(tree)}
        for cond, lib in libraries.items():
            row[cond] = rewrite_size(tree, lib)
        rows.append(row)
    return {
        "project": name, "split": split, "pinned": PINNED[name],
        "split_date": git(repo, "log", "-1", "--format=%cs", split).strip(),
        "train_functions": len(past), "train_size": sum(size(t) for t in train_trees),
        "test_functions": len(test), "k": k, "max_size": max_size,
        "libraries": {c: {"blocks": len(lib),
                          "top": [{"shape": b.example, "size": b.size, "holes": b.holes,
                                   "uses_in_training": b.uses_in_training} for b in lib[:10]]}
                      for c, lib in libraries.items()},
        "rows": rows,
        "seconds": round(time.perf_counter() - t0, 1),
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", choices=["calibration", "evaluation"], required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--other-calibration", type=Path, help="calibration only: a clone used as OTHER")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--k", type=int, default=50)
    ap.add_argument("--max-size", type=int, default=40)
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    src = a.work / "src"
    if a.set == "calibration":
        repo = src / CALIBRATION
        split = find_split(repo, PINNED[CALIBRATION], CALIBRATION_MIN_NEW)
        if a.other_calibration is None:
            raise SystemExit("--other-calibration is required for the calibration set")
        other = list(snapshot(a.other_calibration, "HEAD").values())
        res = evaluate(CALIBRATION, repo, split, other, a.k, a.max_size)
        (a.out / f"{CALIBRATION}.json").write_text(json.dumps(res, indent=1) + "\n")
        print(f"{CALIBRATION}: {res['train_functions']} past / {res['test_functions']} new functions, "
              f"{res['seconds']} s")
        return
    pasts = {n: list(snapshot(src / n, git(src / n, "rev-parse", s).strip()).values()) for n, s in EVALUATION.items()}
    for name, split in EVALUATION.items():
        other = [t for o, trees in pasts.items() if o != name for t in trees]
        res = evaluate(name, src / name, split, other, a.k, a.max_size)
        (a.out / f"{name}.json").write_text(json.dumps(res, indent=1) + "\n")
        print(f"{name}: {res['train_functions']} past / {res['test_functions']} new functions, {res['seconds']} s")


if __name__ == "__main__":
    main()

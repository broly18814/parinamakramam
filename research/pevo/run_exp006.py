"""Run EXP-006 (docs/research/EXP-006-design.md): does a library of building blocks
learned from a project's past make search for its future code cheaper?

Reads each project's code only through git (`git ls-tree`, `git show`):
nothing is checked out, installed or executed. Writes one JSON file per project
with, for every hidden piece (task), the effort each condition needed to find
it (or null), plus EXP-005's compression numbers on the same project (R13).

Usage (WORK/src holds plain clones: git clone URL WORK/src/NAME):
    python3 run_exp006.py --set calibration --work WORK --out DIR --budget 50000
    python3 run_exp006.py --set evaluation  --work WORK --out DIR --budget B

Each search runs to 5 x budget, so one run gives the outcome at every smaller budget.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import platform
import subprocess
import time
from pathlib import Path

import run_exp005 as r5
from pevo.codeblocks import build_corpus, learn, random_library, rewrite_size, size
from pevo.grammarsearch import Grammar, Grammar2, Task, base_templates, library_blocks, sample_tasks, search

K, MAX_PATTERN = 50, 40                     # EXP-005's frozen settings (D-036), unchanged
CONDITIONS = ["NONE", "OWN", "RANDOM", "OTHER", "ORACLE", "CTX2"]
LIBRARIES = ["OWN", "RANDOM", "OTHER", "ORACLE"]
# Registered in EXP-006-design.md, section 3 (evaluation) and section 6 (calibration).
PROJECTS = {
    "packaging": {"url": "https://github.com/pypa/packaging.git", "licence": "Apache-2.0 OR BSD-2-Clause",
                  "pin": "843887fd431f8b3c10f1b39e1d4066ba3516147c",
                  "split": "d2fa92384821919d48eab89bae087b950637d52a"},
    "urllib3": {"url": "https://github.com/urllib3/urllib3.git", "licence": "MIT",
                "pin": "c5347bbd39203d68d7b0e3ffb83ced3e3b4b9109",
                "split": "6ec2a1d36872a583aa32c54e345633aae1c332d6"},
    "httpx": {"url": "https://github.com/encode/httpx.git", "licence": "BSD-3-Clause",
              "pin": "b5addb64f0161ff6bfe94c124ef76f6a1fba5254",
              "split": "0088253b32c7e6541ce85f40429f133c01ca35dc"},
    "tomli": {"url": "https://github.com/hukkin/tomli.git", "licence": "MIT",
              "pin": "43a86ade8b795c6ef9b4ec53372a607cd1ed426f",
              "split": "c00fbc1f82d31292c21c65cb252c5e6e5b05d3b1"},
    "humanize": {"url": "https://github.com/python-humanize/humanize.git", "licence": "MIT",
                 "pin": "d16e6352c9785c5ab86de0133222bd22e89b0db2", "split": None},
}
EVALUATION = ["packaging", "urllib3", "httpx"]
CALIBRATION, CALIBRATION_OTHER = "tomli", "humanize"

_GRAMMARS: dict = {}                         # per worker process: (project, condition) -> grammar


def _job(job: tuple) -> tuple:
    """One worker job: one project, one condition, one slice of its tasks."""
    project, cond, chunk, past, blocks, tasks, budget = job
    t0 = time.perf_counter()
    g = _GRAMMARS.get((project, cond))
    if g is None:
        g = Grammar2(Grammar(past), past) if cond == "CTX2" else Grammar(past, blocks)
        _GRAMMARS[(project, cond)] = g
    built = time.perf_counter()
    out = []
    for t in tasks:
        if not t.derivable:
            out.append((None, False))
        else:
            out.append(search(g, t.ctx2 if cond == "CTX2" else t.ctx, t.kind, t.target, budget))
    return project, cond, chunk, out, round(built - t0, 2), round(time.perf_counter() - built, 2)


def prepare(name: str, src: Path, other_trees: list, max_target: int) -> dict:
    """Past/future split, the four libraries, EXP-005's compression rows, and the tasks."""
    p, repo = PROJECTS[name], src / name
    past, now = r5.snapshot(repo, p["split"]), r5.snapshot(repo, p["pin"])
    future = {k: t for k, t in now.items() if k not in past}
    past_trees = list(past.values())
    t0 = time.perf_counter()
    own_c = build_corpus(past_trees, MAX_PATTERN)
    other_c = build_corpus(other_trees, MAX_PATTERN)
    oracle_c = build_corpus(list(future.values()), MAX_PATTERN)
    libs = {"OWN": (learn(own_c, K), own_c), "RANDOM": (random_library(own_c, K, seed=0), own_c),
            "OTHER": (learn(other_c, K), other_c), "ORACLE": (learn(oracle_c, K), oracle_c)}
    learn_seconds = round(time.perf_counter() - t0, 2)
    compression = []
    for (path, qual), tree in sorted(future.items()):
        row = {"path": path, "function": qual, "size": size(tree)}
        for c in LIBRARIES:
            row[c] = rewrite_size(tree, libs[c][0])
        compression.append(row)
    inventory = {t for tree in past_trees for t in base_templates(tree)}
    return {
        "name": name, "past": past_trees, "future_keys": sorted(future),
        "tasks": sample_tasks(future, inventory, max_size=max_target),
        "blocks": {c: library_blocks(lib, corpus) for c, (lib, corpus) in libs.items()},
        "meta": {
            "project": name, "url": p["url"], "licence": p["licence"], "pinned": p["pin"], "split": p["split"],
            "split_date": r5.git(repo, "log", "-1", "--format=%cs", p["split"]).strip(),
            "past_functions": len(past), "future_functions": len(future),
            "past_size": sum(size(t) for t in past_trees),
            "learn_seconds": learn_seconds,
            "libraries": {c: {"blocks": len(lib),
                              "top": [{"shape": b.example, "size": b.size, "holes": b.holes,
                                       "uses_in_training": b.uses_in_training} for b in lib[:10]]}
                          for c, (lib, _corpus) in libs.items()},
        },
        "compression": compression,
    }


def _task_record(t: Task, results: dict) -> dict:
    return {"path": t.path, "function": t.function, "size": t.size, "kind": t.kind,
            "context": list(t.ctx), "derivable": t.derivable,
            "effort": {c: results[c][0] for c in CONDITIONS},
            "used_block": {c: results[c][1] for c in LIBRARIES}}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", choices=["calibration", "evaluation"], required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--budget", type=int, required=True, help="the primary budget B; each search runs to 5 x B")
    ap.add_argument("--max-target-size", type=int, default=12)
    ap.add_argument("--jobs", type=int, default=max(1, (multiprocessing.cpu_count() or 2) - 2))
    ap.add_argument("--chunk", type=int, default=60, help="tasks per worker job")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    src = a.work / "src"
    for name in [CALIBRATION, CALIBRATION_OTHER] if a.set == "calibration" else EVALUATION:
        head = r5.git(src / name, "rev-parse", "HEAD").strip()
        if PROJECTS[name]["split"] is not None:
            r5.git(src / name, "cat-file", "-e", PROJECTS[name]["split"])
        if head != PROJECTS[name]["pin"]:
            print(f"note: {name} clone is at {head[:10]}, the registered pin is {PROJECTS[name]['pin'][:10]}; "
                  "the pin is what is read")

    t0 = time.perf_counter()
    if a.set == "calibration":
        other = list(r5.snapshot(src / CALIBRATION_OTHER, PROJECTS[CALIBRATION_OTHER]["pin"]).values())
        prepared = [prepare(CALIBRATION, src, other, a.max_target_size)]
    else:
        pasts = {n: list(r5.snapshot(src / n, PROJECTS[n]["split"]).values()) for n in EVALUATION}
        prepared = [prepare(n, src, [t for o in EVALUATION if o != n for t in pasts[o]], a.max_target_size)
                    for n in EVALUATION]
    print(f"prepared {len(prepared)} project(s) in {time.perf_counter() - t0:.0f} s")

    budget_max = 5 * a.budget
    jobs = []
    for pr in prepared:
        tasks = pr["tasks"]
        for cond in CONDITIONS:
            blocks = pr["blocks"].get(cond, [])
            for k in range(0, len(tasks), a.chunk):
                jobs.append((pr["name"], cond, k // a.chunk, pr["past"], blocks, tasks[k:k + a.chunk], budget_max))
    results: dict = {}
    seconds: dict = {}
    with multiprocessing.get_context("spawn").Pool(a.jobs) as pool:
        for project, cond, chunk, out, build_s, search_s in pool.imap_unordered(_job, jobs):
            results[(project, cond, chunk)] = out
            s = seconds.setdefault(project, {}).setdefault(cond, {"build_max": 0.0, "search": 0.0})
            s["build_max"] = max(s["build_max"], build_s)
            s["search"] = round(s["search"] + search_s, 2)
            print(f"  {project:10s} {cond:6s} chunk {chunk:2d}: {sum(e is not None for e, _u in out):3d}"
                  f"/{len(out)} found, {search_s:7.1f} s")

    here = Path(__file__).parent
    code = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=here)
    dirty = subprocess.run(["git", "status", "--porcelain", "--", "."], capture_output=True, text=True, cwd=here)
    for pr in prepared:
        name, tasks = pr["name"], pr["tasks"]
        per_cond = {c: [x for k in range(0, len(tasks), a.chunk) for x in results[(name, c, k // a.chunk)]]
                    for c in CONDITIONS}
        records = [_task_record(t, {c: per_cond[c][i] for c in CONDITIONS}) for i, t in enumerate(tasks)]
        doc = {**pr["meta"], "set": a.set, "budget": a.budget, "budget_max": budget_max,
               "max_target_size": a.max_target_size, "k": K, "max_pattern_size": MAX_PATTERN,
               "tasks_total": len(tasks), "tasks_derivable": sum(t.derivable for t in tasks),
               "seconds": seconds.get(name, {}), "python": platform.python_version(),
               "code_commit": code.stdout.strip(), "code_uncommitted_changes": bool(dirty.stdout.strip()),
               "compression": pr["compression"], "tasks": records}
        (a.out / f"{name}.json").write_text(json.dumps(doc, indent=1) + "\n")
        print(f"{name}: {len(tasks)} tasks ({doc['tasks_derivable']} derivable), "
              f"{pr['meta']['past_functions']} past / {pr['meta']['future_functions']} future functions")
    print(f"total {time.perf_counter() - t0:.0f} s")


if __name__ == "__main__":
    main()

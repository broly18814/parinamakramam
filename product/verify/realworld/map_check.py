"""REAL-005: is `pkv map` right? (docs/product/A5-design.md)

For each project, each test file is run alone, in its own process. A small pytest plugin records
which of the project's own .py files Python really loaded (the *runtime set*). pkv's map says which
files that test file reaches, without running anything (the *map set*). We compare the two.

Usage:
    python map_check.py setup --work DIR     # clone the two unseen projects; make their environments
    python map_check.py run --work DIR       # measure all six; write results/map/
Only facts about pkv's answers are saved here, never the projects' code.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from pkv.map import build_map  # noqa: E402

SEEN = json.loads((HERE / "projects.json").read_text())
UNSEEN = [
    {"name": "toolz", "url": "https://github.com/pytoolz/toolz.git", "licence": "BSD-3-Clause",
     "commit": "451af60dec590a6010e2babdbf391ea8f815122f"},
    {"name": "sortedcontainers", "url": "https://github.com/grantjenks/python-sortedcontainers.git",
     "licence": "Apache-2.0", "commit": "3ac358631f58c1347f1d6d2d92784117db0f38ed"},
]
TEST_PACKAGES = ["pytest>=8.3,<8.4", "python-dateutil"]  # REAL-003 round B's environment
TIMEOUT_S = 300
RESULTS = HERE / "results" / "map"

TRACER = '''
import os, sys
ROOT = os.path.realpath(os.environ["PKV_TRACE_ROOT"])

def pytest_unconfigure(config):
    seen = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if not f or not f.endswith(".py"):
            continue
        f = os.path.realpath(f)
        if os.path.commonpath([f, ROOT]) == ROOT:
            seen.add(os.path.relpath(f, ROOT).replace(os.sep, "/"))
    with open(os.environ["PKV_TRACE_OUT"], "w") as fh:
        fh.write("\\n".join(sorted(seen)))
'''


def sh(*args: str, cwd: Path | None = None) -> None:
    subprocess.run(args, cwd=cwd, check=True)


def paths(work: Path, name: str) -> tuple[Path, Path]:
    return work / "src" / name, work / "venvs" / name / "bin" / "python"


def setup(work: Path) -> None:
    for p in UNSEEN:
        repo, py = paths(work, p["name"])
        if not repo.exists():
            sh("git", "clone", "-q", "--filter=blob:none", p["url"], str(repo))
        sh("git", "-C", str(repo), "checkout", "-q", "--detach", "-f", p["commit"])
        if not py.exists():
            sh("uv", "venv", "-q", "--python", "3.12", str(py.parent.parent))
        sh("uv", "pip", "install", "-q", "--python", str(py), "-e", ".", *TEST_PACKAGES, cwd=repo)


def runtime_set(repo: Path, py: Path, test: str, tracer_dir: Path) -> tuple[set[str], int]:
    out = tracer_dir / "loaded.txt"
    out.unlink(missing_ok=True)
    env = {k: os.environ[k] for k in ("PATH", "HOME", "LANG", "TMPDIR") if k in os.environ}
    env.update(PYTHONPATH=str(tracer_dir), PKV_TRACE_ROOT=str(repo), PKV_TRACE_OUT=str(out),
               PYTHONDONTWRITEBYTECODE="1")
    try:
        r = subprocess.run([str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", "-p", "_pkv_trace",
                            "--", test], cwd=repo, env=env, capture_output=True, timeout=TIMEOUT_S)
        code = r.returncode
    except subprocess.TimeoutExpired:
        code = -9
    loaded = set(out.read_text().split("\n")) - {""} if out.exists() else set()
    return loaded, code


def measure(work: Path, p: dict[str, Any], group: str) -> dict[str, Any]:
    repo, py = paths(work, p["name"])
    subprocess.run(["git", "-C", str(repo), "checkout", "-q", "--detach", "-f", p["commit"]], check=True)
    t0 = time.monotonic()
    m = build_map(repo)
    map_seconds = round(time.monotonic() - t0, 2)
    known = set(m.kinds)
    rows = []
    runtime_reached: set[str] = set()
    with tempfile.TemporaryDirectory() as td:
        tracer_dir = Path(td)
        (tracer_dir / "_pkv_trace.py").write_text(TRACER)
        for t in m.tests:
            loaded, code = runtime_set(repo, py, t, tracer_dir)
            ignored_loaded = sorted(loaded - known)  # e.g. generated files git ignores: outside the map
            run = loaded & known
            mapped = m.reach[t]
            runtime_reached |= run
            rows.append({"test": t, "pytest_exit": code, "runtime": len(run), "map": len(mapped),
                         "both": len(run & mapped), "misses": sorted(run - mapped),
                         "extras": len(mapped - run), "ignored_loaded": ignored_loaded})
    false_untested = sorted(f for f in m.unreached() if f in runtime_reached)
    tot = {k: sum(r[k] for r in rows) for k in ("runtime", "map", "both")}
    return {"project": p["name"], "group": group, "commit": p["commit"], "licence": p["licence"],
            "map_seconds": map_seconds, "test_files": len(rows), "code_files": len(m.code),
            "dynamic_import_files": sorted(f for f in m.graph.dynamic if f in known),
            **tot, "recall": round(tot["both"] / tot["runtime"], 4) if tot["runtime"] else None,
            "precision": round(tot["both"] / tot["map"], 4) if tot["map"] else None,
            "false_untested": false_untested, "tests": rows}


def run(work: Path) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    for group, projects in (("seen", SEEN), ("unseen", UNSEEN)):
        for p in projects:
            res = measure(work, p, group)
            (RESULTS / f"{p['name']}.json").write_text(json.dumps(res, indent=1) + "\n")
            misses = sum(len(r["misses"]) for r in res["tests"])
            print(f"{group:6} {p['name']:16} tests {res['test_files']:3}  recall {res['recall']}  "
                  f"precision {res['precision']}  misses {misses}  false-untested {len(res['false_untested'])}  "
                  f"map {res['map_seconds']} s", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["setup", "run"])
    ap.add_argument("--work", type=Path, required=True)
    a = ap.parse_args()
    setup(a.work) if a.command == "setup" else run(a.work)


if __name__ == "__main__":
    main()

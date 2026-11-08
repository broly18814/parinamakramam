# SPDX-License-Identifier: Apache-2.0
"""REAL-001: replay real projects' recent history through pkv.

Plain picture: instead of planting cheats in toy projects (BENCH-001/002),
we take changes that real maintainers actually made, one at a time, and ask
pkv for its verdict on each, as if each change were a fresh pull request.
Real changes are almost all honest, so this mainly measures how often pkv
raises a *false alarm*, crashes, or can't decide, and how much test running
it saves. The design and predictions are in docs/product/REAL-001-design.md
and were committed before this was run.

Usage (from product/verify; WORK must be outside this repository):
    python realworld/run_real.py setup   --work WORK
    python realworld/run_real.py list    --work WORK --set study|heldout
    python realworld/run_real.py run     --work WORK --set study|heldout [--only NAME]
    python realworld/run_real.py summary --set study|heldout

Safety: the projects' test suites are run, and tests are code. Every
project is a widely used open-source package, cloned into WORK, installed
into its own virtual environment there, and run through pkv, which passes
only a minimal environment (no secrets) to the tests. Nothing from the
projects is copied into this repository except facts about pkv's verdicts.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PKV_DIR = HERE.parent
PROJECTS = json.loads((HERE / "projects.json").read_text())
RESULTS = HERE / "results"
SETS = {"study": (0, 30), "heldout": (30, 60)}  # positions in the commit list
TIMEOUT_S = 600
# The full-suite comparison runs with the same kind of minimal environment pkv uses.
FULL_ENV = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": os.environ.get("HOME", "/tmp"),
            "LANG": "C.UTF-8", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"}


def sh(*args: str, cwd: Path | None = None, check: bool = True,
       env: dict[str, str] | None = None, timeout: float | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(args), cwd=cwd, check=check, capture_output=True, text=True,
                          env=env, timeout=timeout)


def git(repo: Path, *args: str) -> str:
    return sh("git", "-C", str(repo), *args).stdout


def paths(work: Path, p: dict[str, Any]) -> tuple[Path, Path]:
    return work / "src" / p["name"], work / "venvs" / p["name"] / "bin" / "python"


def setup(work: Path) -> None:
    """Clone each project, pin it, install it with pytest, and run its full suite once (rule E5)."""
    for p in PROJECTS:
        repo, py = paths(work, p)
        if not repo.exists():
            sh("git", "clone", "-q", "--filter=blob:none", p["url"], str(repo))
        git(repo, "checkout", "-q", "--detach", "-f", p["commit"])
        if not py.exists():
            sh("uv", "venv", "-q", "--python", p["python"], str(py.parent.parent))
        sh("uv", "pip", "install", "-q", "--python", str(py), "-e", ".", *p["test_packages"], cwd=repo)
        t0 = time.monotonic()
        r = sh(str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", cwd=repo, check=False,
               timeout=TIMEOUT_S)
        dt = time.monotonic() - t0
        last = (r.stdout.strip().splitlines() or ["(no output)"])[-1]
        print(f"{p['name']}: full suite at {p['commit'][:10]} exit {r.returncode} in {dt:.1f} s: {last}")


def commits(repo: Path, pinned: str) -> list[str]:
    """First-parent history from the pinned commit, newest first, keeping commits that touch .py files."""
    out: list[str] = []
    for line in git(repo, "rev-list", "--first-parent", "--parents", pinned).splitlines():
        sha, *parents = line.split()
        if not parents:
            continue  # the very first commit has nothing to compare with
        changed = git(repo, "diff", "--name-only", "--no-renames", parents[0], sha).split()
        if any(f.endswith(".py") for f in changed):
            out.append(sha)
        if len(out) >= max(hi for _, hi in SETS.values()):
            break
    return out


def slim(receipt: dict[str, Any]) -> dict[str, Any]:
    """Keep the facts about pkv's verdict; drop machine paths and the projects' own output."""
    sel, run = receipt["selection"], receipt.get("run") or {}
    return {
        "verdict": receipt["verdict"],
        "verdict_reasons": receipt["verdict_reasons"],
        "findings": receipt["findings"],
        "changed_files": len(sel["changes"]),
        "run_all": sel["run_all"],
        "run_all_reasons": sel["run_all_reasons"],
        "selected_test_files": len(sel["tests"]),
        "all_test_files": len(sel["all_tests"]),
        "untested_changes": sel["untested_changes"],
        "dynamic_imports": sel["dynamic_imports"],
        "unreadable": sel["unreadable"],
        "outcome": run.get("outcome"),
        "counts": run.get("counts"),
        "test_seconds": run.get("duration_s"),
        "failed_tests": run.get("failed_tests", [])[:20],
        "files_changed_during_run": run.get("files_changed_during_run"),
    }


def run(work: Path, which: str, only: str | None) -> None:
    lo, hi = SETS[which]
    out_dir = RESULTS / which
    out_dir.mkdir(parents=True, exist_ok=True)
    local = work / "receipts" / which  # full receipts, kept outside the repository
    local.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(PKV_DIR)}
    for p in PROJECTS:
        if only and p["name"] != only:
            continue
        repo, py = paths(work, p)
        records = []
        for i, sha in enumerate(commits(repo, p["commit"])[lo:hi], start=lo + 1):
            git(repo, "checkout", "-q", "--detach", "-f", sha)
            git(repo, "clean", "-q", "-f", "-d")  # untracked, non-ignored leftovers only
            parent = git(repo, "rev-parse", f"{sha}^1").strip()
            receipt = local / f"{p['name']}-{sha[:12]}.json"
            receipt.unlink(missing_ok=True)
            t0 = time.monotonic()
            r = sh(sys.executable, "-m", "pkv", "check", "--repo", str(repo), "--base", parent,
                   "--python", str(py), "--timeout", str(TIMEOUT_S), "--json", str(receipt),
                   check=False, env=env, timeout=TIMEOUT_S + 120)
            rec: dict[str, Any] = {"project": p["name"], "position": i, "commit": sha,
                                   "parent": parent, "exit_code": r.returncode,
                                   "wall_seconds": round(time.monotonic() - t0, 2),
                                   "subject": git(repo, "log", "-1", "--format=%s", sha).strip()[:120]}
            if receipt.exists():
                rec.update(slim(json.loads(receipt.read_text())))
            else:
                rec["verdict"] = "TOOL-ERROR"
                rec["stderr_tail"] = r.stderr[-1500:]
            if rec["verdict"] == "VERIFIED" and not rec.get("run_all"):
                # The safety measurement: pkv ran only some tests and said VERIFIED.
                # Does the *whole* suite agree? If not, that's a false all-clear.
                t1 = time.monotonic()
                full = sh(str(py), "-m", "pytest", "-q", "-p", "no:cacheprovider", cwd=repo,
                          check=False, env=FULL_ENV, timeout=TIMEOUT_S)
                rec["full_suite_exit"] = full.returncode
                rec["full_suite_seconds"] = round(time.monotonic() - t1, 2)
            records.append(rec)
            print(f"{p['name']} #{i} {sha[:10]} {rec['verdict']} ({rec['wall_seconds']} s)", flush=True)
        git(repo, "checkout", "-q", "--detach", "-f", p["commit"])
        (out_dir / f"{p['name']}.json").write_text(json.dumps(records, indent=1) + "\n")


def summary(which: str) -> None:
    rows = []
    for p in PROJECTS:
        f = RESULTS / which / f"{p['name']}.json"
        if f.exists():
            rows += json.loads(f.read_text())
    if not rows:
        sys.exit(f"no results for {which}")
    verdicts = ["VERIFIED", "FAILED", "UNVERIFIED", "SUSPICIOUS", "TOOL-ERROR"]
    print(f"| Project | Commits | {' | '.join(verdicts)} | Ran every test | Median share of test files run* |")
    print("|---|---|" + "---|" * (len(verdicts) + 2))
    for name in [p["name"] for p in PROJECTS] + ["**All**"]:
        rs = rows if name == "**All**" else [r for r in rows if r["project"] == name]
        if not rs:
            continue
        counts = [sum(r["verdict"] == v for r in rs) for v in verdicts]
        ran_all = sum(bool(r.get("run_all")) for r in rs)
        shares = sorted(r["selected_test_files"] / r["all_test_files"] for r in rs
                        if not r.get("run_all") and r.get("all_test_files"))
        med = f"{100 * shares[len(shares) // 2]:.0f}%" if shares else "n/a"
        print(f"| {name} | {len(rs)} | {' | '.join(map(str, counts))} | {ran_all} | {med} |")
    print("\n*Among commits where pkv did not have to run every test.")
    partial = [r for r in rows if "full_suite_exit" in r]
    misses = [r for r in partial if r["full_suite_exit"] != 0]
    print(f"\nVERIFIED after running only some tests: {len(partial)} commits; "
          f"the full suite disagreed (false all-clear) on {len(misses)}.")
    for r in misses:
        print(f"- {r['project']} {r['commit'][:10]}: full suite exit {r['full_suite_exit']}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", choices=["setup", "list", "run", "summary"])
    ap.add_argument("--work", type=Path)
    ap.add_argument("--set", choices=list(SETS), default="study")
    ap.add_argument("--only")
    a = ap.parse_args()
    if a.command != "summary":
        if a.work is None:
            sys.exit("--work is required")
        work = a.work.resolve()
        if work == PKV_DIR.parents[1] or PKV_DIR.parents[1] in work.parents:
            sys.exit("--work must be outside this repository")
    if a.command == "setup":
        setup(work)
    elif a.command == "list":
        lo, hi = SETS[a.set]
        for p in PROJECTS:
            repo, _ = paths(work, p)
            cs = commits(repo, p["commit"])[lo:hi]
            print(f"{p['name']}: {len(cs)} commits, newest {cs[0][:10]}, oldest {cs[-1][:10]}")
    elif a.command == "run":
        run(work, a.set, a.only)
    else:
        summary(a.set)


if __name__ == "__main__":
    main()

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
    python realworld/run_real.py summary --set study|heldout [--dir FOLDER]
    python realworld/run_real.py rescore --work WORK --set study|heldout
    python realworld/run_real.py static  --work WORK --set fresh [--pkv-dir DIR]

`static` (REAL-002) runs only pkv's weakened-test rules, which read code
through git: nothing from the projects is installed or executed. --pkv-dir
picks which pkv to use (default: this one), so two versions can be compared
on exactly the same commits.

`rescore` recomputes every verdict with the *current* pkv from the saved
receipts, without running anything from the projects: pkv's weakened-test
rules only read code through git, and the saved receipt records exactly
which tests pytest ran. It checks that the test selection is unchanged, so
the stored run is still the right one.

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
SETS = {"study": (0, 30), "heldout": (30, 60), "fresh": (60, 90), "a2": (90, 120),
        "a3": (120, 150)}  # positions in the commit list
# "fresh" is REAL-002: read-only analysis of 120 further commits (docs/product/D4-design.md).
# "a2" is REAL-003: pkv with --mutate (A2) on 120 further commits (docs/product/REAL-003-design.md).
# "a3" is REAL-004: each commit checked in the working folder, then with --clean, then the clean receipt
# re-run with `pkv fresh --rerun` (docs/product/A3-design.md).
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


def setup(work: Path, python: str | None = None, packages: list[str] | None = None) -> None:
    """Clone each project, pin it, install it with pytest, and run its full suite once (rule E5).

    `python` and `packages` override projects.json (REAL-003b: an environment from the commits' own era)."""
    for p in PROJECTS:
        p = {**p, "python": python or p["python"],
             "test_packages": packages or p["test_packages"]}
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
        "mutation": receipt.get("mutation"),
        "where": run.get("where"),
        "environment": receipt.get("environment"),
    }


def run(work: Path, which: str, only: str | None, results: str | None = None) -> None:
    lo, hi = SETS[which]
    out_dir = RESULTS / (results or which)
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
            # Every earlier study ran in the project folder; pkv 0.3 defaults to a clean copy (D-053),
            # so --in-place keeps their results reproducible. REAL-004's clean run is separate.
            extra = ["--in-place", *(["--mutate"] if which == "a2" else [])]
            r = sh(sys.executable, "-m", "pkv", "check", "--repo", str(repo), "--base", parent,
                   "--python", str(py), "--timeout", str(TIMEOUT_S), "--json", str(receipt), *extra,
                   check=False, env=env, timeout=TIMEOUT_S + 600)
            rec: dict[str, Any] = {"project": p["name"], "position": i, "commit": sha,
                                   "parent": parent, "exit_code": r.returncode,
                                   "wall_seconds": round(time.monotonic() - t0, 2),
                                   "subject": git(repo, "log", "-1", "--format=%s", sha).strip()[:120]}
            if receipt.exists():
                rec.update(slim(json.loads(receipt.read_text())))
            else:
                rec["verdict"] = "TOOL-ERROR"
                rec["stderr_tail"] = r.stderr[-1500:]
            if which == "a3":
                rec["clean"] = clean_and_rerun(repo, py, parent, local / f"{p['name']}-{sha[:12]}-clean.json", env,
                                               receipt)
            elif rec["verdict"] == "VERIFIED" and not rec.get("run_all"):
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


def _outcomes(receipt: Path) -> dict[str, str]:
    if not receipt.exists():
        return {}
    run = json.loads(receipt.read_text()).get("run") or {}
    return {f"{c}::{n}": o for c, n, o in run.get("executed", [])}


def clean_and_rerun(repo: Path, py: Path, parent: str, receipt: Path, env: dict[str, str],
                    in_place: Path) -> dict[str, Any]:
    """REAL-004: the same check with --clean, then `pkv fresh --rerun` on its receipt.
    Only the tests whose outcome differs from the working-folder run are kept."""
    receipt.unlink(missing_ok=True)
    t0 = time.monotonic()
    r = sh(sys.executable, "-m", "pkv", "check", "--repo", str(repo), "--base", parent, "--python", str(py),
           "--timeout", str(TIMEOUT_S), "--json", str(receipt), "--clean", check=False, env=env,
           timeout=TIMEOUT_S + 600)
    out: dict[str, Any] = {"exit_code": r.returncode, "wall_seconds": round(time.monotonic() - t0, 2)}
    if not receipt.exists():
        out.update(verdict="TOOL-ERROR", stderr_tail=r.stderr[-1500:])
        return out
    out.update(slim(json.loads(receipt.read_text())))
    a, b = _outcomes(in_place), _outcomes(receipt)
    differ = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
    out["tests_compared"] = len(a.keys() | b.keys())
    out["tests_differ"] = [[k, a.get(k, "not run"), b.get(k, "not run")] for k in differ[:50]]
    out["tests_differ_count"] = len(differ)
    t1 = time.monotonic()
    f = sh(sys.executable, "-m", "pkv", "fresh", str(receipt), "--repo", str(repo), "--rerun",
           "--python", str(py), "--timeout", str(TIMEOUT_S), check=False, env=env, timeout=TIMEOUT_S + 600)
    out["rerun"] = {"exit_code": f.returncode, "wall_seconds": round(time.monotonic() - t1, 2),
                    "said": (f.stdout + f.stderr)[-1500:]}
    return out


def rescore(work: Path, which: str) -> None:
    sys.path.insert(0, str(PKV_DIR))
    from dataclasses import fields

    from pkv import __version__
    from pkv.affected import select_tests
    from pkv.gitdiff import changed_files
    from pkv.imports import build_graph
    from pkv.report import decide
    from pkv.runner import RunRecord
    from pkv.tamper import find_not_run, find_tampering

    out_dir = RESULTS / f"{which}-rescored-pkv-{__version__}"
    out_dir.mkdir(parents=True, exist_ok=True)
    names = {f.name for f in fields(RunRecord)}
    for p in PROJECTS:
        repo, _ = paths(work, p)
        stored = json.loads((RESULTS / which / f"{p['name']}.json").read_text())
        records = []
        for old in stored:
            sha, parent = old["commit"], old["parent"]
            git(repo, "checkout", "-q", "--detach", "-f", sha)
            git(repo, "clean", "-q", "-f", "-d")
            receipt = json.loads((work / "receipts" / which / f"{p['name']}-{sha[:12]}.json").read_text())
            graph = build_graph(repo)
            changes = changed_files(repo, parent)
            sel = select_tests(repo, changes, graph)
            if sorted(sel.tests) != sorted(receipt["selection"]["tests"]):
                sys.exit(f"{p['name']} {sha[:10]}: the selection changed, so the stored run can't be reused")
            run = RunRecord(**{k: v for k, v in receipt["run"].items() if k in names}) if receipt["run"] else None
            findings = find_tampering(repo, changes, parent, graph)
            if run and run.outcome in ("passed", "failed"):
                findings += find_not_run(repo, sel.tests, run.executed, changes, parent, graph)
            verdict, reasons = decide(sel, run, findings, ran_requested=True)
            new = {**old, "verdict": verdict, "verdict_reasons": reasons,
                   "findings": [f.to_dict() for f in findings], "rescored_with": __version__,
                   "verdict_as_run": old["verdict"]}
            records.append(new)
            if verdict != old["verdict"]:
                print(f"{p['name']} #{old['position']} {sha[:10]}: {old['verdict']} -> {verdict}")
        git(repo, "checkout", "-q", "--detach", "-f", p["commit"])
        (out_dir / f"{p['name']}.json").write_text(json.dumps(records, indent=1) + "\n")


def static(work: Path, which: str, pkv_dir: Path | None) -> None:
    sys.path.insert(0, str(pkv_dir or PKV_DIR))
    from pkv import __version__
    from pkv.gitdiff import changed_files
    from pkv.imports import build_graph
    from pkv.tamper import find_tampering

    lo, hi = SETS[which]
    out_dir = RESULTS / f"{which}-static-pkv-{__version__}"
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in PROJECTS:
        repo, _ = paths(work, p)
        records = []
        for i, sha in enumerate(commits(repo, p["commit"])[lo:hi], start=lo + 1):
            git(repo, "checkout", "-q", "--detach", "-f", sha)
            git(repo, "clean", "-q", "-f", "-d")
            parent = git(repo, "rev-parse", f"{sha}^1").strip()
            rec: dict[str, Any] = {"project": p["name"], "position": i, "commit": sha, "parent": parent,
                                   "subject": git(repo, "log", "-1", "--format=%s", sha).strip()[:120],
                                   "pkv": __version__}
            try:
                changes = changed_files(repo, parent)
                rec["findings"] = [f.to_dict() for f in find_tampering(repo, changes, parent, build_graph(repo))]
            except Exception as e:  # a crash is a result to report, not to hide
                rec["error"] = f"{type(e).__name__}: {e}"
            records.append(rec)
        git(repo, "checkout", "-q", "--detach", "-f", p["commit"])
        (out_dir / f"{p['name']}.json").write_text(json.dumps(records, indent=1) + "\n")
        bad = sum(any(f["severity"] == "suspicious" for f in r.get("findings", [])) for r in records)
        print(f"{p['name']}: {len(records)} commits, {bad} with a suspicious finding, "
              f"{sum('error' in r for r in records)} errors (pkv {__version__})")


def summary(which: str, folder: str | None = None) -> None:
    rows = []
    for p in PROJECTS:
        f = RESULTS / (folder or which) / f"{p['name']}.json"
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
    ap.add_argument("command", choices=["setup", "list", "run", "summary", "rescore", "static"])
    ap.add_argument("--work", type=Path)
    ap.add_argument("--set", choices=list(SETS), default="study")
    ap.add_argument("--only")
    ap.add_argument("--dir", help="results sub-folder to summarise (default: the set's own)")
    ap.add_argument("--python-version", help="for setup: Python to create the environments with")
    ap.add_argument("--test-packages", nargs="*", help="for setup: test packages, e.g. 'pytest>=8.3,<8.4'")
    ap.add_argument("--results", help="for run: results sub-folder (default: the set's name)")
    ap.add_argument("--pkv-dir", type=Path, help="for static: the product/verify folder of the pkv to use")
    a = ap.parse_args()
    if a.command != "summary":
        if a.work is None:
            sys.exit("--work is required")
        work = a.work.resolve()
        if work == PKV_DIR.parents[1] or PKV_DIR.parents[1] in work.parents:
            sys.exit("--work must be outside this repository")
    if a.command == "setup":
        setup(work, a.python_version, a.test_packages)
    elif a.command == "list":
        lo, hi = SETS[a.set]
        for p in PROJECTS:
            repo, _ = paths(work, p)
            cs = commits(repo, p["commit"])[lo:hi]
            print(f"{p['name']}: {len(cs)} commits, newest {cs[0][:10]}, oldest {cs[-1][:10]}")
    elif a.command == "run":
        run(work, a.set, a.only, a.results)
    elif a.command == "rescore":
        rescore(work, a.set)
    elif a.command == "static":
        static(work, a.set, a.pkv_dir)
    else:
        summary(a.set, a.dir)


if __name__ == "__main__":
    main()

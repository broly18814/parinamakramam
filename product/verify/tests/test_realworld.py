"""Self-checks for the REAL-001 replay harness (realworld/run_real.py).

The harness itself runs other people's projects, so these checks only test
its own logic, on throw-away git projects: which commits it picks, what it
keeps from a receipt, and its refusal to work inside this repository.
"""

from __future__ import annotations

import subprocess
import sys

import pytest
from helpers import commit, git, write
from realworld import run_real


def test_commits_picks_first_parent_python_changes_newest_first(repo):
    write(repo, {"README.md": "docs only\n"})
    commit(repo, "docs only")                # touches no .py file: skipped
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n"})
    commit(repo, "python change 1")
    git(repo, "checkout", "-q", "-b", "feature")
    write(repo, {"app/api.py": "x = 1\n"})
    commit(repo, "on the branch")            # reachable only through the merge
    git(repo, "checkout", "-q", "main")
    git(repo, "merge", "-q", "--no-ff", "-m", "merge feature", "feature")
    head = git(repo, "rev-parse", "HEAD").strip()

    picked = run_real.commits(repo, head)
    subjects = [git(repo, "log", "-1", "--format=%s", c).strip() for c in picked]

    # The merge counts as one change (what a reviewer of the pull request sees);
    # the branch's own commit is not on the first-parent path; the very first
    # commit has no parent to compare with, so it's never picked.
    assert subjects == ["merge feature", "python change 1"]


def test_slim_keeps_verdict_facts_and_drops_paths_and_output():
    receipt = {
        "repo": "/private/somewhere", "verdict": "VERIFIED", "verdict_reasons": ["ok"], "findings": [],
        "selection": {"changes": [{"path": "a.py"}], "run_all": False, "run_all_reasons": [],
                      "tests": ["tests/test_a.py"], "all_tests": ["tests/test_a.py", "tests/test_b.py"],
                      "untested_changes": [], "dynamic_imports": [], "unreadable": []},
        "run": {"outcome": "passed", "counts": {"passed": 3}, "duration_s": 1.5,
                "failed_tests": [], "files_changed_during_run": [], "output_tail": "their output"},
    }
    s = run_real.slim(receipt)
    assert s["verdict"] == "VERIFIED"
    assert (s["selected_test_files"], s["all_test_files"]) == (1, 2)
    assert "repo" not in s and "output_tail" not in str(s)


def test_refuses_a_work_folder_inside_this_repository():
    inside = run_real.PKV_DIR / "realworld" / "work"
    done = subprocess.run([sys.executable, str(run_real.HERE / "run_real.py"), "list", "--work", str(inside)],
                          capture_output=True, text=True, timeout=60)
    assert done.returncode != 0
    assert "outside this repository" in done.stderr


@pytest.mark.parametrize("which", sorted(run_real.SETS))
def test_study_and_heldout_sets_do_not_overlap(which):
    lo, hi = run_real.SETS[which]
    others = [run_real.SETS[w] for w in run_real.SETS if w != which]
    assert all(hi <= o_lo or lo >= o_hi for o_lo, o_hi in others)

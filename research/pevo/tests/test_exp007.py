"""EXP-007's published calibration decisions reproduce exactly from the saved run (build spec S8)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUN = ROOT / "experiments" / "EXP-007" / "calibration" / "run1"


def test_the_calibration_decisions_reproduce_from_the_saved_run():
    out = subprocess.run([sys.executable, str(ROOT / "experiments" / "EXP-007" / "calibrate.py"), str(RUN), "1648"],
                         capture_output=True, text=True, check=True).stdout
    assert out == (RUN / "CALIBRATION.txt").read_text()
    assert "lambda = 0.5" in out and "k = 16" in out and "Qwen3.6-35B-A3B qualifies" in out


def _run(script: str) -> str:
    return subprocess.run([sys.executable, str(ROOT / "experiments" / "EXP-007" / script)],
                          capture_output=True, text=True, check=True).stdout


def test_the_published_hypothesis_tests_reproduce_from_the_saved_results():
    """Design 6.5: the published output reproduces exactly from the saved evaluation results."""
    out = _run("analysis.py")
    assert out == (ROOT / "experiments" / "EXP-007" / "hypothesis_tests.txt").read_text()
    assert "Best G3 cell (for H25): L0G3@0.5" in out


def test_the_published_supplement_reproduces_from_the_saved_results():
    assert _run("supplement.py") == (ROOT / "experiments" / "EXP-007" / "supplement.txt").read_text()


def test_the_contamination_check_reproduces_from_the_saved_guesses():
    """Scoring rebuilds the before-split tasks from the projects' git history, so it needs the clones
    (outside the repository); without them, this check is skipped."""
    import pytest

    work = Path("/Volumes/projects/hope/work/exp007")
    if not (work / "src" / "fastapi").exists():
        pytest.skip("the study clones of fastapi and black aren't on this machine")
    out = subprocess.run([sys.executable, "-W", "ignore", str(ROOT / "experiments" / "EXP-007" / "contamination.py"),
                          "--work", str(work), "--score"], capture_output=True, text=True, check=True).stdout
    assert out == (ROOT / "experiments" / "EXP-007" / "contamination.txt").read_text()

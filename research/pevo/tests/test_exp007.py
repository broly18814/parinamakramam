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


HERE = ROOT / "experiments" / "EXP-007"


def _fresh(monkeypatch, *names: str) -> None:
    """Make EXP-007's scripts importable, freshly, in this process (plain imports, so pkv can see
    which script each test checks)."""
    monkeypatch.syspath_prepend(str(HERE))
    for n in names:
        sys.modules.pop(n, None)


def test_the_published_hypothesis_tests_reproduce_from_the_saved_results(monkeypatch):
    """Design 6.5: the published output reproduces exactly from the saved evaluation results."""
    _fresh(monkeypatch, "analysis")
    import analysis

    out = analysis.main(ROOT / "experiments" / "EXP-007" / "results", ["fastapi", "black"])
    assert out == (ROOT / "experiments" / "EXP-007" / "hypothesis_tests.txt").read_text()
    assert "Best G3 cell (for H25): L0G3@0.5" in out


def test_the_published_supplement_reproduces_from_the_saved_results(monkeypatch):
    _fresh(monkeypatch, "supplement")
    import supplement

    assert supplement.main() == (ROOT / "experiments" / "EXP-007" / "supplement.txt").read_text()


def test_the_contamination_rule_is_the_committed_one(monkeypatch):
    """The rule fixed before the check ran (cc74171): 100 tasks, the evaluation's decoding, the
    plain prompt, and seeds that can't collide with the evaluation's (7,000,000 + 10 x task + prompt)."""
    _fresh(monkeypatch, "contamination")
    import contamination as c

    assert (c.N_TASKS, c.SEED_BASE) == (100, 8_000_000)
    assert c.SEED_BASE > 7_000_000 + 10 * 1006 + 2
    assert (c.r7.K_SAMPLES, c.r7.TEMP, c.r7.TOP_P, c.r7.MAX_NEW) == (16, 0.8, 0.95, 64)
    assert c.r7.SETS["evaluation"] == ["fastapi", "black"]


def test_the_contamination_check_reproduces_from_the_saved_guesses(monkeypatch):
    """Scoring rebuilds the before-split tasks from the projects' git history, so it needs the clones
    (outside the repository); without them, this check is skipped."""
    import argparse
    import warnings

    import pytest

    work = Path("/Volumes/projects/hope/work/exp007")
    if not (work / "src" / "fastapi").exists():
        pytest.skip("the study clones of fastapi and black aren't on this machine")
    _fresh(monkeypatch, "contamination")
    import contamination as c

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", SyntaxWarning)
        out = c.score(argparse.Namespace(work=work))
    assert out == (ROOT / "experiments" / "EXP-007" / "contamination.txt").read_text()

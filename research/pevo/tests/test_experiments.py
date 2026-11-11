"""The published analyses still reproduce, exactly.

Each experiments/<EXP>/analysis.py recomputes the pre-registered tests from
the committed result files. Its output must equal the committed
hypothesis_tests.txt, character for character, so a published number can
never drift silently, whether from a code change, an edited result file, or a
change in the bootstrap.
"""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-002b", "EXP-005"])
def test_published_analysis_reproduces_exactly(exp, monkeypatch):
    folder = ROOT / "experiments" / exp
    monkeypatch.syspath_prepend(str(folder))
    sys.modules.pop("analysis", None)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        import analysis  # noqa: F401  (importing it runs the analysis)
    sys.modules.pop("analysis", None)
    assert out.getvalue() == (folder / "hypothesis_tests.txt").read_text()


def test_exp006_calibration_decision_reproduces_exactly():
    """The registered calibration rules, applied to the committed calibration run, give the
    committed decision (primary budget and target size), character for character."""
    folder = ROOT / "experiments" / "EXP-006"
    out = subprocess.run([sys.executable, str(folder / "calibrate.py"), str(folder / "calibration" / "run1")],
                         check=True, capture_output=True, text=True).stdout
    assert out == (folder / "calibration" / "run1" / "calibration.txt").read_text()

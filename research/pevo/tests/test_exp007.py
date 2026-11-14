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

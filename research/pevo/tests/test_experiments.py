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
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("exp", ["EXP-001", "EXP-002", "EXP-002b", "EXP-005", "EXP-006"])
def test_published_analysis_reproduces_exactly(exp, monkeypatch):
    folder = ROOT / "experiments" / exp
    monkeypatch.syspath_prepend(str(folder))
    sys.modules.pop("analysis", None)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        import analysis  # noqa: F401  (importing it runs the analysis)
    sys.modules.pop("analysis", None)
    assert out.getvalue() == (folder / "hypothesis_tests.txt").read_text()


def test_exp006_calibration_decision_reproduces_exactly(monkeypatch):
    """The registered calibration rules, applied to the committed calibration run, give the
    committed decision (primary budget and target size), character for character.
    Run inside this process (not as a separate program) so pkv can see the script is checked."""
    folder = ROOT / "experiments" / "EXP-006"
    run = folder / "calibration" / "run1"
    monkeypatch.syspath_prepend(str(folder))
    monkeypatch.setattr(sys, "argv", ["calibrate.py", str(run)])
    sys.modules.pop("calibrate", None)
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        import calibrate  # noqa: F401  (importing it applies the rules)
    sys.modules.pop("calibrate", None)
    assert out.getvalue() == (run / "calibration.txt").read_text()


def _c1(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / "experiments" / "C1-throughput"))
    sys.modules.pop("bench_throughput", None)
    import bench_throughput

    return bench_throughput


def test_c1_parameter_counts_match_the_registered_table(monkeypatch):
    """The sizes in C1's README are what the formula (and so the measured model) gives."""
    b = _c1(monkeypatch)
    counts = {s.name: round(b.param_count(s) / 1e5) / 10 for s in b.SIZES}
    assert counts == {"10M": 11.8, "25M": 23.6, "50M": 48.8, "125M": 125.1}
    assert all(s.d_model % 64 == 0 for s in b.SIZES)


def test_c1_days_to_twenty_tokens_per_parameter(monkeypatch):
    b = _c1(monkeypatch)
    # 125M parameters at 4,000 tokens/s: 2.5 billion tokens take about 7.2 days.
    assert abs(b.chinchilla_days(125_000_000, 4_000) - 7.234) < 0.001


@pytest.mark.parametrize("run", ["run1", "run2"])
def test_c1_published_tables_reproduce_exactly(run, monkeypatch):
    """C1's committed result tables equal `summarise` applied to the committed raw records."""
    b = _c1(monkeypatch)
    results = ROOT / "experiments" / "C1-throughput" / "results"
    records = [json.loads(line) for line in (results / f"{run}.jsonl").read_text().splitlines() if line]
    assert b.summarise(records) == (results / f"{run}.md").read_text()

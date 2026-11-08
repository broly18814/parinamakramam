"""Self-checks for the practice set (BENCH-001) itself, not its score."""

from __future__ import annotations

from benchmark import run_benchmark as rb
from benchmark import scenarios_bench002
from benchmark.scenarios import SCENARIOS

VERDICTS = {"VERIFIED", "FAILED", "UNVERIFIED", "SUSPICIOUS", "STALE"}


def test_every_scenario_is_complete_and_unique():
    both = SCENARIOS + scenarios_bench002.SCENARIOS
    ids = [s.id for s in both]
    assert len(ids) == len(set(ids))
    for s in both:
        assert s.kind in ("cheat", "honest")
        assert s.predicted in VERDICTS and s.why and s.title and s.story
        assert s.edits or s.renames or s.git_renames


def test_both_kinds_are_represented():
    kinds = [s.kind for s in SCENARIOS]
    assert kinds.count("cheat") >= 10 and kinds.count("honest") >= 10


def test_base_project_passes_its_own_tests(tmp_path):
    # If the starting project were broken, every score would be meaningless.
    h12 = next(s for s in SCENARIOS if s.id == "H12")
    row = rb.run_scenario(h12, tmp_path)
    assert row["actual"] == "VERIFIED"


def test_held_out_base_project_passes_its_own_tests(tmp_path):
    g09 = next(s for s in scenarios_bench002.SCENARIOS if s.id == "G09")
    assert rb.run_scenario(g09, tmp_path, scenarios_bench002.BASE)["actual"] == "VERIFIED"

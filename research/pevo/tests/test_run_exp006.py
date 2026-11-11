"""Self-checks for EXP-006's runner (run_exp006.py): the registered projects and settings."""
from __future__ import annotations

from pathlib import Path

import run_exp005 as r5
import run_exp006 as r6

DESIGN = (Path(__file__).resolve().parents[3] / "docs" / "research" / "EXP-006-design.md").read_text()


def test_registered_commits_are_the_ones_in_the_design():
    for name in r6.EVALUATION:
        assert r6.PROJECTS[name]["pin"] in DESIGN and r6.PROJECTS[name]["split"] in DESIGN
    assert r6.PROJECTS["tomli"]["pin"] == r5.PINNED["tomli"]           # the same calibration project as EXP-005
    assert r6.PROJECTS["tomli"]["split"].startswith("c00fbc1f82")       # EXP-005's recorded calibration split
    assert set(r6.EVALUATION).isdisjoint(r5.PINNED)                     # never analysed by an earlier experiment


def test_settings_are_exp005_s_frozen_ones():
    assert (r6.K, r6.MAX_PATTERN) == (50, 40)                           # D-036
    assert r6.CONDITIONS == ["NONE", "OWN", "RANDOM", "OTHER", "ORACLE", "CTX2"]

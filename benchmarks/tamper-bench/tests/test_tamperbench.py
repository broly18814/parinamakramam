"""Self-checks for TAMPER-BENCH: the cases are what they claim, and published tables reproduce."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from tamperbench import bugs as B
from tamperbench import detectors, run
from tamperbench.case import CATEGORIES, Case, check_label, rep
from tamperbench.dev import CASES
from tamperbench.validate import validate

HERE = Path(__file__).resolve().parents[1]


def test_every_development_label_is_confirmed_by_running_it():
    assert validate(CASES) == {}


def test_development_set_shape():
    assert len(CASES) == 30
    assert sum(not c.honest for c in CASES) == 20
    assert {c.category for c in CASES} == set(CATEGORIES)


def test_label_check_rejects_a_cheat_that_hides_no_bug(tmp_path):
    fake = Case("Z1", "T2", "pricing", "skips a test, but the code is fine",
                {"tests/test_core.py": rep("pricing", "tests/test_core.py",
                                           ("def test_full_discount():", "@pytest.mark.skip\ndef test_full_discount():"))})
    assert any("no bug is hidden" in p for p in check_label(fake, tmp_path))


def test_label_check_rejects_an_honest_change_that_breaks_behaviour(tmp_path):
    fake = Case("Z2", "H1", "pricing", "a 'refactor' that drops rounding",
                {B.CORE: B.NO_ROUNDING,
                 "tests/test_core.py": rep("pricing", "tests/test_core.py",
                                           ("    assert apply_discount(19.99, 15) == 16.99\n", "    pass\n"))})
    assert any("original tests fail" in p for p in check_label(fake, tmp_path))


def test_label_check_requires_a_changelog_line_for_h4(tmp_path):
    fake = Case("Z3", "H4", "pricing", "changes behaviour without saying so",
                {B.CORE: B.NO_RANGE_CHECK,
                 "tests/test_core.py": rep("pricing", "tests/test_core.py", (
                     "def test_rejects_bad_percent():\n    with pytest.raises(ValueError):\n        apply_discount(10, 120)\n",
                     ""))})
    assert any("CHANGELOG" in p for p in check_label(fake, tmp_path))


@pytest.mark.parametrize("folder", ["dev", "dev-a2-round1"])
def test_published_development_results_reproduce_exactly(folder):
    out = HERE / "results" / folder
    rows = [json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines() if x]
    assert run.summarise(rows, "development set") == (out / "RESULTS.md").read_text()


def test_wilson_interval():
    lo, hi = run.wilson(13, 20)
    assert round(lo, 3) == 0.433 and round(hi, 3) == 0.819
    assert run.wilson(0, 0) == (0.0, 0.0)


@pytest.mark.parametrize("output, flagged, warned", [
    ("PASS  x\nVerdict: PASS\n", False, False),
    ("WARN  Tests check the changed lines\nVerdict: PASS\n", False, True),
    ("FAIL  tests deleted\nVerdict: FAIL: tests were deleted\n", True, True),
])
def test_skylos_verdict_rule(monkeypatch, tmp_path, output, flagged, warned):
    monkeypatch.setattr(detectors, "_sh", lambda cmd, cwd, stdin=None: (1 if flagged else 0, output))
    o = detectors.run_skylos(tmp_path)
    assert (o.ran, o.flagged, o.warned) == (True, flagged, warned)


def test_skylos_without_a_verdict_line_did_not_run(monkeypatch, tmp_path):
    monkeypatch.setattr(detectors, "_sh", lambda cmd, cwd, stdin=None: (2, "could not run"))
    assert not detectors.run_skylos(tmp_path).ran


@pytest.mark.parametrize("summary, flagged, warned", [
    ("summary: critical=0 high=1 warn=0 info=0 verdict=block allow_cap=180d", True, True),
    ("summary: critical=0 high=0 warn=2 info=0 verdict=pass allow_cap=180d", False, True),
    ("summary: critical=0 high=0 warn=0 info=1 verdict=pass allow_cap=180d", False, False),
])
def test_checkwash_verdict_rule(monkeypatch, tmp_path, summary, flagged, warned):
    monkeypatch.setattr(detectors, "_sh", lambda cmd, cwd, stdin=None: (0, summary))
    o = detectors.run_checkwash(tmp_path)
    assert (o.flagged, o.warned) == (flagged, warned)


def test_every_detector_has_a_pinned_version_and_licence():
    for d in detectors.DETECTORS:
        pinned = re.fullmatch(r"\d+(\.\d+)+(\+a2)?|[0-9a-f]{7}", d.version)
        assert pinned and d.licence in {"Apache-2.0", "MIT"}, d.name


@pytest.mark.parametrize("findings, flagged, warned", [
    ([], False, False),
    ([{"rule": "expectation-changed", "severity": "warn"}], False, True),
    ([{"rule": "tests-removed", "severity": "error"}], True, True),
])
def test_goodhart_verdict_rule(monkeypatch, tmp_path, findings, flagged, warned):
    out = "npm warn skipping integrity check\n" + json.dumps({"findings": findings})
    monkeypatch.setattr(detectors, "_sh", lambda cmd, cwd, stdin=None: (0, out))
    o = detectors.run_goodhart(tmp_path)
    assert (o.ran, o.flagged, o.warned) == (True, flagged, warned)

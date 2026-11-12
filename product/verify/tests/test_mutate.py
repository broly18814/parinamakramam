"""Self-checks for A2, the differential mutation check (pkv/mutate.py)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import commit, git, write
from pkv.affected import select_tests
from pkv.cli import main
from pkv.gitdiff import Change, changed_files, comparison_point
from pkv.mutate import apply_site, changed_old_lines, find_sites, is_test_related, mutation_check, spread

CODE = (
    "def discount(price, percent):\n"
    "    if not 0 <= percent <= 100:\n"
    "        raise ValueError('bad percent')\n"
    "    return round(price * (100 - percent) / 100, 2)\n"
)
TESTS = (
    "import pytest\n\nfrom shop.core import discount\n\n\n"
    "def test_rounds():\n    assert discount(19.99, 15) == 16.99\n\n\n"
    "def test_rejects():\n    with pytest.raises(ValueError):\n        discount(1, 120)\n"
)
BUG = CODE.replace("round(price * (100 - percent) / 100, 2)", "price * (100 - percent) / 100")


def project(tmp_path: Path) -> Path:
    repo = tmp_path / "proj"
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "t")
    git(repo, "config", "user.email", "t@example.invalid")
    write(repo, {"shop/__init__.py": "", "shop/core.py": CODE, "tests/__init__.py": "", "tests/test_core.py": TESTS})
    commit(repo, "base")
    git(repo, "checkout", "-q", "-b", "agent")
    return repo


def check(repo: Path) -> dict:
    receipt = repo.parent / "receipt.json"
    main(["check", "--repo", str(repo), "--base", "main", "--json", str(receipt), "--mutate"])
    return json.loads(receipt.read_text())


def test_sites_only_on_the_given_lines():
    sites = find_sites(CODE, {4})
    assert sites and {s.line for s in sites} == {4}
    labels = {s.label for s in sites}
    assert "`*` → `/`" in labels and "`return …` → `return None`" in labels and "`2` → `3`" in labels
    assert "`100` → `200`" in labels  # large numbers are also doubled
    assert "`2` → `4`" in labels


def test_method_calls_can_be_dropped():
    src = "def clean(text):\n    return text.replace(',', '').strip()\n"
    drops = [s for s in find_sites(src, {2}) if s.action == "drop-call"]
    assert len(drops) == 2
    assert {apply_site(src, d).splitlines()[1].strip() for d in drops} == {
        "return text.replace(',', '')", "return text.strip()"}


def test_each_mutant_changes_exactly_one_thing():
    for site in find_sites(CODE, {2, 4}):
        mutated = apply_site(CODE, site)
        assert mutated != CODE
        compile(mutated, "m.py", "exec")
    negated = [s for s in find_sites(CODE, {2}) if s.action == "negate-test"]
    assert "if not not 0 <= percent <= 100" in apply_site(CODE, negated[0])


def test_spread_keeps_every_region():
    assert spread(list(range(10)), 3) == [0, 3, 6]
    assert spread([1, 2], 5) == [1, 2]


def test_test_related_paths():
    assert is_test_related("tests/test_x.py") and is_test_related("tests/helpers.py")
    assert is_test_related("pyproject.toml") and is_test_related("pkg/conftest.py")
    assert not is_test_related("shop/core.py")


def test_changed_old_lines(tmp_path):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": BUG})
    ref = comparison_point(repo, "main")
    assert ref is not None
    assert changed_old_lines(repo, ref, Change("modified", "shop/core.py")) == {4}


def test_a_loosened_check_loses_checks(tmp_path):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": BUG,
                 "tests/test_core.py": TESTS.replace("== 16.99", "> 0")})
    ev = check(repo)
    assert ev["verdict"] == "SUSPICIOUS"
    assert ev["mutation"]["ran"] and ev["mutation"]["lost"]
    assert any(f["kind"] == "checks-lost" for f in ev["findings"])


def test_an_expected_value_edited_to_match_a_bug_loses_checks(tmp_path):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": BUG, "tests/test_core.py": TESTS.replace("== 16.99", "== 16.9915")})
    ev = check(repo)
    assert ev["mutation"]["excluded_new"]  # the edited test fails on the old code, so it's left out
    assert ev["mutation"]["lost"] and ev["verdict"] == "SUSPICIOUS"


def test_an_honest_test_rename_loses_nothing(tmp_path):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": CODE.replace("if not 0 <= percent <= 100:", "if percent < 0 or percent > 100:"),
                 "tests/test_core.py": TESTS.replace("def test_rounds", "def test_rounds_to_cents")})
    ev = check(repo)
    assert ev["mutation"]["ran"] and ev["mutation"]["lost"] == []
    assert ev["verdict"] == "VERIFIED"


def test_not_run_when_tests_are_untouched(tmp_path):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": CODE.replace("ValueError('bad percent')", "ValueError('bad')")})
    ev = check(repo)
    assert not ev["mutation"]["ran"] and "didn't touch tests" in ev["mutation"]["reason"]


def test_not_run_without_mutate_flag(tmp_path):
    repo = project(tmp_path)
    receipt = repo.parent / "r.json"
    main(["check", "--repo", str(repo), "--base", "main", "--json", str(receipt)])
    assert json.loads(receipt.read_text())["mutation"] is None


def test_new_tests_that_cannot_run_on_old_code_are_reported_not_counted(tmp_path):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": CODE + "\n\ndef double(x):\n    return 2 * x\n",
                 "tests/test_core.py": "from shop.core import double\n\n\ndef test_double():\n"
                                       "    assert double(2) == 4\n"})
    report = mutation_check(repo, comparison_point(repo, "main"), changed_files(repo, "main"),
                            select_tests(repo, changed_files(repo, "main")))
    # The only changed code is new (no old lines), so there is nothing to mutate.
    assert not report.ran


@pytest.mark.parametrize("budget", [0.0])
def test_time_budget_stops_early(tmp_path, budget):
    repo = project(tmp_path)
    write(repo, {"shop/core.py": BUG, "tests/test_core.py": TESTS.replace("== 16.99", "> 0")})
    ref = comparison_point(repo, "main")
    changes = changed_files(repo, "main")
    report = mutation_check(repo, ref, changes, select_tests(repo, changes), budget_s=budget)
    assert report.ran and report.partial and report.mutants == 0

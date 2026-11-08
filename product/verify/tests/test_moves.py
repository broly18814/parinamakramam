"""Self-checks for the move-aware comparison (pkv/moves.py, defect D4).

Each honest reorganisation must be recognised as a move; each look-alike
cheat must stay SUSPICIOUS. These examples are deliberately different from
BENCH-003's, so the practice set stays a fair test.
"""

from __future__ import annotations

from helpers import commit, write
from pkv.cli import main
from pkv.gitdiff import changed_files, comparison_point
from pkv.tamper import find_tampering

API = "from app import api\n\n\n"
GET = "def test_get():\n    assert api.get()\n    assert api.get() is not None\n"


def findings(repo):
    ref = comparison_point(repo, None)
    return find_tampering(repo, changed_files(repo), ref)


def kinds(repo, severity):
    return {f.kind for f in findings(repo) if f.severity == severity}


def check(repo):
    return main(["check", "--repo", str(repo)])


def delete(repo, *paths):
    for rel in paths:
        (repo / rel).unlink()


def base(repo):
    write(repo, {"tests/test_api.py": API + GET})
    commit(repo, "two checks in test_get")


# ---------- honest reorganisations ----------

def test_a_test_moved_to_a_new_file_is_a_move(repo):
    base(repo)
    write(repo, {"tests/test_api.py": API + "def test_other():\n    assert api.get() or True\n",
                 "tests/test_api_get.py": API + GET})
    assert "test-removed" not in kinds(repo, "suspicious")
    assert "test-moved" in kinds(repo, "notice")


def test_a_renamed_test_with_the_same_body_is_a_move(repo):
    base(repo)
    write(repo, {"tests/test_api.py": API + GET.replace("test_get", "test_get_returns_a_user")})
    assert check(repo) == 0


def test_a_migration_to_unittest_is_a_move(repo):
    base(repo)
    write(repo, {"tests/test_api.py": ("import unittest\n\nfrom app import api\n\n\n"
                                       "class TestApi(unittest.TestCase):\n"
                                       "    def test_get(self):\n"
                                       "        self.assertTrue(api.get())\n"
                                       "        self.assertIsNotNone(api.get())\n")})
    assert check(repo) == 0


def test_a_split_test_file_is_a_move(repo):
    base(repo)
    delete(repo, "tests/test_api.py")
    write(repo, {"tests/test_api_a.py": API + GET,
                 "tests/test_api_b.py": API + "def test_more():\n    assert api.get()\n"})
    assert "test-file-deleted" not in kinds(repo, "suspicious")
    assert "test-file-moved" in kinds(repo, "notice")


def test_pytest_raises_and_assert_raises_are_the_same_check(repo):
    write(repo, {"tests/test_raises.py": ("import pytest\n\n\ndef test_bad():\n"
                                          "    with pytest.raises(ZeroDivisionError) as e:\n        1 / 0\n"
                                          "    assert 'zero' in str(e.value)\n")})
    commit(repo, "raises test")
    write(repo, {"tests/test_raises.py": ("import unittest\n\n\nclass TestRaises(unittest.TestCase):\n"
                                          "    def test_bad(self):\n"
                                          "        with self.assertRaises(ZeroDivisionError) as e:\n"
                                          "            1 / 0\n"
                                          "        self.assertIn('zero', str(e.exception))\n")})
    assert "test-removed" not in kinds(repo, "suspicious")


# ---------- cheats that look like reorganisations ----------

def test_moving_a_test_and_dropping_a_check_is_still_suspicious(repo):
    base(repo)
    write(repo, {"tests/test_api.py": API + "def test_other():\n    assert True or api.get()\n",
                 "tests/test_api_get.py": API + "def test_get():\n    assert api.get()\n"})
    assert "test-removed" in kinds(repo, "suspicious")


def test_moving_a_test_into_a_file_pytest_ignores_is_still_suspicious(repo):
    base(repo)
    write(repo, {"tests/test_api.py": API + "def test_other():\n    assert api.get() or True\n",
                 "tests/api_cases.py": API + GET})
    assert "test-removed" in kinds(repo, "suspicious")


def test_moving_a_test_and_skipping_it_is_still_suspicious(repo):
    base(repo)
    write(repo, {"tests/test_api.py": API + "def test_other():\n    assert api.get() or True\n",
                 "tests/test_api_get.py": "import pytest\n" + API + "@pytest.mark.skip\n" + GET})
    assert "test-removed" in kinds(repo, "suspicious")


def test_skipping_the_whole_destination_file_is_still_suspicious(repo):
    base(repo)
    write(repo, {"tests/test_api.py": API + "def test_other():\n    assert api.get() or True\n",
                 "tests/test_api_get.py": "import pytest\n" + API + "pytestmark = pytest.mark.skip\n\n\n" + GET})
    assert "test-removed" in kinds(repo, "suspicious")


def test_moving_a_test_and_swallowing_its_failure_is_still_suspicious(repo):
    base(repo)
    swallowed = ("def test_get():\n    try:\n        assert api.get()\n        assert api.get() is not None\n"
                 "    except AssertionError:\n        pass\n")
    write(repo, {"tests/test_api.py": API + "def test_other():\n    assert api.get() or True\n",
                 "tests/test_api_get.py": API + swallowed})
    assert "test-removed" in kinds(repo, "suspicious")


def test_moving_a_table_driven_test_without_its_failing_row_is_still_suspicious(repo):
    table = ("import pytest\n\nfrom app.utils import slug\n\n\n"
             "@pytest.mark.parametrize('text, out', [('A', 'a'), ('B', 'b'), ('C D', 'c d')])\n"
             "def test_slug_table(text, out):\n    assert slug(text) == out\n")
    write(repo, {"tests/test_table.py": table})
    commit(repo, "table")
    delete(repo, "tests/test_table.py")
    write(repo, {"tests/test_table2.py": table.replace(", ('C D', 'c d')", "")})
    assert "test-file-deleted" in kinds(repo, "suspicious")


def test_the_same_check_lines_about_different_code_do_not_excuse_a_deletion(repo):
    # `assert result` is a common line. Deleting test_get while adding a test
    # whose identical check lines are about *other* code is not a move.
    write(repo, {"tests/test_api.py": API + ("def test_get():\n    result = api.get()\n"
                                             "    assert result\n    assert result is not None\n")})
    commit(repo, "test_get")
    write(repo, {"tests/test_api.py": API + ("def test_other():\n    result = len('abc')\n    extra = 2\n"
                                             "    assert result\n    assert result is not None\n")})
    assert "test-removed" in kinds(repo, "suspicious")


def test_a_test_folded_whole_into_a_bigger_test_is_a_move(repo):
    # The opposite case: the original's whole body, in order, inside a larger test.
    base(repo)
    bigger = ("def test_everything():\n    data = {'a': 1}\n    assert api.get()\n"
              "    assert api.get() is not None\n    assert data['a'] == 1\n")
    write(repo, {"tests/test_api.py": API + bigger})
    assert "test-removed" not in kinds(repo, "suspicious")


def test_one_reappearing_check_cannot_excuse_two_deleted_tests(repo):
    write(repo, {"tests/test_api.py": (API + "def test_one():\n    assert api.get()\n\n\n"
                                       "def test_two():\n    assert api.get()\n")})
    commit(repo, "two tests with the same check")
    write(repo, {"tests/test_api.py": API + "def test_one():\n    assert api.get()\n",
                 "tests/test_api_two.py": API + "def test_three():\n    assert 1 + 1 == 2\n"})
    assert "test-removed" in kinds(repo, "suspicious")  # test_two's check reappears nowhere new


def test_deleting_a_test_with_no_checks_needs_a_look_alike_destination(repo):
    write(repo, {"tests/test_smoke.py": API + "def test_smoke():\n    api.get()\n"})
    commit(repo, "a smoke test")
    write(repo, {"tests/test_smoke.py": API + "def test_new():\n    len('abc')\n"})
    assert "test-removed" in kinds(repo, "suspicious")

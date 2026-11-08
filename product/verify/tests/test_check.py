"""Self-checks for running tests, spotting tampering, the verdict, and receipts.

Every test plants one known situation in a throw-away project (a failing
test, a deleted test, a secret in the environment, an untested change...)
and checks that pkv reports exactly that.
"""

from __future__ import annotations

import json

from helpers import commit, git, write
from pkv.cli import main
from pkv.gitdiff import changed_files, comparison_point
from pkv.runner import run_tests
from pkv.tamper import find_tampering, read_tests


def kinds(repo_path, severity=None):
    ref = comparison_point(repo_path, None)
    found = find_tampering(repo_path, changed_files(repo_path), ref)
    return {f.kind for f in found if severity is None or f.severity == severity}


def check(repo_path, *extra):
    return main(["check", "--repo", str(repo_path), *extra])


# ---------- running tests ----------

def test_runner_records_a_clean_pass(repo):
    rec = run_tests(repo, ["tests/test_utils.py", "tests/test_api.py"])
    assert rec.outcome == "passed" and rec.exit_codes == [0]
    assert rec.counts["passed"] == 2 and rec.counts["failed"] == 0
    assert rec.tree_hash_before == rec.tree_hash_after and not rec.changed_during_run


def test_runner_records_failures_by_name(repo):
    write(repo, {"tests/test_utils.py":
                 "from app.utils import slug\n\ndef test_slug():\n    assert slug('A') == 'A'\n"})
    rec = run_tests(repo, ["tests/test_utils.py"])
    assert rec.outcome == "failed" and rec.counts["failed"] == 1
    assert rec.failed_tests == ["tests.test_utils::test_slug"]


def test_runner_stops_tests_that_hang(repo):
    write(repo, {"tests/test_slow.py": "import time\n\ndef test_slow():\n    time.sleep(30)\n"})
    rec = run_tests(repo, ["tests/test_slow.py"], timeout=2)
    assert rec.timed_out and rec.outcome == "timed-out" and rec.duration_s < 20


def test_runner_hides_secrets_unless_asked(repo, monkeypatch):
    monkeypatch.setenv("PKV_FAKE_SECRET", "hunter2")
    write(repo, {"tests/test_env.py":
                 "import os\n\ndef test_no_secret():\n    assert os.environ.get('PKV_FAKE_SECRET') is None\n"})
    assert run_tests(repo, ["tests/test_env.py"]).outcome == "passed"  # secret not visible
    rec = run_tests(repo, ["tests/test_env.py"], keep_env=["PKV_FAKE_SECRET"])
    assert rec.outcome == "failed"  # visible only when the user explicitly allows it


def test_runner_notices_files_changing_during_the_run(repo):
    write(repo, {"tests/test_writer.py":
                 "from pathlib import Path\n\ndef test_w():\n    Path('app/generated.py').write_text('X=1')\n"})
    rec = run_tests(repo, ["tests/test_writer.py"])
    assert rec.changed_during_run and rec.files_changed_during_run == ["app/generated.py"]


# ---------- spotting tampering ----------

TWO_TESTS = ("from app.utils import slug\n\n"
             "def test_lower():\n    assert slug('A') == 'a'\n    assert slug('B') == 'b'\n\n"
             "def test_same():\n    assert slug('a') == 'a'\n")


def with_two_tests(repo):
    write(repo, {"tests/test_utils.py": TWO_TESTS})
    commit(repo, "two tests")


def test_removed_test_is_suspicious(repo):
    with_two_tests(repo)
    write(repo, {"tests/test_utils.py": TWO_TESTS.split("def test_same")[0]})
    assert "test-removed" in kinds(repo, "suspicious")


def test_fewer_assertions_is_suspicious(repo):
    with_two_tests(repo)
    write(repo, {"tests/test_utils.py": TWO_TESTS.replace("    assert slug('B') == 'b'\n", "")})
    assert "fewer-checks" in kinds(repo, "suspicious")


def test_new_skip_markers_are_suspicious(repo):
    with_two_tests(repo)
    write(repo, {"tests/test_utils.py": "import pytest\n" + TWO_TESTS.replace(
        "def test_same", "@pytest.mark.skip(reason='later')\ndef test_same")})
    assert "skip-added" in kinds(repo, "suspicious")
    write(repo, {"tests/test_utils.py": "import pytest\npytestmark = pytest.mark.xfail\n" + TWO_TESTS})
    assert "skip-added" in kinds(repo, "suspicious")


def test_check_that_can_never_fail_is_suspicious(repo):
    with_two_tests(repo)
    write(repo, {"tests/test_utils.py": TWO_TESTS.replace("assert slug('a') == 'a'", "assert True")})
    assert "always-passes" in kinds(repo, "suspicious")


def test_deleted_or_hidden_test_files_are_suspicious(repo):
    (repo / "tests/test_utils.py").unlink()
    assert "test-file-deleted" in kinds(repo, "suspicious")
    git(repo, "checkout", "--", "tests/test_utils.py")
    git(repo, "mv", "tests/test_utils.py", "tests/utils_checks.py")
    assert "test-file-hidden" in kinds(repo, "suspicious")


def test_expected_values_changed_with_code_is_a_notice(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n",
                 "tests/test_utils.py":
                 "from app.utils import slug\n\ndef test_slug():\n    assert slug('A') == 'A'\n"})
    assert "expected-values-changed" in kinds(repo, "notice")
    assert not kinds(repo, "suspicious")


def test_honest_improvement_raises_nothing_suspicious(repo):
    with_two_tests(repo)
    write(repo, {"tests/test_utils.py": TWO_TESTS + "\ndef test_more():\n    assert slug('C') == 'c'\n"})
    assert not kinds(repo, "suspicious")


def test_shared_settings_and_sensitive_files_are_notices(repo):
    write(repo, {"tests/conftest.py": "import pytest\n", "app/auth.py": "OK = True\n"})
    assert {"shared-settings", "sensitive-file"} <= kinds(repo, "notice")


def test_unittest_style_checks_are_counted():
    src = ("import unittest\n\nclass TestX(unittest.TestCase):\n"
           "    def test_a(self):\n        self.assertEqual(1, 1)\n        self.assertTrue(True)\n"
           "    def test_b(self):\n        self.skipTest('no')\n")
    tests, _ = read_tests(src)
    assert tests["TestX::test_a"].asserts == 2
    assert tests["TestX::test_b"].skips == 1


# ---------- verdicts and receipts (the whole check) ----------

def test_good_change_is_verified_and_receipt_goes_stale_after_edit(repo, capsys, tmp_path):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower().strip()\n"})
    receipt = tmp_path / "receipt.json"
    assert check(repo, "--json", str(receipt)) == 0
    out = capsys.readouterr().out
    assert "# ✅ VERIFIED" in out and "tests/test_utils.py uses app/utils.py" in out
    ev = json.loads(receipt.read_text())
    assert ev["verdict"] == "VERIFIED" and ev["run"]["counts"]["passed"] == 1
    assert main(["fresh", str(receipt), "--repo", str(repo)]) == 0
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n"})
    assert main(["fresh", str(receipt), "--repo", str(repo)]) == 1
    assert "STALE" in capsys.readouterr().out


def test_failing_change_is_failed(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    assert check(repo) == 1
    assert "# ❌ FAILED" in capsys.readouterr().out


def test_passing_but_weakened_tests_are_suspicious(repo, capsys):
    # The classic trick: break the code, then delete the check that catches it.
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n",
                 "tests/test_utils.py": "from app.utils import slug\n\ndef test_slug():\n    pass\n"})
    assert check(repo) == 4
    out = capsys.readouterr().out
    assert "# ⚠️ SUSPICIOUS" in out and "now checks less: 1 checks before, 0 now" in out


def test_change_no_test_reaches_is_unverified(repo, capsys):
    write(repo, {"app/orphan.py": "def f():\n    return 1\n"})
    assert check(repo) == 3
    assert "changed code that no test checks: app/orphan.py" in capsys.readouterr().out


def test_no_changes_and_docs_only_are_verified(repo, capsys):
    assert check(repo) == 0
    write(repo, {"README.md": "# new words\n"})
    assert check(repo) == 0
    assert "nothing that tests could check was changed" in capsys.readouterr().out


def test_all_tests_skipped_is_unverified(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower() \n",
                 "tests/conftest.py": "import pytest\n\ndef pytest_collection_modifyitems(items):\n"
                 "    for i in items:\n        i.add_marker(pytest.mark.skip(reason='x'))\n"})
    assert check(repo) == 3
    assert "every selected test was skipped" in capsys.readouterr().out


def test_code_changing_during_the_run_is_unverified(repo, capsys):
    # Added after a deliberate-break test showed nothing covered this verdict.
    write(repo, {"tests/test_utils.py":
                 "from pathlib import Path\nfrom app.utils import slug\n\n"
                 "def test_slug():\n    Path('app/extra.py').write_text('X = 2')\n"
                 "    assert slug('A') == 'a'\n"})
    assert check(repo) == 3
    assert "files changed while the tests were running (app/extra.py)" in capsys.readouterr().out


def test_no_run_is_unverified(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower()  # tidy\n"})
    assert check(repo, "--no-run") == 3
    assert "tests were selected but not run (--no-run was used)" in capsys.readouterr().out


def test_receipts_inside_the_project_do_not_count_as_changes(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower().strip()\n"})
    assert check(repo, "--json", str(repo / ".pkv/receipt.json"),
                 "--md", str(repo / "receipt.md")) == 0
    assert (repo / ".pkv/receipt.json").exists() and (repo / "receipt.md").exists()
    assert main(["fresh", str(repo / ".pkv/receipt.json"), "--repo", str(repo)]) == 0
    capsys.readouterr()
    assert check(repo, "--json", str(repo / ".pkv/receipt.json"), "--md", str(repo / "receipt.md")) == 0
    out = capsys.readouterr().out
    assert ".pkv/receipt.json" not in out.split("## What changed")[1].split("##")[0]


# ---------- found by running pkv on our own project (dogfooding) ----------

def test_file_reached_by_a_second_route_is_not_called_untested(repo):
    # Bug: only one route per test was remembered, so other changed files a
    # test depends on were wrongly reported as "no test checks this".
    write(repo, {"app/models.py": "class User:\n    a = 1\n",
                 "app/api.py": "from app.models import User\n\ndef get():\n    return User()  # v2\n"})
    from pkv.affected import select_tests
    sel = select_tests(repo, changed_files(repo))
    assert sel.untested_changes == []
    assert "also depends on 1 other changed file" in sel.reasons["tests/test_api.py"]


def test_receipt_shows_the_command_once_and_cleanly(repo):
    rec = run_tests(repo, ["tests/test_utils.py"])
    [cmd] = rec.commands
    assert cmd.count("--junitxml=<temporary file>") == 1
    assert cmd[-2:] == ["--", "tests/test_utils.py"]
    assert "-p" in cmd and "no:cacheprovider" in cmd


def test_sub_projects_with_their_own_settings_run_separately(repo):
    # Found by dogfooding: one pytest run can use only one settings file, so
    # tests from two sub-projects in one repository broke each other.
    write(repo, {"tool/pytest.ini": "[pytest]\npythonpath = .\n",
                 "tool/mylib.py": "def f():\n    return 3\n",
                 "tool/tests/test_mylib.py": "from mylib import f\n\ndef test_f():\n    assert f() == 3\n"})
    from pkv.runner import group_by_project
    tests = ["tests/test_utils.py", "tool/tests/test_mylib.py"]
    assert group_by_project(repo, tests) == [("", ["tests/test_utils.py"]),
                                             ("tool", ["tool/tests/test_mylib.py"])]
    rec = run_tests(repo, tests)
    assert rec.outcome == "passed" and rec.counts["passed"] == 2 and len(rec.commands) == 2


def test_tests_that_cannot_load_are_reported_as_such(repo, capsys):
    write(repo, {"tests/test_utils.py": "import module_that_does_not_exist\nfrom app.utils import slug\n\n"
                 "def test_slug():\n    assert slug('A') == 'a'\n"})
    assert check(repo) == 1
    out = capsys.readouterr().out
    assert "1 test file(s) could not even be loaded" in out
    assert "Last lines of the test output" in out and "module_that_does_not_exist" in out


def test_label_without_value_does_not_crash_the_detector():
    # Regression (found by strict type checking): `pytestmark: list` has no
    # value, and the detector used to crash on it instead of giving a verdict.
    tests, module_skips = read_tests("pytestmark: list\n\ndef test_a():\n    assert 1 == 1\n")
    assert module_skips == 0 and tests["test_a"].asserts == 1


# ---------- rules added in 0.1.0 (each with an honest look-alike) ----------

def _info(src: str, name: str = "test_x"):
    return read_tests(src)[0][name]


def test_swallowed_failures_are_counted_and_honest_try_is_not():
    hidden = "def test_x():\n    try:\n        assert f() == 1\n    except AssertionError:\n        pass\n"
    broad = "def test_x():\n    try:\n        assert f() == 1\n    except Exception:\n        pass\n"
    suppress = ("import contextlib\ndef test_x():\n    with contextlib.suppress(AssertionError):\n"
                "        assert f() == 1\n")
    reraised = "def test_x():\n    try:\n        assert f() == 1\n    except AssertionError:\n        raise\n"
    expects_error = ("import pytest\ndef test_x():\n    try:\n        parse('x')\n    except ValueError:\n"
                     "        pass\n    else:\n        pytest.fail('no error')\n")
    cleanup = "def test_x():\n    try:\n        assert f() == 1\n    finally:\n        close()\n"
    assert _info(hidden).swallowed == 1 and _info(broad).swallowed == 1 and _info(suppress).swallowed == 1
    assert _info(reraised).swallowed == 0 and _info(expects_error).swallowed == 0
    assert _info(cleanup).swallowed == 0


def test_exact_and_loose_checks_are_told_apart():
    assert _info("def test_x():\n    assert f() == 90\n").exact == 1
    assert _info("def test_x():\n    assert f() > 0\n").exact == 0
    assert _info("def test_x():\n    assert f() is not None\n").exact == 0
    assert _info("def test_x():\n    assert f() == pytest.approx(0.1)\n").exact == 1
    tuple_merge = _info("def test_x():\n    assert (f(1), f(2)) == (3, 4)\n")
    assert tuple_merge.asserts == 2 and tuple_merge.exact == 2  # two exact checks, not one
    src = ("import unittest\nclass TestX(unittest.TestCase):\n    def test_x(self):\n"
           "        self.assertEqual(f(), 0)\n        self.assertTrue(g())\n")
    info = read_tests(src)[0]["TestX::test_x"]
    assert info.asserts == 2 and info.exact == 1


def test_parametrize_cases_are_counted():
    three = ("import pytest\n@pytest.mark.parametrize('a, b', [(1, 1), (2, 2), pytest.param(3, 3, id='c')])\n"
             "def test_x(a, b):\n    assert a == b\n")
    stacked = ("import pytest\n@pytest.mark.parametrize('a', [1, 2])\n@pytest.mark.parametrize('b', [1, 2, 3])\n"
               "def test_x(a, b):\n    assert a\n")
    computed = "import pytest\n@pytest.mark.parametrize('a', make_cases())\ndef test_x(a):\n    assert a\n"
    assert _info(three).cases == 3 and _info(stacked).cases == 6 and _info(computed).cases is None
    assert _info("def test_x():\n    assert 1 == 1\n").cases == 1


def test_weakened_swallowed_and_trimmed_tests_are_suspicious_in_a_real_change(repo):
    write(repo, {"tests/test_cases.py": (
        "import pytest\nfrom app.utils import slug\n\n"
        "@pytest.mark.parametrize('s, out', [('A', 'a'), ('B', 'b'), ('C', 'c')])\n"
        "def test_table(s, out):\n    assert slug(s) == out\n\n"
        "def test_exact():\n    assert slug('X') == 'x'\n\n"
        "def test_guarded():\n    assert slug('Y') == 'y'\n")})
    commit(repo, "more tests")
    write(repo, {"tests/test_cases.py": (
        "import pytest\nfrom app.utils import slug\n\n"
        "@pytest.mark.parametrize('s, out', [('A', 'a'), ('B', 'b')])\n"
        "def test_table(s, out):\n    assert slug(s) == out\n\n"
        "def test_exact():\n    assert slug('X') is not None\n\n"
        "def test_guarded():\n    try:\n        assert slug('Y') == 'y'\n    except Exception:\n        pass\n")})
    assert {"fewer-cases", "check-weakened", "failure-swallowed"} <= kinds(repo, "suspicious")


def test_test_deleted_with_its_code_is_a_notice_but_alone_is_suspicious(repo):
    (repo / "app/utils.py").unlink()
    (repo / "tests/test_utils.py").unlink()
    assert "test-deleted-with-code" in kinds(repo, "notice")
    assert "test-file-deleted" not in kinds(repo, "suspicious")
    git(repo, "checkout", "--", "app/utils.py")
    assert "test-file-deleted" in kinds(repo, "suspicious")  # the code it tested still exists


def test_tests_removed_by_settings_are_caught_at_run_time(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n",  # breaks test_slug
                 "pyproject.toml": "[tool.pytest.ini_options]\naddopts = \"-k 'not slug'\"\n"})
    assert check(repo) == 4
    out = capsys.readouterr().out
    assert "test_slug in tests/test_utils.py was selected but pytest never ran it" in out


def test_tests_dropped_by_a_conftest_hook_are_caught_at_run_time(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n",
                 "tests/conftest.py": ("def pytest_collection_modifyitems(items):\n"
                                       "    items[:] = [i for i in items if 'slug' not in i.name]\n")})
    assert check(repo) == 4
    assert "never ran it" in capsys.readouterr().out


def test_conftest_hook_that_only_labels_tests_is_not_flagged(repo, capsys):
    write(repo, {"tests/conftest.py": ("def pytest_collection_modifyitems(items):\n"
                                       "    for i in items:\n        i.add_marker('fast')\n"),
                 "pyproject.toml": "[tool.pytest.ini_options]\nmarkers = ['fast: quick tests']\n"})
    assert check(repo) == 0
    assert "never ran" not in capsys.readouterr().out


def test_whole_file_skipped_on_purpose_is_not_reported_as_not_run(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower()  # same\n",
                 "tests/test_utils.py": ("import pytest\npytest.importorskip('no_such_module_xyz')\n"
                                         "from app.utils import slug\n\ndef test_slug():\n"
                                         "    assert slug('A') == 'a'\n")})
    assert check(repo) == 3
    out = capsys.readouterr().out
    assert "never ran" not in out  # a deliberate whole-file skip is not "removed"
    assert "pytest found no tests to run" in out

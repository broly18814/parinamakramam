"""Self-checks for pkv.

Each test builds a tiny throw-away git project in a temporary folder, makes
a change, and checks that pkv picks exactly the right tests, for the right
reason. Nothing outside the temporary folder is touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from helpers import commit, git, write
from pkv.affected import is_test_file, select_tests
from pkv.cli import main
from pkv.gitdiff import GitError, changed_files, tree_hash
from pkv.imports import build_graph, module_names, read_imports


def affected(repo: Path, base: str | None = None):
    return select_tests(repo, changed_files(repo, base))


# ---------- reading changes ----------

def test_no_changes_means_nothing_selected(repo):
    sel = affected(repo)
    assert sel.changes == [] and sel.tests == [] and not sel.run_all


def test_changed_files_sees_every_kind_of_change(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n",  # modified
                 "app/new.py": "X = 1\n"})                                  # new, untracked
    (repo / "README.md").unlink()                                          # deleted
    git(repo, "mv", "app/models.py", "app/model.py")                        # renamed
    got = {(c.status, c.path, c.old_path) for c in changed_files(repo)}
    assert ("modified", "app/utils.py", None) in got
    assert ("added", "app/new.py", None) in got
    assert ("deleted", "README.md", None) in got
    assert ("renamed", "app/model.py", "app/models.py") in got


def test_base_branch_compares_from_where_work_branched_off(repo):
    git(repo, "checkout", "-q", "-b", "feature")
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n"})
    commit(repo, "feature work")
    git(repo, "checkout", "-q", "main")
    write(repo, {"app/models.py": "class User:\n    x = 1\n"})
    commit(repo, "unrelated main work")
    git(repo, "checkout", "-q", "feature")
    paths = {c.path for c in changed_files(repo, base="main")}
    assert paths == {"app/utils.py"}  # main's later change is not ours


def test_unknown_base_is_a_clear_error(repo):
    with pytest.raises(GitError, match="cannot find"):
        changed_files(repo, base="no-such-branch")


def test_not_a_repo_is_a_clear_error(tmp_path):
    with pytest.raises(GitError, match="not inside a git repository"):
        changed_files(tmp_path)


# ---------- fingerprint ----------

def test_fingerprint_changes_with_code_and_leaves_staging_alone(repo):
    before = tree_hash(repo)
    assert tree_hash(repo) == before  # same code, same fingerprint
    write(repo, {"app/utils.py": "def slug(s):\n    return s  # edited\n"})
    status_before = git(repo, "status", "--porcelain")
    after = tree_hash(repo)
    assert after != before
    assert git(repo, "status", "--porcelain") == status_before  # nothing got staged
    write(repo, {"brand_new.py": ""})
    assert tree_hash(repo) != after  # new files count too


# ---------- the import map ----------

def test_module_names_follow_python_package_rules(repo):
    assert module_names("app/models.py", repo)[0] == "app.models"
    assert module_names("app/__init__.py", repo)[0] == "app"
    assert module_names("tests/helpers.py", repo)[0] == "helpers"  # no __init__.py
    assert "tests.helpers" in module_names("tests/helpers.py", repo)[1]


def test_relative_imports_are_resolved(repo):
    g = build_graph(repo)
    assert "app/models.py" in g.deps["app/sub/deep.py"]


def test_importing_a_submodule_also_depends_on_its_package(repo):
    g = build_graph(repo)
    assert {"app/__init__.py", "app/models.py"} <= g.deps["tests/test_models.py"]


def test_src_layout_is_understood(tmp_path):
    r = tmp_path / "p"
    write(r, {"src/lib/__init__.py": "", "src/lib/core.py": "",
              "tests/test_core.py": "from lib import core\n"})
    g = build_graph(r)
    assert "src/lib/core.py" in g.deps["tests/test_core.py"]


def test_dynamic_imports_are_flagged_and_bad_syntax_is_reported(tmp_path):
    names, dyn = read_imports("import importlib\nm = importlib.import_module('x')\n", "m", False)
    assert dyn and "importlib" in names
    r = tmp_path / "p"
    write(r, {"broken.py": "def (:\n"})
    g = build_graph(r)
    assert "broken.py" in g.unreadable


def test_test_file_naming_rule():
    assert is_test_file("tests/test_api.py") and is_test_file("x/api_test.py")
    assert not is_test_file("tests/helpers.py") and not is_test_file("tests/conftest.py")


# ---------- choosing tests ----------

def test_change_reaches_tests_directly_and_through_other_files(repo):
    write(repo, {"app/models.py": "class User:\n    name = 'x'\n"})
    sel = affected(repo)
    # test_models imports models directly; test_api via app.api; test_deep via
    # app.sub.deep's relative import. test_utils and test_helpers_used don't.
    assert sel.tests == ["tests/test_api.py", "tests/test_deep.py", "tests/test_models.py"]
    assert sel.reasons["tests/test_api.py"] == (
        "tests/test_api.py uses app/api.py, which uses app/models.py, which was modified")
    assert not sel.run_all


def test_changed_test_file_selects_itself(repo):
    write(repo, {"tests/test_utils.py": "def test_slug():\n    assert True\n"})
    sel = affected(repo)
    assert sel.tests == ["tests/test_utils.py"]
    assert sel.reasons["tests/test_utils.py"] == "tests/test_utils.py was modified"


def test_helper_next_to_tests_is_traced(repo):
    write(repo, {"tests/helpers.py": "def make():\n    return 2\n"})
    assert affected(repo).tests == ["tests/test_helpers_used.py"]


def test_shared_test_settings_affect_all_tests_below_them(repo):
    write(repo, {"tests/conftest.py": "import pytest\n"})
    sel = affected(repo)
    assert sel.tests == sel.all_tests and not sel.run_all
    assert "shared test settings in tests/conftest.py" in sel.reasons["tests/test_utils.py"]


def test_settings_file_change_means_run_everything(repo):
    write(repo, {"pyproject.toml": "[project]\nname='sample2'\n"})
    sel = affected(repo)
    assert sel.run_all and sel.tests == sel.all_tests
    assert "pyproject.toml is a project settings file" in sel.run_all_reasons[0]


def test_settings_file_in_a_subfolder_only_affects_that_folder(repo):
    # Found by running pkv on our own repository: a sub-project's settings
    # file wrongly forced every test in the whole repository to run.
    write(repo, {"tools/pyproject.toml": "[project]\nname='tool'\n",
                 "tools/tests/test_tool.py": "def test_t():\n    assert True\n"})
    commit(repo, "add sub-project")
    write(repo, {"tools/pyproject.toml": "[project]\nname='tool2'\n"})
    sel = affected(repo)
    assert not sel.run_all
    assert sel.tests == ["tools/tests/test_tool.py"]
    assert "whose settings file tools/pyproject.toml was changed" in sel.reasons[sel.tests[0]]


def test_documentation_change_runs_nothing(repo):
    write(repo, {"README.md": "# changed\n"})
    sel = affected(repo)
    assert sel.tests == [] and sel.no_effect == ["README.md"] and not sel.run_all


def test_unknown_data_file_is_treated_safely(repo):
    write(repo, {"app/data.json": "{}"})
    sel = affected(repo)
    assert sel.run_all and "not Python code" in sel.run_all_reasons[0]


def test_deleting_a_module_selects_tests_that_imported_it(repo):
    (repo / "app/utils.py").unlink()
    sel = affected(repo)
    assert sel.tests == ["tests/test_utils.py"]
    assert "app/utils.py was deleted" in sel.reasons["tests/test_utils.py"]


def test_deleted_test_file_is_reported(repo):
    (repo / "tests/test_utils.py").unlink()
    sel = affected(repo)
    assert sel.removed_tests == ["tests/test_utils.py"]
    assert "tests/test_utils.py" not in sel.tests


def test_renamed_module_affects_old_importers(repo):
    git(repo, "mv", "app/utils.py", "app/textutils.py")
    sel = affected(repo)
    assert "tests/test_utils.py" in sel.tests  # its import now points nowhere


def test_unreadable_changed_file_means_run_everything(repo):
    write(repo, {"app/utils.py": "def slug(:\n"})
    sel = affected(repo)
    assert sel.run_all and "could not be read" in sel.run_all_reasons[0]


# ---------- the command ----------

def test_command_prints_plain_report(repo, capsys):
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n"})
    assert main(["affected", "--repo", str(repo)]) == 0
    out = capsys.readouterr().out
    assert "Tests to run: 1 of 5" in out
    assert "why: tests/test_utils.py uses app/utils.py, which was modified" in out
    assert "python -m pytest tests/test_utils.py" in out


def test_command_json_and_errors(repo, tmp_path, capsys):
    write(repo, {"app/utils.py": "x = 1\n"})
    assert main(["affected", "--repo", str(repo), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["tests"] == ["tests/test_utils.py"]
    empty = tmp_path / "not_a_repo"
    empty.mkdir()
    assert main(["affected", "--repo", str(empty)]) == 2
    assert "not inside a git repository" in capsys.readouterr().err


def test_command_fingerprint(repo, capsys):
    assert main(["fingerprint", "--repo", str(repo)]) == 0
    assert capsys.readouterr().out.strip() == tree_hash(repo)


def test_fingerprint_sees_same_size_edits_made_in_the_same_second(repo):
    """Regression for the "racy git" bug found by BENCH-001.

    git compares file save times to the whole second. If a file is edited
    to the same size within the same second it was committed, and the
    fingerprint is taken in a LATER second, a copied index makes git trust
    its cached record and fingerprint the OLD contents. We create exactly
    that situation and require the fingerprint to see the new contents.
    """
    import os
    import time

    target = repo / "app/utils.py"
    for attempt in range(5):
        time.sleep(1 - (time.time() % 1) + 0.01)  # start just after a second boundary
        write(repo, {"app/utils.py": f"X = {attempt}\n"})
        commit(repo, f"v{attempt}")
        old_second = int(os.stat(target).st_mtime)
        target.write_text(f"Y = {attempt}\n")  # same size, same second
        if int(os.stat(target).st_mtime) != old_second:
            continue  # the edit slipped into the next second; try again
        time.sleep(1.1)  # take the fingerprint in a later second
        head_tree = git(repo, "rev-parse", "HEAD^{tree}").strip()
        assert tree_hash(repo) != head_tree, "fingerprint described the old contents"
        return
    pytest.skip("could not create the same-second edit on this machine")

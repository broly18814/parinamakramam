"""A3's acceptance tests (docs/product/A3-design.md, "When it's done"): the clean-copy run,
the sealed receipt, and `pkv fresh --rerun`."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys

import pytest
from helpers import commit, write
from pkv.cli import main
from pkv.report import digest

GOOD = {"app/utils.py": "def slug(s):\n    return s.lower().strip()\n"}


def check(repo, *extra):
    return main(["check", "--repo", str(repo), *extra])


def fresh(receipt, repo, *extra):
    return main(["fresh", str(receipt), "--repo", str(repo), *extra])


def make_receipt(repo, tmp_path, *extra):
    write(repo, GOOD)
    receipt = tmp_path / "receipt.json"
    assert check(repo, "--json", str(receipt), *extra) == 0
    return receipt


def leftover_project(repo):
    """A test that only passes because of a file git ignores (a leftover in the working folder)."""
    write(repo, {".gitignore": "app/_generated.py\n",
                 "app/_generated.py": "VALUE = 'a'\n",
                 "app/utils.py": "from app._generated import VALUE\n\ndef slug(s):\n    return s.lower()\n",
                 "tests/test_utils.py": "from app.utils import slug\nfrom app._generated import VALUE\n\n"
                                        "def test_slug():\n    assert slug('A') == VALUE\n"})


# ---------- the seal ----------

def test_a_new_receipt_is_sealed_and_reads_as_intact(repo, tmp_path, capsys):
    receipt = make_receipt(repo, tmp_path)
    ev = json.loads(receipt.read_text())
    assert ev["schema"] == "pkv-evidence/1" and ev["digest"] == digest(ev)
    assert ev["environment"]["python"] and ev["environment"]["pytest"]
    assert fresh(receipt, repo) == 0
    assert "its seal is intact" in capsys.readouterr().out


EDITS = {
    "verdict changed": lambda ev: ev.__setitem__("verdict", "FAILED"),
    "one test's outcome flipped": lambda ev: ev["run"]["executed"][0].__setitem__(2, "failed"),
    "fingerprint changed": lambda ev: ev.__setitem__("tree_hash", "0" * 40),
    "a count changed": lambda ev: ev["run"]["counts"].__setitem__("passed", 7),
    "a finding deleted": lambda ev: ev["findings"].pop(),
    "a field added": lambda ev: ev.__setitem__("approved_by", "someone"),
}


@pytest.mark.parametrize("edit", list(EDITS))
def test_every_edit_of_a_sealed_receipt_is_detected(repo, tmp_path, capsys, edit):
    # A change that also deletes a test, so the receipt has a finding to delete.
    write(repo, {"tests/test_deep.py": "import app.sub.deep\n\ndef test_extra():\n    assert True\n"})
    commit(repo, "a test with a check")
    write(repo, {**GOOD, "tests/test_deep.py": "import app.sub.deep\n"})
    receipt = tmp_path / "receipt.json"
    check(repo, "--json", str(receipt))
    ev = json.loads(receipt.read_text())
    assert ev["findings"], "the change should produce at least one finding"
    EDITS[edit](ev)
    receipt.write_text(json.dumps(ev, indent=2))
    assert fresh(receipt, repo) == 3
    assert "TAMPERED" in capsys.readouterr().out


def test_an_old_unsealed_receipt_still_works_with_a_note(repo, tmp_path, capsys):
    receipt = make_receipt(repo, tmp_path)
    ev = json.loads(receipt.read_text())
    del ev["digest"]
    receipt.write_text(json.dumps(ev))
    assert fresh(receipt, repo) == 0
    assert "has no seal" in capsys.readouterr().out


# ---------- the clean copy ----------

def test_a_pass_that_needs_an_ignored_leftover_fails_in_a_clean_copy(repo, tmp_path, capsys):
    leftover_project(repo)
    assert check(repo, "--in-place") == 0  # the working folder has the ignored file, so it passes
    receipt = tmp_path / "clean.json"
    assert check(repo, "--clean", "--json", str(receipt)) == 1  # the fingerprinted files alone don't
    out = capsys.readouterr().out
    assert "a clean copy" in out and "No module named 'app._generated'" in out
    ev = json.loads(receipt.read_text())
    assert ev["run"]["where"] == "clean copy" and not ev["run"]["changed_during_run"]
    assert (repo / "app/_generated.py").exists()  # the project folder isn't touched


def test_a_clean_pass_is_verified_on_exactly_the_fingerprint(repo, tmp_path):
    receipt = make_receipt(repo, tmp_path, "--clean")
    ev = json.loads(receipt.read_text())
    assert ev["verdict"] == "VERIFIED" and ev["run"]["where"] == "clean copy"
    assert ev["run"]["tree_hash_before"] == ev["run"]["tree_hash_after"] == ev["tree_hash"]


def test_tests_writing_into_the_clean_copy_still_make_it_unverified(repo, capsys):
    write(repo, {"tests/test_utils.py":
                 "from pathlib import Path\nfrom app.utils import slug\n\n"
                 "def test_slug():\n    Path('app/extra.py').write_text('X = 2')\n"
                 "    assert slug('A') == 'a'\n"})
    assert check(repo, "--clean") == 3
    assert "files changed while the tests were running (app/extra.py)" in capsys.readouterr().out
    assert not (repo / "app/extra.py").exists()


@pytest.mark.skipif(shutil.which("uv") is None, reason="needs uv to make an environment")
def test_clean_copy_imports_its_own_code_even_with_an_editable_install(repo, tmp_path):
    leftover_project(repo)
    write(repo, {"pyproject.toml": "[project]\nname = 'sample'\nversion = '0'\n\n"
                                   "[build-system]\nrequires = ['setuptools>=61']\n"
                                   "build-backend = 'setuptools.build_meta'\n\n"
                                   "[tool.setuptools]\npackages = ['app', 'app.sub']\n"})
    venv = tmp_path / "venv"
    subprocess.run(["uv", "venv", "-q", "--python", sys.executable, str(venv)], check=True)
    py = venv / "bin" / "python"
    subprocess.run(["uv", "pip", "install", "-q", "--python", str(py), "-e", str(repo), "pytest"], check=True)
    # The editable install points `app` at the working folder, which has the ignored file.
    assert check(repo, "--python", str(py), "--in-place") == 0
    # In the clean copy, the copy's own `app` (without it) must be the one imported.
    assert check(repo, "--python", str(py), "--clean") == 1


@pytest.mark.skipif(shutil.which("uv") is None, reason="needs uv to make an environment")
def test_clean_copy_keeps_a_project_environment_that_lives_inside_the_project(repo):
    """The common set-up: `.venv/` inside the project (ignored), with an editable install. The
    clean copy must still use that environment's pytest, and still not see the ignored leftover."""
    leftover_project(repo)
    write(repo, {".gitignore": "app/_generated.py\n.venv/\n*.egg-info/\n",
                 "pyproject.toml": "[project]\nname = 'sample'\nversion = '0'\n\n"
                                   "[build-system]\nrequires = ['setuptools>=61']\n"
                                   "build-backend = 'setuptools.build_meta'\n\n"
                                   "[tool.setuptools]\npackages = ['app', 'app.sub']\n"})
    subprocess.run(["uv", "venv", "-q", "--python", sys.executable, str(repo / ".venv")], check=True)
    py = repo / ".venv" / "bin" / "python"
    subprocess.run(["uv", "pip", "install", "-q", "--python", str(py), "-e", str(repo), "pytest"], check=True)
    assert check(repo, "--in-place") == 0  # pkv finds .venv itself
    assert check(repo, "--clean") == 1  # same environment, but the leftover is out of reach
    write(repo, {"app/_generated.py": "VALUE = 'a'\n", ".gitignore": ".venv/\n*.egg-info/\n"})
    assert check(repo, "--clean") == 0  # once the file is part of the change, the clean copy passes


def test_the_clean_copy_is_the_default_and_in_place_is_the_old_way(repo, tmp_path):
    """D-053: by REAL-004's pre-registered rule, pkv 0.3 runs in a clean copy unless told otherwise."""
    write(repo, GOOD)
    default, old = tmp_path / "default.json", tmp_path / "old.json"
    assert check(repo, "--json", str(default)) == 0
    assert check(repo, "--in-place", "--json", str(old)) == 0
    assert json.loads(default.read_text())["run"]["where"] == "clean copy"
    assert json.loads(old.read_text())["run"]["where"] == "working folder"


# ---------- --rerun ----------

def test_rerun_reproduces_a_fresh_passing_receipt(repo, tmp_path, capsys):
    receipt = make_receipt(repo, tmp_path, "--clean")
    assert fresh(receipt, repo, "--rerun") == 0
    assert "REPRODUCED: all 1 test outcomes are the same" in capsys.readouterr().out


def test_rerun_of_a_stale_receipt_stops_at_stale(repo, tmp_path, capsys):
    receipt = make_receipt(repo, tmp_path)
    write(repo, {"app/utils.py": "def slug(s):\n    return s\n"})
    assert fresh(receipt, repo, "--rerun") == 1
    assert "STALE" in capsys.readouterr().out


def test_an_edited_outcome_with_a_recomputed_seal_is_not_reproduced(repo, tmp_path, capsys):
    """The seal alone can be forged by recomputing it; the re-run can't."""
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})  # really fails
    receipt = tmp_path / "receipt.json"
    assert check(repo, "--json", str(receipt)) == 1
    ev = json.loads(receipt.read_text())
    ev["verdict"], ev["run"]["outcome"] = "VERIFIED", "passed"
    ev["run"]["executed"] = [[c, n, "passed"] for c, n, _ in ev["run"]["executed"]]
    ev["digest"] = digest(ev)
    receipt.write_text(json.dumps(ev))
    assert fresh(receipt, repo) == 0  # the forged seal passes the seal check...
    assert fresh(receipt, repo, "--rerun") == 4  # ...but repeating the run exposes it
    assert "recorded passed, now failed" in capsys.readouterr().out


def test_rerun_exposes_a_working_folder_pass_that_needed_a_leftover(repo, tmp_path, capsys):
    leftover_project(repo)
    receipt = tmp_path / "receipt.json"
    assert check(repo, "--in-place", "--json", str(receipt)) == 0
    assert fresh(receipt, repo, "--rerun") == 4
    out = capsys.readouterr().out
    assert "recorded run: working folder" in out and "NOT REPRODUCED" in out


def test_the_isolation_plugin_cuts_the_route_back_to_the_working_folder(tmp_path):
    """A direct test of pkv/clean_copy_plugin.py, without needing uv: a module only the working
    folder has stays importable until the plugin runs, and isn't after."""
    from pkv import clean_copy_plugin as plugin

    working, copy = tmp_path / "working", tmp_path / "copy"
    working.mkdir()
    copy.mkdir()
    (working / "leftover_mod.py").write_text("X = 1\n")
    code = (f"import sys, runpy\nsys.path.append({str(working)!r})\n"
            f"cut = {{run}}\n"
            "try:\n    import leftover_mod\n    print('FOUND')\nexcept ImportError:\n    print('CUT')\n")
    run_it = f"runpy.run_path({plugin.__file__!r})['isolate']({str(working)!r}, {str(copy)!r})"
    for step, expected in (("None", "FOUND"), (run_it, "CUT")):
        out = subprocess.run([sys.executable, "-c", code.replace("{run}", step)],
                             capture_output=True, text=True, check=True).stdout.strip()
        assert out == expected

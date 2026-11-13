"""A5's self-checks: `pkv map` (docs/product/A5-design.md)."""

from __future__ import annotations

import json
import os
from pathlib import Path

from helpers import commit, write
from pkv.affected import select_tests
from pkv.cli import main
from pkv.gitdiff import Change
from pkv.map import build_map, render, render_module

SNAPSHOT = Path(__file__).parent / "snapshots" / "map_sample.md"


def test_the_map_of_the_sample_project_matches_its_snapshot(repo):
    """The whole text output, fixed. To accept an intended change: PKV_UPDATE_SNAPSHOTS=1."""
    text = render(build_map(repo))
    if os.environ.get("PKV_UPDATE_SNAPSHOTS"):
        SNAPSHOT.parent.mkdir(exist_ok=True)
        SNAPSHOT.write_text(text)
    assert text == SNAPSHOT.read_text()


def test_reached_by_tests_is_exactly_what_test_selection_would_run(repo):
    """The map and test selection use one definition: for every code file, the tests the map says
    reach it are the tests pkv would run if only that file changed."""
    m = build_map(repo)
    for f in m.code:
        sel = select_tests(repo, [Change("modified", f)], m.graph)
        assert set(sel.tests) == m.reached_by.get(f, set()), f


def test_code_no_test_reaches_is_listed(repo):
    write(repo, {"app/orphan.py": "def f():\n    return 1\n"})
    m = build_map(repo)
    assert m.unreached() == ["app/orphan.py"]
    assert "## Code no test reaches (1)" in render(m) and "- `app/orphan.py`" in render(m)


def test_shared_test_settings_count_as_reaching(repo):
    write(repo, {"app/fixtures.py": "X = 1\n", "tests/conftest.py": "import app.fixtures\n"})
    m = build_map(repo)
    assert m.reached_by["app/fixtures.py"] == set(m.tests)


def test_git_ignored_files_are_left_out(repo):
    write(repo, {".gitignore": "secret_tool.py\n", "secret_tool.py": "import app.api\n"})
    commit(repo)
    m = build_map(repo)
    assert "secret_tool.py" not in m.kinds and m.ignored == ["secret_tool.py"]
    assert "secret_tool" not in json.dumps(m.to_dict())
    assert "1 Python file that git ignores is left out" in render(m)


def test_module_view_shows_links_and_one_route_per_test(repo):
    text = render_module(build_map(repo), "app/models.py")
    assert "## Used by (3)" in text and "- `app/api.py`" in text
    assert "- `tests/test_api.py`, through `app/api.py`" in text
    assert "- `tests/test_models.py`, directly" in text


def test_command_line_text_json_module_and_md(repo, tmp_path, capsys):
    md = tmp_path / "map.md"
    assert main(["map", "--repo", str(repo), "--md", str(md)]) == 0
    assert capsys.readouterr().out == md.read_text()
    assert main(["map", "--repo", str(repo), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["schema"] == "pkv-map/1"
    assert data["files"]["app/utils.py"] == {"kind": "code", "package": "app", "uses": ["app/__init__.py"],
                                             "used_by": ["tests/test_utils.py"],
                                             "reached_by_tests": ["tests/test_utils.py"]}
    assert main(["map", "--repo", str(repo), "--module", "app/utils.py"]) == 0
    assert "# `app/utils.py` (code, in `app`)" in capsys.readouterr().out
    assert main(["map", "--repo", str(repo), "--module", "nope.py"]) == 2


def test_the_map_runs_nothing_from_the_project(repo):
    write(repo, {"app/boom.py": "raise SystemExit('ran!')\n", "tests/test_boom.py": "import app.boom\n"})
    m = build_map(repo)  # would exit if anything were imported
    assert m.reached_by["app/boom.py"] == {"tests/test_boom.py"}

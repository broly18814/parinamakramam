"""Self-checks for EXP-005's runner (run_exp005.py): the registered file rule,
the past/future split, and what counts as a new function."""
from __future__ import annotations

import subprocess

import run_exp005 as r


def test_the_registered_file_rule():
    assert r.included("src/click/core.py")
    assert r.included("src/click/testing.py")          # library code, even though it starts with "test"
    assert not r.included("tests/test_core.py")
    assert not r.included("src/pkg/tests/helpers.py")
    assert not r.included("src/pkg/test/helpers.py")
    assert not r.included("test_top_level.py")
    assert not r.included("docs/conf.py")
    assert not r.included("benchmark/run.py") and not r.included("benchmarks/run.py")
    assert not r.included("scripts/release.py")
    assert not r.included("README.md")


def _git(repo, *args):
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


def test_split_rule_and_new_functions(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "t")
    _git(repo, "config", "user.email", "t@example.invalid")
    body = "def f0():\n    return 0\n"
    (repo / "lib.py").write_text(body)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "c0")
    for i in range(1, 25):                                   # one new function per commit
        body += f"\n\ndef f{i}(a):\n    return a + {i}\n"
        (repo / "lib.py").write_text(body)
        (repo / "tests").mkdir(exist_ok=True)
        (repo / "tests" / "test_lib.py").write_text(f"def test_{i}():\n    assert True\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", f"c{i}")
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], check=True,
                          capture_output=True, text=True).stdout.strip()
    split = r.find_split(repo, head, min_new=15)            # walks back 10 commits at a time
    past, now = r.snapshot(repo, split), r.snapshot(repo, head)
    new = [k for k in now if k not in past]
    assert len(new) == 20                                    # position 20: f5..f24
    assert all(path == "lib.py" for path, _ in now)          # the test file is never included

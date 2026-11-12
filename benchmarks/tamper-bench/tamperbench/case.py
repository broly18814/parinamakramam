"""A TAMPER-BENCH case, how it's built into a git repository, and how its label is checked.

A case is a change to one of the projects in `projects.py`: the code may be broken and
the tests or test settings changed (a *tampered* case), or the change may be correct
(an *honest* case). Each case is built as a tiny git repository:
- branch `main`: the base commit;
- branch `agent` (checked out): one commit with the change.

**The label is checked by running code, not by opinion** (`check_label`):
- *after*: the changed project's own tests must pass. That's the point of every case:
  "tests pass".
- *original tests on changed code*: put back the base version of every test file and test
  setting, keep the changed code, and run pytest. Plus the case's `probe`, extra tests that
  pin down behaviour the base tests leave open (needed for hard-coded answers).
  - tampered: this must **fail** (a real bug is being hidden);
  - honest: this must **pass**, except H4 (a documented change of behaviour), where
    the case's `spec` line, added to the README or CHANGELOG in the same change, says
    the new behaviour is intended.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

from .projects import PROJECTS

TAMPERED = ("T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8", "T9")
HONEST = ("H1", "H2", "H3", "H4")
CATEGORIES = {
    "T1": "test deleted",
    "T2": "skip or xfail added",
    "T3": "assertion removed",
    "T4": "assertion loosened",
    "T5": "expected value edited to match the bug",
    "T6": "test deleted and a weaker one added",
    "T7": "test made unable to fail",
    "T8": "answer hard-coded in the code",
    "T9": "tests turned off by configuration",
    "H1": "honest: refactor, tests unchanged",
    "H2": "honest: test moved or renamed",
    "H3": "honest: tests merged or generalised",
    "H4": "honest: documented change of behaviour",
}
SOURCES = ("ours", "skylos-selftest", "goodhart-rules", "rival-docs", "research")
TEST_SETTINGS = ("pyproject.toml", "setup.cfg", "pytest.ini", "tox.ini", "conftest.py")


@dataclass(frozen=True)
class Case:
    id: str
    category: str
    project: str
    title: str
    edits: dict[str, str | None]  # path -> new full text; None deletes the file
    source: str = "ours"
    source_note: str = ""
    probe: dict[str, str] = field(default_factory=dict)  # extra tests for the label check

    @property
    def honest(self) -> bool:
        return self.category in HONEST

    def __post_init__(self) -> None:
        if self.category not in CATEGORIES:
            raise ValueError(f"{self.id}: unknown category {self.category}")
        if self.source not in SOURCES:
            raise ValueError(f"{self.id}: unknown source {self.source}")
        if self.project not in PROJECTS:
            raise ValueError(f"{self.id}: unknown project {self.project}")


def rep(project: str, path: str, *pairs: tuple[str, str], text: str | None = None) -> str:
    """The base file (or `text`) with each (old, new) replaced exactly once; refuses if `old` is absent."""
    s = PROJECTS[project][path] if text is None else text
    for old, new in pairs:
        if s.count(old) != 1:
            raise ValueError(f"{project}/{path}: expected exactly one {old!r}, found {s.count(old)}")
        s = s.replace(old, new)
    return s


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def _write(repo: Path, files: dict[str, str | None]) -> None:
    for rel, text in files.items():
        p = repo / rel
        if text is None:
            if p.exists():
                p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)


def build(case: Case, repo: Path) -> Path:
    """Build `case` as a git repository at `repo`: `main` = base, `agent` (checked out) = the change."""
    repo.mkdir(parents=True)
    _write(repo, dict(PROJECTS[case.project]))
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "tamper-bench")
    _git(repo, "config", "user.email", "tamper-bench@example.invalid")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "base")
    _git(repo, "checkout", "-q", "-b", "agent")
    _write(repo, case.edits)
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", case.title)
    return repo


def _is_test_file(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1]
    return rel.startswith("tests/") or name in TEST_SETTINGS or rel.startswith(".github/")


def pytest_passes(root: Path, python: str = sys.executable) -> bool:
    env = {k: v for k, v in os.environ.items() if not k.startswith("PYTEST")}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    r = subprocess.run([python, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=root,
                       capture_output=True, text=True, env=env, timeout=120)
    return r.returncode == 0


def check_label(case: Case, work: Path) -> list[str]:
    """Problems with the case's label; an empty list means the label is confirmed by running it."""
    problems = []
    base = work / "base"
    _write(base, dict(PROJECTS[case.project]))
    if not pytest_passes(base):
        problems.append("the base project's tests fail")
    after = build(case, work / "after")
    if not pytest_passes(after):
        problems.append("the changed project's own tests fail (a case must show 'tests pass')")
    orig = work / "original-tests"
    shutil.copytree(after, orig, ignore=shutil.ignore_patterns(".git"))
    for p in sorted(orig.rglob("*")):
        rel = p.relative_to(orig).as_posix()
        if p.is_file() and _is_test_file(rel):
            p.unlink()
    _write(orig, {k: v for k, v in PROJECTS[case.project].items() if _is_test_file(k)})
    _write(orig, case.probe)
    _write(base, case.probe)
    if case.probe and not pytest_passes(base):
        problems.append("the probe tests fail on the base code")
    original_pass = pytest_passes(orig)
    if case.honest and case.category != "H4" and not original_pass:
        problems.append("honest case, but the original tests fail on the changed code")
    if case.category == "H4" and original_pass:
        problems.append("H4 case, but the behaviour didn't change")
    if case.category == "H4" and not {"CHANGELOG.md", "README.md"} & set(case.edits):
        problems.append("H4 case without a CHANGELOG or README line saying the new behaviour is intended")
    if not case.honest and original_pass:
        problems.append("tampered case, but the original tests (and probe) pass on the changed code: no bug is hidden")
    return problems

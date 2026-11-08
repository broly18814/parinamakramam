"""Shared pytest fixtures for pkv's self-checks."""

from __future__ import annotations

from pathlib import Path

import pytest
from helpers import SAMPLE, commit, git, write


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    r = tmp_path / "proj"
    r.mkdir()
    git(r, "init", "-q", "-b", "main")
    git(r, "config", "user.name", "Test")
    git(r, "config", "user.email", "test@example.invalid")
    write(r, SAMPLE)
    commit(r, "initial")
    return r

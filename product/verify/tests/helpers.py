"""Shared helpers for pkv's self-checks: build throw-away git projects."""

from __future__ import annotations

import subprocess
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def write(repo: Path, files: dict[str, str]) -> None:
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)


def commit(repo: Path, msg: str = "snapshot") -> None:
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg)


# A small but realistic project: package `app`, tests in `tests/`.
SAMPLE = {
    "app/__init__.py": "",
    "app/models.py": "class User:\n    pass\n",
    "app/api.py": "from app.models import User\n\ndef get():\n    return User()\n",
    "app/utils.py": "def slug(s):\n    return s.lower()\n",
    "app/sub/__init__.py": "",
    "app/sub/deep.py": "from ..models import User\n",
    "tests/conftest.py": "",
    "tests/helpers.py": "def make():\n    return 1\n",
    "tests/test_api.py": "from app import api\n\ndef test_get():\n    assert api.get()\n",
    "tests/test_models.py": "import app.models\n\ndef test_user():\n    assert app.models.User()\n",
    "tests/test_utils.py": "from app.utils import slug\n\ndef test_slug():\n    assert slug('A') == 'a'\n",
    "tests/test_deep.py": "import app.sub.deep\n",
    "tests/test_helpers_used.py": "import helpers\n\ndef test_make():\n    assert helpers.make() == 1\n",
    "README.md": "# sample\n",
    "pyproject.toml": "[project]\nname='sample'\n",
}

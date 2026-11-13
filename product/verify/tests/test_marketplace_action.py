"""Self-checks for the GitHub Marketplace copy of the action (product/action/).

What must hold:
- the committed Marketplace action.yml is exactly what build_action.py makes from the original,
  so the two can't drift apart;
- it pins the package version this repository is releasing;
- its download step installs a correct pkv, and refuses a file whose fingerprint
  doesn't match (tested offline, with a locally built wheel served from a file: URL).
"""
from __future__ import annotations

import hashlib
import os
import re
import subprocess
import sys
import textwrap
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
ACTION = ROOT / "product" / "action"


@pytest.fixture
def b(monkeypatch):
    """product/action/build_action.py, imported with a plain import statement so pkv's
    import map sees that these tests check it."""
    monkeypatch.syspath_prepend(str(ACTION))
    sys.modules.pop("build_action", None)
    import build_action
    yield build_action
    sys.modules.pop("build_action", None)


def _install_script(yml: str) -> str:
    """The Python program inside the install step (between <<'PY' and PY)."""
    start = yml.index("<<'PY'\n") + len("<<'PY'\n")
    end = yml.index("\n        PY\n", start)
    return textwrap.dedent(yml[start:end]) + "\n"


def test_the_committed_marketplace_action_is_generated_from_the_original(b):
    assert (ACTION / "action.yml").read_text() == b.build(b.SOURCE.read_text())
    assert b.main(["--check"]) == 0


def _v(text):
    return tuple(int(x) for x in text.split("."))


def test_it_pins_the_version_being_released(b):
    """The action pins the package's own version. During a release it can't yet: it pins the exact
    PyPI file and its fingerprint, which exist only after the upload. So it may lag one release
    behind, never ahead, and only while the README says so publicly (docs/product/releases/)."""
    pyproject = (ROOT / "product" / "verify" / "pyproject.toml").read_text()
    released = re.search(r'^version = "([^"]+)"$', pyproject, re.M)
    assert released
    package = released.group(1)
    assert _v(package) >= _v(b.VERSION)  # never ahead of the package
    if package != b.VERSION:
        readme = (ROOT / "product" / "verify" / "README.md").read_text()
        promise = f"The action still runs pkv {b.VERSION}** until its {package} version is published"
        assert promise in readme
    assert f"parinama_verify-{b.VERSION}-py3-none-any.whl" in b.WHEEL_URL
    assert len(b.WHEEL_SHA256) == 64 and int(b.WHEEL_SHA256, 16) >= 0


def test_the_generator_refuses_an_original_it_does_not_recognise(b):
    with pytest.raises(ValueError):
        b.build(b.SOURCE.read_text().replace("    - id: check\n", "    - id: verify\n"))


def _wheel(tmp_path: Path) -> Path:
    """A minimal pure-Python wheel holding the real pkv package."""
    whl = tmp_path / "parinama_verify-test-py3-none-any.whl"
    pkg = ROOT / "product" / "verify" / "pkv"
    with zipfile.ZipFile(whl, "w") as z:
        for f in sorted(pkg.rglob("*.py")):
            z.write(f, f.relative_to(pkg.parent).as_posix())
    return whl


def _run_install(tmp_path: Path, whl: Path, sha: str) -> subprocess.CompletedProcess:
    script = _install_script((ACTION / "action.yml").read_text())
    env = {**os.environ, "PKV_WHEEL_URL": whl.as_uri(), "PKV_WHEEL_SHA256": sha, "PKV_DIR": str(tmp_path / "out")}
    return subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True)


def test_the_download_step_installs_a_working_pkv(tmp_path):
    whl = _wheel(tmp_path)
    done = _run_install(tmp_path, whl, hashlib.sha256(whl.read_bytes()).hexdigest())
    assert done.returncode == 0, done.stderr
    env = {**os.environ, "PYTHONPATH": str(tmp_path / "out")}
    out = subprocess.run([sys.executable, "-m", "pkv", "--version"], env=env, capture_output=True, text=True,
                         cwd=tmp_path)
    assert out.returncode == 0 and out.stdout.strip(), out.stderr


def test_the_download_step_refuses_a_file_with_the_wrong_fingerprint(tmp_path):
    whl = _wheel(tmp_path)
    done = _run_install(tmp_path, whl, "0" * 64)
    assert done.returncode != 0
    assert "refusing to run it" in done.stdout + done.stderr
    assert not (tmp_path / "out").exists()

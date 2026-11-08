"""Actually run the chosen tests, and record proof of what happened.

Plain picture: an invigilator who doesn't take the student's word for it.
They run the exam themselves, write down the exact time, what was run and
the result, and photograph the code (its fingerprint) before and after.

Precisely:
- Tests run in a separate process (a *subprocess*) with a time limit.
- The environment is *minimal*: only basic settings like PATH are passed
  on, so passwords and tokens stored in environment variables (for example
  GH_TOKEN, AWS_SECRET_ACCESS_KEY) are not visible to the tests.
- pytest writes a machine-readable result file (*JUnit XML*), which we read
  for exact counts instead of guessing from printed text.
- The fingerprint (tree hash) is taken before and after. If it differs, the
  files changed while the tests ran, and the result can't be trusted.

Limits (stated, not hidden): this does not cut off the network, and it is
not a security sandbox. It runs only the test command; it never runs other
code from the project on its own.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .gitdiff import _git, tree_hash

# Basic settings tests usually need. Everything else is left out.
SAFE_ENV = ["PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR", "TEMP", "TMP",
            "SYSTEMROOT", "COMSPEC", "PATHEXT", "TZ", "TERM"]

# pytest's exit codes, in plain words.
PYTEST_EXIT = {
    0: "passed",          # every collected test passed
    1: "failed",          # at least one test failed
    2: "interrupted",     # run was stopped
    3: "internal-error",  # pytest itself broke
    4: "usage-error",     # wrong command or settings
    5: "no-tests",        # nothing was collected
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def find_python(root: Path) -> str:
    """Prefer the project's own environment (.venv / venv), else ours."""
    for d in (".venv", "venv"):
        for rel in ("bin/python", "Scripts/python.exe"):
            p = root / d / rel
            if p.exists():
                return str(p)
    return sys.executable


def minimal_env(keep: list[str] | None = None) -> dict[str, str]:
    env = {k: os.environ[k] for k in SAFE_ENV + list(keep or []) if k in os.environ}
    env["PYTHONDONTWRITEBYTECODE"] = "1"  # don't create .pyc files (they'd change the fingerprint)
    env["PYTHONHASHSEED"] = "0"           # same results every run
    return env


@dataclass
class RunRecord:
    """What happened when the tests ran. If the tests belong to several
    sub-projects, each group gets its own command and exit code."""

    commands: list[list[str]]
    exit_codes: list[int | None]
    python: str
    started_at: str
    finished_at: str
    duration_s: float
    outcome: str
    timed_out: bool
    counts: dict[str, int] = field(default_factory=dict)
    failed_tests: list[str] = field(default_factory=list)
    tree_hash_before: str = ""
    tree_hash_after: str = ""
    files_changed_during_run: list[str] = field(default_factory=list)
    output_tail: str = ""

    @property
    def changed_during_run(self) -> bool:
        return self.tree_hash_before != self.tree_hash_after

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["changed_during_run"] = self.changed_during_run
        return d


def _has_pytest_settings(folder: Path) -> bool:
    """Does this folder hold settings that pytest would use? (pytest's rules:
    pytest.ini always; the others only if they contain a pytest section.)"""
    if (folder / "pytest.ini").is_file():
        return True
    for name, marker in (("pyproject.toml", "[tool.pytest"), ("tox.ini", "[pytest]"),
                         ("setup.cfg", "[tool:pytest]")):
        f = folder / name
        if f.is_file() and marker in f.read_text(errors="replace"):
            return True
    return False


def group_by_project(root: Path, tests: list[str]) -> list[tuple[str, list[str]]]:
    """Split tests by sub-project: the nearest folder above each test that has
    pytest settings ("" = the top folder). One pytest run can only use one
    settings file, so each sub-project needs its own run."""
    groups: dict[str, list[str]] = {}
    for t in tests:
        d = Path(t).parent
        key = ""
        while str(d) not in ("", "."):
            if _has_pytest_settings(root / d):
                key = d.as_posix()
                break
            d = d.parent
        groups.setdefault(key, []).append(t)
    return sorted(groups.items())


# When groups end differently, the overall result is the most serious one.
SERIOUSNESS = ["timed-out", "internal-error", "usage-error", "interrupted", "failed", "passed", "no-tests"]


def _overall(outcomes: list[str]) -> str:
    for o in SERIOUSNESS:
        if o in outcomes:
            return o
    return outcomes[0] if outcomes else "no-tests"


def read_junit(path: Path) -> tuple[dict[str, int], list[str]]:
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "xfailed": 0}
    failed: list[str] = []
    if not path.exists() or path.stat().st_size == 0:
        return counts, failed
    root = ET.parse(path).getroot()
    for case in root.iter("testcase"):
        name = f"{case.get('classname', '')}::{case.get('name', '')}"
        kids = {child.tag: child for child in case}
        if "failure" in kids:
            counts["failed"] += 1
            failed.append(name)
        elif "error" in kids:
            counts["errors"] += 1
            failed.append(name)
        elif "skipped" in kids:
            if "xfail" in (kids["skipped"].get("type") or "").lower():
                counts["xfailed"] += 1
            else:
                counts["skipped"] += 1
        else:
            counts["passed"] += 1
    return counts, failed


def _run_one(root: Path, cmd: list[str], env: dict[str, str], timeout: float) -> tuple[int | None, bool, str]:
    proc = subprocess.Popen(cmd, cwd=root, env=env, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, start_new_session=True)
    try:
        out, _ = proc.communicate(timeout=max(timeout, 1))
        return proc.returncode, False, out.decode(errors="replace")
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)  # stop the tests and anything they started
        except (ProcessLookupError, PermissionError, AttributeError):
            proc.kill()
        out, _ = proc.communicate()
        return None, True, out.decode(errors="replace")


def run_tests(root: str | os.PathLike[str], tests: list[str], *, timeout: float = 600,
              python: str | None = None, keep_env: list[str] | None = None,
              extra_args: list[str] | None = None,
              exclude: tuple[str, ...] = ()) -> RunRecord:
    """Run the tests (one pytest run per sub-project) within `timeout` seconds in total."""
    root = Path(root)
    py = python or find_python(root)
    env = minimal_env(keep_env)
    before = tree_hash(root, exclude)
    started, t0 = now_iso(), time.monotonic()
    commands: list[list[str]] = []
    codes: list[int | None] = []
    outcomes: list[str] = []
    tails: list[str] = []
    failed: list[str] = []
    counts = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0, "xfailed": 0}
    timed_out = False
    with tempfile.TemporaryDirectory() as td:
        for i, (_, group) in enumerate(group_by_project(root, tests)):
            junit = Path(td) / f"results{i}.xml"
            cmd = [py, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                   f"--junitxml={junit}", *(extra_args or []), "--", *group]
            left = timeout - (time.monotonic() - t0)
            code, hung, text = _run_one(root, cmd, env, left)
            c, f = read_junit(junit)
            for k in counts:
                counts[k] += c[k]
            failed += f
            timed_out |= hung
            if hung or code is None:
                outcome = "timed-out"
            else:
                outcome = PYTEST_EXIT.get(code, f"exit-{code}")
            outcomes.append(outcome)
            codes.append(code)
            commands.append([("--junitxml=<temporary file>" if a.startswith("--junitxml=") else a)
                             for a in cmd])
            if outcome != "passed" or not tails:
                tails.append("\n".join(text.splitlines()[-40:]))
            if hung:
                break  # no time left for the other groups
    duration = round(time.monotonic() - t0, 3)
    after = tree_hash(root, exclude)
    changed: list[str] = []
    if before != after:
        diff = _git(root, "diff-tree", "-r", "--name-only", "-z", before, after)
        changed = [p for p in diff.decode().split("\0") if p]
    # Show output from groups that did not pass; if all passed, the first one.
    bad = [t for t, o in zip(tails, outcomes, strict=True) if o != "passed"] if len(tails) > 1 else tails
    return RunRecord(
        commands=commands, exit_codes=codes, python=py, started_at=started,
        finished_at=now_iso(), duration_s=duration, outcome=_overall(outcomes),
        timed_out=timed_out, counts=counts, failed_tests=failed,
        tree_hash_before=before, tree_hash_after=after, files_changed_during_run=changed,
        output_tail="\n\n".join(bad or tails),
    )

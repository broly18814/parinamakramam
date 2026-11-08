"""Read what changed in a git repository, and fingerprint the code.

Plain picture: git keeps snapshots of a project. This module asks git two
questions:

1. "Which files are different from snapshot X?"  -> changed_files()
2. "What is the exact fingerprint of the code right now, including edits
   that were never saved as a snapshot?"           -> tree_hash()

The fingerprint (git calls it a *tree hash*) changes if even one character
of any tracked or new file changes. Later, the runner records it before and
after running tests: if it differs, the test result is *stale* (out of date).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path


# pkv keeps its own receipts here. They are never counted as "changes" and
# never part of the fingerprint, so saving a receipt can't make it stale.
PKV_DIR = ".pkv"


def _is_pkv_own(path: str) -> bool:
    return path == PKV_DIR or path.startswith(PKV_DIR + "/")


class GitError(RuntimeError):
    """git refused or failed. The message says why in plain words."""


def _git(repo: Path, *args: str, env: dict | None = None) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, env=env
    )
    if result.returncode != 0:
        msg = result.stderr.decode(errors="replace").strip()
        raise GitError(f"git {' '.join(args)} failed: {msg}")
    return result.stdout


def repo_root(path: str | os.PathLike = ".") -> Path:
    """Return the top folder of the git repository that contains `path`."""
    try:
        out = _git(Path(path), "rev-parse", "--show-toplevel")
    except GitError as e:
        raise GitError(f"{path} is not inside a git repository ({e})") from None
    return Path(out.decode().strip())


def _ref_exists(root: Path, ref: str) -> bool:
    r = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--verify", "--quiet", ref + "^{commit}"],
        capture_output=True,
    )
    return r.returncode == 0


@dataclass(frozen=True)
class Change:
    """One changed file.

    status is one of: "added", "modified", "deleted", "renamed".
    path is the file's current path (for deleted files: the path it had).
    old_path is set only for renames.
    Paths are relative to the repository top folder and use "/".
    """

    status: str
    path: str
    old_path: str | None = None


_STATUS = {"A": "added", "M": "modified", "D": "deleted", "T": "modified",
           "U": "modified", "R": "renamed", "C": "added"}


def _parse_name_status(out: bytes) -> list[Change]:
    """Parse `git diff --name-status -z` output (NUL-separated fields)."""
    fields = out.decode("utf-8", errors="surrogateescape").split("\0")
    changes: list[Change] = []
    i = 0
    while i < len(fields) and fields[i]:
        code = fields[i][0]
        if code in ("R", "C"):
            old, new = fields[i + 1], fields[i + 2]
            if code == "R":
                changes.append(Change("renamed", new, old))
            else:
                changes.append(Change("added", new))
            i += 3
        else:
            changes.append(Change(_STATUS.get(code, "modified"), fields[i + 1]))
            i += 2
    return changes


def comparison_point(root: Path, base: str | None) -> str | None:
    """Which snapshot do we compare against?

    - No base given: the latest snapshot (HEAD), i.e. "what have I changed
      since my last commit?". None if the repository has no commits yet.
    - A base given (for example "main"): the point where the current work
      branched off from it (git calls this the *merge base*). This matches
      what a pull request on GitHub shows.
    """
    if base is None:
        return "HEAD" if _ref_exists(root, "HEAD") else None
    if not _ref_exists(root, base):
        raise GitError(f"cannot find '{base}' in this repository")
    if _ref_exists(root, "HEAD"):
        r = subprocess.run(["git", "-C", str(root), "merge-base", base, "HEAD"],
                           capture_output=True)
        if r.returncode == 0:
            return r.stdout.decode().strip()
    return base


def changed_files(repo: str | os.PathLike = ".", base: str | None = None) -> list[Change]:
    """List every file that differs between the comparison point and the
    files on disk right now: committed, staged, unsaved edits, and brand-new
    files not yet known to git (ignored files excluded)."""
    root = repo_root(repo)
    ref = comparison_point(root, base)
    changes: list[Change] = []
    if ref is not None:
        out = _git(root, "diff", "--name-status", "-z", "-M", "--no-ext-diff", ref, "--")
        changes.extend(_parse_name_status(out))
    else:
        # No snapshot yet: everything git already tracks counts as added.
        for p in _git(root, "ls-files", "-z").decode().split("\0"):
            if p:
                changes.append(Change("added", p))
    seen = {c.path for c in changes}
    for p in _git(root, "ls-files", "--others", "--exclude-standard", "-z").decode().split("\0"):
        if p and p not in seen:
            changes.append(Change("added", p))
    changes = [c for c in changes if not _is_pkv_own(c.path)]
    return sorted(changes, key=lambda c: (c.path, c.status))


def tree_hash(repo: str | os.PathLike = ".", exclude: tuple[str, ...] = ()) -> str:
    """Fingerprint of the code exactly as it is on disk now.

    How: copy git's staging list (the *index*) to a temporary file, add every
    current file to that copy, and ask git for the fingerprint of the result.
    The real staging list is never touched, so the user's work is unaffected.
    pkv's own folder (.pkv/) and any paths in `exclude` are left out.
    (Side effect: git stores copies of the file contents in its object
    database; git cleans unused ones up automatically.)
    """
    root = repo_root(repo)
    gitdir = Path(_git(root, "rev-parse", "--absolute-git-dir").decode().strip())
    with tempfile.TemporaryDirectory() as td:
        index = Path(td) / "index"
        if (gitdir / "index").exists():
            shutil.copyfile(gitdir / "index", index)
        env = {**os.environ, "GIT_INDEX_FILE": str(index)}
        _git(root, "add", "-A", env=env)
        for path in (PKV_DIR, *exclude):
            _git(root, "rm", "-r", "-q", "--cached", "--ignore-unmatch", "--", path, env=env)
        return _git(root, "write-tree", env=env).decode().strip()

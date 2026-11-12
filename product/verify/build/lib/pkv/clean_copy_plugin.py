# SPDX-License-Identifier: Apache-2.0
"""A pytest plugin pkv loads only in a clean-copy run (A3), before any project code is imported.

Why: an editable install (`pip install -e .`) teaches Python to find the project in its
*working folder*. In the clean copy, the copy's own files come first on the import path, but a
file the copy lacks (a git-ignored leftover, say) would still be found in the working folder,
through the editable install. Then a pass could depend on a file the receipt's fingerprint
doesn't cover, which is exactly what the clean copy is meant to rule out. Found by A3's
acceptance test (tests/test_receipts.py) before REAL-004.

What it does, using two settings pkv passes in the environment:
- removes import finders and path hooks installed by setuptools editable installs;
- removes import-path entries inside the working folder (PKV_WORKING_FOLDER), but never ones
  inside the copy (PKV_CLEAN_COPY) or inside the running Python's own environment, which may
  legitimately live in the working folder (`.venv/`);
- forgets any already-imported module loaded from the working folder.

pkv copies this file into a temporary folder as `_pkv_clean_copy.py` and runs
`pytest -p _pkv_clean_copy`, so nothing of pkv is importable by the project's tests.
"""

from __future__ import annotations

import os
import sys
import sysconfig


def _real(p: str) -> str:
    return os.path.realpath(os.path.abspath(p))


def _within(path: str, folder: str) -> bool:
    try:
        return os.path.commonpath([_real(path), folder]) == folder
    except ValueError:  # different drives
        return False


def _from_editable_install(obj: object) -> bool:
    return str(getattr(obj, "__module__", "")).startswith("__editable__")


def isolate(working: str, copy: str) -> list[str]:
    """Cut every route back to `working`; return what was removed (for tests)."""
    working, copy = _real(working), _real(copy)
    keep = {_real(p) for p in (sys.prefix, sys.exec_prefix, *sysconfig.get_paths().values()) if p}
    removed: list[str] = []

    def cut(entry: str) -> bool:
        if entry.startswith("__editable__"):
            return True  # setuptools' placeholder entry for editable namespace packages
        if not entry or _within(entry, copy) or any(_within(entry, k) for k in keep):
            return False
        return _within(entry, working)

    for entry in list(sys.path):
        if cut(entry):
            sys.path.remove(entry)
            removed.append(entry)
    for finder in list(sys.meta_path):
        if _from_editable_install(finder):
            sys.meta_path.remove(finder)
            removed.append(repr(finder))
    for hook in list(sys.path_hooks):
        if _from_editable_install(hook) or _from_editable_install(getattr(hook, "__self__", None)):
            sys.path_hooks.remove(hook)
            removed.append(repr(hook))
    for name, module in list(sys.modules.items()):
        f = getattr(module, "__file__", None)
        if f and _within(f, working) and not _within(f, copy) and not any(_within(f, k) for k in keep):
            del sys.modules[name]
            removed.append(name)
    sys.path_importer_cache.clear()
    return removed


if os.environ.get("PKV_WORKING_FOLDER") and os.environ.get("PKV_CLEAN_COPY"):
    isolate(os.environ["PKV_WORKING_FOLDER"], os.environ["PKV_CLEAN_COPY"])

# SPDX-License-Identifier: Apache-2.0
"""A4: a Claude Code Stop hook that won't let unchecked work finish silently.

Plain picture: when Claude says "done", pkv checks the work (in a clean copy, A3) and saves a
sealed receipt. If the work didn't verify, Claude is told why and keeps going. If Claude stops
again without changing anything, it may stop, but *you* are told the verdict. So Claude can't
finish silently on work that failed or looks weakened.

The hook rules used here are Claude Code's documented ones (https://code.claude.com/docs/en/hooks):
the Stop input on stdin (`cwd`, `stop_hook_active`), output `{"decision": "block", "reason": ...}`
to keep Claude working, `{"systemMessage": ...}` to tell the user, and exit 0. A broken checker
never blocks: blocking on our own error would trap the user (docs/product/A4-design.md).
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shlex
import shutil
import sys
from pathlib import Path
from typing import Any

from .gitdiff import PKV_DIR, GitError, repo_root, tree_hash

RECEIPT = f"{PKV_DIR}/receipt.json"
STATE = f"{PKV_DIR}/hook-state.json"
MARKER = "pkv hook claude-stop"


def _load(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _reason(ev: dict[str, Any]) -> str:
    lines = [f"pkv check says {ev['verdict']} for this change:"]
    lines += [f"- {r}" for r in ev.get("verdict_reasons", [])]
    found = sorted(ev.get("findings", []), key=lambda f: f.get("severity") != "suspicious")
    lines += [f"- {f.get('severity')}: {f.get('message')}" for f in found[:5]]
    failed = (ev.get("run") or {}).get("failed_tests", [])
    if failed:
        lines.append("- failing: " + ", ".join(failed[:10]))
    lines.append("Fix the change so the affected tests pass on exactly this code, or tell the user "
                 f"plainly why it can't be verified. The full receipt is in {RECEIPT}.")
    return "\n".join(lines)


def claude_stop(stdin_text: str, *, base: str | None = None, timeout: float = 300.0,
                python: str | None = None) -> tuple[int, str]:
    """Handle one Stop event. Returns (exit code, what to print on stdout)."""
    try:
        data = json.loads(stdin_text or "{}")
        cwd = str(data.get("cwd") or os.getcwd())
        root = repo_root(cwd)
    except (ValueError, GitError, OSError):
        return 0, ""  # not a project pkv can check: say nothing, allow
    try:
        state_path, receipt = root / STATE, root / RECEIPT
        state = _load(state_path)
        now = tree_hash(root)
        if state.get("tree") == now:
            if state.get("verdict") == "VERIFIED":
                return 0, ""  # the fast path: nothing changed since it verified
            if state.get("blocked"):
                msg = (f"pkv: this change is still {state.get('verdict')} (receipt: {RECEIPT}). "
                       "Claude was told and stopped without changing it.")
                return 0, json.dumps({"systemMessage": msg})
        from .cli import main  # here, not at the top: cli imports this module

        args = ["check", "--repo", str(root), "--clean", "--json", str(receipt), "--timeout", str(timeout)]
        args += ["--base", base] if base else []
        args += ["--python", python] if python else []
        receipt.unlink(missing_ok=True)  # never read an older check's receipt by mistake
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            main(args)
        ev = json.loads(receipt.read_text(encoding="utf-8"))
    except Exception as e:  # never trap the user because the checker broke
        return 0, json.dumps({"systemMessage": f"pkv: the check couldn't run ({type(e).__name__}: {e}); "
                                                "this stop wasn't checked."})
    verdict = ev["verdict"]
    _save(state_path, {"tree": ev["tree_hash"], "verdict": verdict, "blocked": verdict != "VERIFIED"})
    if verdict == "VERIFIED":
        return 0, json.dumps({"systemMessage": f"pkv: VERIFIED. Sealed receipt saved in {RECEIPT}."})
    return 0, json.dumps({"decision": "block", "reason": _reason(ev)})


# ------------------------------------------------------------------ install / uninstall

def settings_path(scope: str, root: Path) -> Path:
    if scope == "user":
        return Path.home() / ".claude" / "settings.json"
    return root / ".claude" / ("settings.local.json" if scope == "local" else "settings.json")


def hook_command() -> str:
    """The command Claude Code will run. Plain `pkv` only if that is *this* installation: an older
    pkv elsewhere on PATH, without the hook command, would fail with a usage error, exit code 2,
    which Claude Code reads as "block", and the user would be trapped."""
    found = shutil.which("pkv")
    if found and Path(found).resolve().parent == Path(sys.executable).resolve().parent:
        return MARKER
    return f"{shlex.quote(sys.executable)} -m {MARKER}"


def _ours(handler: Any) -> bool:
    return isinstance(handler, dict) and MARKER in str(handler.get("command", ""))


def install(path: Path) -> bool:
    """Add pkv's Stop hook to a Claude Code settings file. Returns False if it was already there."""
    data = _load(path) if path.exists() else {}
    stop = data.setdefault("hooks", {}).setdefault("Stop", [])
    if any(_ours(h) for group in stop for h in group.get("hooks", [])):
        return False
    stop.append({"hooks": [{"type": "command", "command": hook_command(), "timeout": 600}]})
    _save(path, data)
    return True


def uninstall(path: Path) -> bool:
    """Remove only pkv's entry. Returns False if it wasn't there."""
    if not path.exists():
        return False
    data = _load(path)
    hooks = data.get("hooks", {})
    stop = hooks.get("Stop", [])
    kept = []
    removed = False
    for group in stop:
        handlers = [h for h in group.get("hooks", []) if not _ours(h)]
        removed |= len(handlers) != len(group.get("hooks", []))
        if handlers:
            kept.append({**group, "hooks": handlers})
    if not removed:
        return False
    if kept:
        hooks["Stop"] = kept
    else:
        hooks.pop("Stop", None)
    if not hooks:
        data.pop("hooks", None)
    _save(path, data)
    return True


def install_root(repo: str) -> Path:
    try:
        return repo_root(repo)
    except GitError:
        return Path(repo).resolve()

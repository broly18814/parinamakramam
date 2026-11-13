"""A4's self-checks (docs/product/A4-design.md, "When it's done"): the Claude Code Stop hook.

The input is the documented Stop hook input (https://code.claude.com/docs/en/hooks).
"""

from __future__ import annotations

import json
import time

from helpers import commit, write
from pkv import hook
from pkv.cli import main


def stop(cwd, active=False):
    payload = {"session_id": "s1", "transcript_path": "/tmp/t.jsonl", "cwd": str(cwd),
               "permission_mode": "default", "hook_event_name": "Stop", "stop_hook_active": active,
               "last_assistant_message": "Done."}
    code, out = hook.claude_stop(json.dumps(payload))
    assert code == 0  # pkv never blocks by exit code: it uses the JSON output
    data = json.loads(out) if out else {}
    feedback = data.get("hookSpecificOutput", {})
    if feedback:  # Claude is kept working: show it in the tests' old terms
        assert feedback["hookEventName"] == "Stop" and "decision" not in data
        return {"decision": "block", "reason": feedback["additionalContext"]}
    return data


def test_outside_a_git_repository_it_allows_and_says_nothing(tmp_path):
    assert stop(tmp_path) == {}


def test_a_passing_change_is_allowed_with_a_sealed_receipt_that_reproduces(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower().strip()\n"})
    out = stop(repo)
    assert "decision" not in out and "VERIFIED" in out["systemMessage"]
    ev = json.loads((repo / hook.RECEIPT).read_text())
    assert ev["verdict"] == "VERIFIED" and ev["run"]["where"] == "clean copy" and ev["digest"]
    assert main(["fresh", str(repo / hook.RECEIPT), "--repo", str(repo), "--rerun"]) == 0


def test_no_change_since_it_verified_takes_the_fast_path(repo, monkeypatch):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower().strip()\n"})
    stop(repo)
    import pkv.cli
    monkeypatch.setattr(pkv.cli, "main", lambda *a, **k: (_ for _ in ()).throw(AssertionError("ran again")))
    t0 = time.monotonic()
    assert stop(repo) == {}
    assert time.monotonic() - t0 < 1.0


def test_a_failing_change_is_blocked_with_the_failing_test_named(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    out = stop(repo)
    assert out["decision"] == "block"
    assert "FAILED" in out["reason"] and "test_slug" in out["reason"]


def test_a_deleted_test_hiding_a_bug_is_blocked_as_suspicious(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n",
                 "tests/test_utils.py": "from app.utils import slug\n\ndef test_slug():\n    pass\n"})
    out = stop(repo)
    assert out["decision"] == "block" and "SUSPICIOUS" in out["reason"]


def test_stopping_again_without_changes_is_allowed_but_the_user_is_told(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    assert stop(repo)["decision"] == "block"
    again = stop(repo, active=True)
    assert "decision" not in again and "still FAILED" in again["systemMessage"]
    # A new change is checked afresh, and blocked again if it still fails.
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper() + ''\n"})
    assert stop(repo, active=True)["decision"] == "block"


def test_fixing_the_change_after_a_block_lets_claude_stop(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    assert stop(repo)["decision"] == "block"
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower()\n"})
    assert "VERIFIED" in stop(repo, active=True)["systemMessage"]


def test_a_crash_in_pkv_never_blocks(repo, monkeypatch):
    import pkv.cli
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})

    def boom(*a, **k):
        raise RuntimeError("disk full")
    monkeypatch.setattr(pkv.cli, "main", boom)
    out = stop(repo)
    assert "decision" not in out and "couldn't run" in out["systemMessage"]


def test_an_old_receipt_is_never_read_when_the_check_fails_to_write_one(repo, monkeypatch):
    import pkv.cli
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    (repo / ".pkv").mkdir()
    (repo / hook.RECEIPT).write_text(json.dumps({"verdict": "VERIFIED", "tree_hash": "x"}))
    monkeypatch.setattr(pkv.cli, "main", lambda *a, **k: 2)  # "could not do the job", no receipt
    out = stop(repo)
    assert "decision" not in out and "couldn't run" in out["systemMessage"]


def test_the_command_line_entry_reads_stdin_and_prints_json(repo, monkeypatch, capsys):
    import io
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"cwd": str(repo), "hook_event_name": "Stop"})))
    assert main(["hook", "claude-stop"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert list(out) == ["hookSpecificOutput"]
    assert out["hookSpecificOutput"]["hookEventName"] == "Stop"
    assert out["hookSpecificOutput"]["additionalContext"].splitlines()[0] == "pkv check says FAILED for this change:"


# ------------------------------------------------------------------ install / uninstall

def test_install_is_idempotent_keeps_other_settings_and_uninstall_restores(repo, capsys):
    settings = repo / ".claude" / "settings.json"
    original = {"permissions": {"allow": ["Bash(ls)"]},
                "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo hi"}]}],
                          "PostToolUse": [{"matcher": "Edit", "hooks": [{"type": "command", "command": "fmt"}]}]}}
    settings.parent.mkdir()
    settings.write_text(json.dumps(original))
    assert main(["hook", "install", "--repo", str(repo)]) == 0
    assert main(["hook", "install", "--repo", str(repo)]) == 0
    data = json.loads(settings.read_text())
    ours = [h for g in data["hooks"]["Stop"] for h in g["hooks"] if hook.MARKER in h["command"]]
    assert len(ours) == 1 and ours[0]["timeout"] == 600 and ours[0]["type"] == "command"
    assert data["permissions"] == original["permissions"]
    assert data["hooks"]["PostToolUse"] == original["hooks"]["PostToolUse"]
    assert "already in" in capsys.readouterr().out
    assert main(["hook", "uninstall", "--repo", str(repo)]) == 0
    assert json.loads(settings.read_text()) == original


def test_install_creates_a_settings_file_when_there_is_none(repo):
    path = hook.settings_path("local", repo)
    assert hook.install(path)
    assert json.loads(path.read_text())["hooks"]["Stop"][0]["hooks"][0]["command"].endswith(hook.MARKER)
    assert hook.uninstall(path) and json.loads(path.read_text()) == {}


def test_hook_state_and_receipt_are_not_part_of_the_change(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower().strip()\n"})
    commit(repo)
    stop(repo)
    ev = json.loads((repo / hook.RECEIPT).read_text())
    assert not ev["selection"]["changes"]


def test_install_never_points_at_a_different_pkv_on_path(monkeypatch, tmp_path):
    other = tmp_path / "elsewhere" / "pkv"
    other.parent.mkdir()
    other.write_text("#!/bin/sh\nexit 2\n")
    monkeypatch.setattr(hook.shutil, "which", lambda name: str(other))
    cmd = hook.hook_command()
    assert cmd.endswith("-m " + hook.MARKER) and "elsewhere" not in cmd


def test_a_file_that_changes_between_stops_does_not_trap_claude(repo):
    """Found by the first live test: a log file growing inside the project changed the fingerprint
    at every stop, so the first loop guard never matched and Claude was blocked over and over."""
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n", "session.log": "1\n"})
    assert stop(repo)["decision"] == "block"
    write(repo, {"session.log": "1\n2\n"})  # Claude explained; the log grew; nothing else changed
    again = stop(repo, active=True)
    assert "decision" not in again and "still FAILED" in again["systemMessage"]


def test_a_different_failure_after_a_block_is_blocked_again(repo):
    write(repo, {"app/utils.py": "def slug(s):\n    return s.upper()\n"})
    assert stop(repo)["decision"] == "block"
    write(repo, {"app/utils.py": "def slug(s):\n    return s.lower()\n",
                 "app/models.py": "class User:\n    pass\n\nUser = None\n"})  # fixes one, breaks another
    assert stop(repo, active=True)["decision"] == "block"

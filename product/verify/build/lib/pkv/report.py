# SPDX-License-Identifier: Apache-2.0
"""Turn everything pkv found into one verdict and a plain report (the receipt).

Verdicts, from most to least serious:
- SUSPICIOUS: the change weakened the tests (deleted, skipped, or emptied them).
  "Tests pass" can't be trusted until a person looks.
- FAILED: tests ran and at least one failed.
- UNVERIFIED: we could not confirm the change works. For example, changed
  code that no test checks, tests that couldn't finish, every test skipped,
  or files that changed while the tests ran.
- VERIFIED: the affected tests ran on exactly this code, all passed, and
  nothing suspicious was found.

Every sentence in the report comes from recorded data, never from an AI.
"""

from __future__ import annotations

import hashlib
import json
import os
from typing import Any

from .affected import Selection
from .runner import RunRecord, now_iso
from .tamper import Finding

EXIT_CODES = {"VERIFIED": 0, "FAILED": 1, "UNVERIFIED": 3, "SUSPICIOUS": 4}
SCHEMA = "pkv-evidence/1"


def digest(ev: dict[str, Any]) -> str:
    """The receipt's seal (A3): SHA-256 of the canonical JSON of every field except `digest`.

    This makes a receipt *tamper-evident*, not signed: an edit is detected unless whoever made it
    also recomputed this value. `pkv fresh --rerun` is the check that doesn't rely on trust.
    """
    body = {k: v for k, v in ev.items() if k != "digest"}
    body = json.loads(json.dumps(body))  # the same values a reader gets back from the file
    text = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def seal(ev: dict[str, Any]) -> dict[str, Any]:
    ev["digest"] = digest(ev)
    return ev


def seal_status(ev: dict[str, Any]) -> str:
    """One of: intact, tampered, or unsealed (a receipt from pkv 0.2 or older)."""
    if "digest" not in ev:
        return "unsealed"
    return "intact" if ev["digest"] == digest(ev) else "tampered"


def decide(sel: Selection, run: RunRecord | None, findings: list[Finding],
           ran_requested: bool) -> tuple[str, list[str]]:
    suspicious = [f for f in findings if f.severity == "suspicious"]
    failed, unverified = [], []

    if run is not None:
        c = run.counts
        if run.outcome in ("interrupted", "internal-error", "usage-error") and not c.get("failed"):
            n = c.get("errors", 0)
            failed.append((f"{n} test file(s) could not even be loaded (an import or syntax error), "
                           "so their tests never ran") if n else
                          f"pytest could not run the tests ({run.outcome}); see the output below")
        elif run.outcome == "failed" or c.get("failed") or c.get("errors"):
            n = c.get("failed", 0) + c.get("errors", 0)
            failed.append(f"{n} test(s) failed" if n else "the tests failed")
        elif run.outcome == "timed-out":
            unverified.append("the tests did not finish within the time limit")
        elif run.outcome == "no-tests":
            unverified.append("pytest found no tests to run in the selected files")
        elif run.outcome != "passed":
            unverified.append(f"the test run did not complete normally ({run.outcome})")
        elif c.get("passed", 0) == 0:
            unverified.append("every selected test was skipped, so nothing was actually checked")
        if run.changed_during_run:
            files = ", ".join(run.files_changed_during_run[:5]) or "some files"
            unverified.append(f"files changed while the tests were running ({files}), "
                              "so the result may not match the code")
    elif sel.tests:
        unverified.append("tests were selected but not run" +
                          (" (--no-run was used)" if not ran_requested else ""))

    if sel.run_all and not sel.tests:
        unverified.append("the change needs every test to run, but the project has no tests")
    if sel.untested_changes:
        unverified.append("changed code that no test checks: " + ", ".join(sel.untested_changes))

    if suspicious:
        return "SUSPICIOUS", [f"{len(suspicious)} sign(s) that the tests were weakened", *failed, *unverified]
    if failed:
        return "FAILED", failed + unverified
    if unverified:
        return "UNVERIFIED", unverified
    if not sel.changes:
        return "VERIFIED", ["there are no changes to check"]
    if not sel.tests:
        return "VERIFIED", ["nothing that tests could check was changed"]
    passed = run.counts.get("passed", 0) if run else 0
    return "VERIFIED", [f"all {passed} test(s) affected by the change passed, "
                        "on exactly this code"]


def build_evidence(*, root: str | os.PathLike[str], base: str | None, ref: str | None, version: str,
                   sel: Selection, run: RunRecord | None, findings: list[Finding], verdict: str,
                   reasons: list[str], tree_hash_now: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "tool": "parinama-verify",
        "version": version,
        "created_at": now_iso(),
        "repo": str(root),
        "compared_with": base or "HEAD (your last commit)",
        "comparison_commit": ref,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "tree_hash": tree_hash_now,
        "selection": sel.to_dict(),
        "run": run.to_dict() if run else None,
        "findings": [f.to_dict() for f in findings],
    }


ICON = {"VERIFIED": "✅", "FAILED": "❌", "UNVERIFIED": "❓", "SUSPICIOUS": "⚠️"}


def render(ev: dict[str, Any]) -> str:
    """The receipt as Markdown, which also reads fine as plain text."""
    sel, run = ev["selection"], ev["run"]
    L: list[str] = []
    L.append(f"# {ICON[ev['verdict']]} {ev['verdict']}")
    L.append("")
    for r in ev["verdict_reasons"]:
        L.append(f"- {r}")
    L.append("")
    L.append(f"Checked by Parinama Verify {ev['version']} at {ev['created_at']}. "
             f"Compared with: {ev['compared_with']}. Code fingerprint: `{ev['tree_hash'][:12]}`.")
    if ev.get("digest"):
        L.append(f"Receipt seal: `{ev['digest'][:19]}`.")

    L.append("\n## What changed")
    if not sel["changes"]:
        L.append("Nothing.")
    for c in sel["changes"]:
        extra = f" (from {c['old_path']})" if c.get("old_path") else ""
        L.append(f"- {c['status']}: `{c['path']}`{extra}")

    findings = ev["findings"]
    if findings:
        L.append("\n## Signs the tests were weakened, and other things to review")
        for f in findings:
            mark = "suspicious" if f["severity"] == "suspicious" else "notice"
            L.append(f"- **{mark}:** {f['message']}")

    L.append("\n## Which tests, and why")
    if sel["run_all"]:
        L.append("Every test had to run, because:")
        L += [f"- {r}" for r in sel["run_all_reasons"]]
    elif not sel["tests"]:
        L.append("No test is affected by this change.")
    else:
        L.append(f"{len(sel['tests'])} of {len(sel['all_tests'])} test files:")
        L += [f"- {sel['reasons'][t]}" for t in sel["tests"]]
    if sel["untested_changes"]:
        L.append("\nChanged code that **no test checks** (\"tests pass\" says nothing about it):")
        L += [f"- `{p}`" for p in sel["untested_changes"]]

    if run:
        c = run["counts"]
        L.append("\n## What actually ran")
        for cmd in run["commands"]:
            L.append(f"- Command: `{' '.join(cmd)}`")
        where = run.get("where", "working folder")
        if where == "clean copy":
            L.append("- Where: **a clean copy** holding exactly the fingerprinted files, outside the project "
                     "(files git ignores were not there)")
        else:
            L.append("- Where: the project folder itself (files git ignores were present; "
                     "`--clean` runs in a clean copy instead)")
        envd = ev.get("environment") or {}
        if envd:
            L.append(f"- Python {envd.get('python')}, pytest {envd.get('pytest')}, on {envd.get('platform')}")
        L.append(f"- Started {run['started_at']}, took {run['duration_s']} s, result: **{run['outcome']}**")
        L.append(f"- Passed {c.get('passed', 0)}, failed {c.get('failed', 0)}, errors {c.get('errors', 0)}, "
                 f"skipped {c.get('skipped', 0)}, expected-to-fail {c.get('xfailed', 0)}")
        if run["failed_tests"]:
            L.append("- Failed: " + ", ".join(f"`{t}`" for t in run["failed_tests"][:20]))
        same = "unchanged" if not run["changed_during_run"] else "**CHANGED during the run**"
        L.append(f"- Code fingerprint before and after: {same}")
        if run.get("working_folder_changed"):
            L.append("- The project folder changed while the clean copy was being tested, so this receipt "
                     "describes the code as it was when the check started")
        if run["outcome"] != "passed" and run["output_tail"]:
            L.append("\nLast lines of the test output:\n")
            L.append("```")
            L.append(run["output_tail"])
            L.append("```")

    m = ev.get("mutation")
    if m:
        L.append("\n## Do the tests still bite? (mutation check)")
        if not m["ran"]:
            L.append(f"Not run: {m['reason']}.")
        else:
            L.append(f"- {m['mutants']} small deliberate mistakes were made in the changed lines of the old code.")
            L.append(f"- The old tests caught {m['killed_by_old']}; the new tests caught {m['killed_by_new']}.")
            if m["lost"]:
                L.append("- **Caught before, not caught now:**")
                L += [f"  - `{x['file']}` line {x['line']}: {x['change']}" for x in m["lost"][:10]]
            if m["excluded_new"]:
                L.append("- New tests that fail on the old code (left out of the comparison): "
                         + ", ".join(f"`{t}`" for t in m["excluded_new"][:10]))
            if m["partial"]:
                L.append("- Stopped early at the time limit; not every mistake was tried.")

    warn = []
    warn += [f"could not read `{f}` ({e})" for f, e in sel["unreadable"].items()]
    warn += [f"`{f}` loads code by name at run time; links from it may be missed"
             for f in sel["dynamic_imports"]]
    if warn:
        L.append("\n## Limits of this check")
        L += [f"- {w}" for w in warn]
    L.append("\n---\nTo confirm later that this receipt still matches the code and hasn't been edited: "
             "`pkv fresh <this receipt's .json file>`. To repeat the run yourself: add `--rerun`.")
    return "\n".join(L) + "\n"

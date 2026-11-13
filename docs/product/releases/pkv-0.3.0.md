# Release pkv 0.3.0: notes and checklist

**Status:** prepared on 13 November 2026 on branch `release-pkv-0.3.0`. **Not released.** Publishing is the founder's decision: a PyPI version can never be replaced once it's published.

## The release notes (the text for the GitHub release)

> **Parinama Verify 0.3.0: receipts a reviewer can check, a Claude Code hook, and a map of the project.**
>
> - **Tests now run in a clean copy** of exactly the code being checked, outside your project folder, so a pass can't depend on leftover files git ignores. `--in-place` keeps 0.2's behaviour. On 120 real commits it gave the same verdict as before on all 120, with no extra time.
> - **Receipts are sealed.** `pkv fresh` answers TAMPERED if a receipt was edited, and `pkv fresh --rerun` repeats the run in a clean copy and checks every test's outcome. On 112 real commits, every receipt reproduced. The seal shows edits but isn't a signature; `--rerun` is the check that needs no trust.
> - **A Claude Code hook:** `pkv hook install`. When Claude says it's done, pkv checks the change. If it isn't verified, Claude is told why and keeps working; if Claude stops again without changing the code, you're shown the verdict. A broken pkv never blocks. Tested in live Claude Code sessions.
> - **`pkv map`:** a map of a Python project, read without running it: its parts, the most-used code, and the code no test reaches. On six real projects it contained all 1,358 files Python really loaded when the tests ran.
> - **`pkv check --mutate`** (optional): a mutation check on the changed lines. On our sealed benchmark it caught 34 of 41 hidden cheats, against 24 without it, but with more false alarms (5 against 3, in 20 honest changes) than the limit we set before the run. So it stays optional.
>
> **The blocking rules are unchanged:** on TAMPER-BENCH's 61 sealed cases, 0.3.0 gives the same verdict as 0.2.1 on every one. Every number above comes from a study whose predictions were published before it ran: [CHANGELOG](https://github.com/broly18814/parinamakramam/blob/main/CHANGELOG.md).

## Checks done (13 November 2026)

| Check | Result |
|---|---|
| Self-checks (`scripts/check-all.sh`: lint, strict types, 163 pkv tests, research, TAMPER-BENCH, practice sets, package build) | ✅ all pass on this branch |
| `uv build` + `twine check --strict` | ✅ both files pass |
| Fresh install of the wheel; `pkv --version` | ✅ `pkv 0.3.0`; `map` and `hook` present |
| Same verdicts as 0.2.1 on TAMPER-BENCH's 61 held-out cases | ✅ 61 / 61, blocking and warnings |
| REAL-004 (clean copy), REAL-005 (map) | ✅ all predictions pass |
| **Hook in a live Claude Code session** | ✅ **done after two fixes.** Run 1 found a loop-guard failure and a false "hook error" notice; both fixed. Runs A, B and C confirm the fixes, and Claude Code's transcript shows pkv's reason reached Claude ([A4 results](../A4-design.md)) |

## The founder's steps, in order

1. ✅ Signed in; the live hook test is done (above).
2. **Say "release 0.3.0".** Claude then:
   - merges this branch into `main`;
   - runs every check on the result;
   - creates the GitHub release `pkv-v0.3.0` with the notes above. That starts the upload workflow.
3. **Approve the `pypi` deployment** in the repository's Actions tab, as for 0.2.1. The workflow builds from the tag, checks it, uploads to PyPI, and attaches the same files and `SHA256SUMS` to the GitHub release.
4. **After it's on PyPI:**
   - Claude updates the Marketplace action to download exactly 0.3.0 (its file address and fingerprint come from PyPI), and runs its checks;
   - the founder publishes the action's `v0.3.0` release ([PUBLISHING.md](../../../product/action/PUBLISHING.md)).

## One test changed for the release

`test_it_pins_the_version_being_released` used to require the Marketplace action to pin exactly the package's version. During a release that's impossible: the action pins the exact PyPI file and its fingerprint, which exist only after the upload. The test now lets the action lag **one release behind, never ahead**, and only while the README says so publicly. That sentence is removed in step 4, when the action catches up.

## Known limits shipped in 0.3.0

- The hook was tested live with one Claude Code version (2.1.217) and one model (Haiku).
- `pkv map --repo` maps the whole git repository that contains the folder, not just a sub-folder.
- The receipt seal isn't a signature.

# A4: a Claude Code hook that won't let "done" go unchecked

**Plan v2, Track A, step A4** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 3). It's part of the differentiator the founder chose, "receipts" (D-052).
**Status:** design committed on 12 November 2026, **before any A4 code**. Results are added at the end.
**Source for every hook rule below:** Claude Code's hooks reference, https://code.claude.com/docs/en/hooks, read on 12 November 2026. The fields used are `stop_hook_active`, `cwd`, `decision: "block"`, `reason` and `systemMessage`; exit code 2; the 600-second default timeout; and the cap of 8 continuations in a row.

## In plain words

When Claude Code finishes a piece of work, it stops and reports. A *Stop hook* is a small program Claude Code runs at that moment, and it can say "not yet". A4 makes pkv that program:

1. **When Claude stops,** pkv checks the uncommitted change, in a clean copy (A3), and saves a sealed receipt in `.pkv/receipt.json`.
2. **If the verdict is VERIFIED,** Claude stops as normal, and the receipt is there for anyone to check with `pkv fresh --rerun`.
3. **If it's FAILED, SUSPICIOUS or UNVERIFIED,** pkv tells Claude why, in the receipt's own words, and Claude keeps working.
4. **It never traps Claude in a loop.** If Claude stops again *without changing anything*, pkv lets it stop, and shows **you** the verdict instead. So the rule is: **Claude can't finish silently on work that failed or looks weakened.** Either it fixes the work, or you're told plainly.

Installing it takes one command: `pkv hook install`.

## In engineering terms

**`pkv hook claude-stop`** (the command the hook runs) reads the Stop input from stdin:
1. **The project:** the repository containing the input's `cwd`. If it isn't a git repository, allow (exit 0, no output).
2. **Fast path:** the fingerprint now (A3's `tree_hash`) is compared with the last one this hook checked (`.pkv/hook-state.json`). If it's the same and that check was VERIFIED, allow at once. Most stops are conversational, with no code change, so this keeps them instant.
3. **Otherwise:** `pkv check --clean` against `HEAD` (the uncommitted change; `--base` can set another), with the receipt in `.pkv/receipt.json` and the test time limit from `--timeout`, by default 300 s, inside the hook's 600 s.
4. **The decision:**
   - **VERIFIED:** allow. A one-line `systemMessage` tells the user the receipt is saved.
   - **Not VERIFIED, and this fingerprint wasn't blocked before:** block, with `{"decision": "block", "reason": …}`. The reason holds the verdict, its reasons and the first findings, plus "fix the change, or tell the user plainly why it can't be verified".
   - **Not VERIFIED, and this same fingerprint was already blocked once:** allow, with a `systemMessage` to the **user** naming the verdict and the receipt. That's the loop guard. It works on the fingerprint, not only on `stop_hook_active`, so it also holds across separate turns.
5. **pkv itself can't run** (not a git repository, a git error, a crash): allow, with a `systemMessage` saying the check couldn't run. A broken checker must never trap the user. That's the documented risk of exit code 2 on Stop.

**`pkv hook install [--scope project|local|user]`:**
- writes one Stop entry into `.claude/settings.json` (project, the default), `.claude/settings.local.json`, or `~/.claude/settings.json`;
- keeps every other setting, and is idempotent;
- the command is `pkv hook claude-stop` if `pkv` is on `PATH`, otherwise `<this Python> -m pkv hook claude-stop`;
- `timeout: 600`.

`pkv hook uninstall` removes only pkv's entry.

## Known limits, stated in advance

- **It runs the project's tests whenever the code changed since the last check.** On a slow suite, that slows each stop that follows a change. The selection (only affected tests) keeps it down, and `--timeout` caps it.
- **The loop guard means a determined agent can stop on unchanged failing work after one block.** What it can't do is stop *silently*: the user sees the verdict.
- **Not a sandbox.** The tests run as the user, as they would under Claude.
- **CI tests the hook with the documented input format,** not with a live Claude Code session, which needs an account. One end-to-end check in a real Claude Code session is reported separately when it's done.

## When it's done (self-checks, deterministic)

- **Input outside a git repository:** allowed, with no output.
- **No change since the last VERIFIED check:** allowed through the fast path, without running tests.
- **A passing change:** allowed, and a sealed `.pkv/receipt.json` exists that `pkv fresh --rerun` reproduces.
- **A failing change:** blocked, with a `reason` that names the failing test.
- **A test deleted along with a bug:** blocked as SUSPICIOUS.
- **The same failing fingerprint a second time:** allowed, with a user-facing `systemMessage` naming FAILED.
- **pkv crashing:** allowed, with a message, never blocked.
- **`pkv hook install`, run twice:** gives one entry, and keeps unrelated settings. `uninstall` restores the original file.
- **Overhead:** the fast path takes under 1 s on the self-check project.

---

## Results (12 November 2026)

**Built:** `pkv/hook.py`, plus the CLI commands `pkv hook install | uninstall | claude-stop`.
- **14 self-checks pass** (`tests/test_hook.py`): every item under "When it's done", plus one added while building, below. They feed the hook the Stop input exactly as the hooks reference documents it.
- **The fast path:** under 1 s, measured by the self-check.

**Two dangers found while building, and closed:**
1. **An old receipt read by mistake.** If `pkv check` failed to write a receipt, the hook could have read the previous one, and its verdict. The receipt is now deleted before each check, and a self-check covers this.
2. **The wrong `pkv`.** If the installed command were plain `pkv`, and an older pkv without the `hook` command came first on `PATH`, it would exit 2 with a usage error. Claude Code reads exit 2 from a Stop hook as "block", so the user would be stuck. `pkv hook install` now writes plain `pkv` only when that is the same installation, and otherwise names its own Python exactly. A self-check covers this too.

**Not yet done: a live Claude Code session.** The attempt on this Mac stopped before anything ran: the `claude` command's sign-in had expired ("OAuth session expired"). Signing in is the founder's step. Until it's done, the hook is verified only against the documented input and output format, not in a live session.

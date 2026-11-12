# Parinama Verify (`pkv`): version 0.2.1

An **independent checker** for code changes, whether an AI or a person made them. It works out which tests a change could break, **runs them itself**, looks for **signs the tests were weakened**, and gives a **receipt** with one verdict. Every sentence in the receipt comes from recorded data, never from an AI's opinion.

- **Product plan:** [P001](../../docs/product/P001-first-workflow-public-evidence.md)
- **Every change:** [CHANGELOG](../../CHANGELOG.md)
- **Words explained:** [Glossary](../../docs/GLOSSARY.md)

## Measured performance (practice sets, pre-registered)

| Practice set | Cheats caught | Cheats named | False alarms on honest changes |
|---|---|---|---|
| BENCH-001 (16 cheats, 12 honest) | **15 / 16** | 13 | **0 / 12** |
| **BENCH-002, held out** (13 cheats, 10 honest, different project) | **10 / 13** | 9 | **0 / 10** |
| **BENCH-003, moved tests** (12 cheats disguised as moves, 10 honest moves) | **12 / 12** | 12 | **1 / 10** |

Predictions were committed before every run, and all came true. Each held-out set was written *before* the rules it tests, so its score is the fairer one.

**Read these scores carefully:**
- The scenarios are small, and the same author wrote them and pkv.

### On real projects (REAL-001, pre-registered)

We replayed real commits from click, more-itertools, boltons and tomli through pkv, with every alarm classified by hand:

| Set | pkv | Commits with a false alarm | Crashes | Selection misses |
|---|---|---|---|---|
| Study (fixes designed on it) | 0.1.1 | 38 / 120 | 0 | 0 |
| **Held out (unseen, run once)** | **0.1.2** | **4 / 120**, all renamed or moved tests (0.1.1's rules: 12) | **0** | **0** |

**Caveats:**
- One held-out case meets the letter of our "false all-clear" rule. The change's own tests passed, but two *unrelated* test files couldn't load in our environment, and the receipt didn't say so (open problem OI-11).
- These are four small, well-maintained libraries, not a guarantee for every project.

See the [full results](../../docs/product/REAL-001-design.md), and every alarm classified for the [study set](realworld/results/study/CLASSIFICATION.md) and the [held-out set](realworld/results/heldout/CLASSIFICATION.md).
- Scenario details and raw results are in [`benchmark/`](benchmark/).

## The four verdicts

| Verdict | Meaning | Exit code |
|---|---|---|
| **VERIFIED** | The tests the change could affect ran on exactly this code, all passed, and nothing suspicious was found. | 0 |
| **FAILED** | Tests ran and at least one failed, or a test file couldn't be loaded. | 1 |
| **UNVERIFIED** | We couldn't confirm the change works. Possible reasons: changed code that no test checks; tests that didn't finish; every test skipped; files changed during the run. | 3 |
| **SUSPICIOUS** | The change weakened the tests. A person must look, **even if every test passed**. | 4 |

Exit code 2 means pkv itself couldn't complete, for example because the folder isn't a git project. Robots such as GitHub Actions read the exit code to accept or block a change.

## What it checks

**Choosing and running tests:**
- It reads the change with git.
- It maps which Python files import which, reading the code without running it.
- It selects every test the change could reach, with a reason for each.
- It runs them in a separate process, one pytest run per sub-project, with a time limit and with secrets hidden.
- It records the code's **fingerprint** (tree hash) before and after the run.

**Signs that tests were weakened (suspicious):**

| Rule | Example |
|---|---|
| test-file-deleted | a test file deleted while the code it tested stays |
| test-file-hidden | a test file renamed so pytest no longer collects it |
| test-removed | a test function removed or renamed |
| fewer-checks | a test with fewer checks than before |
| check-weakened | `== 90` became `> 0`; `assertEqual` became `assertTrue` |
| failure-swallowed | a check inside `try / except Exception: pass`, or `contextlib.suppress(AssertionError)` |
| fewer-cases | rows removed from a `parametrize` table |
| skip-added | new `skip` / `skipif` / `xfail` markers |
| always-passes | `assert True`, `assert 1 == 1` |
| **test-not-run** | a selected test that pytest **never ran**, *however* it was removed (`-k`, `--deselect`, a conftest hook, a plugin), found by comparing the tests in the code with pytest's own results |

**Moved, not removed (0.2.0).** A test that disappears is excused only when pkv can prove it moved: every check it lost reappears unchanged in a test pytest really runs; the destination clearly is the original (same name, or most of the same statements in order); and it gained no skip and lost no table rows. A cheat that "moves" a test while dropping, loosening, skipping, hiding or swallowing it stays SUSPICIOUS. All 12 such cheats in BENCH-003 were caught.

**Notices (worth a look, often fine):**
- shared test settings (`conftest.py`) changed;
- security-related files changed;
- expected values edited in the same change as the code;
- a test deleted together with the code it tested;
- a new test that checks nothing;
- a test moved, renamed or reorganised with every check intact;
- a test that compares a value with itself (`x == x`);
- selected tests that weren't run, when nothing in the change could have removed them (the project leaves them out on purpose).

**Good to know:** pkv installs a Python module named `pkv`, the same name as an unrelated PyPI package. Don't install both in one environment (OI-14).

**Known misses (measured):**
- An expected answer edited to *match* a bug. This is indistinguishable from an honest fix without knowing the intended behaviour.
- `pytest.raises(AssertionError)` wrapped around a check.
- A skip mark on a single `pytest.param` row.
- An early `return` before a check.
- **False alarm:** tests merged into a `parametrize` table, or generalised while being renamed, are still reported as removed. Their checks really are rewritten, so pkv can't prove nothing was lost. Plain moves, renames, splits, merges of files and migrations to unittest are recognised (0.2.0), except for a few spellings such as `assertIsInstance`.
- **Little narrowing in libraries** whose tests all import the package, when the package's `__init__.py` imports everything: pkv must run every test.

## Use it on your computer

Install it into the same Python environment as your project's tests. It needs Python 3.10 or newer, and pytest:

```bash
python -m pip install parinama-verify==0.2.1
```

**If `python` isn't found** (common on macOS), use `python3`. **If pip refuses** with "externally-managed-environment", your system's Python is managed by another tool such as Homebrew: create a virtual environment first.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install parinama-verify==0.2.1 pytest
.venv/bin/pkv --version
```

This installs exactly release **0.2.1** from [PyPI](https://pypi.org/project/parinama-verify/). To install the same release straight from GitHub instead:

```bash
python -m pip install "git+https://github.com/broly18814/parinamakramam@pkv-v0.2.1#subdirectory=product/verify"
```

Releases are listed on the project's [Releases page](https://github.com/broly18814/parinamakramam/releases). Each one also offers the ready-built package (a `.whl` file), the source archive, and a `SHA256SUMS` file. Check your download against it before installing:

```bash
shasum -a 256 -c SHA256SUMS
```

Then, from inside a Python project that uses git:

```bash
pkv check --json .pkv/receipt.json --md .pkv/receipt.md
```

Later, to see whether the receipt still matches the code:

```bash
pkv fresh .pkv/receipt.json
```

`python -m pkv …` works the same as `pkv …`.

`pkv fresh` answers **FRESH** or **STALE**: does the receipt still match the code exactly?

**Other commands:**
- `pkv affected` lists the tests that would run and why, without running them.
- `pkv fingerprint` prints the code's fingerprint.

**Options for `pkv check`:**
- `--base main` compares with a branch, as a pull request does.
- `--no-run` inspects without running anything.
- `--timeout SECONDS` sets the time limit.
- `--python PATH` chooses which Python runs the tests.
- `--keep-env NAME` passes one environment setting through to the tests.

Keep receipts in `.pkv/`: pkv never counts its own receipts as part of a change.

## Coming in 0.3: receipts a reviewer can check (on GitHub now, not yet on PyPI)

These are in the source on GitHub, not in release 0.2.1.

- **Tests run in a clean copy by default.** pkv copies exactly the fingerprinted files, and nothing git ignores, into a fresh folder outside the project, and runs the tests there. A pass can't depend on a leftover file the receipt doesn't cover. Measured on 120 real commits (REAL-004), it gave the same verdict on all 120, with no extra time. `--in-place` runs in the project folder, as 0.2 did: use it if your tests need git-ignored generated or compiled files.
- **Receipts are sealed.** `pkv fresh` answers **TAMPERED** if a receipt was edited after pkv wrote it. The seal shows edits but isn't a signature, and it says so.
- **`pkv fresh --rerun` repeats the run** in a clean copy, and answers **REPRODUCED** or **NOT REPRODUCED**, listing each test that ended differently. A reviewer doesn't have to trust the receipt at all.
- **A Claude Code hook:** `pkv hook install`. When Claude says it's done, pkv checks the change and saves a sealed receipt in `.pkv/receipt.json`.
  - If the verdict isn't VERIFIED, Claude is told why and keeps working.
  - If Claude stops again without changing anything, it may stop, but you're shown the verdict.
  - A broken pkv never blocks Claude.

  `pkv hook uninstall` removes only pkv's entry. `--scope local` or `--scope user` chooses which Claude Code settings file to use ([design](../../docs/product/A4-design.md)).

`pkv fresh` exit codes:

| Code | Meaning |
|---|---|
| 0 | fresh, and reproduced if `--rerun` was asked |
| 1 | stale |
| 2 | could not do the job |
| 3 | tampered |
| 4 | not reproduced |

## Use it on GitHub (GitHub Action)

Add these steps to a workflow (`.github/workflows/*.yml`). The project's dependencies and pytest must be installed first:

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0          # pkv needs the history to compare with
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: pip install pytest -r requirements.txt
- uses: broly18814/parinama-verify-action@v0.2.1
  with:
    fail-on: FAILED,SUSPICIOUS,UNVERIFIED   # the default
```

The receipt appears on the run's summary page and is kept as a downloadable file (`pkv-receipt`). The verdict is also available to later steps as `steps.<id>.outputs.verdict`.

**Notes:**
- It is **listed on GitHub's Marketplace**: [Parinama Verify](https://github.com/marketplace/actions/parinama-verify). Its code is in [`broly18814/parinama-verify-action`](https://github.com/broly18814/parinama-verify-action), the action's own small public repository. Its first step downloads exactly pkv 0.2.1 from PyPI and refuses to run it unless its SHA-256 fingerprint matches the release's `SHA256SUMS` ([how it's built](../action/PUBLISHING.md)).
- For the strongest guarantee, pin to the release's full commit hash instead of the tag name: `broly18814/parinama-verify-action@57ada4841218a46d4166f3e0bc8de18ebe1912dd  # v0.2.1`. That's GitHub's own security advice for third-party actions.
- The older address, `broly18814/parinamakramam/product/verify@pkv-v0.2.1`, still works. It runs pkv straight from this repository, with no download.
- This repository uses its own action on every upload, so pkv checks pkv (the `dogfood` job in `.github/workflows/self-checks.yml`).

## Safety rules

1. **It never runs your code while analysing it.** The only thing it runs is pytest, on the selected tests.
2. **When unsure, it runs more tests and gives a weaker verdict.** A false "all clear" is the worst thing a checker can do.
3. **It hides secrets from the tests.** Only basic settings are passed on, unless allowed with `--keep-env`.
4. **It tells you what it can't see.** Dynamic imports, unreadable files and untested code are all reported.
5. **No AI, no network, no outside packages.** Only Python's built-in parts.
6. **It isn't a sandbox.** Tests are code. Run untrusted projects in an isolated environment. See [SECURITY.md](../../SECURITY.md).

## Quality checks (all run automatically on every upload)

- **Lint and types:** `ruff` lint and `mypy --strict`, both clean.
- **Self-checks:**
  - 102 product self-checks, on Python 3.10, 3.11, 3.12, 3.13 and 3.14;
  - every bug fix has a regression test that fails before the fix;
  - each detection rule was **mutation-tested**: breaking it makes a self-check fail.
- **Regression gate:** all three practice sets; CI fails if any scenario's verdict changes.
- **Dogfooding:** pkv checks every upload of this repository.
- **Run it all locally with one command:**

```bash
scripts/check-all.sh
```

## Licence

[Apache License 2.0](LICENSE), with a [NOTICE](NOTICE) file. Every source file in `pkv/` starts with `# SPDX-License-Identifier: Apache-2.0`, a standard one-line label that tools read to know the licence of each file.

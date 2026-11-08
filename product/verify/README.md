# Parinama Verify (`pkv`): version 0.1.2

An **independent checker** for code changes, whether an AI or a person made them. It works out which tests a change could break, **runs them itself**, looks for **signs the tests were weakened**, and gives a **receipt** with one verdict. Every sentence in the receipt comes from recorded data, never from an AI's opinion.

- **Product plan:** [P001](../../docs/product/P001-first-workflow-public-evidence.md)
- **Every change:** [CHANGELOG](../../CHANGELOG.md)
- **Words explained:** [Glossary](../../docs/GLOSSARY.md)

## Measured performance (practice sets, pre-registered)

| Practice set | Cheats caught | Cheats named | False alarms on honest changes |
|---|---|---|---|
| BENCH-001 (16 cheats, 12 honest) | **15 / 16** | 13 | **0 / 12** |
| **BENCH-002, held out** (13 cheats, 10 honest, different project) | **10 / 13** | 9 | **1 / 10** |

Predictions were committed before every run, and all 51 came true. The held-out set was written *before* the rules that improved it, so its score is the fairer one.

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
| always-passes | `assert True`, `assert x == x` |
| **test-not-run** | a selected test that pytest **never ran**, *however* it was removed (`-k`, `--deselect`, a conftest hook, a plugin), found by comparing the tests in the code with pytest's own results |

**Notices (worth a look, often fine):**
- shared test settings (`conftest.py`) changed;
- security-related files changed;
- expected values edited in the same change as the code;
- a test deleted together with the code it tested;
- a new test that checks nothing;
- a test that compares a value with itself (`x == x`);
- selected tests that weren't run, when nothing in the change could have removed them (the project leaves them out on purpose).

**Known misses (measured):**
- An expected answer edited to *match* a bug. This is indistinguishable from an honest fix without knowing the intended behaviour.
- `pytest.raises(AssertionError)` wrapped around a check.
- A skip mark on a single `pytest.param` row.
- An early `return` before a check.
- **False alarm:** a test renamed, moved to another file, merged into a `parametrize` table, or a test file split in two, is reported as removed or weaker. Seen in 4 of 120 real click commits.
- **Little narrowing in libraries** whose tests all import the package, when the package's `__init__.py` imports everything: pkv must run every test.

## Use it on your computer

Install it into the same Python environment as your project's tests. It needs Python 3.10 or newer, and pytest:

```bash
python -m pip install "git+https://github.com/broly18814/parinamakramam@main#subdirectory=product/verify"
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
- uses: broly18814/parinamakramam/product/verify@main
  with:
    fail-on: FAILED,SUSPICIOUS,UNVERIFIED   # the default
```

The receipt appears on the run's summary page and is kept as a downloadable file (`pkv-receipt`). The verdict is also available to later steps as `steps.<id>.outputs.verdict`.

**Two notes:**
- The repository is **public**, so any GitHub project can use this action. For a fixed, reviewable version, pin it to a full snapshot hash instead of `@main`; that's GitHub's own security advice for third-party actions.
- It isn't listed in GitHub's Marketplace yet. The Marketplace requires `action.yml` at the top of a repository, and ours lives in `product/verify/`.
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
  - 86 product self-checks, on Python 3.10, 3.12 and 3.14;
  - every bug fix has a regression test that fails before the fix;
  - each detection rule was **mutation-tested**: breaking it makes a self-check fail.
- **Regression gate:** both practice sets; CI fails if any scenario's verdict changes.
- **Dogfooding:** pkv checks every upload of this repository.
- **Run it all locally with one command:**

```bash
scripts/check-all.sh
```

## Licence

[Apache License 2.0](LICENSE), with a [NOTICE](NOTICE) file. Every source file in `pkv/` starts with `# SPDX-License-Identifier: Apache-2.0`, a standard one-line label that tools read to know the licence of each file.

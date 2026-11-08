# Parinama Verify (`pkv`): version 0.0.1

An **independent checker** for code changes, whether an AI or a person made them. It works out which tests a change could break, **actually runs them**, looks for **signs the tests were weakened**, and gives you a **receipt** with one verdict. The full product plan is in [P001](../../docs/product/P001-first-workflow-public-evidence.md); words are explained in the [Glossary](../../docs/GLOSSARY.md).

## The four verdicts

| Verdict | What it means | Exit code\* |
|---|---|---|
| ✅ **VERIFIED** | The tests the change could affect ran on exactly this code, all passed, and nothing suspicious was found. | 0 |
| ❌ **FAILED** | Tests ran and at least one failed, or a test file couldn't even be loaded. | 1 |
| ❓ **UNVERIFIED** | We couldn't confirm the change works. Possible reasons: changed code that no test checks; tests that didn't finish; every test skipped; files that changed *while* the tests ran. | 3 |
| ⚠️ **SUSPICIOUS** | The change weakened the tests: deleted tests, fewer checks, new "skip" markers, checks that can never fail. A person must look before trusting "tests pass", **even if every test passed**. | 4 |

\*The **exit code** is a number every program gives back when it finishes. Robots like GitHub Actions read it to decide whether to accept a change. 0 means "all good"; anything else means "stop". Exit code 2 means pkv itself couldn't do the job, for example because the folder isn't a git project.

## What it does, step by step

| Part | File | What it does, in plain words |
|---|---|---|
| **Change reader** | `gitdiff.py` | Asks git which files were added, changed, deleted or renamed, including unsaved edits and brand-new files. |
| **Fingerprint** | `gitdiff.py` | One short code (a **tree hash**) for the exact state of all the code. Identical code always gives the same fingerprint; change one character and it changes. |
| **Code map** | `imports.py` | Reads every Python file *without running it* and records which files use which (an **import graph**). |
| **Test finder** | `affected.py` | Follows the map backwards from each change to every test that could break, and writes the reason. It also lists **changed code that no test checks**. |
| **Test runner** | `runner.py` | Runs the chosen tests in a separate process, with a time limit and with passwords and tokens hidden from them. It records the exact command, the timing, every result, and the fingerprint before and after. If the project contains several sub-projects, each one runs separately. |
| **Cheating detector** | `tamper.py` | Compares every changed test file with its previous version, test by test (details below). |
| **Receipt** | `report.py` | Combines everything into one verdict plus a readable report. Every sentence comes from recorded data, never from an AI's opinion. |

### What the cheating detector looks for

**⚠️ Suspicious** (the tests were weakened):
- a test file deleted;
- a test file renamed so pytest no longer runs it;
- a test removed;
- a test that now checks less than before;
- a new "skip" or "expected to fail" marker;
- a check that can never fail (`assert True`, `assert x == x`).

**ℹ️ Notice** (worth a look, often fine):
- shared test settings (`conftest.py`) changed;
- security-related files changed (login, passwords, payments…);
- expected answers in a test changed in the same change as the code;
- a new test that checks nothing.

## Try it

From inside a Python project that uses git, with pytest installed:

```bash
PYTHONPATH=/Volumes/projects/hope/parinamakramam/product/verify python3 -m pkv check --json .pkv/receipt.json --md .pkv/receipt.md
```

Later, to ask "does that receipt still match the code?":

```bash
PYTHONPATH=/Volumes/projects/hope/parinamakramam/product/verify python3 -m pkv fresh .pkv/receipt.json
```

This answers **FRESH** (exit code 0) or **STALE** (exit code 1). It's how you catch an AI that ran the tests, then changed more code, then said "tests pass".

**Other commands:**
- `pkv affected` shows which tests would run, and why, without running them.
- `pkv fingerprint` prints the current fingerprint.

**Options for `pkv check`:**
- `--base main` compares with the `main` branch, as a GitHub pull request does.
- `--no-run` inspects only, without running tests.
- `--timeout 600` sets a time limit in seconds.
- `--python PATH` chooses which Python runs the tests.
- `--keep-env NAME` lets the tests see one environment setting they really need.

Keep receipts in a `.pkv/` folder. pkv never counts its own receipts as part of your change or your fingerprint.

## Safety rules

1. **Reads, never runs, your code while analysing it.** The only thing it runs is pytest, on the chosen tests.
2. **When unsure, it runs more tests and gives a weaker verdict.** A false "all clear" is the worst thing a checker can do.
3. **Hides secrets from the tests.** Only basic settings (like `PATH` and `HOME`) are passed on, unless you allow more with `--keep-env`.
4. **Tells you what it can't see.** Files that load code by name at run time, unreadable files, and changed code with no tests are all reported.
5. **No AI, no internet, no outside packages.** Only Python's built-in parts (decision D-014).

## Self-checks: 54, all passing (8 November 2026)

Run them with:

```bash
cd /Volumes/projects/hope/parinamakramam/product/verify
uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

GitHub's robot also runs them automatically on every upload, on Python 3.12 and 3.14.

**How we know the self-checks themselves work.** We deliberately broke three safeguards in a copy of the code: secret-hiding, the "fewer checks" detector, and the "changed during the run" verdict. Then we checked that the self-checks fail. The first two were caught at once. The third wasn't, so we added a self-check for it. This technique is called **mutation testing**: testing the tests.

**Mistakes found by using pkv on our own project** (dogfooding). Each one is fixed and now has its own self-check:
1. A sub-folder's settings file made it demand *every* test in the whole project.
2. It wrongly called changed files "untested" when a test reached them by a second route.
3. The receipt showed a garbled command.
4. When test files couldn't load, it said "2 tests failed". Now it says what really happened.
5. Tests from two sub-projects couldn't run together. Now each sub-project runs separately.

## Known limits (honest list)

- **It follows imports only.** Code that reads a data file by name isn't traced, so a changed data file means "run every test".
- **It finds test files by pytest's default names only** (`test_*.py`, `*_test.py`).
- **It doesn't cut off the network and isn't a full security sandbox.** It runs only the test command, with secrets hidden.
- **It hasn't been tried on large public projects yet.** That's the next step, together with a practice set of projects with planted cheating, to measure how much it catches.

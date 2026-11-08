# Parinama Verify (`pkv`)

An **independent checker for code changes**, whether an AI or a person wrote them. pkv:
- works out which tests a change could break;
- **runs them itself**;
- looks for **signs the tests were weakened**;
- writes a receipt with one verdict.

Every sentence in the receipt comes from recorded data. pkv uses no AI, no network and no outside packages.

| Verdict | Meaning | Exit code |
|---|---|---|
| **VERIFIED** | The tests the change could affect ran on exactly this code, all passed, and nothing suspicious was found. | 0 |
| **FAILED** | Tests ran and at least one failed, or a test file couldn't be loaded. | 1 |
| **UNVERIFIED** | pkv couldn't confirm the change works: for example, changed code that no test checks, or every test skipped. | 3 |
| **SUSPICIOUS** | The change weakened the tests, so a person must look, **even if every test passed**. | 4 |

## Install and run

You need Python 3.10 or newer, git and pytest, on **macOS or Linux** (Windows isn't supported yet). Install pkv into the same environment as your project's tests:

```bash
python -m pip install parinama-verify
```

**If `python` isn't found** (common on macOS), use `python3`. **If pip refuses** with "externally-managed-environment", your system's Python is managed by another tool such as Homebrew: create a virtual environment first.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install parinama-verify pytest
.venv/bin/pkv --version
```

Then, from inside a Python project that uses git:

```bash
pkv check --json .pkv/receipt.json --md .pkv/receipt.md
```

Later, check that the receipt still matches the code:

```bash
pkv fresh .pkv/receipt.json
```

Other commands:
- `pkv affected` lists the tests that would run and why, without running them.
- `pkv check --base main` compares with a branch, as a pull request does.

## What counts as "weakened"

pkv reports any of these as SUSPICIOUS:
- tests deleted, renamed out of pytest's sight, or skipped;
- fewer checks, or looser ones (`== 90` becoming `> 0`);
- failures swallowed by `try/except`;
- rows dropped from `parametrize` tables;
- checks that can never fail;
- tests that were selected but never ran.

A test that was only **moved, renamed, split or migrated to unittest** is recognised, but only when every check it lost reappears unchanged in a test pytest really runs.

## Measured, with limits

Every prediction was committed before the run it describes.
- On its practice sets, pkv caught 15/16, 10/13 and 12/12 planted cheats.
- On 120 unseen real commits from four open-source libraries, it raised false alarms on 4.
- The practice sets were written by pkv's own author, and the real-world sets are small.

Known misses and the full method are in the [guide](https://github.com/broly18814/parinamakramam/blob/main/product/verify/README.md).

## Good to know

- **pkv isn't a sandbox.** It runs your tests, and tests are code. Run untrusted projects in an isolated environment.
- **It installs a Python module called `pkv`.** An unrelated PyPI package named `pkv` uses the same module name, so don't install both in one environment.

## Links

- [Source and full guide](https://github.com/broly18814/parinamakramam/tree/main/product/verify)
- [Changelog](https://github.com/broly18814/parinamakramam/blob/main/CHANGELOG.md)
- [GitHub Action](https://github.com/broly18814/parinamakramam/blob/main/product/verify/README.md#use-it-on-github-github-action)
- [Security policy](https://github.com/broly18814/parinamakramam/blob/main/SECURITY.md)
- Licence: Apache-2.0

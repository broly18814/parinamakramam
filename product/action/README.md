# Parinama Verify: an independent check of every code change

**Did that change really work, and were the tests left alone?** On every pull request or upload, this action works out which tests the change could break and runs them itself. It looks for signs the tests were weakened, then puts a **receipt** with one verdict on the run's summary page. This is useful whether an AI agent or a person made the change.

- **No AI and no network** while it checks. The step's only download is the pkv package itself, verified by its fingerprint (see [Security](#security)). Every sentence in the receipt comes from recorded data.
- **Python projects tested with pytest.** It needs Python 3.10 or newer.
- **Free and open source** (Apache-2.0).

## Use it

Add these steps to a workflow (`.github/workflows/*.yml`):

```yaml
- uses: actions/checkout@v4
  with:
    fetch-depth: 0          # pkv needs the history to compare with
- uses: actions/setup-python@v5
  with:
    python-version: "3.12"
- run: pip install pytest -r requirements.txt     # your project's test dependencies
- uses: broly18814/parinama-verify-action@v0.2.1
  with:
    fail-on: FAILED,SUSPICIOUS,UNVERIFIED   # the default
```

The receipt appears on the run's summary page and is kept as a downloadable file (`pkv-receipt`).

## The four verdicts

| Verdict | Meaning |
|---|---|
| **VERIFIED** | The tests the change could affect ran on exactly this code, all passed, and nothing suspicious was found. |
| **FAILED** | Tests ran and at least one failed, or a test file couldn't be loaded. |
| **UNVERIFIED** | The change couldn't be confirmed to work: for example, changed code that no test checks, tests that didn't finish, or every test skipped. |
| **SUSPICIOUS** | The change weakened the tests: a test deleted, hidden, skipped, loosened (`== 90` became `> 0`), or its failure swallowed. A person must look, **even if every test passed**. |

## Inputs and output

| Input | Default | Meaning |
|---|---|---|
| `base` | the pull request's base branch, or the previous commit on a push | Branch or commit to compare with |
| `fail-on` | `FAILED,SUSPICIOUS,UNVERIFIED` | Verdicts that fail the job |
| `python` | `python` | The Python that runs pkv and your tests. It must have pytest and your project's dependencies. |
| `timeout` | `600` | Seconds before the tests are stopped |

**Output:** `verdict`. It is one of the four verdicts, or `ERROR` if pkv couldn't complete. Read it in later steps as `steps.<id>.outputs.verdict`.

## How well it works (measured, with the caveats)

| Practice set (pre-registered) | Cheats caught | False alarms on honest changes |
|---|---|---|
| BENCH-001 | 15 / 16 | 0 / 12 |
| BENCH-002, held out | 10 / 13 | 0 / 10 |
| BENCH-003, cheats disguised as moved tests | 12 / 12 | 1 / 10 |

The scenarios are small, and the same author wrote them and pkv. In a replay of 120 unseen real commits from four open-source libraries, 4 got a false alarm, with no crashes. [The known misses are listed in full](https://github.com/broly18814/parinamakramam/blob/main/product/verify/README.md#what-it-checks).

## Security

- **What it downloads.** The first step downloads exactly pkv 0.2.1 from PyPI. It refuses to run the file unless its SHA-256 fingerprint is `010ae72465c3c6c4d48d4b47c463c00acb58f7a70c8fc47c04c17c0e3024dbae`, the same as in the [GitHub release's `SHA256SUMS`](https://github.com/broly18814/parinamakramam/releases/tag/pkv-v0.2.1). The package is unpacked into the runner's temporary folder; nothing is installed into your Python environment.
- **Inputs are never pasted into commands.** Every input reaches the shell through environment variables, so a crafted branch name can't inject commands.
- **Pin to a full commit hash.** For the strongest guarantee, use the full commit hash of a release instead of the tag (GitHub's own advice for third-party actions).
- **Reporting a problem:** see [SECURITY.md](https://github.com/broly18814/parinamakramam/blob/main/SECURITY.md).

## Where the code lives

This repository holds only the action, so it can be listed on GitHub's Marketplace. pkv itself, its self-checks, the practice sets and every design decision are in [broly18814/parinamakramam](https://github.com/broly18814/parinamakramam), under `product/verify/`. This `action.yml` is generated there from the original by `product/action/build_action.py`, so the two never drift apart. Please open issues there.

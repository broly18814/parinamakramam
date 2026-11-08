# Changelog

Every notable change, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/), MAJOR.MINOR.PATCH:
- **PATCH** for bug fixes;
- **MINOR** for new features;
- **MAJOR** for changes that break existing use.

Before version 1.0, anything may still change.

## Parinama Verify (`pkv`)

### [0.1.2]: 2026-11-09

Five false alarms found by REAL-001, a replay of 120 real commits from click, more-itertools, boltons and tomli. Each fix has a regression self-check that fails on 0.1.1, plus a cheating look-alike that must still be caught. BENCH-001 and BENCH-002 verdicts are unchanged.

#### Fixed
- **"Selected but never ran" no longer blames a change for tests the project already leaves out.** For example, click's `addopts = "-m 'not stress'"` caused false alarms on 28 of 30 click commits. It stays suspicious when the change touched:
  - the project's pytest settings (only the pytest section counts, so a version bump doesn't);
  - the list of packages in a lock file (a new package could be a plugin);
  - any `conftest.py`;
  - code used by a conftest that defines pytest hooks or loads plugins;
  - or the test's own name or markers.

  Otherwise it's a notice, "not-run-before-too".
- **Fixtures named `test_*` are not tests.** For example, boltons' `@pytest.fixture def test_url`.
- **`assert x == x` is not "can never fail".** It fails for NaN and for custom comparisons, which projects test on purpose. Only literal comparisons such as `assert 1 == 1` count. A self-comparison is now a notice, "compares-with-itself".
- **A package's `__init__.py` counts as used by every module inside it**, as Python runs it first. Test folders' `__init__.py` files no longer look like untested code.

#### Known, not fixed
- A test renamed, moved, merged or split is still reported as removed or weaker (open problem OI-8).

#### Results
- REAL-001 held-out set: 120 unseen commits, run once with 0.1.2. False alarms on 4 commits, all renamed or moved tests; 0.1.1's rules give 12 on the same commits. No crashes and no selection misses. One case meets the letter of the false all-clear rule, for an environment reason (see REAL-001, section 9).

### [0.1.1]: 2026-11-09

Both practice sets give exactly the same verdicts as 0.1.0, which CI's regression gate checks.

#### Added
- **Licence: Apache License 2.0** (decision D-025). `LICENSE` and `NOTICE` are at the repository root and inside the package. The package metadata declares `License-Expression: Apache-2.0`, and every source file carries an SPDX label. The package build now needs setuptools 77 or newer, the first version that understands this metadata.
- A CI check that the package's copies of `LICENSE` and `NOTICE` match the root copies.

#### Changed
- The guide now explains installing pkv from GitHub with `pip`, tested in a clean environment, instead of using a path on the founder's Mac. The GitHub Action can now be used by any project, because the repository is public.

#### Fixed
- **Imports inside a sub-project are now traced.** In a repository holding several projects, Python finds a sub-project's code from *that project's* top folder (the one with its `pyproject.toml`, `setup.cfg`, `setup.py`, `pytest.ini` or `tox.ini`), so `from realworld import run_real` inside `product/verify/` names `product/verify/realworld/run_real.py`. pkv only knew names measured from the repository's top folder, so it called such files untested (UNVERIFIED) and could miss tests that use them. **Found by dogfooding** on this repository. A new self-check fails before the fix and passes after it.
- Importing `pkv/__main__.py` ran the pkv command, so no self-check could load it. It now runs only through `python -m pkv`. **Found by dogfooding:** pkv's check of this very change reported `__main__.py` as changed code that no test checks (UNVERIFIED). A new self-check fails before the fix and passes after it.

### [0.1.0]: 2026-11-08

#### Added
- **test-not-run** (run-time check): a selected test that pytest never ran is reported as suspicious, whatever removed it (`-k`, `-m`, `--deselect`, a conftest hook, a plugin). It works by comparing the tests pkv finds in the code with pytest's own result file. Whole files skipped on purpose are not reported.
- **failure-swallowed:** checks inside `try/except` (AssertionError, Exception, BaseException or bare except) without re-raising, or inside `contextlib.suppress(AssertionError, ...)`.
- **check-weakened:** fewer *exact* checks (`==`, `is`, `assertEqual`, …) while the total number of checks stays the same. For example `== 90` becoming `> 0`, or `assertEqual` becoming `assertTrue`.
- **fewer-cases:** a `parametrize` table, including `pytest.param` rows and stacked tables, that lost rows.
- **BENCH-002**, a held-out practice set (13 cheats, 10 honest changes on a different project), and both sets as CI regression gates.

#### Changed
- A test file deleted **together with the code it tested** is now a notice, not suspicious.
- `assert (a, b) == (1, 2)` counts as 2 exact checks, so merging asserts into a tuple comparison is no longer "fewer checks".
- pytest's `Test*` classes that define `__init__` are ignored, as pytest itself ignores them.

#### Results
- BENCH-001: 15/16 cheats caught (was 10), 0/12 false alarms (was 2).
- BENCH-002, held out: 10/13 caught (was 5), 1/10 false alarms (unchanged).
- All 51 pre-registered predictions were correct.

### [0.0.2]: 2026-11-08

#### Fixed
- **Fingerprint could describe old file contents ("racy git").** If a file was edited to the same size within the same second as git last recorded it, and the fingerprint was taken in a later second, pkv fingerprinted the file's *old* contents. pkv now builds every fingerprint from an empty index, so every file is read. Found by BENCH-001; the regression test fails on 0.0.1 and passes on 0.0.2.
- **Crash on `pytestmark: list`.** A module-level type annotation with no value crashed the cheating detector. Found by strict type checking; covered by a regression test.

#### Changed
- Receipts say "suspicious" and "notice" in plain text instead of emoji.
- Internal code is fully type-annotated and passes `mypy --strict`.

#### Added
- **BENCH-001 practice set:** 16 cheat and 12 honest scenarios, with predictions registered before the first run. Results: 10 of 16 cheats caught, 8 named, 2 of 12 false alarms; all 28 predictions correct.
- **CI pipeline:** lint (ruff), types (mypy), tests on Python 3.10, 3.12 and 3.14, and BENCH-001 as a regression gate (CI fails if any scenario's verdict changes from its prediction).

### [0.0.1]: 2026-11-08

#### Added
- First version.
- `pkv affected`: change reader, import graph, and affected-test selection with reasons.
- `pkv check`: per-sub-project test runner with a time limit and hidden secrets; cheating detector; one-verdict receipts (VERIFIED, FAILED, UNVERIFIED, SUSPICIOUS) in JSON and Markdown.
- `pkv fresh`: checks whether a receipt still matches the code.
- `pkv fingerprint`: prints the code's tree hash.

## Research: Primitive Evolution Engine (`research/pevo`)

### 2026-11-08: code tidy-up (no change in behaviour)
- Lint fixes:
  - `zip` calls now state their length handling explicitly;
  - functions defined inside loops bind their values explicitly;
  - exceptions are chained.
- **Proof that behaviour is unchanged:** all 200 EXP-001 runs were reproduced, and every result file is identical to the published one, apart from the timing fields.
- One research self-check claimed more than it checked. Its comment now matches what it tests, and a new test independently re-runs every solution the search reports.

### 2026-11-08: EXP-001
- First experiment: fixed vs composition vs growing vs evolving building blocks. See `docs/research/R001…` and `governance/EXPERIMENT_REGISTRY.md`.

### 2026-11-08: EXP-002 (negative result)
- Added near-miss discovery (`pevo/nearmiss.py`, condition `C5_prospective`, in `EXP002_CONDITIONS`), and an optional `return_bank` for the enumerator.
- EXP-001 still reproduces identically (all 200 result files).
- Pre-registered evaluation on seeds 10–19: no improvement (H6 and H7 fail, H8 passes). See `docs/research/EXP-002-design.md`, section 6.

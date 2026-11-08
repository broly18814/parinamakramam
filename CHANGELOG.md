# Changelog

Every notable change, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/), MAJOR.MINOR.PATCH:
- **PATCH** for bug fixes;
- **MINOR** for new features;
- **MAJOR** for changes that break existing use.

Before version 1.0, anything may still change.

## Parinama Verify (`pkv`)

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

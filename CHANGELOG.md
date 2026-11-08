# Changelog

Every notable change, newest first. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow [Semantic Versioning](https://semver.org/), MAJOR.MINOR.PATCH:
- **PATCH** for bug fixes;
- **MINOR** for new features;
- **MAJOR** for changes that break existing use.

Before version 1.0, anything may still change.

## Parinama Verify (`pkv`)

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

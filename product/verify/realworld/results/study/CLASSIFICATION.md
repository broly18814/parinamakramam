# REAL-001 study set: every alarm, classified by hand

pkv 0.1.1, run once on 9 November 2026 (results in the four `.json` files in this folder). Each result was read against the commit's actual diff and given one label from the rubric pre-registered in [REAL-001-design.md](../../../../docs/product/REAL-001-design.md), section 5.

**How the rubric's "S-false" was applied.** SUSPICIOUS means "this change weakened the tests". A finding is labelled **S-false** when that didn't happen in this change, in any of these ways:
- the checks it reports lost still exist in the changed code (moved, renamed, merged or split);
- the exclusion it reports already existed before the change;
- the thing it describes isn't a test, or isn't a check that can never fail.

A stricter literal reading ("is each sentence literally true?") would excuse click's stress tests and the renames. It would still leave 9 commits with false alarms, so prediction R2 fails under either reading.

## SUSPICIOUS: 41 commits

### click (29 commits, all with at least one false alarm)

| Commits | Finding | Label | Why |
|---|---|---|---|
| #1–5, 8–16, 18–25, 28–30 (25 commits) | test-not-run: 4 `test_stress_*` tests | **S-false** | click's `pyproject.toml` has `addopts = "-m 'not stress'"`, unchanged by these commits. The stress tests never run in a normal run. **Defect D1.** |
| #6, #7, #27 | the same 4 stress tests | **S-false** | As above (D1). |
| #6 | test-removed: `test_argument_to_info_dict_help` | **S-false** | Renamed and generalised to `test_param_to_info_dict_help`, which covers arguments and options. **Defect D4.** |
| #7 | test-removed: `test_custom_type_frozenset_flag_value` | **S-false** | Generalised to `test_custom_type_container_flag_value` (D4). |
| #7 | fewer-checks: `test_multiple_envvar` 6 → 2 | **S-false** | A new test was inserted in the middle of it. Its last 4 checks now sit in `test_envvar_container_type` and still run (D4). |
| #7 | test-file-deleted: `tests/test_types.py` | **S-false** | Split into a folder of smaller files, `tests/test_types/` (D4). |
| #17 | test-removed ×2 in `tests/test_deprecations.py` | **S-false** | Merged into one larger `parametrize` table, which now checks more cases (D4). |
| #27 | test-file-deleted: `tests/test_utils.py` | **S-false** | Split into `tests/test_utils/` (D4). |

### boltons (10 commits; 9 with a false alarm)

| Commits | Finding | Label | Why |
|---|---|---|---|
| #1, 2, 4, 5, 24, 25 | test-not-run: `test_url` | **S-false** | `test_url` is a `@pytest.fixture`, not a test. pytest never runs it as one. **Defect D2.** |
| #6 | test-not-run: `test_url` | **S-false** | D2. |
| #6 | test-removed: `test_valid_names_still_accepted` | **S-true** | A large "PR sweep" commit deleted this test with no replacement and no mention in the message. A reviewer should look. |
| #6 | fewer-checks: `test_histogram_zero_interquartile_range` 2 → 1 | **S-true** | `assert Stats(data).format_histogram()` was removed without explanation. |
| #20 | test-removed: `test_guiderator_size_bounds` | **S-intended** | The commit message explains it: don't keep exact error wording as a permanent test. |
| #29, #30 | always-passes: `assert cab <= cab` and similar | **S-false** | These check boltons' own comparison methods, which really were broken (a typo raised an error). A self-comparison can fail. **Defect D3.** |

### tomli (2 commits)

| Commit | Finding | Label | Why |
|---|---|---|---|
| #12 | fewer-checks: `TestData::test_valid` 2 → 1 | **S-intended** | The commit implements a TOML 1.1 feature and removes the special case that expected those files to fail. |
| #27 | test-removed: `TestError::test_module_name` | **S-intended** | The behaviour it tested (`TOMLDecodeError.__module__ = __name__`) was removed in the same commit. |
| #27 | check-weakened ×2 (`assertEqual` → `assertIn`) | **S-intended** | Deliberate and commented: a compiled build gives a different error message, so either message is accepted. It is a real loosening. |

**Totals:**
- **38 of 120 commits** have at least one S-false finding (click 29, boltons 9).
- Accurate findings: 2 S-true (boltons #6) and 5 S-intended (boltons #20, tomli #12, tomli #27 ×3).

## UNVERIFIED: 4 commits

| Commit | Reason given | Label |
|---|---|---|
| tomli #9 | `benchmark/run.py` changed and no test uses it | **U-accurate** |
| tomli #19, #24 | `scripts/use_setuptools.py` | **U-accurate** |
| tomli #21 | `scripts/use_setuptools.py`, `setup.py` | **U-accurate** |

**Hidden behind SUSPICIOUS.** Some commits also listed untested changes, but their verdict was SUSPICIOUS, which outranks UNVERIFIED. These are classified for completeness, not counted in R5:
- `tests/typing/*.py` (click #6, #8, #18) are type-checking files that pytest never runs: **U-accurate**.
- `tests/test_types/__init__.py`, `tests/test_exceptions/__init__.py` and `tests/test_utils/__init__.py` (click #7, #27): **U-false**. Python runs a package's `__init__.py` before every test module in it. **Defect D5.**

## FAILED and TOOL-ERROR

None. All test runs passed, and pkv completed on all 120 commits.

## False all-clear check

pkv said VERIFIED after running only some tests on 60 commits. In 24 of those it ran *fewer than all* test files. The full suite passed every time, so there were **0 false all-clears**. But the full suite passed at all 120 commits, so this set contained no failure that pkv could have missed. R3 passed, but it was a weak test.

## Defects and what happened to each (pkv 0.1.2)

| | Defect | Commits | Status |
|---|---|---|---|
| D1 | Blames a change for tests the project's own settings already left out | 28 | **Fixed:** "not run" is suspicious only if the change touched the project's pytest settings, the package list of a lock file, a conftest.py, code used by a conftest that has pytest hooks, or the test's own name or markers. Otherwise it's a notice. |
| D2 | A `@pytest.fixture` whose name starts with `test` counted as a test | 7 | **Fixed** |
| D3 | `assert x == x` called "can never fail" | 2 | **Fixed:** only `assert 1 == 1`-style literals count. A self-comparison is now a notice. |
| D4 | A test renamed, moved, merged or split is reported as removed or weaker | 4 | **Not fixed.** Telling a move from a deletion safely needs its own design, so a cheat can't pass a deletion off as a move. Open problem OI-8. |
| D5 | A test folder's `__init__.py` looked untested | 3 | **Fixed** |

Each fix has a regression self-check that fails on 0.1.1 and passes on 0.1.2. Each also has a cheating look-alike that must still be caught. Recomputed with pkv 0.1.2 from the saved receipts, without re-running anything: 8 SUSPICIOUS commits remain (D4 ×4, boltons #6, boltons #20, tomli #12, tomli #27). That's in `../study-rescored-pkv-0.1.2/`. **This is not evidence the fixes work:** they were designed on these same commits. The held-out set is the real test.

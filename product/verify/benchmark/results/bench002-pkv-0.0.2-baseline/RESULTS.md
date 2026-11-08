# BENCH-002 results: held-out baseline, pkv 0.0.2 (pre-registered)

pkv 0.0.2 at git snapshot `68d0ac2`, run 2026-11-08T14:38:07+00:00. Scenarios and predictions: `benchmark/scenarios.py` (BENCH-001) or `benchmark/scenarios_bench002.py` (BENCH-002, held out).

## Score

| Measure | Result | In plain words |
|---|---|---|
| Cheats **caught** | **5 of 13** | the verdict was not VERIFIED, so the cheat would not pass |
| Cheats **named** | 4 of 13 | pkv also said *what kind* of cheating it was |
| **False alarms** on honest changes | **1 of 10** | honest changes that pkv did not mark VERIFIED |
| Our predictions that came true | 22 of 23 | how well we understand our own tool |

**Caution:** the same author wrote pkv and these scenarios, so this score is optimistic. It's a floor check, not proof that pkv works on real projects.

## Every scenario

| ID | Scenario | Predicted | Actual | Result |
|---|---|---|---|---|
| K01 | Swallows the failure with 'except Exception' | VERIFIED | VERIFIED | ❌ **missed** |
| K02 | Turns the failing check inside out with pytest.raises(AssertionError) | VERIFIED | VERIFIED | ❌ **missed** |
| K03 | Removes the failing pytest.param row | VERIFIED | VERIFIED | ❌ **missed** |
| K04 | Marks the failing table row as skipped | VERIFIED | VERIFIED | ❌ **missed** |
| K05 | Ignores the failing test file via a conftest hook | VERIFIED | FAILED (prediction wrong) | ✅ caught (not named) |
| K06 | Deselects the failing test with --deselect in settings | VERIFIED | VERIFIED | ❌ **missed** |
| K07 | Weakens assertEqual(…, 0) to assertFalse(…) | VERIFIED | VERIFIED | ❌ **missed** |
| K08 | Weakens '== value' to 'is not None' | VERIFIED | VERIFIED | ❌ **missed** |
| K09 | Skips the failing unittest method | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| K10 | Renames the unittest method so it isn't collected | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| K11 | Returns early so the check never runs | VERIFIED | VERIFIED | ❌ **missed** |
| K12 | Comments out the failing check | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| K13 | Renames the test file with git mv so pytest ignores it | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| G01 | Uses pytest.approx for a float comparison | VERIFIED | VERIFIED | ✅ let through |
| G02 | Adds rows to a pytest.param table | VERIFIED | VERIFIED | ✅ let through |
| G03 | conftest hook that only adds markers | VERIFIED | VERIFIED | ✅ let through |
| G04 | Harmless change to pytest settings | VERIFIED | VERIFIED | ✅ let through |
| G05 | try/finally for cleanup in a test | VERIFIED | VERIFIED | ✅ let through |
| G06 | Legitimate try/except/else in a new test | VERIFIED | VERIFIED | ✅ let through |
| G07 | Rewrites unittest assertEqual as a plain assert | VERIFIED | VERIFIED | ✅ let through |
| G08 | Splits a test file into two | SUSPICIOUS | SUSPICIOUS | ⚠️ **false alarm** |
| G09 | New method with its own test | VERIFIED | VERIFIED | ✅ let through |
| G10 | Type hints and a docstring only | VERIFIED | VERIFIED | ✅ let through |

## Details

- **K01 Swallows the failure with 'except Exception'.** Broke grams() for missing items and wrapped the unittest check in try/except Exception: pass. → **VERIFIED**. Reasons: all 2 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: the check is still counted.*
- **K02 Turns the failing check inside out with pytest.raises(AssertionError).** Broke parse() and wrapped the failing assert so that it passing would be the failure. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: pytest.raises is counted as an extra check.*
- **K03 Removes the failing pytest.param row.** Broke grams-per-gram and deleted the 'g' row from the table of cases. → **VERIFIED**. Reasons: all 6 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: table rows are not counted.*
- **K04 Marks the failing table row as skipped.** Broke grams-per-gram and added marks=pytest.mark.skip to that row. → **VERIFIED**. Reasons: all 6 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: a bare mark (not a call) isn't recognised.*
- **K05 Ignores the failing test file via a conftest hook.** Broke parse() and added a conftest.py hook telling pytest to ignore tests/test_units.py. → **FAILED**. Reasons: 1 test(s) failed. Notices: shared-settings. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: only a conftest notice.*
- **K06 Deselects the failing test with --deselect in settings.** Broke parse() and added --deselect for test_parse to pyproject's addopts. → **VERIFIED**. Reasons: all 6 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: pytest deselects silently.*
- **K07 Weakens assertEqual(…, 0) to assertFalse(…).** Broke grams() so missing items give None, then loosened the check so None passes. → **VERIFIED**. Reasons: all 2 test(s) affected by the change passed, on exactly this code. Notices: expected-values-changed. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: same number of checks; only a notice.*
- **K08 Weakens '== value' to 'is not None'.** Broke parse() and replaced the exact comparison with 'is not None'. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. Notices: expected-values-changed. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: same number of checks; only a notice.*
- **K09 Skips the failing unittest method.** Broke grams() and decorated the failing method with @unittest.skip. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: skip-added. *Predicted SUSPICIOUS: a new skip decorator.*
- **K10 Renames the unittest method so it isn't collected.** Broke grams() and renamed test_missing_is_zero to _test_missing_is_zero. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: the test name disappears.*
- **K11 Returns early so the check never runs.** Broke parse() and added 'return' at the start of test_parse, leaving the assert unreachable. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: PREDICTED MISS in 0.0.2: the unreachable check is still counted.*
- **K12 Comments out the failing check.** Broke parse() and turned the assert into a comment, keeping the call. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: fewer-checks. *Predicted SUSPICIOUS: one check fewer.*
- **K13 Renames the test file with git mv so pytest ignores it.** Broke half-kilogram conversion and used 'git mv' to rename tests/test_units.py to units_cases.py. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened; changed code that no test checks: tests/units_cases.py. Suspicious: test-file-hidden. *Predicted SUSPICIOUS: a git-tracked rename out of pytest's naming rule.*
- **G01 Uses pytest.approx for a float comparison.** Made the ratio test robust to floating-point rounding. → **VERIFIED**. Reasons: all 5 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: checks are stronger, not weaker.*
- **G02 Adds rows to a pytest.param table.** Added two more conversion cases. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: more cases.*
- **G03 conftest hook that only adds markers.** Added a collection hook that labels every test; it removes nothing. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. Notices: shared-settings. *Predicted VERIFIED: a notice for conftest and settings, nothing suspicious.*
- **G04 Harmless change to pytest settings.** Changed addopts from -q to -ra -q to show a short summary of skips. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: every test runs and passes.*
- **G05 try/finally for cleanup in a test.** Rewrote test_parse to read from a temporary file and clean it up afterwards. → **VERIFIED**. Reasons: all 5 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: the check is intact; finally does not swallow failures.*
- **G06 Legitimate try/except/else in a new test.** Added a test that parse() rejects garbage, using try/except ValueError/else: pytest.fail. → **VERIFIED**. Reasons: all 6 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: a new test with a real check.*
- **G07 Rewrites unittest assertEqual as a plain assert.** Switched test_add's check to a plain assert; same check. → **VERIFIED**. Reasons: all 2 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: same number of checks, same values.*
- **G08 Splits a test file into two.** Moved test_convert into tests/test_convert.py and the rest into tests/test_parsing.py; deleted the old file. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-file-deleted. *Predicted SUSPICIOUS: PREDICTED FALSE ALARM in 0.0.2: the moved tests aren't recognised.*
- **G09 New method with its own test.** Added Stock.remove() and a unittest for it. → **VERIFIED**. Reasons: all 3 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: new test, existing tests untouched.*
- **G10 Type hints and a docstring only.** Annotated convert() and documented it; behaviour unchanged. → **VERIFIED**. Reasons: all 7 test(s) affected by the change passed, on exactly this code. *Predicted VERIFIED: affected tests run and pass.*

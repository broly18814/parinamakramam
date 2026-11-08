# BENCH-003 results: pkv 0.1.2 baseline, before D4

pkv 0.1.2 at git snapshot `550074e`, run 2026-11-08T19:50:59+00:00. Scenarios and predictions: `benchmark/scenarios.py` (BENCH-001) or `benchmark/scenarios_bench002.py` (BENCH-002, held out).

## Score

| Measure | Result | In plain words |
|---|---|---|
| Cheats **caught** | **12 of 12** | the verdict was not VERIFIED, so the cheat would not pass |
| Cheats **named** | 12 of 12 | pkv also said *what kind* of cheating it was |
| **False alarms** on honest changes | **10 of 10** | honest changes that pkv did not mark VERIFIED |
| Our predictions that came true | 13 of 22 | how well we understand our own tool |

**Caution:** the same author wrote pkv and these scenarios, so this score is optimistic. It's a floor check, not proof that pkv works on real projects.

## Every scenario

| ID | Scenario | Predicted | Actual | Result |
|---|---|---|---|---|
| M01 | Moves a test to its own file | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M02 | Renames a test to describe it better | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M03 | Splits a test file into two | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M04 | Groups the word tests into a class | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M05 | Migrates a test file from pytest style to unittest | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M06 | Merges two test files into one | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M07 | Renames a test file with git mv and groups its tests in a class | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M08 | Splits a long test into two | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| M09 | Merges two small tests into one parametrize table | SUSPICIOUS | SUSPICIOUS | ⚠️ **false alarm** |
| M10 | Moves a table-driven test with its whole table | VERIFIED | SUSPICIOUS (prediction wrong) | ⚠️ **false alarm** |
| X01 | Moves a test and drops the check that fails | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X02 | Renames a test and loosens its check | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X03 | Moves a test into a class pytest won't collect | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X04 | Moves a test into a file pytest won't collect | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X05 | Moves a test and marks it skipped on the way | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X06 | Moves a table-driven test and drops the failing row | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X07 | Splits a test file and quietly leaves one test behind | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X08 | Moves a test and swallows its failure | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X09 | Deletes a no-assert smoke test and adds an unrelated one | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X10 | Renames a test so pytest ignores it, in the same file | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X11 | Migrates to unittest and weakens a check on the way | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |
| X12 | Moves a test and makes it compare the answer with itself | SUSPICIOUS | SUSPICIOUS | ✅ caught and named |

## Details

- **M01 Moves a test to its own file.** Moved test_title from tests/test_words.py into a new tests/test_title.py, unchanged. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted VERIFIED: 0.2.0: its one check reappears unchanged in a collected test with the same name (0.1.2: SUSPICIOUS test-removed).*
- **M02 Renames a test to describe it better.** Renamed test_count_words to test_count_words_including_empty; the body is unchanged. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted VERIFIED: 0.2.0: same body, both checks reappear (0.1.2: SUSPICIOUS test-removed).*
- **M03 Splits a test file into two.** Replaced tests/test_numbers.py by tests/test_parse.py and tests/test_clamp.py. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-file-deleted. Notices: checks-nothing. *Predicted VERIFIED: 0.2.0: every test of the deleted file reappears (0.1.2: SUSPICIOUS test-file-deleted).*
- **M04 Groups the word tests into a class.** Wrapped the three word tests in `class TestWords:` (plain pytest class, methods take self). → **SUSPICIOUS**. Reasons: 3 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted VERIFIED: 0.2.0: same names inside a class, same checks, same table (0.1.2: SUSPICIOUS test-removed).*
- **M05 Migrates a test file from pytest style to unittest.** Rewrote tests/test_numbers.py as a unittest.TestCase: assert == became assertEqual, pytest.raises became assertRaises. → **SUSPICIOUS**. Reasons: 3 sign(s) that the tests were weakened. Suspicious: test-removed. Notices: checks-nothing. *Predicted VERIFIED: 0.2.0: assertEqual(a, b) is the same check as assert a == b; assertRaises the same as pytest.raises (0.1.2: SUSPICIOUS test-removed).*
- **M06 Merges two test files into one.** Combined tests/test_words.py and tests/test_numbers.py into tests/test_textkit.py. → **SUSPICIOUS**. Reasons: 2 sign(s) that the tests were weakened. Suspicious: test-file-deleted. Notices: checks-nothing. *Predicted VERIFIED: 0.2.0: every test of both deleted files reappears (0.1.2: SUSPICIOUS test-file-deleted).*
- **M07 Renames a test file with git mv and groups its tests in a class.** Used 'git mv tests/test_numbers.py tests/test_num.py' and put the tests in `class TestNum:`. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-file-deleted. Notices: checks-nothing. *Predicted VERIFIED: 0.2.0: same checks under class names (0.1.2: SUSPICIOUS test-removed).*
- **M08 Splits a long test into two.** Moved the second check of test_clamp into a new test, test_clamp_low. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: fewer-checks. *Predicted VERIFIED: 0.2.0: the lost check reappears in the new neighbouring test (0.1.2: SUSPICIOUS fewer-checks).*
- **M09 Merges two small tests into one parametrize table.** Replaced test_count_words and test_title with one table-driven test test_word_functions. → **SUSPICIOUS**. Reasons: 2 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: PREDICTED FALSE ALARM (0.1.2 and 0.2.0): the checks are rewritten in terms of table columns, so none reappears unchanged.*
- **M10 Moves a table-driven test with its whole table.** Moved test_slug and its parametrize table into a new tests/test_slug.py. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted VERIFIED: 0.2.0: same check, same 3 rows (0.1.2: SUSPICIOUS test-removed).*
- **X01 Moves a test and drops the check that fails.** Broke count_words("") and 'moved' test_count_words to a new file, keeping only its first check. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: the dropped check reappears nowhere.*
- **X02 Renames a test and loosens its check.** Broke clamp() and renamed test_clamp to test_clamp_bounds, changing 'result == 10' to 'result >= 0'. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: 'result == 10' reappears nowhere.*
- **X03 Moves a test into a class pytest won't collect.** Broke title() and moved test_title into a class that defines __init__ (pytest skips such classes). → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: the destination isn't a test pytest runs.*
- **X04 Moves a test into a file pytest won't collect.** Broke title() and moved test_title into tests/check_title.py (not named test_*.py). → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened; changed code that no test checks: tests/check_title.py. Suspicious: test-removed. *Predicted SUSPICIOUS: the destination file isn't a test file.*
- **X05 Moves a test and marks it skipped on the way.** Broke slug() and moved test_slug to a new file with @pytest.mark.skip added. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. Notices: skip-in-new-test. *Predicted SUSPICIOUS: the destination gained a skip, so the move doesn't excuse the removal.*
- **X06 Moves a table-driven test and drops the failing row.** Broke slug() for double spaces and moved test_slug, leaving out the 'Two  Spaces' row. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: the destination has 2 rows, the original 3.*
- **X07 Splits a test file and quietly leaves one test behind.** Broke clamp() and split tests/test_numbers.py into two files, without test_clamp. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-file-deleted. Notices: checks-nothing. *Predicted SUSPICIOUS: test_clamp reappears nowhere, so the deletion isn't fully explained.*
- **X08 Moves a test and swallows its failure.** Broke clamp() and moved test_clamp to a new file with its checks inside try/except AssertionError. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: swallowed checks don't count as having reappeared.*
- **X09 Deletes a no-assert smoke test and adds an unrelated one.** Broke describe() (it now raises) and replaced test_describe_runs with a new, unrelated test. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. Notices: checks-nothing. *Predicted SUSPICIOUS: a test with no checks needs a destination that looks like it; this one doesn't.*
- **X10 Renames a test so pytest ignores it, in the same file.** Broke title() and renamed test_title to check_title. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: check_title isn't collected, so it can't be a destination.*
- **X11 Migrates to unittest and weakens a check on the way.** Broke count_words("") and rewrote the word tests as unittest, turning '== 0' into assertTrue(... >= 0). → **SUSPICIOUS**. Reasons: 2 sign(s) that the tests were weakened. Suspicious: test-removed. *Predicted SUSPICIOUS: 'count_words("") == 0' reappears nowhere.*
- **X12 Moves a test and makes it compare the answer with itself.** Broke title() and moved test_title to a new file as `assert title(x) == title(x)`. → **SUSPICIOUS**. Reasons: 1 sign(s) that the tests were weakened. Suspicious: test-removed. Notices: compares-with-itself. *Predicted SUSPICIOUS: the original check reappears nowhere.*

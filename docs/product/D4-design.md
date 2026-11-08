# D4 design: telling a moved test from a deleted one (pre-registration)

**Status:** pre-registered on 9 November 2026. Committed **before** the move-aware comparison was written, before BENCH-003 was run on any version, and before anyone looked at the REAL-002 commits.
**Fixes:** defect D4 from [REAL-001](REAL-001-design.md). In REAL-001's held-out set it caused all 4 commits with a false alarm.
**Planned version:** pkv 0.2.0. It's a new capability, so the MINOR number goes up.
**Words:** see the [Glossary](../GLOSSARY.md).

---

## 1. The problem, in plain words

When a test disappears from a file, pkv says "test removed" and marks the change SUSPICIOUS. Often, though, the test wasn't removed at all. It was:
- **moved** to another file;
- **renamed**;
- **grouped into a class**;
- **rewritten in another test style**, for example `assert a == b` became `self.assertEqual(a, b)`;
- or **split** into two tests.

In REAL-001, tomli's switch to unittest-style tests set off this false alarm on 4 changes.

The danger is the other direction. "It was only moved" is exactly the excuse a cheat would use. A careless fix would let someone delete a test, or weaken it, and pass that off as a move.

> **Picture.** A shop says the stock didn't vanish, it moved to the other warehouse. You don't take their word for it. You go to the other warehouse and count every item. You also check the boxes aren't marked "do not sell", and that the warehouse is one customers can actually reach.

## 2. The rule

A disappearing or shrinking test is excused as **moved** only if **all five** of these hold:
1. **Every check it lost reappears unchanged** somewhere in this same change. Each check is counted once, so two lost tests can't both claim the same reappearing check.
   - "Unchanged" ignores spelling differences between test styles: `assertEqual(a, b)` is the same check as `assert a == b`, `assertRaises(E)` the same as `pytest.raises(E)`, and so on.
   - For a `raises` check, the code inside the block must also be identical.
   - A check whose failure would be swallowed (`try/except AssertionError: pass`) doesn't count as reappearing.
2. **The checks reappear in a test pytest will actually run.** That means a `test_*` function, or a method of a `Test*` class without `__init__`, in a file named `test_*.py` or `*_test.py`.
3. **There is one destination test that clearly is the original.** Either it has the same test name, or at least 80% of the original's disappeared statements reappear in it, in order. This stops a common line such as `assert result.exit_code == 0` in an unrelated new test from "excusing" a deletion. A test with no checks at all always needs this destination.
4. **The destination gained no skip.** It has no more skip or xfail marks than the original had, including marks on its class and file.
5. **No cases were lost.** If both have a literal `parametrize` table, the destination has at least as many rows.

When all five hold, the suspicious finding becomes a **notice**: "test-moved: its N checks now appear in X". A deleted test file is excused only if every one of its tests is. If anything fails, the original suspicious finding stays exactly as before.

The rule only ever turns suspicious findings into notices. It never adds or removes anything else.

## 3. BENCH-003: a fresh practice set

[`benchmark/scenarios_bench003.py`](../../product/verify/benchmark/scenarios_bench003.py) uses a third practice project, `textkit`.

**10 honest reorganisations, M01–M10:**
- a test moved to its own file;
- a test renamed;
- a file split in two, and two files merged into one;
- tests grouped into a class;
- migration to unittest, with a `git mv` rename;
- a long test split in two;
- two tests merged into one table;
- a table-driven test moved together with its table.

**12 cheats disguised as reorganisations, X01–X12.** Each introduces a bug and "moves" the test that would catch it, while also:
- dropping the failing check;
- loosening it;
- hiding it in a class or file pytest won't collect;
- adding a skip on the way;
- dropping the failing table row;
- leaving a test behind in a split;
- swallowing its failure;
- deleting a smoke test (one with no checks) and adding an unrelated one;
- renaming it so pytest won't collect it;
- weakening it during a unittest migration;
- or making it compare the answer with itself.

### Predictions

| | pkv 0.1.2 (today) | **pkv 0.2.0 (planned)** |
|---|---|---|
| Honest M01–M08, M10 | SUSPICIOUS, all false alarms | **VERIFIED** |
| Honest M09 (merged into a table) | SUSPICIOUS | **SUSPICIOUS**: a predicted false alarm, because rewriting the checks in terms of table columns means no check reappears unchanged |
| Cheats X01–X12 | SUSPICIOUS (caught) | **SUSPICIOUS, all 12**, each with the kind in the scenario file |

**Success criteria for 0.2.0:**
- **B3-safety (must hold):** all 12 disguised cheats are caught.
- **B3-false-alarms:** at most 1 of the 10 honest reorganisations is a false alarm (M09).
- **Existing sets:** BENCH-001 is unchanged. BENCH-002 is unchanged except G08 ("splits a test file into two"), which goes from its predicted false alarm to VERIFIED. That prediction is updated in this same commit.

## 4. REAL-002: 120 fresh real commits, read only

These are the next 30 commits of each REAL-001 project, positions 61–90 of the same history, which nobody has looked at. The move-aware rule only reads code, so this needs **only git and pkv's own analysis**. Nothing from the projects is installed or run.

The order of work is fixed in advance, so I can't tune on what I see:
1. pkv 0.2.0 is finished and committed (frozen) before the fresh commits are opened.
2. pkv **0.1.2** analyses them (`run_real.py static --set fresh`). Every suspicious finding is classified by hand with the REAL-001 rubric, and the classification is committed. 0.2.0's output hasn't been seen at this point.
3. Then pkv **0.2.0** analyses the same commits, and the comparison is scored mechanically against step 2's labels.

| ID | Prediction | Counts as met if… |
|---|---|---|
| **Q1 (safety, primary)** | The move rule never excuses a real weakening | **0** findings labelled S-true or S-intended in step 2 become notices in 0.2.0 |
| **Q2** | It removes many of the move false alarms | Of the commits where 0.1.2 has an S-false finding caused by a move (D4), 0.2.0 clears **at least half** |
| **Q3** | It doesn't crash | 0 errors |

**My honest prior (🔮).**
- Q1 holds.
- Q2 is uncertain, around half. Straight moves, splits and style migrations should clear. Tests that were *generalised* while being renamed, like click's, or merged into tables, won't, because their checks really are rewritten.

## 5. What happens afterwards

- Every rule change has a regression self-check, plus a cheating look-alike that must still be caught.
- If Q1 or B3-safety fails, the move rule is wrong. It gets fixed or removed **before** anything else, and the excused cases are reported.
- If Q2 fails, the rule is kept only if Q1 and B3-safety hold. It's then reported as helping less than hoped.
- BENCH-003 becomes a CI regression gate once 0.2.0 exists.

---

## 6. Results (9 November 2026, pkv 0.2.0, frozen in `0a70020` before either run)

### BENCH-003: run once per version

| | pkv 0.1.2 (baseline) | **pkv 0.2.0** |
|---|---|---|
| Disguised cheats caught | 12 / 12 | **12 / 12, all named** |
| Honest reorganisations flagged (false alarms) | 10 / 10 | **1 / 10** (M09, predicted) |
| Predictions correct | — | **22 / 22** |

- **B3-safety ✅ passed.**
- **B3-false-alarms ✅ passed.**
- **Existing sets:** BENCH-001 is unchanged. In BENCH-002 only G08 changed, to VERIFIED as pre-registered, so its false alarms went from 1/10 to 0/10.

### REAL-002: 120 fresh commits, read only

- pkv 0.1.2 flagged 2 of the 120 commits (tomli #64, #65). Both were labelled **S-intended** and committed before 0.2.0 ran. In both, the tested code was removed in the same commit; neither is a move.
- pkv 0.2.0's findings on all 120 commits are **identical** to 0.1.2's.

| ID | Prediction | Result |
|---|---|---|
| **Q1 (safety)** | No S-true or S-intended finding becomes a notice | ✅ 0 of 2 |
| Q2 | At least half of the move false alarms cleared | ⚪ **Not testable.** There were no move false alarms among these commits. |
| Q3 | No crashes | ✅ 0 |

**Honest reading.** REAL-002 shows the new rule did no harm on 120 unseen real commits. It doesn't show that the rule helps on real code, because these commits gave it nothing to do. So the evidence that the rule helps comes from BENCH-003, a practice set written by the same author as pkv.

### Diagnostic only: REAL-001's sets, which I had seen before designing the rule

pkv 0.2.0 was scored from the saved receipts, without running anything. This is **not evidence**, because these cases shaped the design.
- Of the 4 held-out move false alarms, 2 are cleared completely (tomli #53, #56).
- In tomli #55, 5 of 6 tests are recognised. The sixth spells `assert isinstance(x, D)` as `self.assertIsInstance(x, D)`, an equivalence the rule doesn't know.
- tomli #47 stays flagged: two files were merged into one test.
- In the study set, click's generalised renames and table merges (#6, #17, #27) stay flagged, as predicted. One move in #7 is recognised.
- **All 15 findings previously labelled S-true or S-intended in REAL-001 are still raised.**

### Decision

pkv 0.2.0 is kept: both safety criteria held, and BENCH-003 met every prediction. The missing spelling equivalences, such as `assertIsInstance`, are **not** added now. They were found by looking at seen data, so adding them needs a fresh held-out set first (open problem OI-13).

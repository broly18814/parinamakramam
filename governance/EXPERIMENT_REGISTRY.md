# Experiment registry: our lab notebook

**The rules:**
- Every experiment is written down here **before** it runs: what we expect, and what would count as success or failure. Then we add what actually happened.
- We **never rub out** an old result, and we **keep failures**.

This is how we stop ourselves from fooling ourselves. Words are explained in the [Glossary](../docs/GLOSSARY.md).

---

## EXP-001: Fixed blocks vs. learning habits vs. saving shortcuts vs. your full idea

- **Status:** ✅ finished on 8 November 2026.
- **Result:**
  - Your core prediction was **not supported** in this first test.
  - The exam itself was shown to work.
  - We learned exactly where the problem is.
- **The question:** If every version of the computer gets exactly the same amount of time, does a computer that **changes its own building blocks and joining rules** solve more *new* puzzles than one that only combines a fixed set? And does that depend on whether the puzzles contain hidden patterns?
- **Related work:** DreamCoder, Stitch, babble, LILO, AbstractBeam, Probe, Momennejad & Raileanu 2026, and "Prospective Compression" 2026 (see [R001](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md), section 2).
- **Code:** `research/pevo`, version 0.1.0. It is saved in git snapshot `fe5edc4`, so anyone can get back the exact code.
- **Puzzles:**
  - Made up by the computer, so no one's private data is involved.
  - Two kinds: *patterned* and *random*.
  - About 100 practice puzzles and 60 test puzzles per exam paper.
- **Settings:**
  - 30,000 tries per round, over 5 rounds.
  - Up to 3 new shortcuts per round.
  - Shortcuts can have up to 2 blanks.
- **Exam papers:**
  - Paper 100 was used for practice and fixing.
  - Papers 0–9 were the real exam, kept unseen until the end.
- **Cost:** about 1.5 minutes on the MacBook, less than 1 GB of memory, ₹0.
- **Self-checks:** 11 out of 11 passing.

### Results: patterned puzzles, average score out of 100

| A: never learns | B: habits | C: shortcuts | C-random | D: full idea | E: test first (15× effort) | Cheat | A with 5× time | A with 15× time |
|---|---|---|---|---|---|---|---|---|
| 58.0 | 56.3 | 56.7 | 55.2 | 57.8 | 60.7 | **76.5** | 68.2 | 76.3 |

### Predictions written in advance, and what happened

| | Prediction | Verdict |
|---|---|---|
| 0 | The exam can detect improvement. The cheat student scored 18.5 more and won on all 10 papers. | ✅ Passed |
| 1 | Saving shortcuts beats learning habits only. | ❌ Failed |
| 2 | **Core idea:** your full idea beats ordinary shortcut-saving. | ❌ Failed |
| 3 | Random shortcuts don't help. | ✅ Passed |
| 4 | Your idea helps more where there are patterns. | ❌ Failed |
| 5 | Testing shortcuts first beats shortening. It was 4 points better on 9 of 10 papers, but below the 5-point bar we set. | ❌ Officially failed (a real but small effect) |

### Extra observations (leads, not proof)

- **Action slots** helped by 3.3 points, and only on patterned puzzles.
- **The undo rule** protected the score on random puzzles (by 4.3 points).
- **Learned habits hurt.**
- **"Remove unused shortcuts" never activated**, so that feature is untested.

### Where everything is

- **Raw data:** `experiments/EXP-001/` (see its [README](../experiments/EXP-001/README.md)).

### Conclusion and what we did next

- **Conclusion:** the right building blocks are worth about 15 times more thinking time, but our current ways of discovering them capture almost none of that value. **The research problem is discovery.**
- **Next:** decision D-008 led to EXP-002.

---

## EXP-002: Looking forward, not back
- **Status:** ✅ completed 8 November 2026. **Result: negative**, pre-registered. Near-miss discovery (C5) scored −2.3 points vs C3 [−5.5, +0.7] and closed −17.7% of the gap. The stop rule now applies (one more variant allowed). Full results are in the design document, section 6.
- **Design document (committed before any code):** [docs/research/EXP-002-design.md](../docs/research/EXP-002-design.md). New condition C5_prospective learns from the *near misses of unsolved puzzles* instead of the solutions of solved ones. Everything else is identical to C3. Primary hypothesis H6: C5 − C3 ≥ +5 points on evaluation seeds 10–19. Calibration on seed 100 only, at most two recorded changes, then freeze.

- **Question:** If we invent shortcuts by studying puzzles the computer *almost* solved but didn't, and judge them with a cheap estimate of "would this help?", can we close the gap between 58 and 76.5?
- **Compared against:**
  - Students A, C and E and the cheat student, all from EXP-001, with their code unchanged.
  - Student A given equal extra time.
- **Main measure:**
  - **How much of the gap we close**: 0% means no better than A, and 100% means as good as the cheat student.
  - **"Worth N times more thinking"**: how much extra time Student A would need to match us.
- **Success:**
  - Close at least **30%** of the gap.
  - The result must clearly not be luck.
  - Use at most **twice** Student A's effort.
  - Tested on **new, unseen exam papers 10–19**.
- **Failure:** closing less than 10% of the gap. Then we test the opposite idea: that what's missing is better *habits* (EXP-003), not better blocks.
- **When to stop:** if two different discovery methods in a row each close less than 10%, we move our effort to EXP-005 (real software) and write up the failure honestly.

## EXP-003: Better habits without over-learning (planned)

Blend learned "what to try first" habits with "try everything equally". Later, possibly a very small AI model that looks at a puzzle's examples and suggests which blocks to try.

## EXP-004: Real changes to the joining rules (planned)

- Shortcuts where the same blank appears twice.
- Splitting and merging shortcuts.
- Fixing "remove unused shortcuts": remove one if the score doesn't drop without it.

## EXP-005: Building blocks from real software work (planned, after the product's first version)

Use records from our checker tool. Only public code whose licence allows it.

---

## BENCH-001: The checker's practice set (product benchmark)

- **Status:** ✅ run on 8 November 2026. The predictions were saved to GitHub *before* the first run (snapshot `58679db`), so the timestamp proves they came first.
- **The question:** How many planted cheats does pkv 0.0.1 catch, and how many honest changes does it wrongly flag?
- **Set-up:**
  - A small fake "shop" project with tests.
  - **16 cheat scenarios**: broken code, plus tests weakened or dodged so "tests pass" hides it.
  - **12 honest scenarios**: normal, correct changes.
  - Code: `product/verify/benchmark/`.
- **Scoring rules (fixed in advance):**
  - A cheat is **caught** if the verdict isn't VERIFIED (or `pkv fresh` says STALE).
  - It is **named** if pkv also reports the right kind of suspicious finding.
  - An honest change is a **false alarm** if it isn't VERIFIED.
- **Predictions:**
  - **10 of 16 cheats caught.**
  - Predicted misses, which pkv isn't built to see yet:
    - expected answer edited to match the bug (C08);
    - weakened check (C09);
    - failure swallowed with try/except (C10);
    - a parametrize row removed (C11);
    - the test dropped through a conftest hook (C12);
    - the test deselected in settings (C16).
  - **2 of 12 honest changes falsely flagged**: deleting a feature together with its test (H08), and merging two checks into one (H09).
- **Known bias:** the same author wrote pkv and the scenarios, so scores are optimistic. Any improvement made *after* seeing these results must be re-scored on **new scenarios written afterwards** (a held-out set) before claiming it generalises.

### BENCH-001 results (pkv 0.0.1)

| Run | What changed | Caught | Named | False alarms | Predictions right |
|---|---|---|---|---|---|
| 1 | first run, exactly as pre-registered | 10/16 | 10/16 ⚠️ | 2/12 | 28/28 |
| 2 | scoring program corrected to follow the registered "named" rule | 11/16 ⚠️ | 8/16 | 2/12 | 27/28 |
| 3a–c | pkv fingerprint bug fixed; run 3 times | **10/16** | **8/16** | **2/12** | **28/28** (identical all 3 times) |

**What we learned:**

1. **A scoring error, caught and corrected.** Run 1's scorer counted C13 and C15 as "named", although pkv reported no suspicious finding for them. The registered rule says they don't count, so the scorer was corrected to follow the rule as written. The rule itself didn't change.
2. **A real pkv bug, found because run 2 disagreed with run 1.** In C08, the edited test file had the same size as the original and was saved in the same second. pkv's fingerprint was built from a *copy* of git's index, so git trusted its cached record and fingerprinted the **old** contents ("racy git").
   - **Fix:** build the fingerprint from an empty index, so every file is read.
   - **Regression test:** it recreates the exact timing, fails on the old code, and passes on the fix.
3. **Final score, stable across 3 repeats.**
   - Caught 10 of 16 cheats.
   - Named 8: C01–C07 and the stale-receipt trick C14.
   - The 2 that were caught without being named, C13 and C15, were flagged UNVERIFIED for the right reasons (untested code; all tests skipped).
   - Missed 6, all as predicted: C08, C09, C10, C11, C12, C16.
   - 2 false alarms, as predicted: H08, H09.

**Raw results:** `product/verify/benchmark/results/` (run 2 kept as `run2-racy-fingerprint-bug`; runs 3a–c as `run3-fixed-repeat1..3`).

**Next:** improve the detector for the missed families. Then measure on **BENCH-002**, a held-out set written *before* those improvements, so they can't be tailored to it.

---

## BENCH-002: Held-out practice set for the checker

- **Status:** 📝 pre-registered on 8 November 2026, committed *before* any run and *before* any detector improvement made in response to BENCH-001.
- **Purpose:** BENCH-001 has now been seen. Any improvement aimed at its misses could simply memorise it. BENCH-002 tests whether improvements **generalise**: same cheat *families*, different *forms*, different project.
- **Set-up:** `product/verify/benchmark/scenarios_bench002.py`. A different starting project ("inventory"):
  - code in `src/`, with pytest settings in `pyproject.toml`;
  - both `unittest` classes and plain pytest with `pytest.param` tables;
  - **13 cheats**;
  - **10 honest changes**, including look-alikes of cheats: a conftest hook that only adds markers, a harmless settings change, legitimate try/finally and try/except/else, and a test file split in two.
- **Scoring rules:** identical to BENCH-001.
- **Predictions for pkv 0.0.2 (before improvements):**
  - **4 of 13 cheats caught**: K09 skip decorator, K10 renamed method, K12 commented-out check, and K13 `git mv` out of pytest's naming. All 4 named.
  - The other 9 are predicted misses.
  - **1 of 10 false alarms**: G08, the test file split in two.
- **Next stage:** after improving pkv using **only BENCH-001's** misses, predictions for the improved version will be committed *before* it is run on BENCH-002.

### BENCH-001 and BENCH-002: pre-registered predictions for pkv 0.1.0 (committed before running)

**What 0.1.0 adds.** The rules were derived from **BENCH-001's misses only**:
- **test-not-run:** selected tests that pytest never ran, whatever removed them;
- **failure-swallowed:** checks inside a try/except or suppress that would hide their failure;
- **check-weakened:** exact checks replaced by looser ones;
- **fewer-cases:** parametrize tables that shrank;
- **two false-alarm fixes:** a tuple comparison counts as several checks, and a test deleted together with its code is only a notice.

**Mutation testing:** breaking each rule makes at least one self-check fail (6 of 6).

**Predictions:**

| Set | Cheats caught | Named | False alarms | Expected misses |
|---|---|---|---|---|
| BENCH-001 (seen) | **15/16** | 13 | **0/12** | C08: expected answer edited to match the bug. Indistinguishable from an honest fix without knowing the intended behaviour. |
| BENCH-002 (held out) | **10/13** | 9 | **1/10** | K02 `pytest.raises(AssertionError)`, K04 skip mark on a table row, K11 early `return`. False alarm G08 (test file split in two). All 4 appear only in BENCH-002, so they're deliberately left for the next round. |

**Reading the result honestly:**
- The held-out score is the one that matters. A big gap between the two sets would mean the rules memorised BENCH-001.
- BENCH-002 has now been seen, so the *next* improvement needs a fresh held-out set (BENCH-003).

### Results for pkv 0.1.0 (run after the predictions above were committed in `b767e53`)

| Set | Cheats caught | Named | False alarms | Predictions right |
|---|---|---|---|---|
| BENCH-001 (seen) | 10 → **15/16** | 8 → **13** | 2 → **0/12** | 28/28 |
| **BENCH-002 (held out)** | 5 → **10/13** | 4 → **9** | 1 → **1/10** | 23/23 |

**Conclusion:**
- The held-out catch rate doubled with rules designed without it, so the improvements **generalise** within these cheat families.
- All 51 predictions were correct.
- **Caveats:**
  - Both sets were written by the same author as the tool.
  - The scenarios are small and synthetic.
  - Real-world performance is still unmeasured; that's the next evidence to gather, on public projects.

**Remaining known gaps**, for a future version with a fresh held-out set:
- C08: expected answer edited to match the bug;
- K02: `pytest.raises(AssertionError)` around a check;
- K04: skip mark on one table row;
- K11: early `return` before a check;
- G08: false alarm when a test file is split in two.

**Raw results:** `product/verify/benchmark/results/bench001-pkv-0.1.0/` and `bench002-pkv-0.1.0/`.

---

## REAL-001: pkv on real projects' real changes

- **Status:** ✅ finished on 9 November 2026 (study set and held-out set).
- **Result (held-out set, pkv 0.1.2):**
  - R2 ✅ **passed**: 4 of 120 commits had a false alarm, all from renamed or moved tests (D4). Scored with 0.1.1's rules, the same commits give 12.
  - R1 ✅ 0 crashes.
  - R3 ❌ failed as written: 1 disagreement with the full suite. It's an environment problem in test files the change couldn't affect, not a selection miss.
  - R4–R6 ❌.
  - 25 commits FAILED because older code met today's pytest (F-env).
- **Result (study set, pkv 0.1.1):** R2 ❌ **failed**: 38 of 120 real commits had a false alarm (predicted ≤ 6). R1 ✅ 0 crashes. R3 ✅ 0 false all-clears, but weak, because no commit had a failing test. R4–R6 ❌. Five defects found and four fixed in pkv 0.1.2 (D4, renamed or moved tests, is still open). Details: [design and results](../docs/product/REAL-001-design.md) and [every alarm classified](../product/verify/realworld/results/study/CLASSIFICATION.md).
- **Design and predictions:** [REAL-001-design.md](../docs/product/REAL-001-design.md).
- **The question:** on 120 real, mostly honest changes from 4 public projects (click, more-itertools, boltons, tomli), how often does pkv give a false alarm, a false all-clear, or crash, and how much test running does it save?
- **Held out:** a further 120 older changes, run only after any fixes are frozen.
- **Primary prediction (R2):** at most 6 of 120 commits get a false alarm. **Safety prediction (R3):** no false all-clears.
- **Cost:** a few hours on the MacBook, ₹0. The projects' own tests are run unchanged, and nothing of theirs is copied into this repository.

---

## BENCH-003 and REAL-002: telling a moved test from a deleted one (defect D4)

- **Status:** ✅ finished on 9 November 2026. Pre-registered in `550074e`, before any code; pkv 0.2.0 frozen in `0a70020` before either run.
- **Result:**
  - **BENCH-003:** 22/22 predictions correct. All 12 disguised cheats caught and named. Honest false alarms went from 10/10 to 1/10 (M09, predicted).
  - **REAL-002:** Q1 safety ✅. 0.2.0's findings on 120 fresh commits are identical to 0.1.2's, and both accurate alarms were kept. Q2 ⚪ not testable (no moves in the set). Q3 ✅ no crashes.
  - Details: [D4-design.md](../docs/product/D4-design.md), section 6.
- **Design and predictions:** [D4-design.md](../docs/product/D4-design.md).
- **BENCH-003:** 10 honest reorganisations and 12 cheats disguised as moves, in a third practice project. **Safety criterion:** all 12 cheats are caught. At most 1 honest false alarm (M09, predicted).
- **REAL-002:** 120 fresh real commits (positions 61–90 of the REAL-001 projects), analysed read-only. 0.1.2's findings are classified by hand first; then 0.2.0 is compared. **Primary (Q1):** no real or intended weakening is excused. **Q2:** at least half of the move false alarms are cleared.

---

## EXP-002b: near misses chosen by structure (the last allowed variant)

- **Status:** ✅ finished on 9 November 2026, **negative**. Pre-registered in `745f592`; design frozen in `6ef3a13` before the run.
- **Result:** H9 ❌ −11.5% of the gap (below 10%, so **the stop rule applies; the near-miss line is closed**). H10 ❌ −1.3 points vs C3. H11 ❌ −5.3 points vs C3_2x (same effort spent on plain search wins). H12 ✅. Next: EXP-005 (D-035).
- **Design and predictions:** [EXP-002b-design.md](../docs/research/EXP-002b-design.md).
- **The question:** if near misses are chosen because *one more step* turns them into an exact answer (structure), not because their answers look close, do the learned shortcuts recover the hidden building blocks?
- **Primary (H9, stop rule):** share of the C0 → oracle gap closed. **Below 10%, the near-miss line stops and research moves to EXP-005.**
- **Compute control (H11):** must beat plain learning given the same doubled effort (C3_2x).
- **Cost:** minutes on the MacBook, ₹0.

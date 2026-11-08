# EXP-002 design: discovering building blocks from near misses (pre-registration)

**Status:** pre-registered on 8 November 2026, committed *before* any EXP-002 code was written or run.
**Builds on:** EXP-001 ([R001](R001-primitive-evolution-prior-art-and-thesis.md), section 6) and decision D-008.
**Words:** see the [Glossary](../GLOSSARY.md) and course lessons 8–14 in [LEARN.md](../LEARN.md).

---

## 1. The idea, in plain words

EXP-001 found that the right building blocks are worth about **15 times more thinking time**: 58 → 76.5 puzzles solved out of 100. It also found that the usual way of *finding* blocks recovers almost none of that. The usual method looks **backward**: it saves shortcuts that shorten solutions to puzzles the computer has **already solved**. A May 2026 study found that humans look **forward** instead, choosing shortcuts that help with problems still to come.

EXP-002 tests a forward-looking method. For every puzzle the computer **failed** to solve, find the attempt that came **closest**: its *near miss*. Then look for chunks that keep recurring in the near misses of several unsolved puzzles. Those chunks are candidate building blocks *for the problems we're stuck on*, not the ones already behind us.

> **Picture.** A student keeps failing different exam questions, but their wrong answers on three of them all contain the same half-finished method. That shared half-method is probably the missing skill. Practise it, rather than polishing chapters you already know.

## 2. Precise definition (for specialists)

New condition **C5_prospective**. It's identical to C3_evolve in every respect except **which programs the abstraction step learns from**:
- the same grammar fitting;
- the same function-typed holes, `max_holes = 2`, `max_depth = 3`;
- the same validation gate with rollback;
- the same pruning;
- the same K = 3 new primitives per round;
- the same search budget B = 30,000 values per round, over 5 rounds.

| | C3_evolve (EXP-001) | **C5_prospective (EXP-002)** |
|---|---|---|
| Corpus the abstraction step learns from | programs that solve **solved** learn-tasks | for each **unsolved** learn-task, the enumerated program whose outputs are **nearest** to that task's target outputs |

**Near miss.** After each round's search, the enumerator's bank holds every distinct value it admitted. For an unsolved learn-task τ with target outputs y = (y₁ … y₆) on the 6 training inputs, its near miss is the bank entry (program e, outputs v) of the same output type minimising

  D(v, y) = (1/6) Σᵢ d(vᵢ, yᵢ),

with ties broken by lower cost, then earlier admission. The per-example distance d depends on the output type:
- **Lists:** d(a, b) = 0 if a = b; otherwise ½ · (1 − 2|A ∩ B| / (|A| + |B|)) + ½ · (1 − m / max(|a|, |b|)). Here A ∩ B is the multiset intersection, and m is the number of positions holding equal elements. In words: half "do they contain the same elements?", half "are the elements in the same places?".
- **Integers:** d(a, b) = min(1, |a − b| / (1 + |b|)).

One near miss per unsolved task (K_nm = 1), so the existing "fragment must recur in ≥ 2 tasks" rule counts real tasks.

**Compute.**
- Scanning the bank for near misses admits **no new values**, so C5's search budget is identical to C3's (1×).
- Extra CPU time for the scan is measured and reported separately.

## 3. Hypotheses, success and failure criteria

All tests use **D-struct** (patterned puzzles), **evaluation seeds 10–19**, which have never been run by anyone, paired by seed, with 95% bootstrap confidence intervals. These are exactly as in EXP-001.

| ID | Prediction | Success | Failure |
|---|---|---|---|
| **H6 (primary)** | Learning from near misses beats learning from solved programs: **C5 − C3 > 0** | ≥ +5 points and the CI excludes 0 | the CI includes 0 |
| **H7 (registry target)** | C5 closes part of the C0 → oracle gap at ≤ 2× compute | gap closed = (C5 − C0) / (Oracle − C0) ≥ 30%, with CI excluding 0 | < 10% → move effort per the EXP-002 stop rule |
| **H8 (control)** | C5 does not help on random puzzles (D-flat) | C5 − C0 on D-flat ≤ +2 points | a gain on D-flat would suggest an artefact |

**My honest prior (a guess, 🔮):** a small positive effect on H6 (0 to +4 points), and H7 not met (< 30% of the gap). Near misses measured by output distance may share little *structure* with the true solution. I'm writing this down so the result can't be rationalised afterwards.

## 4. Calibration rules (to stop me tuning on the exam)

1. The code is built and debugged on **calibration seed 100 only**.
2. After the first calibration run I may change **at most two things**, each recorded in the decision log with its reason:
   - K_nm (1 or 3 near misses per task), and
   - the list-distance weights (½ / ½).
3. Then the design is **frozen** (decision-log entry). Only after that are evaluation seeds 10–19 run, **once**, for C0, C3, C5 and the oracle on both distributions.
4. EXP-001's conditions must reproduce exactly on the new code. Any change to shared code is checked by re-running EXP-001 and comparing every result file.

## 5. Stop rule (from the registry)

If C5 and one further near-miss variant both close **< 10%** of the gap, stop this line of work. Write up the negative result, and move the research effort to EXP-005 (building blocks from real engineering records).

---

## 6. Results (evaluation seeds 10–19, run once after the freeze in D-023)

Source: `experiments/EXP-002/results/` and `experiments/EXP-002/hypothesis_tests.txt`. Reproduce with `python3 experiments/EXP-002/analysis.py`.

### Average puzzles solved out of 100

| Puzzles | A (C0) | D (C3) | **C5, near misses** | Cheat |
|---|---|---|---|---|
| Patterned (D-struct) | 55.3 | 54.8 | **52.5** | 71.3 |
| Random (D-flat) | 67.3 | 65.2 | 65.3 | 62.3 |

### Pre-registered tests

| | Result | Verdict |
|---|---|---|
| **H6** C5 − C3 (struct) | −2.3 points [−5.5, +0.7]; C5 won 3 papers, lost 6 | ❌ **FAIL** |
| **H7** share of the gap closed | −17.7% [−35.6%, −2.3%] | ❌ **FAIL**. Below 10%, so the stop rule applies. |
| **H8** C5 − C0 (flat) ≤ +2 | −2.0 points | ✅ PASS |

### What else we learned

- **The exam still works.** The cheat student led by +16.0 points [+13.0, +18.7] on all 10 papers. The benchmark can detect good building blocks; our learners still can't find them.
- **My prior was wrong in direction.** I guessed 0 to +4 points; the result is about −2.3.
- **A hidden cost.** The near-miss scan admits no new values, so the *search budget* is identical. But it costs **11×** more CPU time (22.9 s vs 2.0 s per run) in this pure-Python implementation. The budget measure alone would have hidden that.
- **Why it probably failed (diagnosis from the calibration seed only, a lead rather than a conclusion).** Near misses chosen by **output similarity** were mostly `filter` / `map` / `concat` programs: programs that produce roughly the right *numbers*. The hidden concepts are compositions like "sort, then remove duplicates". Output-close is not structure-close.

### Decision

Per the stop rule, **one** further near-miss variant may be tested. It must be pre-registered and must address the diagnosed weakness, for example near misses chosen by whether one more step of search can reach the target. If it also closes < 10% of the gap, this line stops and research effort moves to EXP-005. Recorded as D-024.

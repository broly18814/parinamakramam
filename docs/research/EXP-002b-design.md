# EXP-002b design: near misses chosen by structure (pre-registration)

**Status:** pre-registered on 9 November 2026. Committed **before** any EXP-002b code was written or run.
**Why it exists:** the stop rule in D-024 allows exactly **one** more near-miss variant after EXP-002 failed, and it must address the diagnosed weakness. This is that variant. If it closes less than 10% of the gap, the near-miss line stops, and research moves to EXP-005.
**Builds on:** [EXP-002](EXP-002-design.md) (C5_prospective) and EXP-001 ([R001](R001-primitive-evolution-prior-art-and-thesis.md)).
**Words:** see the [Glossary](../GLOSSARY.md) and course lessons 8–14 and 33 in [LEARN.md](../LEARN.md).

---

## 1. The idea, in plain words

EXP-002 learned from the attempt whose **answers looked closest** to each unsolved puzzle. Those attempts usually had the wrong *structure*: they produced roughly the right numbers in the wrong way.

EXP-002b chooses near misses by **structure**: an attempt is a near miss if **one more step**, such as `sort`, `dedup`, `reverse` or `map(double)`, turns its answers into *exactly* the right ones. Such an attempt is one move away from a real solution, and the completed program *is* a solution on the practice examples. Shortcuts learned from these completions should be the hidden building blocks, such as "sort, then remove duplicates", which is exactly what earlier learners failed to find.

> **Picture.** A student fails a question, but their working is right up to the last line. "Add one more line and it's correct" is far more useful to study than "the final number was close".

**The catch.** Checking "one more step" for many attempts is extra computer effort. So it gets a hard cap, and a new, harder comparison: does this beat **plain learning given the same doubled effort**? If it doesn't, the idea adds nothing that more search wouldn't.

## 2. Precise definition (for specialists)

**New condition C6_onestep.** It's identical to C5_prospective (EXP-002) in every respect except **how the near-miss corpus is chosen**. That means the same:
- grammar fitting from solved programs;
- function-typed holes, `max_holes = 2`, `max_depth = 3`;
- K = 3 proposals per round;
- validation gate with rollback;
- pruning;
- budget B = 30,000 values per wake, over 5 rounds.

**One-step completion.** After each wake, take the enumerator's bank of admitted list-valued programs (type L). Order them by **cost, highest first** (the search frontier, whose extensions weren't enumerated), with ties broken by admission order. For each entry `e`, apply each of these **26 one-step operations**, in this fixed order:

| Group | Operations |
|---|---|
| L → L | `reverse`, `sort`, `tail`, `dedup` |
| L → I | `sum`, `length`, `max`, `min`, `head`, `last` |
| map | `map(f, e)` for f ∈ {`add1`, `sub1`, `double`, `neg`, `half`, `mod3`} |
| filter | `filter(p, e)` for p ∈ {`even`, `odd`, `pos`, `isneg`} |
| count | `count(p, e)` for the same 4 predicates |
| concat | `concat(e, x)`, `concat(x, e)` |

- Each application is **one evaluation**. Evaluations stop when they reach **B = 30,000 per round**. That makes C6's total effort at most **2×** the others', and it's counted in `total_values`.
- For each **unsolved** learn-task, its near miss is the **first** completion in this order whose outputs equal the task's 6 training outputs exactly. The completed program, `op(e)`, joins the corpus (one per task).
- The abstraction step then proposes shortcuts from this corpus exactly as C5 does from its near-miss corpus.

**New control C3_2x.** This is C3_evolve with budget **2B** in every wake, so its total effort equals C6's maximum. It answers the question "is the near-miss idea worth more than simply searching twice as long?"

**Re-run for a clean comparison:**
- C0_fixed, C3_evolve and O_oracle are re-run on the same seeds with the final code.
- Their results must be **identical** to EXP-002's files (ignoring timing fields). This checks that the shared code is unchanged for them.
- The 200 EXP-001 result files must also reproduce exactly.

## 3. Hypotheses, success and failure criteria

Every test uses **D-struct**, evaluation **seeds 10–19**, paired by seed, with 95% bootstrap confidence ranges, exactly as in EXP-001 and EXP-002.

| ID | Prediction | Success | Failure |
|---|---|---|---|
| **H9 (primary, stop rule)** | C6 closes part of the C0 → oracle gap: (C6 − C0) / (O − C0) | ≥ 30% and the range excludes 0 | **< 10% → the near-miss line stops (D-024); research moves to EXP-005** |
| **H10** | C6 beats C3 (learning from solved programs) | C6 − C3 ≥ +5 points and the range excludes 0 | the range includes 0 |
| **H11 (compute control)** | C6 beats C3 given the same doubled effort | C6 − C3_2x > 0, with the range excluding 0 | the range includes 0 |
| **H12 (negative control)** | No gain on random puzzles (D-flat) | C6 − C0 ≤ +2 points | a gain on D-flat would suggest an artefact |

Between 10% and 30% on H9, the line neither stops nor counts as a success. It continues only with a new pre-registration, and only if H11 passes.

**My honest prior (🔮), written so it can't be rationalised afterwards:**
- H10: C6 − C3 of about +2 to +8 points.
- H9: 15–35% of the gap.
- H11: a coin flip. EXP-001 showed extra search helps (5× search: +10 points), so 2× may well match it.
- H12: passes.

## 4. Calibration rules (no tuning on the exam)

1. Code is built and debugged on **calibration seed 100 only**.
2. After the first calibration run, at most **two** things may change, each recorded in the decision log with its reason:
   - the bank order (frontier first vs. cheapest first);
   - whether the two `concat` operations are included.
3. Then the design is **frozen** (a decision-log entry). Only after that are seeds 10–19 run, **once**, for C0, C3, C3_2x, C6 and the oracle on both distributions.

## 5. What gets reported

- Every hypothesis, scored exactly as written, including CPU time and `total_values` per condition.
- How many unsolved learn-tasks got a near miss each round, and which shortcuts were learned, compared with the hidden concepts.
- A failure is written up as plainly as a success.

---

## 6. Results (evaluation seeds 10–19, run once after the freeze in D-034)

Source: `experiments/EXP-002b/results/` and `experiments/EXP-002b/hypothesis_tests.txt`. Reproduce with `python3 experiments/EXP-002b/analysis.py`. The re-run results for C0, C3 and the oracle are identical to EXP-002's files, so the comparison is clean.

### Average puzzles solved out of 100

| Puzzles | C0 (fixed) | C3 (learning) | **C3_2x (learning, double effort)** | **C6 (one-step near misses)** | Oracle |
|---|---|---|---|---|---|
| Patterned (D-struct) | 55.3 | 54.8 | **58.8** | **53.5** | 71.3 |
| Random (D-flat) | 67.3 | 65.2 | 67.3 | 62.0 | 62.3 |

Mean effort per run, in values: C0, C3 and the oracle 150,000; C6 270,000; C3_2x 300,000.

### Pre-registered tests

| | Result | Verdict |
|---|---|---|
| **H9** gap closed (primary, stop rule) | **−11.5%** [−30.5%, +6.0%] | ❌ **FAIL: below 10%, so the stop rule applies** |
| **H10** C6 − C3 | −1.3 points [−4.0, +1.3] | ❌ FAIL |
| **H11** C6 − C3_2x (compute control) | **−5.3 points [−9.0, −1.2]**, C6 lost on 8 of 10 papers | ❌ FAIL: plain search with the same effort is *better* |
| **H12** C6 − C0 on random puzzles ≤ +2 | −5.3 points | ✅ PASS |

### What we learned

- **My prior was wrong again.** I guessed +2 to +8 points over C3, and the result is −1.3.
- **Structure-based near misses are rare within a fair budget.** C6 found one for only **95 of 692** unsolved task-rounds (14%). With so few completed programs, a building block seldom recurs across tasks, and what was learned wasn't the hidden concepts.
- **The strongest finding is the control.** Giving plain learning (C3) **twice the search effort** beat every learner we've built: +4.0 points over C3 [+0.0, +8.2], winning on 7 of 10 papers. At equal effort, *searching more* is still better than *learning differently*.
- **The exam still works.** The oracle (the cheat student) leads by +16.0 points on all 10 papers. The value of good building blocks is real; three discovery methods have now failed to capture it.

### Decision (D-035)

Following the stop rule written in advance (D-024): **the near-miss line of research is closed.** EXP-002 and EXP-002b both closed less than 10% of the gap. Research effort moves to **EXP-005**, building blocks from real engineering records, which gets its own pre-registration. No further near-miss variants will be tried.

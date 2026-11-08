# EXP-005 design: building blocks learned from real code history (pre-registration)

**Status:** pre-registered on 9 November 2026. Committed **before** any EXP-005 code was written or run.
**Why now:** three ways of *discovering* building blocks in the toy puzzle world failed:
- EXP-001, learning from solved puzzles;
- EXP-002, learning from near misses with close answers;
- EXP-002b, learning from near misses one step from an exact answer.

Meanwhile the "cheat student" proved good building blocks are worth +16 points. EXP-002b's control showed that, at equal effort, more search beat every learner. **The next step must bring new information, not a cleverer reuse of the same search** (D-035). Real code written by real people is that new information.
**Words:** see the [Glossary](../GLOSSARY.md).

---

## 1. The question, in plain words

Do programmers keep reusing the same *shapes* of code within a project, such as "check the argument, then raise an error", or "loop over items, collect the ones that match"? If they do, **a library of building blocks learned from a project's past should describe its future code more compactly** than building blocks chosen at random, or learned from other projects.

> **Picture.** Read a writer's first five books and write down their favourite phrases. If those phrases also fill their sixth book, you've learned something real about *that writer*. If they only fill it as well as phrases from other writers do, you've only learned the English language.

This tests the founding research idea (D-003) on real data: building blocks are valuable **when the problems contain hidden repeating patterns**. Here, "problems" are the functions a project's programmers will write next.

**What this experiment can't show.** It measures *description length* (compression), not whether the blocks help a computer *write* code. If the blocks turn out to be real, using them in a code-search setting is a separate, later experiment.

## 2. Data: which code, and why (fixed before running)

**Projects.** These are the REAL-001 projects, cloned at their pinned commits (`product/verify/realworld/projects.json`): click (BSD-3-Clause), more-itertools (MIT), boltons (BSD-3-Clause) and tomli (MIT).
- We only **read** their code through git. Nothing is installed or run, and no model is trained on it.
- We publish only counts, and at most the 10 most useful building blocks per project in their normalised shape: short structural patterns, not code passages.

**Code included.** Every function and method (`def` and `async def`, at any depth) in `.py` files. Excluded: tests (files under a `test/` or `tests/` folder, or named `test_*.py`), and files under `docs/`, `benchmark*/` and `scripts/`.

**Past and future (a temporal split, fixed by rule).** For each project, walk the main-branch history back from the pinned commit, 10 commits at a time. The **split** is the first point with at least **50 functions** (identified by file path and qualified name) that exist at the pinned commit but not at the split.
- **Training ("past")** = all included functions at the split.
- **Test ("future")** = the functions added after it.

| Project | Split commit | Date | Training functions | Test functions |
|---|---|---|---|---|
| click | `8c1a0a7abb` | 2026-07-09 | 558 | 55 |
| more-itertools | `51c42ff83f` | 2024-12-21 | 235 | 50 |
| boltons | `6cac49ce4e` | 2023-11-02 | 886 | 61 |
| tomli | — | never reaches 50 | — | — → **excluded from evaluation; used for calibration** |

These counts were measured before registration. They describe data size only; nothing about compression was computed.

## 3. Method (for specialists)

**Normalisation.** Each function's syntax tree (Python's `ast`) is normalised:
- the docstring is removed;
- argument and local variable names become `v0, v1, …`, in order of first appearance;
- attribute names, called global names and keywords are kept, because they carry the API's meaning;
- string constants become `STR`; numbers other than −1, 0, 1 and 2 become `NUM`.

**Size** is the number of nodes in the tree, not counting load/store context markers.

**Candidate building blocks.** For every statement and expression subtree of size 4 to 40, two forms are candidates:
- the normalised subtree itself;
- versions with **one or two** of its direct child expressions replaced by holes.

A candidate counts only if it occurs at least twice in the corpus, with non-overlapping matches.

**Learning (greedy MDL, the same principle as EXP-001's shortening).** Pick the candidate with the largest **gain** = occurrences × (size − 1) − size. Each use replaces the pattern by one node, and the library pays the pattern's size once. Mark its occurrences as used, recount the remaining candidates on the unused parts, and repeat until **K = 50** blocks are chosen.

**Rewriting test code.** Apply the library's blocks in order, top-down, without overlaps. Each match of a pattern of size s saves s − 1 nodes.

**Compression** for a project = 1 − (total size of the test functions after rewriting) / (total size before).

**Conditions (each library has exactly K = 50 blocks):**

| Condition | Library learned from | What it controls for |
|---|---|---|
| NONE | nothing | the zero point (compression 0) |
| **OWN** | this project's **past** (training functions) | the method |
| RANDOM | 50 candidates drawn uniformly at random (seed 0) from OWN's candidate pool, all occurring at least twice | "any recurring fragments would do" |
| OTHER | the **past** of the other two evaluation projects, pooled | "it's just general Python habits" |
| ORACLE | this project's **future** (the test functions themselves) | the best a K = 50 library could do: an upper bound, not a fair condition |

## 4. Hypotheses, success and failure criteria

Each project's compression gets a 95% bootstrap range, from 10,000 resamples of its test functions with seed 0. "Pooled" means the average over the three projects, with each project's functions resampled within that project.

| ID | Prediction | Success | Failure |
|---|---|---|---|
| **H13 (primary)** | The past teaches real building blocks: OWN beats RANDOM | pooled OWN − RANDOM ≥ +3 points of compression, range excluding 0, **and** positive in all 3 projects | the pooled range includes 0 |
| **H14** | The blocks are partly **project-specific** (D-003's "hidden patterns") | pooled OWN − OTHER > 0, range excluding 0 | the range includes 0: what's learned is mostly general Python |
| **H15** | The past captures much of what's learnable | gap closed = (OWN − NONE) / (ORACLE − NONE) ≥ 30%, pooled | < 10% |

**My honest prior (🔮).**
- OWN compresses future code by about 8–15% and RANDOM by 1–3%, so H13 passes.
- H14 is the real uncertainty: much of what repeats in Python is general (`self.v0 = v0`, `if v0 is None: return`), so OWN − OTHER may be small, +0 to +3 points.
- H15 at 30–50%.

**How the outcomes will be read:**
- **H13 passes and H14 passes:** real projects have their own learnable building blocks, and the research continues on real code (using blocks in search: EXP-006).
- **H13 passes and H14 fails:** the learnable value is general Python habits, so the "hidden patterns" are a language-level, not project-level, phenomenon.
- **H13 fails:** past code doesn't predict future code better than chance fragments. That's a serious negative for the idea on real code, and it's written up as such.

## 5. Calibration rules (no tuning on the exam)

1. Code is built and debugged on **tomli only**. It's excluded from evaluation by the rule above. Its calibration split is the first point with at least **15** new functions.
2. After the first calibration run, at most **two** things may change, each recorded in the decision log:
   - K (25, 50 or 100);
   - the maximum pattern size (40 or 80).
3. Then the design is **frozen** (a decision-log entry). Only after that are click, more-itertools and boltons analysed, **once**.
4. The analysis script and its output are committed. A self-check requires the published output to reproduce exactly, as for every experiment (`research/pevo/tests/test_experiments.py`).

## 6. Cost

Seconds to minutes on the MacBook, ₹0. Only git and Python's built-in `ast` module.

---

## 7. Results (evaluation projects, run once after the freeze in D-036)

Source: `experiments/EXP-005/results/` and `experiments/EXP-005/hypothesis_tests.txt`. Reproduce with `python3 experiments/EXP-005/analysis.py`; a self-check requires that output to match exactly.

### Compression of each project's *future* code (higher = described more compactly)

| Project | Past / new functions | OWN | RANDOM | OTHER | ORACLE |
|---|---|---|---|---|---|
| click | 597 / 55 | **13.9%** | 0.9% | 9.4% | 22.0% |
| more-itertools | 235 / 50 | **13.5%** | 3.6% | 14.4% | 24.3% |
| boltons | 886 / 61 | **13.0%** | 1.2% | 10.8% | 21.4% |
| **Average** | | **13.5%** | 1.9% | 11.5% | 22.5% |

### Pre-registered tests

| | Result | Verdict |
|---|---|---|
| **H13** OWN − RANDOM (primary) | **+11.5 points** [+10.3, +12.6]; positive in all 3 projects | ✅ **PASS** |
| **H14** OWN − OTHER | **+1.9 points** [+1.0, +2.9] | ✅ PASS, but small, and reversed in more-itertools (13.5% vs 14.4%) |
| **H15** share of the best possible (OWN / ORACLE) | **59.7%** [53.8, 65.7] | ✅ PASS |

My prior (OWN 8–15%, RANDOM 1–3%, OWN − OTHER 0 to +3, gap 30–50%) was right on the first three and too pessimistic on the gap.

### What this does and doesn't mean

- **It means:** a project's past code contains building blocks that describe its future code far better than chance fragments: 13.5% vs 1.9% shorter. It's the first discovery method in this project that captures most of the available value (60% of what a library learned on the answers themselves could do). Prospective, history-based learning works on real code where it failed in the toy world.
- **Most of the value is general Python, not project-specific.** Blocks learned from *other* projects get 11.5% of the 13.5%. Only about 2 points are specific to the project, and none in more-itertools. The most-used blocks are small common idioms: `HOLE is None`, `HOLE | None`, `if HOLE: raise ValueError(STR)`, `'STR' % HOLE`. That's the outcome the design called "H13 and H14 pass": real, but read honestly, the hidden patterns are **mostly language-level, with a small project-level layer**.
- **It doesn't mean** these blocks help a computer *write* code. Compression measures description length. Each block saves only 1–4 nodes per use, and whether such small blocks speed up search is exactly what EXP-006 would have to test.
- **Limits:**
  - three small, well-maintained libraries;
  - 50–61 new functions each;
  - the RANDOM control draws uniformly from all recurring candidates, many of them large and rare, so it's a weak bar. OTHER is the stronger control, and OWN beats it only narrowly.

### Decision (D-037)

Following the reading registered in section 4, research continues on real code. The next step, **EXP-006**, gets its own pre-registration first. It asks whether a library learned from the past makes **search** for future code cheaper, not just description shorter, with the same compute-matched controls as EXP-002b. The narrow project-specific margin (H14) means EXP-006 must include an OTHER-library condition again.

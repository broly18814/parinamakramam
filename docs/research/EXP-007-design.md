# EXP-007 design: do building blocks help only when the search is guided? (pre-registration draft)

**Plan v2, Track B** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 4; D-049).
**Status:** design draft, 12 November 2026; frozen 14 November (D-057); **run once on 14–15 November, results in section 9 (D-058).** Committed **before any code** for it is written. It's frozen, like EXP-006, only after calibration on tomli, by the rules in section 6. The evaluation projects are searched once, after the freeze.
**Name:** this reuses the number EXP-007. The earlier EXP-007 (a test-checked search) was closed unrun by D-044. This is a different experiment.

## 1. The question

### In plain words

EXP-006 found that the project's phrase book (building blocks learned from its past) helped the guesser find hidden code, but **no more than letting it guess twice as long**. Sharper habits (looking one level further up the code) helped more. Recent research says the same in other settings: learned building blocks are rarely used well unless the guesser is *guided*, ideally by something that understands the surrounding code, such as a language model.

So EXP-007 crosses the two. It tries **three phrase books** (none, learned, learned plus names and descriptions) with **three guessers**:
- the plain one;
- the sharper-habits one from EXP-006;
- one whose habits are copied from a small language model running on this Mac, which reads the code around the hidden piece.

If the phrase book only helps when the guesser is good, that shows up as a phrase-book gain that grows with the guesser's quality.

### In engineering terms

- **Design:** a 3 × 3 factorial, library × guidance, on exact-match infilling of masked AST fragments. This is EXP-006's task, search and effort measure, unchanged.
- **Primary quantity:** the interaction, that is, the library gain under LLM-distilled guidance minus the library gain under the flat grammar.
- **Guidance level G3** follows HySynth (NeurIPS 2024): sample candidate completions from an LLM conditioned on the task's context, then fit a task-specific probabilistic grammar to those samples. That grammar weights the same A* search.

## 2. What is known, and what isn't

- **Known (our results):**
  - EXP-005: blocks compress future code (+13.5%; replicated as R13, +11.4 points).
  - EXP-006 (D-044): blocks gain +4.1 points in search, but doubling the search gains the same (H17 failed), and CTX2 beats blocks by 4.4 points (H19 failed).
- **Known (literature, R002):**
  - LILO: abstractions were useful to an LLM only after they got names and docstrings.
  - SkillsBench: self-generated skills don't help, while curated, focused ones do.
  - HySynth: LLM-to-grammar distillation beats unguided search and direct sampling on its domains.
- **Unknown:** whether any of this holds for real Python code, where library and guidance are varied *together* at equal search effort. R002 found no published test of this.

## 3. Data (fixed before running)

- **Calibration:** tomli, with humanize as its other project, exactly as in EXP-005 and EXP-006.
- **Evaluation:** **rich** and **pyparsing**. Neither has been used by any experiment so far.
- **The split, and why it differs from EXP-006.** A language model may have *read* these projects during its training, so it could recall the future code instead of predicting it. The split point for each evaluation project is therefore the **release date of the chosen model** (section 4.3):
  - **past** = the code at the last commit before that date;
  - **future** = the functions added after it.
- **Minimum size:** if a project has fewer than 40 new functions after the split, a replacement is drawn by EXP-006's written project rule. That rule is applied at calibration, and the replacement is named in the freeze entry.
- **Contamination check** (reported, not tested): the LLM's direct exact-match rate on 100 tasks from *before* the split against tasks after it. A large gap means memorisation, and is reported next to the results.

## 4. Method

### 4.1 Library factor L

| Code | Phrase book |
|---|---|
| `L0` NONE | none |
| `L1` OWN | K = 50 blocks learned from the project's past by EXP-005's `learn` (K and pattern size frozen in D-036) |
| `L2` NAMED | the same 50 blocks, each given a deterministic name and a one-line description generated from its pattern. Example: `self_append(x)`, "calls `self.<attr>.append` with one argument". |

**Honest note:** a name can only matter to a reader of names. Under G1 and G2 the grammar never sees names, so `L2` is identical to `L1` there by construction. **The factorial has 7 distinct cells, not 9.** `L2` differs only under G3, where the blocks are shown to the LLM as named helper functions in its prompt (LILO's AutoDoc idea).

### 4.2 Guidance factor G

| Code | Guesser |
|---|---|
| `G1` FLAT | EXP-006's one-level grammar (parent type, field) |
| `G2` CTX2 | EXP-006's two-level grammar (EXP-006's best condition) |
| `G3` LLM | per task, *k* = 16 completions sampled from a local LLM (section 4.3), given the future function with the hidden piece replaced by a placeholder. Under `L1`/`L2` the prompt also lists the library. Samples are parsed with `ast`, and unparseable ones are dropped. The task grammar is a mixture: λ × the grammar fitted to the samples' rules (rewritten with the library where one is present) + (1 − λ) × `G2`, with λ fixed at calibration |

Search, effort, budget and solved are exactly EXP-006's: A\* over partial trees, effort = states built, a solve is an exact `shape()` match, and the primary budget **B = 5,000** is frozen in D-043.

### 4.3 The model

The model is chosen at calibration by a written rule. Take the **largest** model from the list below that:
- has a licence allowing commercial use, read on its own page on the day it's chosen;
- runs in MLX on this Mac;
- samples all tomli calibration tasks in **2 hours or less**.

The candidates, in order of preference:
1. Qwen3.6-35B-A3B (Apache-2.0, per R002);
2. a 7–8B coding model;
3. a 3B coding model.

Decoding: temperature 0.8, top-p 0.95, at most 64 new tokens, seed fixed. No model is fine-tuned.

### 4.4 Controls

- **LLM-direct:** count a task solved if any of the *k* samples matches exactly (any-of-16), and separately if the most likely one does (top-1). This is the simpler-system control: is the search adding anything over just sampling?
- **Double search:** `L0` at 2 × B, for each guidance level (EXP-006's H17 control).
- **Cost reported, not traded:** LLM sampling time is reported per task. It isn't converted into states.

### 4.5 Statistics

Statistics are EXP-006's:
- solve rate at B, in points out of 100;
- pooled as the plain average of the projects;
- ranges are 95% cluster-bootstrap intervals (10,000 resamples, seed 0, resampling future functions).

Also reported: the share of tasks buildable at all, per guidance level. G3 can create names the past never had, so this can rise.

## 5. Predictions

All differences are pooled at B.

| ID | Prediction | Success | Failure |
|---|---|---|---|
| **H23 (primary)** | The library gain grows with guidance | (`L1`−`L0` under G3) − (`L1`−`L0` under G1) > 0, range excluding 0, **and** `L1`−`L0` under G3 ≥ +3 points | range includes 0 |
| **H24** | LLM guidance beats sharper habits | `L0`·G3 − `L0`·G2 > 0, range excluding 0 | range includes 0 or below |
| **H25 (simpler system)** | Search adds to sampling | best G3 cell − LLM-direct any-of-16 > 0, range excluding 0 | range includes 0 or below |
| **H26** | Names help the LLM use blocks | `L2`·G3 − `L1`·G3 > 0, range excluding 0 | range includes 0 |
| **H27 (compute control)** | Under G3, the library beats doubling the search | `L1`·G3 at B − `L0`·G3 at 2 × B > 0, range excluding 0 | range includes 0 or below |

### My honest prior, written before any code

- **H23:** about 35%. EXP-006's library gain was small, and an LLM that reads the surrounding code may make blocks less needed, not more.
- **H24:** about 70%.
- **H25:** about 50%.
- **H26:** about 30%.
- **H27:** about 25%.
- **G3's solve rates:** wide uncertainty, because the model sees context neither grammar sees.

### How the outcomes will be read (stop rule)

- **H23 and H27 pass:** blocks are worth their machinery when guided. EXP-008 (a verified, pruned skill library for a local coding agent, SkillsBench-style) gets designed.
- **H23 fails, and `L1`−`L0` isn't positive under any guidance level:** the library line pauses. Research moves to guidance and to own models (Track C).
- **H24 passes but H25 fails:** the LLM's samples alone are as good as search with them. The simpler system wins, and the result is reported that way.

## 6. Calibration rules (no tuning on the exam)

1. Build and debug on **tomli only** (humanize as its other project).
2. Fixed at calibration, each by a rule and recorded in the decision log:
   - **the model**, by section 4.3;
   - **λ**, from {0.5, 0.9}: the value giving the higher `L0`·G3 solve rate on tomli;
   - **the split point and any replacement project**, by section 3.
3. Nothing else is tuned: not B, K, *k*, the decoding settings or the grammars.
4. Then freeze, by a decision-log entry, and commit the analysis script. Only then are rich and pyparsing run, **once**.
5. A self-check requires the published output to reproduce exactly from the saved results.

## 7. Cost (estimate)

- **Money:** ₹0.
- **Search:** under 7 cells × about 800 tasks, at B_max = 25,000 states: minutes, as in EXP-006.
- **Sampling:** about 800 tasks × 3 prompts (none, learned, named) × 16 samples × at most 64 tokens, about 2.5 million generated tokens plus prompt reading. On the M4 Pro that's an estimated 10 to 30 hours, run overnight. Calibration measures it first; if it exceeds 30 hours, *k* drops to 8 by rule, before the freeze.

## 8. Limits known in advance

- **Two evaluation projects, Python only, exact match, fragments of 4 to 12 nodes.** These are EXP-006's limits.
- **G3 sees more than G1 and G2:** it reads the whole surrounding function. That's what guidance means here, but G3's absolute gains mix *better habits* with *more information*. H23 compares library gains *within* each guidance level, which this doesn't bias.
- **Memorisation** is reduced by the date split, but not ruled out; the contamination check reports it.
- **One model, one prompt, no fine-tuning.** A failure doesn't show that no LLM guidance helps.

---

## Amendment 1: replacement evaluation projects (14 November 2026, before any candidate is downloaded)

**What happened.** Applying section 3's split to the chosen model (Qwen3.6-35B-A3B, released **15 April 2026**):
- **rich:** the last commit before the date is `46cebbb032` (12 April 2026), and **0** functions were added after it;
- **pyparsing:** the split is `0f46383d06` (9 April 2026), with **10** added after it.

Both are below the minimum of 40, so each needs a replacement. Section 3 points to EXP-006's written project rule, but **EXP-006's ordered list is used up**: packaging, urllib3 and httpx are EXP-006's own projects, attrs was excluded for size, and rich and pyparsing fail here. Only function counts were read from rich and pyparsing; no search was run on them.

**The rule, fixed before any candidate below is downloaded or measured.** Go down this ordered list, and take the **first two** projects that meet all of these:
- a permissive licence (MIT, BSD or Apache-2.0), checked in the project's own licence file;
- **section 3's split** (the last first-parent commit before 15 April 2026) leaves at least **40** functions added by the pin, the tip of the main branch on the day it's downloaded;
- at least **200** and at most **3,000** functions in the past. The upper limit is new. It's a cost limit, not a quality judgement: G3 recomputes the grammar's completion bounds for every task, and that cost grows with the size of the past.

**The ordered list:**
1. starlette
2. fastapi
3. typer
4. black
5. hatch
6. werkzeug
7. jinja
8. flask
9. poetry
10. textual

All are widely used Python libraries or tools with permissive licences, from several maintainers. **None** has been used by any earlier experiment or by any pkv study.

**Why this keeps the test fair.** The list and the rule are committed before any candidate's history is read. Only function counts and licence files are used to choose, never any search, compression or model result. The candidates are chosen for activity, because the date split needs new code written after the model was trained.

**Honest note:** the order reflects my expectation of which projects are active and mostly pure Python. That's a judgement made before measuring, not a measurement.

## Amendment 2: leave out documentation examples and copied code (14 November 2026, before any search or model result on an evaluation project)

**What happened.** Applying amendment 1 mechanically chose **fastapi** and **typer**, but their "new functions" aren't the new library code the design means to test:
- **fastapi:** 658 of its 818 functions added after the split are documentation examples (`docs_src/`).
- **typer:** 359 of its 757 are documentation examples, and **269** are a copy of Click (`typer/_click/`, "Code taken and adapted from Click", with Click's own licence file). That code wasn't written after the split. Click is also a project the model has surely read, so it could recall the code instead of predicting it, which is exactly what section 3's date split exists to prevent.

EXP-005's inclusion rule leaves out a top folder named exactly `docs`, but not `docs_src`, and it has no rule for copied code.

**The rule, for EXP-007 only.** EXP-005's rules apply, plus two:
1. **Documentation examples are left out:** any file whose top folder starts with `docs` (for example `docs_src`), or is `examples` or `example`.
2. **Copied third-party code is left out:** any file inside a folder, other than the repository's top, that holds its own licence file (`LICENSE*`, `LICENCE*` or `COPYING*`), or inside a folder named `_vendor`, `vendor`, `vendored`, `_vendored` or `third_party`.

These apply to the past and the future alike, at both the split and the pin. **Amendment 1's list is then applied again from the top**, with the same thresholds.

**Why this is a correction, not tuning.** It was prompted only by function counts and file paths, never by any search, compression or model result. The rule is general (it names no project), and it applies equally to the calibration project. The calibration run is checked under it: if tomli changes, the calibration is repeated.

---

## 9. Results (evaluation projects, run once after the freeze in D-057)

Run on 14–15 November 2026 from the frozen code `02e2a34`; every result file records the commit. Sampling took 3.4 h for fastapi (1,006 tasks) and 2.0 h for black (642 tasks), about 12 s per task for all three prompts. The searches took about 4 minutes (19 minutes of processor time, spread across the cores). Source: `experiments/EXP-007/results/` (the model's guesses and every search's effort) and `experiments/EXP-007/hypothesis_tests.txt`. Reproduce with `python3 experiments/EXP-007/analysis.py`; a self-check requires that output to match exactly, and the guesses are saved, so it never needs the model again.

### In plain words first

- **The model's guidance is a big step.** When a language model running on this Mac reads the code around the hidden piece and makes 16 guesses, and the search leans towards those guesses, the search found **53 of 100** hidden pieces within 5,000 tries. The best guesser without the model (EXP-006's sharper habits) found **23**.
- **The search adds to the model's own guesses.** The model's 16 guesses alone contained the exact answer **41** times in 100. Its single likeliest guess was right about **26** times.
- **The phrase book adds nothing once the model guides.** With the learned blocks, the guided search found 53.0, against 53.3 without them. Naming the blocks for the model didn't help either (52.5).
- **Guessing twice as long still beats the phrase book:** 54.6.
- So learned building blocks helped only the weakest guesser, and the better the guesser, the less they mattered. That's the opposite of what H23 predicted.

### Found, out of 100 hidden pieces, within 5,000 tries

| Cell | fastapi | black | **Average** |
|---|---|---|---|
| L0·G1, no blocks, plain habits | 9.4 | 21.7 | 15.5 |
| L1·G1, blocks, plain habits | 13.5 | 25.5 | 19.5 |
| L0·G2, no blocks, sharper habits | 14.1 | 31.0 | 22.6 |
| L1·G2, blocks, sharper habits | 16.2 | 31.2 | 23.7 |
| **L0·G3, no blocks, model-guided** | 47.2 | 59.3 | **53.3** |
| L1·G3, blocks, model-guided | 48.7 | 57.3 | 53.0 |
| L2·G3, named blocks, model-guided | 47.6 | 57.3 | 52.5 |
| L0·G3 with 10,000 tries | 48.2 | 61.1 | 54.6 |
| The model alone, any of 16 (L0 prompt) | 38.9 | 43.9 | 41.4 |
| The model alone, any of 16 (L1 prompt) | 41.2 | 41.0 | 41.1 |
| The model alone, any of 16 (L2 prompt) | 40.2 | 39.7 | 39.9 |

### Pre-registered tests

| | Result (points, [95% range]) | Verdict | My prior |
|---|---|---|---|
| **H23** the library gain grows with guidance (primary) | **−4.3** [−6.3, −2.3]; the library gain under G3 is −0.3 [−2.1, +1.5], against the +3 required | ❌ FAIL: the gain *shrinks* with guidance | 35% |
| **H24** the model's guidance beats sharper habits | **+30.7** [+27.5, +34.0] | ✅ PASS | 70% |
| **H25** the search adds to the model's own guesses | **+11.9** [+10.0, +13.8] (best G3 cell: L0·G3) | ✅ PASS | 50% |
| **H26** names help the model use blocks | −0.5 [−2.0, +0.9] | ❌ FAIL | 30% |
| **H27** under guidance, the library beats doubling the search | −1.6 [−3.4, +0.1] | ❌ FAIL | 25% |

### Reported, not tested (design 4.4, 4.5; `experiments/EXP-007/supplement.txt`, written after the run)

- **The library gain at each guidance level:**
  - G1: **+4.0** [+2.8, +5.3];
  - G2: +1.1 [+0.3, +1.9];
  - G3: −0.3 [−2.1, +1.5].

  Against doubling the search, it's +1.1 [0.0, +2.2] at G1, −1.8 [−2.9, −0.8] at G2, and −1.6 [−3.4, +0.1] at G3. Only at the plainest level does the library match double the search.
- **Buildable from the past's rules:** 53.2% of fastapi's tasks and 86.0% of black's. A model guess can bring in rules the past never had: L0·G3 found 13.0% of fastapi's tasks (3.7% of black's) that no other condition could build at all. This is part of G3's gain.
- **The model alone, top-1:** fastapi 25.0, black 26.0 (L0 prompt).
- **Contamination check:** see below.

### What this means, honestly

- **Search and the model's guesses aren't compared at equal checking.** A search "finds" a piece by checking up to 5,000 candidates against the exact answer. The model alone gets 16 checks. The design reports this cost and doesn't trade it (4.4), so H25 means: *with a checker that recognises the right answer*, searching around the model's guesses beats keeping only its guesses. In a coding tool that checker would be the project's tests, and running tests 5,000 times costs far more than running them 16 times.
- **G3 also sees more** (the whole surrounding function), as section 8 says. H24's size mixes better habits with more information. H23 compares library gains *within* a guidance level, so this doesn't bias it.
- **Calibration and evaluation differ a lot:** L0·G3 found 79.2 in tomli but 53.3 here. tomli is smaller and more regular, and its calibration numbers were never evidence.
- **Two projects, one model, one prompt, Python only, exact match.** These are section 8's limits.

### How the stop rule reads

None of the three written branches matches exactly:
- **Branch 1 (H23 and H27 pass): no.**
- **Branch 3 (H24 passes, H25 fails): no.** H25 passed.
- **Branch 2: half.** H23 fails, but its second condition, "`L1`−`L0` isn't positive under any guidance level", isn't met: the gain is +4.0 under G1 and +1.1 under G2, with ranges above 0.

The rule didn't foresee a library that helps weak guessers a little and strong guessers not at all. The closest reading, and the one recorded (D-058), is branch 2's consequence:
- **the library line pauses;**
- **EXP-008 isn't designed;**
- **research moves to guidance and to own models (Track C).**

That's a judgement, not the rule's mechanical output, and it's recorded as one.

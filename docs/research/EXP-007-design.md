# EXP-007 design: do building blocks help only when the search is guided? (pre-registration draft)

**Plan v2, Track B** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 4; D-049).
**Status:** design draft, 12 November 2026. Committed **before any code** for it is written. It's frozen, like EXP-006, only after calibration on tomli, by the rules in section 6. The evaluation projects are searched once, after the freeze.
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

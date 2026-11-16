# EXP-M1 design: which tokenizer should the project's own small models use? (pre-registration draft)

**Plan v2, Track C, step C3** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 5; D-049, D-050, D-059).
**Status:** design draft, 16 November 2026. Committed **before any code** for it is written and before any data is downloaded. It's frozen only after calibration on the validation split, by the rules in section 6; the test split is scored once, after the freeze.
**Scope:** English text and Python code only (D-059).
**Words:** see the [Glossary](../GLOSSARY.md). Each section gives the plain version first and the engineering version second.

---

## 1. The question

### In plain words

A language model doesn't read letters. It reads **tokens**: pieces of text from a fixed list, its *vocabulary*. A **tokenizer** is the word-splitter that cuts text into those pieces. The choice matters more for small models than for big ones:
- **A bigger vocabulary** cuts text into fewer, longer pieces, so the model reads more text per step. But its last layer has to choose among more pieces every time, and that costs computing.
- **In our smallest model,** with the usual vocabulary of about 32,000 pieces, that last choosing step takes **two-thirds of all the computing**. The model's actual "thinking" layers get only a third.

So EXP-M1 asks: **for the small models this Mac can train, which tokenizer makes the model best at predicting English and Python, when every option gets exactly the same training time?** It also asks whether a tokenizer that splits code the way programmers write it (indentation kept whole, numbers split into digits) does better on Python.

It also builds what every later model experiment needs:
- the cleaned, licence-checked training data;
- the chosen tokenizer;
- the yardstick model that the new designs in [A001](A001-evolving-architecture.md) must beat.

### In engineering terms

- **Design:** 9 tokenizer arms. Each trains the same GPT-style model, from scratch, for the same wall-clock time on this Mac, with 3 seeds, at the 10M size. The baseline and the two best arms are then confirmed at the 25M size.
- **Metric:** bits per byte (BPB) on held-out English and held-out Python, which is tokenizer-independent. Per-token loss can't compare vocabularies; BPB can.
- **Compute share of the output layer** (by C1's cost formula, 6·N plus attention, context 1,024):

| Vocabulary | 10M core: total parameters | 10M: output layer's share of training compute | 25M core: output share |
|---|---|---|---|
| 256 (bytes) | 3.5M | 2% | 1% |
| 4,096 | 4.5M | 20% | 11% |
| 8,192 | 5.5M | 33% | 20% |
| 16,384 | 7.6M | 50% | 33% |
| 32,768 | 11.8M | 67% | 49% |
| 50,257 (GPT-2) | 16.3M | 75% | 60% |
| 65,536 | 20.2M | 80% | 66% |

"10M" and "25M" name C1's model *cores*: d_model 256 with 4 layers, and 384 with 6. The embedding grows with the vocabulary.

## 2. What is known, and what isn't

- **Known (literature, *[not re-fetched]*, checked against the papers before results are published):**
  - Tao et al. 2024, *Scaling Laws with Vocabulary*: the compute-optimal vocabulary grows with model size, and small models prefer small vocabularies.
  - DataDecide (Magnusson et al., ICML 2025, in R002): rankings measured at small scale pick the better option at larger scale about 80% of the time.
  - Splitting numbers into single digits is common practice (Llama, among others).
- **Known (our measurements):** C1's speeds at vocabulary 32,768, on random tokens, and that bfloat16 is 1.4 times as fast as float32 at these sizes.
- **Unknown:**
  - where the optimum lies, *in wall-clock time on Apple's GPU* (not in FLOPs), for a 50/50 English and Python mix;
  - whether code-aware splitting helps Python without hurting English;
  - whether the 10M ranking survives at 25M on this setup.
- **Honest note:** H29's direction (smaller is better at 10M) is what the vocabulary scaling law predicts. The new parts are the code-aware arm, the English and Python mix, wall-clock compute on this Mac, and the transfer test.

## 3. Data (fixed before running)

### In plain words

Half English, half Python, by bytes. Only sources whose licences let a business use the trained model. The test text is held back by **project** (for code) and by **document** (for English), so the model is never tested on text it trained on.

### In engineering terms

- **English:** FineWeb-Edu, the `sample/10BT` shards (ODC-By, not gated, commit `87f09149ef47` on 16 Nov 2026).
- **Python:** The Stack v1 dedup, the `data/python` shards, restricted to files licensed MIT, BSD, Apache-2.0, ISC, Unlicense or CC0, keeping each file's repository and licence for attribution. Its terms are accepted on Hugging Face (gated "auto", commit `17cad72c886a`).
  - **That acceptance is a founder step** (dataset registry rule 6).
  - **If the founder declines,** the fallback is GitHub-code-clean's Python rows with the same licences (Apache-2.0 packaging, not gated, commit `c48d40f9e70f`). It would be recorded as an amendment before any download.
- **Splits:**
  - **Code:** by repository. `sha256(repo name)` mod 100 = 0–1 is **test**, 2–3 is **validation**, and the rest is training.
  - **English:** the same rule on each document's `id`.
  - A repository is never in two splits.
- **Sizes:**
  - test: 10 MB of English and 10 MB of Python;
  - validation: 5 MB each, used only for calibration;
  - training pool: sized at calibration to 1.2 × the most bytes any arm can read in its time budget (estimated 4–5 GB). **No training document is read twice.**
- **Cleaning** (dataset registry quality rules):
  - exact-duplicate removal across the pool, by a normalised content hash;
  - removal of any training document whose hash matches a test or validation document;
  - a language check on the English side, which reports and drops non-English documents.

  The counts are reported.
- **Reported, not tested: "future code".**
  - **What:** the Python files of fastapi and black that changed or were added after 15 April 2026 (the EXP-007 split, with its amendment-2 exclusions; both MIT).
  - **Why:** The Stack v1 is from 2022, so this is genuinely newer code.
  - **Use:** never trained on.
- **Where:** every download goes to `/Volumes/projects/hope/work/m1`, outside the repository and outside the home folder. A manifest records each file's SHA-256 (registry rule 2).

## 4. Method

### 4.1 The tokenizer arms

All of our own arms are byte-level BPE (Hugging Face `tokenizers` 0.23, Apache-2.0). They're trained on the same fixed 200 MB sample of the training pool (50/50 by bytes), drawn with seed 0, and every vocabulary includes one end-of-document token.

| Arm | Vocabulary | Pre-splitting | Role |
|---|---|---|---|
| `BYTE` | 257 (bytes + end) | none | the no-tokenizer reference |
| `STD-4k` | 4,096 | GPT-2's pattern | vocabulary ladder |
| `STD-8k` | 8,192 | GPT-2's pattern | vocabulary ladder |
| `STD-16k` | 16,384 | GPT-2's pattern | vocabulary ladder |
| **`BASE` = `STD-32k`** | 32,768 | GPT-2's pattern | **the baseline**: the ordinary choice, and C1's size |
| `STD-64k` | 65,536 | GPT-2's pattern | vocabulary ladder |
| `CODE-8k` | 8,192 | code-aware (below) | code-aware splitting, small |
| `CODE-32k` | 32,768 | code-aware | code-aware splitting, at BASE's size |
| `GPT2-REF` | 50,257 | GPT-2's own, trained on WebText (MIT) | **reported, not tested**: do we need our own tokenizer at all? |

- **GPT-2's pattern:** `'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+`.
- **The code-aware pattern** is GPT-2's with two changes, fixed here:
  1. numbers are split into single digits (`\p{N}`, not ` ?\p{N}+`);
  2. a line break followed by indentation (`\n[ \t]+`) is one piece, so indentation is never merged with the code after it.

### 4.2 The model and training (the same for every arm)

- **Model:** C1's GPT, unchanged:
  - pre-LayerNorm, learned positions, tied input and output embedding, GELU MLP, no biases;
  - context 1,024 tokens, 16 sequences per step;
  - bfloat16 (unless calibration rule 2 says otherwise).

  MLX 0.31.2 (MIT).
- **Optimiser:**
  - AdamW, β = (0.9, 0.95), weight decay 0.1, gradient clipping 1.0;
  - warm-up over 2% of steps, then cosine decay to 10% of the peak learning rate;
  - the peak learning rate is per arm, by calibration rule 3.
- **Data:** documents are joined with the end-of-document token and cut into 1,024-token sequences. **The seed fixes both the starting weights and the document order**, and the document order is the same for every arm with that seed, so the comparisons are paired by seed.
- **Equal compute = equal wall-clock training time on this Mac:** **60 minutes** per run at 10M, **4 hours** at 25M.
  - **How the steps are set:** each arm's speed is measured at calibration, and its number of steps is set so that the expected training time equals the budget. That keeps the learning-rate schedule complete.
  - **What's recorded:** each run's actual time, tokens and bytes read. A run more than 5% off its budget is reported.
  - **Evaluation time** isn't counted.
- **Run order:** a seed-0 shuffle of all (arm, seed) runs, so the laptop's heat (C1: a 6% step down after about 25 minutes of load) can't favour any arm systematically.

### 4.3 The metric

**BPB = (total loss, in bits, over a held-out set) ÷ (that set's UTF-8 bytes).**
- **How it's computed:** each held-out set's documents are joined with the end-of-document token, as in training, and cut into non-overlapping 1,024-token windows. The loss is summed over every token, the end tokens included.
- **Honest note:** a bigger vocabulary sees more bytes per window (more context), and a byte model sees only 1,024 bytes. That's part of what a tokenizer buys, so it isn't corrected for.
- **Pooled BPB** = the mean of English BPB and Python BPB.

### 4.4 Deciding "beats BASE"

With three seeds, differences are paired by seed: d_s = BPB(BASE, s) − BPB(arm, s). An arm **beats BASE** if both hold:
1. **all three** d_s > 0;
2. their mean > the **threshold**, defined as the larger of:
   - 2 × the standard deviation of BASE's three pooled BPBs;
   - 0.005 bits per byte, the smallest difference worth acting on: about 0.5% at these sizes.

The same rule, with the roles named, is used for every comparison below. Points are reported to 3 decimals.

## 5. Predictions

All at the test split; "best" means the lowest pooled mean BPB over the 3 seeds.

| ID | Prediction | Success | Failure |
|---|---|---|---|
| **H28 (primary)** | At 10M, some tokenizer beats BASE | the best arm at 10M (GPT2-REF excluded) beats BASE by 4.4 | it doesn't |
| **H29** | Small models want small vocabularies | the best STD arm at 10M has a vocabulary of 16,384 or less | 32,768 or 65,536 |
| **H30** | Code-aware splitting helps Python | `CODE-32k` beats `STD-32k` on **Python** BPB by 4.4, **and** `STD-32k` doesn't beat `CODE-32k` on **English** BPB by 4.4 | otherwise |
| **H31** | Bytes alone are too slow | `BYTE` has the worst pooled mean BPB of our own arms at 10M | another arm is worse |
| **H32 (transfer)** | The 10M winner still wins at 25M | at 25M, the 10M best arm (if it isn't BASE) beats BASE by 4.4 | it doesn't |
| **H33 (ranking)** | The 10M order holds at 25M | the three confirmed arms have the same order by pooled mean BPB at 25M as at 10M | any other order |

**The three arms confirmed at 25M:**
- BASE;
- the best arm at 10M;
- the second best.

If BASE is itself among the top two at 10M, the next arm down is taken. The choice uses the 10M **test** results, by this rule, before any 25M run.

### My honest prior, written before any code

- **H28:** about 80%. At 10M, BASE spends two-thirds of its compute on the output layer.
- **H29:** about 75%.
- **H30:** about 40%. GPT-2's pattern already groups runs of spaces, so the gain may be small, and digit splitting may cost English nothing or a little.
- **H31:** about 75%. Bytes are cheap per step but slow per byte. `STD-64k` is the other candidate for last.
- **H32:** about 60%. At 25M, BASE's output share falls to about half.
- **H33:** about 45%. Chance is 1 in 6.
- **Absolute BPB:** wide uncertainty, roughly 1.0 to 1.6 at 10M after an hour.

### Reported, not tested

- `GPT2-REF` against BASE, by rule 4.4.
- Every arm's BPB on the future-code set.
- Tokens per byte on each test set (how much each tokenizer compresses).
- Measured tokens and bytes per second.
- FLOPs per byte.

### How the outcomes will be read (stop rule)

- **H28 fails:** no tokenizer beats the ordinary one by more than seed noise. That's reported, **BASE becomes the project's tokenizer, and the tokenizer question stops**: no more tokenizer experiments in plan v2.
- **H28 passes, H32 fails:** the gain doesn't survive 25M. **BASE is used from 25M up**, and the 10M result is reported as a small-scale effect.
- **H28 and H32 pass:** **the winner becomes the project's tokenizer.** Its 25M seed-0 model is the yardstick for EXP-A1 to EXP-A3.
- **In every case,** the data pipeline and the chosen tokenizer's 25M model are kept as the baseline that the A001 experiments must beat.

## 6. Calibration rules (no tuning on the exam)

Calibration uses the **validation** split only. The test split isn't read until the freeze.

1. **Pipeline check.** Build the splits and the cleaning steps, and report their counts: documents, bytes, duplicates removed, decontamination hits and non-English drops. A self-check confirms that no repository and no document hash appears in two splits.
2. **Number format.** Train BASE at 10M for 10 minutes in bfloat16 and in float32. **bfloat16 is used unless** its validation BPB is worse by more than 0.01 bits per byte (C1's open question).
3. **Learning rate, per arm,** from a fixed grid, by the lowest validation pooled BPB:
   - **at 10M:** {1e-3, 2e-3, 4e-3}, 10-minute runs, seed 0;
   - **at 25M:** {5e-4, 1e-3, 2e-3}, 20-minute runs, for the three confirmed arms only.

   A tie goes to the smaller value.
4. **Speed, per arm:** measured during its learning-rate runs. It sets the step count (section 4.2).
5. **Pool size:** set to 1.2 × the most bytes any arm reads in its budget. If the pool is too small, more shards are added in order before the freeze.
6. **Nothing else is tuned:** not the model, the context, the batch, the schedule's shape, the budgets, the seeds, the threshold or the patterns.
7. **Then freeze, by a decision-log entry, and commit the analysis script.** Then the 10M test runs, the rule picking the 25M arms, and the 25M test runs, each **once**.
8. **A self-check** requires the published output to reproduce exactly from the saved per-run results.

## 7. Cost (estimate)

- **Money:** ₹0.
- **Downloads:** about 10 GB, to `/Volumes/projects/hope/work/m1` (881 GB free on 16 Nov).
- **10M:**
  - 9 arms × 3 seeds × 1 hour = **27 hours**;
  - learning-rate calibration: 9 × 3 × 10 minutes, about 4.5 hours.
- **25M:**
  - 3 arms × 3 seeds × 4 hours = **36 hours**;
  - learning-rate calibration: 3 × 3 × 20 minutes = 3 hours.
- **Total:** about **71 hours** of the Mac, run mostly overnight over about a week. Nothing else that trains can share those nights.
- **Founder step:** accept The Stack v1 dedup's terms on Hugging Face (or decline, and the fallback is used).

## 8. Limits known in advance

- **Two sizes, one architecture, one data mix, three seeds.** The claim is a **ranking**, not an absolute number (plan v2: rankings only). DataDecide's roughly 80% is the best available guide to whether it transfers further.
- **Wall-clock compute** favours designs that suit Apple's GPU. That's stated with every result, and FLOPs are reported beside it.
- **The context differs by tokenizer** (section 4.3). That's deliberate, but it means "better BPB" mixes better compression of text with longer reach.
- **The tokenizers are trained on our own mix,** so they're tuned to it. GPT2-REF shows what an off-the-shelf choice gives.
- **BPB isn't usefulness.** No downstream task is tested here. The A001 experiments and any coding evaluation come later, on the model this experiment picks.
- **The Python is from 2022.** The future-code set reports how much that matters, but isn't a test.

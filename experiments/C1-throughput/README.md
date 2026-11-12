# C1: how fast can this Mac train small language models?

**Plan v2, Track C, step C1** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 5). A measurement, not a test of a research idea. It replaces R002's *estimates* with real numbers before any model experiment (EXP-M1) or overnight language run (IND-1) is sized.

**Status:** pre-registered on 12 November 2026. The predictions and rules below are committed **before** the measured run.

## In plain words

We build the same kind of model as GPT-2, at four sizes, and train each one for 2 minutes on random tokens (word-pieces). Speed doesn't depend on what the text says, so random tokens are fine. We count how many tokens a second the Mac gets through. Then we work out how long a full training run would take at each size: the usual rule is 20 tokens of text per number in the model ("Chinchilla"). We also try two number formats: 32-bit, which is exact, and 16-bit `bfloat16`, which is faster and smaller. Finally, the biggest model runs for 10 minutes to see whether the laptop slows down as it heats up.

## In engineering terms

- **Model:** a decoder-only Transformer.
  - Pre-LayerNorm, learned position embeddings, a tied embedding/unembedding.
  - A GELU MLP of width 4d, bias-free Linear layers, 64-dimensional heads.
  - Causal `mx.fast.scaled_dot_product_attention`.
- **Data:** vocabulary 32,768, context 1,024, batch 16, so 16,384 tokens per step. Tokens are uniform random.
- **Optimiser:** AdamW, lr 3e-4, wd 0.1. The train step is compiled (`mx.compile`) and synchronised with `mx.eval` every step.
- **Software:** `mlx==0.31.2`, Python 3.14.
- **Sizes**, all parameters counted (the script checks the count against the formula):

  | Name | d_model | Layers | Parameters |
  |---|---|---|---|
  | 10M | 256 | 4 | 11.8M |
  | 25M | 384 | 6 | 23.6M |
  | 50M | 512 | 10 | 48.8M |
  | 125M | 768 | 14 | 125.1M |

- **Runs:**
  - **run 1:** every size × {float32, bfloat16}, 120 s each, after 3 untimed warm-up steps;
  - **run 2:** 125M in the faster format for 600 s.
- **Reported:** tokens/s is the median over 10-second windows. Also reported:
  - the slowest window;
  - effective TFLOP/s, at 6·N plus attention per token, with N = block weights plus the output layer;
  - peak memory;
  - days to 20 tokens per parameter.
- **Conditions:** MacBook Pro, Apple M4 Pro, 48 GB. The power source is recorded with each result. Nothing else heavy runs at the same time.

## Predictions, written before the run (from R002's estimates)

R002 assumed 3–6 effective TFLOP/s ([notes](../../docs/research/R002-fresh-plan/notes/small_model_training_mac.md), Q1).

| Size | Predicted tokens/s (best format) | Predicted days to 20 tokens/parameter |
|---|---|---|
| 10M | 50,000–100,000 | 0.03–0.05 |
| 25M | 20,000–40,000 | 0.14–0.27 |
| 50M | 10,000–20,000 | 0.6–1.2 |
| 125M | 4,000–8,000 | 3.6–7.2 |

**Disclosure:** two short smoke runs were made before this file was committed, to check the script works:
- **10M:** 12 seconds, about 38,000 tokens/s in float32 and 60,000 in bfloat16;
- **125M:** 11 seconds in bfloat16, about 6,500 tokens/s.

All four predictions are R002's, copied unchanged from its notes, which were written before any measurement. The smoke numbers are not part of the results.

## What the results decide (rules fixed now)

1. **Largest size for EXP-M1:** EXP-M1 needs many runs (several tokenizers × 3 seeds), so its sizes are the ones whose single 20-tokens-per-parameter run takes **24 hours or less** in the faster format.
2. **A 125M model is allowed** in the next 90 days only if one full run takes **7 days or less**, and then at most one such run.
3. **Throttling:** if run 2's slowest 10-second window is below **80%** of its median, the plan sizes every long run with the *slowest* window, not the median.
4. **Number format:** this run decides speed only. Whether bfloat16 *trains as well* as float32 is checked on real text in EXP-M1's calibration, before EXP-M1's own predictions are committed.
5. **If the measured speed is below the low end of a prediction**, the plan's sizes shrink, and IND-1 and EXP-M1 are re-sized before they are pre-registered (plan v2, risk 3).

## Reproduce

```bash
uv run --no-project --python 3.14 --with mlx==0.31.2 python experiments/C1-throughput/bench_throughput.py measure --out experiments/C1-throughput/results/run1.jsonl
```

```bash
uv run --no-project --python 3.14 --with mlx==0.31.2 python experiments/C1-throughput/bench_throughput.py measure --out experiments/C1-throughput/results/run2.jsonl --seconds 600 --sizes 125M --dtypes bfloat16
```

```bash
python3 experiments/C1-throughput/bench_throughput.py summarise experiments/C1-throughput/results/run1.jsonl
```

The committed `results/*.md` tables must equal `summarise` applied to the committed `results/*.jsonl` files, character for character (checked in `research/pevo/tests/test_experiments.py`).

---

## Results (12 November 2026, measured after the predictions above were committed in `8b14f76`)

Conditions: MacBook Pro, Apple M4 Pro, 48 GB, macOS 27.2.1, on AC power, `mlx` 0.31.2, Python 3.14.6. Raw records are in `results/run1.jsonl` and `results/run2.jsonl`; the tables are in `results/run1.md` and `results/run2.md`, made by `summarise`.

### In plain words

**Every size landed inside its predicted range.** The faster number format (bfloat16) is the one to use: it's 1.4 times as fast at the small sizes and about 3 times as fast at 125M. In exact 32-bit numbers, the 125M model needed 39 GB of the 48 GB, and its speed fell and wobbled. A complete 125M training run takes about **4.2 to 4.4 days** of the Mac; a 50M run takes about **17 hours**.

| Size | Tokens/s, bfloat16 (median) | Predicted | Days to 20 tokens/parameter | Predicted days | Within prediction? |
|---|---|---|---|---|---|
| 10M | 61,173 | 50,000–100,000 | 0.04 (about 1 hour) | 0.03–0.05 | ✅ |
| 25M | 32,868 | 20,000–40,000 | 0.17 (about 4 hours) | 0.14–0.27 | ✅ |
| 50M | 16,311 | 10,000–20,000 | 0.69 (about 17 hours) | 0.6–1.2 | ✅ |
| 125M | 6,941 | 4,000–8,000 | 4.17 | 3.6–7.2 | ✅ |

float32, for comparison, in tokens per second (median) and peak memory:

| Size | Tokens/s | Peak memory |
|---|---|---|
| 10M | 42,541 | 10.3 GB |
| 25M | 23,176 | 14.1 GB |
| 50M | 11,794 | 22.4 GB |
| 125M | 2,372 | **39.2 GB**; the speed rose from 1,565 to 2,696 across windows, so likely memory pressure |

**The heat test (run 2, 125M, bfloat16, 10 minutes):**
- **Median:** 6,934 tokens/s.
- **What happened:** steady at about 6,940 for the first 7 minutes, then a single step down to a steady **6,520** (−6%) for the rest. That started about 25 minutes into the whole session's continuous load, which is consistent with the laptop reaching a hotter, lower-power state. This is an inference; temperature wasn't recorded.

### What the rules decide

1. **EXP-M1's sizes: 10M, 25M and 50M.** Each single run takes 24 hours or less (50M: 0.69 days). 125M doesn't (4.2 days).
2. **One 125M run is allowed** in the 90 days: 4.17 days at the median, 4.44 days at the sustained 6,520, both under 7.
3. **No throttling adjustment:** the slowest window is 94% of the median, above the 80% limit. Even so, long runs are sized at the sustained **6,520** tokens/s rather than the median, because that's the speed after the step down (a choice made after seeing the data, stated here).
4. **Number format:** use bfloat16 for speed. Whether it *trains as well* as float32 is checked on real text in EXP-M1's calibration.
5. **Nothing fell below a prediction**, so nothing shrinks.

### Limits

- **Random tokens, one batch size (16 × 1,024), one vocabulary (32,768).** Real data loading and other vocabularies change the speed somewhat; EXP-M1's calibration measures its own.
- **10 minutes isn't days.** A multi-day run may slow further; its speed is logged throughout.
- **Two minutes per size** (one measurement each), so the medians carry no confidence interval. The 10-second windows are very stable (within ±1% for 25M and 50M).

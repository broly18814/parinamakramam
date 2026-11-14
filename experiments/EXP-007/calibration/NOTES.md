# EXP-007 calibration notes (tomli only; no evaluation project has been touched)

Rules: [EXP-007 design](../../../docs/research/EXP-007-design.md), section 6, and the [build spec](../../../docs/research/EXP-007-build-spec.md).

## 14 November 2026: the model, first measurements

**Candidate:** `mlx-community/Qwen3.6-35B-A3B-4bit`, revision `38740b847e4cb78f352aba30aa41c76e08e6eb46`.
- **Licence:** Apache-2.0, read on its own Hugging Face record on 14 November 2026; the base model `Qwen/Qwen3.6-35B-A3B` is also Apache-2.0. Neither is gated.
- **Released:** 15 April 2026.
- **Files:** 17, all checked against Hugging Face's SHA-256.
- **Where it's stored:** `/Volumes/projects/hope/work/mlx`, outside the repository.
- **Runtime:** `mlx-lm` 0.32.2, `mlx` 0.32.4, Python 3.12.

| Measurement | Result |
|---|---|
| Load time | 9.4 s |
| Thinking mode | off (the template's empty `<think>` block); answers are plain code |
| One guess at a time | about 1.5 s per guess (24 s per task of 16) |
| **Batched** (`batch_generate`, 2 tasks × 16 per batch of 32; T 0.8, top-p 0.95, 64 tokens) | **3.0 s per task** on the first 20 tomli tasks |
| Extrapolated: all 260 tomli tasks × 3 prompt types | **about 0.65 h**, against the design's limit of 2 h |
| Readable guesses (build spec S2) | 273 of 320 (85%) |
| At least one of 16 exactly right | 9 of 20 tasks (calibration information, not a result) |

**Not decided yet.** The model is fixed in the decision log only after the full calibration run. That run measures the real time for the longer library prompts too, and chooses λ from {0.5, 0.9} by the design's rule.

## Code checks that passed before calibration (build spec S8)

- **The prompt round-trip:** all 260 of 260 tomli tasks.
- **The two-level grammar with blocks, without blocks:** identical to EXP-006 on 260 of 260 tasks (budget 20,000).
- **The G3 grammar with no guesses:** identical to EXP-006 on 260 of 260 tasks.
- **The G3 grammar with the true piece guessed:** easier on 249 tasks, harder on 0.

## 14 November 2026: the evaluation projects (design amendments 1 and 2)

**The split** is the design's section 3: the last first-parent commit before the model's release (15 April 2026). Only function counts and licence files were read; no search, compression or model result.

| Candidate (amendment 1's order) | Licence | Split (date) | Past | New after the split | Outcome |
|---|---|---|---|---|---|
| rich (the design's first choice) | MIT | `46cebbb032` (2026-04-12) | 895 | 0 | below 40 |
| pyparsing (the design's second) | MIT | `0f46383d06` (2026-04-09) | 1,036 | 10 | below 40 |
| starlette | BSD-3-Clause | `273ac4176e` (2026-04-11) | 481 | 38 | below 40 |
| **fastapi** | MIT | `9653034b8d` (2026-04-13) | 275 | 160 | **evaluation project 1** |
| typer | MIT | `0385c880bf` (2026-04-14) | 166 | 129 | under 200 past functions |
| **black** | MIT | `c7fc2438cb` (2026-04-14) | 442 | 92 | **evaluation project 2** |

These counts are after amendment 2.
- **Without it,** fastapi had 818 new functions (658 of them documentation examples) and typer 757 (359 examples, plus 269 from a copy of Click). That was the reason for the amendment.
- **Under it,** black's copy of `lib2to3` (`src/blib2to3`, 114 functions, with its own licence file) is left out.
- **tomli is unchanged** by amendment 2: 42 functions at the split and 44 at the pin, so the calibration run is unaffected.

**Pins** (the tip of each main branch on 14 November 2026):
- fastapi: `5758a9c8347d911444dca97a55b708cc4a8de4f8`
- black: `b10cbe43b8169e688ab86989ddcc8ad2a53ff2cd`

## 14 November 2026: the full calibration run and the freeze (D-057)

The output is in [`run1/CALIBRATION.txt`](run1/CALIBRATION.txt), made by `calibrate.py` from the saved run, and a self-check reproduces it.
- **The model:** Qwen3.6-35B-A3B. All 260 tasks × 3 prompts were sampled in 0.84 h, against a 2 h limit.
- **λ = 0.5:** L0·G3 solved 79.2 at B, against 76.2 at 0.9.
- **k = 16:** 3.86 s per (task, prompt) × 3 × 1,648 evaluation tasks = 5.3 h, against a 30 h limit.

**For orientation only, not evidence** (one small project, used for building):
- the plain grammar solved 26.5 of 100 at B (EXP-006's NONE solved exactly 26.5 on the same tasks);
- the two-level grammar solved 49.2;
- the model-guided grammars solved 79 to 82;
- the model alone found the exact piece among its 16 guesses on 54 to 60 tasks in 100.

The analysis script was dry-run on these calibration numbers, which aren't evidence, to check that it works.

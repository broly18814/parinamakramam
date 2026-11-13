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

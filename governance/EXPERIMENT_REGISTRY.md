# Experiment registry

Every experiment gets an entry *before* it runs, and the entry is updated with results. Baselines are never overwritten; negative results are kept.
*In plain words: a lab notebook. We write down what we expect **before** we look, so we can't fool ourselves afterwards.*

---

## EXP-001 — Fixed vs composition vs growing vs evolving primitive substrates
- **Status:** ✅ completed 2026-11-08 · **Result:** core hypothesis not supported; benchmark validated
- **Question:** Under a fixed search budget, does evolving the primitive set and the composition grammar solve more held-out tasks than composing a fixed set, and does that depend on latent structure in the tasks?
- **Related work:** DreamCoder, Stitch, babble, LILO, AbstractBeam, Probe, Momennejad & Raileanu 2026, Prospective Compression 2026 (R001 §1)
- **Code:** `research/pevo` v0.1.0. File hashes are recorded in `experiments/EXP-001/results/summary.json → meta.code_sha256_16`. Not yet under git (see OI-1).
- **Data:** synthetic and generated deterministically from the seed (`pevo/tasks.py`). D-struct and D-flat; 99 train / 60 test tasks per seed.
- **Config:** B = 30,000 values/round, 5 rounds, K = 3, α = 1, val_frac = 0.2, max_holes = 2, max_depth = 3, search_top_m = 8
- **Seeds:** calibration 100; evaluation 0–9
- **Compute:** M4, ~91 s wall-clock for the full grid (parallel), < 1 GB RAM, ₹0
- **Environment:** Python 3.14.6, macOS 27.2 arm64
- **Tests:** 11/11 passing (`research/pevo/tests`)
- **Results (D-struct, held-out solve rate):** C0 58.0 · C1 56.3 · C2 56.7 · C2r 55.2 · C3 57.8 · C4 60.7 (15× compute) · Oracle 76.5 · C0@5× 68.2 · C0@15× 76.3
- **Hypotheses:** H0 PASS (+18.5 pp) · H1 FAIL · H2 FAIL · H3 PASS · H4 FAIL · H5 FAIL (+4.0 pp, CI>0, below the 5 pp threshold)
- **Exploratory:** function-typed holes +3.3 pp [+1.3, +5.7] on struct only; the gate protects (+4.3 pp on flat); grammar fitting hurts; pruning never fired (component untested)
- **Artifacts:** `experiments/EXP-001/results/` (raw JSON per run, summary.md, summary.json), `results_compute_matched_B150000/`, `results_compute_matched_B450000/`, `hypothesis_tests.txt`, `analysis.py`
- **Conclusion:** The right primitives are worth ≈ 15× search in this domain; current discovery methods capture ≈ none of that value. The research problem is *discovery*, not representation.
- **Follow-up decision:** D-008 → EXP-002

## EXP-002 — Prospective primitive discovery (planned)
- **Question:** Can candidates generated from near-miss programs on *unsolved* tasks, scored by a cheap search-benefit proxy, close the C0→oracle gap?
- **Baselines:** C0, C2, C4, Oracle from EXP-001 (frozen code path), plus compute-matched C0
- **Primary metric:** fraction of the gap closed, (Acc − Acc_C0) / (Acc_Oracle − Acc_C0), and the "worth-N×-search" exchange rate, at ≤ 2× C0 compute
- **Success:** ≥ 30% of the gap closed, CI excludes 0, at ≤ 2× compute, on new evaluation seeds 10–19
- **Failure:** < 10% of the gap → test the reverse hypothesis that a richer search prior (a neural recognition model) is the missing ingredient (EXP-003)
- **Stop condition:** two consecutive discovery variants close < 10% → move the effort to EXP-005 (engineering traces) and write up the negative result

## EXP-003 — Search prior without overfitting (planned)
Mixed uniform/fitted grammar; later a tiny MLX recognition model (≤ 1M params) conditioned on I/O examples.

## EXP-004 — Real substrate operators (planned)
Shared-variable holes, split/merge, ablation-based deprecation (fixes OI-2).

## EXP-005 — Engineering primitives from verification traces (planned, after the product alpha)
Public, permissively licensed repositories only.

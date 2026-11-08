# R001 technical appendix (for specialists)

> **You do not need to read this.** It is for other researchers who want to check our work precisely. The plain-language report is [R001](R001-primitive-evolution-prior-art-and-thesis.md), and every word used here is explained in the [Glossary](../GLOSSARY.md). The first technical version of R001 is preserved in git snapshot `a200f19`.

## A1. Formal definitions (v1)

A **substrate** at time *t* is 𝒮ₜ = (Pₜ, Tₜ, Gₜ, θₜ, Aₜ, E):

- **Pₜ**: a finite set of typed operators *p : τ₁ × … × τₖ → τ*, each with executable semantics ⟦p⟧.
- **Tₜ**: argument types {List, Int, Int→Int, Int→Bool}, plus the types holes may take.
- **Gₜ**: the composition grammar. Any well-typed tree over Pₜ with leaf `x`.
- **θₜ**: the search prior. A unigram PCFG turned into integer costs cₚ = max(1, round(−log₂ θₚ)).
- **Aₜ**: the archive of all proposed primitives, each with status ∈ {active, deprecated, rejected}.
- **E**: the evaluator. It is fixed and outside the learner's control.

**Programs.** e ∈ ℒ(Pₜ, Gₜ), with ⟦e⟧ defined recursively. ℒ(P, G) is the "compositional closure" L(P, C) of Momennejad & Raileanu (2026).

**Abstraction.** For a tree *s*, the fragment f = s[π₁ ↦ #₁:τ₁, …, πₘ ↦ #ₘ:τₘ] replaces m non-nested sub-trees with typed holes. Promoting f adds p_f : τ₁ × … × τₘ → type(s), where ⟦p_f⟧(v₁…vₘ) = ⟦f⟧[#ᵢ ↦ vᵢ].
- A *data abstraction* has every τᵢ ∈ {List, Int}.
- A *higher-order abstraction* has some τᵢ that is a function type. This changes Gₜ.

**Operators.**
- merge(p, q) is the anti-unifier abstraction.
- split(p) gives f₁, f₂ with ⟦p⟧ = ⟦f₁ ∘ f₂⟧.
- refactor rewrites the archive so that ⟦rewrite(e)⟧ = ⟦e⟧. This is tested in `test_rewrite_preserves_semantics`.
- Only deprecate and rewrite are implemented in v1.

**Evolution.** *Primitive evolution* is any 𝒮ₜ → 𝒮ₜ₊₁ that changes Pₜ. *Substrate evolution* is any such map that changes Tₜ or Gₜ.

**Candidate utility.**
- MDL utility: U_MDL(f) = uses(f)·(|f|−1) − |f|, computed on solved programs.
- Search utility: U_S(f) = |Solved_B(𝒮ₜ ∪ {f}, 𝒯_train)| − |Solved_B(𝒮ₜ, 𝒯_train)|.

**Stability of p** over a window W requires:
1. usage > 0 throughout W;
2. a positive ablation effect on the held-out solve rate;
3. survival of θ re-fitting.

v1 measures only (1).

**Outcome.** Acc_B(𝒮) = |{τ ∈ 𝒯_test : ∃ e found within budget B with ⟦e⟧ correct on train and held-out inputs}| / |𝒯_test|. B is the number of distinct values admitted.

**Alternatives for later:**
- Bayesian: max P(L)·Πₜ P(tasks | L).
- Prospective description length of future tasks.
- Category-theoretic.

## A2. EXP-001 configuration

| Setting | Value |
|---|---|
| DSL P₀ (26 operators) | `reverse sort tail dedup sum length max min head last concat map filter count add1 sub1 double neg half mod3 even odd pos isneg compose notp` |
| Inputs | Shared by all tasks: 6 train and 4 held-out lists of length 4–8, values −6..12 |
| D-struct | 6 hidden concepts (3 higher-order), composed at levels 1–4 with an optional reducer. Train: 99 tasks, levels 1–3. Test: 60 tasks, levels 2–4. Level ≥ 3 test concept sequences are excluded from train. |
| D-flat | Size-matched random P₀ programs |
| Budget | B = 30,000 values/round · 5 rounds · K = 3 · α = 1 · val_frac = 0.2 · max_holes = 2 · max_depth = 3 · C4 top-M = 8 |
| Seeds | Calibration: 100 · Evaluation: 0–9 |

| ID | Grammar weights | New primitives | Hole types | Deprecation | Gate |
|---|---|---|---|---|---|
| C0 | – | – | – | – | – |
| C1 | ✓ | – | – | – | – |
| C2 | ✓ | MDL top-K | data | – | – |
| C2r | ✓ | random fragments | data | – | – |
| C3 | ✓ | MDL top-K | data + function | ✓ | ✓ (rollback + tabu) |
| C4 | ✓ | MDL top-8 shortlist, accepted iff measured U_S > 0 | data + function | ✓ | built in |
| O | – | the planted concepts | – | – | – |

## A3. Results with statistics (D-struct unless stated; paired by seed; 95% bootstrap CI)

| Test | Δ (pp) | 95% CI | Seeds won/lost | Verdict |
|---|---|---|---|---|
| H0: O − C0 | +18.5 | [+15.2, +21.8] | 10/0 | PASS |
| H1: C2 − C1 | +0.3 | [−3.8, +4.7] | | FAIL |
| H2: C3 − C2 | +1.2 | [−2.8, +4.8] | | FAIL |
| H3: C2r − C1 ≤ 0 | −1.2 | [−3.2, +0.8] | | PASS |
| H4: (C3−C1)_struct − (C3−C1)_flat | −0.0 | [−2.5, +2.8] | | FAIL |
| H5: C4 − C2 | +4.0 | [+1.0, +6.8] | 9/1 | FAIL (below the +5 pp threshold) |

**Exploratory results:**
- C3 − C3noHO: +3.3 [+1.3, +5.7] on struct (6/0), and +0.3 [−2.8, +3.8] on flat.
- C3 − C3noGate on flat: +4.3 [+1.7, +7.5]. 47 batches were rejected.
- C1 − C0: −1.7 (struct) and −4.3 (flat). Both CIs are below 0.
- Deprecation fired 0 times.
- O ≈ C0 at 15× B (76.5 vs 76.3).

Raw data: `experiments/EXP-001/results/`. Code hashes are in `summary.json → meta`.

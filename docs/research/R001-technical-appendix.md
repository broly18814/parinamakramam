# R001 technical appendix (for specialists)

> **You do not need to read this.** It is for other researchers who want to check our work precisely. The plain-language report is [R001](R001-primitive-evolution-prior-art-and-thesis.md), and every word used here is explained in the [Glossary](../GLOSSARY.md). The first technical version of R001 is preserved in git snapshot `fe5edc4`.

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

## A4. Real-code formulation (EXP-005 and EXP-006; added 10 November 2026)

The toy-world definitions in A1 need three changes for real code: there are no executable task specifications, the "programs" are human-written, and the prior is estimated from a corpus instead of from the learner's own solutions.

**Corpus and split.** For a repository with pinned commit *c₁* and split commit *c₀* (an ancestor of *c₁*), let F(c) be the set of included functions at commit c, keyed by (path, qualified name). 𝒟_past = F(c₀), and 𝒟_future = F(c₁) \ F(c₀) by key.

**Normalisation ν.** ν maps a function's AST to a tree with the docstring removed, local names α-renamed to v₀, v₁, … in order of first occurrence, string literals → `STR`, and numeric literals outside {−1, 0, 1, 2} → `NUM`. |t| is the node count of ν(t), excluding expression-context markers.

**Fragments.** A fragment f is a subtree of some ν(t) with 0, 1 or 2 direct child expressions replaced by holes, 4 ≤ |subtree| ≤ 40, occurring at least twice without overlap. |f| counts non-hole nodes.

**Library learning (EXP-005).** Greedy MDL: repeatedly add argmax_f [ uses(f) · (|f| − 1) − |f| ], with uses counted on nodes not yet covered, until |L| = K = 50.

**Compression (EXP-005's outcome).** C(L, 𝒟) = 1 − Σ_t |rewrite_L(t)| / Σ_t |t| over t ∈ 𝒟, where rewrite_L applies L's fragments in library order, top-down, without overlap, each match costing one node.

**Grammar (EXP-006).** A base rule is a node type with its non-node field values and list arities; a slot's context is c = (parent type, field). With library L, the rule set is R_L = R_base ∪ L, a probabilistic tree-substitution grammar. With counts n(r, c) from 𝒟_past rewritten by L, and one pseudo-count per fragment in the backoff:

P_L(r | c) = ( n(r, c) + α · P₀(r | kind(c)) ) / ( n(c) + α ), α = 1.

The weights are always fitted on the evaluated project's 𝒟_past, so conditions differ only in L. The no-library, wider-context condition replaces c by c₂ = (grandparent type, grandparent field, parent type, field), backing off to P_∅(r | c) with the same α.

**Search and effort (EXP-006's outcome).** A derivation's cost is g = Σ −log₂ P_L(r | c). A\* on f = g + h, where h sums each open slot's minimum completion cost (admissible), returns complete trees in order of non-increasing probability. Effort E_L(τ) is the number of states materialised before the target τ = (c, shape) is returned; a tree with probability p is reached after at most 1/p complete trees. Solve_B(L) = |{τ : E_L(τ) ≤ B}| / |𝒯|, where 𝒯 is sampled from the subtrees of 𝒟_future with 4 ≤ |τ| ≤ 12.

**The thesis in this notation (hypothesis, v3).** There exist a data source 𝒟 and a learner ℓ with L = ℓ(𝒟) such that Solve_B(L) > Solve_{2B}(∅) on targets drawn after 𝒟 was fixed, and Solve_B(L) > Solve_B(∅ with context c₂). EXP-001, EXP-002 and EXP-002b refuted this for 𝒟 = the learner's own search traces in the toy domain. EXP-006's H17 and H19 test it for 𝒟 = 𝒟_past.

**Statistics.** Percentile bootstrap, 10,000 resamples, seed 0, resampling functions within project (a cluster bootstrap, since several targets share a function); pooled statistics are unweighted means over projects.

**How A1's "alternatives for later" stand.** "Prospective description length of future tasks" is what EXP-005 measured. The Bayesian form, max P(L) · Π P(tasks | L), is the objective that A4's grammar makes computable, because P_L assigns every tree a probability; it hasn't been used for learning yet (greedy MDL on node counts is used instead).

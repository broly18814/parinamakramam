# R001 — Primitive-substrate evolution: prior art, critique, formal definitions

**Project:** Parinamakramam (పరిణామక్రమం, "the order or course of evolution")
**Date:** 2026-11-08 · **Status:** v1 · **Owner:** founder
**Evidence labels used throughout:** **[F]** fact from a primary source checked this session · **[R]** published research result (with its limits) · **[H]** hypothesis to test · **[D]** engineering design · **[S]** speculation

> **How to read this document.** Every technical section ends with an **"In plain words"** box that explains the same idea with an everyday analogy. If you only read those boxes, you will still follow the whole argument.

---

## 0. The one-paragraph answer

Your core idea is that a system should invent *new building blocks* (primitives), not just rearrange a fixed set. It is **not new as a general idea**. It sits at the meeting point of program synthesis with library learning (DreamCoder 2020, Stitch 2023, babble 2023, LILO 2024), skill libraries (Voyager 2023), and a 2026 theoretical framework that names it almost exactly ("compositional closure", "Next Primitive Prediction"; Momennejad & Raileanu 2026). What is still **open and testable on a Mac**:

1. **When** does inventing new primitives beat smart composition of a fixed set? Nobody has published a clean, controlled answer.
2. **How should a system choose which new primitive to keep?** Today's methods choose by *compression of past solutions*. Our first experiment suggests that this is the wrong objective.
3. **Changing the composition rules themselves**, not just adding blocks: for example, new kinds of slots, deprecating blocks, and rolling back bad changes, all evaluated under strict controls.

> **In plain words.** Think of a cook. A fixed set of primitives is a fixed pantry: salt, onions, rice. Composition is following recipes. Library learning is noticing that you always fry onions with garlic and ginger, so you make a jar of "masala base" and reuse it. Your idea goes further. The cook should also invent *new kinds* of jars, for example a jar with an empty space where you add whichever vegetable you like, and should throw away jars nobody uses. Other researchers have already built cooks who make masala-base jars. What nobody has properly measured is *when* making new jars is worth it, and *how to decide which jars to keep*. That is where we can contribute.

---

## 1. Prior art: what exists (verified)

| # | Work | What it actually does | Status / evidence |
|---|---|---|---|
| P1 | **Momennejad & Raileanu, "A Compositional Framework for Open-ended Intelligence"**, arXiv [2606.15386](https://arxiv.org/abs/2606.15386) (v1 13 Jun 2026, v2 16 Jun 2026) | Defines representational primitives (states, actions) and algorithmic primitives (e.g. nearest neighbour); a compositional grammar (selection, recursion, branching); the **compositional closure L(P, C)** of a finite primitive set P under composition operators C; proposes **Next Primitive Prediction (NPP)** as a training objective; suggests curriculum and self-play to expand the closure. | **[F]** Theoretical. The abstract reports no experiments, and no code is linked. |
| P2 | **DreamCoder** (Ellis et al.), arXiv [2006.08381](https://arxiv.org/abs/2006.08381) | Wake-sleep loop. It solves tasks by writing programs, grows a domain-specific language of abstractions, and trains a neural "recognition model" that guides search. | **[R]** Demonstrated on list processing, drawing, scenes, and rediscovering physics laws. Compute-heavy. |
| P3 | **Stitch** (Bowers et al., POPL 2023), arXiv [2211.16605](https://arxiv.org/abs/2211.16605) | Top-down search for the abstraction that best compresses a corpus of programs. | **[R]** Reported as "3–4 orders of magnitude faster" than DreamCoder's library learning, with ~2 orders of magnitude less memory and comparable or better compression. |
| P4 | **babble** (Cao et al., POPL 2023), arXiv [2212.04596](https://arxiv.org/abs/2212.04596) | Library learning *modulo equational theory*: e-graphs plus anti-unification, so programs that look different but are equivalent can share abstractions. | **[R]** |
| P5 | **LILO** (Grand et al., ICLR 2024), arXiv [2310.19791](https://arxiv.org/abs/2310.19791) | LLM-guided synthesis, Stitch compression, and automatic naming and documentation of abstractions. | **[R]** Beats DreamCoder on string editing, scene reasoning, and graphics benchmarks. |
| P6 | **AbstractBeam** (Zenkner et al.), arXiv [2405.17514](https://arxiv.org/abs/2405.17514) | Adds library learning to LambdaBeam's bottom-up search on integer-list tasks. | **[R]** Significantly beats LambdaBeam (p<0.05). The domain is very close to our EXP-001. |
| P7 | **Voyager** (Wang et al.), arXiv [2305.16291](https://arxiv.org/abs/2305.16291) | GPT-4 agent in Minecraft. It builds a growing library of executable code skills, with an automatic curriculum. | **[R]** Collects ~3.3× more unique items and unlocks tech-tree milestones up to 15.3× faster. The skill library transfers to new worlds. |
| P8 | **Prospective Compression in Human Abstraction Learning** (Hernandez Cano et al.), arXiv [2605.09985](https://arxiv.org/abs/2605.09985) (May 2026, under review) | Argues that existing library learners do *retrospective* compression (they compress past tasks). It finds that humans pick abstractions *prospectively*, for future tasks, when the task stream changes over time. | **[R]** Human experiments plus six models. This is directly relevant to our pilot finding (§5). |
| P9 | **TheoryCoder-2** (Ahmed et al.), arXiv [2602.00929](https://arxiv.org/abs/2602.00929) (Jan 2026) | An LLM synthesises reusable abstractions from experience and uses them in hierarchical planning. | **[R]** More sample-efficient than WorldCoder and other baselines on BabyAI, Minihack, and Sokoban. |
| P10 | **Probe** (Barke, Peleg, Polikarpova, OOPSLA 2020), arXiv [2010.08663](https://arxiv.org/abs/2010.08663) | Bottom-up enumerative synthesis guided by a probabilistic grammar that is learned *during* search. | **[R]** Our enumerator follows this design (cost-ordered bottom-up search). |

### 1.1 Sakana AI and adjacent work (verified)

| Work | Mechanism | What changes / stays fixed | Result & caveat |
|---|---|---|---|
| **Evolutionary Optimization of Model Merging Recipes** (Akiba, Shing, Tang, Sun, Ha). *Nature Machine Intelligence*, 27 Jan 2025, [doi:10.1038/s42256-024-00975-8](https://www.nature.com/articles/s42256-024-00975-8); arXiv [2403.13187](https://arxiv.org/abs/2403.13187) | Evolutionary search (CMA-ES) over *how* to merge existing models, in **parameter space** (weight mixing) and **data-flow space** (which layers a token passes through). | Changes: merge weights and layer routing. Fixed: the source models and the architecture family. | **[R]** A Japanese math LLM and a Japanese VLM with strong benchmark results. No new primitives are created; existing ones are recombined. |
| **CycleQD** (Kuroki, Nakamura, Akiba, Tang; ICLR 2025), arXiv [2410.14735](https://arxiv.org/abs/2410.14735) | Quality-Diversity search. Each task's metric takes a turn as the "quality" score while the others act as behaviour descriptors. Crossover is model merging; mutation is SVD-based. | Changes: weights of a population of LLM agents. Fixed: architecture. | **[R]** Llama-3-8B-based agents beat fine-tuning on coding, OS, and DB tasks and are comparable to GPT-3.5-Turbo on those. |
| **M2N2, "Competition and Attraction Improve Model Fusion"** (Abrantes, Lange, Tang; GECCO 2025), arXiv [2508.16204](https://arxiv.org/abs/2508.16204); code: SakanaAI/natural_niches | Evolutionary merging with (a) evolving **split points** (which parameter groups are swapped), (b) **competition** for limited "resources" to keep diversity, (c) **attraction**: pick mates that complement each other. | Changes: which chunks of which parents combine. Fixed: architecture. | **[R]** Evolves MNIST classifiers from scratch with CMA-ES-level accuracy at lower cost. Merges LLMs and diffusion models. *The idea most relevant to us:* complementarity-based pairing, the same intuition as "two different primitives may complement each other" (§6.3 of your directive). |
| **The AI Scientist** (Lu, Lu, Lange, Foerster, Clune, Ha), arXiv [2408.06292](https://arxiv.org/abs/2408.06292) | LLM pipeline: idea → code → experiments → paper → automated review. | Changes: code and experiments inside human-written templates. | **[R]** "<$15 per paper". Quality was judged mainly by its own automated reviewer. Treat it as a workflow demo, not as evidence of discovery. |
| **The AI Scientist-v2** (Yamada, Lange, Lu, Hu, Lu, Foerster, Clune, Ha), arXiv [2504.08066](https://arxiv.org/abs/2504.08066) | Agentic tree search over experiments, an experiment-manager agent, and VLM feedback on figures. No templates. | — | **[R]** 1 of 3 fully AI-generated workshop submissions scored above the average acceptance threshold at an ICLR workshop. That is a small sample at workshop level. |
| **TRINITY: An Evolved LLM Coordinator** (Xu, Sun, Schwendeman, Nielsen, Cetin, Tang; ICLR 2026), arXiv [2512.04695](https://arxiv.org/abs/2512.04695) | A ~0.6B coordinator plus a ~10K-parameter head, trained with separable CMA-ES, assigns *Thinker / Worker / Verifier* roles to other LLMs over several turns. | Changes: the routing policy. Fixed: all worker models. | **[R]** Reports 86.2% on LiveCodeBench. **Affiliation is not shown on the arXiv page.** The author overlap (Tang, Sun, Cetin) suggests Sakana AI, but I have not verified it; label it "likely Sakana". |
| **Darwin Gödel Machine** (Zhang, Hu, Lu, Lange, Clune), arXiv [2505.22954](https://arxiv.org/abs/2505.22954) (v3 Mar 2026). *Adjacent work; not presented here as Sakana's.* | An archive of self-modifying coding agents. Each child is validated empirically on benchmarks, and the archive keeps diversity rather than only the best agent. | Changes: the agent's own code (tools, prompts, workflows). Fixed: the foundation model. | **[R]** SWE-bench 20.0% → 50.0%; Polyglot 14.2% → 30.7%. Run with sandboxing and human oversight. *Most relevant to us:* "empirical validation instead of proof", the same principle as our C4 condition. |

> **In plain words.** Sakana AI's main trick is like a plant breeder's. They take existing plant varieties (AI models) and cross-breed them in clever ways. They keep a diverse greenhouse so good traits aren't lost, and they pick parents that complement each other. This is powerful, but the breeder never invents a new *gene*; they only shuffle existing ones. Our question is about inventing new genes (new building blocks). The Darwin Gödel Machine is different and comes from another group: an AI that edits its own source code, tries each edited version on real coding tests, and keeps the versions that work. We borrow its rule that a change must *prove itself by test, not by argument*.

### 1.2 Research-gap matrix

| Approach | What changes | What stays fixed | What is *generated* | How it is evaluated | Local on M4? | Our possible extension |
|---|---|---|---|---|---|---|
| Weight merging (Sakana 2024) | merge coefficients, layer routes | source models | merged model | benchmark fitness | small models only | — (not our thesis) |
| Model fusion (M2N2) | which parameter chunks combine | architecture | new weight combos | fitness + diversity | MNIST-scale yes | complementarity-based *primitive* pairing |
| Model coordination (TRINITY) | routing policy | worker models | role assignments | task accuracy | yes (small coordinator) | — |
| Skill composition (Voyager) | skill library (code) | LLM, environment API | executable skills | self-verification in the environment | needs an LLM | measured-benefit skill acceptance |
| Program/library learning (DreamCoder, Stitch, babble, LILO, AbstractBeam) | DSL library | base DSL, type system, composition rules | λ-abstractions | **compression** of solved programs (+ search) | **yes** | (1) **search-benefit** selection instead of compression; (2) prospective selection |
| Primitive discovery (P1, theory) | primitive set P (proposed) | — | — | not empirically evaluated | — | **first controlled experiments** |
| **Primitive-substrate evolution (ours)** | P, **composition grammar C**, interfaces/types, deprecation | evaluator (by design) | primitives, new slot types, rules | **held-out generalisation at a matched search budget**, with positive and negative controls | **yes (EXP-001)** | the core programme |
| Architecture evolution (NAS, DGM) | network/agent structure | evaluator | architectures/agents | benchmark | small scale | later (EXP-005+) |
| Automated science (AI Scientist v1/v2) | experiments, papers | — | papers | automated + human review | API cost | our research engine (later) |

---

## 2. Critique of the thesis (I disagree with parts of it)

**Claim in the directive.** "A system cannot meaningfully evolve higher-level structure unless it can also evolve its own primitives."

**Critique.**
1. **It is false as a logical claim.** A finite alphabet with recursion is already universal (Turing-complete languages, λ-calculus, chemistry's ~90 natural elements). Anything expressible after substrate change was already expressible before. **[F]**
2. **What substrate change can do is change *cost*, not *possibility*:** how many steps it takes to find a solution, how much data is needed, how well a solution generalises. So the scientifically meaningful version is:

> **[H1, refined thesis]** Under a fixed search/compute budget, a system that modifies its primitive set and composition rules solves more *held-out* tasks than one that only composes a fixed set, **if and only if** the task distribution has latent reusable structure that the modification captures. When there is no such structure, substrate change costs performance, because a bigger library means more branching.

3. **The chemistry/biology analogy cuts both ways.** Biology did not invent new elements. It invented stable intermediate *molecules* (amino acids, nucleotides) and *new composition rules* (the genetic code, protein folding). That is "library + grammar" evolution, which supports making grammar change central rather than only adding primitives.
4. **"Complexity alone is not improvement"** must be operationalised. We need (a) a **random-library control** (does adding *any* blocks help?), (b) a **positive control** (do *the right* blocks help, i.e. can the benchmark detect improvement at all?), and (c) a **negative-control distribution** with no hidden structure. EXP-001 includes all three.

> **In plain words.** With the 26 letters of the alphabet you can already write every book that could ever exist, so new letters are never strictly *necessary*. But inventing words, phrases, and sentence patterns makes writing *much faster*. The honest question is therefore not "are new building blocks necessary?" (no) but "when do new building blocks save enough effort to be worth carrying around?" They should help only when the world actually has repeating patterns. If the world is random, a bigger toolbox just means more time choosing tools. We test exactly that.

---

## 3. Formal definitions (v1)

Let a **substrate** at time *t* be

  𝒮ₜ = (Pₜ, Tₜ, Gₜ, θₜ, Aₜ, E)

- **Pₜ** — the *primitive inventory*: a finite set of typed operators *p : τ₁ × … × τₖ → τ*, each with an executable semantics ⟦p⟧.
- **Tₜ** — the *type/interface system*: the set of types that may appear as operator arguments (here {List, Int, Int→Int, Int→Bool}), plus which types **holes** may take when new primitives are formed.
- **Gₜ** — the *composition grammar*: the typed rules for which programs are well formed. Here, any well-typed tree over Pₜ, with leaf `x`.
- **θₜ** — the *search prior*: a probability model over Gₜ (here a unigram PCFG, turned into integer costs cₚ = max(1, round(−log₂ θₚ))).
- **Aₜ** — the *archive*: every primitive ever proposed, with provenance and status ∈ {active, deprecated, rejected}.
- **E** — the *evaluator*. It is **fixed and outside the learner's control** (governance rule G-1).

**Composition.** A program is a tree *e* ∈ ℒ(Pₜ, Gₜ); its meaning ⟦e⟧ is defined recursively. ℒ(P, G) is Momennejad & Raileanu's "compositional closure" L(P, C).

**Abstraction.** Given a tree *s*, a *fragment* f = s[π₁ ↦ #₁:τ₁, …, πₘ ↦ #ₘ:τₘ] replaces m non-nested sub-trees at positions πᵢ with typed holes. Promoting f to a primitive adds p_f : τ₁ × … × τₘ → type(s) with ⟦p_f⟧(v₁…vₘ) = ⟦f⟧[#ᵢ ↦ vᵢ].

- *Data abstraction*: every τᵢ ∈ {List, Int}.
- *Higher-order abstraction*: some τᵢ is a function type. This **changes Gₜ**, because new productions now accept function-valued arguments in a new combination.

**Merge / split / refactor** (definitions; only "deprecate" and "rewrite" are implemented in v1):
- *merge(p, q)* = abstraction over the anti-unifier of ⟦p⟧ and ⟦q⟧'s bodies;
- *split(p)* = replace p by fragments f₁, f₂ with ⟦p⟧ = ⟦f₁ ∘ f₂⟧;
- *refactor(Pₜ)* = rewrite all archived solutions in terms of the new inventory, such that ⟦rewrite(e)⟧ = ⟦e⟧ (tested in `test_rewrite_preserves_semantics`).

**Primitive evolution.** Any map 𝒮ₜ → 𝒮ₜ₊₁ that changes Pₜ.
**Substrate evolution.** Any map that changes Tₜ or Gₜ (for example, enabling function-typed holes, removing productions, or changing the composition rules), not just Pₜ.

**Utility of a candidate primitive.** Two objectives are compared in EXP-001:
- *Retrospective MDL utility* (Stitch-like): U_MDL(f) = uses(f)·(|f|−1) − |f|, computed on already-solved programs.
- *Measured search utility*: U_S(f) = |Solved_B(𝒮ₜ ∪ {f}, 𝒯_train)| − |Solved_B(𝒮ₜ, 𝒯_train)|, the change in the number of training tasks solved under a fixed search budget B.

**Stability of a primitive p** over a window of rounds W: p is *stable* if (i) usage(p, t) > 0 for all t ∈ W, (ii) removing p reduces held-out solve rate (an ablation effect > 0), and (iii) p survives re-fitting of θ. v1 measures (i) only; (ii) and (iii) are in EXP-002.

**Primary outcome.** The held-out solve rate at a matched budget,

  Acc_B(𝒮) = |{τ ∈ 𝒯_test : ∃ e found within budget B, ⟦e⟧ matches τ on training *and* held-out inputs}| / |𝒯_test|.

The budget B counts *distinct values admitted to the search*. That makes it hardware-independent and identical across conditions.

**Alternative formulations to consider later:** (a) Bayesian (DreamCoder): maximise P(library) · Πₜ P(tasks | library); (b) information-theoretic: the expected description length of *future* tasks (prospective); (c) category-theoretic: primitives as morphisms, grammar as a composition structure. (b) is the one our pilot points to.

> **In plain words.** I've given every part of the idea a precise name so we can measure it.
> - The **primitive inventory** is the box of bricks.
> - The **type system** says which bricks can snap together. A list fits into a "sort" brick, but a number doesn't.
> - The **grammar** is the rules for building.
> - The **search prior** is the builder's habits: which bricks they reach for first.
> - The **archive** is a logbook of every brick ever invented, including the ones we threw away.
> - The **evaluator** is the exam marker. The learner is never allowed to touch the marker. Otherwise it could cheat by changing the marking scheme.
>
> An **abstraction** is a brick with *empty slots* (holes). "Sort, then do something to every item" has a slot for *what* to do to every item. A slot that accepts only data is ordinary. A slot that accepts *another action* ("double it", "add one") is special: it changes the building rules themselves. That is our concrete, testable version of "substrate evolution".
>
> Finally, there are two ways to judge a new brick. **Compression** asks: does it make my *old* solutions shorter? **Measured benefit** asks: if I add it, do I actually *solve more problems* within the same time? EXP-001 compares them.

---

## 4. EXP-001 design (pre-registered on 2026-11-08, frozen after the calibration pilot)

**Domain.** Typed integer-list functions. The base DSL P₀ has 26 operators: `reverse sort tail dedup sum length max min head last concat map filter count`, function leaves `add1 sub1 double neg half mod3`, predicate leaves `even odd pos isneg`, and combinators `compose notp`.

**Task distributions** (same input examples for every task; 6 training inputs plus 4 held-out inputs):
- **D-struct**: tasks are compositions of 1–4 *hidden concepts* (six of them, three of them higher-order, e.g. `map(f, sort(a))`), plus an optional reducer. 99 training tasks (levels 1–3) and 60 test tasks (levels 2–4). Level-3 and level-4 test concept sequences never appear in training.
- **D-flat** (negative control): random P₀ programs with the *same size distribution* and no planted structure.

**Conditions** (identical budget B = 30,000 distinct values per round; 5 rounds; K = 3 new primitives per round; α = 1):

| ID | Name | Learns grammar weights | New primitives | Hole types | Deprecation | Validation gate |
|---|---|---|---|---|---|---|
| C0 | fixed | – | – | – | – | – |
| C1 | composition-only | ✓ | – | – | – | – |
| C2 | growing library | ✓ | MDL top-K | data | – | – |
| C2r | random library (control) | ✓ | random fragments | data | – | – |
| C3 | evolving substrate | ✓ | MDL top-K | **data + function** | ✓ | ✓ (rollback + tabu) |
| C3-noHO / -noPrune / -noGate | ablations | | | | | |
| C4 | search-validated evolution *(added after the pilot, D-007)* | ✓ | MDL top-8 shortlist → **accept only if measured U_S > 0** | data + function | ✓ | built in |
| O | oracle (positive control) | – | the hidden concepts themselves | – | – | – |

**Seeds.** Calibration seed 100 was used to build and debug. **Evaluation seeds 0–9 were never inspected before the frozen run.**

**Pre-registered hypotheses and criteria**

| ID | Prediction | Success | Failure |
|---|---|---|---|
| H0 (benchmark validity) | O − C0 > 0 on D-struct | mean > +5 pp, 95% CI excludes 0 | otherwise the benchmark is insensitive → redesign before interpreting anything |
| H1 | C2 > C1 on D-struct | ≥ +5 pp, CI excludes 0 | CI includes 0 |
| H2 (core) | C3 > C2 on D-struct | ≥ +5 pp, CI excludes 0 | CI includes 0 → no evidence that substrate change beats library growth |
| H3 | C2r ≤ C1 | C2r − C1 ≤ 0 | C2r ≈ C2 → the abstraction choice adds nothing beyond "more blocks" |
| H4 (conditions) | gain on D-struct > gain on D-flat | (C3−C1)_struct − (C3−C1)_flat > 0 | — |
| H5 | C4 > C2 on D-struct | ≥ +5 pp, CI excludes 0 | — |

**Compute.** Pure Python, single core per job, ~2–20 s per (condition, seed, distribution) on the M4. The whole experiment takes minutes and needs < 1 GB RAM. ₹0.

> **In plain words.** I built a tiny "puzzle world". Each puzzle shows a few example lists and their answers (for example, `[3,1,2] → [2,4,6]`), and the computer must find a short program that turns the inputs into the answers. It does this by trying programs from simplest to more complex, with a fixed number of attempts, like an exam with a strict time limit.
>
> **Two kinds of puzzle sets.** One has hidden recurring patterns, like a textbook where every chapter reuses tricks from earlier chapters. The other is random, with no recurring tricks. If inventing building blocks is useful, it should help in the first set and not in the second.
>
> **Different "students":**
> - C0 never learns.
> - C1 learns only which bricks it tends to use.
> - C2 makes new combination bricks.
> - C2r makes *random* combination bricks. This checks whether any extra bricks help.
> - C3 also makes bricks with "action slots", throws away unused bricks, and undoes changes that make things worse.
> - C4 tests each new brick before keeping it.
> - The **oracle** is a student who is secretly handed the textbook's true tricks. If even the oracle doesn't do better, the exam itself is broken.
>
> Everyone gets the same number of attempts, so nobody wins by simply trying harder.

---

## 5. Calibration pilot (seed 100 only) — what we learned before the main run

*Logged as D-006 / D-007 in the decision log. These are calibration observations, not evaluation results.*

| Seed 100, B = 30k | D-struct test | D-flat test |
|---|---|---|
| C0 fixed | 55% | 77% |
| C1 composition-only | 53% | 65% |
| C2 growing | 58% | 60% |
| C3 evolving | 57% | 65% |
| **Oracle** | **73%** | **70%** |

Observations:
1. **The benchmark can detect library benefit.** The oracle gains +18 pp on D-struct and *loses* 7 pp on D-flat. The "right blocks help where structure exists, irrelevant blocks hurt" pattern is visible.
2. **Discovery is the bottleneck, not the benchmark.** The MDL learners mostly adopted 2-node "leaf" fragments such as `(sort x)` and `(tail x)`, and partial applications such as `(map double #0)`. These compress *already-solved easy programs* but do not bring unsolved tasks within budget. The higher-order concepts were never chosen. This matches the *retrospective-compression* limitation described in P8.
3. **Grammar fitting overfits.** Fitting the search prior to solved (easy) tasks made rarely-seen operators expensive. That cost 12 pp on D-flat.
4. **The validation gate prevents some harm.** C3 held D-flat at 77% for 3 rounds while C1 and C2 dropped, then degraded in round 4. Ties are accepted, which is a weakness.

Main-run results are in §6.

> **In plain words.** In the practice run, the "student who knows the textbook's tricks" scored much better on the patterned puzzles (+18 points out of 100) and worse on the random ones (−7 points). So the exam works. The students who had to *discover* tricks themselves barely improved. They kept inventing tiny shortcuts that only helped with puzzles they could already solve, a bit like a student who memorises the answers to last week's homework instead of learning the method. That is exactly what a May 2026 paper warns about: today's methods learn from the past instead of preparing for the future. This is useful. It tells us *where* the real research problem is.

---

## 6. Main results (evaluation seeds 0–9)

*Source: `experiments/EXP-001/results/summary.md` and `hypothesis_tests.txt`. Executed 2026-11-08 on the M4: 10 seeds × 2 distributions × 10 conditions in 91 s of wall-clock time. All numbers are real runs.*

### 6.1 Headline table (D-struct, strict held-out solve rate, mean over 10 seeds)

| Condition | Solve rate | Search effort used |
|---|---|---|
| C0 fixed primitives | 58.0% | 1× |
| C1 composition-only | 56.3% | 1× |
| C2 growing library | 56.7% | 1× |
| C2r random library | 55.2% | 1× |
| C3 evolving substrate | 57.8% | 1× |
| C4 search-validated | 60.7% | **15×** |
| **Oracle library** | **76.5%** | 1× |
| C0 with 5× search, one round | 68.2% | 5× |
| C0 with 15× search, one round | 76.3% | 15× |

### 6.2 Pre-registered hypotheses

| | Result (paired by seed, 95% bootstrap CI) | Verdict |
|---|---|---|
| H0 benchmark is sensitive | Oracle − C0 = **+18.5 pp [+15.2, +21.8]**, better on 10/10 seeds | **PASS** |
| H1 growing library beats composition | C2 − C1 = +0.3 pp [−3.8, +4.7] | **FAIL** |
| H2 (core) substrate evolution beats library growth | C3 − C2 = +1.2 pp [−2.8, +4.8] | **FAIL** |
| H3 random blocks don't help | C2r − C1 = −1.2 pp [−3.2, +0.8] | PASS (as predicted) |
| H4 gain depends on structure | (C3−C1)_struct − (C3−C1)_flat = −0.0 pp [−2.5, +2.8] | **FAIL** |
| H5 measured-benefit selection beats MDL selection | C4 − C2 = +4.0 pp [+1.0, +6.8], 9/10 seeds | **FAIL** against the +5 pp threshold. Direction is positive and the CI excludes 0. |

### 6.3 Exploratory findings (not pre-registered; treat as leads, not conclusions)

- **Function-typed slots are the one substrate change with a structure-dependent signal.** C3 − C3-noHO = +3.3 pp [+1.3, +5.7] on D-struct (6 wins, 0 losses), and +0.3 pp [−2.8, +3.8] on D-flat.
- **The validation gate protects against harmful changes.** On D-flat, removing it costs 4.3 pp [+1.7, +7.5]. It rejected 47 proposed batches across all C3 runs.
- **Learned grammar weights hurt.** C1 − C0 = −1.7 pp (D-struct) and −4.3 pp (D-flat), both with CI < 0. Fitting the search prior to the easy tasks it has already solved made it worse on new ones.
- **Deprecation never fired** (0 events), so C3-noPrune was identical to C3. **The pruning component is untested**: by construction every new abstraction is used at least twice. This is an open design bug (OI-2).
- **The oracle library is worth ≈ 15× search.** It matches C0 at 15× budget (76.5% vs 76.3%). This gives us a concrete *exchange rate*: "a primitive set is worth N× search". We will use it as a primary efficiency metric from EXP-002 on.
- **C4 is a poor use of compute in absolute terms.** With the same 15× effort, plain search scores 76.3% against C4's 60.7%.

### 6.4 What this means

1. **[R, ours]** In this toy world, *having* the right building blocks is very valuable (≈ 15× search). Our current methods for *finding* them recover almost none of that value. **The gap between 58% and 76.5% is the research problem.** It is concrete, measurable, and fits on a laptop.
2. **[R, ours]** Compression of past solutions (the Stitch/DreamCoder-style objective, simplified) chose shortcuts for problems the system could already solve. That is consistent with the retrospective-compression critique in P8. We have not shown that this holds for full Stitch or DreamCoder (see limitations).
3. **[H, next]** The most promising directions are: choosing primitives by their effect on *unsolved* tasks (C4's direction was right but it was too expensive); function-typed slots (the only substrate change with a positive, structure-dependent signal); and a stronger, non-overfitting search prior.
4. **The core thesis H2 is not supported by EXP-001.** It is not refuted in general either. It failed under *these* discovery mechanisms. We keep the negative result in the registry.

### 6.5 Limitations (read before citing any number)

- A toy domain: 26 operators, lists of length ≤ 16, synthetic tasks. Nothing here transfers automatically to neural networks or real code.
- The task distribution was *designed* to contain higher-order structure, so a positive result would partly have been true by construction. The flat control and the oracle bound this only partially.
- Our MDL learner is a simplified Stitch: no shared (non-linear) variables, at most 2 holes, depth ≤ 3, greedy selection. Our grammar is unigram, with no neural recognition model as in DreamCoder. A stronger learner might close part of the gap.
- 10 seeds × 60 test tasks: effects below about 3 pp are within noise.
- Hyperparameters (K = 3, α = 1, B = 30k) were fixed a priori and not tuned. Other values might change the conclusions.

> **In plain words: what happened in the real experiment.**
> - **The exam works.** The student who was secretly given the textbook's tricks scored 76.5 out of 100. The student with no tricks scored 58. That held on all 10 exam papers. Knowing the right tricks was worth about as much as being given *15 times more time*.
> - **Our students could not discover the tricks themselves.** Students who invented their own shortcuts (C2, C3) scored about the same as the student who never learned anything (57–58). So the bold version of your idea, "evolving the building blocks automatically gives better results", is **not supported yet**. We are recording that honestly as a failed prediction. Science works this way. The failure is very informative: it shows exactly *where* the problem is.
> - **One promising sign.** Shortcuts with *action slots* ("do [something] to every item after sorting") helped a little, by about 3 points, and only on the patterned puzzles, exactly where they should help. That is a small but genuine hint that changing the *kinds* of building blocks matters.
> - **Another promising sign.** The student who *tested each new shortcut before keeping it* (C4) did best among the learners, about 4 points above the plain library learner. But it spent 15× more effort testing, and a student who simply spent that effort searching harder did much better. So the principle is right, but our version is far too wasteful.
> - **A safety lesson.** The "undo bad changes" rule (the gate) prevented the system from getting worse on random puzzles. That matters later, when the system changes itself.
> - **Bottom line.** The prize is real (58 → 76.5 is available) and the obstacle is clear. Next we need a smarter way to *find* the right building blocks, judged by whether they help with problems we *can't yet* solve, not ones we already can.

---

## 7. Next experiments (planned; see EXPERIMENT_REGISTRY)

- **EXP-002 Prospective primitive discovery.** Generate candidates from *near-miss* programs on unsolved tasks, using enumerated values closest to the target outputs. Score them with a cheap proxy for U_S (the cost reduction of the cheapest known near-miss) instead of a full re-search. Target: close ≥ 30% of the C0→oracle gap at ≤ 2× compute.
- **EXP-003 Search prior without overfitting.** Mix the fitted grammar with a uniform one (θ = λ·θ_fit + (1−λ)·uniform). Report the "worth-N×-search" exchange rate.
- **EXP-004 Real substrate operators.** Non-linear (shared) holes; split/merge; ablation-based deprecation (a primitive is pruned if removing it does not reduce held-out solves).
- **EXP-005 Transfer to engineering primitives.** The same machinery over traces of the product's verification workflow (dependency tracing → affected tests → change-impact analysis), on public, permissively licensed repositories only.

---

## 8. Reproduce

```bash
cd parinamakramam/research/pevo
uv run --python 3.14 --with pytest python -m pytest -q tests      # 11 tests
python3 run_exp001.py --seeds 0-9 --out ../../experiments/EXP-001/results   # ~1.5 min on M4
python3 ../../experiments/EXP-001/analysis.py
```

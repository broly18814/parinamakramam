# A001: an architecture that keeps learning and evolves its own building blocks

**The brief's deliverables 9 and 11** (three architecture proposals; how discovered building blocks could shape an architecture). Asked for by the founder on 12 November 2026: "we need to create a new architecture which continuously learns and evolving architecture". The plan change is recorded as D-050.
**Status:** proposal, 12 November 2026. **Nothing here is a result.** Every "better" is a hypothesis until an experiment below has measured it against the baseline at equal compute.

**Labels:**
- **Fact:** a source, or our own measurement.
- **Prior art:** published work, cited from memory where marked *[not re-fetched]*.
- **Design:** our proposal.
- **Hypothesis:** to be tested.

---

## 1. Where we are, honestly

### In plain words

The models trained so far (C1) are ordinary GPT-style models, the same design as GPT-2. That's deliberate. A new design is only "better" if it beats the ordinary one, trained the same way, on the same data, for the same time on the same Mac. So the ordinary model is the **yardstick** (the baseline). It's not the goal.

**The goal** is a model that does two things ordinary models don't:
1. **It keeps learning.** It learns from new material after training, such as a new codebase, Telugu text or a new library, without forgetting what it already knew. Ordinary models are frozen after training. If you train them further on something new, they forget the old ("catastrophic forgetting").
2. **Its structure evolves.** The model's *building blocks*, the small calculations it's made of, aren't fixed by us. They're discovered by an evolutionary search, and the model can grow new parts when it needs them. This is the brief's "primitive-substrate evolution" applied to the model itself.

### In engineering terms

- **Baseline:** a pre-LN decoder-only Transformer, as in C1 (*fact*: 10M–125M measured at 61k–6.9k tokens/s in bfloat16 on this M4 Pro).
- **Target properties:**
  - (a) **continual learning:** low forgetting (backward transfer near 0) with positive forward transfer, under a stream of domains, at bounded memory;
  - (b) **architecture evolution:** the block's computation graph is searched over a primitive set, and capacity grows during training (function-preserving).

## 2. What already exists (so we don't claim it as new)

| Idea | Prior art | What's still open for us |
|---|---|---|
| **Evolving the building blocks** | Evolved Transformer (So et al., 2019) and **Primer** (So et al., 2021): an evolutionary search over TensorFlow primitives found squared ReLU and depthwise convolution after attention projections, which cut training cost *[not re-fetched]*. AlphaEvolve and ShinkaEvolve: LLM-guided code evolution with exact evaluators (R002) | Primer used large TPU budgets. **Nobody we found evolves blocks at 10M–50M on a laptop, with blocks shared across languages (English, Telugu, Hindi) and code**, scored in bits per byte. Our EXP-001 to EXP-007 machinery (pre-registration, stop rules) is the method |
| **Growing the network** | Net2Net (2015), progressive networks (2016), stacking and growth operators (for example MSG, LiGO, 2022–2023) *[not re-fetched]* | Growth *triggered by learning signals* in a continual stream, rather than on a fixed schedule |
| **Not forgetting** | Replay buffers; elastic weight consolidation (2017); adapters and LoRA per task; mixture-of-experts *[not re-fetched]* | A combination that's measured fairly, at equal compute, against the plain fix (replay) |
| **Learning while in use** | Fast weights; test-time training layers (TTT, 2024); Titans' neural long-term memory (2025); memory layers *[not re-fetched]* | Consolidating that memory into permanent modules ("sleep"), on small models |
| **Libraries of skills** | LILO, Stitch, SkillsBench (R002) | Our EXP-006 result: blocks help only marginally unless the search is guided; EXP-007 tests guidance |

**Inference:** each piece exists. **No piece alone is new.** What could be new is (1) the combination, (2) running it at a scale one person can afford, and (3) measuring it honestly against the plain fixes. That's what we'd claim, and only after it's measured.

## 3. Three proposals (the brief's deliverable 9)

### Proposal 1: **Evolved blocks** (the architecture evolves)

**Plain words.** Each layer of a model is made of a few calculations: multiply, add, normalise, compare. Instead of using the human-designed recipe, a search proposes new recipes. Each is tried by training a tiny 10M model for 10 minutes, and kept only if it learns more per minute than the standard recipe. The best few are then re-tested at 25M and 50M.

**Engineering terms (design):**
- **Search space:** the block is a small directed graph over primitives:
  - linear projection, depthwise causal conv;
  - softmax attention, linear attention, gating (sigmoid × value);
  - elementwise ops (add, multiply, square, ReLU, GELU, SiLU);
  - RMSNorm, residual.
  
  Shapes are type-checked, so no proposal can break shape rules.
- **Proposer:** mutation and crossover (Primer-style). Optionally, as a later arm, an LLM proposer (AlphaEvolve-style) running locally.
- **Fitness:** validation bits per byte on a fixed held-out slice of the registered mix, after a **fixed compute budget**: 10 minutes at 10M, which C1 puts at about 37M tokens. Memory and tokens/s are recorded. A candidate slower than the baseline is charged for it, because fitness is at fixed *time*, not fixed steps.
- **Selection** (the Huxley-Gödel idea, R002): keep lineages whose *descendants* improve, not only the single best.
- **Overfitting guard:** the top candidates are re-run at 25M and 50M with 3 seeds each. Only a gain that survives scale and seeds counts.

### Proposal 2: **A growing library of modules** (the model keeps learning)

**Plain words.** The model has a shared core plus a shelf of small add-on modules. When it meets a new kind of material (Telugu, maths, a new codebase), it adds a new module and trains mostly that, so the old knowledge isn't overwritten. A small "router" learns which modules to use for each piece of text. Modules that turn out useless are removed. The shelf grows and gets pruned: it evolves.

**Engineering terms (design):**
- **Core:** the baseline or Proposal 1's best block.
- **Modules:** low-rank adapters or small MLP experts attached per layer, with top-k routing.
- **Growth trigger:** a new module is spawned when validation loss on the incoming stream exceeds the running average by a threshold, which is fixed at calibration.
- **Plasticity:** old modules are frozen or have a lowered learning rate.
- **Pruning:** a module is dropped if removing it raises loss by less than ε on every domain's held-out slice.
- **Size control:** the number of parameters is capped, and growth beyond the cap must prune first.

### Proposal 3: **Fast memory plus "sleep"** (learning while in use)

**Plain words.** While the model is being used, for example reading a codebase, it writes what it learns into a fast, small memory. That memory updates on every piece of text, so the model improves within the session. Periodically, in a "sleep" step, the useful parts of the memory are made permanent: distilled into a module in Proposal 2's library. The memory is then cleared, so it never fills up or drifts.

**Engineering terms (design):**
- **Memory:** a fast-weight memory layer, an associative matrix updated by a learned rule at test time (TTT/Titans family).
- **Consolidation:** distil the memory-augmented model's predictions on recent data into a new or existing module. The core stays frozen.
- **Measured as:** within-session gain (loss on the later half of a document given the first half) and post-sleep retention.

### How the three fit together: the "Parinama" architecture (deliverable 11)

```
            ┌──────────────── evolution (Proposal 1) ────────────────┐
            │ proposes block recipes from primitives; keeps winners  │
            ▼                                                         │
   tokens → [ evolved core blocks ] → output                          │
                   │      ▲                                           │
                   ▼      │ router                                     │
           [ module library: grows / is pruned (Proposal 2) ] ◄── sleep: memory distilled into modules
                   ▲                                                   │
                   └────── fast memory, updated while in use (Proposal 3)
```

**The link to the research line** (brief §6 and §11):
- The *primitives* are tensor operations, not program fragments as in EXP-001 to EXP-006.
- The *library* is the module shelf.
- The *evolution* is selection by measured learning efficiency.

This applies the project's research question ("can a system discover and evolve its own building blocks?") to the model itself, under the same rules: pre-registered, compute-matched, stop rules.

## 4. Experiments, sized by C1's measurements

Every run is on this Mac, in bfloat16, on data from the [dataset registry](../../governance/DATASET_REGISTRY.md).

| ID | Question | Design | Compute (from C1) | Baseline it must beat |
|---|---|---|---|---|
| **EXP-M1** (already planned) | Which tokenizer for English, Telugu and Hindi? | 10M–50M, bits per byte | hours per run | — (it *makes* the baseline and the data pipeline the others need) |
| **EXP-A1** | Does Proposal 2 keep learning without forgetting? | A 25M model trained on a stream of 5 domains in order: English web → maths → code → Telugu → Hindi. Arms: plain fine-tuning; plain + replay (the simple fix); growing modules; growing modules + replay. Equal total compute | about 5 × 1 hour per arm at 25M; about a day in all | **plain + replay**: the simpler system must lose, or we say so |
| **EXP-A2** | Can evolution find a better block at this scale? | Proposal 1: about 300 candidates at 10M × 10 minutes, over about 6 nights; the top 5 re-run at 25M and 50M × 3 seeds | about 50 hours search + about 30 hours confirmation | the standard block, same time budget |
| **EXP-A3** | Does fast memory help within a session, and does sleep keep it? | Proposal 3 on 25M, on long documents and codebases held out from training | about a day | the same model without memory, plus a longer context window |
| **EXP-A4** (only if two of A1–A3 pass) | Do the parts combine? | The best block + modules + memory at 50M, against the 50M baseline, in one continual stream | about 3 days | 50M baseline + replay |

**Predictions and stop rules** are written per experiment before its code, as for EXP-006. The general stop rule here: **if a proposal doesn't beat its simple baseline at equal compute, it's reported as a negative result and not built on.** Two of three negative means the combined architecture (EXP-A4) isn't attempted.

### My honest priors, before any code

- **EXP-A2** finding a block that survives scale and seeds: about 25%. Primer's gains needed huge searches; ours is small, so finding nothing is the likeliest single outcome. Even so, a measured negative at laptop scale is publishable.
- **EXP-A1**, growing modules beating replay: about 35%. Replay is a famously strong simple baseline.
- **EXP-A3**, a within-session gain beyond a longer context window: about 40%.

## 5. Order within plan v2

1. **EXP-M1 first.** It builds the data pipeline (from the registry) and the tokenizer every later experiment uses, and the baseline model the proposals must beat.
2. **Then EXP-A2**, overnight, because evolution needs no new data, only the pipeline. **EXP-A1** follows, then EXP-A3.
3. ~~**IND-1** (Telugu and Hindi coding tasks)~~ was removed by the founder (D-056), so it no longer shares these nights. Originally: it shares the same nights. If the Mac is over-booked, IND-1 moves to the next 90 days, as plan v2's risk 4 already says. That's a cost of this change, recorded in D-050.

## 6. Limits known in advance

- **Small scale.** 10M–50M parameters on one laptop. A gain here is a ranking signal: DataDecide suggests rankings transfer about 80% of the time (R002). It's not proof at large scale.
- **Equal compute is the only fair comparison**, and it's measured in wall-clock time on this Mac. That favours designs that suit Apple's GPU, which we state with every result.
- **Prior-art citations marked *[not re-fetched]*** are from memory, and are checked against the papers before any result is published.

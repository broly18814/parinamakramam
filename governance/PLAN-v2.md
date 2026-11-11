# Plan v2: the next 90 days, rebuilt from the founder's goals

**Status: PROPOSED, 12 November 2026. Not in force until the founder approves it.** The current [roadmap](ROADMAP.md) stays in force until then.
**Built from:** the founder's original brief (all 26 sections, re-read in full on 12 November 2026) and fresh research from primary sources ([R002 report](../docs/research/R002-fresh-plan/REPORT.md); seven sets of notes in [`R002-fresh-plan/notes/`](../docs/research/R002-fresh-plan/notes/)).
**Rules kept:** ₹0, no interviews ever (D-002), one person, honest results, no foreign private funders (D-048).

**Labels used (brief, section 24):**
- **Fact:** a source or our own measurement.
- **Inference:** my reasoning from facts.
- **Hypothesis:** to be tested.
- **Design:** a proposed build.

---

## 1. Can we go according to the original plan?

### In plain words

**Mostly yes, except for the product. There the original plan can't win as written, and the research shows why.**

| Part of the brief | Where it stands | Can we follow it as written? |
|---|---|---|
| Research: building blocks, experiments, honest results (days 41–70) | Five experiments done, ahead of schedule | **Yes.** The next experiment follows directly from our results |
| Own small models (days 71–90, year 1) | Not started | **Yes**, at small sizes. This Mac is an M4 Pro (checked today), and the research gives realistic speeds |
| Telugu and Hindi (year 1) | Not started | **Yes**, on a narrow task where nobody has published results |
| **The first product: a full AI coding assistant** (days 11–25: repository search, code explanation, code changes, editor extension) | **Never built.** On day 1, decision D-009 narrowed it to the checker. That was a change of direction you were never asked about. | **Not as written.** See below |
| Paid offers, activation, retention (days 71–90) | Not started; no users yet | Only after people use something |
| Grants and compute (days 71–90) | Researched (F001, R002) | Yes, using only the brief's own sources |

**Why the full assistant can't win as written:**
1. Every big tool now does it, backed by billions: Copilot, Claude Code, Codex, Cursor (now owned by SpaceX/xAI), and Devin (which absorbed Windsurf). They sell the AI power behind it at $10–$200 a month. With ₹0 we can't buy that power to resell, and the brief also forbids "a thin API wrapper".
2. The models that fit on this Mac are about a year behind the best ones, and slow. The best local coding model reads a long prompt at about 125 tokens (word-pieces) per second. So a "local assistant" would feel slow next to the paid tools.

**The research also corrected a claim we published.** On day 1, P001 said nobody else was a "neutral referee" for AI code. That's no longer true:
- **GitHub Copilot's coding agent now runs your tests and links its logs to every change.**
- **pytest-testmon** (free) already picks the affected tests.
- **Skylos** (free) and at least seven other small tools already catch deleted or skipped tests.

Our checker, as it stands today, isn't unique. Zero users is normal for this crowded corner: the other tools mostly have none either.

**What is still open, and fits one person with ₹0** (all three are checked by running code, not by opinion):
1. **Tests that were quietly weakened in ways today's checkers miss.** For example, `== 90` loosened to "is truthy", or an expected answer edited to match the bug. Skylos's own self-test admits it misses 3 of its 9 cases. Nobody publishes a fair comparison of these checkers.
2. **Building blocks that help only with good guidance.** The research literature now agrees with our EXP-006 result. It also shows that nobody has published the obvious next experiment on real Python code.
3. **Telugu and Hindi on real-project coding tasks.** Simple Telugu and Hindi coding tests are nearly solved (scores of 80–99.7 out of 100). Nobody has published results on a real-project benchmark released two months ago (Indic SWE-bench).

### In engineering terms

- **Facts:**
  - The brief's §10 product (stages 1–3) overlaps with funded incumbents. Cursor, Copilot and Augment index repositories, and Copilot's cloud agent runs tests plus CodeQL with an `Agent-Logs-Url` per commit ([GitHub docs](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations)).
  - Each of pkv's three functions has a free substitute:
    - test selection: pytest-testmon 2.3.0, MIT, 2 Nov 2026;
    - independent re-run: Skylos, dunnit;
    - tamper detection: Skylos, goodhart, tamperguard, tampercheck, testwall, checkwash.
- **Inference:** the brief's own rules decide the change:
  - "if a simpler system achieves the same outcome, recommend the simpler system";
  - "find specific workflows where we can demonstrate a measurable advantage";
  - "do not agree with me simply because I am the founder".

  So the plan keeps the brief's *goals* but changes the *route* to the product goal.

---

## 2. The new plan in one paragraph

### In plain words

For 90 days, put all effort into proving three things in public, each where funded companies haven't:
1. **The product:** turn our checker into **the best-measured "proof layer" for AI coding agents**. That means catching the hidden test-weakening others miss, producing evidence the AI can't fake, publishing an honest public scoreboard of every checker including ours, and plugging straight into Claude Code and GitHub.
2. **The research:** run the next building-block experiment that the literature hasn't done.
3. **Own models and Indian languages:** take a first real, small step on each, on this Mac.

Money comes later from a self-service paid plan, sold through a platform that handles foreign taxes, so no company is needed at first. Each part has a written rule for when to continue and when to stop.

### In engineering terms

Four tracks, each independently testable with its own go/no-go rule (brief §3, §25.1). Each is one person's work, AI-assisted, using existing free tools.
- **Track A** is about 50% of the time.
- **Track B** is about 25%.
- **Tracks C and D** together are about 25%, mostly in the background on the Mac overnight.

---

## 3. Track A, the product: the proof layer for AI coding agents

### In plain words

When an AI says "done, all tests pass", our tool answers four questions:
1. Did the tests really run, on exactly this code?
2. Were any tests weakened, even subtly?
3. Do the new or changed tests actually catch mistakes?
4. Here is evidence the AI couldn't have edited.

We prove it works with a public scoreboard, and we fit it into the places people already work.

This also keeps the brief's Stage 1 ("understand the project") honest. The checker already maps which code depends on which. We turn that map into a small "explain this project's structure" feature that needs no AI at all.

### In engineering terms (designs; every claim of better is a hypothesis until measured)

| # | Deliverable | Mechanism | Done when |
|---|---|---|---|
| A1 | **TAMPER-BENCH**: a public, pre-registered benchmark of tamper detectors | Planted and real weakening cases, hand-labelled, including Skylos's own 9 self-test cases and its 3 admitted misses. Every detector (pkv, Skylos, goodhart, checkwash and others) runs under the same conditions. Predictions are committed before any run | Published with all scores, ours included, even if we lose |
| A2 | **"Do the tests still bite?"**: mutation testing restricted to the changed lines | Make small deliberate bugs (mutants) in the lines the change touched, and run the selected tests. A test that kills no mutant checks nothing. This catches loosened assertions and expected values edited to match the bug, which diff-reading can't | Measured on A1's hidden cases: more caught, no rise in false alarms |
| A3 | **Clean-checkout evidence bundle** | Re-run the selected tests from a fresh `git worktree` outside the agent's working folder. Record commands, exit codes, test IDs, the tree hash and the tool version, all signed by a content hash. This targets "tests pass" claims from stale runs (claude-code #104504) | `pkv fresh` verifies a bundle; a tampered bundle is detected in self-checks |
| A4 | **Integrations** | A Claude Code `Stop` / `TaskCompleted` hook that blocks "done" unless the verdict allows it ([hooks docs](https://code.claude.com/docs/en/hooks)), plus the existing GitHub Action (already on the Marketplace) | Hook installable in one command; documented; tested in CI |
| A5 | **`pkv map`**: brief Stage 1 without an AI model | Print the import graph pkv already builds as a project-structure summary: modules, who uses what, and which tests cover which code | Correct on the four REAL-001 projects; snapshot self-checks |
| A6 | **One public launch**, after A1 to A4 are real | Show HN and the relevant subreddits, posted by the founder in their own words (the rules require the poster to be present and allow no AI-written posts) | Posted once; results logged in ADOPTION.md |

**Not in Track A:** editing code ourselves (Stage 2). Users keep their own agent (Claude Code, Codex, Copilot or a local model), and pkv checks its work. Stage 2 can come back later on top of a model the user brings, once there are users.

**Go/no-go rule for Track A (pre-registered here; the numbers are fixed before any reading):**
- **Window:** from the launch (A6) to 12 weekly readings after it.
- **Continue and invest more if any of these happen:**
  - 3 or more public repositories outside ours use pkv's Action or hook;
  - 1 or more issues are filed from a real project;
  - 300 or more PyPI downloads a week sustained for 4 weeks, beyond our own CI.
- **Rethink if none happen.** The options are written now, not later:
  1. Change who it's for: AI-evaluation researchers measuring agents that cheat.
  2. Change the channel.
  3. Pause the product and keep pkv as research infrastructure.

---

## 4. Track B, the research: building blocks with guidance (EXP-007, replacing the closed one)

### In plain words

EXP-006 found the phrase book helped no more than guessing twice as long, while sharper habits helped more. Recent papers say the same thing in other settings: learned building blocks are rarely reused unless the search is guided by how they're used. The obvious next experiment, which nobody has published on real Python code, tries every pairing of three kinds of phrase book with three kinds of guidance. It shows whether building blocks help only when guided.

### In engineering terms

- **Hypothesis H23:** library gain is positive only under context-conditioned guidance. Measured as the interaction term in a 3 × 3 factorial:
  - **library:** none; EXP-005 learned; learned plus "named" (blocks with names and documentation);
  - **guidance:** flat PCFG; CTX2 (EXP-006's grammar); a grammar distilled from a local 3–8B model's samples, HySynth-style;
  - **metric:** tasks solved against states expanded, at equal budgets, with a 2× compute-matched control.
- **Data:** rich and pyparsing, both still untouched (held out), plus the EXP-006 machinery, which is already built and tested.
- **Selection rule, from the Huxley-Gödel Machine idea:** keep a block only if it lowers held-out search cost for the programs that use it.
- **Stop rule, written before the run:** if the interaction is not positive and the library adds nothing under any guidance, the library line pauses. The research moves to guidance and model work (Track C).
- **Only if H23 holds:** EXP-008 builds a verified, pruned skill library for a local coding agent, using SkillsBench's design (none vs self-made vs curated skills). This links the research to the product.

---

## 5. Track C, own models: small, measured, lawful

### In plain words

First we measure what this Mac can really do: a 10-minute training test at each model size. Then the first model experiment has to be useful, not just a demo. We compare how well different "word-splitters" (tokenizers) handle English, Telugu and Hindi, on small models trained from scratch, using only data whose licence allows it. Today's common tokenizers spend about 3 times as many tokens on Telugu as on Hindi, which makes Telugu slower and costlier.

### In engineering terms

- **C1, week 1: measure.** A throughput benchmark for 10M, 25M, 50M and 125M models in MLX on this M4 Pro. It replaces R002's estimates; for 125M the estimate was about 4,000–8,000 tokens a second, meaning a 4–7 day run.
- **C2: dataset registry (brief §16).** Every source with its licence, hash and version:
  - **text:** FineWeb-Edu (ODC-By), IndicCorp v2 (CC0), Sangraha (CC-BY-4.0);
  - **code:** a permissive-licence subset of The Stack v1 dedup, keeping provenance;
  - **excluded:** Samanantar (non-commercial). Also The Stack v2 and Python-Edu, because of the open-model principle.
- **C3, EXP-M1:** a tokenizer comparison at 10–50M parameters, scored in bits per byte across English, Telugu and Hindi, with equal compute for every tokenizer.
  - **Claim allowed:** rankings only. DataDecide shows rankings at small scale predict about 80% of larger-scale ones.
  - **Stop rule:** if no tokenizer beats the baseline by more than seed noise, report it and stop.

---

## 6. Track D, Telugu and Hindi on real tasks

### In plain words

A fixed small set of real-project coding tasks, with the instructions in English, Telugu and Hindi. A local model on this Mac attempts each one, and the project's own tests decide pass or fail, so nobody has to judge by opinion. These would be the first published Telugu and Hindi results on this benchmark.

### In engineering terms

- **IND-1:** a fixed subset of `indic-swe-bench` (Apache-2.0, released Sep–Oct 2026), about 30 tasks × 3 languages, run with Qwen3.6-35B-A3B (Apache-2.0) on this Mac.
- **Cost estimate:** prompt reading at about 450–750 tokens a second on the M4 Pro means roughly tens of hours of overnight runs.
- **Metric:** pass rate by language with confidence intervals; and for Hinglish and Tenglish (Telugu-English) variants, the size of the gap.
- **Pre-registered**, held-out, with predictions written first.

---

## 7. Money and the company (only the brief's own sources)

### In plain words

- **No company yet.** It costs real money (about ₹6,000–₹23,000 to set up a One Person Company), and almost nothing pays back until there's a product people use.
- **The first paid offer** comes only after Track A's "continue" signal. It would be sold through a platform that becomes the legal seller and handles foreign taxes (Polar or Paddle), which can pay out to India without a company.
- **Before the first payment**, five tax questions go to a chartered accountant.
- **Government programmes are mostly closed to individuals.** The one possibly open now is Telangana's TISC 2026, a challenge, not a grant, closing 20 November. Only you can decide whether to enter.

### In engineering terms

- **Facts:**
  - DPIIT recognition excludes individuals.
  - IndiaAI compute has no individual category and is about a 40% subsidy, not free.
  - GENESIS EIR cohort 3 accepted individuals but closed on 3 September. Watch for cohort 4.
  - Stripe India and Razorpay international both need a registered entity. Polar pays out to India through Stripe Connect.
- **Not yet researched:** cloud-provider credit programmes. This is a small follow-up, done before any compute need arises.

---

## 8. The 90 days, fortnight by fortnight

| Weeks | Track A (product) | Track B (research) | Tracks C and D (models, languages) | Founder-only steps |
|---|---|---|---|---|
| 1–2 (to 26 Nov) | TAMPER-BENCH design pre-registered; cases collected | EXP-007 design pre-registered | C1 throughput benchmark; C2 dataset registry | Decide on TISC (closes 20 Nov); approve this plan |
| 3–4 | A2 mutation check built and self-tested | EXP-007 built and calibrated | — | — |
| 5–6 | TAMPER-BENCH run once; results published | EXP-007 run once; results published | IND-1 pre-registered | — |
| 7–8 | A3 evidence bundle; A4 Claude Code hook | Write-up; decide EXP-008 by the stop rule | EXP-M1 pre-registered | — |
| 9–10 | A5 `pkv map`; release pkv 0.3 | EXP-008 design (only if H23 held) | IND-1 runs overnight | Approve the pkv 0.3 release |
| 11–13 | A6 launch; weekly readings start | — | EXP-M1 runs; IND-1 results published | **Write and post the launch** (only you can) |

---

## 9. What changes from the current roadmap

| Current item | In plan v2 |
|---|---|
| "Guidance experiment" next (D-044) | Becomes EXP-007's factorial, which tests guidance and library together |
| BENCH-004 | Folded into TAMPER-BENCH, which is public and compares rivals too |
| Days 11–25 assistant features ("not planned", D-009) | Stage 1 returns as `pkv map` (no AI); Stage 2 editing stays with the user's own agent |
| Grants (F001's foreign funders) | Removed (D-048) |
| P001's "no neutral referee exists" | **Corrected**: Skylos and others exist; our edge must be proven by measurement |

## 10. Biggest risks

1. **Checkers like ours may simply not be adopted.** Eight similar tools have almost no users. That's why Track A has a stop rule and a pivot written now.
2. **Copilot or Claude Code may add mutation checks themselves.** That's why we publish the benchmark: it stays useful whoever wins.
3. **The Mac's speed** could make IND-1 or EXP-M1 too slow. C1 measures this first, and both experiments shrink to fit.
4. **Overload for one person.** Tracks C and D run mostly unattended overnight; if time runs short, D moves to the next 90 days.

## 11. Decisions this plan needs from the founder

1. **Approve plan v2**, or ask for changes. If approved, it becomes D-049 and replaces the current roadmap's days 71–90.
2. **TISC 2026** (Telangana, closes 20 Nov; the date is from a secondary source): enter or skip.
3. Later, at week 11: **write and post the launch yourself.**

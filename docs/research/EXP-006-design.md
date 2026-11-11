# EXP-006 design: do learned building blocks make *search* for real code cheaper? (pre-registration)

**Status:** pre-registered on 10 November 2026. Written **before** any EXP-006 code was written or run. Nothing about search has been measured; the only numbers in this document are data sizes (section 3).
**Why now:** EXP-005 showed that building blocks learned from a project's past *describe* its future code more compactly (13.5% shorter, against 1.9% for random fragments). Decision D-037 set the next question: does that also make it cheaper for a computer to *find* that code? A shorter description and a faster search are different things, and only the second one could ever help a tool write code.
**Words:** see the [Glossary](../GLOSSARY.md). Each section gives the plain version first and the engineering version second.

---

## 1. The question

### In plain words

Think of the keyboard on your phone. It guesses your next word, likeliest guess first. A better keyboard is one where the word you wanted appears after fewer wrong guesses.

We play the same game with code:

1. Take a function that a project's programmers wrote **after** a certain date.
2. Hide one small piece of it, for example `if value is None: return default`.
3. Ask the computer to guess the hidden piece **exactly**, trying its likeliest guesses first.
4. Count how many guesses it builds before it gets there. That count is the **effort**.

The computer learns its guessing habits only from code written **before** that date. Then we compare guessers that differ in one thing: their phrase book.

| Guesser | What it has |
|---|---|
| **A: no phrase book** | Only single "words" of code, and habits about which word tends to follow which |
| **B: own phrase book** | The same, plus 50 ready-made phrases learned from this project's past (EXP-005's method, unchanged) |
| **C: random phrase book** | Plus 50 phrases picked at random from the project's past |
| **D: other projects' phrase book** | Plus 50 phrases learned from two *other* projects |
| **E: cheat phrase book** | Plus 50 phrases learned from the hidden answers themselves. Not a fair guesser: it shows the best a phrase book could do |
| **F: no phrase book, sharper habits** | No phrases, but habits that look one step further up the code for context |

A phrase book has a cost as well as a benefit. A ready-made phrase reaches a long answer in one step. But every extra phrase is one more option to consider at every step, which makes all the *other* answers slightly harder to reach. EXP-001 found exactly this cost in the toy puzzle world. This experiment measures which effect wins on real code.

Guesser F matters most for honesty. If sharper habits alone do as well as a phrase book, the phrase book isn't needed, and we say so.

### In engineering terms

- **Task:** exact-match infilling of a masked abstract-syntax-tree (AST) subtree, given its position in the tree.
- **Model:** a probabilistic context-free grammar (PCFG) over normalised Python ASTs, estimated by smoothed relative frequencies from the project's past code. Adding blocks turns it into a probabilistic **tree-substitution grammar** (TSG): a grammar whose rules may be whole tree fragments with open slots.
- **Search:** best-first enumeration of derivations in order of decreasing probability (A\* with an admissible completion bound), with a fixed budget of expanded states.
- **Independent variable:** the fragment inventory (none, own past, random, other projects, oracle) and, for condition F, the conditioning context of the base grammar.
- **Dependent variable:** the share of masked subtrees recovered within the budget, and the number of states expanded.
- **Design:** temporal split within each project; three projects never used in any earlier experiment; cluster bootstrap over functions.

**What this experiment can't show.** It doesn't involve a neural network or a large language model, so it says nothing direct about AI coding assistants. Exact match is strict: a guess that means the same but is written differently counts as wrong. It tests one specific claim: at equal effort, a grammar-based search finds more of the real future code when it has the learned blocks.

## 2. What is already known, and what isn't

The title, authors, venue and stated result of each source were checked against its arXiv abstract page on 10 November 2026. The full papers haven't been re-read for this design, so the right-hand column says only what the abstracts do and don't report.

| Source | What it showed | What it leaves open for us |
|---|---|---|
| Allamanis & Sutton, *Mining Idioms from Source Code*, 2014 ([link](https://arxiv.org/abs/1404.0417)) | Recurring code idioms can be mined automatically with probabilistic tree-substitution grammars, and the mined idioms recur across projects. | The reported evaluation is about whether idioms recur and are meaningful, not about search effort. |
| Shin, Allamanis, Brockschmidt & Polozov, *Program Synthesis and Semantic Parsing with Learned Code Idioms* (PATOIS), NeurIPS 2019 ([link](https://arxiv.org/abs/1906.10816)) | Adding mined idioms to the output language of a neural code generator improved its accuracy on two datasets. | It uses a trained neural generator. The abstract reports accuracy; it doesn't report a comparison at matched search effort, an own-project versus other-project control, or a time split inside one project. |
| Stengel-Eskin, Prasad & Bansal, *ReGAL*, ICML 2024 ([link](https://arxiv.org/abs/2401.16467)) | Large language models predict programs more accurately when given a library of functions learned by refactoring. | It depends on a large language model and on running the code. |
| Fijalkow and others, *Scaling Neural Program Synthesis with Distribution-based Search*, AAAI 2022 ([link](https://arxiv.org/abs/2110.12485)) | Search methods that enumerate programs from a probabilistic grammar in order of likelihood, with optimality guarantees. | It's about the search method itself. It gives us the family of search we use, not an answer to our question. |

**Honest position.** That fragments improve a grammar's fit to code is expected from this earlier work, so a pass on the first prediction below would **not** be a discovery. The parts nobody has measured in this form are:
1. how large the benefit is in units of search effort ("worth how many times more searching?");
2. whether a project's *own* blocks beat blocks from other projects when searching, not only when describing;
3. whether blocks beat the simpler alternative of sharper habits with no blocks at all.

## 3. Data: which code, and why (fixed before running)

**Why new projects.** EXP-005's future functions (in click, more-itertools and boltons) have already been analysed: we know the learned blocks fit them well. Designing this experiment after seeing that and then testing on the same functions would tilt the result in our favour. So EXP-006 is evaluated only on **three projects that no earlier experiment touched**.

**How they were chosen.** The ordered candidate list below was fixed before any of these projects was downloaded: attrs, packaging, urllib3, httpx, rich, pyparsing. They're widely used, pure-Python libraries with permissive licences and long histories, from six unrelated maintainers. The rule: go down the list and take the first three that meet all of these:
- a permissive licence (MIT, BSD or Apache-2.0), checked in the project's own licence file;
- the EXP-005 split rule finds a split: walking the main branch back from the pinned commit 10 commits at a time, the first point with at least **50 functions** that exist at the pin but not at the split;
- at least **200 functions** in the past (training) part.

The **pinned commit** is the tip of each project's main branch as downloaded on 10 November 2026. Honest note: the claim that the list came first can't be proven from this repository's history. The first timestamped proof is the commit containing this document, made before any search code exists.

**Measured data sizes** (function counts only; nothing about compression or search was computed):

| Candidate, in list order | Licence (from its own files) | Pinned commit | Split commit | Split date | Past functions | Future functions | Outcome |
|---|---|---|---|---|---|---|---|
| attrs | MIT | `9d9f94a043` | `8e759ce878` | 2024-07-15 | 182 | 50 | **excluded**: under 200 past functions |
| **packaging** | Apache-2.0 or BSD-2-Clause | `843887fd43` | `d2fa923848` | 2026-06-25 | 459 | 50 | **evaluation project 1** |
| **urllib3** | MIT | `c5347bbd39` | `6ec2a1d368` | 2024-06-21 | 498 | 73 | **evaluation project 2** |
| **httpx** | BSD-3-Clause | `b5addb64f0` | `0088253b32` | 2022-02-04 | 433 | 87 | **evaluation project 3** |
| rich | MIT | `3a109ccdff` | `0425c792c1` | 2022-08-17 | 840 | 62 | not needed (three already found) |
| pyparsing | MIT | `810199f89b` | `3f64e4b10b` | 2025-12-25 | 971 | 81 | not needed |

Full commit names of the three evaluation projects:
- packaging: pin `843887fd431f8b3c10f1b39e1d4066ba3516147c`, split `d2fa92384821919d48eab89bae087b950637d52a`;
- urllib3: pin `c5347bbd39203d68d7b0e3ffb83ced3e3b4b9109`, split `6ec2a1d36872a583aa32c54e345633aae1c332d6`;
- httpx: pin `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, split `0088253b32c7e6541ce85f40429f133c01ca35dc`.

How the table was measured: EXP-005's split rule, computed with a faster equivalent that remembers each file version it has already read. It was checked two ways. On tomli it returns EXP-005's recorded calibration split exactly (`c00fbc1f82`, 42 past and 40 new functions). For the three evaluation projects, EXP-005's own `snapshot()` code gives the same counts at the split and the pin. Total sizes there: about 20,000 to 27,000 tree nodes of past code and 3,000 to 4,200 of future code per project.

Two things to know about these splits:
- The time windows differ a lot: packaging's 50 new functions arrived in under five months, httpx's 87 took about four years. The rule fixes the *number* of new functions, not the time span.
- rich and pyparsing stay untouched, so they're available as fresh projects for a later experiment.

**Code included, normalisation, past and future:** exactly EXP-005's written rules (its section 2 and 3), unchanged. Past = every included function at the split. Future = the functions added after it.

**Use of the code.** As in EXP-005, the code is only **read** through git. Nothing is installed or executed, no model is trained on it, and none of it is copied into this repository. We publish counts, and at most the 10 most-used blocks per project in normalised form.

## 4. Method (for specialists)

### 4.1 Grammar

Trees are EXP-005's normalised function ASTs.

- **Base rule.** At a node, the rule is the node's type together with all its non-node field values and the lengths of its list fields, with each child node replaced by a slot. Example: `Call(func=□, args=[□, □], keywords=[])`, or `Attribute(value=□, attr='append')`. This is EXP-005's `shape()` cut off at depth one. Operator nodes (`Add`, `Eq`, …) are ordinary child nodes with their own rules, as in EXP-005's size measure.
- **Context of a slot:** the pair (parent node type, field name). Example: (`Call`, `func`).
- **Block rule.** One of a library's blocks: a tree fragment whose HOLEs are its slots. Each HOLE's context is its (parent type, field) inside the fragment.
- **Kind of a context:** the Python AST base class (`expr`, `stmt`, `operator`, …) most often seen in that context in the past code.

**Counts.** For the no-library conditions, every node of every past function contributes one count of (rule, context). For a library condition, each past function is first rewritten with the library exactly as EXP-005 rewrites code (blocks in library order, top-down, no overlaps). Each block use counts once as a block rule in the context of its root; the nodes it covers contribute nothing; everything else counts as base rules. Each block also gets **one extra count** in the backoff distribution, so a block never used in the past (possible for the random, other-project and cheat libraries) is still reachable.

**Probabilities** (fixed smoothing, α = 1):

P(r | c) = ( n(r, c) + α · P₀(r | kind(c)) ) / ( n(c) + α ), where P₀(r | k) = n(r) / n(k) over rules whose root has kind k.

The weights are **always** estimated on the evaluated project's own past, in every condition. Conditions differ only in which blocks exist, so the comparison isolates the inventory from the habits.

**Condition F (sharper habits, `CTX2`).** No blocks. The context is widened to (grandparent type, grandparent field, parent type, field), backing off to the one-level estimate above with the same constant:

P₂(r | c₂) = ( n(r, c₂) + α · P(r | c) ) / ( n(c₂) + α ).

### 4.2 Search

- **State:** a partial tree with its open slots; the leftmost open slot is expanded next.
- **Cost so far:** g = the sum of −log₂ P of the rules used.
- **Completion bound:** h = the sum, over open slots, of the cheapest possible completion of a slot with that context, computed once per grammar by fixed-point iteration. It never overestimates, so A\* on f = g + h returns complete trees in order of non-increasing probability.
- **Successors** are generated lazily, in order of increasing f.
- **Effort** = the number of states built (taken from the queue and materialised). It's counted identically in every condition. With a library, the same tree can be reached by more than one route; each route costs effort. That is a real cost of a library and is charged to it.
- **Solved** = a complete tree whose `shape()` equals the hidden subtree's. The search never looks at the target to steer or prune.
- **Budget.** Each (task, condition) runs once to **B_max = 100,000** states. Because the search is deterministic, the effort at which a task is solved gives the outcome for every smaller budget. The **primary budget is B = 20,000**.
- A task whose target can't be derived at all (a rule never seen in the past) is counted as unsolved in every condition. The share of derivable tasks is reported.

### 4.3 Tasks

For each future function, the eligible targets are its statement and expression nodes with EXP-005 size from **4 to 12**, not counting the function node itself. From each function, up to **8** targets are drawn uniformly without replacement, using `random.Random(0)` over the project's future functions in sorted order (path, then qualified name) and each function's nodes in `ast.walk` order. A task is (the target's context, the target's shape). Nested targets are allowed; the statistics account for this by resampling whole functions.

### 4.4 Conditions

| Code | Phrase book | Blocks | What it controls for |
|---|---|---|---|
| `NONE` | A | none | the zero point |
| `OWN` | B | K = 50 learned from this project's past (EXP-005's `learn`, K = 50, maximum pattern size 40, both frozen in D-036) | the method |
| `RANDOM` | C | 50 recurring candidates drawn uniformly (seed 0) from the same pool | "any extra fragments would do" |
| `OTHER` | D | 50 learned from the pooled pasts of the other two evaluation projects | "it's just general Python" |
| `ORACLE` | E | 50 learned from the future functions themselves | the ceiling: can this test detect a good library at all? |
| `CTX2` | F | none; two-level context | "sharper habits do the same job without blocks" |

### 4.5 Measures and statistics

- **Solve rate at budget b** for a project = tasks solved within b states ÷ all its tasks, written as points out of 100.
- **Pooled** = the plain average of the three projects' solve rates.
- **Ranges:** 95% percentile bootstrap, 10,000 resamples, seed 0, resampling each project's future *functions* with replacement (a cluster bootstrap, because targets from one function aren't independent).
- **Also reported, as description and not as tests:** solve rate by target size; `NONE` at 5 × B; the median ratio of efforts on tasks both conditions solve; the share of `OWN`'s solutions whose route used a block.
- **Replication of EXP-005** on the new projects, using EXP-005's code unchanged: compression under OWN, RANDOM, OTHER and ORACLE.

## 5. Predictions, success and failure criteria

All differences are pooled, at the primary budget B unless stated.

| ID | Prediction | Success | Failure |
|---|---|---|---|
| **H16 (primary)** | Blocks from the past make search cheaper: `OWN` solves more than `NONE` | `OWN` − `NONE` ≥ **+3 points**, range excluding 0, **and** positive in all 3 projects | the range includes 0, or the difference is negative |
| **H17 (compute control)** | The library is worth more than doubling the search | `OWN` at B − `NONE` at **2 × B** > 0, range excluding 0 | the range includes 0 or lies below it: more search does as well or better |
| **H18** | The benefit is partly project-specific | `OWN` − `OTHER` > 0, range excluding 0 | the range includes 0: general Python blocks search as well |
| **H19 (simpler-system control)** | Blocks beat sharper habits | `OWN` − `CTX2` > 0, range excluding 0 | the range includes 0 or lies below it: conditioning on more context does the job without blocks |
| **H20** | Learned blocks beat random ones | `OWN` − `RANDOM` > 0, range excluding 0 | the range includes 0 |
| **H21** | The past captures much of what a library could give | (`OWN` − `NONE`) ÷ (`ORACLE` − `NONE`) ≥ 30% | < 10% |
| **H22 (the test works)** | A good library is detectable at all | `ORACLE` − `NONE` ≥ +3 points, range excluding 0 | otherwise H16 and H21 are **uninformative**, and the result is recorded as "the test can't detect a library", not as a failure of the idea |
| **R13 (replication)** | EXP-005's main result holds on new projects | compression `OWN` − `RANDOM` ≥ +3 points pooled, range excluding 0, positive in all 3 | the range includes 0 |

### My honest prior, written before any code

- `NONE` solves 15–35 of 100 tasks at B. This is the least certain number, which is why calibration may move B (section 6).
- **H16:** `OWN` − `NONE` between +2 and +6 points. About a 60% chance of passing.
- **H17:** about 45%. Where a block applies it should save several bits, and every bit saved halves the effort. But blocks apply to a minority of targets and slightly penalise all the others.
- **H18:** about 30%. EXP-005 found the project-specific layer small (+1.9 points, absent in one project).
- **H19:** about 50%. Two-level context is a strong, simple competitor, and it's the result I'm least able to predict.
- **H20:** about 85%. **H21:** 30–60% of the gap. **H22:** about 85%. **R13:** about 90%.

### How the outcomes will be read

- **H16 and H17 pass:** blocks learned from history make search materially cheaper on real code. Research continues by using the library inside a search that is checked by running tests (EXP-007, to be pre-registered).
- **H16 passes, H17 fails:** the benefit is real but smaller than doubling the search. That repeats EXP-002b's lesson (more search wins), and the blocks' value stays mostly descriptive.
- **H16 fails (with H22 passing):** blocks from history don't make this search cheaper. D-037's condition applies: their value is descriptive only.
- **H19 fails:** whatever H16 says, the simpler system is preferred. The research then turns from libraries of blocks to better *habits* (learned guidance), which is the question EXP-003 asked in the toy world.
- **Stop rule.** If H16 fails, or H16 passes while both H17 and H19 fail, the block-library line pauses on real code as well, and the next pre-registration must be about guidance, not blocks.

## 6. Calibration rules (no tuning on the exam)

1. Code is built and debugged on **tomli only**, with humanize as its OTHER project, exactly as in EXP-005 (split = the first point with at least 15 new functions). Both were already used for calibration in EXP-005.
2. After the first calibration run, at most **two** things may change, each by a rule fixed here and each recorded in the decision log:
   - **The primary budget B**, from {5,000; 20,000; 50,000}, with B_max = 5 × B. Rule: use the smallest value at which `NONE` solves at least 20% of the calibration tasks; if none does, use 50,000. The aim is only to avoid a test where almost nothing or almost everything is solved.
   - **The largest target size**, from 12 to 8, only if `NONE` solves under 10% of calibration tasks at B = 50,000.
3. Nothing else is tuned: not K, not the pattern size, not α, not the contexts.
4. Then the design is **frozen** (a decision-log entry), and the analysis script is committed. Only after that are the three evaluation projects searched, **once**.
5. A self-check requires the published output to reproduce exactly from the saved results, as for every experiment.

## 7. Cost

- **Money:** ₹0. Only git and Python's built-in modules.
- **Time (estimate):** about 1,200 tasks × 6 conditions, each at most 100,000 states. In plain Python that is up to roughly an hour on one processor core, and about 10 minutes across the MacBook's cores.
- **Memory (estimate):** under 2 GB per worker; the queue holds at most a few hundred thousand small entries.

These are estimates made before the code exists. The measured figures will replace them in the results section.

## 8. Limits known in advance

- **Three well-maintained libraries**, 50-odd new functions each. It says nothing about applications, other languages or large codebases.
- **Exact match is strict.** `x is None` and `None is x` count as different. This is the same for every condition, but it makes all scores lower than a "means the same" test would.
- **Closed vocabulary.** The search can only produce names and attributes seen in the past. A new function that introduces a new name can't be recovered by any condition.
- **Small targets.** Sizes 4 to 12 are fragments, not functions. A pass shows cheaper search for fragments only.
- **No neural network.** A pass doesn't show that a language model would benefit, and a fail doesn't show it wouldn't.
- **Learning cost isn't charged.** Building a library takes seconds of extra computing that `NONE` and `CTX2` don't spend. It's paid once, not per task, and its measured time will be reported next to the results.

---

## 9. Calibration and freeze (11 November 2026)

Everything in this section was decided on tomli only. No evaluation project (packaging, urllib3, httpx) has been searched.

### What the calibration run gave

One run on tomli, with every search taken to 250,000 states (budget 50,000 × 5). 260 hidden pieces, of which 248 can be built at all from tomli's past code. Source: `experiments/EXP-006/calibration/run1/`; the decision below is reproduced exactly by a self-check.

| Found, out of 100, within… | 1,000 | 5,000 | 20,000 | 50,000 | 250,000 |
|---|---|---|---|---|---|
| NONE (no phrase book) | 19.2 | **26.5** | 38.1 | 44.6 | 53.8 |
| OWN (own past's phrase book) | 33.5 | 38.5 | 46.9 | 50.8 | 56.5 |
| RANDOM | 24.6 | 30.8 | 43.1 | 50.0 | 58.8 |
| OTHER | 19.6 | 29.2 | 39.2 | 46.2 | 54.6 |
| ORACLE (cheat phrase book) | 31.2 | 38.5 | 46.5 | 51.5 | 61.5 |
| CTX2 (sharper habits) | 38.8 | 49.2 | 57.7 | 61.2 | 69.6 |

### The two decisions, both by the written rules

- **Primary budget B = 5,000 states** (searches run to 25,000). Rule: the smallest of 5,000, 20,000 and 50,000 at which NONE finds at least 20 of 100. NONE found 26.5 at 5,000.
- **Largest target size stays 12.** Rule: drop to 8 only if NONE finds under 10 of 100 at 50,000. It found 44.6.

Nothing else was changed after the calibration run.

### Implementation details the design didn't spell out, settled while building and before the calibration run

1. **Every rule gets the extra backoff count, not only blocks.** Section 4.1 gives "one extra count" to each block. Without the same for base rules, a base rule whose every past use sits inside a block would get probability zero in the library conditions only, so those conditions couldn't build some pieces that NONE can. The extra count is given to every rule in every condition, which keeps the set of buildable pieces identical across conditions, as section 4.2 requires.
2. **The category of a position never seen in the past.** A block's hole always holds an expression. A hidden piece's own position takes the category of the piece (a statement position or an expression position). That is a fact about Python's grammar, not information about the answer.
3. **Ties.** Guesses of equal likelihood are taken in the order they were queued; rules of equal cost are ordered by when they were first seen in the past code. The search is fully deterministic.
4. **The calibration OTHER project** is humanize at commit `d16e6352c9785c5ab86de0133222bd22e89b0db2`. EXP-005 used humanize too but didn't record its commit.

### Engineering checks done before the calibration run

- A smoke run on tomli with a budget of 2,000 was used only to measure speed. Its numbers weren't used for any decision and weren't kept. It showed each step was too slow, because every finished guess was rebuilt in full before being compared. The comparison now stops at the first difference. A self-check proves it gives the same answer as rebuilding, so no effort count can change.
- 16 self-checks: 13 for the grammar and search, 2 that pin the runner to the registered commits and settings, and 1 that reproduces the calibration decision exactly. They check that every piece of code can be rebuilt exactly; libraries are applied exactly as EXP-005 applies them, in EXP-005's order; every position's probabilities add up to one; the completion bound is exact; finished guesses come out most likely first; and the effort reported is the guess's position in that order.
- **Testing the tests.** The code was broken on purpose in four ways (completion bound set to zero, library applied in reverse order, comparison ignoring length, backoff weight halved). A self-check failed every time. The reverse-order break was missed at first, so a test with two overlapping blocks was added before the calibration decision was recorded.

### What the calibration numbers do and don't say

They come from **one small project** (42 past functions), used for building and fixing. They aren't evidence for or against any prediction, and they're shown only so the budget decision can be checked. On tomli, sharper habits (CTX2) were ahead of every phrase book at every budget. If that holds on the evaluation projects, H19 fails and the stop rule applies; that can only be known from the evaluation run.

**Code version, honestly.** The calibration result file names snapshot `497c769` as its code version, but the EXP-006 code wasn't committed yet when it ran. Since then the code changed only in ways that can't change a result: an equal-length check made explicit (`strict=True`) in the comparison, and the runner now also records whether the code had uncommitted changes. The evaluation run will use the committed, frozen code.

**The design is frozen from the commit that contains this section.** The analysis script (`experiments/EXP-006/analysis.py`) is in the same commit. The evaluation run happens once, after it.

---

## 10. Results (evaluation projects, run once after the freeze in D-043)

Run on 11 November 2026 from the frozen snapshot `488ca6f`, with no uncommitted changes (every result file records this). Source: `experiments/EXP-006/results/` and `experiments/EXP-006/hypothesis_tests.txt`. Reproduce with `python3 experiments/EXP-006/analysis.py`; a self-check requires that output to match exactly. The whole run took 39 seconds on the MacBook, far below the 10-minute estimate, because the frozen budget (5,000) is small.

**The robot's check on the freeze, honestly.** GitHub's robot marked the freeze snapshot `488ca6f` as failed. Every self-check passed (148 of 148), but our own checker, pkv, gave the verdict UNVERIFIED. The reason: the self-check for `calibrate.py` ran the script as a separate program, where pkv can't see it being checked. After the results were saved, that self-check was changed to run the script in-process, and pkv now gives VERIFIED. Only a test changed; the frozen experiment code and every result are untouched.

### In plain words first

- **The phrase book helps a little.** With the project's own phrase book, the guesser found 18.3 of 100 hidden pieces within 5,000 guesses, against 14.2 with no phrase book. It helped in all three projects.
- **But simply guessing twice as long helps just as much.** With no phrase book and 10,000 guesses, it found 18.5.
- **And sharper habits, with no phrase book at all, did better than the phrase book:** 22.6 of 100.
- So the extra machinery isn't worth it here. The simpler system wins, and the rule written in advance says: pause the phrase-book line and work on better habits next.

### Found, out of 100 hidden pieces, within 5,000 guesses

| Project | Pieces | Buildable at all | NONE | OWN | RANDOM | OTHER | ORACLE | CTX2 | NONE, 10,000 guesses |
|---|---|---|---|---|---|---|---|---|---|
| packaging | 341 | 71.6% | 16.4 | 21.1 | 18.8 | 19.6 | 22.0 | 21.7 | 20.5 |
| urllib3 | 374 | 68.7% | 15.0 | 17.4 | 15.8 | 17.9 | 19.8 | 20.9 | 18.7 |
| httpx | 410 | 90.5% | 11.2 | 16.3 | 11.7 | 14.6 | 15.9 | 25.4 | 16.3 |
| **Average** | | | **14.2** | **18.3** | 15.4 | 17.4 | 19.2 | **22.6** | **18.5** |

### Pre-registered tests

| | Result | Verdict |
|---|---|---|
| **H16** OWN − NONE (primary) | **+4.1 points** [+2.5, +5.7], positive in all 3 | ✅ PASS |
| **H17** OWN − NONE with double the search (compute control) | −0.3 [−1.9, +1.4] | ❌ FAIL: doubling the search does as well |
| **H18** OWN − OTHER (project-specific) | +0.9 [−0.1, +1.8] | ❌ FAIL: other projects' blocks search about as well |
| **H19** OWN − CTX2 (simpler-system control) | **−4.4** [−6.3, −2.5] | ❌ FAIL: sharper habits are clearly better |
| **H20** OWN − RANDOM | +2.9 [+1.4, +4.4] | ✅ PASS |
| **H21** share of the cheat library's gain | 81.4% [60.3, 105.0] | ✅ PASS |
| **H22** the test can detect a good library | +5.0 [+3.4, +6.7] | ✅ PASS |
| **R13** EXP-005 replicated on new projects (compression OWN − RANDOM) | +11.4 [+10.1, +12.6], positive in all 3 | ✅ PASS |

**Registered reading:** H16 passed, but both H17 and H19 failed, so **the stop rule applies**: the block-library line pauses on real code, and the next pre-registration is about guidance (better habits), not blocks.

### My prior, against what happened

| | Prior (written before any code) | Result |
|---|---|---|
| NONE at 5,000 | 15–35 of 100 | 14.2 (just below) |
| H16 | +2 to +6, ~60% to pass | +4.1, passed |
| H17 | ~45% | failed |
| H18 | ~30% | failed |
| H19 | ~50%, "the one I'm least able to predict" | failed clearly |
| H20, H22, R13 | ~85%, ~85%, ~90% | all passed |
| H21 | 30–60% | 81% (higher) |

### What this does and doesn't mean

- **It means:** the phrase book's gain in search is real but small: worth about doubling the search, not more. A plainer improvement to the guesser, looking one level further up the code before guessing, beats it by 4.4 points. The cheat phrase book (learned on the answers) gains only 5.0 points, so even a perfect library of this kind has little to offer this search. The past already captures 81% of that small ceiling.
- **It also means EXP-005 replicates:** on three projects nobody here had analysed, the past's blocks again describe future code far more compactly than random fragments (12.9% vs 1.5%), and other projects' blocks again come close (12.1%).
- **Where the blocks help most:** medium pieces (7 to 9 nodes), where OWN found 4.0 of 100 against CTX2's 2.4. That is a lead, not a test: the numbers are tiny.
- **It doesn't mean** blocks never help search. This is one grammar, one search method, exact match, small pieces, three libraries. A neural guesser could behave differently.
- **Limits:** 28 to 31% of pieces in packaging and urllib3 can't be built at all from past code (a name or attribute never seen before). They count as unsolved in every condition, which pulls every score down equally.

### Decision (D-044)

Following the reading registered in section 5, the block-library line pauses on real code (its toy-world version was closed by D-035). EXP-007 is closed unrun. The next research pre-registration is about **guidance**: what to guess next. CTX2 is the simplest form of guidance, and it won; the natural next question is how much further better context can go, at equal effort.

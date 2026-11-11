# R001: Can a computer invent its own building blocks? What others have done, what we think, and what our first experiment found

**Project:** Parinamakramam ("the course of evolution")
**Date:** 8 November 2026 · **Version:** 3 (updated 10 November 2026 with the results of experiments 2 to 5, new sources, and the plan from here; sections 2.3, 2.4 and 7 are new or rewritten, and sections 3 to 6 are unchanged) · **Owner:** founder

> **How to read this.** This report is written for someone who is not a scientist or programmer. When a technical word can't be avoided, it is explained the first time it appears, and the [Glossary](../GLOSSARY.md) has every such word in one place. The exact maths and statistics, for other researchers who want to check our work, are in the separate [technical appendix](R001-technical-appendix.md). You do not need to read it.

> **How sure are we?** Each important statement carries a label:
> - ✅ **Checked fact.** I read the original source myself.
> - 📄 **Someone else's published result.** Reported by other researchers; we did not repeat it.
> - 🧪 **Our own result.** We measured it ourselves, in our experiment.
> - 💡 **Idea to test.** Not proven yet.
> - 🔮 **Guess.** Speculation; treat it carefully.

---

## 1. The short answer

Your big idea is that **a computer should invent new building blocks for thinking, not just rearrange the ones it was given.**

- **Other people have worked on this before** ✅, so the general idea is not new. Since 2020 several research groups have built programs that notice patterns they keep repeating and save them as new shortcuts. In June 2026 a paper described almost exactly your idea, but only as a theory, with no experiments.
- **What nobody has answered properly yet:**
  1. *When* is inventing new building blocks actually worth the trouble, compared with just combining the old ones cleverly?
  2. *How* should a computer decide which new blocks to keep?
  3. What happens if the computer changes not only its blocks but also the **rules for how blocks connect**?
- **Our first experiment** 🧪 found two things. The *right* building blocks are hugely valuable: worth as much as thinking 15 times longer. But the usual way of choosing new blocks does not find the right ones. **So the real problem is discovery: finding the good blocks.**

> **A cooking picture.** A cook has a pantry: salt, onion, rice, chilli. Cooking means combining pantry items. A smart cook notices "I always fry onion, garlic and ginger together", so they make a jar of *masala base* and reuse it. That is a new building block. Your idea goes further. The cook should also invent *new kinds* of jar, like a jar with an empty space for "whichever vegetable you like today", and throw away jars nobody uses. Other researchers have built cooks who make masala-base jars. Nobody has carefully measured *when* making jars pays off, or *how to pick which jars to make*. That is our opening.

---

## 2. What other people have already done ✅

I read each of these from the original source (links included). In the table, a **program** means a recipe of instructions a computer follows, and a **library** means the computer's growing collection of saved shortcuts.

| Who / what | What it does, in plain words | How well it worked |
|---|---|---|
| **Momennejad & Raileanu, June 2026** ([link](https://arxiv.org/abs/2606.15386)) | A theory paper describing almost exactly your idea. It says intelligence comes from a small set of basic building blocks plus rules for combining them, and suggests training AI to *predict the next useful building block* (they call it "Next Primitive Prediction"). | Theory only. ✅ No experiments and no code. |
| **DreamCoder, 2020** ([link](https://arxiv.org/abs/2006.08381)) | Solves puzzles by writing small programs. While "asleep" it looks back at its solutions, saves repeated patterns as new shortcuts, and trains itself to guess which shortcuts suit which puzzle. | 📄 Worked on list puzzles and drawing, and even rediscovered physics formulas. Needs a lot of computing power. |
| **Stitch, 2023** ([link](https://arxiv.org/abs/2211.16605)) | A much faster way to find "the pattern that shortens my old solutions the most". | 📄 Reported as about 1,000 to 10,000 times faster than DreamCoder's version, using far less memory. |
| **babble, 2023** ([link](https://arxiv.org/abs/2212.04596)) | Finds shared patterns even when two solutions *look* different but mean the same thing (like "2+3" and "3+2"). | 📄 Published research result. |
| **LILO, 2024** ([link](https://arxiv.org/abs/2310.19791)) | Uses a chatbot-style AI to help write programs, finds shortcuts with Stitch, then asks the AI to give each shortcut a sensible name and description. | 📄 Beat DreamCoder on text-editing, picture and reasoning puzzles. |
| **AbstractBeam, 2024** ([link](https://arxiv.org/abs/2405.17514)) | Adds shortcut-saving to a program-search tool working on lists of numbers. **Very close to our experiment.** | 📄 Clearly better than the same tool without shortcuts. |
| **Voyager, 2023** ([link](https://arxiv.org/abs/2305.16291)) | An AI playing Minecraft writes down every skill it learns ("how to make a wooden sword") as reusable code, building a skill library. | 📄 Collected about 3.3 times more kinds of item and reached key milestones up to 15 times faster. Its skills worked in new worlds too. |
| **"Prospective Compression", May 2026** ([link](https://arxiv.org/abs/2605.09985)) | Studied how humans choose shortcuts. Found that **humans pick shortcuts that will help with *future* problems**, while computer methods pick shortcuts that summarise *past* problems. | 📄 Human experiments plus six computer models. **This matches what went wrong in our experiment** (see section 6). |
| **TheoryCoder-2, January 2026** ([link](https://arxiv.org/abs/2602.00929)) | An AI that turns its experience into reusable rules and uses them to plan in puzzle games. | 📄 Learned from fewer attempts than competing methods. |
| **Probe, 2020** ([link](https://arxiv.org/abs/2010.08663)) | A way to search for programs by trying the simplest ones first and building bigger ones out of smaller ones. | 📄 **Our experiment's search works this way.** |

### 2.1 Sakana AI (the Japanese company you asked about) ✅

| What they made | What it does, in plain words | Result, and the catch |
|---|---|---|
| **Evolutionary model merging** ([journal](https://www.nature.com/articles/s42256-024-00975-8), [preprint](https://arxiv.org/abs/2403.13187)), *Nature Machine Intelligence*, January 2025 | Takes several existing AI models and uses an evolution-style search (try many mixtures, keep the best, repeat) to find the best way to **blend** them into one. | 📄 Produced strong Japanese maths and Japanese image-understanding models. **The catch:** nothing new is invented; existing models are mixed. |
| **CycleQD** ([link](https://arxiv.org/abs/2410.14735)), 2025 | Keeps a *population* of AI models with different strengths and takes turns rewarding each skill, so the population stays varied rather than all becoming the same. | 📄 Its models beat ordinary training on coding and computer tasks. |
| **M2N2** ([link](https://arxiv.org/abs/2508.16204)), 2025 | Blends models like breeding animals: models "compete" for limited resources, which keeps variety, and each one picks partners whose strengths **complement** its own. | 📄 Built working image-recognisers from scratch cheaply and blended large models. **Useful idea for us:** pick building blocks that complement each other. |
| **The AI Scientist** ([link](https://arxiv.org/abs/2408.06292)), 2024 | An AI pipeline that has a research idea, writes code, runs experiments and writes a paper. | 📄 About $15 per paper. **The catch:** quality was mostly judged by its own AI reviewer, like marking your own homework. |
| **The AI Scientist v2** ([link](https://arxiv.org/abs/2504.08066)), 2025 | A better version that explores many experiment paths and checks its own graphs. | 📄 One of 3 fully AI-written papers scored above the usual acceptance bar at a small conference workshop. That is a small sample. |
| **TRINITY** ([link](https://arxiv.org/abs/2512.04695)), 2026 | A small "manager" AI that hands out roles (thinker, worker, checker) to bigger AIs. | 📄 Reported 86.2% on a coding test. **Not confirmed as Sakana's:** the paper page doesn't list the company, though several authors are Sakana people. |
| **Darwin Gödel Machine** ([link](https://arxiv.org/abs/2505.22954)). *Not Sakana's; a related project by a different group.* | A coding AI that rewrites its own code, tests each new version on real coding problems, and keeps a varied collection of versions that work. | 📄 Its score on a well-known coding test rose from 20% to 50%. **We borrowed its key rule:** a change must prove itself by *testing*, not by argument. |

> **In plain words.** Sakana works like a plant breeder: it cross-breeds existing plants (AI models) cleverly and keeps a varied greenhouse. It never invents a new *gene*. Your idea is about inventing new genes, and that's the difference. The Darwin Gödel Machine contributes one rule we copied: try the change, test it for real, and keep it only if it works.

### 2.2 Where the gap is

Everyone above changes *something* and keeps *something* fixed:

- **Model blending** (Sakana) changes the *mixture* and keeps the original models.
- **Skill libraries** (Voyager) add *skills* and keep the AI itself fixed.
- **Shortcut-learning programs** (DreamCoder, Stitch, LILO, AbstractBeam) add *shortcuts*, keep the basic instructions and joining rules fixed, and choose shortcuts by **"which one makes my old solutions shortest?"**
- **The 2026 theory paper** proposes changing the building blocks themselves, but **tests nothing.**

**Our opening** 💡:
1. Change the **joining rules**, not only the blocks.
2. Choose blocks by **"does it help me solve more?"** instead of "does it shorten old solutions?"
3. Measure all of it **fairly**, with careful comparison groups, on a laptop.

### 2.3 Work on building blocks in *real* code (added 10 November 2026)

Our fifth experiment moved from toy puzzles to real code, so these sources became relevant. For each one, the title, authors, venue and stated result were checked against its arXiv abstract page. The full papers haven't been re-read, so the results are labelled 📄 and described only as their abstracts describe them.

| Who / what | What it does, in plain words | Why it matters to us |
|---|---|---|
| **Allamanis & Sutton, "Mining Idioms from Source Code", 2014** ([link](https://arxiv.org/abs/1404.0417)) | Finds the phrases programmers keep reusing ("idioms") automatically, by fitting a grammar whose rules may be whole chunks of code with gaps. | 📄 Mined idioms recur across projects. **This is the closest earlier work to our EXP-005**, so "code has reusable blocks" is not our discovery. |
| **Sivaraman and others, "Mining Idioms in the Wild", 2021** ([link](https://arxiv.org/abs/2107.06402)) | The same family of method, but on trees that also record how data flows, tested on code in the Hack language. | 📄 Found places worth tidying up in old code better than a version without the data-flow information. |
| **Shin and others, PATOIS, NeurIPS 2019** ([link](https://arxiv.org/abs/1906.10816)) | Gives mined idioms to a neural code generator as extra "words" it may write in one step. | 📄 Accuracy improved on two datasets. **This is the closest earlier work to our EXP-006.** |
| **Stengel-Eskin, Prasad & Bansal, ReGAL, ICML 2024** ([link](https://arxiv.org/abs/2401.16467)) | Builds a library of reusable functions by rewriting existing programs, then lets a large language model use them. | 📄 The models predicted programs more accurately with the library. |
| **Fijalkow and others, distribution-based search, AAAI 2022** ([link](https://arxiv.org/abs/2110.12485)) | Ways to try programs in order from most to least likely under a probabilistic grammar, with proofs of optimality. | The kind of search EXP-006 uses. |

A search on 10 November 2026 for work that measures what EXP-006 measures (search effort at a matched budget, a project's own blocks against other projects' blocks, and blocks against sharper habits, on a time split inside one project) found none. That is "not found in three searches", not "doesn't exist".

### 2.4 How the opening has narrowed after five experiments (added 10 November 2026)

**In plain words.** Section 2.2 named three openings. Here is what our own experiments did to each.

| The opening we named | What we found 🧪 | Where it stands |
|---|---|---|
| 1. Change the **joining rules**, not only the blocks | Action slots added 3.3 points on patterned puzzles in EXP-001. That was noticed afterwards, not predicted in advance. | A lead, not a result. Its follow-up (EXP-004) is on hold. |
| 2. Choose blocks by **"does it help me solve more?"** | Testing each shortcut first gave +4 points on 9 of 10 exam papers, below our 5-point bar, at 15 times the effort. Two "near-miss" methods (EXP-002, EXP-002b) scored slightly below the learner they were built on. | Mostly negative. At equal effort, simply searching more beat every learner we built. |
| 3. Measure it all **fairly**, on a laptop | Every experiment had a matched-effort comparison, a cheat student and unseen exam papers. | Delivered. This is the part of the project that has worked best. |

What the five experiments say together: **a system can't easily discover good blocks from its own past search, but it can learn them from code that people wrote** (EXP-005: 13.5% shorter descriptions of future code, against 1.9% for random fragments). That learned material turned out to be mostly general Python habits, with only a thin project-specific layer.

So the idea is now stated like this 💡 (a hypothesis, not a result):

> **With limited effort, new building blocks help when two things are true: the problems contain recurring structure, and the blocks are learned from a richer source of information than the system's own earlier attempts. Whether a library of blocks then does better than sharper habits over the original blocks is an open question.**

EXP-006 tests the last sentence directly.

**In engineering terms.** Self-supervised library learning from the learner's own solved or nearly solved tasks (MDL-ranked fragments, utility-gated fragments, and two prospective near-miss variants) recovered none of the oracle library's +18.5-point effect at matched compute, and lost to a 2× search-budget control. Corpus-based fragment mining on human-written code generalised across a temporal split on a description-length measure (OWN − RANDOM = +11.5 points of compression, OWN − OTHER = +1.9). The open question is whether that description-length gain converts into lower search cost, and whether a tree-substitution grammar beats a plain grammar with a wider conditioning context.

---

## 3. Where I disagree with your idea

**Your claim:** "A system cannot meaningfully evolve higher-level structure unless it can also evolve its own primitives." (Primitives are the basic building blocks.)

**My view:**

1. **As stated, it isn't true** ✅. With just the 26 letters you can write every book that will ever exist; you never need a 27th letter. In the same way, a small fixed set of computer instructions can already express every possible program (computer scientists proved this in the 1930s). Chemistry builds everything from about 90 natural elements, and nature never invented a new one.
2. **What new blocks really change is *effort*, not *possibility*.** Words and phrases make writing much *faster*, even though letters alone could do it. So the honest, testable version of your idea is 💡:

   > **"When the computer has limited time, inventing new building blocks helps it solve more *new* problems, but only if those problems contain hidden repeating patterns. If the problems are random, extra blocks only slow it down, because there are more choices to try."**

3. **Your chemistry example supports changing the joining rules.** Life didn't invent new elements. It invented useful *molecules* (amino acids) and new *rules for joining them* (the genetic code). That points to the joining rules being central, not only new blocks.
4. **"More complex" isn't automatically "better".** To show a new block really helps, we need three comparison groups (we used all three):
   - a computer given **random** new blocks, to check whether *any* extra blocks help;
   - a computer secretly given **the right** blocks, to check whether our test can detect improvement at all;
   - a set of puzzles with **no hidden patterns**, where new blocks should *not* help.

---

## 4. Naming the parts precisely

To measure an idea you must name its parts precisely. Here are the parts of your idea in LEGO terms (the exact maths is in the [technical appendix](R001-technical-appendix.md)):

| Part | LEGO picture | What it is in our experiment |
|---|---|---|
| **Building blocks** (primitives) | the kinds of brick in the box | 26 basic actions: sort, reverse, add 1, keep even numbers… |
| **Fitting rules** (types) | which bricks can snap together | a "sort" action needs a list, not a single number |
| **Building rules** (grammar) | how you may stack bricks | any stack where every piece fits |
| **Habits** (search preferences) | which bricks the builder grabs first | cheaper actions are tried earlier |
| **Logbook** (archive) | a notebook of every brick ever invented, including the discarded ones | every proposed shortcut with its history |
| **Exam marker** (evaluator) | the person who marks the final exam | **fixed, and the learner can never change it.** Otherwise it could cheat by changing the marking. |

**A shortcut with slots** (an abstraction) is a pre-built chunk with gaps to fill in:
- A **data slot** takes a thing, for example "sort *this list*".
- An **action slot** takes *another action*, for example "sort, then do *[something]* to every number", where the something could be "double it" or "add 1". **Action slots change the building rules themselves**, so this is our concrete, testable version of evolving the substrate (the material the computer builds with).

**Two ways to judge a new shortcut:**
- **Shortening** asks whether it makes my *old* solutions shorter. This is what Stitch and DreamCoder do. Researchers call it "compression".
- **Measured benefit** asks whether, if I add it, I actually *solve more puzzles* in the same time.

---

## 5. How the experiment was designed

### 5.1 The puzzle world

The computer is shown example inputs and outputs and must find a recipe that turns each input into its output:

> `[3, 1, 2] → [1, 2, 3]` and `[5, 4] → [4, 5]` → the recipe is **"sort"**.

Harder puzzles need longer recipes, for example "remove the first number, then sort, then reverse".

The computer searches by trying the simplest recipes first, then building longer ones out of shorter ones that worked. Each puzzle has 6 practice examples plus **4 hidden check examples**. A recipe counts as correct only if it also works on the hidden ones. That stops lucky recipes that happen to fit the visible examples.

### 5.2 Two kinds of puzzle set

- **Patterned puzzles:** built from 6 hidden "tricks" that keep coming back, like a textbook where later chapters reuse earlier tricks. Some test puzzles combine tricks in ways the computer **never saw in practice**.
- **Random puzzles:** the same sizes, but no hidden tricks. If new building blocks are useful, they should help with patterned puzzles and *not* with random ones.

Each exam paper has about 100 practice puzzles and 60 test puzzles.

### 5.3 The students

| Student | Code name | What it does |
|---|---|---|
| **A** | C0 | Never learns. Uses only the 26 basic actions. **The comparison point.** |
| **B** | C1 | Learns only *which actions to try first*. Invents nothing. |
| **C** | C2 | Saves repeated patterns as new shortcuts, choosing by **shortening** (the usual method). |
| **C-random** | C2r | Saves **random** shortcuts. Checks whether *any* extra shortcuts help. |
| **D** | C3 | **Your full idea:** shortcuts with action slots, plus "undo any change that makes practice scores worse", plus "remove unused shortcuts". |
| **D without action slots / without removal / without undo** | C3-noHO / -noPrune / -noGate | Student D with one feature switched off, to see what each feature contributes. |
| **E** | C4 | Before keeping a shortcut, **tests it**: does it actually solve more practice puzzles? *(Added after the practice run; see 5.5.)* |
| **Cheat** | O (oracle) | Secretly given the 6 true tricks. Shows the **best a learner could hope for.** If even this student doesn't improve, the exam is broken. |

### 5.4 Fairness and honesty rules

- **Equal time.** Every student gets exactly the same number of tries (30,000 distinct results per round, 5 rounds of learning). Nobody can win by simply trying harder.
- **Unseen exams.** One "practice paper" (number 100) was used to build and fix the system. The **10 real exam papers (numbers 0–9) were not looked at** until everything was frozen. This prevents a common trap: accidentally tuning the system to the exam.
- **Success decided in advance.** Before running, I wrote down what would count as success: at least **5 points better out of 100**, and **not explainable by luck**.
- **"Not luck"** means this: we repeated the comparison on 10 different exam papers and used a standard method that reshuffles the results thousands of times (the *bootstrap*). It gives a **range** of likely true differences. If the whole range is above zero, the difference is very unlikely to be luck. If the range includes zero, we can't rule out luck.

### 5.5 What the practice run (paper 100) taught us before the real exam

| Practice paper 100 | Patterned puzzles | Random puzzles |
|---|---|---|
| A: never learns | 55 | 77 |
| B: learns what to try first | 53 | 65 |
| C: saves shortcuts | 58 | 60 |
| D: full idea | 57 | 65 |
| **Cheat** | **73** | **70** |

*(Scores are puzzles solved out of 100.)*

What we learned:
1. **The exam works.** The cheat student did much better on patterned puzzles (+18) and *worse* on random ones (−7). That's exactly right: the right blocks help where patterns exist, and extra blocks get in the way where they don't.
2. **The learners picked useless shortcuts.** They saved tiny chunks like "sort the list", which only helped with puzzles they could *already* solve. They never found the important "do [something] to every number" tricks. This is the mistake the May 2026 paper describes.
3. **Learning "what to try first" backfired.** The computer learned its habits from easy puzzles, so it stopped trying actions it rarely needed, and then failed on new puzzles that needed them.
4. **The undo rule helped somewhat**, but it also accepted changes that made no difference. That is a weakness.

Because of this practice run, I added the **cheat student** and **Student E** *before* the real exam. Then I froze everything.

---

## 6. The real results (10 unseen exam papers) 🧪

*All numbers are real runs on your MacBook, 8 November 2026. The whole experiment (10 papers × 2 puzzle types × 10 students) took about 1.5 minutes.*

### 6.1 Patterned puzzles: average score out of 100

| Student | Score | Effort used |
|---|---|---|
| A: never learns | 58.0 | normal |
| B: learns what to try first | 56.3 | normal |
| C: saves shortcuts | 56.7 | normal |
| C-random | 55.2 | normal |
| D: your full idea | 57.8 | normal |
| E: tests each shortcut first | 60.7 | **15 times more** |
| **Cheat** | **76.5** | normal |
| A with 5 times more tries | 68.2 | 5 times more |
| A with 15 times more tries | 76.3 | 15 times more |

### 6.2 The predictions we wrote down in advance

| Prediction | What happened | Range of likely true difference | Verdict |
|---|---|---|---|
| **0. Our exam can detect improvement** (Cheat beats A) | Cheat scored **18.5 more**, and won on **all 10 papers** | 15.2 to 21.8 more | ✅ **Passed** |
| **1. Saving shortcuts beats only learning habits** (C vs B) | 0.3 more | 3.8 less to 4.7 more | ❌ **Failed**: no real difference |
| **2. The core idea: your full idea beats ordinary shortcut-saving** (D vs C) | 1.2 more | 2.8 less to 4.8 more | ❌ **Failed**: could be luck |
| **3. Random shortcuts don't help** (C-random vs B) | 1.2 less | 3.2 less to 0.8 more | ✅ **Passed**, as expected |
| **4. Your idea helps more on patterned than on random puzzles** | 0.0 difference | 2.5 less to 2.8 more | ❌ **Failed** |
| **5. Testing shortcuts first beats shortening** (E vs C) | **4.0 more**, won on 9 of 10 papers | 1.0 to 6.8 more | ❌ **Officially failed**: real, but below the 5-point bar we set |

### 6.3 Extra things we noticed (not predicted in advance, so treat them as leads, not proof)

- **Action slots are the one part of your idea that showed a real signal.** D with action slots beat D without them by **3.3 points** (range 1.3 to 5.7) on patterned puzzles, winning 6 papers and losing none. On random puzzles the difference was about zero (0.3). That is exactly how a genuine effect should look: it helps only where patterns exist.
- **The undo rule protects the system.** On random puzzles, switching it off cost **4.3 points** (range 1.7 to 7.5). It blocked 47 bad change attempts.
- **Learning "what to try first" hurt:** 1.7 points worse on patterned puzzles and 4.3 worse on random ones, both clearly real. The same over-learning from easy puzzles as in the practice run.
- **"Remove unused shortcuts" never activated** (0 times), so that feature is **untested**. The cause is a design flaw: every saved shortcut is, by how it's chosen, used at least twice, so it never looks unused. Logged as open problem OI-2.
- **Exchange rate.** The right blocks were worth almost exactly 15 times more thinking time (76.5 vs 76.3). From now on this becomes a main yardstick: "this set of blocks is worth N times more search."
- **Student E wastes effort.** Given the same 15 times more effort, plain Student A scored 76.3 against E's 60.7. The idea of testing first is good; our version of it is far too costly.

### 6.4 What it all means

1. 🧪 **The prize is real.** In this puzzle world, having the right building blocks is worth about 15 times more thinking. The gap between **58 and 76.5 is our research problem**. It's concrete, measurable, and fits on a laptop.
2. 🧪 **The usual way of choosing blocks fails here.** Choosing shortcuts by "which one shortens my old solutions" picked shortcuts for puzzles the computer could already solve. It's like a student who makes beautiful notes on chapters they already know and skips the chapter they keep failing. *Caution:* we used a simplified version of Stitch and DreamCoder; the full versions might do better.
3. 💡 **Most promising next steps:**
   - choose blocks by their effect on **puzzles not yet solved**;
   - develop **action slots** further;
   - learn "what to try first" without over-learning from easy puzzles.
4. **Your core prediction is "not supported yet"; it hasn't been proven wrong.** It failed with *these* discovery methods. We keep the failure in the record, because hiding failures is how research fools itself.

### 6.5 Limits: read these before quoting any number

- **It's a toy world:** 26 actions, short lists of numbers, made-up puzzles. Nothing here automatically applies to big AI models or real software.
- **I designed the patterned puzzles myself**, so they contain the kind of patterns action slots are good at. The random puzzles and the cheat student only partly guard against that bias.
- **Our shortcut-finder is simpler than the real Stitch or DreamCoder.** A stronger one might close part of the gap.
- **Differences smaller than about 3 points are within the noise.** With 10 papers × 60 puzzles, we can't reliably see smaller effects.
- **The settings** (3 new shortcuts per round, the amount of time, and so on) were fixed in advance and not tuned. Other settings could change the picture.

---

## 7. What comes next (details in the [experiment registry](../../governance/EXPERIMENT_REGISTRY.md))

This section was rewritten on 10 November 2026. The plan as first written on 8 November is kept in git snapshot `fe5edc4`.

### 7.1 What happened to the plan of 8 November

| Planned | What happened |
|---|---|
| **EXP-002 · Looking forward, not back** (learn from near misses) | Done, **negative**. It closed −17.7% of the gap. A second variant, EXP-002b, closed −11.5% and lost to plain learning given the same doubled effort. The stop rule closed this line (D-035). |
| **EXP-003 · Better habits without over-learning** | Not run in the toy world. The same question is now asked on real code, as the "sharper habits" guesser in EXP-006. |
| **EXP-004 · Real joining-rule changes** | On hold. The toy world stopped telling us new things (D-004's condition for moving on), so effort moved to real code. |
| **EXP-005 · From puzzles to real software** | Done, **positive, read narrowly**. It was run on the *shapes of code* in three projects' histories, not on records from our product as first planned, because the product has no users yet and so no records. |

### 7.2 The plan from here

**EXP-006** is designed and not yet built ([design](EXP-006-design.md)): does a phrase book of blocks learned from a project's past let a search *find* its future code with fewer guesses? What follows depends on its result, and each branch was written down before the experiment exists:

| If EXP-006 shows… | Then the next step is… |
|---|---|
| Blocks help, by more than doubling the search would | **EXP-007:** use the library inside a search whose answers are checked by *running tests*, not by exact match. This is the first point where the research and the product (`pkv`) could meet. |
| Blocks help, but less than doubling the search | Record that more search wins again. The blocks stay a way of *describing* code. |
| Sharper habits do as well as blocks | Prefer the simpler system. The research turns from libraries of blocks to learned **guidance**: a small model, trainable on the MacBook, that suggests what to try next. |
| Blocks don't help at all | The block-library line pauses on real code as well as in the toy world, and the next pre-registration is about guidance. |

**What happened (11 November 2026, D-044):** blocks helped a little (+4.1 of 100), less than doubling the search, and sharper habits did better (+8.4). Both of the last two rows of the table above applied, so **the research turns to learned guidance.**

Two branches lead to learned guidance. That would be the project's first use of a neural network, and the natural place to start the small own-model work the founder's brief asks for.

**Not planned yet, on purpose:** the three architecture proposals in the founder's brief. They should be built on whichever branch above turns out to be true, so they're written after EXP-006.

---

## 8. How to re-run everything yourself

These commands run the research self-checks (46 tests, as of 11 November 2026), the full first experiment (about 1.5 minutes), and its analysis:

```bash
cd parinamakramam/research/pevo
uv run --python 3.14 --with pytest python -m pytest -q tests
python3 run_exp001.py --seeds 0-9 --out ../../experiments/EXP-001/results
python3 ../../experiments/EXP-001/analysis.py
```

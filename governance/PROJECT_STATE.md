# Project state: read this first

**Last updated:** 8 November 2026 · **Stage:** day 1 of the 90-day plan

This file says where everything stands right now, so anyone (you, or a new Claude session) can continue without guessing. Words are explained in the [Glossary](../docs/GLOSSARY.md). To learn all the ideas from zero, use the [course](../docs/LEARN.md).

## Done so far

**Research**
- Read and checked the earlier work by others: DreamCoder, Stitch, babble, LILO, AbstractBeam, Voyager, Probe, TheoryCoder-2, the two 2026 papers, Sakana AI's work, and the Darwin Gödel Machine. See [R001](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md), section 2.
- Gave a critique of your idea and named its parts precisely (R001, sections 3–4).
- **Experiment EXP-001** built, self-checked (11 out of 11 pass) and run. Results are in R001 section 6 and the [registry](EXPERIMENT_REGISTRY.md).

**Product**
- Chose the first product from public evidence: an independent checker for AI-written code ([P001](../docs/product/P001-first-workflow-public-evidence.md)).
- **Checker tool (`pkv`), first part built:** it reads what changed, maps which files use which, and picks the tests that could break, with a reason for each. **27 out of 27 self-checks pass.** We also tried it on our own project, which found one mistake. It's now fixed and guarded by a check. See [product/verify/README.md](../product/verify/README.md).

**Company habits**
- **Version control:** the project is saved with git. The first snapshot is `a200f19`.
- **Plain language:** every document is now in plain language, with a [Glossary](../docs/GLOSSARY.md) and a learn-from-zero [course](../docs/LEARN.md). The exact maths is in a separate [technical appendix](../docs/research/R001-technical-appendix.md).

## What's in the project

| Folder | What it holds |
|---|---|
| `research/pevo/` | The puzzle-world experiment: building blocks, search, puzzle maker, shortcut learner, 10 "students", self-checks. Plain Python. |
| `product/verify/` | The checker tool `pkv`: change reader, fingerprint, code map, test finder, command, self-checks. Uses only Python's built-in parts. |
| `experiments/EXP-001/` | All results from the first experiment, with a [guide to reading them](../experiments/EXP-001/README.md). |
| `docs/` | Research report, product report, glossary, course. |
| `governance/` | This file, the decision log, and the experiment registry. |

## What we know (our own results, in the toy puzzle world only)

- 🧪 The right building blocks are worth about **15 times more thinking time** (58 → 76.5 out of 100).
- 🧪 Our methods for *discovering* building blocks recovered almost none of that.
- 🧪 Learning "what to try first" from easy puzzles made things worse.
- 🧪 Shortcuts with action slots gave a small, real gain (+3.3), and only on patterned puzzles. This was an extra observation, not one of our advance predictions.

## Ideas still to test 💡

- Choosing building blocks by whether they help with *unsolved* puzzles closes the gap (EXP-002).
- Action slots are the useful kind of joining-rule change.
- Programmers will use, and later pay for, an independent checker (P001).

## Failed predictions (kept, never deleted)

- EXP-001 predictions 1, 2, 4 and 5 (see the registry).

## Open problems

- ~~**OI-1:** project not saved with git.~~ ✅ Fixed (snapshot `a200f19`, decision D-013).
- **OI-2:** "remove unused shortcuts" never activates, because every saved shortcut is used at least twice by design. Fix in EXP-004 by removing a shortcut if the score doesn't drop without it.
- **OI-3:** the undo rule keeps changes that make no difference. Consider requiring a real improvement, or preferring the smaller set of shortcuts when scores tie.
- **OI-4:** TRINITY's link to Sakana isn't confirmed, and the Stack Overflow numbers came from news reports. Read the original sources before quoting them publicly.
- **OI-5 (your decision):** which **licence** the checker tool is published under. The usual choices are MIT or Apache-2.0, which let anyone use it, including companies. [Course lesson 21](../docs/LEARN.md) explains the difference. It's needed before the tool goes public (around day 10).
- **OI-6:** the checker finds test files only by pytest's default naming, and can't see links made by reading data files. Both are documented. Revisit after trying it on real public projects (day 5).

## Top 5 risks

| Risk | How likely | How bad | What we do about it |
|---|---|---|---|
| AI tool makers build their own checker | High | High | Work with *every* AI tool, run inside CI, publish openly, move fast |
| Research eats all the time and the product stalls | Medium | High | Fixed weekly split (about 60% product, 40% research), plus stop rules in the registry |
| Toy-world results don't carry over to real problems | High | Medium | EXP-005 on records from real software |
| Too much for one person | High | High | The weekly plan below; automate; one product only |
| Misusing someone's code or data | Low | High | Only made-up data and public code whose licence allows it; a list of every dataset from the first one |

## Next steps, in order

1. ~~Set up git.~~ ✅
2. ~~Checker: change reader, code map, test finder.~~ ✅
3. **Checker: test runner.** Actually run the chosen tests in a separate, sealed-off process with a time limit; record the command, result and timing; record the fingerprint before and after, and mark the result *stale* if it changed.
4. **Checker: cheating detector, version 0.** Spot deleted tests, fewer assertions, new skip markers, `assert True`, changed shared test settings, and changed sensitive folders.
5. **A practice set for the checker:** 20 small made-up projects with known, planted cheating. This becomes the product's own benchmark.
6. **EXP-002 code:** invent shortcuts from near-miss attempts on unsolved puzzles. Practice paper 100 only, until the design is frozen.

## Week 1 plan (about 6 hours a day, one person)

| Day | Product (checker) | Research | Admin and learning |
|---|---|---|---|
| 1 (today) | change reader, code map, test finder ✅ | EXP-001 ✅ | git ✅; course lessons 1–4 |
| 2 | test runner + staleness check | — | lessons 5–8; check whether the name "parinamakramam" / "parinama" is free as a website and handle |
| 3 | evidence saved as a file (JSON) | — | lessons 9–12; create the free GitHub organisation |
| 4 | cheating detector, version 0 | — | lessons 13–16; **decide the licence (OI-5)** |
| 5 | readable report; try it on 3 public Python projects with planted cheating | EXP-002 design | lessons 17–20 |
| 6 | — | EXP-002 near-miss shortcut maker + self-checks | lessons 21–23 |
| 7 | review the week; update this file and the logs | EXP-002 practice run (paper 100 only) | reread R001 and P001 |

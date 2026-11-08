# Project state: read this first

**Last updated:** 8 November 2026 (evening) · **Stage:** day 1 of the 90-day plan, with the day 2–4 product work done early

This file says where everything stands right now, so anyone (you, or a new Claude session) can continue without guessing. Words are explained in the [Glossary](../docs/GLOSSARY.md). To learn all the ideas from zero, use the [course](../docs/LEARN.md) (27 lessons).

## Where the project lives

- **On this Mac:** `/Volumes/projects/hope/parinamakramam`
- **Online:** https://github.com/broly18814/parinamakramam
  - **Private**: only you can see it.
  - This project is set to always upload as `broly18814`, even though another GitHub account is the default on this Mac (decision D-015).
- **Automatic checks:** GitHub's robot runs all self-checks on every upload, on Python 3.12 and 3.14.

## Done so far

**Research**
- Read and checked earlier work by others (R001, section 2).
- Gave a critique of your idea and named its parts precisely (R001, sections 3–4).
- **Experiment EXP-001** built, self-checked (11 out of 11 pass) and run (R001 section 6; [registry](EXPERIMENT_REGISTRY.md)).

**Product: Parinama Verify (`pkv`)**, full first version ([guide](../product/verify/README.md))
- Reads what changed, fingerprints the code, maps which files use which, and picks the tests that could break, with reasons.
- **Runs the tests**: separately per sub-project, with a time limit, secrets hidden, and the fingerprint recorded before and after.
- **Cheating detector**: deleted, hidden or emptied tests; new "skip" markers; checks that can never fail; plus notices for shared settings, security files and edited expected answers.
- **Receipt** with one verdict (VERIFIED, FAILED, UNVERIFIED or SUSPICIOUS), saved as JSON and Markdown. `pkv fresh` later says whether a receipt still matches the code.
- **54 out of 54 self-checks pass.** Mutation testing confirmed the self-checks catch deliberately broken safeguards.
- **Dogfooding** (using pkv on our own project) found 5 real mistakes. All are fixed and each has a regression test.

**Company habits**
- Saved with git and uploaded to GitHub.
- Every document is in plain language, with a glossary, a course, and a technical appendix for specialists.

## What's in the project

| Folder | What it holds |
|---|---|
| `research/pevo/` | The puzzle-world experiment, with its self-checks. |
| `product/verify/` | The checker tool `pkv`, with 54 self-checks. Uses only Python's built-in parts. |
| `experiments/EXP-001/` | All results from the first experiment, with a [reading guide](../experiments/EXP-001/README.md). |
| `docs/` | Research report, product report, glossary, course. |
| `governance/` | This file, the decision log, and the experiment registry. |
| `.github/workflows/` | Instructions for GitHub's robot (runs the self-checks). |

## What we know (our own results)

- 🧪 In the toy puzzle world, the right building blocks are worth about **15 times more thinking time** (58 → 76.5 out of 100). Our methods for *discovering* them recovered almost none of that.
- 🧪 Shortcuts with action slots gave a small, real gain (+3.3), and only on patterned puzzles. This was an extra observation, not an advance prediction.
- 🧪 pkv works correctly on our own project and on all 54 planted situations. **It hasn't been tested on outside projects yet.**

## Ideas still to test 💡

- Choosing building blocks by whether they help with *unsolved* puzzles closes the gap (EXP-002).
- Programmers will use, and later pay for, an independent checker (P001).
- pkv catches most real cheating patterns. To measure this, we'll build a practice set of projects with planted cheating.

## Open problems

- ~~OI-1: no git.~~ ✅ Fixed.
- **OI-2:** "remove unused shortcuts" never activates in EXP-001 (fix in EXP-004).
- **OI-3:** the undo rule keeps changes that make no difference.
- **OI-4:** read the original TRINITY and Stack Overflow sources before quoting them publicly.
- **OI-5 (your decision):** the checker's **licence** (MIT or Apache-2.0 are the usual choices; [lesson 21](../docs/LEARN.md)). Needed before making it public.
- **OI-6:** pkv finds test files only by pytest's default names, and can't trace code that reads data files by name. Both are documented.
- **OI-7 (waiting for you):** you asked to delete every other repository in `broly18814`. Deletion is permanent, so it needs your explicit confirmation of the list, plus a permission you have to grant yourself. See the decision log entry D-018.

## Top 5 risks

| Risk | How likely | How bad | What we do about it |
|---|---|---|---|
| AI tool makers build their own checker | High | High | Work with every AI tool, run inside CI, publish openly, move fast |
| Research eats all the time and the product stalls | Medium | High | About 60% product / 40% research each week; stop rules in the registry |
| Toy-world results don't carry over | High | Medium | EXP-005 on real software records |
| Too much for one person | High | High | The weekly plan; automation; one product only |
| Misusing someone's code or data | Low | High | Only made-up data and public code whose licence allows it |

## Next steps, in order

1. **A practice set for the checker:** about 20 small made-up projects, each with one known, planted kind of cheating, plus honest changes that must *not* be flagged. Measure how many cheats pkv catches and how many false alarms it raises. This becomes the product's own benchmark.
2. **Try pkv on 3 public Python projects** whose licences allow it: plant a cheat in a copy, run pkv, and record what happens.
3. **GitHub add-on (Action):** run `pkv check` automatically on every pull request and post the receipt as a comment.
4. **EXP-002 code:** invent shortcuts from near-miss attempts on unsolved puzzles. Practice paper 100 only, until the design is frozen.

## Plan for the rest of week 1 (about 6 hours a day)

| Day | Product (checker) | Research | Admin and learning |
|---|---|---|---|
| 2 | practice set: 10 cheat types + 10 honest changes | — | lessons 1–8; check whether the name is free as a website and handle |
| 3 | run the practice set; fix what it finds; publish the score in the README | — | lessons 9–14; create a free GitHub organisation (optional) |
| 4 | try pkv on 3 public projects | — | lessons 15–20; **decide the licence (OI-5)** |
| 5 | GitHub Action, version 0 | EXP-002 design document | lessons 21–27 |
| 6 | — | EXP-002 near-miss shortcut maker + self-checks | — |
| 7 | review the week; update this file and the logs | EXP-002 practice run (paper 100 only) | reread R001 and P001 |

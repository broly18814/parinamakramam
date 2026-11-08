# Project state: read this first

**Last updated:** 8 November 2026 (night) · **Stage:** day 1 of the 90-day plan; week-1 product work and EXP-002 done early

This file says where everything stands right now, so anyone (you, or a new Claude session) can continue without guessing. Words are explained in the [Glossary](../docs/GLOSSARY.md). To learn every idea from zero, use the [course](../docs/LEARN.md) (33 lessons).

## Where the project lives

- **On this Mac:** `/Volumes/projects/hope/parinamakramam`
- **Online:** https://github.com/broly18814/parinamakramam
  - **Public** since 8 November 2026 (D-026); it's the only repository in the account.
  - Turned on: secret scanning, push protection, and private vulnerability reporting.
  - This project always uploads as `broly18814`. The Mac's default GitHub account is unchanged.
- **Backup of the 14 deleted repositories:** `/Volumes/projects/hope/github-backup-broly18814-2026-11-08` (verified; see D-020 and D-021).
- **Every upload is checked automatically:**
  - lint and strict types;
  - tests on Python 3.10, 3.12 and 3.14;
  - both practice sets as a regression gate;
  - pkv checking its own change.
- **Run the same checks locally:** `scripts/check-all.sh`.

## Done so far

### Research
- **Prior work** reviewed and a critique given ([R001](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md)).
- **EXP-001 (completed):** the right building blocks are worth about 15× more thinking, but discovering them failed. The tidied code reproduces all 200 results exactly.
- **EXP-002 (completed, negative):** learning from near misses was worse, −2.3 points vs C3, closing −17.7% of the gap. The stop rule now applies: one more variant at most ([design and results](../docs/research/EXP-002-design.md)).

### Product: Parinama Verify 0.1.0 ([guide](../product/verify/README.md))
- **Full check:**
  - picks the affected tests, with reasons;
  - runs them per sub-project, with secrets hidden;
  - fingerprints the code before and after;
  - detects 10 kinds of weakened tests, including the run-time "selected but never ran" check;
  - gives a one-verdict receipt;
  - `pkv fresh` detects stale receipts.
- **Measured on pre-registered practice sets** (all 51 predictions correct):
  - BENCH-001: 15 of 16 cheats caught, 0 of 12 false alarms;
  - **BENCH-002 (held out): 10 of 13 caught, 1 of 10 false alarms.**
- **GitHub Action:** `product/verify/action.yml`. This repository uses it on itself.
- **Quality:**
  - 70 product self-checks and 16 research self-checks;
  - `mypy --strict` clean;
  - mutation-tested detection rules;
  - two real bugs found and fixed with regression tests: the "racy git" fingerprint bug, and a crash.

### Company habits
- **Standard project files:** [CHANGELOG](../CHANGELOG.md), [SECURITY](../SECURITY.md), [CONTRIBUTING](../CONTRIBUTING.md).
- **Versioning:** Semantic Versioning.
- **Pre-registration:** every experiment and benchmark is pre-registered and committed before it runs.
- **Plain language:** all documents, with a glossary, a course, and a technical appendix for specialists.
- **Git history:** shows only the founder as author.
- **Licence:** Apache License 2.0 ([LICENSE](../LICENSE), decision D-025). This closes open problem OI-5.

## What we know (our own results)

- 🧪 In the toy puzzle world, the right building blocks are worth about 15× more search. **Neither** backward-looking (EXP-001) **nor** near-miss (EXP-002) discovery captures that value.
- 🧪 On its practice sets, pkv catches most planted cheats with few false alarms, and its improvements generalised to a held-out set. **It hasn't been tested on real outside projects yet.**

## Ideas still to test 💡

- A near-miss variant chosen by *structure* (for example "one more search step reaches the target") instead of output similarity: the last allowed variant.
- Building blocks from real engineering records (EXP-005).
- Programmers will use, and later pay for, an independent checker (P001).

## Open problems

- **OI-2:** "remove unused shortcuts" never activates (fix planned in EXP-004).
- **OI-3:** the undo rule keeps changes that make no difference.
- **OI-4:** read the original TRINITY and Stack Overflow sources before quoting them publicly.
- **OI-6:** pkv finds tests by pytest's default naming only, and can't trace code that reads data files by name.
- **OI-8:** known pkv misses: an expected answer edited to match a bug; `pytest.raises(AssertionError)`; a skip mark on one table row; an early `return`. Known false alarm: a test file split in two. Each needs a fresh held-out set (BENCH-003) before it's addressed.
- **OI-9:** the near-miss scan costs 11× CPU in pure Python. It matters only if the near-miss line continues.

## Top 5 risks

| Risk | How likely | How bad | What we do about it |
|---|---|---|---|
| AI tool makers build their own checker | High | High | Work with every AI tool, run inside CI, publish openly, move fast |
| Research eats all the time | Medium | High | Stop rules (EXP-002's is now active); about 60% product / 40% research |
| Toy-world results don't carry over | High | Medium | EXP-005 on real engineering records |
| Practice-set scores flatter pkv | Medium | High | Held-out sets; next, measure on real public projects |
| Too much for one person | High | High | Automation (CI, check-all script); one product only |

## Next steps, in order

1. **Real-world evidence for pkv.** Run it, read-only and in a sandboxed copy, on a few public Python projects whose licences allow it, and record what it finds. (Downloading those projects needs your go-ahead.)
2. **BENCH-003:** a fresh held-out set *before* tackling the known misses in OI-8.
3. **EXP-002b:** the one remaining near-miss variant, pre-registered (structure-based). If it closes < 10% of the gap, stop and move to EXP-005.
4. **Publish more widely:** tag a first release (`pkv-v0.1.0`), and decide how to reach GitHub's Marketplace, which needs `action.yml` at the top of a repository (either a small separate repository for the action, or moving the file). Then watch install counts (no interviews; D-002).

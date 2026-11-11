# Project state: read this first

**Last updated:** 11 November 2026 · **Stage:** day 4 of the [90-day roadmap](ROADMAP.md). Days 1–55 are done; days 56–70 are mostly done; days 71–90 wait for real users.

This file says where everything stands right now, so anyone (you, or a new Claude session) can continue without guessing. Words are explained in the [Glossary](../docs/GLOSSARY.md). To learn every idea from zero, use the [course](../docs/LEARN.md) (38 lessons).

## Where the project lives

- **On this Mac:** `/Volumes/projects/hope/parinamakramam`. Restored from GitHub on 10 November 2026 after the folder was found empty; every check passed on the restored copy (D-038).
- **Online:** https://github.com/broly18814/parinamakramam
  - **Public** since 8 November 2026 (D-026); it's the only repository in the account.
  - Turned on: secret scanning, push protection, and private vulnerability reporting.
  - This project always uploads as `broly18814`. The Mac's default GitHub account is unchanged.
- **Backup of the 14 deleted repositories: missing.** It was at `/Volumes/projects/hope/github-backup-broly18814-2026-11-08` (D-020, D-021) and was never uploaded anywhere. On 10 November 2026 that folder was gone, deleted through the Trash (D-038, D-041, open problem OI-15).
- **Study copies of other people's projects** (read-only, never uploaded): `/Volumes/projects/hope/work/exp006/src`.
- **Every upload is checked automatically:**
  - lint and strict types;
  - tests on Python 3.10, 3.11, 3.12, 3.13 and 3.14;
  - both practice sets as a regression gate;
  - pkv checking its own change.
- **Run the same checks locally:** `scripts/check-all.sh`.

## Done so far

### Research
- **Prior work** reviewed and a critique given ([R001](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md)).
- **EXP-006 (completed; stop rule applies, D-044):** the phrase book made search a little cheaper (+4.1 of 100), but no more than doubling the search, and sharper habits with no phrase book did better (+8.4). The question was: does a phrase book of blocks learned from a project's past let a search *find* its future code with fewer guesses? Tested on three projects nobody here has analysed (packaging, urllib3, httpx), against double the search and against sharper habits with no blocks ([design](../docs/research/EXP-006-design.md), D-039).
- **EXP-001 (completed):** the right building blocks are worth about 15× more thinking, but discovering them failed. The tidied code reproduces all 200 results exactly.
- **EXP-005 (completed, positive):** building blocks learned from real projects' past code compress their future code by 13.5%, against 1.9% for random fragments; 60% of the best possible. They're mostly general Python idioms, plus a small (+1.9-point) project-specific layer ([design and results](../docs/research/EXP-005-design.md)).
- **EXP-002b (completed, negative):** near misses chosen by structure closed −11.5% of the gap and lost to plain learning given the same doubled effort. **The near-miss line is closed (D-035)**; research moves to EXP-005.
- **EXP-002 (completed, negative):** learning from near misses was worse, −2.3 points vs C3, closing −17.7% of the gap. The stop rule now applies: one more variant at most ([design and results](../docs/research/EXP-002-design.md)).

### Product: Parinama Verify 0.2.1 ([guide](../product/verify/README.md))
- **Full check:**
  - picks the affected tests, with reasons;
  - runs them per sub-project, with secrets hidden;
  - fingerprints the code before and after;
  - detects 10 kinds of weakened tests, including the run-time "selected but never ran" check;
  - gives a one-verdict receipt;
  - `pkv fresh` detects stale receipts.
- **Measured on pre-registered practice sets** (every prediction correct; figures for 0.2.0, unchanged in 0.2.1):
  - BENCH-001: 15 of 16 cheats caught, 0 of 12 false alarms;
  - **BENCH-002 (held out): 10 of 13 caught, 0 of 10 false alarms** (0.1.0 had 1, a split test file);
  - BENCH-003 (cheats disguised as moved tests): 12 of 12 caught, 1 of 10 false alarms.
- **GitHub Action:** `product/verify/action.yml`. This repository uses it on itself.
- **The Action's own public repository** (D-045, D-046): [broly18814/parinama-verify-action](https://github.com/broly18814/parinama-verify-action), tag `v0.2.1` (commit `57ada48`). It downloads pkv 0.2.1 from PyPI and checks its fingerprint. The robot tests both the copy here and the published one on every upload. **Listed on GitHub's Marketplace** since 11 November 2026 ([Parinama Verify](https://github.com/marketplace/actions/parinama-verify); categories Testing and Continuous integration; D-047).
- **Releases:** `pkv-v0.2.0` (D-030), then `pkv-v0.2.1`, the first on PyPI (`pip install parinama-verify`), each with the wheel, the source archive and checksums.
- **Quality:**
  - 107 product self-checks and 47 research self-checks;
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

## The research idea as it now stands (D-042)

> With limited effort, new building blocks help when the problems contain recurring structure **and** the blocks are learned from a richer source of information than the system's own earlier attempts. Whether a library of blocks then does better than sharper habits over the original blocks is open. 💡 A hypothesis; EXP-006 tests the open part.

**Answered on 11 November 2026 for EXP-006's setting (D-044):** a library of blocks did not beat sharper habits; it gained no more than doubling the search would.

What each result leads to next is written down in advance: [R001, section 7.2](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md).

## What we know (our own results)

- 🧪 In the toy puzzle world, the right building blocks are worth about 15× more search. **None** of backward-looking (EXP-001), output-similar near-miss (EXP-002) or structure-based near-miss (EXP-002b) discovery captures that value. At equal effort, more plain search (C3_2x) beat them all.
- 🧪 **On real code (EXP-005), learning from history works:** a project's past predicts the *shapes* of its future code (13.5% shorter vs 1.9% for chance). Most of it is general Python, so whether it helps a computer *write* code is untested (EXP-006).
- 🧪 On its practice sets, pkv catches most planted cheats with few false alarms, and its improvements generalised to a held-out set.
- 🧪 **On 120 real commits (REAL-001 study set), pkv 0.1.1 had false alarms on 38.** Four of the five causes are fixed in 0.1.2. **On 120 unseen commits (held-out), pkv 0.1.2 had false alarms on 4 (3%)**, all from renamed or moved tests; 0.1.1's rules give 12 on the same commits. No crashes and no selection misses. This holds on four small, well-maintained libraries only.

## Ideas still to test 💡

- **Better guidance beats more blocks** (from EXP-006): how much further can a better guesser go at equal effort? The next pre-registration (D-044).
- Programmers will use, and later pay for, an independent checker (P001).

## Open problems

- **OI-15:** the local backup of the 14 deleted repositories is gone for good: the disk's change log shows the folder was put in the Trash and deleted from it on 10 November (D-041). **GitHub can still restore the 14 repositories until about 6 February 2027** (Settings → Repositories → Deleted repositories); that is the founder's step. The two bundles of this project's pre-rewrite history can't be recovered.
- **OI-2:** "remove unused shortcuts" never activates (fix planned in EXP-004).
- **OI-3:** the undo rule keeps changes that make no difference.
- **OI-4:** read the original TRINITY and Stack Overflow sources before quoting them publicly.
- **OI-6:** pkv finds tests by pytest's default naming only, and can't trace code that reads data files by name.
- **OI-14:** pkv's Python module is called `pkv`, the same as an unrelated PyPI package (`pkv`, a key-value store). The two can't be installed together. Renaming the module would break existing use, so it waits for a 1.0 decision.
- **OI-13:** more equivalent check spellings for the move rule (for example `assertIsInstance` and `assert isinstance`). Found on seen data, so they need a fresh held-out set with real moves before they're added (D-029).
- **OI-11:** a cheap whole-suite load check (`pytest --collect-only`), so a receipt can say when test files outside the selection can't even load. Found in REAL-001's held-out set (tomli #58).
- **OI-12:** replay studies should install the test tools each commit was written for. In REAL-001, 25 old commits failed only because of today's pytest or a missing old test package.
- **OI-10:** finer test selection for libraries: follow `from package import name` to the module that defines `name`, so a change to one module doesn't select every test. REAL-001 measured a median of 100% of test files selected in three of four projects.
- **OI-8:** known pkv misses: an expected answer edited to match a bug; `pytest.raises(AssertionError)`; a skip mark on one table row; an early `return`. Known false alarms: tests merged into a table, or generalised while renamed (D4 handles plain moves since 0.2.0). Each needs a fresh held-out set (BENCH-004) before it's addressed.
- **OI-9:** the near-miss scan costs 11× CPU in pure Python. It matters only if the near-miss line continues.

## Top 5 risks

| Risk | How likely | How bad | What we do about it |
|---|---|---|---|
| AI tool makers build their own checker | High | High | Work with every AI tool, run inside CI, publish openly, move fast |
| Research eats all the time | Medium | High | Stop rules (EXP-002's is now active); about 60% product / 40% research |
| Toy-world results don't carry over | High | Medium | EXP-005 on real engineering records |
| Practice-set scores flatter pkv | Medium | High | Held-out sets; next, measure on real public projects |
| Too much for one person | High | High | Automation (CI, check-all script); one product only |

## The founder's brief: what is still unwritten

The founder restated the full brief on 10 November 2026. Checked against it, these deliverables don't exist yet as documents. They're listed in the order recommended for writing them.

| Deliverable in the brief | Status | Why this order |
|---|---|---|
| 18. Grants, compute credits and incubators in India | ✅ written: [F001](../docs/business/F001-grants-compute-and-incubators-india.md) (11 Nov) | Re-read every three months; deadlines and rules change. |
| 14. Own-model roadmap for the MacBook | not started | A small baseline model can be trained on this Mac at no cost, and later architecture work needs that baseline. |
| 8. Three discovery algorithms, compared in writing | partly | Four have been *tested* (EXP-001, 002, 002b, 005) but never set side by side with pseudocode and costs. |
| 9 and 11. Three architecture proposals, and how blocks could shape an architecture | not started | Better written after EXP-006, so they build on evidence about whether blocks help search at all. |
| 15. Languages: English, Telugu, Hindi | not started | Needs dataset licences checked one by one. |
| 12. An automated research assistant | not started | The manual version (pre-register, run, analyse, self-check) is the specification; automate it once it has stopped changing. |
| 3 and 16. Full competitor and pricing table; three-part business model | partly | P001 covers the checker's competitors and a first view of earning. Prices should be re-read from official pages at the time a paid offer is designed (D-010). |
| 7. The full engine design document | partly | `research/pevo` implements a first version; the formal definitions are in R001's appendix. |

Done and current: 1 and 19 to 21 (strategy and plans, in the roadmap and decision log), 2 (P001), 4 to 6 (R001 and its appendix), 10 (EXP-001), 13 (pkv), 17 (ADOPTION.md).

## Next steps, in order

1. **Founder: decide whether to restore the 14 deleted repositories on GitHub** while its 90-day window is open (OI-15, D-041). If they're restored, keep the new backup in **two** places.
2. **Research: pre-register the guidance experiment** (D-044). Start from EXP-006's machinery, which is built and tested; compare guessers that use more context against each other at equal effort, on rich and pyparsing (untouched so far), with NONE and CTX2 as the baselines to beat. A small neural guesser trainable on the MacBook is the natural strong condition.
3. **BENCH-004:** a fresh held-out set, written *before* tackling the remaining known misses in OI-8 (`pytest.raises(AssertionError)`, a skip on one table row, an early `return`) and the extra move spellings in OI-13.
4. **Watch adoption weekly, with no interviews (D-002).** Reading of 10 November: no real use yet ([ADOPTION.md](ADOPTION.md)). Next reading: 17 November.
5. **Watch whether the Marketplace listing brings anyone** (D-047): add the action repository's traffic and the listing to the weekly adoption reading.
6. **Funding, as individuals first ([F001](../docs/business/F001-grants-compute-and-incubators-india.md)):** draft applications to Emergent Ventures India, then the Transformative AI Fund, for the founder to read and submit. Registering a company is deferred until pkv has real users; that is the founder's decision.
7. **The unwritten deliverables above**, next the own-model roadmap (14).

# The 90-day roadmap: plan and status

The roadmap from the founder's original brief, copied as written, with the status of every item. Day 1 was **8 November 2026**. Last updated: **10 November 2026 (day 3)**.

Status marks:
- ✅ done;
- 🟡 partly done;
- ⏳ not started yet;
- ↪️ replaced by a recorded decision.

> **The big picture.** The product and research work of days 1–55 is done, well ahead of schedule. Of days 56–70, the alpha is published and the major failures were improved; the demonstration and the feedback route are done today. Measuring usage has started, but there are no users yet. Days 71–90 (commercial validation) haven't started, and **can't usefully start until real people use pkv**. Time can't speed that up: it's the one thing no amount of work today can replace.

## Days 1–10: Research foundation

| Item | Status | Where |
|---|---|---|
| Establish project identity | ✅ | Name, licence (D-001, D-025) |
| Check company and domain names | 🟡 | All candidate domains (`parinamakramam.com`, `.ai`, `.in`, `.dev`, `.org`) look unregistered as of 9 Nov 2026. **Buying one costs money: the founder's decision** (D-010). No trademark search yet. |
| Create a GitHub organisation | ↪️ / 🟡 | The project lives at `broly18814/parinamakramam` (D-015). The organisation name `parinamakramam` is free. **Creating it is the founder's step.** |
| Research competitors | ✅ | [P001](../docs/product/P001-first-workflow-public-evidence.md) |
| Analyse public user complaints and issues | ✅ | P001 |
| Define the first product workflow | ✅ | P001, and D-009 (an independent checker, not a coding assistant) |
| Study primitive-evolution prior art | ✅ | [R001](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md) |
| Study Sakana AI | ✅ | R001 |
| Define first research experiment | ✅ | EXP-001 in the [registry](EXPERIMENT_REGISTRY.md) |
| Prepare Mac environment | ✅ | `scripts/check-all.sh` runs everything locally |
| Create project documentation | ✅ | README, glossary, 38-lesson course, decision log |
| **Deliverables:** product specification, research map, **technical architecture**, experiment specification, development environment | ✅ | The architecture document was added on day 2: [ARCHITECTURE.md](../docs/ARCHITECTURE.md) |

## Days 11–25: Product prototype

The brief's list (repository search, file retrieval, code explanation, repository questions, reviewable code changes, extension interface) describes a **coding assistant**. Decision **D-009** chose an **independent checker** instead: the public evidence for it was stronger, and the big AI companies already build assistants. The equivalent prototype work is done:

| Item (as replaced by D-009) | Status |
|---|---|
| Read a repository and its changes (git, import graph) | ✅ |
| Select the affected tests, with reasons | ✅ |
| Usable local prototype (`pkv affected`, `pkv check`) | ✅ |
| The assistant features themselves | ↪️ not planned (D-009) |

## Days 26–40: Verification

| Item | Status |
|---|---|
| Git integration | ✅ |
| Approved command execution | ✅ pkv runs only pytest, with secrets hidden |
| Test execution | ✅ |
| Real output display | ✅ the receipt, Markdown and JSON |
| Error handling | ✅ four verdicts, plus exit code 2 for pkv's own errors |
| Rollback | ↪️ not applicable: pkv never changes code. Its version of this guarantee is the before/after fingerprint plus `pkv fresh`. |
| Benchmark tasks | ✅ BENCH-001, -002 and -003, and REAL-001/002 on 360 real commits |
| **Deliverable:** a verifiable coding workflow | ✅ pkv 0.2.1, plus the GitHub Action |

## Days 41–55: Primitive research

| Item | Status |
|---|---|
| Primitive registry, fixed-library and composition-only baselines | ✅ `research/pevo` |
| Primitive discovery and candidate evaluation | ✅ EXP-001 and EXP-002, both recorded as **negative results** |
| Basic library evolution | ✅ |
| **Deliverable:** a runnable research prototype and comparative experiment | ✅ EXP-001 (200 runs, reproducible) |

## Days 56–70: Alpha and research improvement

| Item | Status |
|---|---|
| Publish an alpha | ✅ PyPI `parinama-verify` 0.2.1 ("Alpha"), GitHub releases, the Action |
| Collect voluntary feedback | ✅ issue templates for false alarms, missed cheats and bugs, plus private security reports. **No interviews** (D-002). |
| Measure product usage | 🟡 public counters only ([ADOPTION.md](ADOPTION.md)). Second reading on 10 November: still no real users. |
| Publish a demonstration | ✅ [DEMO.md](../docs/product/DEMO.md), a two-minute reproducible script |
| Improve major failures | ✅ REAL-001: false alarms down from 38 to 4 per 120 real commits |
| Run primitive-evolution ablations | ✅ EXP-001's ablations, plus EXP-002b with a compute-matched control (C3_2x). Negative: the near-miss line is closed by the stop rule (D-035). |
| **Deliverable:** public product evidence and experimental results | 🟡 The experimental results are public. *Product* evidence (other people using it) doesn't exist yet. |

## Days 71–90: Commercial validation

| Item | Status | Why not yet |
|---|---|---|
| Test self-service paid offers | ⏳ | Needs users first. D-010 says no payment systems before there's something people use. |
| Measure activation and retention | ⏳ | The method is defined in ADOPTION.md. It needs users. |
| Measure cost per task | ⏳ | Easy to do: pkv costs ₹0 per check on the user's machine. To be written down with the first users. |
| Improve the product | ⏳ (continuous) | |
| Run the first architecture experiment | ⏳ | EXP-006 comes first (D-037, D-039) |
| Investigate compute opportunities | ✅ | [F001](../docs/business/F001-grants-compute-and-incubators-india.md) (11 Nov): free notebooks and TPU Research Cloud now; cloud credits after a company exists |
| Prepare the next proprietary-model experiment | ⏳ | |

## The next items, in the roadmap's order

1. **Founder decisions:** buy a domain, create the GitHub organisation, enable GitHub Discussions. Each is a click or a purchase only the founder can make.
2. **Research:** EXP-002b is done (negative; the near-miss line is closed). **EXP-005 is done (positive):** building blocks learned from real projects' history describe their future code 13.5% more compactly. **EXP-006 is designed** (D-039): does that make search cheaper? Next: commit the design, then build and calibrate it on tomli.
3. **Days 56–70, product:** watch adoption weekly, and fix whatever real users report, starting with each held-out set (BENCH-004).
4. **Days 71–90:** start once there are real users. Until then, keep the product free and improving.

## The research plan from here (added 10 November 2026)

The 90-day list above names "primitive research" only in general terms. After five experiments the plan is specific. Full reasoning: [R001, sections 2.4 and 7](../docs/research/R001-primitive-evolution-prior-art-and-thesis.md).

| Step | What it is | Depends on |
|---|---|---|
| **EXP-006** ✅ | Do blocks learned from a project's past let a search find its future code with fewer guesses? **Done (D-044): a little, no more than doubling the search; sharper habits did better.** | — |
| ~~EXP-007~~ | The same blocks, in a search judged by running tests | **Closed unrun:** the double-search control failed |
| **next: learned guidance** | A better guesser of what to try next, from wider context up to a small model trained on the MacBook. The project's first neural network, and the start of the own-model work. | **Triggered** by EXP-006 (D-044); needs its own pre-registration |
| **Architecture proposals** (the brief's deliverables 9 and 11) | Three candidate designs, written on top of whichever branch holds | EXP-006's result |

## The brief's first year, checked against the evidence so far

| Year-1 goal in the founder's brief | Status on day 4 (11 Nov) |
|---|---|
| A working software-engineering product | ✅ pkv 0.2.1, public |
| Repeat usage; early paying customers "if validation succeeds" | ⏳ no users yet; nothing to validate |
| Self-service distribution | ✅ PyPI, and the GitHub Action in its own public repository (D-045, D-046); 🟡 the Marketplace listing waits for the founder's one-time step on GitHub |
| Primitive discovery prototype; compositional library learning | ✅ built and tested; the toy-world results were negative, the real-code result positive |
| Small proprietary models; architecture baselines | ⏳ not started; the first one follows from EXP-006 (see above) |
| Early research automation | 🟡 by hand, with scripts and self-checks; not automated |
| English, Telugu and Hindi experiments | ⏳ not started |

Years 2 and 3 stay as written in the brief. Nothing measured so far bears on them.


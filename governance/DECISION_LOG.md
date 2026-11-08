# Decision log

Append-only. Never edit a past entry; supersede it with a new one.
*In plain words: a diary of every important choice, why we made it, and what would make us change our mind.*

| ID | Date | Decision | Why | Revisit if |
|---|---|---|---|---|
| D-001 | 2026-11-08 | Company/project name: **Parinamakramam** (పరిణామక్రమం, "course of evolution") | Founder's choice | Trademark/domain check fails |
| D-002 | 2026-11-08 | No interviews, ever. Validate with public evidence and self-service signals only | Founder constraint (non-negotiable) | Never |
| D-003 | 2026-11-08 | Refine the thesis from "substrate evolution is *necessary*" to "under a fixed budget, substrate change helps **iff** the task distribution has latent reusable structure" (R001 §2) | Finite alphabets with recursion are already universal; necessity is false. Cost/efficiency is the testable claim | — |
| D-004 | 2026-11-08 | First experiment uses a typed list-DSL with Probe-style bottom-up search, pure Python, no GPU | Fits ₹0 and the M4; well studied (DreamCoder/AbstractBeam domain); runs in minutes | Results stop being informative → move to EXP-005 (engineering traces) |
| D-005 | 2026-11-08 | Search budget = number of distinct values admitted, identical across conditions | Hardware-independent and fair; stops "trying harder" from passing as "learning better" | — |
| D-006 | 2026-11-08 | Seed 100 is the calibration seed; seeds 0–9 are evaluation seeds and must not be inspected before the frozen run | Prevents tuning to the test (benchmark gaming) | — |
| D-007 | 2026-11-08 | After the calibration pilot: (a) add the **oracle** positive control and (b) add **C4** (accept a primitive only if it measurably increases training-task solves). Freeze the design; then run seeds 0–9 | The pilot showed MDL learners pick "leaf" shortcuts; without an oracle we could not tell a broken benchmark from a broken learner | — |
| D-008 | 2026-11-08 | EXP-001 core hypothesis H2 **not supported**; record it as a negative result. Next work targets *discovery* (EXP-002), not the benchmark | Oracle +18.5 pp proves the benchmark is sensitive; learners recover ≈ 0 of it | EXP-002 fails too → reconsider the domain or the thesis framing |
| D-009 | 2026-11-08 | First commercial wedge: **independent verification of AI-authored changes** for Python/pytest/GitHub (P001), not a general coding assistant | Strongest public evidence-to-competition ratio; no inference cost (₹0-compatible); feeds research traces | A major vendor ships an equivalent agent-agnostic verifier, or adoption signals are weak after the alpha |
| D-010 | 2026-11-08 | No incorporation, payments infrastructure, or paid tools yet | Nothing to sell yet; no cost justified | First paid offer is ready (≈ day 60–70) |
| D-011 | 2026-11-08 | Use plain-language explanations in all docs ("In plain words" boxes) | Founder request | — |

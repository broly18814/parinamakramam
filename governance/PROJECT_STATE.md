# Project state — read this first in any new session

**Last updated:** 2026-11-08 · **Phase:** Day 1 of the 90-day plan

## Completed
- Prior-art research, verified against primary sources (R001 §1): Momennejad & Raileanu 2026, DreamCoder, Stitch, babble, LILO, AbstractBeam, Voyager, Probe, Prospective Compression 2026, TheoryCoder-2; Sakana: model-merging recipes (Nat. Mach. Intell. 2025), CycleQD, M2N2, AI Scientist v1/v2, TRINITY (affiliation unverified); adjacent: Darwin Gödel Machine.
- Thesis critique and formal definitions (R001 §2–3).
- EXP-001 built, tested (11/11) and run (R001 §5–6, EXPERIMENT_REGISTRY).
- Commercial wedge chosen from public evidence (P001).

## Current implementation
- `research/pevo/` — DSL, bottom-up enumerator, task generators, library learning, 10 conditions, runner, tests. Pure Python 3.14, no dependencies except pytest.

## Confirmed facts (ours, toy domain)
- Oracle primitives: +18.5 pp held-out ≈ 15× search budget.
- MDL-based library growth and our substrate changes: no significant gain.
- Learned unigram grammar weights hurt (−1.7 / −4.3 pp).

## Open hypotheses
- Prospective / search-benefit selection closes the gap (EXP-002).
- Function-typed slots are the useful substrate change (+3.3 pp exploratory).
- Independent verification of AI changes is a payable need (P001).

## Failed experiments
- EXP-001 H1, H2, H4, H5 (see registry). Kept.

## Open issues
- **OI-1:** the project is not under git. Run `git init` and make a first commit so experiments can cite commit hashes instead of file hashes.
- **OI-2:** C3 deprecation never fires (abstractions are used ≥ 2 times by construction). Replace it with ablation-based pruning (EXP-004).
- **OI-3:** the validation gate accepts ties; consider requiring strict improvement or a tie-break by library size.
- **OI-4:** TRINITY's affiliation is unverified; the Stack Overflow numbers came via secondary sources, so read the primary report before quoting them publicly.

## Risk register (top 5)
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Agent vendors build native verification | High | High | Be agent-agnostic and CI-enforced; ship fast; open source |
| Research burns time with no product progress | Medium | High | Fixed weekly split (≈ 60% product / 40% research); stop conditions in the registry |
| Toy results don't transfer | High | Medium | EXP-005 on real engineering traces |
| Solo-founder overload | High | High | Weekly plan below; automate; one workflow only |
| Licence/data misuse | Low | High | Synthetic and permissively licensed data only; dataset registry from the first dataset |

## Next exact actions
1. `git init` the project and commit (OI-1).
2. Create the `pkv` (Parinama Verify) package skeleton under `product/verify/`: diff model + import-graph affected-test selection + a subprocess runner with tree-hash staleness check. Tests first.
3. Build a synthetic tamper corpus (20 small repos × known tampering types) as the product's first benchmark.
4. Draft EXP-002 code: near-miss candidate generation (closest enumerated values to unsolved targets).

## Week 1 plan (≈ 6 h/day, one person)
| Day | Product (Verify) | Research | Admin |
|---|---|---|---|
| 1 (today) | — | EXP-001 ✅ | git init; read R001/P001 |
| 2 | diff model + import graph + tests | — | check domain/handle availability for "parinamakramam" / "parinama" |
| 3 | pytest runner, staleness check, JSON evidence | — | create the GitHub org (free) |
| 4 | tamper detectors v0 (removed tests, asserts, skip/xfail) | — | — |
| 5 | Markdown report; run on 3 public Python repos with a planted tamper | EXP-002 design doc | — |
| 6 | — | EXP-002 near-miss generator + tests | — |
| 7 | review week; update this file and the logs | run EXP-002 calibration (seed 100 only) | — |

# TAMPER-BENCH: the seal and the predictions (committed before the held-out run)

**Sealed on 12 November 2026**, before any detector, including pkv, was run on any held-out case.

## The seal

The held-out set is one file, kept on the founder's Mac and **not** uploaded until after the run:

| File | Cases | SHA-256 |
|---|---|---|
| `private/tamper-bench-heldout/heldout.py` | 61 (41 tampered, 20 honest) | `150155faf41f867f3b962825d2ad8eb94f771d99523b72944a968acf1b28d30c` |

- **What sealing means.** After the run, the file is published, and anyone can check its SHA-256 against this line. If even one character had changed after today, the fingerprint wouldn't match.
- **Other files it depends on:** `tamperbench/case.py`, `projects.py` and `bugs.py`, the case builder and label check. These are committed in the same snapshot as this file, so they're fixed too.
- **Labels:** every held-out label was confirmed by running it (`python -m tamperbench.validate`):
  - each tampered case hides a real bug: the original tests, plus a probe where needed, fail on the changed code;
  - each honest case doesn't, except the documented behaviour changes (H4).
- **Make-up of the held-out set:**
  - 24 of 61 cases (39%) come from outside sources: Skylos's 9 published self-test cases, 10 goodhart rules, 3 rival README examples, and 2 ImpossibleBench behaviours. The design requires at least a third.
  - 37 are ours.
  - Across both sets, every tampered category has at least 5 cases.

**Rule for anyone working on pkv:** don't open the held-out file before the run. The development set (`tamperbench/dev.py`, public) is for building.

## The detectors and their verdict rules

These are fixed in [`tamperbench/detectors.py`](tamperbench/detectors.py) in this same snapshot. In each case the primary score is the tool's *blocking* verdict, and any finding counts as a warning, reported beside it:

| Detector | Version | Licence | Blocking rule |
|---|---|---|---|
| pkv (ours) | 0.2.1 | Apache-2.0 | verdict ≠ VERIFIED |
| pkv + A2 (ours, `--mutate`) | 0.2.1+a2 | Apache-2.0 | verdict ≠ VERIFIED. Added on 12 November 2026 after the seal: this is the "pkv 0.3 with A2" of H-TB3, built and tuned **on the development set only** (two rounds, [A2 design](../../docs/product/A2-design.md)). It's frozen for the held-out run |
| Skylos | 5.6.0 | Apache-2.0 | `Verdict: FAIL` |
| tamperguard | 0.2.0 | MIT | exit code 2 |
| tampercheck | 0.1.1 | Apache-2.0 | exit code 1, at its default severity (high) |
| checkwash | 0.12.0 | Apache-2.0 | `verdict=block` |
| testwall | 1.0.1 | MIT | `testwall verify` after `init` at the base doesn't print "PASS All … verified" |
| dunnit | 0.3.0 | MIT | `verdict: FAIL` after `dunnit init` at the base |
| goodhart | commit `4ec997e` (no package-index release) | MIT | a finding of severity `error` (its default `--fail-on` level). **Added on 12 November 2026, after the seal** but before any held-out run, once the founder allowed running it ("Yes, run them") |

## Predictions (fixed now)

Rates are on the held-out set, using blocking verdicts.
- **"Semantic"** means T4–T7: the test still looks real but checks less (loosened, expected value edited, replaced by a weaker test, or made unable to fail).
- **"Removal"** means T1–T3: deleted, skipped, or assertion removed.

| ID | Prediction | Passes if | Fails if |
|---|---|---|---|
| **H-TB1** | pkv 0.2.1 is good at removal and poor at semantic weakening | pkv's removal recall ≥ 70% **and** its semantic recall ≤ 50% | either side misses |
| **H-TB2** | No detector handles semantic weakening well without false alarms | no detector has semantic recall ≥ 80% with false alarms ≤ 10% | some detector does (then that tool, not pkv, is the one to beat, and we say so) |
| **H-TB3** | pkv 0.3, with the A2 mutation check, closes the semantic gap | semantic recall ≥ pkv 0.2.1's + 25 points, **and** false alarms ≤ pkv 0.2.1's + 5 points | either misses. **A2's stop rule:** the mutation check isn't presented as an advantage, and Track A rethinks its differentiator before the launch |
| **H-TB4** (our fidelity check) | Our re-creation of Skylos's self-test reproduces its published result | Skylos 5.6.0 blocks exactly cases X01–X06 and lets X07–X09 through. Skylos's report was for version 4.49.0, so a newer version catching more counts as a version change, not a failure | otherwise: our re-creation differs from theirs, and that's reported next to every Skylos score |

**Disclosure:**
- pkv 0.2.1 was run on the **development** set only, before these predictions were written. It caught 13 of 20 cheats, 4 of 9 semantic ones, with 2 false alarms in 10 honest changes ([results/dev/RESULTS.md](results/dev/RESULTS.md)).
- The rival tools were each tried on **two development cases only** (D01 and D21), to learn how to run them and to write the rules above.
- No tool has seen a held-out case.

## When it runs

1. **The founder allowed running the rival tools on 12 November 2026** ("Yes, run them"). They were run on the **development set** that day ([results/dev/RESULTS.md](results/dev/RESULTS.md)).
2. **Why the held-out run waits:** publishing the held-out cases after the run would let them be seen before pkv 0.3 (with A2) is built, which would spoil H-TB3. So the held-out run happens **once, after A2 is built**, in plan v2's weeks 5–6, with pkv 0.2.1, pkv 0.3 (with A2) and every rival together. The two pkv versions are scored separately, and 0.2.1's score is never replaced.
3. After the run, the held-out file and all results are published, and the run is recorded in the [experiment registry](../../governance/EXPERIMENT_REGISTRY.md).

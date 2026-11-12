# TAMPER-BENCH: a fair public test of tools that catch weakened tests

**Plan v2, Track A, step A1** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 3). It replaces BENCH-004 (D-049).
**Status:** built and sealed, 12 November 2026. The code is in [`benchmarks/tamper-bench/`](../../benchmarks/tamper-bench/): 30 public development cases and 61 sealed held-out cases, every label confirmed by running it. The fingerprint, the verdict rules and the predictions are in [SEAL.md](../../benchmarks/tamper-bench/SEAL.md), all committed **before** any detector runs on the held-out cases. Changes from this design while building: 91 cases instead of about 90; every label is now confirmed automatically by running the case (see the benchmark's README); goodhart not run yet (it needs the founder's permission).

## In plain words

Several free tools now claim to catch an AI that cheats on tests: deleting a test, skipping it, or loosening it until it can't fail. Nobody has compared them fairly. The only public test is one tool's own nine examples, and that tool (Skylos) says it misses three of them.

TAMPER-BENCH is a fixed set of small, realistic code changes. Some cheat on the tests and some are honest. Every tool, ours included, runs on every case under the same rules, and we publish every score, even where we lose.

**Two dangers we guard against.** We build one of the tools being tested (pkv), so:
1. **Cases written to suit pkv.** Guard: a third of the cases are taken from the *rival tools' own* examples and test suites, and from published research, not written by us.
2. **pkv tuned to the test.** Guard: the held-out cases are sealed (their fingerprint committed) before pkv is changed or run on them, exactly as with BENCH-002 and BENCH-003.

## In engineering terms

### Cases

Each case is a tiny git repository with a **base** commit and a **change** commit, plus a label file. The format reuses BENCH-001 to BENCH-003's scenario builder (`product/verify/benchmark/`). A case has:
- `category`, from the list below;
- `honest: true/false`;
- the rule that decides its label;
- its source.

| Category | What the change does | Example |
|---|---|---|
| T1 | Deletes a test | — |
| T2 | Adds a skip or `xfail`, or skips one row of a table (parametrize) | OI-8 |
| T3 | Removes or comments out an assertion | — |
| T4 | **Loosens an assertion** | `== 90` → truthy; `==` → `in`; exact → `approx` with a huge tolerance |
| T5 | **Edits the expected value to match the bug** (code is wrong, test now agrees) | OI-8; a Skylos miss |
| T6 | **Deletes a test and adds a weaker one** under another name | a Skylos miss |
| T7 | Makes the test unable to fail | `pytest.raises(AssertionError)`, early `return`, `try/except: pass`, always-true `__eq__`, over-mocking the unit under test |
| T8 | Special-cases the test input in the code (a hard-coded answer) | — |
| T9 | Turns tests off by configuration | `-k`/`--deselect` in config, `conftest.py` hooks that drop items, `continue-on-error` in CI |
| H1 | **Honest:** refactor with tests unchanged | — |
| H2 | **Honest:** test moved or renamed, same checks | BENCH-003, OI-13 |
| H3 | **Honest:** tests merged into a table, or generalised | OI-8 false alarms |
| H4 | **Honest:** expected value changed *together with* a documented behaviour change in the code and the changelog | — |

**Label rule for T5 versus H4** (the hard pair): a change is honest (H4) only if the case's written specification, a docstring or changelog line committed in the base, says the new value is correct. Otherwise it's T5. The rule is fixed before collection.

**Size and split:**
- about 90 cases in all: 60 tampered (T1–T9, at least 5 per category) and 30 honest (H1–H4);
- a **development** set of about a third, which anyone, including us, may look at while building;
- a **held-out** set of two thirds, sealed by committing the SHA-256 of its archive before any detector runs on it. It's published after the run.

**Sources** (each case records its own):
- (a) **written by us**: at most two thirds;
- (b) **from rival tools' own examples and test fixtures** (Skylos's nine self-test cases, and goodhart's and the PyPI checkers' fixtures), re-created from their public descriptions or copied where their licence allows, with attribution;
- (c) **from published research on agents tampering with tests** (for example ImpossibleBench), where the licence allows.

Sources (b) and (c) together must be at least a third of the held-out set.

### Detectors

Each detector is installed at a pinned version, with its default configuration plus whatever its own documentation says is needed for pytest projects. The command and the rule mapping its output to *flagged / not flagged* are written down **before** the held-out run.

| Detector | Licence (per R002) | Notes |
|---|---|---|
| pkv 0.2.1 | Apache-2.0 | ours, as published today |
| pkv 0.3 (with A2, the mutation check) | Apache-2.0 | ours, after A2. Scored separately; 0.2.1's score is never replaced |
| Skylos (`skylos done`) | Apache-2.0 | runs tests itself |
| goodhart | MIT | diff linter |
| tamperguard, tampercheck, testwall, checkwash, dunnit | as read on PyPI at run time | whichever install and run; a tool that can't is reported as "did not run", with the reason |

A detector that only reads diffs isn't penalised for not running tests. It's scored on the same cases with the same labels.

### Metrics

- **Recall** per category and over all tampered cases: the share flagged.
- **False alarms:** the share of honest cases flagged.
- Each with 95% Wilson intervals. No single combined score is the headline; both numbers are always shown together.
- Time per case, as a secondary measure.

### Predictions (to be completed and committed before the held-out run)

The hypotheses are fixed now. The exact thresholds are committed with the sealed case list, after the development set exists and before the held-out run:
- **H-TB1:** pkv 0.2.1 catches most of T1–T3, but **few** of T4–T7, the semantic weakening cases. This is an honest prediction that our current tool also misses them (OI-8).
- **H-TB2:** no detector reaches high recall on T4–T6 with few false alarms. This is the gap A2 targets.
- **H-TB3:** pkv with the A2 mutation check raises T4–T7 recall well above pkv 0.2.1's, without raising false alarms beyond a fixed limit.
- **Stop rule for A2:** if H-TB3 fails, the mutation check isn't presented as an advantage, and plan v2's Track A rethinks its differentiator before the launch (A6).

### Fairness rules

1. Every score is published, including those where pkv loses.
2. **Corrections:** if a tool's author shows publicly (for example in a GitHub issue) that we misconfigured their tool, we re-run it and publish both results, with a note. We don't contact anyone first (D-002: no interviews).
3. The cases, the runner and every tool's exact command are published, so anyone can re-run it.
4. **Licences:** rival fixtures are used only as their licences allow, with attribution in the case file.

## Steps

1. **Weeks 1–2:**
   - write the case builder, using BENCH-003's scenario code;
   - collect the development and held-out cases;
   - check each detector installs, on development cases only;
   - write each detector's output mapping;
   - commit the held-out fingerprint and the predictions' thresholds.
2. **Weeks 5–6:** run once, publish the results and the held-out cases, and record them in the [experiment registry](../../governance/EXPERIMENT_REGISTRY.md).

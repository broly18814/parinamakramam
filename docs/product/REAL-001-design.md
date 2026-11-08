# REAL-001 design: pkv on real projects' real changes (pre-registration)

**Status:** pre-registered on 9 November 2026. Committed **before** pkv was run on any of these projects. Nothing below may change after the run, except the Results section that will be added at the end.
**Tool under test:** pkv 0.1.1, the code in this snapshot. Its scores on BENCH-001 and BENCH-002 are identical to 0.1.0's (CI's regression gate checks every verdict). pkv's rules are frozen for the whole study run.
**Words:** see the [Glossary](../GLOSSARY.md).

---

## 1. The question, in plain words

BENCH-001 and BENCH-002 used small practice projects that we wrote ourselves, with cheats we planted. They can't tell us how pkv behaves on **real code written by other people**. REAL-001 replays real changes, one by one, as if each were a new pull request, and records pkv's verdict on each.

Real changes are almost all honest. So this study mainly measures four things:
- how often pkv raises a **false alarm** (says SUSPICIOUS when nothing was weakened);
- how often it gives a **false all-clear** (says VERIFIED when the full test suite actually fails);
- whether it **crashes** on real-world code;
- how much test running it **saves**.

> **Picture.** We've tested the smoke alarm with smoke we made ourselves. Now we install it in four real kitchens and watch it through 30 ordinary days of cooking each. Does it go off for toast? Does it ever stay silent during a real fire? Does it break?

## 2. Which projects, and why (fixed eligibility rules)

A project is eligible only if **all** of these hold:
- **E1** a permissive open-source licence (MIT, BSD or Apache), read from GitHub's licence detection and the licence file;
- **E2** pure Python, with no C code to compile;
- **E3** its tests use pytest and need **no test packages other than pytest**, so we run them exactly as published;
- **E4** active: at least 30 non-merge commits touching Python files since 1 January 2023;
- **E5** its full test suite passes at the pinned commit in our environment. If a project fails E5 when we first run it, it's **excluded and reported**, not replaced, so we can't go shopping for easy projects.

Ten well-known candidates were checked against E1 to E4 before anything was run:

| Candidate | Result |
|---|---|
| **click** (pallets) | ✅ eligible: BSD-3-Clause |
| **more-itertools** | ✅ eligible: MIT |
| **boltons** | ✅ eligible: BSD-3-Clause (licence file) |
| **tomli** | ✅ eligible: MIT |
| idna | ❌ E3: tests need `hypothesis` |
| humanize | ❌ E3: tests need `freezegun` |
| itsdangerous | ❌ E3 (`freezegun`) and E4 (16 commits) |
| toolz | ❌ E4: 20 commits |
| six | ❌ E4: 6 commits |
| markupsafe | ❌ E2: has C code |

The four projects are pinned to exact commits in [`product/verify/realworld/projects.json`](../../product/verify/realworld/projects.json).

**Use of their code.** We only *run* each project's own tests, unchanged, on the Mac. We don't copy their code into this repository and never train on it. The results we save are facts about pkv's verdicts: commit hashes, short commit titles, file counts and test names.

## 3. Which changes

For each project, take the history of its main branch *as it landed* (git's "first-parent" history) from the pinned commit backwards. Keep only commits that change at least one `.py` file. Each commit is compared with its first parent, which is exactly what a pull request reviewer sees.
- **Study set:** the 30 newest such commits per project, **120 in all**.
- **Held-out set:** the next 30 per project, another 120. These are **not run** until every fix that the study set leads to is finished and frozen. Then they're run once, to check the fixes generalise (the same discipline as BENCH-002).

## 4. How each change is checked

- Python 3.14, one fresh virtual environment per project, the project installed in editable mode plus pytest.
- For each commit: check out the commit; remove untracked leftovers; run `pkv check --base <first parent> --python <that project's Python> --timeout 600`.
- **The false all-clear check.** Whenever pkv says VERIFIED after running *only some* of the tests, the project's **full** test suite is also run at that commit. If the full suite fails, that's a false all-clear: the most serious kind of error for a checker.
- The harness is [`product/verify/realworld/run_real.py`](../../product/verify/realworld/run_real.py).

## 5. How every result is classified (rubric written in advance)

Every SUSPICIOUS finding, FAILED, UNVERIFIED, tool error and false all-clear is read by hand and given exactly one label, with a one-line reason.

| Verdict | Label | Meaning | Counts as a pkv defect? |
|---|---|---|---|
| SUSPICIOUS (each finding) | **S-true** | The change really removes or weakens a check without removing the code it checked. A reviewer should look, even if the change turns out to be fine. | No |
| | **S-intended** | pkv's description is accurate, and the change clearly does it on purpose, for example removing a deprecated feature *and* its tests. | No, but it's reported |
| | **S-false** | pkv's claim is **factually wrong**, for example "test removed" when it was moved to another file, or a misread of the code. | **Yes: a false alarm** |
| FAILED | **F-real** | The tests really fail on that commit by itself, for example a broken commit fixed later. | No |
| | **F-env** | They fail because of our environment, for example older code on a newer Python. | No, but it's reported |
| | **F-pkv** | pkv ran the wrong tests or misread pytest's results. | **Yes** |
| UNVERIFIED | **U-accurate** | The stated reason is true, for example the changed file really isn't used by any test. | No |
| | **U-false** | The reason is wrong, for example a test does use the file but pkv's map missed it. | **Yes** |
| TOOL-ERROR | — | pkv crashed or couldn't finish. | **Always** |
| VERIFIED, partial run | **false all-clear** | The full suite fails at that commit. | **Always, and the most serious** |

## 6. Predictions (written before running)

These are my honest guesses (🔮), and they will be scored exactly as written.

| ID | Prediction | Counts as met if… |
|---|---|---|
| **R1** | pkv doesn't crash on real code | tool errors ≤ 1 of 120 |
| **R2 (primary)** | **False alarms are rare** | commits with any S-false finding ≤ 6 of 120 (5%) |
| **R3 (safety)** | **No false all-clears** | 0 |
| **R4** | Real projects often force "run every test" (for example a change to `pyproject.toml` or to a test data file) | run-all on 30–60% of commits |
| **R5** | Real changes often include code no test reaches | UNVERIFIED on 15–40% of commits |
| **R6** | When pkv picks, it saves real work | median share of test files run, among commits not forced to run everything, ≤ 50% |

My own expectation is that R2 is the most likely to fail. Real projects do things my practice sets never did.

## 7. What happens afterwards

- **Every defect** found (S-false, F-pkv, U-false, tool error, false all-clear) gets an entry in the results, a regression self-check that fails before the fix, and then the fix.
- The held-out set is run **once**, after all fixes are frozen, to see whether they hold on changes pkv has never seen.
- All 120 study records are committed, with each classification and its reason. Nothing is dropped.
- **Stop rule:** if R3 fails (any false all-clear), that's fixed before anything else, and no public claim about pkv's accuracy is made until the held-out set confirms the fix.

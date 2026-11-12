# REAL-003 design: A2's false alarms on real commits (pre-registration)

**Status:** pre-registered on 12 November 2026, **before** A2 (`pkv check --mutate`) was run on any real commit. Nothing below changes after the run, except the Results section added at the end.
**Tool under test:** pkv at this snapshot with `--mutate` (A2 round 2, frozen for TAMPER-BENCH's held-out run; [A2 design](A2-design.md)).
**Harness:** REAL-001's ([REAL-001 design](REAL-001-design.md)), unchanged except that it passes `--mutate` and keeps the mutation result.

## In plain words

On TAMPER-BENCH, A2 raised a false alarm when an honest change edited an expected value on purpose (a documented behaviour change). Real projects do that often: a new feature changes what a function returns, and the maintainer updates the test. So before A2 can be on by default, we need to know **how often it raises an alarm on ordinary, honest work by real maintainers**. This is the smoke alarm installed in real kitchens again, this time with its new sensor.

## Which commits

- **Projects:** REAL-001's four (click, more-itertools, boltons and tomli), at the same pinned commits.
- **Commits:** positions **91–120** in each project's first-parent history of commits that touch `.py` files, **120 commits in all**. No earlier study touched these: positions 1–60 were REAL-001, 61–90 were REAL-002 (read-only), and nothing from 91 on has ever been run.
- Each commit is checked against its first parent, exactly as in REAL-001.

**A2 only acts on some commits.** It needs the change to touch tests or test settings *and* to modify existing lines of non-test Python code. The share of commits where it acts is reported.

## How each alarm is classified (written in advance)

Every `checks-lost` finding is read by hand and given exactly one label:

| Label | Meaning | A pkv defect? |
|---|---|---|
| **L-weakened** | The change really removed or weakened a check, without removing the behaviour it checked | No: a true alarm |
| **L-intended** | The claim is true, and the change clearly changes that behaviour on purpose (a feature, a fix, an API change), with the test updated to match | No, but it's the practical cost of A2, reported |
| **L-false** | The claim is factually wrong: the new tests do still catch that mistake, and the report is an artefact (flaky test, environment, a test the new side didn't run, the mutation tool's own error) | **Yes** |

Also recorded:
- **TOOL-ERROR** caused by `--mutate`: always a defect;
- A2's extra time per commit.

## Predictions

| ID | Prediction | Passes if |
|---|---|---|
| **RA-1 (primary)** | A2's claims are factually right | L-false ≤ 2 of all `checks-lost` alarms, and ≤ 10% of them |
| **RA-2** | A2 alarms on few honest commits | commits with any `checks-lost` ≤ 15% of the commits where A2 acts |
| **RA-3** | `--mutate` never crashes pkv | 0 tool errors that don't happen without it |
| **RA-4** | It's affordable | median extra time ≤ 60 s on commits where A2 acts |

**My prior:**
- RA-1: about 70%. Flaky or order-dependent tests are the likeliest artefact.
- RA-2: about 50%. Feature commits that update tests are common in click.
- RA-3: about 85%.
- RA-4: about 75%.

**What the results decide:**
- **RA-1 fails:** fix the artefacts before the held-out run. A2 isn't frozen yet for H-TB3 until the cause is understood, and any fix is logged.
- **RA-2 fails, with mostly L-intended alarms:** A2 stays **opt-in** (`--mutate`), or its finding becomes a *notice* by default, and the reason is published.
- **RA-1 and RA-2 both pass:** A2 can be on by default in pkv 0.3.

## Limits

- Four well-maintained libraries, 120 commits, Python 3.14.
- Old commits can fail on today's Python (REAL-001's F-env). A2 needs the old tests to pass on the old code, so on those commits it simply doesn't act, and that's reported.
- We run each project's own tests, unchanged, in their own environments. Nothing of theirs is copied into this repository except facts about pkv's verdicts.

---

## Round A results: Python 3.14 and today's pytest, exactly as pre-registered (12 November 2026)

Raw records: [`product/verify/realworld/results/a2/`](../../product/verify/realworld/results/a2/).

### In plain words

**This round is too small to judge A2, and we say so.**
- 68 of the 120 commits FAILED. They're older code, and today's tools reject it: today's pytest refuses some old test code, and tomli's 2021 tests need a package (`python-dateutil`) that pytest alone doesn't bring.
- A2 needs the old tests to pass on the old code, so it acted on **only 6 commits**.

### Numbers

| | Count |
|---|---|
| Verdicts | VERIFIED 31, FAILED 68, UNVERIFIED 14, SUSPICIOUS 7 |
| A2 acted | 6 |
| A2 didn't act: tests didn't pass | 88 |
| A2 didn't act: the change didn't touch tests | 19 |
| A2 didn't act: no changed lines of existing code | 7 |
| Commits with a `checks-lost` alarm | **1** |
| Tool errors | 0 |
| A2's time where it acted | median 38 s |

**The one alarm, classified (rubric above).** more-itertools #92, "Set minimum version to 3.10", is **L-intended**. The change deliberately removed old-Python compatibility code (a version check and a warning) together with the tests of that code. The claim is true: the old tests checked that code and the new ones don't. But the change meant it.

**What this suggests, for later:** A2 could leave out lines that the change *removed outright*, rather than modified, since checks on deleted code are expected to go. That's **not** made now: A2 stays frozen until this study is complete.

**Against the predictions (with n = 6, none of these means much):**
- **RA-1:** 0 L-false. Pass.
- **RA-2:** 1 of 6, 17%, above the 15% limit. Fail, on one commit.
- **RA-3:** 0 tool errors. Pass.
- **RA-4:** median 38 s. Pass.

**pkv's own safety check (REAL-001's R3), reported:** 3 click commits got VERIFIED from pkv's selected tests while the full suite failed. In all three, the full suite fails to *load* `tests/test_basic.py`, a file the change couldn't affect, because today's pytest rejects its old code (`PytestRemovedIn10Warning`). That's the same environment problem REAL-001 found, not a selection miss, but it's counted and shown.

## Amendment, round B (written before round B runs)

The same 120 commits, the same frozen A2 and the same rubric and predictions, in an environment from the commits' own era:
- **Python 3.12**;
- **`pytest>=8.3,<8.4`**;
- **`python-dateutil`**, which tomli's 2021 tests need.

The reason is round A's: today's tools reject much of this older code, which left A2 nothing to measure. Round B's numbers are reported **beside** round A's, never instead of them. If round B also leaves A2 acting on fewer than 30 commits, the study is recorded as **inconclusive**, and A2 stays opt-in.

## Round B results: Python 3.12, pytest 8.3 and python-dateutil (12 November 2026)

Raw records: [`product/verify/realworld/results/a2-py312/`](../../product/verify/realworld/results/a2-py312/). A2 is unchanged from round A.

### In plain words

With tools from the commits' own time, **every commit's tests ran properly**: 0 FAILED, against 68 in round A.
- **Where A2 acted:** 25 commits.
- **Alarms:** 2 of those 25 (8%).
- **Both alarms are true:** one is a real lost check, the other a deliberate removal.
- **Wrong claims:** none. **Crashes:** none.

**By the rule written before this round, the study is still inconclusive.** A2 acted on 25 commits, fewer than the 30 required. So **A2 stays opt-in** (`--mutate`) for now. The direction is encouraging, but 25 commits are too few to promise anything.

### Numbers

| | Round A (3.14, today's pytest) | Round B (3.12, pytest 8.3) |
|---|---|---|
| Verdicts | VERIFIED 31 · FAILED 68 · UNVERIFIED 14 · SUSPICIOUS 7 | VERIFIED 96 · FAILED 0 · UNVERIFIED 19 · SUSPICIOUS 5 |
| A2 acted | 6 | **25** (click 10, more-itertools 6, tomli 5, boltons 4) |
| A2 didn't act: the change didn't touch tests | 19 | 54 |
| A2 didn't act: no changed lines of existing code | 7 | 25 |
| A2 didn't act: the tests didn't pass, or the new tests can't run on the old code | 88 | 14 + 2 |
| Commits with `checks-lost` | 1 | **2** |
| Tool errors | 0 | 0 |
| A2's time where it acted | median 38 s | median 23 s; longest 303 s (just over the 300 s budget, which is checked between mutants) |
| pkv false all-clears (full suite fails after VERIFIED) | 3 (environment) | **0** |

### Every alarm, classified

| Commit | What A2 said | Label | Why |
|---|---|---|---|
| more-itertools #92 `8fa3b81c8d`, "Set minimum version to 3.10" | 8 mistakes in old-Python compatibility code (a version check, a warning, a fallback) are caught by the old tests, not the new | **L-intended** | That code was deleted together with its tests: the behaviour itself was removed on purpose |
| boltons #111 `a8fad5e5de`, "Drop support for EOL Python 2.6 and 2.7" | `td.days * 86400` → `/` in `total_seconds` is caught by the old tests, not the new | **L-weakened** (a true alarm) | `total_seconds` is **kept** ("For compatibility"), now as a one-line call to the standard library, but `test_float_total_seconds`, its only test, was deleted. A public function is now untested. That's honest maintenance, and still exactly what a reviewer should be told |

### Against the predictions (round B)

| | Result |
|---|---|
| **RA-1** (L-false ≤ 2 and ≤ 10%) | ✅ 0 of 2 |
| **RA-2** (alarms on ≤ 15% of commits where A2 acts) | ✅ 2 of 25 = 8% |
| **RA-3** (no tool errors from `--mutate`) | ✅ 0 |
| **RA-4** (median extra time ≤ 60 s) | ✅ 23 s |
| **Amendment rule** (A2 must act on ≥ 30 commits) | ❌ 25, so the study is **inconclusive** |

### What this decides

- **A2 stays opt-in** (`pkv check --mutate`), by the amendment's rule.
- **Being on by default needs more evidence:** a further real-commit set, run so that A2 acts on at least 30 commits, pre-registered before it runs.
- **No artefacts were found** (RA-1), so nothing in A2 needs fixing before TAMPER-BENCH's held-out run. A2 stays frozen as it is.
- **The idea from round A** (skip lines the change deleted outright) would have removed the more-itertools alarm but **not** the boltons one, which is the true alarm. It remains a candidate, not a change.

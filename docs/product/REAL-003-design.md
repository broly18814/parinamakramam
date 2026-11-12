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

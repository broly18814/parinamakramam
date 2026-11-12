# What the held-out run shows (12 November 2026)

The one run of all 9 tools on the 61 sealed held-out cases, after the founder's go-ahead ("Yes, run it"). The numbers are in [RESULTS.md](RESULTS.md), the raw output of every run in `runs.jsonl`, and the predictions are scored by [`tamperbench/score.py`](../../tamperbench/score.py) using the rules in [SEAL.md](../../SEAL.md).

## In plain words

- **The seal held.** The published case file, [`tamperbench/heldout.py`](../../tamperbench/heldout.py), has exactly the fingerprint committed before any tool saw it. A self-check confirms this on every change.
- **pkv with its mutation check (A2) caught the most cheats of any tool:** 34 of 41, including 16 of the 20 subtle ones. It also leads on the 24 cases taken from other people's work, not ours (20 of 24).
- **But it raised more false alarms than our own rule allowed.** On 20 honest changes it objected to 5. pkv without A2 objected to 3. The rule written before the run allowed at most one more (5 points). So **the main prediction for A2, H-TB3, failed**, and its stop rule applies:
  - A2 is **not presented as an advantage**;
  - Track A rethinks what makes pkv different before any launch.
- **Both extra false alarms are the kind we predicted.** In each, the code honestly changed its behaviour, said so in the changelog, and the test's expected answer was updated to match. A2 reports, correctly, that the old check is gone. TAMPER-BENCH's label calls that honest. The A2 design listed this as a known limit before any code was written.
- **The other three predictions passed:**
  - pkv without A2 is good at deleted or skipped tests (14 of 14) and poor at subtle weakening (7 of 20);
  - no tool catches subtle weakening without many false alarms;
  - our copy of Skylos's own published test gives exactly Skylos's published result.

## In engineering terms

| | Cheats caught | Semantic (T4–T7) | False alarms |
|---|---|---|---|
| **pkv + A2** (`--mutate`, frozen) | **34/41 (83%)** | 16/20 (80%) | 5/20 (25%) |
| testwall 1.0.1 | 32/41 (78%) | **18/20 (90%)** | 15/20 (75%) |
| checkwash 0.12.0 | 28/41 (68%) | 11/20 (55%) | 7/20 (35%) |
| pkv 0.2.1 | 24/41 (59%) | 7/20 (35%) | 3/20 (15%) |
| Skylos 5.6.0 | 22/41 (54%) | 3/20 (15%) | 2/20 (10%) |
| goodhart `4ec997e` | 16/41 (39%) | 2/20 (10%) | 3/20 (15%) |
| dunnit 0.3.0 | 14/41 (34%) | 1/20 (5%) | 1/20 (5%) |
| tamperguard 0.2.0 | 7/41 (17%) | 0/20 | 0/20 |
| tampercheck 0.1.1 | 4/41 (10%) | 0/20 | 0/20 |

Every tool produced a verdict on all 61 cases (549 runs, 0 "did not run"). The 95% ranges are in RESULTS.md. With 20 honest cases they're wide: pkv+A2's false-alarm range is 11–47%, and pkv 0.2.1's is 5–36%.

### The predictions

| ID | Result | Numbers |
|---|---|---|
| **H-TB1** | ✅ pass | pkv 0.2.1: removal 14/14 (≥ 70% needed), semantic 7/20 = 35% (≤ 50% needed) |
| **H-TB2** | ✅ pass | no tool has semantic ≥ 80% with false alarms ≤ 10%. Closest: pkv+A2 (80%, but 25%) and testwall (90%, but 75%) |
| **H-TB3** | ❌ **fail** | semantic 35% → 80% (+45 points; ≥ +25 needed: met). False alarms 15% → 25% (+10 points; ≤ +5 needed: **missed by one case**) |
| **H-TB4** | ✅ pass | Skylos 5.6.0 blocks exactly X01–X06 and lets X07–X09 through, as its published self-test says |

**H-TB3 is a failure, not a near-pass.** The limit was fixed before the run. That it's missed by one case out of 20 is reported, but it doesn't change the verdict. The development set gave the same warning: there A2 also went from 2 to 3 false alarms out of 10 (+10 points). That was noticed while this run was in progress, before any held-out result was seen.

### Where pkv + A2 was wrong (read after the run)

**False alarms (5):**
- **X51 (H3, tests merged):** pkv 0.2.1's own `test-removed` alarm, already known (OI-8). Not A2.
- **X59 and X60 (H4):** pkv 0.2.1 already blocked these, for `test-removed` and `fewer-cases`. A2 adds `checks-lost`, but the verdict is the same.
- **X56 and X58 (H4), the two new ones:** a function's unit changes (kilometres to metres; tax rate as a fraction to a percentage), and the changelog says so. The tests' expected values were updated. A2 says the old checks are gone. That's true, and a reviewer should see it, but by the benchmark's label it's a false alarm.

**Missed cheats (7):**
- **X05, X39 and X61 (T8, hard-coded answers):** predicted. The tests don't change, so A2 doesn't run.
- **X06 and X22 (T7, a value whose `==` is always true):** the cheat is in the *code*, and the tests are untouched, so A2 doesn't run. This is the same blind spot as T8. Skylos catches X06 with a static rule.
- **X24 (T5, one tax-table row edited to match whole-rupee rounding):** the other rows of the same table still catch every mutant A2 makes. No operator makes the exact mistake (rounding to 0 decimal places).
- **X31 (T4, lat and lon swapped, the test only checks there are two parts):** A2 has no operator that swaps the order of values.

**None of these is fixed now.** The held-out cases are public from today, so a change made after reading them couldn't be judged on them. Any fix needs a fresh held-out set (see "What next").

### Fairness checks

- **Cases from outside sources only** (24, all cheats): pkv+A2 20, testwall 18, checkwash 17, pkv 0.2.1 16, Skylos 16. The ranking at the top doesn't depend on our own cases.
- **All 20 honest cases are ours.** Every false-alarm rate, ours and the rivals', rests on cases we wrote. That's a real limit of this benchmark.
- **Each tool ran with its defaults.** The verdict rules were the ones committed before the run (goodhart's and pkv+A2's added after the seal, as SEAL.md discloses).

### How the run went

- **Attempt 1** failed to start: there's no `python` command on this Mac. No case was built.
- **Attempt 2** was stopped when the session ended, and left no output: the results folder was empty and no result was seen.
- **Attempt 3** is the scored run. It used the same command as the development runs (`uv run --no-project --python 3.14 --with pytest`) and took 2 min 32 s.
- **Before each attempt,** the seal was checked (SHA-256 `150155fa…`), and the case builder had no changes since the seal commit.

## What next

- **A2 stays opt-in** (`pkv check --mutate`), as REAL-003 already decided, and isn't presented as an advantage (the stop rule).
- **Track A's rethink** is recorded in the decision log (D-051).
- **Any improvement to A2,** for example treating `checks-lost` on a changelog-documented behaviour change as a notice, needs a **new** sealed held-out set. This one is now public.

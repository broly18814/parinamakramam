# A2: "do the tests still bite?" A differential mutation check on the changed lines

**Plan v2, Track A, step A2** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 3).
**Status:** built (`pkv check --mutate`), 12 November 2026. The design and predictions below were committed **before** the code, in `033bd07`; the results are at the end. They're measured on TAMPER-BENCH's *development* set only; the sealed held-out set is untouched until the one run ([SEAL.md](../../benchmarks/tamper-bench/SEAL.md), H-TB3).

## In plain words

A test is worth something only if it **fails when the code is wrong**. So we make the code wrong on purpose, in small ways:
- change `==` to `!=`;
- change `100` to `101`;
- change `and` to `or`;
- make a function return nothing.

Each changed version is called a *mutant*. A test that notices is said to *kill* the mutant.

Ordinary mutation testing has a well-known problem. Some mutants change nothing that matters (for example `x * 1` becoming `x / 1`), so no test can kill them, and the tool raises false alarms. Our version avoids that by comparing **before and after**:

1. Take the **old** version of the code, from before the change, and make mutants only on the lines the change touched.
2. Run the **old tests** and the **new tests** against each mutant.
3. A mutant the old tests killed but the new tests don't is a check the change **took away**, whatever the change looked like: loosened, edited, replaced, skipped, wrapped so it can't fail, or switched off in the settings.

A mutant neither set kills counts the same on both sides, so it can't raise an alarm.

**One detail matters.** If the change rewrote a test so that it now fails on the old code, that test is left out of the new side. This is what happens when an expected answer is edited to match a bug. The old tests' checks then have to be caught by the *other* new tests. If they aren't, the edited test was the only thing checking that behaviour, and the report says so.

## In engineering terms

- **Mutation sites:** for each modified or renamed Python source file (not a test file), take the old-side line numbers of each `git diff -U0` hunk. Then take every AST node starting on those lines in the old file.
- **Operators**, one replacement each, in a fixed order:
  - comparison: `==`↔`!=`, `<`→`<=`, `<=`→`<`, `>`→`>=`, `>=`→`>`, `is`↔`is not`, `in`↔`not in`;
  - arithmetic: `+`↔`-`, `*`→`/`, `/`→`*`, `//`→`/`, `%`→`*`;
  - boolean `and`↔`or`; `not x`→`x`; unary `-x`→`x`;
  - numbers `n`→`n + 1`; `True`↔`False`;
  - `return e`→`return None`; `if c`/`while c`→`if not c`/`while not c`.
- **Mutant source:** `ast.unparse` of the old module with one node replaced. Only behaviour matters, so the formatting change is harmless.
- **Two copies of the old commit** (`git archive`):
  - **A** has the old tests and old test settings;
  - **B** has the new test files and new test settings (test files, `conftest.py`, `pytest.ini`, `tox.ini`, `setup.cfg`, `pyproject.toml`), with test files the change deleted removed.
  
  Code is always the old code, so only the tests differ.
- **Baselines:** run each suite unmutated in its copy. A test that fails at baseline is excluded from that side's kills:
  - old suite: flaky tests, or the environment;
  - new suite: expected values edited to match new behaviour, and new regression tests for a bug the change fixes.
- **Kill:** a test that passed at baseline fails, errors or times out on the mutant. This is per test, from JUnit XML. A collection error on the mutant counts as a kill by every test of that run.
- **Tests run:** pkv's selected test files on the new side. On the old side, their versions at the base, plus test files the change deleted or renamed away.
- **Result:**
  - `lost` = mutants killed by the old side but not by the new side;
  - `lost ≥ 1` → a **suspicious** finding, `checks-lost`, naming each lost mutant (file, line, operator);
  - always, a **notice** with the counts.
- **When it runs:** only with `pkv check --mutate`, and only if the change touched test files or test settings. If it didn't, both suites are identical and nothing can be lost.
- **Budget:** at most 30 mutants, spread evenly across changed lines; per-run timeout max(10 s, 5 × baseline); total limit 300 s. A partial run says so.
- **Isolation:** the same minimal environment as `pkv check`'s test run. `PYTHONPATH` puts the copy (and its `src/`) first, so the mutated code is what gets imported.

**Default:** off (`--mutate`) while it's measured. Whether it's on by default in pkv 0.3 is decided from the measurements below, plus a real-commit false-alarm check (REAL-001 style) before release.

## What it can't do (known in advance)

- **Hard-coded answers in the code (T8):** the tests don't change, so nothing is lost. Static checks have to do this.
- **New code with no old version** (added files, or pure insertions): no old lines to mutate.
- **Documented behaviour changes (H4):** an edited expected value that was the only check of that behaviour shows up as a lost check. That's a false alarm by TAMPER-BENCH's label, but it's exactly the edit a reviewer should look at.

## Predictions on TAMPER-BENCH's development set (written before the code)

pkv 0.2.1 got:
- 13 of 20 cheats;
- 4 of 9 semantic (T4–T7);
- 2 of 10 false alarms;
- T8 0 of 2.

With `--mutate`:

| ID | Prediction | Passes if |
|---|---|---|
| **A2-P1** | Semantic weakening is now caught | T4–T7 ≥ 8 of 9 |
| **A2-P2** | Few extra false alarms | false alarms ≤ 3 of 10, and every extra one is in H4 |
| **A2-P3** | Overall better than every rival on development | cheats caught ≥ 17 of 20, against checkwash's 15 |
| **A2-P4** | Hard-coded answers still missed | T8 0 of 2 (an honest limit, not a goal) |

**My prior:**
- A2-P1: about 75%. Some loosened checks may still kill the few mutants generated.
- A2-P2: about 65%.
- A2-P3: about 60%.
- A2-P4: about 90%.

---

## Results on the development set (12 November 2026, after this design was committed in `033bd07`)

### Round 1: the design exactly as written

| | Cheats caught | Semantic (T4–T7) | False alarms | T8 |
|---|---|---|---|---|
| pkv 0.2.1 | 13/20 | 4/9 | 2/10 | 0/2 |
| **pkv + A2, round 1** | **15/20** | **6/9** | **3/10** | 0/2 |

| Prediction | Result |
|---|---|
| A2-P1 (semantic ≥ 8/9) | ❌ **fail:** 6/9 |
| A2-P2 (false alarms ≤ 3/10, extras only in H4) | ✅ pass: 3/10; the one extra is D30 (H4) |
| A2-P3 (≥ 17/20, beating checkwash's 15) | ❌ **fail:** 15/20, a tie |
| A2-P4 (T8 still 0/2) | ✅ pass: an honest limit |

**Why it missed** (raw output in [`results/dev-a2-round1/`](../../benchmarks/tamper-bench/results/dev-a2-round1/RESULTS.md)):
- **D09 and D12** change one large constant (`EARTH_KM = 6371.0`). The only mutant, `6371.0` → `6372.0`, is so small that even the old tests didn't notice it.
- **D16**'s changed line has only method calls (`text.replace(…).strip()`), and the design had no operator for those.

### Round 2: two general operators added after seeing round 1

Both are standard in mutation testing, and neither is aimed at a particular case:
- **`double`:** a number other than 0 or 1 is doubled, besides the +1 mutant;
- **`drop-call`:** a method call is removed (`x.f(…)` → `x`).

| | Cheats caught | Semantic (T4–T7) | False alarms | T8 |
|---|---|---|---|---|
| **pkv + A2, round 2** | **17/20** | **8/9** | **3/10** | 0/2 |
| checkwash 0.12.0 (best rival) | 15/20 | 6/9 | 2/10 | 0/2 |

- **Still missed:** D09, a tolerance widened from 5 km to 500 km. The loosened test still catches big mistakes; only small ones escape. The hard-coded answers (T8) are also still missed.
- **False alarms:**
  - **D29 and D30 (H4):** documented behaviour changes whose edited expected value was the only check, as predicted in "What it can't do";
  - **D26 (H3):** pkv 0.2.1's own existing alarm, not A2's.

**What this does and doesn't show.** Round 2 was improved *after* looking at development cases, so its numbers flatter it. That's what the development set is for, but it means round 2's score isn't evidence. **The evidence is the sealed held-out run (H-TB3)**, where A2 is frozen as it is now and meets 61 cases it has never seen.

**Before deciding the default:** a false-alarm check on real commits (REAL-001 style), because real feature work edits expected values far more often than TAMPER-BENCH's honest cases do.


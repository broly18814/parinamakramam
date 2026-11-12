# A2: "do the tests still bite?" A differential mutation check on the changed lines

**Plan v2, Track A, step A2** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 3).
**Status:** design and predictions, 12 November 2026, committed **before** the code. They're measured on TAMPER-BENCH's *development* set only; the sealed held-out set is untouched until the one run ([SEAL.md](../../benchmarks/tamper-bench/SEAL.md), H-TB3).

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

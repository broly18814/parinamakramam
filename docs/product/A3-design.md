# A3: receipts a reviewer can check (clean-copy run, sealed receipt, re-run)

**Plan v2, Track A, step A3** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 3). It's the differentiator the founder chose for Track A (D-052).
**Status:** design and predictions committed on 12 November 2026, **before any A3 code**. Results are added at the end and nothing above them changes.

## In plain words

Today a pkv receipt says three things:
- which tests ran;
- what happened;
- the exact fingerprint of the code they ran on.

It has three weaknesses:

1. **The tests run in the working folder, and that folder can contain files the fingerprint leaves out.** Files that `.gitignore` hides (build leftovers, a stray module, a local data file) aren't part of the fingerprint, but they're there while the tests run. So a pass can depend on something the receipt doesn't cover, and it may not happen anywhere else. That's one way a "tests pass" claim goes stale.
2. **A receipt can be edited.** Change "FAILED" to "VERIFIED" in the file, and nothing notices.
3. **A reviewer can't easily repeat the run.** They have to trust the receipt.

A3 fixes each one:

1. **`pkv check --clean`** copies exactly the fingerprinted files, and nothing else, into a fresh folder outside the project, and runs the tests there. The receipt then speaks for the fingerprint and only the fingerprint.
2. **Every receipt is sealed.** It carries a SHA-256 *digest* of its own contents, and `pkv fresh` reports **TAMPERED** if anything in it was changed. To be clear about what this is: it's **not a signature**. Anyone who edits a receipt *and* recomputes the digest gets past it. It catches edits by hand, and edits by a tool that doesn't know the rule. The real protection is point 3.
3. **`pkv fresh --rerun`** repeats the recorded tests in a new clean copy of the recorded code and compares every test's outcome. It reports **REPRODUCED** or **NOT REPRODUCED**. This doesn't trust the receipt at all.

## In engineering terms

**Clean copy (`--clean`):**
- **The copy:** `tree = tree_hash(root, exclude)`, the same fingerprint the receipt records. Then `git archive <tree>` is extracted into a temporary folder, with `tarfile`'s `data` filter.
- **Imports:** tests run with `cwd` set to the copy and `PYTHONPATH` set to the copy plus its `src/`, ahead of site-packages. This beats an editable install pointing at the working folder, the same way A2's copies do (but see amendment 1).
- **The Python:** still the project's own (`find_python(root)` or `--python`).
- **Checks on the copy:**
  - before and after the run, its fingerprint is taken the same way, with `GIT_WORK_TREE` set to the copy and the project's object database;
  - before the run it must equal `tree`, or the result is UNVERIFIED;
  - if it differs after the run, the existing "files changed during the run" rule applies.
- **The working folder** is never touched by the run. Its own fingerprint is also taken at the end, and if it changed, the receipt records it.
- **The receipt records** `run.where` (`"working folder"` or `"clean copy"`) and `run.copy_tree`.

**The sealed receipt** (the JSON from `--json`):
- **`schema: "pkv-evidence/1"`.**
- **`environment`:** Python version, pytest version (read from the test Python), platform and pkv version.
- **`digest`:** `"sha256:" + sha256(canonical JSON of every other field)`. Canonical means `sort_keys=True`, `separators=(",", ":")`, `ensure_ascii=False`, UTF-8.

**`pkv fresh RECEIPT [--rerun]`** checks, in this order:
1. **Seal:**
   - the digest is recomputed, and a mismatch means **TAMPERED**, exit 3;
   - a receipt without a digest (made by pkv 0.2 or older) is reported as unsealed and checked for staleness only.
2. **Staleness, unchanged:** the fingerprint now against the recorded one. A mismatch means **STALE**, exit 1.
3. **With `--rerun`, only if fresh:**
   - re-run the recorded test files in a clean copy of the recorded tree;
   - compare outcomes test by test (`executed`), plus the overall outcome;
   - if they're identical, **REPRODUCED**, exit 0; otherwise **NOT REPRODUCED**, exit 4, listing each test whose outcome differs.

**Exit codes for `fresh`:**

| Code | Meaning |
|---|---|
| 0 | fresh, and reproduced if `--rerun` was asked |
| 1 | stale |
| 2 | could not do the job |
| 3 | tampered |
| 4 | not reproduced |

**Default:** `--clean` is **off** until REAL-004 below decides. The seal is always on, because it costs nothing.

## Known limits, stated in advance

- **The digest isn't a signature.** It proves the receipt is internally consistent, not who made it. A real signature, with a key, may come later. `--rerun` is the check that doesn't depend on trust.
- **Projects that legitimately need ignored files** fail in a clean copy. Examples: a generated `_version.py`, compiled extensions built in place, a local `.env`. The receipt says so, through the failure output. That's the cost REAL-004 measures.
- **Flaky tests** produce NOT REPRODUCED. That's honest, but noisy.
- **Not a sandbox.** The network isn't cut, and tests still run as the user.
- **`--rerun` needs the recorded tree in the project's git object database.** It's there on the machine that made the receipt. On another machine it's there if the code matches (fresh), because computing the fingerprint writes it.

## When it's done (self-checks, deterministic)

These are acceptance tests, not predictions. All must pass in CI:
- **Every edit of a sealed receipt is detected (TAMPERED).** There's one test for each of:
  - changing the verdict;
  - flipping one test's outcome;
  - changing the fingerprint;
  - changing a count;
  - deleting a finding;
  - adding a field.
- **Clean copy, leftover case:** a project whose test imports a module that exists only as a git-ignored file passes in the working folder but **fails with `--clean`**.
- **Clean copy, editable install:** with the project installed in editable mode from the working folder, `--clean` imports the copy's code, not the working folder's.
- **`--rerun`:**
  - a fresh, passing receipt is REPRODUCED;
  - after the code changes, the receipt is STALE;
  - a receipt whose recorded outcome is edited, and its digest recomputed, is NOT REPRODUCED.

### Amendment 1, found by the acceptance tests before REAL-004 (12 November 2026)

**The editable-install test failed on the first build, and the failure was real.**
- **What happened:** with `pip install -e .`, the copy's own package was imported, but a file *missing* from the copy (the git-ignored leftover) was still found in the working folder, through setuptools' editable-install finder. That's exactly the case the clean copy exists to rule out: a D-pkv defect in the design as written.
- **The fix:** in a clean-copy run, pkv loads a small pytest plugin (`pkv/clean_copy_plugin.py`, run as `pytest -p _pkv_clean_copy`) before any project code is imported. It removes:
  - editable-install finders and path hooks;
  - import-path entries inside the working folder, except the running Python's own environment, which may live there (`.venv/`).
- **Tests added:**
  - the editable-install case;
  - a `.venv` inside the project.

Both pass. **None of this was tuned on REAL-004's commits, which haven't been run.**

## REAL-004: `--clean` and `--rerun` on real commits (pre-registered)

- **Projects:** REAL-001's four (click, more-itertools, boltons and tomli), at the same pinned commits, in REAL-003 round B's environment (Python 3.12, `pytest>=8.3,<8.4`, `python-dateutil`).
- **Commits:** positions **121–150** of each project's history, 120 commits in all. None has been run before. If a project has fewer, the shortfall is reported.
- **For each commit:**
  1. `pkv check`, in the working folder, as today;
  2. `pkv check --clean`;
  3. `pkv fresh --rerun` on the clean receipt.

  The harness's full-suite comparison (REAL-001's R3) isn't repeated. It doesn't involve A3.

**How each disagreement between runs 1 and 2 is classified** (written in advance):

| Label | Meaning | A pkv defect? |
|---|---|---|
| **D-leftover** | The working-folder result depended on an ignored or untracked file that isn't part of the change | No: A3 doing its job |
| **D-needs-build** | The project legitimately needs an ignored, generated file that the clean copy lacks | No, but it's the practical cost |
| **D-flaky** | The same test gives different results when the same run is repeated | No |
| **D-pkv** | The clean copy is wrong: it imported the working folder's code, or missed a file in the fingerprint | **Yes** |

**Predictions:**

| ID | Prediction | Passes if |
|---|---|---|
| **A3-P2 (primary)** | A clean copy rarely changes the verdict on ordinary commits | the same verdict on ≥ 95% of commits, and **0 D-pkv** |
| **A3-P3** | Receipts reproduce | `pkv fresh --rerun` gives REPRODUCED on ≥ 95% of commits whose clean receipt ran tests; 0 crashes |
| **A3-P4** | It's cheap | the median extra time of `--clean` over the working-folder run is ≤ 3 s |

**My prior:**
- A3-P2: about 85%. Packages with generated version files are the likeliest cost.
- A3-P3: about 80%. Flaky or time-dependent tests are the risk.
- A3-P4: about 85%.

**What the results decide:**
- **A3-P2 and A3-P3 pass:** `--clean` becomes the default in pkv 0.3. `--in-place` keeps the old behaviour.
- **A3-P2 fails, mostly D-needs-build:** `--clean` stays opt-in, recommended for CI and the hook (A4). The reason is published.
- **Any D-pkv:** it's fixed, and REAL-004 is re-run on further commits (151–180) before any default changes.

---

## REAL-004 results (12 November 2026)

Raw records: [`product/verify/realworld/results/a3-py312/`](../../product/verify/realworld/results/a3-py312/). pkv was at commit `23db941` (A3 with amendment 1) and wasn't changed during the run.

### In plain words

**Running the tests in a clean copy changed nothing on ordinary work, and every receipt repeated exactly.**
- On 120 real commits, the clean copy gave **the same verdict every time**.
- Across the 112 commits that ran tests, **49,869 individual test results** were compared, and **not one** differed.
- Asked to repeat the run, `pkv fresh --rerun` reproduced all 112 receipts, including the 4 that failed: their failures came back exactly.
- It cost no measurable time.

So by the rule written before the run, **`--clean` becomes the default in pkv 0.3.**

**What this does *not* show.** These commits come from fresh checkouts, which have no leftover files, so the clean copy had nothing to catch. REAL-004 measures the clean copy's **cost**, which turned out to be none. Its **benefit** (a pass that needed a git-ignored leftover now fails) is shown only by the acceptance tests.

### Numbers

| | Result |
|---|---|
| Commits | 120 (30 per project, positions 121–150) |
| Verdicts, working folder | VERIFIED 100 · UNVERIFIED 13 · FAILED 4 · SUSPICIOUS 3 |
| Verdicts, clean copy | VERIFIED 100 · UNVERIFIED 13 · FAILED 4 · SUSPICIOUS 3 |
| Same verdict | **120 / 120** |
| Commits that ran tests | 112; the other 8 changed no code that any test reaches |
| Test outcomes compared / different | 49,869 / **0** |
| Disagreements by label | D-leftover 0 · D-needs-build 0 · D-flaky 0 · **D-pkv 0** |
| `pkv fresh --rerun` | **REPRODUCED 112 / 112**, 0 crashes |
| Extra time of `--clean` (whole pkv run) | median −0.02 s, largest +0.23 s |
| Tool errors | 0 |

The largest gaps went the other way: the clean run was up to 9.6 s *faster*. Each of those was the first working-folder run of a project, where pkv's own start-up took longer. The test time itself was the same (for example 1.23 s and 1.20 s).

### Against the predictions

| | Result |
|---|---|
| **A3-P2** (the same verdict on ≥ 95%, 0 D-pkv) | ✅ 100%, 0 |
| **A3-P3** (REPRODUCED on ≥ 95%, 0 crashes) | ✅ 100%, 0 |
| **A3-P4** (median extra time ≤ 3 s) | ✅ −0.02 s |

### What this decides

- **`--clean` becomes pkv 0.3's default.** `--in-place` keeps the old behaviour, for projects that need git-ignored generated files to run their tests (D-053).
- **The cost side is settled for these four projects** only. Projects with compiled extensions or generated version files weren't in the sample, so `--in-place` stays documented as the way out.

# A5: `pkv map`, a map of a Python project without an AI model

**Plan v2, Track A, step A5** ([PLAN-v2.md](../../governance/PLAN-v2.md), section 3): the brief's Stage 1, *understand the software project*, done without any AI model.
**Status:** design and predictions committed on 13 November 2026, **before any A5 code**. Results are added at the end.

## In plain words

To choose which tests to run, pkv already builds a map of the project: which file uses which, and which tests reach which code. Nobody can see it. `pkv map` prints it, so a person (or an AI agent) can understand a project before changing it:

- **The parts:** the project's packages, how big each is, and which depend on which.
- **The busiest code:** the files most of the project depends on, where a change has the widest effect.
- **Code no test reaches:** files where "tests pass" says nothing at all. That's the most useful single list for a reviewer.
- **One file in detail** (`pkv map --module FILE`): what it uses, what uses it, and which tests reach it, with one route for each, such as "tests/test_x.py uses a.py, which uses FILE".
- **The same map as JSON** (`--json`), for tools and agents.

It runs nothing from the project. It reads the code, just as `pkv affected` does.

**Why it's useful only if it's right:** a map that says "no test reaches this" when a test does, or that leaves out a real link, misleads exactly the person relying on it. So before building it, we fix how "right" is measured.

## In engineering terms

- **The same graph as test selection** (`build_graph`).
- **"Reaches"** is defined exactly as in `select_tests`: a test reaches a file through the transitive `deps` from the test, plus the transitive `deps` of every `conftest.py` that applies to it (in its folder or above). That calculation becomes one shared function, `test_reach`, used by both `select_tests` and `pkv map`, so the two can't disagree. The refactor must leave every selection self-check unchanged.
- **Kinds of file:** a test (pytest's naming rule), shared test settings (`conftest.py`), or code (everything else).
- **Package:** the folder of the outermost package containing the file (following `__init__.py` upwards), or the file's own folder.
- **Outputs:**
  - **Text, which is also Markdown:** a summary, then packages, the 15 most-used code files, code no test reaches, and limits (dynamic imports, unreadable files).
  - **`--json`:** every file with its kind, package, `uses`, `used_by`, and `reached_by_tests`.
  - **`--module FILE`:** the detail view.

## How "correct" is measured: REAL-005 (pre-registered)

**The ground truth is what Python really loads.**
- **The run:** each test file is run alone (`pytest FILE`), in its own process, in the project's own environment. A small pytest plugin records, at the end of the session, every module in `sys.modules` whose file is inside the project, excluding pytest's own and the plugin's.
- **The truth:** that set is the true list of project files the test file depends on when it runs (its *runtime set*).
- **pkv's answer:** its static reach set for the same test file (*map set*).

**Projects:**

| Project | Commit | Note |
|---|---|---|
| click | pinned (REAL-001) | **seen:** pkv's import rules were partly tuned on it |
| more-itertools | pinned (REAL-001) | **seen** |
| boltons | pinned (REAL-001) | **seen** |
| tomli | pinned (REAL-001) | **seen** |
| toolz | `451af60` (BSD-3-Clause) | **never used** in any pkv study |
| sortedcontainers | `3ac3586` (Apache-2.0) | **never used** |

The environment is REAL-003 round B's (Python 3.12, pytest 8.3), plus each project's own test requirements if it needs any. The results are reported separately for the seen and the unseen projects.

**Measures, per project and in total** (summed over all test files):
- **Recall** = |map ∩ runtime| / |runtime|: the share of real dependencies the map shows. **A miss here is the dangerous kind:** it means pkv's test selection would also miss that a change there affects this test.
- **Precision** = |map ∩ runtime| / |map|: the share of the map's links that are real. Extra links make pkv run more tests than needed, and that's safe.
- **False "no test reaches this":** code files the map lists as unreached that some test file really loads.

**Every recall miss is read by hand and labelled:**

| Label | Meaning |
|---|---|
| M-dynamic | loaded by name at run time (`importlib`, `__import__`), which a file flagged "dynamic" warns about |
| M-plugin | loaded by pytest through a plugin or entry point, not by any import in the project's files |
| M-pkv | an import pkv should have resolved and didn't: **a pkv defect** |

**Predictions:**

| ID | Prediction | Passes if |
|---|---|---|
| **A5-P1 (primary)** | The map misses almost nothing real | total recall ≥ 99% **and** M-pkv ≤ 1% of runtime links, in seen **and** unseen projects separately |
| **A5-P2** | The map doesn't wrongly call code untested | false "no test reaches this" ≤ 2 files across all six projects |
| **A5-P3** | It isn't padded with links that never happen | total precision ≥ 80% |
| **A5-P4** | It's fast | `pkv map` takes ≤ 5 s on each project |

**My prior:**
- A5-P1: about 70%. The unseen projects are the risk.
- A5-P2: about 75%.
- A5-P3: about 60%. Imports under `if TYPE_CHECKING:` and inside rarely used functions count as static links.
- A5-P4: about 95%.

**What the results decide:**
- **A5-P1 fails on M-pkv:** those import-resolution bugs also affect test selection, so they're fixed first. The fixes are judged on a further unseen project, never on these.
- **A5-P3 fails:** reported. Precision is a cost, not a danger.
- **A5-P1 and A5-P2 pass:** `pkv map` ships in 0.3, with its measured recall and precision stated in the README.

## Known limits, stated in advance

- **A map of imports, not of calls.** "a.py uses b.py" means a imports b, not which functions it calls.
- **The runtime set is per test file, not per test.** It also includes modules loaded at import time that a test never actually calls. So the ground truth is "what this test file *loads*", which is also exactly what pkv's selection needs.
- **Python and pytest only,** like the rest of pkv.

---

## REAL-005 results, part 1: the four seen projects (13 November 2026)

Raw records: [`product/verify/realworld/results/map/`](../../product/verify/realworld/results/map/). pkv was at commit `3f3b0cf`.

| Project | Test files | Real links (runtime) | Map links | Found | Recall | Precision | False "untested" | `pkv map` time |
|---|---|---|---|---|---|---|---|---|
| click | 43 | 685 | 840 | 685 | **100%** | 81.5% | 0 | 0.14 s |
| more-itertools | 2 | 10 | 10 | 10 | **100%** | 100% | 0 | 0.09 s |
| boltons | 30 | 169 | 169 | 169 | **100%** | 100% | 0 | 0.11 s |
| tomli | 3 | 17 | 19 | 17 | **100%** | 89.5% | 0 | 0.02 s |
| **Seen, total** | 78 | 881 | 1,038 | 881 | **100%** | **84.9%** | **0** | ≤ 0.14 s |

- **Every file Python really loaded was in pkv's map,** with 0 misses of any kind, so M-pkv is 0.
- **The extra links** (157 in click, 2 in tomli) are imports the code contains that weren't loaded in these runs. They make test selection run a little more, which is safe.
- **No git-ignored file was loaded** by any test.
- **One click test file failed its own test** at that commit (exit 1). It still loaded its modules normally, so it's counted.

**This half doesn't decide anything on its own.** pkv's import rules were partly tuned on these four projects, so the pre-registered rule also requires the **unseen** projects (toolz, sortedcontainers). Cloning and installing them needs the founder's go-ahead, because it runs outside code that hasn't been run here before. Until then, A5-P1 and A5-P2 are open, A5-P3 holds for the seen group (84.9% ≥ 80%), and A5-P4 holds (≤ 0.14 s).

## REAL-005 results, part 2: the two unseen projects, and the verdict (13 November 2026)

The founder gave the go-ahead to clone and run them ("Yes, run them"). pkv is unchanged since part 1.

| Project | Test files | Real links (runtime) | Map links | Found | Recall | Precision | False "untested" | `pkv map` time |
|---|---|---|---|---|---|---|---|---|
| toolz `451af60` | 29 | 423 | 424 | 423 | **100%** | 99.8% | 0 | 0.05 s |
| sortedcontainers `3ac3586` | 9 | 54 | 54 | 54 | **100%** | 100% | 0 | 0.06 s |
| **Unseen, total** | 38 | 477 | 478 | 477 | **100%** | **99.8%** | **0** | ≤ 0.06 s |
| **All six projects** | 116 | 1,358 | 1,516 | 1,358 | **100%** | **89.6%** | **0** | ≤ 0.14 s |

- **Every test file passed** in both unseen projects.
- **toolz has four files that load code by name at run time,** which pkv flags as "dynamic", and the map still missed nothing.

### In plain words

**Across six real projects, every file Python actually loaded when a test file ran was on pkv's map: 1,358 of 1,358, including two projects pkv had never seen.**
- No file was wrongly called "untested".
- Nine in ten of the map's links really happened; the rest are imports the code contains that these runs didn't load, which only makes pkv run a few extra tests.
- Each map took under a fifth of a second.

### Against the predictions

| | Result |
|---|---|
| **A5-P1** (recall ≥ 99% and M-pkv ≤ 1%, in seen and unseen separately) | ✅ 100% and 0 in both |
| **A5-P2** (≤ 2 files wrongly called untested) | ✅ 0 |
| **A5-P3** (precision ≥ 80%) | ✅ 89.6% (seen 84.9%, unseen 99.8%) |
| **A5-P4** (≤ 5 s per project) | ✅ ≤ 0.14 s |

**What this decides (rule above):** `pkv map` ships in 0.3, with its measured recall and precision stated in the README (D-054).

**Limits of this result:**
- Six well-kept, pure-Python libraries; nothing with compiled extensions, plugins loaded through entry points, or heavy dynamic loading.
- The ground truth is what each test *file* loads, not what each test calls.
- Perfect recall here doesn't prove it everywhere. It means no counter-example turned up in 1,358 real links.

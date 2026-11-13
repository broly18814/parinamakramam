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

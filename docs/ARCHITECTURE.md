# Technical architecture

This is how the two systems in this repository are built: what each part does, how the parts connect, and the rules that hold everywhere. It describes the code as it is (pkv 0.2.1, research code as of EXP-006; updated 11 November 2026). Words are explained in the [Glossary](GLOSSARY.md).

---

## Part 1: Parinama Verify (`pkv`), the product

### What it is, in one picture

> A building inspector who doesn't take the builder's word for it. They look at what changed, work out which safety checks it affects, run those checks themselves, look for checks that were quietly removed or weakened, photograph the building before and after, and sign one report.

### The flow of one `pkv check`

```
git ──▶ gitdiff ──▶ affected ──▶ runner ──▶ report ──▶ receipt (.json + .md)
           │            ▲            │          ▲
           │         imports         │          │
           └────────▶ tamper ──▶ moves ─────────┘
                        ▲                       │
                        └── not-run check ◀─────┘ (uses runner's results)
```

| Module | Job | Key idea |
|---|---|---|
| `gitdiff.py` | What changed, and the code's **fingerprint** (tree hash) | The fingerprint is built in an empty, temporary git index, so cached file timestamps can't fool it (the "racy git" bug, fixed in 0.0.2). Receipts in `.pkv/` are left out of both. |
| `imports.py` | The **import graph**: which file uses which | Built by reading code (Python's `ast`), never by running it. A module gets names relative to the repository and to each sub-project folder (`pyproject.toml`, `setup.cfg`, …). A file also depends on the `__init__.py` files of its packages. Dynamic imports and unreadable files are reported. |
| `affected.py` | Which test files the change could break, and **why** | Follows the graph backwards from each changed file. Settings files force a run of all tests in their scope; documentation changes force nothing; unknown files force all tests (the safe choice). Changed code that no test reaches is recorded as *untested*. |
| `runner.py` | Runs the selected tests and records evidence | One pytest process per sub-project, with a minimal environment that hides secrets, a time limit (with the process group stopped when it runs out), JUnit results parsed for counts and the exact tests run, and the fingerprint taken before and after. |
| `tamper.py` | Signs that the tests were **weakened** | Compares each test before and after: removed, hidden, fewer or looser checks, swallowed failures, fewer `parametrize` rows, new skips, checks that can never fail. Also finds tests that were selected but never ran, comparing the code with pytest's own list, and excusing tests the project already left out. |
| `moves.py` | Whether a "removed" test only **moved** | Excuses a disappearance only when every lost check reappears unchanged (style-independent) in a collected destination that resembles the original, with no added skip and no lost rows. It only ever turns suspicious findings into notices. |
| `report.py` | One verdict and a plain-language receipt | Order of seriousness: SUSPICIOUS > FAILED > UNVERIFIED > VERIFIED. Exit codes 4 / 1 / 3 / 0, and 2 if pkv itself couldn't finish. |
| `cli.py` | The `pkv` command: `check`, `affected`, `fresh`, `fingerprint` | Builds the import graph once and shares it. |

### The rules that hold everywhere (invariants)

1. **No false all-clear by design.** Any doubt lowers the verdict (to UNVERIFIED or SUSPICIOUS), never raises it.
2. **Nothing of the user's code is executed during analysis.** The only thing pkv runs is pytest, on the selected tests.
3. **Standard library only.** No outside packages, no network, no AI (D-014).
4. **Every sentence in a receipt comes from recorded data**, such as git, the graph, or pytest's results.
5. **Deterministic.** The same repository and change always give the same verdict; the practice sets enforce this in CI.

### How it's checked

| Layer | What it guards | Where |
|---|---|---|
| Lint and strict types | Code quality, and real bugs (mypy found two) | CI: `lint`, `types` |
| 107 self-checks, Python 3.10–3.14 | Each rule, plus a regression test for every bug | `product/verify/tests/` |
| 3 practice sets, as regression gates | That no verdict changes silently | `benchmark/`, CI job |
| Packaging | Builds, passes PyPI's checks, installs cleanly | CI: `package` |
| Dogfooding | pkv checks every change to this repository | CI: `dogfood` |
| The Marketplace copy of the action | It downloads the released pkv, checks its fingerprint, and runs | CI: `marketplace-action` |
| The published action | It works when used from its public repository, pinned to its commit | CI: `published-action` |
| Replay studies | Behaviour on real projects' real commits | `realworld/` (REAL-001, REAL-002) |

### Distribution

- PyPI (`parinama-verify`), published by `.github/workflows/publish.yml` with Trusted Publishing and the founder's approval;
- GitHub Releases (`pkv-vX.Y.Z`, with checksums);
- the GitHub Action `product/verify/action.yml`;
- its Marketplace copy, [broly18814/parinama-verify-action](https://github.com/broly18814/parinama-verify-action) (`v0.2.1` = commit `57ada48`). It is generated by `product/action/build_action.py`, downloads the pinned pkv wheel from PyPI, and is published by `scripts/publish-action.sh` ([how](../product/action/PUBLISHING.md)).

### Deliberate limits

- macOS and Linux only (the process-group stop is POSIX).
- pytest only.
- Python only.
- Not a sandbox: tests are code.
- File-level selection: libraries whose tests import everything get little narrowing (OI-10).

---

## Part 2: the research engine (`research/pevo`)

### What it is, in one picture

> A student solving number-list puzzles by trying combinations of known moves. After each round, it may save new shortcuts: combinations of moves, possibly with blanks. The question is whether saving the *right* shortcuts lets it solve more new puzzles with the same effort.

| Module | Job |
|---|---|
| `dsl.py` | The puzzle language: the starting building blocks (`map`, `filter`, `sort`, …), typed programs (`Node`), evaluation, and saved shortcuts (abstractions, including ones with action slots). |
| `tasks.py` | Makes puzzles from a seed: *patterned* ones (built from hidden compositions) and *random* ones (the control). |
| `enumerate.py` | The search: tries programs cheapest-first, keeps one per distinct result, and stops at a fixed **budget** of distinct values. That budget is the fair measure of effort (D-005). |
| `abstraction.py` | Proposes shortcuts from a set of programs, scored by how much they shorten them (MDL); fits the search habits; random shortcuts as a control. |
| `nearmiss.py` | EXP-002: finds the closest attempt for each unsolved puzzle. |
| `onestep.py` | EXP-002b: finds attempts that one more step turns into an exact answer, within a capped effort. |
| `codeblocks.py` | EXP-005, real code: turns each function into a normalised syntax tree, finds recurring shapes (with up to two gaps), picks 50 by how much they shorten the code, and measures how much they shorten *later* code. It only reads code; nothing is executed. |
| `learner.py` | The experimental conditions (A, B, C, C-random, D, E, cheat, C5) and the round-by-round loop, with a validation gate that keeps a shortcut only if it helps on held-out practice puzzles. |
| `run_exp001.py` | Runs conditions × seeds and writes one result file each. |
| `run_exp005.py` | EXP-005: reads each project's past and future functions through git, at the registered split commits, and writes one result file per project. |
| `grammarsearch.py` | EXP-006: a probabilistic grammar fitted on a project's past code (with or without learned blocks, or with a wider context), and a best-first search that counts how many guesses it needs to recover a hidden piece of future code exactly ([design](research/EXP-006-design.md)). |
| `run_exp006.py` | EXP-006: prepares each project, runs every condition in parallel worker processes, and writes one result file per project. |

**Experimental discipline built into the code:**
- seeds are fixed;
- the budget is identical across conditions;
- practice paper 100 is kept separate from the exam papers;
- the analysis scripts compute pre-registered tests with bootstrap confidence ranges;
- any change to shared code must reproduce all 200 EXP-001 result files exactly.

---

## How the two parts relate

They share **no code** (as of 10 November 2026; a planned EXP-007 would be the first to reuse pkv's test selection in research). They share a method: pre-registration, held-out tests, honest reporting of failures, and one CI. The research question (inventing building blocks) and the product (verifying changes) were chosen to run in parallel without overwhelming one founder, as the original 90-day roadmap required.

# TAMPER-BENCH

A fair, public test of tools that claim to catch an AI weakening tests. Plan v2, Track A, step A1. Design: [docs/product/TAMPER-BENCH-design.md](../../docs/product/TAMPER-BENCH-design.md). Seal and predictions: [SEAL.md](SEAL.md).

## In plain words

Each case is a tiny project with one change. Some changes hide a bug by weakening the tests: deleting one, skipping one, loosening a check, editing the expected answer to match the bug. Others are honest changes that should pass. Every tool runs on every case under the same rules, and every score is published, ours included.

**Every label is checked by running it, not by opinion.** For a cheat, the project's original tests must fail on the changed code (so a real bug is hidden). For an honest change, they must pass. The one exception is a documented change of behaviour, which must say so in the changelog.

## What's here

| Path | What it is |
|---|---|
| `tamperbench/projects.py` | the three small starting projects (`pricing`, `geo`, `ledger`) |
| `tamperbench/bugs.py` | realistic mistakes the cheats hide |
| `tamperbench/case.py` | the case format, the git builder, and the label check |
| `tamperbench/dev.py` | the **development set**: 30 public cases (20 cheats, 10 honest) |
| `tamperbench/detectors.py` | how each tool is run, and its verdict rule (fixed before the held-out run) |
| `tamperbench/run.py` | runs tools on cases and writes `runs.jsonl` and `RESULTS.md` |
| `results/dev/` | pkv 0.2.1 on the development set |
| `SEAL.md` | the held-out set's fingerprint and the predictions |

The **held-out set** (61 cases) is sealed: its fingerprint is in `SEAL.md`, and the file itself is published after the one held-out run.

## Categories

| Code | Cheat | Code | Honest |
|---|---|---|---|
| T1 | test deleted | H1 | refactor, tests unchanged |
| T2 | skip or xfail added | H2 | test moved or renamed |
| T3 | assertion removed | H3 | tests merged or generalised |
| T4 | assertion loosened | H4 | documented change of behaviour |
| T5 | expected value edited to match the bug | | |
| T6 | test deleted and a weaker one added | | |
| T7 | test made unable to fail | | |
| T8 | answer hard-coded in the code | | |
| T9 | tests turned off by configuration | | |

## Run it

From this folder:

```bash
uv run --no-project --python 3.14 --with pytest python -m tamperbench.validate
```

```bash
uv run --no-project --python 3.14 --with pytest python -m tamperbench.run --out results/dev --detectors pkv
```

Leaving out `--detectors` runs every tool in `detectors.py`. Each one is installed from PyPI at its pinned version with `uvx`.

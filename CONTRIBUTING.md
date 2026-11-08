# Contributing

This repository holds two things:
- `research/pevo`, the research code for the primitive-evolution experiments;
- `product/verify`, Parinama Verify (`pkv`).

Changes must keep both trustworthy.

## The rules

1. **Every change keeps all checks green.** CI must pass:
   - lint (`ruff`);
   - types (`mypy --strict` for pkv);
   - all tests, on Python 3.10, 3.12 and 3.14;
   - the BENCH-001 regression gate.
2. **Every bug fix comes with a regression test** that fails before the fix and passes after it. Say in the pull request that you checked both.
3. **No false "all clear".** pkv must never turn an uncertain situation into VERIFIED. When in doubt, run more tests or give a weaker verdict.
4. **Results are deterministic.** A benchmark or experiment must give the same answer every time it runs.
5. **Frozen research code stays frozen.** Code behind a published result (for example EXP-001) may be tidied only if the experiment is reproduced and every result file is identical. Say so in the changelog.
6. **Benchmarks are pre-registered.** Predictions are written down and committed *before* a benchmark runs. An improvement made after seeing results must also be scored on a held-out set written before the improvement.
7. **No private data.** Never add private source code, credentials or personal data, and never use code whose licence forbids it.
8. **Record decisions and changes.** Important decisions go in `governance/DECISION_LOG.md`, and user-visible changes go in `CHANGELOG.md`.

## Running everything locally

One command runs exactly what CI runs. Use it before every upload:

```bash
scripts/check-all.sh
```

Or step by step:

```bash
uvx ruff check product/verify research/pevo experiments
```

```bash
cd product/verify && uvx mypy --python-version 3.10 --strict pkv
```

```bash
cd product/verify && uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

```bash
cd research/pevo && uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

```bash
cd product/verify && uv run --no-project --python 3.14 --with pytest python benchmark/run_benchmark.py --check
```

## Commit messages

Start with one short line saying what changed, then a blank line, then *why*. If a commit fixes a bug, say how it was found and how the fix was tested.

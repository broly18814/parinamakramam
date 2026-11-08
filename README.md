# Parinamakramam (పరిణామక్రమం, "the course of evolution")

An independent AI research and product company, started with ₹0 on one MacBook.

- **The research question:** can a computer invent, keep and improve its *own* building blocks for thinking? And when is that better than cleverly combining a fixed set?
- **The first product:** **Parinama Verify** (`pkv`), an independent checker that confirms whether code written by an AI really works, and catches it when the tests were skipped, out of date, or quietly edited.

## Where to start

| If you want to… | Open |
|---|---|
| See where everything stands and what's next | [governance/PROJECT_STATE.md](governance/PROJECT_STATE.md) |
| **Learn every idea from zero**, step by step | [docs/LEARN.md](docs/LEARN.md) |
| Look up a word | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Read the research and the first experiment's results | [docs/research/R001…](docs/research/R001-primitive-evolution-prior-art-and-thesis.md) |
| Read why we chose this product | [docs/product/P001…](docs/product/P001-first-workflow-public-evidence.md) |
| See every important decision and why | [governance/DECISION_LOG.md](governance/DECISION_LOG.md) |
| See every experiment: predictions, then results | [governance/EXPERIMENT_REGISTRY.md](governance/EXPERIMENT_REGISTRY.md) |
| Use or read the checker tool | [product/verify/](product/verify/README.md) |
| See the experiment code | `research/pevo/` |
| See the raw results | [experiments/EXP-001/](experiments/EXP-001/README.md) |

## Re-run everything (Terminal commands)

Research self-checks (11) and the full experiment (about 1.5 minutes):

```bash
cd research/pevo
uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
python3 run_exp001.py --seeds 0-9 --out ../../experiments/EXP-001/results
python3 ../../experiments/EXP-001/analysis.py
```

Checker tool self-checks (54):

```bash
cd product/verify
uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

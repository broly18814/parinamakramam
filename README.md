# Parinamakramam ("the course of evolution")

An independent AI research and product company, started with ₹0 on one MacBook.

- **The research question:** can a computer invent, keep and improve its *own* building blocks for thinking? And when is that better than cleverly combining a fixed set?
- **The first product:** **Parinama Verify** (`pkv`), an independent checker that confirms whether code written by an AI really works, and catches it when the tests were skipped, out of date, or quietly edited.

## Where to start

| If you want to… | Open |
|---|---|
| See where everything stands and what's next | [governance/PROJECT_STATE.md](governance/PROJECT_STATE.md) |
| The 90-day roadmap and the status of every item | [governance/ROADMAP.md](governance/ROADMAP.md) |
| How the product and research code are built | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| See pkv catch a cheat in two minutes | [docs/product/DEMO.md](docs/product/DEMO.md) |
| Public usage numbers (no interviews) | [governance/ADOPTION.md](governance/ADOPTION.md) |
| **Learn every idea from zero**, step by step | [docs/LEARN.md](docs/LEARN.md) |
| Look up a word | [docs/GLOSSARY.md](docs/GLOSSARY.md) |
| Read the research and the first experiment's results | [docs/research/R001…](docs/research/R001-primitive-evolution-prior-art-and-thesis.md) |
| Read why we chose this product | [docs/product/P001…](docs/product/P001-first-workflow-public-evidence.md) |
| See every important decision and why | [governance/DECISION_LOG.md](governance/DECISION_LOG.md) |
| See every experiment: predictions, then results | [governance/EXPERIMENT_REGISTRY.md](governance/EXPERIMENT_REGISTRY.md) |
| Use or read the checker tool (version 0.2.1, on PyPI as `parinama-verify`) | [product/verify/](product/verify/README.md) |
| See every change, version by version | [CHANGELOG.md](CHANGELOG.md) |
| Report a security problem | [SECURITY.md](SECURITY.md) |
| Rules for changing the code | [CONTRIBUTING.md](CONTRIBUTING.md) |
| The legal terms for using this work | [LICENSE](LICENSE) (Apache-2.0) and [NOTICE](NOTICE) |
| See the experiment code | `research/pevo/` |
| See the raw results | [experiments/EXP-001/](experiments/EXP-001/README.md), `experiments/EXP-002/` |
| Read the real-code experiment (positive) | [docs/research/EXP-005-design.md](docs/research/EXP-005-design.md) |
| Read the next experiment's plan (written before any code; not run yet) | [docs/research/EXP-006-design.md](docs/research/EXP-006-design.md) |
| Read the second experiment and its last variant (both negative) | [EXP-002](docs/research/EXP-002-design.md), [EXP-002b](docs/research/EXP-002b-design.md) |

## Check everything (exactly what GitHub's robot runs)

```bash
scripts/check-all.sh
```

## Re-run the experiments (Terminal commands)

Research self-checks (46) and the full first experiment (about 1.5 minutes):

```bash
cd research/pevo
uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
python3 run_exp001.py --seeds 0-9 --out ../../experiments/EXP-001/results
python3 ../../experiments/EXP-001/analysis.py
```

Checker tool self-checks (102):

```bash
cd product/verify
uv run --no-project --python 3.14 --with pytest python -m pytest -q tests
```

## Licence

Everything in this repository is licensed under the **Apache License 2.0**; see [LICENSE](LICENSE) and [NOTICE](NOTICE).

In plain words: anyone may use, change and share this work, including for commercial purposes, as long as they keep the licence and notice files. The licence also grants a patent licence from contributors, and gives no warranty. Decision D-025 explains why we chose it.

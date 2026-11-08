# Parinamakramam (పరిణామక్రమం)

An independent AI research and product company, started from ₹0 on one MacBook Pro M4.

- **Research question:** can a system discover, stabilise and evolve its own computational building blocks, and when does that beat composing a fixed set?
- **First product:** an independent verifier for AI-written code changes (P001).

| Where | What |
|---|---|
| `governance/PROJECT_STATE.md` | **Start here.** Current state, next actions, risks |
| `governance/DECISION_LOG.md` | Every important decision and why |
| `governance/EXPERIMENT_REGISTRY.md` | Every experiment, pre-registered, with results |
| `docs/research/R001-…` | Prior art, thesis critique, formal definitions, EXP-001 results |
| `docs/product/P001-…` | First commercial workflow, from public evidence |
| `research/pevo/` | Primitive Evolution Engine prototype (EXP-001 code + tests) |
| `experiments/EXP-001/` | Raw results, summaries, analysis script |

```bash
cd research/pevo
uv run --python 3.14 --with pytest python -m pytest -q tests
python3 run_exp001.py --seeds 0-9 --out ../../experiments/EXP-001/results
python3 ../../experiments/EXP-001/analysis.py
```

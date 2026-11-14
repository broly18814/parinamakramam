"""EXP-007's contamination check (docs/research/EXP-007-design.md, section 3): reported, not tested.

Plain words: if the model had memorised these projects, it would fill holes in code it may have
read in training (from *before* the split) far better than in code written after its release.
So the same kind of task is drawn from the past, and the model alone is scored the same way.

The rule, fixed before this runs (it was left out of the build spec, so it runs after the
evaluation; it reads nothing from the evaluation's searches and changes no prediction):
- for each evaluation project, tasks are built from the past snapshot (the split commit, after
  design amendment 2's exclusions) by the same sampler and size limit as the evaluation's tasks;
- 100 of them are drawn with random.Random(0).sample;
- each gets the plain prompt (L0: no library), from the file at the split commit, and 16 guesses
  with the evaluation's decoding (temperature 0.8, top-p 0.95, at most 64 tokens), seed
  8_000_000 + task number;
- scored as the evaluation's model-alone control: any of 16, and top-1.
The comparison is with the model-alone L0 rate on the after-split tasks, from results/PROJECT.json.

Run with the environment that has mlx-lm, from the repository root:
    python experiments/EXP-007/contamination.py --work WORK --model PATH            # sample
    python3 experiments/EXP-007/contamination.py --work WORK --score                # score only
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parents[1] / "research" / "pevo"))

import run_exp005 as r5  # noqa: E402
import run_exp007 as r7  # noqa: E402
from pevo.codeblocks import shape  # noqa: E402
from pevo.grammarsearch import base_templates  # noqa: E402
from pevo.llmguide import direct_scores, make_hole, piece_node, prompt, sample_tasks_with_nodes  # noqa: E402

N_TASKS, SEED_BASE = 100, 8_000_000
OUT = HERE / "results" / "contamination"


def before_tasks(name: str, src: Path) -> tuple[list, list]:
    p, repo = r7.PROJECTS[name], src / name
    past = r7.snapshot(repo, p["split"])
    inventory = {t for tree in past.values() for t in base_templates(tree)}
    tasks = random.Random(0).sample(sample_tasks_with_nodes(past, inventory, max_size=r7.MAX_TARGET), N_TASKS)
    files: dict[str, str] = {}
    holes = []
    for t, fn, node in tasks:
        text = files.setdefault(t.path, r5.git(repo, "show", f"{p['split']}:{t.path}"))
        holes.append(make_hole(text, fn, node))
    return tasks, holes


def sample(a: argparse.Namespace) -> None:
    import mlx.core as mx
    from mlx_lm import batch_generate, load
    from mlx_lm.sample_utils import make_sampler

    model, tok = load(a.model)
    sampler = make_sampler(temp=r7.TEMP, top_p=r7.TOP_P)
    OUT.mkdir(parents=True, exist_ok=True)
    for name in r7.SETS["evaluation"]:
        _tasks, holes = before_tasks(name, a.work / "src")
        path = OUT / f"{name}-before-samples.jsonl"
        done = {r["task"] for r in map(json.loads, path.read_text().splitlines()) if r} if path.exists() else set()
        with path.open("a") as fh:
            for i, h in enumerate(holes):
                if i in done:
                    continue
                ids = tok.apply_chat_template([{"role": "user", "content": prompt(h, None)}],
                                              add_generation_prompt=True, enable_thinking=False)
                mx.random.seed(SEED_BASE + i)
                t0 = time.perf_counter()
                r = batch_generate(model, tok, prompts=[ids] * r7.K_SAMPLES, max_tokens=r7.MAX_NEW, sampler=sampler,
                                   return_logprobs=True, completion_batch_size=r7.K_SAMPLES)
                lps = [sum(x) / len(x) if x else float("-inf") for x in r.logprobs]
                fh.write(json.dumps({"task": i, "seed": SEED_BASE + i, "seconds": round(time.perf_counter() - t0, 3),
                                     "texts": r.texts, "mean_logprob": lps}) + "\n")
                fh.flush()
                if i % 20 == 0:
                    print(f"{name}: before-split task {i + 1}/{N_TASKS}", flush=True)


def score(a: argparse.Namespace) -> str:
    lines = ["EXP-007 contamination check (reported, not tested): the model alone, plain prompt (L0)", "",
             f"{'project':10s}{'before: any16':>15s}{'top1':>7s}{'after: any16':>15s}{'top1':>7s}{'gap (any16)':>14s}"]
    for name in r7.SETS["evaluation"]:
        tasks, holes = before_tasks(name, a.work / "src")
        rows = {r["task"]: r for r in map(json.loads, (OUT / f"{name}-before-samples.jsonl").read_text().splitlines())
                if r}
        anyk = top1 = 0
        for i, (t, _fn, _node) in enumerate(tasks):
            pieces = [piece_node(holes[i], x) for x in rows[i]["texts"]]
            x, y = direct_scores(t.target, [None if p is None else shape(p) for p in pieces], rows[i]["mean_logprob"])
            anyk, top1 = anyk + x, top1 + y
        after = json.loads((HERE / "results" / f"{name}.json").read_text())["tasks"]
        a_any = 100 * sum(t["direct"]["L0"]["any"] for t in after) / len(after)
        a_top = 100 * sum(t["direct"]["L0"]["top1"] for t in after) / len(after)
        b_any, b_top = 100 * anyk / N_TASKS, 100 * top1 / N_TASKS
        lines.append(f"{name:10s}{b_any:15.1f}{b_top:7.1f}{a_any:15.1f}{a_top:7.1f}{b_any - a_any:+14.1f}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--model")
    ap.add_argument("--score", action="store_true")
    args = ap.parse_args()
    if args.score:
        print(score(args), end="")
    else:
        sample(args)

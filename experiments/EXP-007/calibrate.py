"""Apply EXP-007's registered calibration rules (docs/research/EXP-007-design.md, section 6) to the
tomli calibration run. Nothing here looks at an evaluation project's searches.

Rule (model, design 4.3): the largest candidate whose licence allows commercial use, that runs in
    MLX on this Mac, and samples all tomli calibration tasks in 2 hours or less.
Rule (lambda, design 6.2): from {0.5, 0.9}, the value with the higher L0.G3 solve rate at B on tomli.
Rule (k, design 7): if sampling the evaluation is estimated to take more than 30 hours, k drops
    from 16 to 8. The estimate is tomli's mean seconds per (task, prompt) x 3 prompts x the
    evaluation's task count (given on the command line once the split is computed; until then,
    EXP-006's evaluation size, 800, is used as a stand-in).

Run from the repository root:
    python3 experiments/EXP-007/calibrate.py [run folder] [evaluation task count]
"""
import json
import sys
from pathlib import Path

run = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "calibration" / "run1"
eval_tasks = int(sys.argv[2]) if len(sys.argv) > 2 else 800
d = json.loads((run / "tomli.json").read_text())
rows = [json.loads(x) for x in (run / "tomli-samples.jsonl").read_text().splitlines() if x]
tasks, b = d["tasks"], d["budget"]


def rate(cell: str, budget: int) -> float:
    return sum(1 for t in tasks if t["effort"][cell] is not None and t["effort"][cell] <= budget) / len(tasks)


def direct(v: str, which: str) -> float:
    return sum(t["direct"][v][which] for t in tasks) / len(tasks)


print(f"EXP-007 calibration on tomli: {len(tasks)} tasks; budget B = {b:,} (searches to {d['budget_max']:,})\n")
print("solved, out of 100 tasks:")
print(f"{'cell':12s}{'at B':>8s}{'at 2B':>8s}")
for c in d["cells"]:
    print(f"{c:12s}{rate(c, b) * 100:8.1f}{rate(c, 2 * b) * 100:8.1f}")
print("\nmodel alone (any of 16 / top-1):")
for v in ("L0", "L1", "L2"):
    readable = sum(t["readable"][v] for t in tasks) / (16 * len(tasks))
    print(f"  {v}: {direct(v, 'any') * 100:5.1f} / {direct(v, 'top1') * 100:5.1f}"
          f"   readable guesses {readable * 100:.0f}%")

hours = d["sampling_seconds"] / 3600
print(f"\nRule (model): sampling all tomli tasks took {hours:.2f} h (limit 2 h)  ->  "
      f"{'Qwen3.6-35B-A3B qualifies' if hours <= 2 else 'too slow: the next candidate'}")
lam = {float(c.split('@')[1]): rate(c, b) for c in d["cells"] if c.startswith("L0G3@")}
chosen = max(sorted(lam), key=lambda x: lam[x])          # a tie goes to the smaller lambda
print("Rule (lambda): L0.G3 at B = " + ", ".join(f"{k}: {v * 100:.1f}" for k, v in sorted(lam.items()))
      + f"  ->  lambda = {chosen}")
per = sum(r["seconds"] for r in rows) / len(rows)
est = per * 3 * eval_tasks / 3600
print(f"Rule (k): {per:.2f} s per (task, prompt) x 3 x {eval_tasks} evaluation tasks = {est:.1f} h (limit 30 h)"
      f"  ->  k = {16 if est <= 30 else 8}")

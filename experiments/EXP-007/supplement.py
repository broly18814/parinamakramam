"""EXP-007's reported-only numbers (design 4.4, 4.5 and the stop rule's condition), from the saved
results. Exploratory: written after the run, so nothing here is a test of a prediction.

- L1 - L0 at B under each guidance level, with the same cluster bootstrap as analysis.py
  (10,000 resamples, seed 0): the stop rule's second branch asks whether it is positive anywhere.
- The double-search control at every guidance level: L1 at B against L0 at 2B.
- The model alone, top-1, next to any-of-16.
- The share of tasks the past's rules can build at all, and the share each cell found within 5B.
- Sampling time per task.

Run from the repository root:  python3 experiments/EXP-007/supplement.py
"""
import json
import random
import statistics
from pathlib import Path

HERE = Path(__file__).parent
PROJECTS = ("fastapi", "black")
RESAMPLES = 10_000


def main() -> str:
    data = {p: json.loads((HERE / "results" / f"{p}.json").read_text()) for p in PROJECTS}
    b, lam = data[PROJECTS[0]]["budget"], data[PROJECTS[0]]["lambdas"][0]
    g = {"G1": ("L0G1", "L1G1"), "G2": ("L0G2", "L1G2"), "G3": (f"L0G3@{lam}", f"L1G3@{lam}")}

    def solved(t: dict, cell: str, budget: int) -> int:
        e = t["effort"][cell]
        return int(e is not None and e <= budget)

    measures = {}
    for lvl, (c0, c1) in g.items():
        measures[f"L1-L0 {lvl}"] = lambda t, c0=c0, c1=c1: solved(t, c1, b) - solved(t, c0, b)
        measures[f"L1@B-L0@2B {lvl}"] = lambda t, c0=c0, c1=c1: solved(t, c1, b) - solved(t, c0, 2 * b)

    groups = {}
    for p in PROJECTS:
        gr: dict = {}
        for t in data[p]["tasks"]:
            gr.setdefault((t["path"], t["function"]), []).append(t)
        groups[p] = [(len(ts), {k: sum(f(t) for t in ts) for k, f in measures.items()}) for ts in gr.values()]

    def pooled(idx: dict) -> dict:
        out = {}
        for k in measures:
            out[k] = statistics.fmean(sum(groups[p][i][1][k] for i in idx[p]) / sum(groups[p][i][0] for i in idx[p])
                                      for p in PROJECTS)
        return out

    point = pooled({p: range(len(groups[p])) for p in PROJECTS})
    rng = random.Random(0)
    boot = {k: [] for k in measures}
    for _ in range(RESAMPLES):
        idx = {p: [rng.randrange(len(groups[p])) for _ in groups[p]] for p in PROJECTS}
        for k, v in pooled(idx).items():
            boot[k].append(v)

    L = ["EXP-007 supplement (exploratory, written after the run; not a test of any prediction)", "",
         "Pooled differences, points out of 100 [95% range]:"]
    for k in measures:
        xs = sorted(boot[k])
        lo, hi = xs[int(0.025 * RESAMPLES)], xs[int(0.975 * RESAMPLES) - 1]
        L.append(f"  {k:18s}{point[k] * 100:+6.1f}  [{lo * 100:+6.1f}, {hi * 100:+6.1f}]")

    L += ["", f"{'':40s}" + "".join(f"{p:>10s}" for p in PROJECTS)]

    def row(label: str, pred) -> None:
        """The share of tasks, out of 100, for which pred(task) holds, per project."""
        L.append(f"{label:40s}" + "".join(f"{100 * statistics.fmean(map(pred, data[p]['tasks'])):10.1f}"
                                          for p in PROJECTS))

    for v in ("L0", "L1", "L2"):
        row(f"model alone {v}, any of 16", lambda t, v=v: t["direct"][v]["any"])
        row(f"model alone {v}, top-1", lambda t, v=v: t["direct"][v]["top1"])
    row("buildable from the past's rules", lambda t: t["derivable"])
    for c in data[PROJECTS[0]]["cells"]:
        row(f"found within 5B, {c}", lambda t, c=c: t["effort"][c] is not None)
    for c in (f"L0G3@{lam}", f"L1G3@{lam}"):
        row(f"found, not buildable before, {c}", lambda t, c=c: t["effort"][c] is not None and not t["derivable"])
    L.append(f"{'tasks':40s}" + "".join(f"{data[p]['tasks_total']:10d}" for p in PROJECTS))
    L.append(f"{'sampling, seconds per task (3 prompts)':40s}"
             + "".join(f"{data[p]['sampling_seconds'] / data[p]['tasks_total']:10.1f}" for p in PROJECTS))
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    print(main(), end="")

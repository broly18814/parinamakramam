"""Pre-registered hypothesis tests for EXP-007 (docs/research/EXP-007-design.md, section 5).
Written and committed before the evaluation run, after the freeze (D-057).

Solve rate at budget b, per project = tasks found within b states / all tasks (tasks a cell can't
derive count as unsolved). Pooled = the mean over the evaluation projects. 95% percentile
bootstrap: 10,000 resamples (seed 0) of each project's future functions with replacement,
carrying every task of a resampled function (a cluster bootstrap), in one fixed loop.
Differences are paired: both sides use the same resample. Points are out of 100.

H23  (L1.G3 - L0.G3) - (L1.G1 - L0.G1) > 0, range excluding 0, and L1.G3 - L0.G3 >= +3 points
H24  L0.G3 - L0.G2 > 0, range excluding 0
H25  best G3 cell - the model alone (any of 16) with that cell's prompt > 0, range excluding 0.
     "Best" = the G3 cell with the highest pooled solve rate at B (fixed before the run).
H26  L2.G3 - L1.G3 > 0, range excluding 0
H27  L1.G3 at B - L0.G3 at 2B > 0, range excluding 0

Run from the repository root:
    python3 experiments/EXP-007/analysis.py                     # the evaluation results
    python3 experiments/EXP-007/analysis.py FOLDER PROJECT ...  # any other folder (e.g. calibration)
"""
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
RESAMPLES = 10_000
VARIANTS = ("L0", "L1", "L2")


def main(folder: Path, projects: list) -> str:
    data = {p: json.loads((folder / f"{p}.json").read_text()) for p in projects}
    b = data[projects[0]]["budget"]
    lam = data[projects[0]]["lambdas"]
    if len(lam) != 1 or any(data[p]["lambdas"] != lam or data[p]["budget"] != b for p in projects):
        raise SystemExit("every project must be run with the one frozen lambda and the same budget")
    g3 = {v: f"{v}G3@{lam[0]}" for v in VARIANTS}
    cells = ["L0G1", "L1G1", "L0G2", "L1G2", *g3.values()]
    keys = [(c, b) for c in cells] + [(g3["L0"], 2 * b)] + [("direct", v) for v in VARIANTS]

    fn = {}
    for p in projects:
        groups: dict = {}
        for t in data[p]["tasks"]:
            groups.setdefault((t["path"], t["function"]), []).append(t)
        rows = list(groups.values())
        solved = {k: [0] * len(rows) for k in keys}
        for i, ts in enumerate(rows):
            for t in ts:
                for k in keys:
                    if k[0] == "direct":
                        solved[k][i] += t["direct"][k[1]]["any"]
                    else:
                        e = t["effort"][k[0]]
                        solved[k][i] += e is not None and e <= k[1]
        fn[p] = {"solved": solved, "n": [len(ts) for ts in rows]}

    def rates(p: str, idx) -> dict:
        f = fn[p]
        n = sum(f["n"][i] for i in idx)
        return {k: sum(f["solved"][k][i] for i in idx) / n for k in keys}

    def pooled(per: dict, k) -> float:
        return statistics.fmean(per[p][k] for p in projects)

    point = {p: rates(p, range(len(fn[p]["n"]))) for p in projects}
    best = max(VARIANTS, key=lambda v: (pooled(point, (g3[v], b)), -VARIANTS.index(v)))

    def measures(per: dict) -> dict:
        gain = {g: pooled(per, (f"L1{g}", b)) - pooled(per, (f"L0{g}", b)) for g in ("G1",)}
        gain3 = pooled(per, (g3["L1"], b)) - pooled(per, (g3["L0"], b))
        return {
            "H23": gain3 - gain["G1"],
            "H23_gain_G3": gain3,
            "H24": pooled(per, (g3["L0"], b)) - pooled(per, ("L0G2", b)),
            "H25": pooled(per, (g3[best], b)) - pooled(per, ("direct", best)),
            "H26": pooled(per, (g3["L2"], b)) - pooled(per, (g3["L1"], b)),
            "H27": pooled(per, (g3["L1"], b)) - pooled(per, (g3["L0"], 2 * b)),
        }

    est = measures(point)
    rng = random.Random(0)
    boot = {k: [] for k in est}
    for _ in range(RESAMPLES):
        per = {p: rates(p, [rng.randrange(len(fn[p]["n"])) for _ in fn[p]["n"]]) for p in projects}
        for k, v in measures(per).items():
            boot[k].append(v)

    def ci(k: str) -> tuple:
        xs = sorted(boot[k])
        return xs[int(0.025 * RESAMPLES)], xs[int(0.975 * RESAMPLES) - 1]

    def pts(x: float) -> str:
        return f"{x * 100:+6.1f}"

    L = [f"EXP-007 results: {', '.join(projects)}; B = {b:,}; lambda = {lam[0]}; {RESAMPLES:,} resamples, seed 0", "",
         "Solve rate at B, out of 100:", f"{'cell':16s}" + "".join(f"{p:>12s}" for p in projects) + f"{'pooled':>10s}"]
    for k in [(c, b) for c in cells] + [(g3["L0"], 2 * b)] + [("direct", v) for v in VARIANTS]:
        label = f"{k[0]} at 2B" if k == (g3["L0"], 2 * b) else (f"model {k[1]}" if k[0] == "direct" else k[0])
        each = "".join(f"{point[p][k] * 100:12.1f}" for p in projects)
        L.append(f"{label:16s}{each}{pooled(point, k) * 100:10.1f}")
    L += ["", f"Best G3 cell (for H25): {g3[best]}", "", "Predictions (pooled difference [95% range]):"]
    verdict = {
        "H23": est["H23"] > 0 and ci("H23")[0] > 0 and est["H23_gain_G3"] >= 0.03,
        "H24": ci("H24")[0] > 0, "H25": ci("H25")[0] > 0, "H26": ci("H26")[0] > 0, "H27": ci("H27")[0] > 0,
    }
    for k in ("H23", "H23_gain_G3", "H24", "H25", "H26", "H27"):
        lo, hi = ci(k)
        tag = "" if k == "H23_gain_G3" else ("  PASS" if verdict[k] else "  FAIL")
        L.append(f"  {k:12s}{pts(est[k])}  [{pts(lo)}, {pts(hi)}]{tag}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    if len(sys.argv) > 2:
        print(main(Path(sys.argv[1]), sys.argv[2:]), end="")
    else:
        print(main(HERE / "results", ["fastapi", "black"]), end="")

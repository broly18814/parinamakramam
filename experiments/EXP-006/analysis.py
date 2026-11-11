"""Pre-registered hypothesis tests for EXP-006 (docs/research/EXP-006-design.md, section 5).

Solve rate at budget b, per project = tasks found within b states / all tasks (tasks
that can't be derived count as unsolved). Pooled = mean over the three evaluation
projects. 95% percentile bootstrap: 10,000 resamples (seed 0) of each project's future
functions with replacement, carrying every task and compression row of a resampled
function (a cluster bootstrap, because tasks from one function aren't independent),
in one fixed loop. Differences are paired: both sides use the same resample.

Run from the repository root:
    python3 experiments/EXP-006/analysis.py
(or, to try it on another folder: analysis.py FOLDER PROJECT [PROJECT ...])

Written and committed before the evaluation run.
"""
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
CONDS = ["NONE", "OWN", "RANDOM", "OTHER", "ORACLE", "CTX2"]
LIBS = ["OWN", "RANDOM", "OTHER", "ORACLE"]
RESAMPLES = 10_000


def pts(x: float) -> str:
    return f"{x * 100:+6.1f}"


def main(folder: Path, projects: list) -> None:
    data = {p: json.loads((folder / f"{p}.json").read_text()) for p in projects}
    budget = {p: data[p]["budget"] for p in projects}
    if len(set(budget.values())) != 1:
        raise SystemExit("projects were run with different budgets")
    b = budget[projects[0]]
    keys = [(c, b) for c in CONDS] + [("NONE", 2 * b), ("NONE", 5 * b)]

    # Per project, per future function: tasks solved for each (condition, budget), tasks, and sizes.
    fn = {}
    for p in projects:
        rows = data[p]["compression"]
        index = {(r["path"], r["function"]): i for i, r in enumerate(rows)}
        solved = {k: [0] * len(rows) for k in keys}
        ntasks = [0] * len(rows)
        for t in data[p]["tasks"]:
            i = index[(t["path"], t["function"])]
            ntasks[i] += 1
            for c, bb in keys:
                e = t["effort"][c]
                if e is not None and e <= bb:
                    solved[(c, bb)][i] += 1
        fn[p] = {"solved": solved, "ntasks": ntasks, "size": [r["size"] for r in rows],
                 "after": {c: [r[c] for r in rows] for c in LIBS}}

    def stats(p: str, idx) -> dict:
        f = fn[p]
        n = sum(f["ntasks"][i] for i in idx)
        out = {k: (sum(f["solved"][k][i] for i in idx) / n if n else 0.0) for k in keys}
        total = sum(f["size"][i] for i in idx)
        for c in LIBS:
            out[("comp", c)] = 1 - sum(f["after"][c][i] for i in idx) / total
        return out

    point = {p: stats(p, range(len(fn[p]["ntasks"]))) for p in projects}

    def pooled(per: dict, k) -> float:
        return statistics.fmean(per[p][k] for p in projects)

    def measures(per: dict) -> dict:
        own, none = pooled(per, ("OWN", b)), pooled(per, ("NONE", b))
        oracle = pooled(per, ("ORACLE", b))
        return {
            "H16": own - none,
            "H17": own - pooled(per, ("NONE", 2 * b)),
            "H18": own - pooled(per, ("OTHER", b)),
            "H19": own - pooled(per, ("CTX2", b)),
            "H20": own - pooled(per, ("RANDOM", b)),
            "H21": (own - none) / (oracle - none) if oracle - none > 0 else float("nan"),
            "H22": oracle - none,
            "R13": pooled(per, ("comp", "OWN")) - pooled(per, ("comp", "RANDOM")),
        }

    est = measures(point)
    rng = random.Random(0)
    boot: dict = {h: [] for h in est}
    for _ in range(RESAMPLES):
        per = {}
        for p in projects:
            n = len(fn[p]["ntasks"])
            per[p] = stats(p, rng.choices(range(n), k=n))
        for h, v in measures(per).items():
            boot[h].append(v)
    ci = {}
    for h, v in boot.items():
        v = sorted(x for x in v if x == x)          # drop undefined ratios (NaN)
        ci[h] = (v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]) if v else (float("nan"), float("nan"))

    print("EXP-006: do learned building blocks make search for real code cheaper? (run once, after the freeze)\n")
    print(f"Primary budget B = {b:,} states; searches ran to {5 * b:,}. Scores: tasks found, out of 100.\n")
    head = "".join(f"{c:>8s}" for c in CONDS)
    print(f"{'project':12s} {'tasks':>6s} {'deriv':>6s}{head}  NONE@2B  NONE@5B")
    for p in projects:
        d, s = data[p], point[p]
        print(f"{p:12s} {d['tasks_total']:6d} {d['tasks_derivable'] / d['tasks_total'] * 100:5.1f}%"
              + "".join(f"{s[(c, b)] * 100:8.1f}" for c in CONDS)
              + f"  {s[('NONE', 2 * b)] * 100:7.1f}  {s[('NONE', 5 * b)] * 100:7.1f}")
    print(f"{'pooled':12s} {'':6s} {'':6s}" + "".join(f"{pooled(point, (c, b)) * 100:8.1f}" for c in CONDS)
          + f"  {pooled(point, ('NONE', 2 * b)) * 100:7.1f}  {pooled(point, ('NONE', 5 * b)) * 100:7.1f}")

    print("\nCompression of the future functions (EXP-005's measure, R13):")
    print(f"{'project':12s}" + "".join(f"{c:>8s}" for c in LIBS))
    for p in projects:
        print(f"{p:12s}" + "".join(f"{point[p][('comp', c)] * 100:7.1f}%" for c in LIBS))
    print(f"{'pooled':12s}" + "".join(f"{pooled(point, ('comp', c)) * 100:7.1f}%" for c in LIBS))

    def rng_s(h: str) -> str:
        lo, hi = ci[h]
        return f"[{lo * 100:+.1f}, {hi * 100:+.1f}]"

    v = {}
    all16 = all(point[p][("OWN", b)] > point[p][("NONE", b)] for p in projects)
    lo = ci["H16"][0]
    v["H16"] = ("PASS" if est["H16"] >= 0.03 and lo > 0 and all16 else
                "FAIL" if lo <= 0 or est["H16"] < 0 else "neither (below +3 points, or not positive in every project)")
    for h in ("H17", "H18", "H19", "H20"):
        v[h] = "PASS" if ci[h][0] > 0 else "FAIL"
    frac = est["H21"]
    v["H21"] = ("undefined (ORACLE does not beat NONE)" if frac != frac else
                "PASS" if frac >= 0.30 else "FAIL" if frac < 0.10 else "neither (10-30%)")
    v["H22"] = "PASS" if est["H22"] >= 0.03 and ci["H22"][0] > 0 else "FAIL"
    all13 = all(point[p][("comp", "OWN")] > point[p][("comp", "RANDOM")] for p in projects)
    lo = ci["R13"][0]
    v["R13"] = ("PASS" if est["R13"] >= 0.03 and lo > 0 and all13 else
                "FAIL" if lo <= 0 else "neither (below +3 points, or not positive in every project)")

    print()
    print(f"H16 OWN - NONE at B [primary]            {pts(est['H16'])} pts {rng_s('H16')}  "
          f"positive in all: {'yes' if all16 else 'no'}  -> {v['H16']}")
    print(f"H17 OWN at B - NONE at 2B [compute]      {pts(est['H17'])} pts {rng_s('H17')}  -> {v['H17']}")
    print(f"H18 OWN - OTHER                          {pts(est['H18'])} pts {rng_s('H18')}  -> {v['H18']}")
    print(f"H19 OWN - CTX2 [simpler system]          {pts(est['H19'])} pts {rng_s('H19')}  -> {v['H19']}")
    print(f"H20 OWN - RANDOM                         {pts(est['H20'])} pts {rng_s('H20')}  -> {v['H20']}")
    h21 = "  n/a " if frac != frac else f"{frac * 100:6.1f}"
    lo, hi = ci["H21"]
    print(f"H21 (OWN-NONE) / (ORACLE-NONE)           {h21} %   [{lo * 100:.1f}, {hi * 100:.1f}]  -> {v['H21']}")
    print(f"H22 ORACLE - NONE [the test works]       {pts(est['H22'])} pts {rng_s('H22')}  -> {v['H22']}")
    print(f"R13 compression OWN - RANDOM [EXP-005]   {pts(est['R13'])} pts {rng_s('R13')}  "
          f"positive in all: {'yes' if all13 else 'no'}  -> {v['R13']}")

    print("\nDescriptive (not tests):")
    for lo_s, hi_s in ((4, 6), (7, 9), (10, 12)):
        cells = []
        for c in ("NONE", "OWN", "CTX2", "ORACLE"):
            rates = []
            for p in projects:
                ts = [t for t in data[p]["tasks"] if lo_s <= t["size"] <= hi_s]
                if ts:
                    rates.append(sum(1 for t in ts if t["effort"][c] is not None and t["effort"][c] <= b) / len(ts))
            cells.append(f"{c} {statistics.fmean(rates) * 100:5.1f}" if rates else f"{c}   n/a")
        print(f"  target size {lo_s:2d}-{hi_s:2d}: " + "   ".join(cells))
    ratios = [t["effort"]["NONE"] / t["effort"]["OWN"] for p in projects for t in data[p]["tasks"]
              if t["effort"]["NONE"] is not None and t["effort"]["OWN"] is not None]
    if ratios:
        print(f"  median effort NONE / OWN, on the {len(ratios)} tasks both found within {5 * b:,}: "
              f"{statistics.median(ratios):.2f}")
    own_found = [t for p in projects for t in data[p]["tasks"]
                 if t["effort"]["OWN"] is not None and t["effort"]["OWN"] <= b]
    if own_found:
        share = sum(t["used_block"]["OWN"] for t in own_found) / len(own_found)
        print(f"  OWN's solutions within B whose route used a block: {share * 100:.1f}% of {len(own_found)}")

    print("\nReading (registered in the design, section 5):")
    if v["H22"] == "FAIL":
        print("  H22 failed: this test can't detect even the cheat library, so H16 and H21 are uninformative.")
        print("  Recorded as 'the test can't detect a library', not as a failure of the idea.")
    elif v["H16"] == "FAIL":
        print("  H16 failed: blocks from history don't make this search cheaper; their value is descriptive only.")
        print("  Stop rule engaged: the block-library line pauses on real code; the next pre-registration is about"
              " guidance.")
    elif v["H16"] == "PASS" and v["H17"] == "FAIL" and v["H19"] == "FAIL":
        print("  H16 passed, but both H17 and H19 failed.")
        print("  Stop rule engaged: the block-library line pauses on real code; the next pre-registration is about"
              " guidance.")
    elif v["H16"] == "PASS" and v["H17"] == "PASS":
        print("  H16 and H17 passed: blocks from history make search materially cheaper on real code.")
        print("  Next: EXP-007, the library inside a search checked by running tests (to be pre-registered).")
    elif v["H16"] == "PASS":
        print("  H16 passed and H17 failed: the benefit is real but smaller than doubling the search.")
    else:
        print("  H16 is neither a pass nor a fail, so no registered reading applies; it is reported as measured.")
    if v["H19"] == "FAIL" and v["H22"] != "FAIL":
        print("  H19 failed: sharper habits do at least as well as the blocks, so the simpler system is preferred.")


if __name__ == "__main__" and len(sys.argv) > 1:
    main(Path(sys.argv[1]), sys.argv[2:])
else:
    main(HERE / "results", ["packaging", "urllib3", "httpx"])

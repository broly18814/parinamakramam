"""EXP-001 runner: fixed vs composition vs growing vs evolving primitive substrates.

Usage (from research/pevo):
    python3 run_exp001.py --seeds 0-9 --out ../../experiments/EXP-001/results
    python3 run_exp001.py --seeds 100 --conds C0_fixed,C3_evolve --out /tmp/x   # calibration

Writes one JSON per (dist, seed, condition) plus summary.json / summary.md with
seed-level bootstrap 95% CIs and paired differences.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import random
import statistics
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from pevo.dsl import base_prods  # noqa: E402
from pevo.learner import ALL_CONDITIONS, CONDITIONS, RunConfig, run_condition  # noqa: E402
from pevo.tasks import build_suite  # noqa: E402


def parse_seeds(s):
    out = []
    for part in s.split(","):
        if "-" in part:
            a, b = part.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(part))
    return out


def code_hashes():
    h = {}
    for p in [*sorted((HERE / "pevo").glob("*.py")), HERE / "run_exp001.py"]:
        h[str(p.relative_to(HERE))] = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    return h


def job(args):
    dist, seed, conds, cfgd, outdir = args
    cfg = RunConfig(**cfgd)
    lib = base_prods()
    Xtr, Xho, train, test = build_suite(dist, seed, lib)
    res = []
    for c in conds:
        t0 = time.perf_counter()
        out = run_condition(ALL_CONDITIONS[c], cfg, Xtr, Xho, train, test, seed)
        out.update({"dist": dist, "seed": seed, "wall_seconds": round(time.perf_counter() - t0, 2),
                    "n_train": len(train), "n_test": len(test)})
        Path(outdir, "raw").mkdir(parents=True, exist_ok=True)
        Path(outdir, "raw", f"{dist}_s{seed}_{c}.json").write_text(json.dumps(out, indent=1))
        res.append({k: out[k] for k in ("dist", "seed", "condition", "wall_seconds", "total_values")}
                   | {"test_strict": out["rounds"][-1]["test_strict"],
                      "learn_strict": out["rounds"][-1]["learn_strict"],
                      "by_level": _by_level(out["test_per_task"])})
    return res


def _by_level(per_task):
    d = defaultdict(list)
    for v in per_task.values():
        d[v["level"]].append(v["strict"])
    return {str(k): sum(v) / len(v) for k, v in sorted(d.items())}


def boot_ci(xs, n=10000, seed=0):
    rng = random.Random(seed)
    if len(xs) < 2:
        return (xs[0], xs[0]) if xs else (float("nan"),) * 2
    ms = sorted(statistics.fmean(rng.choices(xs, k=len(xs))) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def summarise(rows, conds):
    S = {}
    for dist in sorted({r["dist"] for r in rows}):
        D = [r for r in rows if r["dist"] == dist]
        by = defaultdict(dict)
        for r in D:
            by[r["condition"]][r["seed"]] = r
        seeds = sorted({r["seed"] for r in D})
        S[dist] = {}
        for c in conds:
            xs = [by[c][s]["test_strict"] for s in seeds if s in by[c]]
            entry = {"mean": statistics.fmean(xs), "ci95": boot_ci(xs), "n_seeds": len(xs),
                     "mean_compute_values": statistics.fmean(by[c][s]["total_values"] for s in seeds),
                     "mean_wall_s": statistics.fmean(by[c][s]["wall_seconds"] for s in seeds)}
            levels = sorted({k for s in seeds for k in by[c][s]["by_level"]})
            entry["by_level"] = {k: statistics.fmean(by[c][s]["by_level"][k] for s in seeds) for k in levels}
            for ref in ("C0_fixed", "C1_compose", "C2_grow"):
                if ref in by and ref != c:
                    d = [by[c][s]["test_strict"] - by[ref][s]["test_strict"] for s in seeds]
                    entry[f"diff_vs_{ref}"] = {"mean": statistics.fmean(d), "ci95": boot_ci(d),
                                               "wins": sum(x > 0 for x in d), "ties": sum(x == 0 for x in d),
                                               "losses": sum(x < 0 for x in d)}
            S[dist][c] = entry
    return S


def to_md(S, meta):
    lines = ["# EXP-001 summary\n", f"Generated {meta['timestamp']} · budget {meta['config']['budget']} values/round · "
             f"rounds {meta['config']['rounds']} · seeds {meta['seeds']}\n",
             "Metric: strict test solve rate (correct on 6 training inputs AND 4 held-out inputs), "
             "final round. CI = bootstrap over seeds.\n"]
    for dist, E in S.items():
        lines.append(f"\n## D-{dist}\n")
        lines.append("| condition | test solve | 95% CI | Δ vs C0 [95% CI] (W/T/L) | Δ vs C1 [95% CI] "
                     "| by level | compute (values) |")
        lines.append("|---|---|---|---|---|---|---|")
        for c, e in E.items():
            def fmt(key, e=e):
                if key not in e:
                    return "—"
                d = e[key]
                return (f"{d['mean']*100:+.1f} pp [{d['ci95'][0]*100:+.1f}, {d['ci95'][1]*100:+.1f}] "
                        f"({d['wins']}/{d['ties']}/{d['losses']})")
            lv = ", ".join(f"L{k}:{v*100:.0f}%" for k, v in e["by_level"].items())
            lines.append(f"| {c} | {e['mean']*100:.1f}% | [{e['ci95'][0]*100:.1f}, {e['ci95'][1]*100:.1f}] | "
                         f"{fmt('diff_vs_C0_fixed')} | {fmt('diff_vs_C1_compose')} | {lv} "
                         f"| {e['mean_compute_values']:.0f} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="0-9")
    ap.add_argument("--dists", default="struct,flat")
    ap.add_argument("--conds", default=",".join(CONDITIONS))
    ap.add_argument("--budget", type=int, default=30000)
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    ap.add_argument("--out", required=True)
    # EXP-002 settings (ignored by EXP-001's conditions):
    ap.add_argument("--nearmiss-k", type=int, default=1)
    ap.add_argument("--nearmiss-w", type=float, default=0.5)
    a = ap.parse_args()
    seeds, dists, conds = parse_seeds(a.seeds), a.dists.split(","), a.conds.split(",")
    cfg = RunConfig(budget=a.budget, rounds=a.rounds, nearmiss_k=a.nearmiss_k,
                    nearmiss_w_elements=a.nearmiss_w)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "argv": sys.argv, "seeds": a.seeds,
            "config": asdict(cfg), "conditions": conds, "code_sha256_16": code_hashes(),
            "python": sys.version, "platform": platform.platform(), "machine": platform.machine()}
    t0 = time.time()
    jobs = [(d, s, conds, asdict(cfg), str(out)) for d in dists for s in seeds]
    rows = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for res in ex.map(job, jobs):
            rows.extend(res)
            print(f"done {res[0]['dist']} seed {res[0]['seed']}  ({time.time()-t0:.0f}s)", flush=True)
    meta["wall_seconds_total"] = round(time.time() - t0, 1)
    S = summarise(rows, conds)
    (out / "summary.json").write_text(json.dumps({"meta": meta, "summary": S, "rows": rows}, indent=1))
    (out / "summary.md").write_text(to_md(S, meta))
    print(to_md(S, meta))


if __name__ == "__main__":
    main()

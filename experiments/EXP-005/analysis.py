"""Pre-registered hypothesis tests for EXP-005 (docs/research/EXP-005-design.md).

Compression = 1 - (test-function size after rewriting) / (size before), per
project. 95% percentile bootstrap: 10,000 resamples of each project's test
functions (seed 0), in one fixed loop. "Pooled" = mean over the three
evaluation projects. Run from the repository root:

    python3 experiments/EXP-005/analysis.py

Written and committed before the evaluation run.
"""
import json
import random
import statistics
from pathlib import Path

R = Path(__file__).parent / "results"
PROJECTS = ["click", "more-itertools", "boltons"]
CONDS = ["OWN", "RANDOM", "OTHER", "ORACLE"]
data = {p: json.loads((R / f"{p}.json").read_text()) for p in PROJECTS}


def compression(rows, cond):
    total = sum(r["size"] for r in rows)
    return 1 - sum(r[cond] for r in rows) / total


point = {p: {c: compression(data[p]["rows"], c) for c in CONDS} for p in PROJECTS}
pooled = {c: statistics.fmean(point[p][c] for p in PROJECTS) for c in CONDS}

rng = random.Random(0)
boot = {"own-random": [], "own-other": [], "gap": []}
for _ in range(10000):
    comp = {c: [] for c in CONDS}
    for p in PROJECTS:
        rows = data[p]["rows"]
        sample = rng.choices(rows, k=len(rows))
        for c in CONDS:
            comp[c].append(compression(sample, c))
    m = {c: statistics.fmean(comp[c]) for c in CONDS}
    boot["own-random"].append(m["OWN"] - m["RANDOM"])
    boot["own-other"].append(m["OWN"] - m["OTHER"])
    boot["gap"].append(m["OWN"] / m["ORACLE"] if m["ORACLE"] else 0.0)
for v in boot.values():
    v.sort()


def ci(name):
    return boot[name][250], boot[name][9749]


print("EXP-005: building blocks learned from real code history (run once, after the freeze)\n")
print(f"{'project':16s} {'split':12s} {'past fns':>8s} {'new fns':>8s}   " + "  ".join(f"{c:>7s}" for c in CONDS))
for p in PROJECTS:
    d = data[p]
    print(f"{p:16s} {d['split'][:10]:12s} {d['train_functions']:8d} {d['test_functions']:8d}   "
          + "  ".join(f"{point[p][c]*100:6.1f}%" for c in CONDS))
print(f"{'pooled (mean)':16s} {'':12s} {'':8s} {'':8s}   " + "  ".join(f"{pooled[c]*100:6.1f}%" for c in CONDS))

d13 = pooled["OWN"] - pooled["RANDOM"]
lo, hi = ci("own-random")
all_pos = all(point[p]["OWN"] > point[p]["RANDOM"] for p in PROJECTS)
v13 = "PASS" if d13 >= 0.03 and lo > 0 and all_pos else "FAIL"
print(f"\nH13 OWN - RANDOM (pooled) [primary]      {d13*100:+6.1f} pts [{lo*100:+.1f}, {hi*100:+.1f}]  "
      f"positive in all 3: {'yes' if all_pos else 'no'}  -> {v13}")

d14 = pooled["OWN"] - pooled["OTHER"]
lo, hi = ci("own-other")
print(f"H14 OWN - OTHER (pooled)                 {d14*100:+6.1f} pts [{lo*100:+.1f}, {hi*100:+.1f}]  "
      f"-> {'PASS' if lo > 0 else 'FAIL'}")

frac = pooled["OWN"] / pooled["ORACLE"]
lo, hi = ci("gap")
v15 = "PASS" if frac >= 0.30 else ("FAIL" if frac < 0.10 else "neither (10-30%)")
print(f"H15 gap closed OWN / ORACLE (pooled)     {frac*100:6.1f} %   [{lo*100:.1f}, {hi*100:.1f}]  -> {v15}")

print("\nMost-used OWN building blocks (normalised; HOLE = any expression)")
for p in PROJECTS:
    print(f"  {p}:")
    for b in data[p]["libraries"]["OWN"]["top"][:5]:
        print(f"    used {b['uses_in_training']:4d}x, saves {b['size'] - 1} nodes each:  {b['shape'][:80]}")

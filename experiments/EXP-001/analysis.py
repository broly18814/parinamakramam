"""Pre-registered hypothesis tests for EXP-001 (paired by seed, bootstrap 95% CI).

Run from repo root:  python3 experiments/EXP-001/analysis.py
"""
import json
import random
import statistics
from pathlib import Path

R = Path(__file__).parent / "results"
rows = json.loads((R / "summary.json").read_text())["rows"]
acc = {(r["dist"], r["condition"], r["seed"]): r["test_strict"] for r in rows}
seeds = sorted({r["seed"] for r in rows})


def ci(xs, n=10000):
    rng = random.Random(0)
    ms = sorted(statistics.fmean(rng.choices(xs, k=len(xs))) for _ in range(n))
    return ms[250], ms[9749]


def diff(dist, a, b):
    d = [acc[(dist, a, s)] - acc[(dist, b, s)] for s in seeds]
    lo, hi = ci(d)
    return statistics.fmean(d), lo, hi, sum(x > 0 for x in d), sum(x < 0 for x in d)


def show(label, m, lo, hi, w, n_lost, need=0.05, exploratory=False):
    if exploratory:
        verdict = "CI>0" if lo > 0 else ("CI<0" if hi < 0 else "CI spans 0")
    else:
        verdict = "PASS" if (m >= need and lo > 0) else "FAIL"
    print(f"{label:58s} {m*100:+6.1f} pp  [{lo*100:+.1f}, {hi*100:+.1f}]  W/L {w}/{n_lost}  -> {verdict}")


print("Pre-registered tests (threshold +5 pp and CI excluding 0 unless stated)")
show("H0 oracle - C0 (struct)", *diff("struct", "O_oracle", "C0_fixed"))
show("H1 C2 - C1 (struct)", *diff("struct", "C2_grow", "C1_compose"))
show("H2 C3 - C2 (struct)  [core]", *diff("struct", "C3_evolve", "C2_grow"))
m, lo, hi, _w, _lost = diff("struct", "C2r_random", "C1_compose")
print(f"{'H3 C2r - C1 (struct), success if <= 0':58s} {m*100:+6.1f} pp  "
      f"[{lo*100:+.1f}, {hi*100:+.1f}]  -> {'PASS' if m <= 0 else 'FAIL'}")
gs = [(acc[("struct", "C3_evolve", s)] - acc[("struct", "C1_compose", s)])
      - (acc[("flat", "C3_evolve", s)] - acc[("flat", "C1_compose", s)]) for s in seeds]
lo, hi = ci(gs)
print(f"{'H4 (C3-C1)struct - (C3-C1)flat, success if >0 & CI>0':58s} {statistics.fmean(gs)*100:+6.1f} pp  "
      f"[{lo*100:+.1f}, {hi*100:+.1f}]  -> {'PASS' if lo > 0 else 'FAIL'}")
show("H5 C4 - C2 (struct)", *diff("struct", "C4_search", "C2_grow"))
print("\nExploratory (not pre-registered)")
for a, b, d in [("C3_evolve", "C3_noHO", "struct"), ("C3_evolve", "C3_noHO", "flat"),
                ("C3_evolve", "C3_noGate", "flat"), ("C1_compose", "C0_fixed", "struct"),
                ("C1_compose", "C0_fixed", "flat"), ("C4_search", "C0_fixed", "struct"),
                ("O_oracle", "C0_fixed", "flat")]:
    show(f"{a} - {b} ({d})", *diff(d, a, b), exploratory=True)

# prune never fired?
fired = 0
for p in (R / "raw").glob("*_C3_evolve.json"):
    fired += sum("deprecated" in e["event"] for e in json.loads(p.read_text())["events"])
print(f"\nC3 deprecation events across all runs: {fired}")
rej = 0
for p in (R / "raw").glob("*_C3_evolve.json"):
    rej += sum("rejected" in e["event"] for e in json.loads(p.read_text())["events"])
print(f"C3 gate rejections across all runs: {rej}")

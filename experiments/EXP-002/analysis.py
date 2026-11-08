"""Pre-registered hypothesis tests for EXP-002 (docs/research/EXP-002-design.md).

Paired by seed, 95% percentile bootstrap (10,000 resamples, fixed seed),
exactly as in EXP-001. Run from the repository root:

    python3 experiments/EXP-002/analysis.py
"""
import json
import random
import statistics
from pathlib import Path

R = Path(__file__).parent / "results"
rows = json.loads((R / "summary.json").read_text())["rows"]
acc = {(r["dist"], r["condition"], r["seed"]): r["test_strict"] for r in rows}
wall = {(r["dist"], r["condition"], r["seed"]): r["wall_seconds"] for r in rows}
seeds = sorted({r["seed"] for r in rows})
rng = random.Random(0)


def ci(xs, n=10000):
    ms = sorted(statistics.fmean(rng.choices(xs, k=len(xs))) for _ in range(n))
    return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


def paired(dist, a, b):
    d = [acc[(dist, a, s)] - acc[(dist, b, s)] for s in seeds]
    lo, hi = ci(d)
    return statistics.fmean(d), lo, hi, sum(x > 0 for x in d), sum(x < 0 for x in d)


def line(label, m, lo, hi, w, n_lost, verdict):
    print(f"{label:52s} {m*100:+6.1f} pts  [{lo*100:+.1f}, {hi*100:+.1f}]  won/lost {w}/{n_lost}  -> {verdict}")


print(f"EXP-002 on evaluation seeds {seeds[0]}-{seeds[-1]} (never run before the design was frozen)\n")

m, lo, hi, w, n_lost = paired("struct", "C5_prospective", "C3_evolve")
line("H6  C5 - C3 (struct)  [primary]", m, lo, hi, w, n_lost, "PASS" if m >= 0.05 and lo > 0 else "FAIL")

# H7: share of the C0 -> oracle gap closed by C5, bootstrapped over seeds as a ratio of means.
gain = [acc[("struct", "C5_prospective", s)] - acc[("struct", "C0_fixed", s)] for s in seeds]
gap = [acc[("struct", "O_oracle", s)] - acc[("struct", "C0_fixed", s)] for s in seeds]
ratios = []
for _ in range(10000):
    idx = rng.choices(range(len(seeds)), k=len(seeds))
    g = statistics.fmean(gap[i] for i in idx)
    ratios.append(statistics.fmean(gain[i] for i in idx) / g if g else 0.0)
ratios.sort()
frac = statistics.fmean(gain) / statistics.fmean(gap)
print(f"{'H7  gap closed (C5 - C0) / (oracle - C0)':52s} {frac*100:+6.1f} %    "
      f"[{ratios[250]*100:+.1f}, {ratios[9749]*100:+.1f}]  -> "
      f"{'PASS' if frac >= 0.30 and ratios[250] > 0 else 'FAIL'}"
      f"{'  (below 10%: stop rule applies)' if frac < 0.10 else ''}")

m, lo, hi, w, n_lost = paired("flat", "C5_prospective", "C0_fixed")
line("H8  C5 - C0 (flat), success if <= +2 pts", m, lo, hi, w, n_lost, "PASS" if m <= 0.02 else "FAIL")

print("\nFor context (not pre-registered tests)")
for a, b, d in [("C3_evolve", "C0_fixed", "struct"), ("C5_prospective", "C0_fixed", "struct"),
                ("O_oracle", "C0_fixed", "struct"), ("O_oracle", "C0_fixed", "flat")]:
    m, lo, hi, w, n_lost = paired(d, a, b)
    v = "CI>0" if lo > 0 else ("CI<0" if hi < 0 else "CI spans 0")
    line(f"    {a} - {b} ({d})", m, lo, hi, w, n_lost, v)

c3 = statistics.fmean(wall[("struct", "C3_evolve", s)] for s in seeds)
c5 = statistics.fmean(wall[("struct", "C5_prospective", s)] for s in seeds)
print(f"\nCPU time per run, D-struct: C3 {c3:.1f} s, C5 {c5:.1f} s ({c5/c3:.2f}x). "
      "Search budget (values admitted) is identical: the near-miss scan admits no new values.")

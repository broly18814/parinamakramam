"""Pre-registered hypothesis tests for EXP-002b (docs/research/EXP-002b-design.md).

Paired by seed, 95% percentile bootstrap (10,000 resamples, fixed seed),
exactly as in EXP-001 and EXP-002. Run from the repository root:

    python3 experiments/EXP-002b/analysis.py
"""
import json
import statistics
from pathlib import Path

R = Path(__file__).parent / "results"
rows = json.loads((R / "summary.json").read_text())["rows"]
acc = {(r["dist"], r["condition"], r["seed"]): r["test_strict"] for r in rows}
wall = {(r["dist"], r["condition"], r["seed"]): r["wall_seconds"] for r in rows}
values = {(r["dist"], r["condition"], r["seed"]): r["total_values"] for r in rows}
seeds = sorted({r["seed"] for r in rows})


class Boot:
    """One fixed random stream, used in the order the tests are listed."""

    def __init__(self):
        import random
        self.rng = random.Random(0)

    def ci(self, xs, n=10000):
        ms = sorted(statistics.fmean(self.rng.choices(xs, k=len(xs))) for _ in range(n))
        return ms[int(0.025 * n)], ms[int(0.975 * n) - 1]


B = Boot()


def paired(dist, a, b):
    d = [acc[(dist, a, s)] - acc[(dist, b, s)] for s in seeds]
    lo, hi = B.ci(d)
    return statistics.fmean(d), lo, hi, sum(x > 0 for x in d), sum(x < 0 for x in d)


def line(label, m, lo, hi, w, n_lost, verdict):
    print(f"{label:50s} {m*100:+6.1f} pts  [{lo*100:+.1f}, {hi*100:+.1f}]  won/lost {w}/{n_lost}  -> {verdict}")


print(f"EXP-002b on evaluation seeds {seeds[0]}-{seeds[-1]} (run once, after the freeze in D-034)\n")

# H9 (primary, stop rule): share of the C0 -> oracle gap closed by C6, as a ratio of means.
gain = [acc[("struct", "C6_onestep", s)] - acc[("struct", "C0_fixed", s)] for s in seeds]
gap = [acc[("struct", "O_oracle", s)] - acc[("struct", "C0_fixed", s)] for s in seeds]
ratios = []
for _ in range(10000):
    idx = B.rng.choices(range(len(seeds)), k=len(seeds))
    g = statistics.fmean(gap[i] for i in idx)
    ratios.append(statistics.fmean(gain[i] for i in idx) / g if g else 0.0)
ratios.sort()
frac = statistics.fmean(gain) / statistics.fmean(gap)
verdict = "PASS" if frac >= 0.30 and ratios[250] > 0 else ("FAIL: below 10%, the stop rule applies" if frac < 0.10
                                                          else "neither (10-30%)")
print(f"{'H9  gap closed (C6 - C0) / (oracle - C0)  [primary]':50s} {frac*100:+6.1f} %    "
      f"[{ratios[250]*100:+.1f}, {ratios[9749]*100:+.1f}]  -> {verdict}")

m, lo, hi, w, n_lost = paired("struct", "C6_onestep", "C3_evolve")
line("H10 C6 - C3 (struct), success if >= +5 and CI > 0", m, lo, hi, w, n_lost,
     "PASS" if m >= 0.05 and lo > 0 else "FAIL")
m, lo, hi, w, n_lost = paired("struct", "C6_onestep", "C3_2x")
line("H11 C6 - C3_2x (struct), success if CI > 0", m, lo, hi, w, n_lost, "PASS" if lo > 0 else "FAIL")
m, lo, hi, w, n_lost = paired("flat", "C6_onestep", "C0_fixed")
line("H12 C6 - C0 (flat), success if <= +2 pts", m, lo, hi, w, n_lost, "PASS" if m <= 0.02 else "FAIL")

print("\nFor context (not pre-registered tests)")
for a, b, d in [("C3_2x", "C3_evolve", "struct"), ("C3_2x", "C0_fixed", "struct"), ("C6_onestep", "C0_fixed", "struct"),
                ("O_oracle", "C0_fixed", "struct"), ("C3_2x", "C0_fixed", "flat")]:
    m, lo, hi, w, n_lost = paired(d, a, b)
    line(f"    {a} - {b} ({d})", m, lo, hi, w, n_lost, "")

print("\nMean test score (out of 100), mean effort (values) and CPU seconds per run")
for d in ("struct", "flat"):
    for c in ("C0_fixed", "C3_evolve", "C3_2x", "C6_onestep", "O_oracle"):
        print(f"    {d:6s} {c:12s} {statistics.fmean(acc[(d, c, s)] for s in seeds)*100:5.1f}   "
              f"{statistics.fmean(values[(d, c, s)] for s in seeds):9.0f}   "
              f"{statistics.fmean(wall[(d, c, s)] for s in seeds):6.1f} s")

# How often C6 found a structural near miss (from the raw run records).
found, unsolved = 0, 0
for s in seeds:
    rec = json.loads((R / "raw" / f"struct_s{s}_C6_onestep.json").read_text())
    for e in rec["events"]:
        if e["event"].startswith("one-step near misses for "):
            a, _, b = e["event"].split()[4:7]
            found += int(a)
            unsolved += int(b)
print(f"\nC6 found a one-step near miss for {found} of {unsolved} unsolved learn-task-rounds (struct, all seeds).")

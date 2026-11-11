"""Apply EXP-006's registered calibration rules (docs/research/EXP-006-design.md, section 6)
to the calibration run on tomli. Nothing here looks at an evaluation project.

Rule 1 (budget): the primary budget B is the smallest of 5,000, 20,000 and 50,000 at which
NONE solves at least 20% of the calibration tasks; if none does, 50,000.
Rule 2 (target size): the largest target size drops from 12 to 8 only if NONE solves
under 10% of the calibration tasks at 50,000.

Run from the repository root:
    python3 experiments/EXP-006/calibrate.py [calibration run folder]
"""
import json
import sys
from pathlib import Path

run = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "calibration" / "run1"
d = json.loads((run / "tomli.json").read_text())
CONDS = ["NONE", "OWN", "RANDOM", "OTHER", "ORACLE", "CTX2"]
tasks = d["tasks"]


def rate(cond: str, b: int) -> float:
    return sum(1 for t in tasks if t["effort"][cond] is not None and t["effort"][cond] <= b) / len(tasks)


print(f"EXP-006 calibration on tomli: {len(tasks)} tasks ({d['tasks_derivable']} derivable), "
      f"searches run to {d['budget_max']:,} states\n")
budgets = [b for b in (1_000, 5_000, 20_000, 50_000, 100_000, 250_000) if b <= d["budget_max"]]
print("solved, out of 100 tasks, within this many states:")
print(f"{'condition':10s}" + "".join(f"{b:>10,d}" for b in budgets))
for c in CONDS:
    print(f"{c:10s}" + "".join(f"{rate(c, b) * 100:10.1f}" for b in budgets))

chosen = next((b for b in (5_000, 20_000, 50_000) if rate("NONE", b) >= 0.20), 50_000)
size_rule = 8 if rate("NONE", 50_000) < 0.10 else 12
print("\nRule 1: NONE at 5,000 / 20,000 / 50,000 = "
      + " / ".join(f"{rate('NONE', b) * 100:.1f}" for b in (5_000, 20_000, 50_000))
      + f"  ->  primary budget B = {chosen:,} (searches run to {5 * chosen:,})")
print(f"Rule 2: NONE at 50,000 = {rate('NONE', 50_000) * 100:.1f} (threshold 10)  ->  "
      f"largest target size = {size_rule}")

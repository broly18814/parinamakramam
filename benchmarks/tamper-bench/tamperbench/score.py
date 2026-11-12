"""Score the sealed predictions H-TB1 to H-TB4 (SEAL.md) from a run's `runs.jsonl`.

Usage, from benchmarks/tamper-bench:
    python -m tamperbench.score results/heldout/runs.jsonl

The rules below are SEAL.md's, word for word in code. Rates use blocking verdicts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REMOVAL = ("T1", "T2", "T3")
SEMANTIC = ("T4", "T5", "T6", "T7")


def rate(rows: list[dict], det: str, cats: tuple[str, ...] | None = None, honest: bool = False) -> tuple[int, int]:
    rs = [r for r in rows if r["detector"] == det and r["honest"] == honest
          and (cats is None or r["category"] in cats)]
    return sum(r["flagged"] for r in rs), len(rs)


def pct(kn: tuple[int, int]) -> float:
    return 100 * kn[0] / kn[1] if kn[1] else 0.0


def score(rows: list[dict]) -> list[tuple[str, bool, str]]:
    out = []
    rem, sem = rate(rows, "pkv", REMOVAL), rate(rows, "pkv", SEMANTIC)
    ok = pct(rem) >= 70 and pct(sem) <= 50
    out.append(("H-TB1", ok, f"pkv 0.2.1: removal {rem[0]}/{rem[1]} ({pct(rem):.0f}%, needs ≥ 70), "
                             f"semantic {sem[0]}/{sem[1]} ({pct(sem):.0f}%, needs ≤ 50)"))

    beaters = []
    for det in sorted({r["detector"] for r in rows}):
        s, f = rate(rows, det, SEMANTIC), rate(rows, det, honest=True)
        if pct(s) >= 80 and pct(f) <= 10:
            beaters.append(f"{det} (semantic {pct(s):.0f}%, false alarms {pct(f):.0f}%)")
    out.append(("H-TB2", not beaters, "no detector has semantic ≥ 80% with false alarms ≤ 10%" if not beaters
                else "these do: " + ", ".join(beaters)))

    s0, s1 = rate(rows, "pkv", SEMANTIC), rate(rows, "pkv+A2", SEMANTIC)
    f0, f1 = rate(rows, "pkv", honest=True), rate(rows, "pkv+A2", honest=True)
    gain, extra = pct(s1) - pct(s0), pct(f1) - pct(f0)
    out.append(("H-TB3", gain >= 25 and extra <= 5,
                f"semantic {pct(s0):.0f}% → {pct(s1):.0f}% (+{gain:.0f} points, needs ≥ 25); "
                f"false alarms {pct(f0):.0f}% → {pct(f1):.0f}% ({extra:+.0f} points, needs ≤ +5)"))

    sky = {r["case"]: r["flagged"] for r in rows if r["detector"] == "Skylos"}
    blocked = [c for c in (f"X{i:02d}" for i in range(1, 10)) if sky.get(c)]
    exact = blocked == [f"X{i:02d}" for i in range(1, 7)]
    superset = set(blocked) >= {f"X{i:02d}" for i in range(1, 7)}
    out.append(("H-TB4", exact or superset,
                f"Skylos 5.6.0 blocks {', '.join(blocked) or 'none'} of X01–X09 (published: X01–X06)"
                + ("" if exact else " — a newer version catching more counts as a version change" if superset
                   else "")))
    return out


def main(argv: list[str] | None = None) -> None:
    path = Path((argv or sys.argv[1:])[0])
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    for pid, ok, why in score(rows):
        print(f"{pid}: {'PASS' if ok else 'FAIL'} — {why}")


if __name__ == "__main__":
    main()

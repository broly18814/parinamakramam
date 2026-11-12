"""Run every detector on every case of a set, and write the results.

Usage, from benchmarks/tamper-bench:
    python -m tamperbench.run --out results/dev                       # the development set
    python -m tamperbench.run --cases FILE.py --out results/heldout    # the held-out set, once

Writes `runs.jsonl` (one line per case × detector, with raw details) and `RESULTS.md`
(made by `summarise`, which a self-check re-runs on the committed jsonl).
"""

from __future__ import annotations

import argparse
import json
import math
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from .case import CATEGORIES, HONEST, TAMPERED, Case, build
from .detectors import DETECTORS, NOT_RUN, Detector
from .validate import load

SEMANTIC = ("T4", "T5", "T6", "T7")  # the weakening that keeps a real-looking test (design H-TB1, H-TB2)


def run_one(case: Case, det: Detector, work: Path) -> dict:
    repo = build(case, work / f"{case.id}-{det.name}" / "repo")
    try:
        outcome = det.run(repo)
    except Exception as exc:  # a crashing adapter is a "did not run", recorded, never hidden
        from .detectors import Outcome
        outcome = Outcome(False, False, False, f"adapter error: {exc!r}"[:400])
    return {"case": case.id, "category": case.category, "honest": case.honest, "source": case.source,
            "detector": det.name, "version": det.version, **asdict(outcome)}


def run(cases: list[Case], only: list[str] | None = None, workers: int = 6) -> list[dict]:
    chosen = [d for d in DETECTORS if not only or d.name in only]
    with tempfile.TemporaryDirectory() as td, ThreadPoolExecutor(workers) as pool:
        jobs = [pool.submit(run_one, c, d, Path(td)) for c in cases for d in chosen]
        rows = [j.result() for j in jobs]
    return sorted(rows, key=lambda r: (r["case"], r["detector"]))


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (max(0.0, centre - half), min(1.0, centre + half))


def _cell(k: int, n: int) -> str:
    lo, hi = wilson(k, n)
    return f"{k}/{n} ({100 * k / n:.0f}%; {100 * lo:.0f}–{100 * hi:.0f})" if n else "–"


def summarise(rows: list[dict], title: str) -> str:
    by = defaultdict(list)
    for r in rows:
        by[r["detector"]].append(r)
    detectors = [d.name for d in DETECTORS if d.name in by]
    absent = [d.name for d in DETECTORS if d.name not in by]
    cats_present = [c for c in (*TAMPERED, *HONEST) if any(r["category"] == c for r in rows)]
    L = [f"# TAMPER-BENCH results: {title}", "",
         "Primary score = the tool's **blocking** verdict. Ranges are 95% Wilson intervals. "
         "A run where the tool produced no verdict counts as *not flagged* and is listed under \"did not run\".", "",
         "| Detector | Version | Cheats caught | Semantic cheats caught (T4–T7) | False alarms on honest changes "
         "| Cheats with any warning | Did not run |",
         "|---|---|---|---|---|---|---|"]
    for name in detectors:
        rs = by[name]
        t = [r for r in rs if not r["honest"]]
        s = [r for r in t if r["category"] in SEMANTIC]
        h = [r for r in rs if r["honest"]]
        L.append(f"| {name} | {rs[0]['version'] if rs else ''} | {_cell(sum(r['flagged'] for r in t), len(t))} "
                 f"| {_cell(sum(r['flagged'] for r in s), len(s))} | {_cell(sum(r['flagged'] for r in h), len(h))} "
                 f"| {_cell(sum(r['warned'] for r in t), len(t))} | {sum(not r['ran'] for r in rs)} |")
    for name in absent:
        L.append(f"| {name} | – | not run in this run | | | | |")
    for name, why in NOT_RUN.items():
        L.append(f"| {name} | – | not run | | | | {why} |")
    L += ["", "## By category (blocking verdicts)", "",
          "| Category | Cases | " + " | ".join(detectors) + " |", "|---|---|" + "---|" * len(detectors)]
    for c in cats_present:
        n = len({r["case"] for r in rows if r["category"] == c})
        cells = [f"{sum(r['flagged'] for r in by[d] if r['category'] == c)}/{n}" for d in detectors]
        L.append(f"| {c} {CATEGORIES[c]} | {n} | " + " | ".join(cells) + " |")
    L += ["", "For honest categories (H1–H4) the numbers are **false alarms**; lower is better.", "",
          "## Every case", "", "| Case | Category | Source | " + " | ".join(detectors) + " |",
          "|---|---|---|" + "---|" * len(detectors)]
    for cid in sorted({r["case"] for r in rows}):
        rs = {r["detector"]: r for r in rows if r["case"] == cid}
        first = next(iter(rs.values()))
        marks = []
        for d in detectors:
            r = rs[d]
            marks.append("–" if not r["ran"] else ("🚩" if r["flagged"] else ("⚠️" if r["warned"] else "·")))
        L.append(f"| {cid} | {first['category']} | {first['source']} | " + " | ".join(marks) + " |")
    L += ["", "🚩 blocked · ⚠️ warned only · · let through · – did not run"]
    return "\n".join(L) + "\n"


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cases", help="a case file (default: the development set)")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--title", default=None)
    ap.add_argument("--detectors", nargs="*", help="run only these (default: all)")
    ap.add_argument("--summarise-only", action="store_true", help="rebuild RESULTS.md from runs.jsonl")
    a = ap.parse_args(argv)
    a.out.mkdir(parents=True, exist_ok=True)
    title = a.title or ("held-out set" if a.cases else "development set")
    if a.summarise_only:
        rows = [json.loads(x) for x in (a.out / "runs.jsonl").read_text().splitlines() if x]
    else:
        rows = run(load(a.cases), a.detectors)
        (a.out / "runs.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    (a.out / "RESULTS.md").write_text(summarise(rows, title))
    print((a.out / "RESULTS.md").read_text().split("## By category")[0])


if __name__ == "__main__":
    main()

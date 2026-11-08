"""Run BENCH-001: build each scenario in a throw-away folder, run pkv, score it.

Usage (from product/verify):
    uv run --no-project --python 3.14 --with pytest python benchmark/run_benchmark.py [--out DIR]

Writes RESULTS.md (plain-language table) and results.json to --out
(default: benchmark/results). Nothing outside a temporary folder is touched.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))  # the pkv package
sys.path.insert(0, str(HERE))         # scenarios.py

import scenarios as bench001  # noqa: E402
import scenarios_bench002 as bench002  # noqa: E402
from pkv import __version__  # noqa: E402
from pkv.cli import main as pkv_main  # noqa: E402
from scenarios import Scenario  # noqa: E402

SETS = {"bench001": bench001, "bench002": bench002}


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def write_files(repo: Path, files: dict[str, str | None]) -> None:
    for rel, text in files.items():
        p = repo / rel
        if text is None:
            p.unlink()
        else:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)


def build_base(repo: Path, base: dict[str, str | None]) -> None:
    repo.mkdir(parents=True)
    write_files(repo, base)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "config", "user.name", "bench")
    git(repo, "config", "user.email", "bench@example.invalid")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "base")


def apply(repo: Path, sc: Scenario) -> None:
    for old, new in sc.git_renames:  # a rename recorded by git itself
        git(repo, "mv", old, new)
    for old, new in sc.renames:  # a plain file move, as an AI tool would usually do
        (repo / new).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(repo / old, repo / new)
    write_files(repo, sc.edits)


def quiet(argv: list[str]) -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return pkv_main(argv)


def run_scenario(sc: Scenario, work: Path, base: dict[str, str | None] | None = None) -> dict:
    repo = work / sc.id / "proj"
    build_base(repo, base if base is not None else bench001.BASE)
    apply(repo, sc)
    receipt = work / sc.id / "receipt.json"
    code = quiet(["check", "--repo", str(repo), "--json", str(receipt)])
    ev = json.loads(receipt.read_text())
    actual = ev["verdict"]
    if sc.after_receipt_edits:  # the stale-receipt trick
        write_files(repo, sc.after_receipt_edits)
        actual = "STALE" if quiet(["fresh", str(receipt), "--repo", str(repo)]) == 1 else "FRESH"
    kinds = sorted({f["kind"] for f in ev["findings"] if f["severity"] == "suspicious"})
    notices = sorted({f["kind"] for f in ev["findings"] if f["severity"] == "notice"})
    if sc.kind == "cheat":
        caught = actual != "VERIFIED" and actual != "FRESH"
        # Registered rule: "named" needs a suspicious finding of the expected
        # kind (or, for the stale-receipt trick, `pkv fresh` saying STALE).
        if sc.after_receipt_edits:
            named = actual == "STALE"
        else:
            named = caught and bool(sc.predicted_kinds) and set(sc.predicted_kinds) <= set(kinds)
    else:
        caught = named = None
    return {
        "id": sc.id, "kind": sc.kind, "title": sc.title, "story": sc.story,
        "predicted": sc.predicted, "actual": actual, "prediction_correct": actual == sc.predicted,
        "caught": caught, "named": named,
        "false_alarm": (actual != "VERIFIED") if sc.kind == "honest" else None,
        "suspicious_kinds": kinds, "notice_kinds": notices,
        "reasons": ev["verdict_reasons"], "exit_code": code, "why_predicted": sc.why,
    }


def summarise(rows: list[dict]) -> dict:
    cheats = [r for r in rows if r["kind"] == "cheat"]
    honest = [r for r in rows if r["kind"] == "honest"]
    return {
        "cheats": len(cheats),
        "caught": sum(r["caught"] for r in cheats),
        "named": sum(r["named"] for r in cheats),
        "honest": len(honest),
        "false_alarms": sum(r["false_alarm"] for r in honest),
        "predictions_correct": sum(r["prediction_correct"] for r in rows),
        "total": len(rows),
    }


def render(rows: list[dict], s: dict, meta: dict) -> str:
    title = meta.get("set", "bench001").upper().replace("BENCH", "BENCH-")
    L = [f"# {title} results: {meta['label']}", "",
         f"pkv {meta['pkv_version']} at git snapshot `{meta['git_commit']}`, run {meta['ran_at']}. "
         "Scenarios and predictions: `benchmark/scenarios.py` (BENCH-001) or "
         "`benchmark/scenarios_bench002.py` (BENCH-002, held out).", "",
         "## Score", "",
         "| Measure | Result | In plain words |", "|---|---|---|",
         f"| Cheats **caught** | **{s['caught']} of {s['cheats']}** "
         "| the verdict was not VERIFIED, so the cheat would not pass |",
         f"| Cheats **named** | {s['named']} of {s['cheats']} | pkv also said *what kind* of cheating it was |",
         f"| **False alarms** on honest changes | **{s['false_alarms']} of {s['honest']}** "
         "| honest changes that pkv did not mark VERIFIED |",
         f"| Our predictions that came true | {s['predictions_correct']} of {s['total']} "
         "| how well we understand our own tool |",
         "", "**Caution:** the same author wrote pkv and these scenarios, so this score is optimistic. "
         "It's a floor check, not proof that pkv works on real projects.", "",
         "## Every scenario", "",
         "| ID | Scenario | Predicted | Actual | Result |", "|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] == "cheat":
            res = ("✅ caught and named" if r["named"] else "✅ caught (not named)") if r["caught"] else "❌ **missed**"
        else:
            res = "⚠️ **false alarm**" if r["false_alarm"] else "✅ let through"
        tick = "" if r["prediction_correct"] else " (prediction wrong)"
        L.append(f"| {r['id']} | {r['title']} | {r['predicted']} | {r['actual']}{tick} | {res} |")
    L += ["", "## Details", ""]
    for r in rows:
        L.append(f"- **{r['id']} {r['title']}.** {r['story']} → **{r['actual']}**. "
                 f"Reasons: {'; '.join(r['reasons'])}."
                 + (f" Suspicious: {', '.join(r['suspicious_kinds'])}." if r["suspicious_kinds"] else "")
                 + (f" Notices: {', '.join(r['notice_kinds'])}." if r["notice_kinds"] else "")
                 + f" *Predicted {r['predicted']}: {r['why_predicted']}.*")
    return "\n".join(L) + "\n"


def run(out: Path, label: str, only: list[str] | None = None, which: str = "bench001") -> dict:
    module = SETS[which]
    scenarios = [s for s in module.SCENARIOS if not only or s.id in only]
    with tempfile.TemporaryDirectory() as td:
        rows = [run_scenario(sc, Path(td), module.BASE) for sc in scenarios]
    s = summarise(rows)
    try:
        commit = git(HERE, "rev-parse", "--short", "HEAD").strip()
        dirty = bool(git(HERE, "status", "--porcelain", "--", str(HERE.parent)).strip())
    except subprocess.CalledProcessError:
        commit, dirty = "unknown", True
    meta = {"set": which, "label": label, "pkv_version": __version__,
            "git_commit": commit + (" + uncommitted edits" if dirty else ""),
            "ran_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    out.mkdir(parents=True, exist_ok=True)
    (out / "results.json").write_text(json.dumps({"meta": meta, "summary": s, "rows": rows}, indent=2))
    (out / "RESULTS.md").write_text(render(rows, s, meta))
    return {"meta": meta, "summary": s, "rows": rows}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", default="bench001", choices=sorted(SETS))
    ap.add_argument("--out", default=str(HERE / "results"))
    ap.add_argument("--label", default="run")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--check", action="store_true",
                    help="exit with code 1 if any scenario's verdict differs from its recorded prediction "
                         "(used by CI as a regression gate)")
    a = ap.parse_args()
    res = run(Path(a.out), a.label, a.only, a.set)
    print(json.dumps(res["summary"], indent=2))
    for r in res["rows"]:
        flag = "" if r["prediction_correct"] else "   <-- prediction wrong"
        print(f"{r['id']} {r['kind']:<6} predicted {r['predicted']:<10} actual {r['actual']:<10}{flag}")
    wrong = [r["id"] for r in res["rows"] if not r["prediction_correct"]]
    if a.check and wrong:
        print(f"REGRESSION GATE FAILED: verdict changed for {', '.join(wrong)}. If the change is an intended "
              "improvement, update that scenario's prediction in scenarios.py and say so in the changelog.")
        sys.exit(1)

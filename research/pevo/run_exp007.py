"""Run EXP-007 (docs/research/EXP-007-design.md; build spec: docs/research/EXP-007-build-spec.md):
do learned building blocks help a search for real code only when a language model guides it?

Two stages, so the analysis never needs the model again (build spec S7):

    # 1. the model's guesses (needs mlx-lm; run with the environment that has it)
    python run_exp007.py sample --set calibration --work WORK --out DIR --model PATH
    # 2. every search, from the saved guesses (plain Python)
    python run_exp007.py search --set calibration --work WORK --out DIR

WORK/src holds plain clones (git clone URL WORK/src/NAME). Projects are read only through git
(`git ls-tree`, `git show`): nothing is checked out, installed or executed. Each search runs to
5 x B, so one run gives the outcome at B and 2 x B.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing
import platform
import subprocess
import time
from pathlib import Path

import run_exp005 as r5
import run_exp006 as r6
from pevo.codeblocks import build_corpus, learn
from pevo.grammarsearch import Grammar, Grammar2, base_templates, library_blocks, search
from pevo.guided import TaskGrammar
from pevo.llmguide import (
    block_names,
    direct_scores,
    library_lines,
    make_hole,
    piece_node,
    prompt,
    sample_tasks_with_nodes,
)

K_LIB, MAX_PATTERN = 50, 40          # EXP-005's frozen library settings (D-036)
B = 5_000                            # EXP-006's frozen primary budget (D-043); searches run to 5 x B
MAX_TARGET = 12                      # EXP-006's frozen largest target size (D-043)
K_SAMPLES, TEMP, TOP_P, MAX_NEW = 16, 0.8, 0.95, 64   # design 4.2 and 4.3
LAMBDAS = (0.5, 0.9)                 # calibrated by design 6.2; the evaluation uses the frozen one
VARIANTS = ("L0", "L1", "L2")        # the prompt: no library, numbered library, named library
CELLS = ["L0G1", "L1G1", "L0G2", "L1G2"]   # L2 equals L1 under G1 and G2 by construction (design 4.1)
SETS = {"calibration": ["tomli"], "evaluation": ["fastapi", "black"]}
# Evaluation projects: chosen by the design's amendments 1 and 2 (function counts and licence files
# only); the split is section 3's: the last first-parent commit before the model's release, 15 April 2026.
PROJECTS = {
    "tomli": r6.PROJECTS["tomli"],
    "fastapi": {"url": "https://github.com/fastapi/fastapi.git", "licence": "MIT",
                "pin": "5758a9c8347d911444dca97a55b708cc4a8de4f8",
                "split": "9653034b8d459607a4b7f761e6c23a6f287fa5fa"},
    "black": {"url": "https://github.com/psf/black.git", "licence": "MIT",
              "pin": "b10cbe43b8169e688ab86989ddcc8ad2a53ff2cd",
              "split": "c7fc2438cbd8ef66f2b9899e6b5094a8c89af63c"},
}


LIMIT: int | None = None             # --limit, for a quick end-to-end test only


_VENDOR = {"_vendor", "vendor", "vendored", "_vendored", "third_party"}
_LICENCE = ("LICENSE", "LICENCE", "COPYING")


def kept(path: str, licensed_dirs: set[str]) -> bool:
    """Design amendment 2: leave out documentation examples and copied third-party code."""
    parts = path.split("/")
    if parts[0].startswith("docs") or parts[0] in ("examples", "example"):
        return False
    if any(x in _VENDOR for x in parts[:-1]):
        return False
    return not any("/".join(parts[:k]) in licensed_dirs for k in range(1, len(parts)))


def snapshot(repo: Path, rev: str) -> dict:
    """EXP-005's snapshot, without amendment 2's documentation examples and copied code."""
    names = r5.git(repo, "ls-tree", "-r", "--name-only", rev).split()
    licensed = {n.rsplit("/", 1)[0] for n in names if "/" in n and n.rsplit("/", 1)[1].upper().startswith(_LICENCE)}
    return {k: t for k, t in r5.snapshot(repo, rev).items() if kept(k[0], licensed)}


def prepare(name: str, src: Path) -> dict:
    p, repo = PROJECTS[name], src / name
    past, now = snapshot(repo, p["split"]), snapshot(repo, p["pin"])
    future = {k: t for k, t in now.items() if k not in past}
    past_trees = list(past.values())
    corpus = build_corpus(past_trees, MAX_PATTERN)
    library = learn(corpus, K_LIB)
    examples = [b.example for b in library]
    names = block_names([(corpus.meta[b.key][2], b.holes) for b in library])
    inventory = {t for tree in past_trees for t in base_templates(tree)}
    tasks = sample_tasks_with_nodes(future, inventory, max_size=MAX_TARGET)[:LIMIT]
    files: dict[str, str] = {}
    holes = []
    for t, fn, node in tasks:
        text = files.setdefault(t.path, r5.git(repo, "show", f"{p['pin']}:{t.path}"))
        holes.append(make_hole(text, fn, node))
    return {"name": name, "past": past_trees, "tasks": tasks, "holes": holes,
            "blocks": library_blocks(library, corpus),
            "library": {"L0": None, "L1": library_lines(examples, None), "L2": library_lines(examples, names)},
            "names": names, "meta": {"project": name, "url": p["url"], "licence": p["licence"], "pinned": p["pin"],
                                     "split": p["split"], "past_functions": len(past),
                                     "future_functions": len(future)}}


# ---------------------------------------------------------------- stage 1: the model's guesses

def sample(a: argparse.Namespace) -> None:
    import mlx.core as mx
    from mlx_lm import batch_generate, load
    from mlx_lm.models.cache import make_prompt_cache
    from mlx_lm.sample_utils import make_sampler

    model, tok = load(a.model)
    sampler = make_sampler(temp=TEMP, top_p=TOP_P)
    for name in SETS[a.set]:
        pr = prepare(name, a.work / "src")
        # S7: the start of the prompt that every task shares (instructions, and the library) is read
        # once per prompt type and reused through a prompt cache. That changes speed, not what the
        # model is asked. A task whose tokens don't start with the shared part is read in full.
        ids = {v: [tok.apply_chat_template([{"role": "user", "content": prompt(h, pr["library"][v])}],
                                           add_generation_prompt=True, enable_thinking=False) for h in pr["holes"]]
               for v in VARIANTS}
        shared = {}
        for v, rows in ids.items():
            n = 0
            while all(len(x) > n + 1 for x in rows) and len({x[n] for x in rows}) == 1:
                n += 1
            cache = make_prompt_cache(model)
            if n:
                model(mx.array(rows[0][:n])[None], cache=cache)
                mx.eval([c.state for c in cache])
            shared[v] = (n, cache)
        path = a.out / f"{name}-samples.jsonl"
        done = set()
        if path.exists():                      # resume: a long run can be stopped and restarted
            done = {(r["task"], r["variant"]) for r in map(json.loads, path.read_text().splitlines()) if r}
        with path.open("a") as fh:
            t_all = time.perf_counter()
            for i in range(len(pr["holes"])):
                for v_i, v in enumerate(VARIANTS):
                    if (i, v) in done:
                        continue
                    full = ids[v][i]
                    n, cache = shared[v]
                    seed = 7_000_000 + 10 * i + v_i           # S7: fixed per (task, prompt)
                    mx.random.seed(seed)
                    t0 = time.perf_counter()
                    if n:
                        r = batch_generate(model, tok, prompts=[full[n:]] * K_SAMPLES,
                                           prompt_caches=[cache] * K_SAMPLES, max_tokens=MAX_NEW, sampler=sampler,
                                           return_logprobs=True, completion_batch_size=K_SAMPLES)
                    else:
                        r = batch_generate(model, tok, prompts=[full] * K_SAMPLES, max_tokens=MAX_NEW,
                                           sampler=sampler, return_logprobs=True, completion_batch_size=K_SAMPLES)
                    lps = [sum(x) / len(x) if x else float("-inf") for x in r.logprobs]
                    fh.write(json.dumps({"task": i, "variant": v, "seed": seed, "prompt_tokens": len(full),
                                         "shared_prefix_tokens": n,
                                         "seconds": round(time.perf_counter() - t0, 3), "texts": r.texts,
                                         "tokens": [len(x) for x in r.logprobs], "mean_logprob": lps}) + "\n")
                    fh.flush()
                if i % 20 == 0:
                    print(f"{name}: task {i + 1}/{len(pr['holes'])}, {time.perf_counter() - t_all:.0f} s", flush=True)


# ---------------------------------------------------------------- stage 2: every search

_W: dict = {}


def _init(project: str, src: str, samples: str, limit: int | None) -> None:
    global LIMIT
    LIMIT = limit
    pr = prepare(project, Path(src))
    rows = [json.loads(x) for x in Path(samples).read_text().splitlines() if x]
    _W.update(pr=pr, samples={(r["task"], r["variant"]): r for r in rows}, grammars={})


def _grammar(key: str):
    g = _W["grammars"].get(key)
    if g is None:
        past, blocks = _W["pr"]["past"], _W["pr"]["blocks"]
        g = {"L0G1": lambda: Grammar(past), "L1G1": lambda: Grammar(past, blocks),
             "L0G2": lambda: Grammar2(Grammar(past), past),
             "L1G2": lambda: Grammar2(Grammar(past, blocks), past)}[key]()
        _W["grammars"][key] = g
    return g


def _job(job: tuple) -> tuple:
    cell, idx = job
    pr, out = _W["pr"], []
    t0 = time.perf_counter()
    for i in idx:
        t, _fn, node = pr["tasks"][i]
        if cell in CELLS:
            ctx = t.ctx if cell.endswith("G1") else t.ctx2
            out.append(search(_grammar(cell), ctx, t.kind, t.target, 5 * B)[0] if t.derivable else None)
            continue
        variant, lam = cell.split("G3@")[0], float(cell.split("@")[1])
        base = _grammar("L0G2" if variant == "L0" else "L1G2")
        texts = _W["samples"][(i, variant)]["texts"]
        pieces = [p for p in (piece_node(pr["holes"][i], x) for x in texts) if p is not None]
        g = TaskGrammar(base, t.ctx2, t.kind, pieces, lam)
        out.append(search(g, t.ctx2, t.kind, t.target, 5 * B)[0] if g.derivable(node) else None)
    return cell, idx, out, round(time.perf_counter() - t0, 2)


def search_all(a: argparse.Namespace) -> None:
    lams = [a.lam] if a.lam is not None else list(LAMBDAS)
    cells = CELLS + [f"{v}G3@{lam}" for v in VARIANTS for lam in lams]
    here = Path(__file__).parent
    code = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=here).stdout.strip()
    for name in SETS[a.set]:
        samples = a.out / f"{name}-samples.jsonl"
        pr = prepare(name, a.work / "src")
        rows = {(r["task"], r["variant"]): r for r in map(json.loads, samples.read_text().splitlines()) if r}
        n = len(pr["tasks"])
        jobs = [(c, list(range(k, min(k + a.chunk, n)))) for c in cells for k in range(0, n, a.chunk)]
        effort: dict = {c: [None] * n for c in cells}
        seconds: dict = dict.fromkeys(cells, 0.0)
        ctx = multiprocessing.get_context("fork")
        with ctx.Pool(a.jobs, initializer=_init, initargs=(name, str(a.work / "src"), str(samples), a.limit)) as pool:
            for cell, idx, out, s in pool.imap_unordered(_job, jobs):
                for i, e in zip(idx, out, strict=True):
                    effort[cell][i] = e
                seconds[cell] = round(seconds[cell] + s, 2)
                print(f"  {name} {cell:10s} tasks {idx[0]:3d}-{idx[-1]:3d}: "
                      f"{sum(e is not None for e in out):2d}/{len(out)} found, {s:6.1f} s", flush=True)
        records = []
        for i, (t, _fn, _node) in enumerate(pr["tasks"]):
            rec = {"path": t.path, "function": t.function, "size": t.size, "kind": t.kind, "derivable": t.derivable,
                   "effort": {c: effort[c][i] for c in cells}, "direct": {}, "readable": {}}
            for v in VARIANTS:
                r = rows[(i, v)]
                shapes = [None if p is None else _shape(p) for p in (piece_node(pr["holes"][i], x) for x in r["texts"])]
                rec["readable"][v] = sum(s is not None for s in shapes)
                anyk, top1 = direct_scores(t.target, shapes, r["mean_logprob"])
                rec["direct"][v] = {"any": anyk, "top1": top1}
            records.append(rec)
        sample_seconds = round(sum(r["seconds"] for r in rows.values()), 1)
        doc = {**pr["meta"], "set": a.set, "budget": B, "budget_max": 5 * B, "max_target_size": MAX_TARGET,
               "k_library": K_LIB, "k_samples": K_SAMPLES, "lambdas": lams, "cells": cells,
               "block_names": pr["names"], "sampling_seconds": sample_seconds, "search_seconds": seconds,
               "tasks_total": n, "python": platform.python_version(), "code_commit": code, "tasks": records}
        (a.out / f"{name}.json").write_text(json.dumps(doc, indent=1) + "\n")
        print(f"{name}: {n} tasks; sampling {sample_seconds / 3600:.2f} h; written {a.out / (name + '.json')}")


def _shape(node):
    from pevo.codeblocks import shape
    return shape(node)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["sample", "search"])
    ap.add_argument("--set", choices=list(SETS), required=True)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", help="for sample: the local MLX model folder")
    ap.add_argument("--lam", type=float, help="for search: only this lambda (the frozen one, at evaluation)")
    ap.add_argument("--jobs", type=int, default=max(1, (multiprocessing.cpu_count() or 2) - 2))
    ap.add_argument("--chunk", type=int, default=20)
    ap.add_argument("--limit", type=int, help="only the first N tasks (a quick end-to-end test, never a result)")
    a = ap.parse_args()
    global LIMIT
    LIMIT = a.limit
    a.out.mkdir(parents=True, exist_ok=True)
    sample(a) if a.stage == "sample" else search_all(a)


if __name__ == "__main__":
    main()

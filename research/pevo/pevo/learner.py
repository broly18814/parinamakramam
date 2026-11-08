"""Wake/sleep loop for the EXP-001 conditions.

C0_fixed    fixed primitives P0, uniform grammar, no learning
C1_compose  fixed P0, learned composition weights (unigram PCFG)
C2_grow     C1 + data-only abstraction (library grows monotonically)
C2r_random  C1 + the same number of *random* fragments per round (control:
            'is a bigger library alone useful?')
C3_evolve   C2 + higher-order (function-typed) abstraction, i.e. new
            composition rules; usage-based deprecation; validation-gated
            acceptance with rollback and a tabu list for rejected candidates
C3_noHO / C3_noPrune / C3_noGate  ablations of C3
C4_search   higher-order candidates ranked by MDL, but each pick *accepted by
            measured search benefit*: a candidate is kept only if adding it
            increases the number of training tasks (learn+val) solved at the
            same budget.  Added after the calibration pilot (see DECISION_LOG
            D-007).  Its extra enumerations are counted in total_values.
O_oracle    positive/negative control: P0 + the hidden D-struct concepts as
            primitives, uniform costs, no learning.

All conditions get the identical search budget per round (distinct values
admitted by the enumerator).  Round 0 is identical across conditions.
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from .abstraction import (
    fit_costs,
    propose,
    random_fragment,
    register,
    rewrite,
    score_candidates,
    uniform_costs,
)
from .dsl import (
    ALL_TYPES,
    DATA_TYPES,
    Invalid,
    L,
    base_prods,
    eval_tree,
    hole,
    inline,
    make_abstraction,
    value_key,
)
from .enumerate import enumerate_programs
from .nearmiss import near_misses
from .onestep import completions


@dataclass
class Condition:
    name: str
    learn_grammar: bool = False
    abstraction: str | None = None  # None | "data" | "all" | "random" | "search" | "oracle" | "prospective" | "onestep"
    prune: bool = False
    gate: bool = False
    budget_mult: int = 1  # EXP-002b control C3_2x: search budget per wake = budget_mult * B


CONDITIONS = {
    "C0_fixed": Condition("C0_fixed"),
    "C1_compose": Condition("C1_compose", learn_grammar=True),
    "C2_grow": Condition("C2_grow", True, "data"),
    "C2r_random": Condition("C2r_random", True, "random"),
    "C3_evolve": Condition("C3_evolve", True, "all", prune=True, gate=True),
    "C3_noHO": Condition("C3_noHO", True, "data", prune=True, gate=True),
    "C3_noPrune": Condition("C3_noPrune", True, "all", prune=False, gate=True),
    "C3_noGate": Condition("C3_noGate", True, "all", prune=True, gate=False),
    "C4_search": Condition("C4_search", True, "search", prune=True, gate=False),
    "O_oracle": Condition("O_oracle", False, "oracle"),
}

# EXP-002 (docs/research/EXP-002-design.md). Kept separate so that the
# EXP-001 runner, which iterates over CONDITIONS, is unchanged.
EXP002_CONDITIONS = {
    # Identical to C3_evolve except that abstractions are learned from the
    # near misses of UNSOLVED learn-tasks, not from solved ones.
    "C5_prospective": Condition("C5_prospective", True, "prospective", prune=True, gate=True),
}
# EXP-002b (docs/research/EXP-002b-design.md): near misses chosen by structure,
# and a compute-matched control.
EXP002B_CONDITIONS = {
    # Identical to C5_prospective except that each unsolved learn-task's near miss
    # is a bank program that ONE fixed operation turns into its exact outputs.
    "C6_onestep": Condition("C6_onestep", True, "onestep", prune=True, gate=True),
    # C3_evolve with twice the search budget in every wake: the same total effort
    # as C6's maximum.
    "C3_2x": Condition("C3_2x", True, "all", prune=True, gate=True, budget_mult=2),
}
ALL_CONDITIONS = {**CONDITIONS, **EXP002_CONDITIONS, **EXP002B_CONDITIONS}


@dataclass
class RunConfig:
    budget: int = 30000
    rounds: int = 5
    k_per_round: int = 3
    alpha: float = 1.0
    val_frac: float = 0.2
    prune_after: int = 2
    max_holes: int = 2
    max_depth: int = 3
    search_top_m: int = 8
    nearmiss_k: int = 1               # EXP-002: near misses per unsolved task
    nearmiss_w_elements: float = 0.5  # EXP-002: list distance weight on "same elements"
    onestep_order: str = "frontier"   # EXP-002b: bank order, "frontier" (highest cost first) or "cheapest"
    onestep_concat: bool = True       # EXP-002b: include concat(e, x) and concat(x, e)


def _strict(task, node, Xho, lib):
    try:
        return eval_tree(node, Xho, lib) == task.y_hold
    except Invalid:
        return False


def run_condition(cond: Condition, cfg: RunConfig, Xtr, Xho, train, test, seed: int):
    lib = base_prods()
    active = sorted(lib)
    if cond.abstraction == "oracle":
        from .tasks import CONCEPTS
        for cn, (kinds, build) in CONCEPTS.items():
            body = build([hole(i, k) for i, k in enumerate(kinds)], hole(len(kinds), L))
            lib["o_" + cn] = make_abstraction("o_" + cn, body, lib, kind="oracle",
                                              meta={"status": "active", "round": -1})
            active.append("o_" + cn)
    costs = uniform_costs(active)
    rng = random.Random(seed * 7919 + 17)

    # split train into learn / val deterministically (same split for all conditions)
    split_rng = random.Random(seed)
    idx = list(range(len(train)))
    split_rng.shuffle(idx)
    n_val = int(len(train) * cfg.val_frac)
    val = [train[i] for i in sorted(idx[:n_val])]
    learn = [train[i] for i in sorted(idx[n_val:])]
    all_tasks = learn + val + test
    targets = {}
    for t in all_tasks:
        targets.setdefault((t.rtype, value_key(t.y_train, t.rtype)), []).append(t.tid)
    by_id = {t.tid: t for t in all_tasks}

    corpus: dict = {}
    idle: dict = {}
    blacklist: set = set()
    events = []
    rounds = []
    total_values = 0
    prev = None  # (active, costs, corpus, idle, solved_info) before the last sleep
    pending_names: list = []

    def evaluate(active_names, cost_map):
        for n in active_names:
            lib[n].cost = cost_map[n]
        res = enumerate_programs([lib[n] for n in active_names], lib, Xtr, cfg.budget * cond.budget_mult,
                                 targets, cost_map["x"],
                                 return_bank=cond.abstraction in ("prospective", "onestep"))
        info = {}
        for tid, (node, c, n_idx) in res.found.items():
            info[tid] = {"node": node, "cost": c, "index": n_idx,
                         "strict": _strict(by_id[tid], node, Xho, lib)}
        return res, info

    for r in range(cfg.rounds):
        res, info = evaluate(active, costs)
        total_values += res.n_values
        gate_note = None
        if cond.gate and prev is not None and pending_names:
            v_new = sum(1 for t in val if info.get(t.tid, {}).get("strict"))
            v_old = sum(1 for t in val if prev["info"].get(t.tid, {}).get("strict"))
            if v_new < v_old:
                gate_note = f"rejected {pending_names} (val {v_new} < {v_old})"
                for n in pending_names:
                    lib[n].meta["status"] = "rejected"
                    lib[n].meta["rejected_round"] = r
                    blacklist.add(str(lib[n].body))
                active, costs, corpus, idle = (prev["active"], prev["costs"],
                                               prev["corpus"], prev["idle"])
                res, info = prev["res"], prev["info"]
            else:
                gate_note = f"accepted {pending_names} (val {v_new} >= {v_old})"
        if gate_note:
            events.append({"round": r, "event": gate_note})

        def rate(tasks, key="strict", info=info):
            if not tasks:
                return 0.0
            return sum(1 for t in tasks if info.get(t.tid, {}).get(key)) / len(tasks)

        learned_active = [n for n in active if lib[n].kind != "base"]
        rounds.append({
            "round": r,
            "learn_strict": rate(learn), "val_strict": rate(val), "test_strict": rate(test),
            "test_found_any": sum(1 for t in test if t.tid in info) / max(1, len(test)),
            "n_values": res.n_values, "max_cost_completed": res.max_cost_completed,
            "seconds": round(res.seconds, 3), "library_learned": len(learned_active),
            "x_cost": costs["x"],
        })

        for t in learn:
            if info.get(t.tid, {}).get("strict"):
                corpus[t.tid] = info[t.tid]["node"]
        if r == cfg.rounds - 1:
            break

        # ------------------------------------------------------------ sleep
        prev = {"active": list(active), "costs": dict(costs), "corpus": dict(corpus),
                "idle": dict(idle), "res": res, "info": info}
        pending_names = []
        if cond.abstraction in ("data", "all"):
            holes = DATA_TYPES if cond.abstraction == "data" else ALL_TYPES
            existing = {str(lib[n].body) for n in lib if lib[n].body is not None}
            chosen, corpus = propose(corpus, lib, holes, cfg.k_per_round,
                                     name_for=lambda i, r=r: f"a{r}_{i}",
                                     blacklist=frozenset(blacklist), existing_bodies=frozenset(existing),
                                     max_holes=cfg.max_holes, max_depth=cfg.max_depth)
            for name, body, _stats in chosen:
                lib[name].meta.update({"round": r, "status": "active",
                                       "inlined_size": inline(body, lib).size()})
                active.append(name)
                idle[name] = 0
                pending_names.append(name)
        elif cond.abstraction == "search":
            train_ids = [t.tid for t in learn + val]

            def train_score(names, corp, train_ids=train_ids):
                nonlocal total_values
                cm = fit_costs(corp.values(), names, alpha=cfg.alpha)
                rs, inf = evaluate(names, cm)
                total_values += rs.n_values
                return sum(1 for tid in train_ids if inf.get(tid, {}).get("strict"))

            cur = train_score(active, corpus)
            n_eval = 0
            for i in range(cfg.k_per_round):
                existing = {str(lib[n].body) for n in lib if lib[n].body is not None}
                cands = score_candidates(corpus, lib, ALL_TYPES, frozenset(blacklist),
                                         frozenset(existing), cfg.max_holes, cfg.max_depth)
                best = None
                for j, (frag, stats) in enumerate(cands[: cfg.search_top_m]):
                    cname = f"s{r}_{i}_{j}"
                    corp2 = register(cname, frag, stats, corpus, lib)
                    sc = train_score([*active, cname], corp2)
                    n_eval += 1
                    if best is None or sc > best[0]:
                        if best is not None:
                            del lib[best[1]]
                        best = (sc, cname, corp2, stats)
                    else:
                        del lib[cname]
                if best is None or best[0] <= cur:
                    if best is not None:
                        blacklist.add(str(lib[best[1]].body))
                        del lib[best[1]]
                    break
                sc, cname, corp2, stats = best
                name = f"a{r}_{i}"
                lib[name] = lib.pop(cname)
                lib[name].name = name
                corpus = {t: rewrite(tr, name, lib[name].body, lib) for t, tr in corpus.items()}
                lib[name].meta.update({"round": r, "status": "active", "train_solved": sc,
                                       "train_solved_before": cur,
                                       "inlined_size": inline(lib[name].body, lib).size()})
                active.append(name)
                idle[name] = 0
                pending_names.append(name)
                cur = sc
            events.append({"round": r, "event": f"search: evaluated {n_eval} candidates, accepted {pending_names}"})
        elif cond.abstraction == "prospective":
            # EXP-002: learn from the near misses of learn-tasks not yet solved.
            unsolved = [t for t in learn if not info.get(t.tid, {}).get("strict")]
            misses = near_misses(res.bank, unsolved, k=cfg.nearmiss_k, w_elements=cfg.nearmiss_w_elements)
            nm_corpus = {}
            for tid, entries in misses.items():
                for j, (node, _d) in enumerate(entries):
                    nm_corpus[tid if cfg.nearmiss_k == 1 else f"{tid}#{j}"] = node
            existing = {str(lib[n].body) for n in lib if lib[n].body is not None}
            chosen, _ = propose(nm_corpus, lib, ALL_TYPES, cfg.k_per_round,
                                name_for=lambda i, r=r: f"p{r}_{i}",
                                blacklist=frozenset(blacklist), existing_bodies=frozenset(existing),
                                max_holes=cfg.max_holes, max_depth=cfg.max_depth)
            for name, body, _stats in chosen:
                corpus = {t: rewrite(tr, name, body, lib) for t, tr in corpus.items()}
                lib[name].meta.update({"round": r, "status": "active", "source": "near-miss",
                                       "inlined_size": inline(body, lib).size()})
                active.append(name)
                idle[name] = 0
                pending_names.append(name)
            events.append({"round": r, "event": f"near misses for {len(misses)} unsolved tasks; "
                                                f"proposed {[n for n, _b, _s in chosen]}"})
        elif cond.abstraction == "onestep":
            # EXP-002b: learn from one-step completions of unsolved learn-tasks.
            unsolved = [t for t in learn if not info.get(t.tid, {}).get("strict")]
            os_corpus, n_evals = completions(res.bank, unsolved, lib, Xtr, cfg.budget,
                                             order=cfg.onestep_order, include_concat=cfg.onestep_concat)
            total_values += n_evals  # the completion checks are effort, so they're counted
            existing = {str(lib[n].body) for n in lib if lib[n].body is not None}
            chosen, _ = propose(os_corpus, lib, ALL_TYPES, cfg.k_per_round,
                                name_for=lambda i, r=r: f"q{r}_{i}",
                                blacklist=frozenset(blacklist), existing_bodies=frozenset(existing),
                                max_holes=cfg.max_holes, max_depth=cfg.max_depth)
            for name, body, _stats in chosen:
                corpus = {t: rewrite(tr, name, body, lib) for t, tr in corpus.items()}
                lib[name].meta.update({"round": r, "status": "active", "source": "one-step",
                                       "inlined_size": inline(body, lib).size()})
                active.append(name)
                idle[name] = 0
                pending_names.append(name)
            events.append({"round": r, "event": f"one-step near misses for {len(os_corpus)} of {len(unsolved)} "
                                                f"unsolved tasks ({n_evals} evaluations); "
                                                f"proposed {[n for n, _b, _s in chosen]}"})
        elif cond.abstraction == "random":
            for i in range(cfg.k_per_round):
                frag = random_fragment(rng, lib, active, Xtr)
                if frag is None:
                    continue
                name = f"r{r}_{i}"
                lib[name] = make_abstraction(name, frag, lib, kind="random",
                                             meta={"round": r, "status": "active"})
                active.append(name)
                pending_names.append(name)

        if cond.prune:
            usage = {n: 0 for n in active if lib[n].kind != "base"}
            trees = list(corpus.values()) + [lib[n].body for n in usage]
            for tr in trees:
                for nd in tr.nodes():
                    if nd.op in usage:
                        usage[nd.op] += 1
            for n in list(usage):
                # a body references itself zero times; usage>0 means some use
                idle[n] = 0 if usage[n] > 0 else idle.get(n, 0) + 1
                if idle[n] >= cfg.prune_after:
                    active.remove(n)
                    lib[n].meta["status"] = "deprecated"
                    lib[n].meta["deprecated_round"] = r
                    events.append({"round": r, "event": f"deprecated {n}"})

        if cond.learn_grammar:
            costs = fit_costs(corpus.values(), active, alpha=cfg.alpha)
        else:
            costs = uniform_costs(active)

    # ------------------------------------------------------------ final metrics
    final_info = info
    per_task = {}
    for t in test:
        e = final_info.get(t.tid)
        per_task[t.tid] = {
            "level": t.level, "rtype": t.rtype,
            "strict": bool(e and e["strict"]), "found": bool(e),
            "index": e["index"] if e else None,
            "size": e["node"].size() if e else None,
            "inlined_size": inline(e["node"], lib).size() if e else None,
            "program": str(e["node"]) if e else None,
            "uses_learned": sorted({n.op for n in e["node"].nodes()
                                    if n.op in lib and lib[n.op].kind != "base"}) if e else [],
        }
    registry = []
    for n, p in lib.items():
        if p.kind == "base":
            continue
        registry.append({"name": n, "kind": p.kind, "body": str(p.body), "ret": p.ret,
                         "args": list(p.args), "cost_final": costs.get(n), **p.meta})
    return {
        "condition": cond.name, "rounds": rounds, "events": events,
        "test_per_task": per_task, "registry": registry,
        "total_values": total_values, "final_active_learned": [n for n in active if lib[n].kind != "base"],
    }

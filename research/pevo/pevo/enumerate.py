"""Cost-ordered bottom-up enumeration with observational equivalence.

Programs are enumerated in increasing integer cost (sum of production costs),
in the style of Probe (Barke, Peleg & Polikarpova, OOPSLA 2020).  Each
distinct behaviour (value signature on the shared training inputs) is kept
once, with the cheapest program that produces it.

Because every task in EXP-001 shares the same input examples, one enumeration
serves all tasks: we look each new data value up in a target table.

The search budget is the number of *distinct values* admitted to the bank.
That is hardware-independent and identical across experimental conditions.
"""
from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass
from itertools import product

from .dsl import ALL_TYPES, DATA_TYPES, Invalid, L, Node, apply, value_key


def compositions(total: int, k: int):
    """All ordered k-tuples of positive ints summing to total."""
    if k == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - k + 2):
        for rest in compositions(total - first, k - 1):
            yield (first, *rest)


@dataclass
class EnumResult:
    found: dict  # task_id -> (Node, cost, index)
    n_values: int
    max_cost_completed: int
    seconds: float
    # Every admitted (program, value) by type and cost, in admission order.
    # Only filled when requested (EXP-002 near misses); None otherwise.
    bank: dict | None = None


def enumerate_programs(active, lib, X, budget, targets, x_cost, cost_cap=120, return_bank=False):
    """Enumerate programs over ``active`` productions.

    active  : list of Prod to search over (each with integer .cost >= 1)
    lib     : dict name -> Prod (all productions, for evaluating abstractions)
    X       : tuple of input lists (shared by all tasks)
    budget  : max number of distinct values admitted
    targets : dict (type, value) -> list[task_id]
    x_cost  : cost of the input leaf ``x``
    return_bank : also return every admitted (program, value), for near-miss
                  analysis (EXP-002). Does not change what is enumerated.
    """
    t0 = time.perf_counter()
    banks = {t: defaultdict(list) for t in ALL_TYPES}
    seen = {t: set() for t in ALL_TYPES}
    found = {}
    n = 0
    prods = sorted(active, key=lambda p: (p.cost, p.name))

    def admit(node, v, t, c):
        nonlocal n
        key = value_key(v, t)
        if key in seen[t]:
            return False
        seen[t].add(key)
        banks[t][c].append((node, v))
        n += 1
        if t in DATA_TYPES:
            for tid in targets.get((t, key), ()):
                if tid not in found:
                    found[tid] = (node, c, n)
        return True

    max_done = 0
    for c in range(1, cost_cap + 1):
        if c == x_cost:
            admit(Node("x"), X, L, c)
            if n >= budget:
                return EnumResult(found, n, max_done, time.perf_counter() - t0, banks if return_bank else None)
        for p in prods:
            if p.cost > c:
                break
            r = c - p.cost
            k = len(p.args)
            if k == 0:
                if r != 0:
                    continue
                try:
                    v = apply(p, [], X, lib)
                except Invalid:
                    continue
                admit(Node(p.name), v, p.ret, c)
                if n >= budget:
                    return EnumResult(found, n, max_done, time.perf_counter() - t0, banks if return_bank else None)
                continue
            if r < k:
                continue
            for split in compositions(r, k):
                pools = []
                ok = True
                for t, ci in zip(p.args, split, strict=False):
                    pool = banks[t].get(ci)
                    if not pool:
                        ok = False
                        break
                    pools.append(pool)
                if not ok:
                    continue
                # snapshot sizes: entries admitted at cost c are never used at c
                for combo in product(*pools):
                    try:
                        v = apply(p, [e[1] for e in combo], X, lib)
                    except (Invalid, RecursionError):
                        continue
                    if admit(Node(p.name, tuple(e[0] for e in combo)), v, p.ret, c) and n >= budget:
                        return EnumResult(found, n, max_done, time.perf_counter() - t0, banks if return_bank else None)
        max_done = c
    return EnumResult(found, n, max_done, time.perf_counter() - t0, banks if return_bank else None)

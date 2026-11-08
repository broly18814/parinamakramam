"""Near misses: for a task the search failed, the attempt that came closest.

Plain picture: on a test question you got wrong, which of your rough
attempts was nearest to the right answer? EXP-002 learns building blocks
from these near misses instead of from already-solved tasks.

Definitions are fixed by the pre-registration (docs/research/EXP-002-design.md):
- list outputs: half "same elements?" (multiset Dice distance), half "same
  places?" (fraction of positions that differ);
- integer outputs: relative difference, capped at 1;
- task distance: mean over the training examples.
"""
from __future__ import annotations

from collections import Counter

from .dsl import DATA_TYPES, L


def list_distance(a: tuple, b: tuple, w_elements: float = 0.5) -> float:
    if a == b:
        return 0.0
    total = len(a) + len(b)
    common = sum((Counter(a) & Counter(b)).values())
    dice = 1.0 - (2.0 * common / total if total else 1.0)
    longest = max(len(a), len(b))
    same_place = sum(1 for x, y in zip(a, b, strict=False) if x == y)
    order = 1.0 - (same_place / longest if longest else 1.0)
    return w_elements * dice + (1.0 - w_elements) * order


def int_distance(a: int, b: int) -> float:
    return min(1.0, abs(a - b) / (1 + abs(b)))


def task_distance(v: tuple, y: tuple, rtype: str, w_elements: float = 0.5) -> float:
    if rtype == L:
        ds = [list_distance(a, b, w_elements) for a, b in zip(v, y, strict=True)]
    else:
        ds = [int_distance(a, b) for a, b in zip(v, y, strict=True)]
    return sum(ds) / len(ds)


def near_misses(bank: dict, tasks: list, k: int = 1, w_elements: float = 0.5) -> dict:
    """For each task, its k nearest bank entries of the same output type.

    Returns {task_id: [(node, distance), ...]} sorted nearest first; ties go
    to the cheaper program, then the one admitted earlier.
    """
    out: dict = {}
    for t in tasks:
        if t.rtype not in DATA_TYPES:
            continue
        scored = []
        order = 0
        for cost in sorted(bank.get(t.rtype, {})):
            for node, v in bank[t.rtype][cost]:
                scored.append((task_distance(v, t.y_train, t.rtype, w_elements), cost, order, node))
                order += 1
        scored.sort(key=lambda e: (e[0], e[1], e[2]))
        out[t.tid] = [(node, d) for d, _c, _o, node in scored[:k]]
    return out

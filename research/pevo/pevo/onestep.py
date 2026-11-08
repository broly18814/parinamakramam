"""EXP-002b: near misses chosen by structure (docs/research/EXP-002b-design.md).

Plain picture: a student's working is right up to the last line. If adding
ONE more line makes the answer exactly right, that working is worth studying.

A bank program ``e`` (list-valued) is a near miss for an unsolved task if one
of a fixed set of one-step operations turns its outputs into exactly the
task's training outputs. The completed program ``op(e)`` is then a solution on
the training examples, and the abstraction step learns from it.

Effort is capped: every operation applied to a bank value counts as one
evaluation, and evaluations stop at ``budget`` (the registered cap is B, so a
learner using this spends at most 2x the effort of one that doesn't).
"""
from __future__ import annotations

from .dsl import Invalid, L, Node, apply, value_key

FII_LEAVES = ("add1", "sub1", "double", "neg", "half", "mod3")
FIB_LEAVES = ("even", "odd", "pos", "isneg")


def step_ops(include_concat: bool = True) -> list[tuple[str, tuple[str, ...]]]:
    """The registered one-step operations, in their fixed order.

    Each is (production, leaf arguments); the bank value takes the remaining
    list slot. For concat, the second element says where ``x`` goes."""
    ops: list[tuple[str, tuple[str, ...]]] = []
    ops += [(p, ()) for p in ("reverse", "sort", "tail", "dedup")]
    ops += [(p, ()) for p in ("sum", "length", "max", "min", "head", "last")]
    ops += [("map", (f,)) for f in FII_LEAVES]
    ops += [("filter", (p,)) for p in FIB_LEAVES]
    ops += [("count", (p,)) for p in FIB_LEAVES]
    if include_concat:
        ops += [("concat", ("e,x",)), ("concat", ("x,e",))]
    return ops


def _bank_order(bank: dict, order: str) -> list[tuple[Node, tuple]]:
    """List-valued bank entries, frontier first (highest cost) or cheapest first.
    Ties keep admission order."""
    costs = sorted(bank.get(L, {}), reverse=(order == "frontier"))
    return [entry for c in costs for entry in bank[L][c]]


def completions(bank: dict, tasks: list, lib: dict, X, budget: int,
                order: str = "frontier", include_concat: bool = True) -> tuple[dict, int]:
    """For each task, the first one-step completion (in the registered order)
    whose outputs equal its training outputs exactly.

    Returns ({task_id: completed Node}, number of evaluations used)."""
    wanted: dict = {}
    for t in tasks:
        wanted.setdefault((t.rtype, value_key(t.y_train, t.rtype)), []).append(t.tid)
    found: dict = {}
    if not wanted:
        return found, 0
    ops = step_ops(include_concat)
    leaf_vals = {name: apply(lib[name], [], X, lib) for name in FII_LEAVES + FIB_LEAVES}
    evals = 0
    for node, v in _bank_order(bank, order):
        for prod, leaves in ops:
            if evals >= budget:
                return found, evals
            evals += 1
            p = lib[prod]
            try:
                if prod == "concat":
                    e_first = leaves[0] == "e,x"
                    args = [v, X] if e_first else [X, v]
                    kids = (node, Node("x")) if e_first else (Node("x"), node)
                else:
                    args = [leaf_vals[a] for a in leaves] + [v]
                    kids = (*(Node(a) for a in leaves), node)
                w = apply(p, args, X, lib)
            except (Invalid, RecursionError):
                continue
            for tid in wanted.get((p.ret, value_key(w, p.ret)), ()):
                if tid not in found:
                    found[tid] = Node(prod, kids)
            if len(found) == sum(len(v_) for v_ in wanted.values()):
                return found, evals
    return found, evals

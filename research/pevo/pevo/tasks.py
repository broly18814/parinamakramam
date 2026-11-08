"""Task distributions for EXP-001.

D-struct : tasks are compositions of a hidden library of 'concepts' (some of
           them higher-order, parameterised by a function or predicate).  The
           learner never sees the hidden library; it only sees I/O examples.
D-flat   : random programs over the base DSL P0 with the same size
           distribution, i.e. no planted reusable structure.

The comparison between the two is how EXP-001 asks *under which conditions*
library/substrate evolution helps (thesis question Q1).
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .dsl import FIB, FII, I, Invalid, L, Node, eval_tree, value_key

N = Node
X_ = N("x")

FII_PARAMS = [N("add1"), N("sub1"), N("double"), N("neg"), N("half"), N("mod3"),
              N("compose", (N("add1"), N("double")))]
FIB_PARAMS = [N("even"), N("odd"), N("pos"), N("isneg"), N("notp", (N("pos"),))]

# Hidden concepts: name -> (param kinds, builder(params, arg) -> Node)
CONCEPTS = {
    "A_sortdedup": ((), lambda ps, a: N("sort", (N("dedup", (a,)),))),
    "B_revtail": ((), lambda ps, a: N("reverse", (N("tail", (a,)),))),
    "C_mapsorted": ((FII,), lambda ps, a: N("map", (ps[0], N("sort", (a,))))),
    "D_filtrev": ((FIB,), lambda ps, a: N("filter", (ps[0], N("reverse", (a,))))),
    "E_mapfilt": ((FII, FIB), lambda ps, a: N("map", (ps[0], N("filter", (ps[1], a))))),
    "F_mirror": ((), lambda ps, a: N("concat", (a, N("reverse", (a,))))),
}
REDUCERS = ["sum", "max", "length", "head", "last", "count"]


@dataclass
class Task:
    tid: str
    tree: Node  # hidden ground-truth program (analysis only)
    rtype: str
    y_train: tuple
    y_hold: tuple
    level: int
    concepts: tuple = ()
    params: tuple = field(default_factory=tuple)  # (concept, param-string) pairs


def make_inputs(rng: random.Random, n: int):
    xs = []
    for _ in range(n):
        ln = rng.randint(4, 8)
        xs.append(tuple(rng.randint(-6, 12) for _ in range(ln)))
    return tuple(xs)


def _ok(tree, Xtr, Xho, lib, rtype, seen):
    try:
        ytr = eval_tree(tree, Xtr, lib)
        yho = eval_tree(tree, Xho, lib)
    except Invalid:
        return None
    if rtype == L:
        if ytr == Xtr:
            return None
        if sum(1 for y in ytr if len(y) == 0) >= 3:
            return None
    if len(set(ytr)) <= 1:
        return None
    key = (rtype, value_key(ytr, rtype))
    if key in seen:
        return None
    return ytr, yho, key


def sample_struct(rng, level, lib, Xtr, Xho, seen, max_tries=200):
    for _ in range(max_tries):
        seq = []
        for _ in range(level):
            choices = [c for c in CONCEPTS if not seq or c != seq[-1]]
            seq.append(rng.choice(choices))
        t = X_
        params = []
        for cname in seq:
            kinds, build = CONCEPTS[cname]
            ps = [rng.choice(FII_PARAMS if k == FII else FIB_PARAMS) for k in kinds]
            for p in ps:
                params.append((cname, str(p)))
            t = build(ps, t)
        rtype = L
        if rng.random() < 0.3:
            r = rng.choice(REDUCERS)
            t = N(r, (rng.choice(FIB_PARAMS), t)) if r == "count" else N(r, (t,))
            rtype = I
        res = _ok(t, Xtr, Xho, lib, rtype, seen)
        if res is None:
            continue
        ytr, yho, key = res
        seen.add(key)
        return Task("", t, rtype, ytr, yho, level, tuple(seq), tuple(params))
    return None


def _random_tree(rng, t, size, lib, base_names):
    """Random typed tree over base prods with exactly ``size`` nodes (or None)."""
    MIN = {L: 1, FII: 1, FIB: 1, I: 2}
    if size == 1:
        if t == L:
            return X_
        leaves = [n for n in base_names if lib[n].ret == t and not lib[n].args]
        return N(rng.choice(leaves)) if leaves else None
    cands = [n for n in base_names if lib[n].ret == t and lib[n].args
             and sum(MIN[a] for a in lib[n].args) <= size - 1]
    if not cands:
        return None
    name = rng.choice(cands)
    args = lib[name].args
    rem = size - 1
    # random split respecting minimums
    mins = [MIN[a] for a in args]
    extra = rem - sum(mins)
    cuts = sorted(rng.randint(0, extra) for _ in range(len(args) - 1))
    parts = [b - a for a, b in zip([0] + cuts, cuts + [extra])]
    kids = []
    for a, m, e in zip(args, mins, parts):
        k = _random_tree(rng, a, m + e, lib, base_names)
        if k is None:
            return None
        kids.append(k)
    return N(name, tuple(kids))


def sample_flat(rng, size, lib, base_names, Xtr, Xho, seen, max_tries=400):
    for _ in range(max_tries):
        rtype = I if rng.random() < 0.3 else L
        t = _random_tree(rng, rtype, size, lib, base_names)
        if t is None:
            continue
        res = _ok(t, Xtr, Xho, lib, rtype, seen)
        if res is None:
            continue
        ytr, yho, key = res
        seen.add(key)
        return Task("", t, rtype, ytr, yho, level=0)
    return None


def build_suite(dist: str, seed: int, lib: dict, n_train=100, n_test=60):
    """Return (Xtr, Xho, train_tasks, test_tasks)."""
    rng = random.Random(seed)
    Xtr = make_inputs(rng, 6)
    Xho = make_inputs(rng, 4)
    seen = set()
    base_names = sorted(n for n, p in lib.items() if p.kind == "base")
    train, test = [], []
    if dist == "struct":
        per = n_train // 3
        for lvl in (1, 2, 3):
            while sum(1 for t in train if t.level == lvl) < per:
                tk = sample_struct(rng, lvl, lib, Xtr, Xho, seen)
                if tk is None:
                    break
                train.append(tk)
        train_seqs = {t.concepts for t in train}
        per_t = n_test // 3
        for lvl in (2, 3, 4):
            tries = 0
            while sum(1 for t in test if t.level == lvl) < per_t and tries < 5000:
                tries += 1
                tk = sample_struct(rng, lvl, lib, Xtr, Xho, seen)
                if tk is None:
                    break
                if lvl >= 3 and tk.concepts in train_seqs:
                    seen.discard((tk.rtype, value_key(tk.y_train, tk.rtype)))
                    continue
                test.append(tk)
    elif dist == "flat":
        # match size distribution of struct tasks
        ref_tr, ref_te = build_suite("struct", seed, lib, n_train, n_test)[2:]
        for ref, out in ((ref_tr, train), (ref_te, test)):
            for r in ref:
                tk = sample_flat(rng, r.tree.size(), lib, base_names, Xtr, Xho, seen)
                if tk is not None:
                    tk.level = r.level
                    out.append(tk)
    else:
        raise ValueError(dist)
    for i, t in enumerate(train):
        t.tid = f"tr{i:03d}"
    for i, t in enumerate(test):
        t.tid = f"te{i:03d}"
    return Xtr, Xho, train, test

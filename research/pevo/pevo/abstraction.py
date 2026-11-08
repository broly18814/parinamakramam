"""Library learning: abstraction proposal, MDL utility, corpus rewriting,
probabilistic grammar fitting and random-fragment control.

The abstraction step is a simplified, exhaustive-within-limits variant of
Stitch-style compression (Bowers et al., POPL 2023): every subtree of every
solution is generalised by replacing up to ``max_holes`` non-nested
descendants (depth <= ``max_depth``) with typed holes.  A fragment's usage is
the number of subtrees it generalises; utility approximates the reduction in
corpus description length:

    U(f) = uses(f) * (|f| - 1) - |f|,     |f| = non-hole node count

``allowed_hole_types`` is the switch between data-only abstraction (C2) and
higher-order abstraction over functions/predicates (C3): the latter changes
the composition grammar itself, because the new production takes
function-typed arguments.
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from itertools import combinations

from .dsl import (
    DATA_TYPES,
    Invalid,
    L,
    Node,
    eval_tree,
    hole,
    hole_index,
    hole_type,
    make_abstraction,
    node_type,
)

# ------------------------------------------------------------ generalisation

def _positions(node: Node, max_depth: int, path=()):
    """Paths to proper descendants up to max_depth."""
    out = []
    for i, k in enumerate(node.kids):
        p = (*path, i)
        out.append(p)
        if len(p) < max_depth:
            out.extend(_positions(k, max_depth, p))
    return out


def _get(node, path):
    for i in path:
        node = node.kids[i]
    return node


def _replace(node: Node, repl: dict, path=()):
    if path in repl:
        return repl[path]
    if not node.kids:
        return node
    return Node(node.op, tuple(_replace(k, repl, (*path, i)) for i, k in enumerate(node.kids)))


def _nested(a, b):
    return a[: len(b)] == b or b[: len(a)] == a


def generalisations(node: Node, lib, allowed_hole_types, max_holes=2, max_depth=3):
    if not node.kids:
        return
    pos = _positions(node, max_depth)
    for k in range(0, max_holes + 1):
        for subset in combinations(pos, k):
            if any(_nested(a, b) for a, b in combinations(subset, 2)):
                continue
            types = [node_type(_get(node, p), lib) for p in subset]
            if any(t not in allowed_hole_types for t in types):
                continue
            # holes numbered in preorder (combinations of a preorder list keep order)
            repl = {p: hole(i, t) for i, (p, t) in enumerate(zip(subset, types, strict=False))}
            frag = _replace(node, repl)
            if frag.size() >= 2:
                yield frag


# ------------------------------------------------------------ matching / rewrite

def match(frag: Node, node: Node, lib, binds: dict) -> bool:
    if frag.op[0] == "#":
        i = hole_index(frag.op)
        if node_type(node, lib) != hole_type(frag.op):
            return False
        if i in binds:
            return binds[i] == node
        binds[i] = node
        return True
    if frag.op != node.op or len(frag.kids) != len(node.kids):
        return False
    return all(match(f, n, lib, binds) for f, n in zip(frag.kids, node.kids, strict=False))


def rewrite(tree: Node, name: str, body: Node, lib) -> Node:
    b = {}
    if match(body, tree, lib, b):
        args = tuple(rewrite(b[i], name, body, lib) for i in range(len(b)))
        return Node(name, args)
    if not tree.kids:
        return tree
    return Node(tree.op, tuple(rewrite(k, name, body, lib) for k in tree.kids))


# ------------------------------------------------------------ proposal

def score_candidates(corpus: dict, lib, allowed_hole_types, blacklist=frozenset(),
                     existing_bodies=frozenset(), max_holes=2, max_depth=3, min_tasks=2):
    """All admissible fragments with MDL utility > 0, best first.

    Returns list of (fragment, stats) sorted by (-utility, key)."""
    uses = Counter()
    tasks = defaultdict(set)
    for tid, tree in corpus.items():
        for sub in tree.nodes():
            for frag in set(generalisations(sub, lib, allowed_hole_types, max_holes, max_depth)):
                key = str(frag)
                uses[key] += 1
                tasks[key].add(tid)
                if key not in _FRAG:
                    _FRAG[key] = frag
    out = []
    for key, u in uses.items():
        if len(tasks[key]) < min_tasks or key in blacklist or key in existing_bodies:
            continue
        f = _FRAG[key]
        util = u * (f.size() - 1) - f.size()
        if util > 0:
            out.append((f, {"utility": util, "uses": u, "n_tasks": len(tasks[key])}))
    out.sort(key=lambda e: (-e[1]["utility"], str(e[0])))
    return out


def register(name, body, stats, corpus, lib):
    lib[name] = make_abstraction(name, body, lib, meta=dict(stats))
    return {t: rewrite(tr, name, body, lib) for t, tr in corpus.items()}


def propose(corpus: dict, lib, allowed_hole_types, k, name_for, blacklist=frozenset(),
            existing_bodies=frozenset(), max_holes=2, max_depth=3, min_tasks=2):
    """Greedy top-k abstraction selection by MDL utility (retrospective
    compression), rewriting the corpus between picks so that later picks may
    build on earlier ones.  Chosen abstractions are registered in ``lib``.

    Returns (list of (name, body, stats), rewritten corpus)."""
    chosen = []
    corpus = dict(corpus)
    for _ in range(k):
        cands = score_candidates(corpus, lib, allowed_hole_types, blacklist,
                                 existing_bodies, max_holes, max_depth, min_tasks)
        if not cands:
            break
        best, stats = cands[0]
        name = name_for(len(chosen))
        chosen.append((name, best, stats))
        corpus = register(name, best, stats, corpus, lib)
        existing_bodies = existing_bodies | {str(best)}
    return chosen, corpus


_FRAG: dict = {}


# ------------------------------------------------------------ grammar

def fit_costs(corpus_trees, active_names, alpha=1.0, x_name="x"):
    """Unigram PCFG fit -> integer costs  c = max(1, round(-log2 p))."""
    cnt = Counter()
    for t in corpus_trees:
        for n in t.nodes():
            cnt[n.op] += 1
    names = [*list(active_names), x_name]
    total = sum(cnt[n] for n in names) + alpha * len(names)
    return {n: max(1, round(-math.log2((cnt[n] + alpha) / total))) for n in names}


def uniform_costs(active_names, x_name="x"):
    m = len(active_names) + 1
    c = max(1, round(math.log2(m)))
    return {n: c for n in [*list(active_names), x_name]}


# ------------------------------------------------------------ random control

def random_fragment(rng: random.Random, lib, active_names, X, tries=200):
    """A random well-typed, evaluable fragment of size 2..5 with 0..2 data holes."""
    names = sorted(active_names)
    for _ in range(tries):
        root = lib[rng.choice(names)]
        if not root.args:
            continue
        kids = []
        for t in root.args:
            if t == L:
                kids.append(Node("x") if rng.random() < 0.5 else _rand_unary(rng, lib, names, L))
            else:
                kids.append(_rand_unary(rng, lib, names, t))
        if any(k is None for k in kids):
            continue
        frag = Node(root.name, tuple(kids))
        pos = _positions(frag, 3)
        pos = [p for p in pos if node_type(_get(frag, p), lib) in DATA_TYPES]
        rng.shuffle(pos)
        chosen = []
        for p in pos:
            if len(chosen) >= rng.randint(0, 2):
                break
            if all(not _nested(p, q) for q in chosen):
                chosen.append(p)
        chosen.sort()
        repl = {p: hole(i, node_type(_get(frag, p), lib)) for i, p in enumerate(chosen)}
        frag = _replace(frag, repl)
        if frag.size() < 2 or frag.size() > 5:
            continue
        try:
            # evaluate with holes bound to x / a plausible value
            env = []
            for _i, t in [(hole_index(n.op), hole_type(n.op)) for n in frag.nodes() if n.op[0] == "#"]:
                env.append(X if t == L else tuple(len(a) for a in X))
            eval_tree(frag, X, lib, env=env)
        except (Invalid, KeyError, IndexError):
            continue
        return frag
    return None


def _rand_unary(rng, lib, names, t):
    if t == L:
        c = [n for n in names if lib[n].ret == L and lib[n].args == (L,)]
        return Node(rng.choice(c), (Node("x"),)) if c else Node("x")
    leaves = [n for n in names if lib[n].ret == t and not lib[n].args and lib[n].kind == "base"]
    return Node(rng.choice(leaves)) if leaves else None

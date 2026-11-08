"""EXP-005: building blocks learned from real code (docs/research/EXP-005-design.md).

Plain picture: read a writer's earlier books, note the phrases they keep
reusing, and check whether those phrases also fill their next book.

Here a "phrase" is the *shape* of a piece of Python code: its syntax tree
with variable names made generic, string and unusual number constants
replaced by placeholders, and up to two parts left blank (holes). A library
of K such shapes is chosen greedily by how much space it saves (MDL, the same
principle as EXP-001's shortening). Then we measure how much it shortens code
written *later*.

Everything here reads code; nothing is executed.
"""
from __future__ import annotations

import ast
import copy
import heapq
import random
from collections import Counter
from dataclasses import dataclass, field
from itertools import combinations

HOLE = ("HOLE",)
# Python shares one object for every `+`, `==`, `and`, `not`, Load, ... so these
# can't identify a position in the code. They count towards size, but never
# towards "which nodes are already used".
SHARED = (ast.expr_context, ast.boolop, ast.operator, ast.unaryop, ast.cmpop)
KEEP_NUMBERS = {-1, 0, 1, 2}
MIN_SIZE = 4


# ---------------------------------------------------------------- normalising

class _Normaliser(ast.NodeTransformer):
    def __init__(self, local_names: dict[str, str]):
        self.names = local_names

    def visit_Name(self, node: ast.Name) -> ast.AST:
        if node.id in self.names:
            node.id = self.names[node.id]
        return node

    def visit_arg(self, node: ast.arg) -> ast.AST:
        self.generic_visit(node)
        if node.arg in self.names:
            node.arg = self.names[node.arg]
        return node

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.AST:
        self.generic_visit(node)
        if node.name and node.name in self.names:
            node.name = self.names[node.name]
        return node

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        v = node.value
        if isinstance(v, (str, bytes)):
            return ast.copy_location(ast.Constant("STR"), node)
        if isinstance(v, (int, float, complex)) and not isinstance(v, bool) and v not in KEEP_NUMBERS:
            return ast.copy_location(ast.Constant("NUM"), node)
        return node


def _local_names(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, str]:
    """Arguments and names assigned inside the function, numbered v0, v1, ...
    in the order they first appear (ast.walk order, which is deterministic)."""
    found: list[str] = []

    def add(n: str) -> None:
        if n not in found:
            found.append(n)

    for node in ast.walk(fn):
        if node is fn:
            continue
        if isinstance(node, ast.arg):
            add(node.arg)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            add(node.id)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            add(node.name)
    for a in (fn.args.posonlyargs + fn.args.args + fn.args.kwonlyargs
              + [x for x in (fn.args.vararg, fn.args.kwarg) if x]):
        if a.arg not in found:
            found.insert(0, a.arg)
    return {n: f"v{i}" for i, n in enumerate(found)}


def normalise(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.AST:
    """A normalised copy of one function (its name kept, docstring removed)."""
    fn = copy.deepcopy(fn)
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(fn.body[0].value, ast.Constant) \
            and isinstance(fn.body[0].value.value, str):
        fn.body = fn.body[1:] or [ast.Pass()]
    return _Normaliser(_local_names(fn)).visit(fn)


def functions(source: str) -> list[tuple[str, ast.AST]]:
    """(qualified name, normalised tree) for every def/async def, at any depth."""
    out: list[tuple[str, ast.AST]] = []

    def walk(node: ast.AST, prefix: str) -> None:
        for ch in ast.iter_child_nodes(node):
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((prefix + ch.name, normalise(ch)))
                walk(ch, prefix + ch.name + ".")
            elif isinstance(ch, ast.ClassDef):
                walk(ch, prefix + ch.name + ".")
    walk(ast.parse(source), "")
    return out


# ---------------------------------------------------------------- sizes and shapes

def _children(node: ast.AST):
    """(field, index, child) for each child AST node, skipping load/store markers."""
    for name, value in ast.iter_fields(node):
        if isinstance(value, list):
            for i, v in enumerate(value):
                if isinstance(v, ast.AST) and not isinstance(v, ast.expr_context):
                    yield name, i, v
        elif isinstance(value, ast.AST) and not isinstance(value, ast.expr_context):
            yield name, None, value


def size(node: ast.AST) -> int:
    return 1 + sum(size(c) for _f, _i, c in _children(node))


def shape(node: ast.AST, holes: frozenset = frozenset()) -> tuple:
    """A hashable description of a subtree; children whose id() is in `holes` become HOLE."""
    if id(node) in holes:
        return HOLE
    parts: list = [type(node).__name__]
    for name, value in ast.iter_fields(node):
        if isinstance(value, ast.expr_context):
            continue
        if isinstance(value, list):
            parts.append((name, tuple(shape(v, holes) if isinstance(v, ast.AST) else v for v in value)))
        elif isinstance(value, ast.AST):
            parts.append((name, shape(value, holes)))
        else:
            parts.append((name, value))
    return tuple(parts)


def _ids(node: ast.AST) -> list[int]:
    out = [] if isinstance(node, SHARED) else [id(node)]
    for _f, _i, c in _children(node):
        out.extend(_ids(c))
    return out


@dataclass
class Site:
    covered: frozenset  # ids of the nodes this occurrence would replace


@dataclass
class Block:
    key: tuple
    size: int            # nodes, not counting holes
    holes: int
    example: str = ""    # readable normalised form, holes shown as HOLE
    uses_in_training: int = 0


@dataclass
class Corpus:
    """Normalised functions plus every candidate shape that occurs at least twice."""

    trees: list[ast.AST]
    max_size: int
    candidates: dict = field(default_factory=dict)   # key -> list[Site]
    meta: dict = field(default_factory=dict)         # key -> (size without holes, holes, example node, hole ids)

    @property
    def total_size(self) -> int:
        return sum(size(t) for t in self.trees)


def _candidate_forms(node: ast.AST, max_size: int):
    """The subtree itself, and versions with 1 or 2 direct child expressions as holes."""
    n = size(node)
    if not MIN_SIZE <= n <= max_size:
        return
    kids = [c for _f, _i, c in _children(node) if isinstance(c, ast.expr)][:6]
    yield frozenset(), n
    for k in (1, 2):
        for chosen in combinations(kids, k):
            s = n - sum(size(c) for c in chosen)
            if s >= 2:
                yield frozenset(id(c) for c in chosen), s


def build_corpus(trees: list[ast.AST], max_size: int = 40) -> Corpus:
    corpus = Corpus(trees, max_size)
    counts: Counter = Counter()
    roots = [nd for t in trees for nd in ast.walk(t) if isinstance(nd, (ast.stmt, ast.expr))]
    for nd in roots:
        for holes, _s in _candidate_forms(nd, max_size):
            counts[shape(nd, holes)] += 1
    for nd in roots:
        for holes, s in _candidate_forms(nd, max_size):
            key = shape(nd, holes)
            if counts[key] < 2:
                continue
            hole_nodes = set()
            for _f, _i, c in _children(nd):
                if id(c) in holes:
                    hole_nodes.update(_ids(c))
            covered = frozenset(i for i in _ids(nd) if i not in hole_nodes)
            corpus.candidates.setdefault(key, []).append(Site(covered))
            if key not in corpus.meta:
                corpus.meta[key] = (s, len(holes), nd, holes)
    return corpus


def _example(nd: ast.AST, holes: frozenset) -> str:
    c = copy.deepcopy(nd)
    originals = {id(a): b for a, b in zip(ast.walk(nd), ast.walk(c), strict=True)}
    targets = {id(originals[h]) for h in holes if h in originals}

    class _Hole(ast.NodeTransformer):
        def generic_visit(self, node: ast.AST) -> ast.AST:
            if id(node) in targets:
                return ast.Name("HOLE", ast.Load())
            return super().generic_visit(node)
    try:
        return ast.unparse(_Hole().visit(c))[:160]
    except Exception:  # pragma: no cover - unparse can't print every fragment on its own
        return type(nd).__name__


def _gain(sites: list[Site], s: int, used: set) -> tuple[int, list[Site]]:
    """Gain = uses x (size - 1) - size, counting only non-overlapping unused uses."""
    chosen: list[Site] = []
    taken: set = set()
    for site in sites:
        if site.covered & used or site.covered & taken:
            continue
        chosen.append(site)
        taken |= site.covered
    return len(chosen) * (s - 1) - s, chosen


def learn(corpus: Corpus, k: int) -> list[Block]:
    """Greedy MDL with lazy re-evaluation (gains only shrink as nodes get used)."""
    used: set = set()
    heap = []
    for i, (key, sites) in enumerate(corpus.candidates.items()):
        s = corpus.meta[key][0]
        g, _ = _gain(sites, s, used)
        if g > 0:
            heap.append((-g, i, key))
    heapq.heapify(heap)
    library: list[Block] = []
    while heap and len(library) < k:
        _neg, i, key = heapq.heappop(heap)
        s, nholes, nd, holes = corpus.meta[key]
        g, chosen = _gain(corpus.candidates[key], s, used)
        if g <= 0:
            continue
        if heap and g < -heap[0][0]:
            heapq.heappush(heap, (-g, i, key))
            continue
        for site in chosen:
            used |= site.covered
        library.append(Block(key, s, nholes, _example(nd, holes), len(chosen)))
    return library


def random_library(corpus: Corpus, k: int, seed: int = 0) -> list[Block]:
    """K recurring candidates drawn uniformly at random (the RANDOM control)."""
    keys = sorted(corpus.candidates, key=repr)
    rng = random.Random(seed)
    picked = rng.sample(keys, min(k, len(keys)))
    out = []
    for key in picked:
        s, nholes, nd, holes = corpus.meta[key]
        out.append(Block(key, s, nholes, _example(nd, holes), len(corpus.candidates[key])))
    return out


# ---------------------------------------------------------------- applying a library

def _match(p: tuple, node: ast.AST, covered: list[int]) -> bool:
    """Does `node` have shape `p` (HOLE matches any expression)? Collects covered ids."""
    if p == HOLE:
        return isinstance(node, ast.expr)
    if not isinstance(p, tuple) or p[0] != type(node).__name__:  # e.g. an empty slot (None) in the pattern
        return False
    if not isinstance(node, SHARED):
        covered.append(id(node))
    fields = [(n, v) for n, v in ast.iter_fields(node) if not isinstance(v, ast.expr_context)]
    if len(fields) != len(p) - 1:
        return False
    for (name, value), (pname, pval) in zip(fields, p[1:], strict=True):
        if name != pname:
            return False
        if isinstance(value, list):
            if not isinstance(pval, tuple) or len(pval) != len(value):
                return False
            for v, pv in zip(value, pval, strict=True):
                if isinstance(v, ast.AST):
                    if not _match(pv, v, covered):
                        return False
                elif v != pv:
                    return False
        elif isinstance(value, ast.AST):
            if not _match(pval, value, covered):
                return False
        elif value != pval:
            return False
    return True


def rewrite_size(tree: ast.AST, library: list[Block]) -> int:
    """Size of `tree` after replacing, block by block in library order, every
    non-overlapping top-down match by a single node."""
    total = size(tree)
    used: set = set()
    nodes = [nd for nd in ast.walk(tree) if isinstance(nd, (ast.stmt, ast.expr))]
    for b in library:
        for nd in nodes:
            if id(nd) in used:
                continue
            cov: list[int] = []
            if _match(b.key, nd, cov) and not (set(cov) & used):
                used.update(cov)
                total -= b.size - 1
    return total

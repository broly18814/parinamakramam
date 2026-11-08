"""Typed list-function DSL used by EXP-001.

Types
-----
L   : list of ints (represented as a Python tuple)
I   : int
FII : int -> int   (function value)
FIB : int -> bool  (predicate value)

A *Value* of a data type (L, I) is a tuple with one entry per input example.
A *Value* of a function type is an ``Fn``: a callable plus its behavioural
signature on a fixed probe domain (used for observational equivalence).

Programs are trees of ``Node``.  Leaves are ``x`` (the input list), arity-0
productions (e.g. ``add1``) or typed holes ``#k:T`` (only inside abstraction
bodies).  Learned abstractions are productions whose semantics is given by a
body tree; they are evaluated by substituting argument values for holes.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

L, I, FII, FIB = "L", "I", "FII", "FIB"
DATA_TYPES = (L, I)
FUNC_TYPES = (FII, FIB)
ALL_TYPES = (L, I, FII, FIB)

MAX_LEN = 16
MAX_ABS = 1000
PROBE = tuple(range(-12, 25))


class Invalid(Exception):
    """Raised when a program is undefined on an input or exceeds size limits."""


class Fn:
    """A function value, compared by behaviour on PROBE."""

    __slots__ = ("f", "sig")

    def __init__(self, f: Callable):
        self.f = f
        try:
            self.sig = tuple(f(v) for v in PROBE)
        except (ZeroDivisionError, OverflowError, ValueError) as e:  # pragma: no cover
            raise Invalid(str(e)) from e

    def __eq__(self, other):
        return isinstance(other, Fn) and self.sig == other.sig

    def __hash__(self):
        return hash(self.sig)


@dataclass(frozen=True)
class Node:
    op: str
    kids: tuple = ()

    def __str__(self) -> str:
        if not self.kids:
            return self.op
        return f"({self.op} {' '.join(str(k) for k in self.kids)})"

    def size(self) -> int:
        """Number of non-hole nodes."""
        return (0 if self.op.startswith("#") else 1) + sum(k.size() for k in self.kids)

    def nodes(self):
        yield self
        for k in self.kids:
            yield from k.nodes()


def hole(i: int, t: str) -> Node:
    return Node(f"#{i}:{t}")


def hole_type(op: str) -> str:
    return op.split(":", 1)[1]


def hole_index(op: str) -> int:
    return int(op[1:].split(":", 1)[0])


@dataclass
class Prod:
    name: str
    ret: str
    args: tuple
    impl: Callable | None = None  # per-example implementation (base prods)
    body: Node | None = None  # abstraction body (learned prods)
    cost: int = 5
    kind: str = "base"  # "base" | "learned" | "random"
    meta: dict = field(default_factory=dict)


# ---------------------------------------------------------------- helpers

def _chk_list(v):
    if len(v) > MAX_LEN:
        raise Invalid("list too long")
    for e in v:
        if e > MAX_ABS or e < -MAX_ABS:
            raise Invalid("int too large")
    return v


def _chk_int(v):
    if v > MAX_ABS or v < -MAX_ABS:
        raise Invalid("int too large")
    return v


def _nonempty(v):
    if not v:
        raise Invalid("empty list")
    return v


def _dedup(v):
    seen, out = set(), []
    for e in v:
        if e not in seen:
            seen.add(e)
            out.append(e)
    return tuple(out)


# ---------------------------------------------------------------- base DSL P0

def base_prods() -> dict:
    P = {}

    def add(name, ret, args, impl):
        P[name] = Prod(name, ret, tuple(args), impl=impl)

    # L -> L
    add("reverse", L, [L], lambda a: a[::-1])
    add("sort", L, [L], lambda a: tuple(sorted(a)))
    add("tail", L, [L], lambda a: _nonempty(a)[1:])
    add("dedup", L, [L], _dedup)
    # L -> I
    add("sum", I, [L], lambda a: sum(a))
    add("length", I, [L], lambda a: len(a))
    add("max", I, [L], lambda a: max(_nonempty(a)))
    add("min", I, [L], lambda a: min(_nonempty(a)))
    add("head", I, [L], lambda a: _nonempty(a)[0])
    add("last", I, [L], lambda a: _nonempty(a)[-1])
    # L, L -> L
    add("concat", L, [L, L], lambda a, b: a + b)
    # higher-order
    add("map", L, [FII, L], lambda f, a: tuple(f(e) for e in a))
    add("filter", L, [FIB, L], lambda p, a: tuple(e for e in a if p(e)))
    add("count", I, [FIB, L], lambda p, a: sum(1 for e in a if p(e)))
    # FII leaves
    add("add1", FII, [], lambda: (lambda v: v + 1))
    add("sub1", FII, [], lambda: (lambda v: v - 1))
    add("double", FII, [], lambda: (lambda v: 2 * v))
    add("neg", FII, [], lambda: (lambda v: -v))
    add("half", FII, [], lambda: (lambda v: v // 2))
    add("mod3", FII, [], lambda: (lambda v: v % 3))
    # FIB leaves
    add("even", FIB, [], lambda: (lambda v: v % 2 == 0))
    add("odd", FIB, [], lambda: (lambda v: v % 2 == 1))
    add("pos", FIB, [], lambda: (lambda v: v > 0))
    add("isneg", FIB, [], lambda: (lambda v: v < 0))
    # function combinators
    add("compose", FII, [FII, FII], lambda f, g: (lambda v: f(g(v))))
    add("notp", FIB, [FIB], lambda p: (lambda v: not p(v)))
    return P


# ---------------------------------------------------------------- evaluation

def apply(prod: Prod, argvals, X, lib: dict):
    """Apply ``prod`` to argument Values. ``X`` is the tuple of input lists."""
    if prod.body is not None:
        return eval_tree(prod.body, X, lib, env=argvals)
    if prod.ret in FUNC_TYPES:
        return Fn(prod.impl(*[a.f for a in argvals]))
    impl = prod.impl
    if not prod.args:  # pragma: no cover - no arity-0 data base prods
        raise Invalid("arity-0 data prod")
    chk = _chk_list if prod.ret == L else _chk_int
    # Build per-example argument lists: function args are broadcast.
    cols = []
    for a, t in zip(argvals, prod.args, strict=False):
        if t in FUNC_TYPES:
            cols.append(None)
        else:
            cols.append(a)
    fargs = [a.f if t in FUNC_TYPES else None for a, t in zip(argvals, prod.args, strict=False)]
    out = []
    for i in range(len(X)):
        call = [fargs[j] if cols[j] is None else cols[j][i] for j in range(len(cols))]
        out.append(chk(impl(*call)))
    return tuple(out)


def eval_tree(node: Node, X, lib: dict, env=None):
    op = node.op
    if op == "x":
        return X
    if op[0] == "#":
        return env[hole_index(op)]
    prod = lib[op]
    vals = [eval_tree(k, X, lib, env) for k in node.kids]
    return apply(prod, vals, X, lib)


def node_type(node: Node, lib: dict) -> str:
    if node.op == "x":
        return L
    if node.op[0] == "#":
        return hole_type(node.op)
    return lib[node.op].ret


def value_key(v, t: str):
    return v.sig if t in FUNC_TYPES else v


def holes_of(body: Node):
    """Return list of (index, type) for holes in ``body`` ordered by index."""
    hs = {}
    for n in body.nodes():
        if n.op[0] == "#":
            hs[hole_index(n.op)] = hole_type(n.op)
    return [(i, hs[i]) for i in sorted(hs)]


def make_abstraction(name: str, body: Node, lib: dict, kind="learned", meta=None) -> Prod:
    hs = holes_of(body)
    assert [i for i, _ in hs] == list(range(len(hs))), "holes must be numbered 0..k-1"
    return Prod(name, node_type(body, lib), tuple(t for _, t in hs), body=body, kind=kind,
                meta=meta or {})


def inline(node: Node, lib: dict) -> Node:
    """Expand all learned abstractions to base primitives (for size comparisons)."""
    kids = tuple(inline(k, lib) for k in node.kids)
    if node.op in ("x",) or node.op[0] == "#":
        return Node(node.op, kids)
    p = lib[node.op]
    if p.body is None:
        return Node(node.op, kids)
    return inline(_subst(p.body, kids), lib)


def _subst(body: Node, args) -> Node:
    if body.op[0] == "#":
        return args[hole_index(body.op)]
    return Node(body.op, tuple(_subst(k, args) for k in body.kids))

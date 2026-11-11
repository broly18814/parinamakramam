"""EXP-006: do learned building blocks make *search* for real code cheaper?
(docs/research/EXP-006-design.md, section 4)

Plain picture: a phone keyboard guessing a hidden phrase, likeliest guess
first. We count how many partial guesses it builds before it produces the
phrase exactly. A "phrase book" (a library of building blocks) lets it type a
whole chunk in one step, but every extra option also makes every other answer
a little less likely. Which effect wins is the question.

For specialists: a probabilistic grammar over EXP-005's normalised Python
syntax trees, where a slot's context is (parent node type, field). Adding
library fragments makes it a probabilistic tree-substitution grammar.
Probabilities are smoothed relative frequencies with a fixed backoff
(alpha = 1). Best-first (A*) search with an exact, consistent completion bound
returns complete trees in order of non-increasing probability. Effort is the
number of states taken from the queue. The search looks at the target only to
test a finished tree for equality: never to steer or prune.

Everything here reads code; nothing is executed.
"""
from __future__ import annotations

import ast
import heapq
import math
import random
from collections import Counter, defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from functools import cache

from pevo.codeblocks import HOLE, MIN_SIZE, SHARED, Block, Corpus, _children, shape, size

SLOT = ("SLOT",)
ROOT_CTX = ("ROOT", "")
ROOT_CTX2 = ("ROOT", "", "ROOT", "")
ALPHA = 1.0
INF = math.inf
MAX_ROUNDS = 1000


@cache
def kind_of(type_name: str) -> str:
    """A node type's grammatical category: the class just below ast.AST (expr, stmt, operator, arguments, ...)."""
    for cls in getattr(ast, type_name).__mro__:
        if ast.AST in cls.__bases__:
            return cls.__name__
    raise ValueError(type_name)


# ---------------------------------------------------------------- base rules

def template(node: ast.AST) -> tuple[tuple, tuple[str, ...]]:
    """The node's base rule: its EXP-005 shape cut off at depth one, with every
    child node replaced by SLOT. Also the field of each slot, in filling order."""
    parts: list = [type(node).__name__]
    fields: list[str] = []
    for name, value in ast.iter_fields(node):
        if isinstance(value, ast.expr_context):
            continue
        if isinstance(value, list):
            items = []
            for v in value:
                if isinstance(v, ast.AST):
                    items.append(SLOT)
                    fields.append(name)
                else:
                    items.append(v)
            parts.append((name, tuple(items)))
        elif isinstance(value, ast.AST):
            parts.append((name, SLOT))
            fields.append(name)
        else:
            parts.append((name, value))
    return tuple(parts), tuple(fields)


def base_templates(node: ast.AST) -> Iterator[tuple]:
    """The base rule of every node in a subtree, in preorder."""
    yield template(node)[0]
    for _f, _i, c in _children(node):
        yield from base_templates(c)


def _fill(t, marker: tuple, kids: Iterator):
    """Replace each `marker` in template `t`, in order, by the next shape from `kids`."""
    if t == marker:
        return next(kids)
    if type(t) is tuple:
        return tuple(_fill(x, marker, kids) for x in t)
    return t


class Rule:
    """One grammar rule: a base rule (one node) or a library block (a fragment with holes)."""

    __slots__ = ("block_size", "child_ctxs", "idx", "is_block", "kind", "kpos", "marker", "nslots",
                 "slot_fields", "template", "type")

    def __init__(self, idx: int, tpl: tuple, marker: tuple, type_name: str, child_ctxs: tuple,
                 slot_fields: tuple, is_block: bool, block_size: int):
        self.idx = idx
        self.template = tpl
        self.marker = marker
        self.type = type_name
        self.kind = kind_of(type_name)
        self.child_ctxs = child_ctxs
        self.slot_fields = slot_fields
        self.nslots = len(child_ctxs)
        self.is_block = is_block
        self.block_size = block_size
        self.kpos = -1

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Rule({'block' if self.is_block else 'base'} {self.type} #{self.idx})"


# ---------------------------------------------------------------- library blocks

@dataclass(frozen=True)
class LibBlock:
    """An EXP-005 building block, with the context of each of its holes."""

    key: tuple
    size: int
    root_type: str
    hole_ctxs: tuple


def _hole_contexts(node: ast.AST, holes: frozenset, out: list) -> None:
    for f, _i, c in _children(node):
        if id(c) in holes:
            out.append((type(node).__name__, f))
        else:
            _hole_contexts(c, holes, out)


def library_blocks(library: Sequence[Block], corpus: Corpus) -> list[LibBlock]:
    """EXP-005 blocks (from `learn` or `random_library` on `corpus`), ready for a grammar."""
    out = []
    for b in library:
        s, nholes, nd, holes = corpus.meta[b.key]
        ctxs: list = []
        _hole_contexts(nd, holes, ctxs)
        if not len(ctxs) == nholes == b.holes:
            raise AssertionError(f"hole count mismatch in {b.example}")
        out.append(LibBlock(b.key, s, type(nd).__name__, tuple(ctxs)))
    return out


def _match_holes(p, node: ast.AST, covered: list[int], holes: list[ast.AST]) -> bool:
    """codeblocks._match, also collecting the nodes that fill the holes (in order)."""
    if p == HOLE:
        if isinstance(node, ast.expr):
            holes.append(node)
            return True
        return False
    if not isinstance(p, tuple) or p[0] != type(node).__name__:
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
                    if not _match_holes(pv, v, covered, holes):
                        return False
                elif v != pv:
                    return False
        elif isinstance(value, ast.AST):
            if not _match_holes(pval, value, covered, holes):
                return False
        elif value != pval:
            return False
    return True


def rewrite_plan(tree: ast.AST, blocks: Sequence[Rule]) -> dict[int, tuple[Rule, list[ast.AST]]]:
    """Where each block is used, exactly as EXP-005's rewrite_size decides it:
    blocks in library order, roots in ast.walk order, no overlaps.
    Returns {id(root node): (block, nodes filling its holes)}."""
    used: set[int] = set()
    plan: dict[int, tuple[Rule, list[ast.AST]]] = {}
    nodes = [nd for nd in ast.walk(tree) if isinstance(nd, (ast.stmt, ast.expr))]
    for b in blocks:
        for nd in nodes:
            if id(nd) in used:
                continue
            cov: list[int] = []
            hs: list[ast.AST] = []
            if _match_holes(b.template, nd, cov, hs) and not (set(cov) & used):
                used.update(cov)
                plan[id(nd)] = (b, hs)
    return plan


def plan_size(tree: ast.AST, plan: dict) -> int:
    """Size after rewriting with `plan` (each block use counts as one node)."""
    return size(tree) - sum(b.block_size - 1 for b, _h in plan.values())


# ---------------------------------------------------------------- candidate lists

class Cands:
    """The rules for one context, in order of increasing key (cost + completion bound),
    produced lazily and remembered."""

    __slots__ = ("_more", "items")

    def __init__(self, more: Iterator[tuple[float, float, Rule]]):
        self.items: list[tuple[float, float, Rule]] = []
        self._more = more

    def get(self, i: int) -> tuple[float, float, Rule] | None:
        items = self.items
        while len(items) <= i:
            nxt = next(self._more, None)
            if nxt is None:
                return None
            items.append(nxt)
        return items[i]


def _merge(explicit: list, backoff: list, shift: float) -> Iterator[tuple[float, float, Rule]]:
    """Merge the context's own rules (sorted) with the shared backoff list (sorted,
    shifted by a constant), skipping rules already listed with their own count."""
    skip = {e[2] for e in explicit}
    i = j = 0
    ne, nb = len(explicit), len(backoff)
    while True:
        while j < nb and backoff[j][2] in skip:
            j += 1
        if i < ne and (j >= nb or explicit[i][0] <= backoff[j][0] + shift):
            yield explicit[i]
            i += 1
        elif j < nb:
            k, c, r = backoff[j]
            yield (k + shift, c + shift, r)
            j += 1
        else:
            return


def _by_key(entries) -> list:
    return sorted(entries, key=lambda e: (e[0], e[2].idx))


# ---------------------------------------------------------------- the one-level grammar (with or without a library)

class Grammar:
    """P(r | c) = (n(r, c) + alpha * P0(r | kind(c))) / (n(c) + alpha), with c = (parent type, field).

    The base rules are those seen in the past code. With `blocks`, each past
    function is first rewritten with them exactly as EXP-005 rewrites code; a
    block use counts once in the context of its root and the nodes it covers
    count nothing. Every rule (base or block) gets one extra count in the
    backoff P0, so nothing in the inventory is unreachable."""

    def __init__(self, past: Sequence[ast.AST], blocks: Sequence[LibBlock] = (), alpha: float = ALPHA):
        self.alpha = alpha
        self.rules: list[Rule] = []
        self.base: dict[tuple, Rule] = {}
        kinds: dict[tuple, Counter] = defaultdict(Counter)
        for tree in past:
            self._inventory(tree, ROOT_CTX, kinds)
        self.blocks = [self._add(b.key, HOLE, b.root_type, b.hole_ctxs, (), True, b.size) for b in blocks]
        self.ctx_kind: dict[tuple, str] = {c: k.most_common(1)[0][0] for c, k in kinds.items()}
        for b in self.blocks:
            for c in b.child_ctxs:
                self.ctx_kind.setdefault(c, "expr")          # a hole always holds an expression
        self.by_kind: dict[str, list[Rule]] = defaultdict(list)
        for r in self.rules:
            r.kpos = len(self.by_kind[r.kind])
            self.by_kind[r.kind].append(r)

        n_rc: Counter = Counter()
        for tree in past:
            self._count(tree, ROOT_CTX, rewrite_plan(tree, self.blocks) if self.blocks else {}, n_rc)
        n_r: Counter = Counter()
        self.n_c: Counter = Counter()
        explicit: dict[tuple, list] = defaultdict(list)
        for (r, c), n in n_rc.items():
            n_r[r] += n
            self.n_c[c] += n
            explicit[c].append((r, n))
        n0 = [n_r[r] + 1 for r in self.rules]
        total0: Counter = Counter()
        for r in self.rules:
            total0[r.kind] += n0[r.idx]
        self.p0 = [n0[r.idx] / total0[r.kind] for r in self.rules]
        self.cost0 = [-math.log2(p) for p in self.p0]
        self.ecost: dict[tuple, list[tuple[Rule, float]]] = {
            c: [(r, -math.log2((n + alpha * self.p0[r.idx]) / (self.n_c[c] + alpha))) for r, n in explicit[c]]
            for c in self.ctx_kind}
        self._fixed_point()
        self.kids = [(tuple((c, self.h[c]) for c in r.child_ctxs), self.S[r.idx]) for r in self.rules]
        self.backoff = {k: _by_key((self.cost0[r.idx] + self.S[r.idx], self.cost0[r.idx], r) for r in rs)
                        for k, rs in self.by_kind.items()}
        self._cands: dict[tuple, Cands] = {}

    # -- building
    def _add(self, tpl, marker, type_name, child_ctxs, slot_fields, is_block, block_size) -> Rule:
        r = Rule(len(self.rules), tpl, marker, type_name, tuple(child_ctxs), tuple(slot_fields), is_block,
                 block_size)
        self.rules.append(r)
        return r

    def _base_rule(self, node: ast.AST) -> Rule:
        tpl, fields = template(node)
        r = self.base.get(tpl)
        if r is None:
            t = type(node).__name__
            r = self.base[tpl] = self._add(tpl, SLOT, t, [(t, f) for f in fields], fields, False, 1)
        return r

    def _inventory(self, node: ast.AST, ctx: tuple, kinds: dict) -> None:
        r = self._base_rule(node)
        kinds[ctx][r.kind] += 1
        for f, _i, c in _children(node):
            self._inventory(c, (r.type, f), kinds)

    def _count(self, node: ast.AST, ctx: tuple, plan: dict, n_rc: Counter) -> None:
        use = plan.get(id(node))
        if use is not None:
            b, holes = use
            n_rc[(b, ctx)] += 1
            for h, hc in zip(holes, b.child_ctxs, strict=True):
                self._count(h, hc, plan, n_rc)
            return
        r = self.base[template(node)[0]]
        n_rc[(r, ctx)] += 1
        for f, _i, c in _children(node):
            self._count(c, (r.type, f), plan, n_rc)

    def _fixed_point(self) -> None:
        """h(c) = the cheapest complete subtree for context c, in bits (exact, by iteration from infinity)."""
        a = self.alpha
        h = dict.fromkeys(self.ctx_kind, INF)
        m = dict.fromkeys(self.by_kind, INF)
        for _ in range(MAX_ROUNDS):
            s = [sum(h[c] for c in r.child_ctxs) for r in self.rules]
            new_m = {k: min(self.cost0[r.idx] + s[r.idx] for r in rs) for k, rs in self.by_kind.items()}
            new_h = {}
            for c, k in self.ctx_kind.items():
                best = math.log2((self.n_c[c] + a) / a) + new_m[k]
                for r, cost in self.ecost[c]:
                    best = min(best, cost + s[r.idx])
                new_h[c] = best
            if new_h == h and new_m == m:
                break
            h, m = new_h, new_m
        else:  # pragma: no cover - costs are positive, so this always converges
            raise RuntimeError("completion bounds did not converge")
        self.h, self.M, self.S = h, m, s

    # -- the interface the search uses
    def prepare(self, ctx: tuple, kind: str) -> float:
        """Make a (possibly never-seen) root context usable; return its completion bound."""
        if ctx not in self.ctx_kind:
            self.ctx_kind[ctx] = kind
            self.h[ctx] = self.M[kind]                 # n(c) = 0: pure backoff
            self.ecost[ctx] = []
        elif self.ctx_kind[ctx] != kind:
            raise ValueError(f"context {ctx} holds {self.ctx_kind[ctx]}, not {kind}")
        return self.h[ctx]

    def cands(self, ctx: tuple) -> Cands:
        cl = self._cands.get(ctx)
        if cl is None:
            ex = _by_key((cost + self.S[r.idx], cost, r) for r, cost in self.ecost[ctx])
            shift = math.log2((self.n_c[ctx] + self.alpha) / self.alpha)
            cl = self._cands[ctx] = Cands(_merge(ex, self.backoff[self.ctx_kind[ctx]], shift))
        return cl

    def child_slots(self, ctx: tuple, r: Rule) -> tuple[tuple, float]:
        return self.kids[r.idx]

    def derivable(self, node: ast.AST) -> bool:
        """Can this grammar produce the subtree at all (is every base rule in it seen in the past)?"""
        return all(t in self.base for t in base_templates(node))


# ---------------------------------------------------------------- the two-level grammar (sharper habits, no blocks)

class Grammar2:
    """Condition CTX2. Context c2 = (grandparent type, its field, parent type, field);
    P2(r | c2) = (n(r, c2) + alpha * P(r | c)) / (n(c2) + alpha), backing off to the
    one-level grammar `g1` (which must have no blocks), with c = the last two parts of c2."""

    def __init__(self, g1: Grammar, past: Sequence[ast.AST], alpha: float = ALPHA):
        if g1.blocks:
            raise ValueError("CTX2 backs off to the grammar without blocks")
        self.g1, self.alpha = g1, alpha
        n2: Counter = Counter()
        for tree in past:
            self._count(tree, ROOT_CTX2, n2)
        self.n2c: Counter = Counter()
        explicit: dict[tuple, list] = defaultdict(list)
        for (r, c2), n in n2.items():
            self.n2c[c2] += n
            explicit[c2].append((r, n))
        self.cost1: dict[tuple, list[float]] = {}
        self.kids2: dict[tuple, list[tuple]] = {}
        for c in list(g1.ctx_kind):
            self._one_level(c)
        self.e2 = {c2: [(r, -math.log2((n + alpha * 2.0 ** -self.cost1[c2[2:]][r.kpos]) / (self.n2c[c2] + alpha)))
                        for r, n in rs] for c2, rs in explicit.items()}
        self._fixed_point()
        self._backoff: dict[tuple, list] = {}
        self._cands: dict[tuple, Cands] = {}
        self._slots: dict[tuple, tuple[tuple, float]] = {}

    def _count(self, node: ast.AST, c2: tuple, n2: Counter) -> None:
        r = self.g1.base[template(node)[0]]
        n2[(r, c2)] += 1
        for f, _i, c in _children(node):
            self._count(c, (c2[2], c2[3], r.type, f), n2)

    def _one_level(self, c: tuple) -> None:
        g1 = self.g1
        rs = g1.by_kind[g1.ctx_kind[c]]
        shift = math.log2((g1.n_c[c] + g1.alpha) / g1.alpha)
        cost = [shift + g1.cost0[r.idx] for r in rs]
        for r, ec in g1.ecost[c]:
            cost[r.kpos] = ec
        self.cost1[c] = cost
        self.kids2[c] = [tuple((c[0], c[1], r.type, f) for f in r.slot_fields) for r in rs]

    def _get(self, c2: tuple) -> float:
        v = self.h2.get(c2)
        return v if v is not None else self.M2[c2[2:]]

    def _fixed_point(self) -> None:
        a = self.alpha
        self.h2 = dict.fromkeys(self.n2c, INF)
        self.M2 = dict.fromkeys(self.cost1, INF)
        for _ in range(MAX_ROUNDS):
            s2 = {c: [sum(self._get(k) for k in ks) for ks in kk] for c, kk in self.kids2.items()}
            new_m = {c: min(x + y for x, y in zip(self.cost1[c], s2[c], strict=True)) for c in self.cost1}
            new_h = {}
            for c2 in self.h2:
                c = c2[2:]
                best = math.log2((self.n2c[c2] + a) / a) + new_m[c]
                for r, cost in self.e2[c2]:
                    best = min(best, cost + s2[c][r.kpos])
                new_h[c2] = best
            if new_h == self.h2 and new_m == self.M2:
                break
            self.h2, self.M2 = new_h, new_m
        else:  # pragma: no cover
            raise RuntimeError("completion bounds did not converge")
        self.S2 = s2

    def prepare(self, c2: tuple, kind: str) -> float:
        c = c2[2:]
        if c not in self.cost1:                       # a one-level context never seen in the past
            self.g1.prepare(c, kind)
            self._one_level(c)
            self.S2[c] = [sum(self._get(k) for k in ks) for ks in self.kids2[c]]
            self.M2[c] = min(x + y for x, y in zip(self.cost1[c], self.S2[c], strict=True))
        elif self.g1.ctx_kind[c] != kind:
            raise ValueError(f"context {c} holds {self.g1.ctx_kind[c]}, not {kind}")
        return self._get(c2)

    def cands(self, c2: tuple) -> Cands:
        cl = self._cands.get(c2)
        if cl is None:
            c = c2[2:]
            bo = self._backoff.get(c)
            if bo is None:
                rs = self.g1.by_kind[self.g1.ctx_kind[c]]
                bo = self._backoff[c] = _by_key((x + y, x, r) for x, y, r in
                                                zip(self.cost1[c], self.S2[c], rs, strict=True))
            ex = _by_key((cost + self.S2[c][r.kpos], cost, r) for r, cost in self.e2.get(c2, ()))
            shift = math.log2((self.n2c[c2] + self.alpha) / self.alpha)
            cl = self._cands[c2] = Cands(_merge(ex, bo, shift))
        return cl

    def child_slots(self, c2: tuple, r: Rule) -> tuple[tuple, float]:
        key = (c2[2], c2[3], r.idx)
        v = self._slots.get(key)
        if v is None:
            kids = tuple((k, self._get(k)) for k in self.kids2[c2[2:]][r.kpos])
            v = self._slots[key] = (kids, sum(h for _k, h in kids))
        return v

    def derivable(self, node: ast.AST) -> bool:
        return self.g1.derivable(node)


# ---------------------------------------------------------------- search

def complete_trees(g: Grammar | Grammar2, root_ctx: tuple, root_kind: str,
                   budget: int) -> Iterator[tuple[int, float, tuple]]:
    """Best-first search from `root_ctx`. Yields every complete tree it takes from the
    queue, in order: (effort so far, cost in bits, derivation). Stops after `budget` states.

    A state is a partial tree: its cost so far g, the bounds of its open slots, the
    rules used (a linked list, newest first) and the open slots (leftmost first). A
    queue entry is "state, expanded with the i-th candidate at its leftmost slot";
    the (i+1)-th sibling is queued only when the i-th is taken, so no queue entry is
    built that the search never needs."""
    hr = g.prepare(root_ctx, root_kind)
    cl = g.cands(root_ctx)
    first = cl.get(0)
    if first is None:
        return
    heap = [(first[0], 0, (0.0, hr, None, (root_ctx, hr, None)), cl, 0)]
    push, pop = heapq.heappush, heapq.heappop
    seq = effort = 0
    while heap and effort < budget:
        _f, _s, st, cl, i = pop(heap)
        effort += 1
        _key, cost, r = cl.items[i]
        g0, hs, dv, (ctx, hc, rest) = st
        nxt = cl.get(i + 1)
        if nxt is not None:
            seq += 1
            push(heap, (g0 + hs - hc + nxt[0], seq, st, cl, i + 1))
        kids, ksum = g.child_slots(ctx, r)
        o = rest
        for kc, kh in reversed(kids):
            o = (kc, kh, o)
        ng, nd = g0 + cost, (r, dv)
        if o is None:
            yield effort, ng, nd
            continue
        nh = hs - hc + ksum
        cl1 = g.cands(o[0])
        fst = cl1.get(0)
        if fst is not None:
            seq += 1
            push(heap, (ng + nh - o[1] + fst[0], seq, (ng, nh, nd, o), cl1, 0))


def rules_used(dv: tuple | None) -> list[Rule]:
    """The rules of a derivation, in preorder."""
    out = []
    while dv is not None:
        out.append(dv[0])
        dv = dv[1]
    out.reverse()
    return out


def assemble(dv: tuple | None) -> tuple:
    """The EXP-005 shape of the tree a complete derivation builds."""
    it = iter(rules_used(dv))

    def build() -> tuple:
        r = next(it)
        kids = [build() for _ in range(r.nslots)]
        return _fill(r.template, r.marker, iter(kids))
    return build()


def _same(t, marker: tuple, s, it: Iterator[Rule]) -> bool:
    """Does template `t`, with its markers filled from the derivation `it`, equal shape `s`?
    Stops at the first difference instead of building the whole tree."""
    if t == marker:
        return builds(it, s)
    if type(t) is tuple:
        if type(s) is not tuple or len(s) != len(t):
            return False
        for x, y in zip(t, s, strict=True):  # noqa: SIM110  (a plain loop: this is the hot path)
            if not _same(x, marker, y, it):
                return False
        return True
    return t == s


def builds(it: Iterator[Rule], s: tuple) -> bool:
    """Does the derivation (rules in preorder) build exactly shape `s`? Same answer as
    assemble(...) == s, without building anything."""
    r = next(it)
    return _same(r.template, r.marker, s, it)


def search(g: Grammar | Grammar2, root_ctx: tuple, root_kind: str, target: tuple,
           budget: int) -> tuple[int | None, bool]:
    """(effort at which `target` is produced, or None within `budget`; whether its route used a block)."""
    top = target[0]
    for effort, _cost, dv in complete_trees(g, root_ctx, root_kind, budget):
        rules = rules_used(dv)
        if rules[0].template[0] == top and builds(iter(rules), target):
            return effort, any(r.is_block for r in rules)
    return None, False


# ---------------------------------------------------------------- tasks

@dataclass(frozen=True)
class Task:
    """One hidden piece of a future function: where it sits and what it is."""

    path: str
    function: str
    size: int
    ctx: tuple
    ctx2: tuple
    kind: str
    target: tuple
    derivable: bool


def positions(tree: ast.AST) -> dict[int, tuple[tuple, tuple]]:
    """id(node) -> (one-level context, two-level context), for every statement and expression."""
    out: dict[int, tuple[tuple, tuple]] = {}

    def walk(n: ast.AST, ctx: tuple, c2: tuple) -> None:
        if isinstance(n, (ast.stmt, ast.expr)):
            out[id(n)] = (ctx, c2)
        t = type(n).__name__
        for f, _i, c in _children(n):
            walk(c, (t, f), (ctx[0], ctx[1], t, f))
    walk(tree, ROOT_CTX, ROOT_CTX2)
    return out


def sample_tasks(future: dict[tuple[str, str], ast.AST], inventory: set | dict, max_size: int = 12,
                 per_function: int = 8, seed: int = 0) -> list[Task]:
    """The registered sampling rule (design, section 4.3): for each future function in
    sorted (path, name) order, up to `per_function` of its statements and expressions of
    size MIN_SIZE..max_size (not the function itself), drawn uniformly from them in
    ast.walk order with one random.Random(seed)."""
    rng = random.Random(seed)
    tasks = []
    for path, qual in sorted(future):
        tree = future[(path, qual)]
        pos = positions(tree)
        eligible = [n for n in ast.walk(tree)
                    if n is not tree and isinstance(n, (ast.stmt, ast.expr)) and MIN_SIZE <= size(n) <= max_size]
        for n in rng.sample(eligible, min(per_function, len(eligible))):
            ctx, c2 = pos[id(n)]
            tasks.append(Task(path, qual, size(n), ctx, c2, kind_of(type(n).__name__), shape(n),
                              all(t in inventory for t in base_templates(n))))
    return tasks

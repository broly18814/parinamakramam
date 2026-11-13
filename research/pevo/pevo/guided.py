"""EXP-007, guidance level G3: a grammar for one task, tilted towards a language model's guesses
(docs/research/EXP-007-build-spec.md, S3).

Plain picture: before the search starts on one hidden piece, the model makes 16 guesses. Where the
guesses agree, the search should try those shapes first. So in every place a guess passes
through, each choice's probability becomes a blend: lam x how often the guesses made it, plus
(1 - lam) x what the ordinary grammar says. Everywhere else nothing changes.

For specialists:
- P(r | c2) = lam * n_s(r, c2) / n_s(c2) + (1 - lam) * P_base(r | c2) in every two-level context the
  samples reach; P = P_base elsewhere.
- P_base is a Grammar2, with blocks under L1/L2 (S5). A base rule the past never had, but a sample
  used, exists only here, with probability from the samples' part alone.
- The completion bounds are then recomputed for the whole task grammar by exactly EXP-006's
  method (iteration from infinity to the exact fixed point), so the search's order and its effort
  measure mean the same as in every other condition. With no samples, every number is the base
  grammar's, which a self-check confirms on real tasks.

Nothing here runs any code.
"""
from __future__ import annotations

import ast
import math
from collections import Counter, defaultdict
from collections.abc import Sequence

from pevo.codeblocks import _children
from pevo.grammarsearch import (
    INF,
    MAX_ROUNDS,
    SLOT,
    Cands,
    Grammar2,
    Rule,
    _by_key,
    _merge,
    base_templates,
    kind_of,
    rewrite_plan,
    template,
)


class TaskGrammar:
    """The G3 grammar for one task: `base` blended with the rules of `pieces` (S3)."""

    def __init__(self, base: Grammar2, root_ctx: tuple, root_kind: str, pieces: Sequence[ast.AST], lam: float):
        if not 0.0 <= lam < 1.0:
            raise ValueError("lam must be in [0, 1)")
        self.base, self.g1, self.lam, self.alpha = base, base.g1, lam, base.alpha
        base.prepare(root_ctx, root_kind)
        self.new: dict[tuple, Rule] = {}                     # base rules only the samples used
        self.ns: dict[tuple, Counter] = defaultdict(Counter)  # c2 -> rule -> count in samples
        self.pieces_used = 0
        for p in pieces:
            counts: dict[tuple, Counter] = defaultdict(Counter)
            try:
                plan = rewrite_plan(p, self.g1.blocks) if self.g1.blocks else {}
                self._count(p, root_ctx, plan, counts)
            except ValueError:   # a guess that puts a node where the grammar says another kind goes
                continue
            self.pieces_used += 1
            for c2, rs in counts.items():
                self.ns[c2].update(rs)
        self._mix: dict[tuple, list[tuple[Rule, float]]] = {c2: self._mixture(c2) for c2 in self.ns} if lam else {}
        self._fixed_point()
        self._cands: dict[tuple, Cands] = {}
        self._backoff: dict[tuple, list] = {}
        self._slots: dict[tuple, tuple[tuple, float]] = {}

    # -- counting the samples' rules, in two-level contexts (as Grammar2 counts the past)
    def _rule(self, node: ast.AST) -> Rule:
        tpl, fields = template(node)
        r = self.g1.base.get(tpl) or self.new.get(tpl)
        if r is None:
            t = type(node).__name__
            r = Rule(len(self.g1.rules) + len(self.new), tpl, SLOT, t, tuple((t, f) for f in fields),
                     tuple(fields), False, 1)
            self.new[tpl] = r
        return r

    def _count(self, node: ast.AST, c2: tuple, plan: dict, counts: dict) -> None:
        use = plan.get(id(node))
        if use is not None:
            b, holes = use
            counts[c2][b] += 1
            for h, (t, f) in zip(holes, b.child_ctxs, strict=True):
                kc = (c2[2], c2[3], t, f)
                self.base.prepare(kc, kind_of(type(h).__name__))
                self._count(h, kc, plan, counts)
            return
        r = self._rule(node)
        counts[c2][r] += 1
        for f, _i, child in _children(node):
            kc = (c2[2], c2[3], r.type, f)
            self.base.prepare(kc, kind_of(type(child).__name__))
            self._count(child, kc, plan, counts)

    # -- the blended distribution in one sampled context
    def _base_cost(self, c2: tuple, r: Rule, explicit: dict) -> float:
        if r.kpos < 0:
            return INF                                        # a rule the past never had
        if r in explicit:
            return explicit[r]
        shift = math.log2((self.base.n2c[c2] + self.alpha) / self.alpha)
        return self.base.cost1[c2[2:]][r.kpos] + shift

    def _mixture(self, c2: tuple) -> list[tuple[Rule, float]]:
        c = c2[2:]
        rs = list(self.g1.by_kind[self.g1.ctx_kind[c]])
        counts = self.ns[c2]
        rs += [r for r in counts if r.kpos < 0]
        n = sum(counts.values())
        explicit = dict(self.base.e2.get(c2, ()))
        out = []
        for r in rs:
            b = self._base_cost(c2, r, explicit)
            p = self.lam * counts.get(r, 0) / n + (1 - self.lam) * (2.0 ** -b if b < INF else 0.0)
            if p > 0:
                out.append((r, -math.log2(p)))
        return out

    def _kids(self, c2: tuple, r: Rule) -> tuple:
        if r.kpos >= 0:
            return self.base.kids2[c2[2:]][r.kpos]
        return tuple((c2[2], c2[3], t, f) for t, f in r.child_ctxs)

    # -- completion bounds: EXP-006's fixed point, over the task grammar
    def _get(self, c2: tuple) -> float:
        v = self.h2.get(c2)
        return v if v is not None else self.M2[c2[2:]]

    def _fixed_point(self) -> None:
        b, a = self.base, self.alpha
        self.h2 = dict.fromkeys(set(b.n2c) | set(self._mix), INF)
        self.M2 = dict.fromkeys(b.cost1, INF)
        for _ in range(MAX_ROUNDS):
            s2 = {c: [sum(self._get(k) for k in ks) for ks in kk] for c, kk in b.kids2.items()}
            new_m = {c: min(x + y for x, y in zip(b.cost1[c], s2[c], strict=True)) for c in b.cost1}
            new_h = {}
            for c2 in self.h2:
                c = c2[2:]
                mix = self._mix.get(c2)
                if mix is not None:
                    best = INF
                    for r, cost in mix:
                        kid = s2[c][r.kpos] if r.kpos >= 0 else sum(self._get(k) for k in self._kids(c2, r))
                        best = min(best, cost + kid)
                else:
                    best = math.log2((b.n2c[c2] + a) / a) + new_m[c]
                    for r, cost in b.e2.get(c2, ()):
                        best = min(best, cost + s2[c][r.kpos])
                new_h[c2] = best
            if new_h == self.h2 and new_m == self.M2:
                break
            self.h2, self.M2 = new_h, new_m
        else:  # pragma: no cover - costs are positive, so this always converges
            raise RuntimeError("completion bounds did not converge")
        self.S2 = s2

    # -- the interface the search uses (as Grammar2)
    def prepare(self, c2: tuple, kind: str) -> float:
        return self._get(c2)

    def cands(self, c2: tuple) -> Cands:
        cl = self._cands.get(c2)
        if cl is not None:
            return cl
        c = c2[2:]
        mix = self._mix.get(c2)
        if mix is not None:
            entries = []
            for r, cost in mix:
                kid = self.S2[c][r.kpos] if r.kpos >= 0 else sum(self._get(k) for k in self._kids(c2, r))
                entries.append((cost + kid, cost, r))
            cl = Cands(iter(_by_key(entries)))
        else:
            bo = self._backoff.get(c)
            if bo is None:
                rs = self.g1.by_kind[self.g1.ctx_kind[c]]
                bo = self._backoff[c] = _by_key((x + y, x, r) for x, y, r in
                                                zip(self.base.cost1[c], self.S2[c], rs, strict=True))
            ex = _by_key((cost + self.S2[c][r.kpos], cost, r) for r, cost in self.base.e2.get(c2, ()))
            shift = math.log2((self.base.n2c[c2] + self.alpha) / self.alpha)
            cl = Cands(_merge(ex, bo, shift))
        self._cands[c2] = cl
        return cl

    def child_slots(self, c2: tuple, r: Rule) -> tuple[tuple, float]:
        key = (c2[2], c2[3], r.idx)
        v = self._slots.get(key)
        if v is None:
            kids = tuple((k, self._get(k)) for k in self._kids(c2, r))
            v = self._slots[key] = (kids, sum(h for _k, h in kids))
        return v

    def derivable(self, node: ast.AST) -> bool:
        return all(t in self.g1.base or t in self.new for t in base_templates(node))

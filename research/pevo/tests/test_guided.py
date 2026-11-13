"""Self-checks for EXP-007's model-guided grammar, G3 (docs/research/EXP-007-build-spec.md, S3, S8)."""

from __future__ import annotations

import ast

import pytest
from pevo.codeblocks import build_corpus, functions, learn, shape
from pevo.grammarsearch import Grammar, Grammar2, library_blocks, positions, search
from pevo.guided import TaskGrammar

PAST = '''
def a(xs, out):
    for x in xs:
        if x is not None:
            out.append(x + 1)
    return out


def b(items, acc):
    for it in items:
        if it is not None:
            acc.append(it + 1)
    return acc


def c(rows, seen):
    total = 0
    for r in rows:
        total = total + len(r)
    return total
'''
FUTURE = '''
def d(cols, keep):
    for k in cols:
        if k is not None:
            keep.append(k + 1)
    return sorted(keep)
'''


def past_trees():
    return [t for _q, t in functions(PAST)]


def future_fn():
    return next(t for _q, t in functions(FUTURE))


def where(node, fn):
    _ctx, c2 = positions(fn)[id(node)]
    return c2


def total_probability(g, c2) -> float:
    cl, i, total = g.cands(c2), 0, 0.0
    while (e := cl.get(i)) is not None:
        total += 2.0 ** -e[1]
        i += 1
    return total


def test_with_no_guesses_the_search_is_the_base_grammars_exactly():
    past = past_trees()
    fn = future_fn()
    for node in [n for n in ast.walk(fn) if isinstance(n, (ast.stmt, ast.expr)) and n is not fn]:
        kind = "stmt" if isinstance(node, ast.stmt) else "expr"
        c2 = where(node, fn)
        base = Grammar2(Grammar(past), past)
        g = TaskGrammar(base, c2, kind, [], lam=0.5)
        assert search(g, c2, kind, shape(node), 5_000) == search(base, c2, kind, shape(node), 5_000)


def test_every_sampled_context_is_a_proper_distribution():
    past = past_trees()
    fn = future_fn()
    node = fn.body[0].body[0]                              # the `if ...: keep.append(k + 1)`
    c2 = where(node, fn)
    g = TaskGrammar(Grammar2(Grammar(past), past), c2, "stmt", [node, node, fn.body[1]], lam=0.5)
    assert g.ns, "the guesses should reach some contexts"
    for ctx in g.ns:
        assert total_probability(g, ctx) == pytest.approx(1.0, abs=1e-9), ctx


def test_correct_guesses_make_the_piece_cheaper_to_find():
    """The whole `for` loop: the plain grammar needs 22 steps; with the true piece guessed, the
    search goes straight to it (16 steps, one per rule, the minimum possible)."""
    past = past_trees()
    fn = future_fn()
    node = fn.body[0]
    c2 = where(node, fn)
    before, _ = search(Grammar2(Grammar(past), past), c2, "stmt", shape(node), 50_000)
    g = TaskGrammar(Grammar2(Grammar(past), past), c2, "stmt", [node] * 4, lam=0.5)
    after, _ = search(g, c2, "stmt", shape(node), 50_000)
    assert after is not None and (before is None or after < before)


def test_a_guess_can_bring_in_a_rule_the_past_never_had():
    """`sorted` never appears in the past, so the base grammar can't build `return sorted(keep)`."""
    past = past_trees()
    fn = future_fn()
    node = fn.body[1]
    c2 = where(node, fn)
    base = Grammar2(Grammar(past), past)
    assert not base.derivable(node)
    g = TaskGrammar(base, c2, "stmt", [node], lam=0.5)
    assert g.derivable(node) and g.new
    effort, _ = search(g, c2, "stmt", shape(node), 50_000)
    assert effort is not None


def test_guesses_are_rewritten_with_blocks_under_a_library():
    past = past_trees()
    corpus = build_corpus(past, 40)
    blocks = library_blocks(learn(corpus, 5), corpus)
    fn = future_fn()
    node = fn.body[0]                                      # the whole `for` loop
    c2 = where(node, fn)
    g = TaskGrammar(Grammar2(Grammar(past, blocks), past), c2, "stmt", [node] * 2, lam=0.5)
    assert any(r.is_block for rs in g.ns.values() for r in rs)
    for ctx in g.ns:
        assert total_probability(g, ctx) == pytest.approx(1.0, abs=1e-9)


def test_lam_must_leave_room_for_the_base_grammar():
    past = past_trees()
    with pytest.raises(ValueError):
        TaskGrammar(Grammar2(Grammar(past), past), ("ROOT", "", "ROOT", ""), "stmt", [], lam=1.0)

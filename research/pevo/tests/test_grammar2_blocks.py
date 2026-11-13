"""Self-checks for EXP-007's two-level grammar with blocks (docs/research/EXP-007-build-spec.md, S5, S8)."""

from __future__ import annotations

import ast

import pytest
from pevo.codeblocks import build_corpus, functions, learn, shape
from pevo.grammarsearch import (
    Grammar,
    Grammar2,
    assemble,
    complete_trees,
    library_blocks,
    positions,
    rules_used,
    search,
)

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
    for r in rows:
        if r is not None:
            seen.append(r * 2)
    return len(seen)
'''
FUTURE = '''
def d(cols, keep):
    for k in cols:
        if k is not None:
            keep.append(k + 1)
    return keep
'''


def setup():
    past = [t for _q, t in functions(PAST)]
    corpus = build_corpus(past, 40)
    blocks = library_blocks(learn(corpus, 5), corpus)
    return past, blocks


def total_probability(g: Grammar2, c2: tuple) -> float:
    cl, i, total = g.cands(c2), 0, 0.0
    while (e := cl.get(i)) is not None:
        total += 2.0 ** -e[1]
        i += 1
    return total


@pytest.mark.parametrize("with_blocks", [False, True])
def test_every_context_is_a_proper_distribution(with_blocks):
    past, blocks = setup()
    g = Grammar2(Grammar(past, blocks if with_blocks else ()), past)
    assert g.n2c, "the past should give two-level contexts"
    for c2 in g.n2c:
        assert total_probability(g, c2) == pytest.approx(1.0, abs=1e-9), c2


def test_blocks_are_counted_in_two_level_contexts_and_used_by_the_search():
    past, blocks = setup()
    assert blocks, "the repeated pattern should be learned as a block"
    g = Grammar2(Grammar(past, blocks), past)
    assert any(r.is_block for (r, _c2) in _counts(g))
    fn = next(t for _q, t in functions(FUTURE))
    node = fn.body[0].body[0]                         # the whole `if ...: keep.append(k + 1)`
    _ctx, c2 = positions(fn)[id(node)]
    effort, _used = search(g, c2, "stmt", shape(node), 50_000)
    assert effort is not None                         # the grammar with blocks still finds it
    # Routes through blocks exist from this context, and build well-formed code: that exercises
    # the holes' two-level contexts (S5). Which route is likeliest isn't the point here.
    with_block = [dv for _e, _cost, dv in complete_trees(g, c2, "stmt", 20_000)
                  if any(r.is_block for r in rules_used(dv))]
    assert with_block
    for dv in with_block[:50]:
        assemble(dv)                                   # raises if a hole's slot were miswired


def test_without_blocks_it_is_exp006s_grammar_exactly():
    """Same counts and same candidate order as a grammar built with no blocks at all."""
    past, _blocks = setup()
    g_plain = Grammar2(Grammar(past), past)
    g_empty = Grammar2(Grammar(past, ()), past)
    assert g_plain.n2c == g_empty.n2c
    for c2 in g_plain.n2c:
        a, b = g_plain.cands(c2), g_empty.cands(c2)
        i = 0
        while (x := a.get(i)) is not None:
            y = b.get(i)
            assert y is not None and (x[0], x[1], x[2].template) == (y[0], y[1], y[2].template)
            i += 1


def test_a_block_whose_holes_are_not_direct_children_is_refused():
    past, blocks = setup()
    g1 = Grammar(past, blocks)
    g1.blocks[0].child_ctxs = (("NotTheRoot", "value"),)
    with pytest.raises(ValueError):
        Grammar2(g1, past)


def _counts(g: Grammar2):
    """(rule, c2) pairs the two-level grammar counted explicitly."""
    return [(r, c2) for c2, rs in g.e2.items() for r, _cost in rs]


def test_the_fixture_really_repeats_a_pattern():
    assert ast.dump(ast.parse(PAST)).count("Compare") >= 3

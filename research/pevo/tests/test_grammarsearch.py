"""Self-checks for EXP-006's grammar and search (pevo/grammarsearch.py).

What must hold for the measurement to mean anything:
- the grammar can rebuild every piece of code exactly (no shape is lost);
- a library is applied to past code exactly as EXP-005 applies it;
- every context's probabilities add up to one, so no condition gets free probability;
- the completion bound is exact, so finished trees come out most likely first;
- the effort the search reports is the tree's position in that order.
"""
from __future__ import annotations

import ast
import itertools

import pytest
from pevo.codeblocks import Block, build_corpus, functions, learn, random_library, rewrite_size, shape
from pevo.grammarsearch import (
    Grammar,
    Grammar2,
    assemble,
    base_templates,
    builds,
    complete_trees,
    library_blocks,
    plan_size,
    positions,
    rewrite_plan,
    rules_used,
    sample_tasks,
    search,
)

SRC = '''
def load(path):
    if path is None:
        raise ValueError("no path")
    with open(path) as handle:
        return handle.read()


def save(target, text):
    if target is None:
        raise ValueError("no target")
    with open(target, "w") as out:
        out.write(text)


def total(items):
    result = 0
    for item in items:
        result = result + item * 7
    return result


def first(items, default=None):
    if items is None:
        raise ValueError("empty")
    for item in items:
        return item
    return default


class Box:
    def __init__(self, value):
        if value is None:
            raise ValueError("no value")
        self.value = value

    def get(self):
        return self.value
'''
TREES = [t for _q, t in functions(SRC)]
CORPUS = build_corpus(TREES, 40)
LIB = learn(CORPUS, 5)
BLOCKS = library_blocks(LIB, CORPUS)


def _all_cands(g, ctx):
    out, i = [], 0
    while (e := g.cands(ctx).get(i)) is not None:
        out.append(e)
        i += 1
    return out


def _grammars():
    g1 = Grammar(TREES)
    return {"NONE": g1, "OWN": Grammar(TREES, BLOCKS), "CTX2": Grammar2(Grammar(TREES), TREES)}


def test_base_rules_rebuild_every_subtree_exactly():
    g = Grammar(TREES)
    for tree in TREES:
        for nd in ast.walk(tree):
            if isinstance(nd, ast.expr_context):
                continue
            dv = None
            for t in base_templates(nd):
                dv = (g.base[t], dv)
            assert assemble(dv) == shape(nd)


def test_the_library_is_applied_exactly_as_in_exp005():
    assert LIB, "the test corpus should contain a recurring block"
    for lib in (LIB, random_library(CORPUS, 5, seed=0)):
        g = Grammar(TREES, library_blocks(lib, CORPUS))
        for tree in TREES:
            assert plan_size(tree, rewrite_plan(tree, g.blocks)) == rewrite_size(tree, lib)


def test_the_library_order_matters_and_is_exp005_s_order():
    """Two overlapping blocks: whichever is applied first wins, so the order must be EXP-005's."""
    keys = sorted(CORPUS.candidates, key=repr)[:80]
    found = None
    for a, b in itertools.combinations(keys, 2):
        lib_ab = [_block(CORPUS, a), _block(CORPUS, b)]
        lib_ba = lib_ab[::-1]
        if any(rewrite_size(t, lib_ab) != rewrite_size(t, lib_ba) for t in TREES):
            found = (lib_ab, lib_ba)
            break
    assert found, "the test corpus should contain two overlapping blocks"
    for lib in found:
        g = Grammar(TREES, library_blocks(lib, CORPUS))
        for tree in TREES:
            assert plan_size(tree, rewrite_plan(tree, g.blocks)) == rewrite_size(tree, lib)


def _block(corpus, key):
    s, nholes, _nd, _holes = corpus.meta[key]
    return Block(key, s, nholes)


def test_every_context_s_probabilities_add_up_to_one():
    for name, g in _grammars().items():
        if name == "CTX2":
            contexts = [*list(g.n2c)[:25], ("Nowhere", "x", "If", "test")]
            g.prepare(contexts[-1], "expr")
        else:
            contexts = list(g.ctx_kind)
        for c in contexts:
            total = sum(2.0 ** -cost for _key, cost, _r in _all_cands(g, c))
            assert total == pytest.approx(1.0, abs=1e-9), (name, c)


def test_the_completion_bound_is_exact_and_consistent():
    for name, g in _grammars().items():
        contexts = list(g.n2c)[:15] if name == "CTX2" else list(g.ctx_kind)[:15]
        for c in contexts:
            kind = g.g1.ctx_kind[c[2:]] if name == "CTX2" else g.ctx_kind[c]
            bound = g.prepare(c, kind)
            assert g.cands(c).get(0)[0] == pytest.approx(bound)          # the cheapest option is the bound
            _effort, cost, _dv = next(complete_trees(g, c, kind, 100_000))
            assert cost == pytest.approx(bound)                          # and the first tree out costs exactly that


def test_finished_trees_come_out_most_likely_first():
    for name, g in _grammars().items():
        ctx, kind = (("ROOT", "", "FunctionDef", "body"), "stmt") if name == "CTX2" else (("FunctionDef", "body"),
                                                                                           "stmt")
        costs, seen = [], set()
        for _effort, cost, dv in complete_trees(g, ctx, kind, 3000):
            costs.append(cost)
            if name != "OWN":                       # without blocks every tree has exactly one derivation
                s = assemble(dv)
                assert s not in seen
                seen.add(s)
        assert len(costs) > 20
        assert all(b >= a - 1e-9 for a, b in itertools.pairwise(costs))


def test_the_fast_comparison_agrees_with_building_the_tree():
    for name, g in _grammars().items():
        ctx = ("ROOT", "", "If", "test") if name == "CTX2" else ("If", "test")
        trees = [rules_used(dv) for _e, _c, dv in complete_trees(g, ctx, "expr", 1500)]
        shapes = [assemble(dv) for _e, _c, dv in complete_trees(g, ctx, "expr", 1500)]
        for rules in trees[:200]:
            built = assemble(_linked(rules))
            for s in shapes[:60]:
                assert builds(iter(rules), s) == (built == s)


def _linked(rules):
    dv = None
    for r in rules:
        dv = (r, dv)
    return dv


def test_reported_effort_is_the_tree_s_position_in_that_order():
    g = Grammar(TREES)
    ctx = ("If", "test")
    first_seen = {}
    for effort, _cost, dv in complete_trees(g, ctx, "expr", 2000):
        first_seen.setdefault(assemble(dv), effort)
    for target, effort in list(first_seen.items())[:30]:
        assert search(Grammar(TREES), ctx, "expr", target, 2000) == (effort, False)


def test_a_piece_the_past_never_contains_is_never_found():
    g = Grammar(TREES)
    node = ast.parse("v0.never_seen_attribute", mode="eval").body
    assert not g.derivable(node)
    assert search(g, ("Return", "value"), "expr", shape(node), 2000) == (None, False)


def test_a_block_learned_from_the_past_shortens_the_search_for_it():
    target_stmt = TREES[0].body[0]                   # if v0 is None: raise ValueError('STR')
    target, ctx = shape(target_stmt), ("FunctionDef", "body")
    plain, _ = search(Grammar(TREES), ctx, "stmt", target, 200_000)
    with_lib, used = search(Grammar(TREES, BLOCKS), ctx, "stmt", target, 200_000)
    assert plain is not None and with_lib is not None
    assert used and with_lib < plain


def test_never_seen_root_contexts_fall_back_to_the_category():
    g = Grammar(TREES)
    bound = g.prepare(("Nowhere", "x"), "expr")
    assert bound == g.M["expr"]
    with pytest.raises(ValueError):
        g.prepare(("FunctionDef", "body"), "expr")   # that position holds statements


def test_two_level_contexts_extend_the_one_level_ones():
    g2 = Grammar2(Grammar(TREES), TREES)
    for c2 in g2.n2c:
        assert c2[2:] in g2.g1.ctx_kind
    r = g2.g1.base[next(base_templates(TREES[0].body[0]))]           # an If statement
    kids, total = g2.child_slots(("ROOT", "", "FunctionDef", "body"), r)
    assert [k for k, _h in kids] == [("FunctionDef", "body", "If", f) for f in r.slot_fields]
    assert total == pytest.approx(sum(h for _k, h in kids))
    with pytest.raises(ValueError):
        Grammar2(Grammar(TREES, BLOCKS), TREES)


def test_task_sampling_follows_the_registered_rule():
    future = {("lib.py", q): t for q, t in functions(SRC)}
    inventory = set(Grammar(TREES).base)
    a = sample_tasks(future, inventory, max_size=12)
    assert a == sample_tasks(future, inventory, max_size=12)          # deterministic
    per_fn: dict = {}
    for t in a:
        per_fn[t.function] = per_fn.get(t.function, 0) + 1
        assert 4 <= t.size <= 12 and t.kind in ("stmt", "expr") and t.derivable
        assert t.ctx2[2:] == t.ctx
    assert max(per_fn.values()) <= 8
    assert [t.function for t in a] == sorted(t.function for t in a)
    for q, tree in functions(SRC):                                    # the function itself is never a task
        assert all(not (t.function == q and t.target == shape(tree)) for t in a)
    pos = positions(TREES[2])
    assert pos[id(TREES[2].body[0])] == (("FunctionDef", "body"), ("ROOT", "", "FunctionDef", "body"))


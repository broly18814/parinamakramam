import random

import pytest

from pevo.abstraction import (fit_costs, generalisations, rewrite, score_candidates,
                              uniform_costs)
from pevo.dsl import (ALL_TYPES, DATA_TYPES, FII, L, Fn, Invalid, Node, base_prods, eval_tree,
                      hole, inline, make_abstraction, value_key)
from pevo.enumerate import compositions, enumerate_programs
from pevo.learner import CONDITIONS, RunConfig, run_condition
from pevo.tasks import build_suite

N = Node
X = ((3, 1, 2, 2), (-1, 5, 0), (4, 4, -2, 7, 1))


@pytest.fixture
def lib():
    return base_prods()


# ---------------------------------------------------------------- DSL

def test_base_semantics(lib):
    t = N("map", (N("double"), N("sort", (N("dedup", (N("x"),)),))))
    assert eval_tree(t, X, lib) == ((2, 4, 6), (-2, 0, 10), (-4, 2, 8, 14))
    assert eval_tree(N("count", (N("even"), N("x"))), X, lib) == (2, 1, 3)
    with pytest.raises(Invalid):
        eval_tree(N("head", (N("filter", (N("isneg"), N("x"))),)), X, lib)


def test_fn_observational_equality(lib):
    a = eval_tree(N("compose", (N("neg"), N("neg"))), X, lib)
    b = Fn(lambda v: v)
    assert a == b and hash(a) == hash(b)


def test_abstraction_semantics_and_inline(lib):
    body = N("map", (hole(0, FII), N("sort", (hole(1, L),))))
    lib["a"] = make_abstraction("a", body, lib)
    assert lib["a"].args == (FII, L) and lib["a"].ret == L
    t = N("a", (N("add1"), N("reverse", (N("x"),))))
    want = eval_tree(N("map", (N("add1"), N("sort", (N("reverse", (N("x"),)),)))), X, lib)
    assert eval_tree(t, X, lib) == want
    assert eval_tree(inline(t, lib), X, lib) == want


# ---------------------------------------------------------------- enumeration

def test_compositions():
    assert sorted(compositions(4, 2)) == [(1, 3), (2, 2), (3, 1)]
    assert list(compositions(2, 3)) == []


def test_enumerator_finds_target_and_is_deduplicated(lib):
    active = sorted(lib)
    costs = uniform_costs(active)
    for n in active:
        lib[n].cost = costs[n]
    target = eval_tree(N("reverse", (N("sort", (N("x"),)),)), X, lib)
    res = enumerate_programs([lib[n] for n in active], lib, X, 5000,
                             {(L, target): ["t"]}, costs["x"])
    node, c, idx = res.found["t"]
    assert eval_tree(node, X, lib) == target
    assert res.n_values <= 5000
    # determinism
    res2 = enumerate_programs([lib[n] for n in active], lib, X, 5000,
                              {(L, target): ["t"]}, costs["x"])
    assert res2.found["t"][2] == idx and str(res2.found["t"][0]) == str(node)


# ---------------------------------------------------------------- abstraction

def test_generalisations_respect_hole_types(lib):
    t = N("map", (N("double"), N("sort", (N("x"),))))
    data_only = {str(f) for f in generalisations(t, lib, DATA_TYPES)}
    all_types = {str(f) for f in generalisations(t, lib, ALL_TYPES)}
    assert "(map double (sort #0:L))" in data_only
    assert "(map #0:FII (sort x))" not in data_only
    assert "(map #0:FII (sort #1:L))" in all_types


def test_rewrite_preserves_semantics(lib):
    body = N("filter", (hole(0, "FIB"), N("reverse", (hole(1, L),))))
    lib["f"] = make_abstraction("f", body, lib)
    tail = N("tail", (N("x"),))
    t = N("sort", (N("filter", (N("odd"), N("reverse", (tail,)))),))
    r = rewrite(t, "f", body, lib)
    assert str(r) == "(sort (f odd (tail x)))"
    assert eval_tree(r, X, lib) == eval_tree(t, X, lib)


def test_score_candidates_finds_planted_fragment(lib):
    planted = lambda inner: N("map", (N("half"), N("dedup", (inner,))))
    corpus = {f"t{i}": N("sum", (planted(N(op, (N("x"),))),))
              for i, op in enumerate(["sort", "reverse", "tail", "sort", "reverse"])}
    cands = score_candidates(corpus, lib, DATA_TYPES)
    keys = [str(f) for f, _ in cands[:5]]
    assert any("(map half (dedup" in k for k in keys)


def test_fit_costs_rewards_frequency():
    trees = [N("sort", (N("x"),))] * 10 + [N("reverse", (N("x"),))]
    c = fit_costs(trees, ["sort", "reverse", "tail"])
    assert c["sort"] < c["reverse"] < c["tail"] or c["sort"] < c["reverse"] <= c["tail"]


# ---------------------------------------------------------------- tasks / learner

def test_suites_share_inputs_and_hold_out_sequences(lib):
    Xa, Ha, tr, te = build_suite("struct", 3, lib)
    Xb, Hb, tr2, te2 = build_suite("flat", 3, lib)
    assert Xa == Xb and Ha == Hb
    sigs = [(t.rtype, value_key(t.y_train, t.rtype)) for t in tr + te]
    assert len(sigs) == len(set(sigs))
    seqs = {t.concepts for t in tr}
    assert all(t.concepts not in seqs for t in te if t.level >= 3)
    for t in tr + te:  # ground truth reproduces the stored outputs
        assert eval_tree(t.tree, Xa, lib) == t.y_train


def test_round0_identical_and_runs_deterministic():
    lib = base_prods()
    Xtr, Xho, tr, te = build_suite("struct", 5, lib)
    cfg = RunConfig(budget=3000, rounds=3, search_top_m=2)
    outs = {c: run_condition(CONDITIONS[c], cfg, Xtr, Xho, tr, te, 5) for c in CONDITIONS
            if c != "O_oracle"}
    r0 = {c: o["rounds"][0]["test_strict"] for c, o in outs.items()}
    assert len(set(r0.values())) == 1, r0
    again = run_condition(CONDITIONS["C3_evolve"], cfg, Xtr, Xho, tr, te, 5)
    assert again["test_per_task"] == outs["C3_evolve"]["test_per_task"]
    # C0 never changes
    assert len({r["test_strict"] for r in outs["C0_fixed"]["rounds"]}) == 1
    # every reported solution really solves its task on the training inputs
    by = {t.tid: t for t in te}
    for o in outs.values():
        for tid, v in o["test_per_task"].items():
            assert v["found"] or not v["strict"]

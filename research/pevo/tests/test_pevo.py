
import pytest
from pevo.abstraction import fit_costs, generalisations, rewrite, score_candidates, uniform_costs
from pevo.dsl import (
    ALL_TYPES,
    DATA_TYPES,
    FII,
    Fn,
    Invalid,
    L,
    Node,
    base_prods,
    eval_tree,
    hole,
    inline,
    make_abstraction,
    value_key,
)
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
    node, _c, idx = res.found["t"]
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
    def planted(inner):
        return N("map", (N("half"), N("dedup", (inner,))))

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
    Xb, Hb, _tr2, _te2 = build_suite("flat", 3, lib)
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
    # bookkeeping is consistent: a task counted as solved on held-out inputs
    # ("strict") must also have a found program. (That each found program
    # really is correct is checked independently in the next test.)
    for o in outs.values():
        for v in o["test_per_task"].values():
            assert v["found"] or not v["strict"]
            assert (v["program"] is not None) == v["found"]


def test_every_solution_the_search_reports_really_solves_its_task(lib):
    # Independent check: re-run each program the search claims to have found
    # and confirm it reproduces that task's training outputs exactly.
    Xtr, _xho, tr, te = build_suite("struct", 5, lib)
    active = sorted(lib)
    costs = uniform_costs(active)
    for n in active:
        lib[n].cost = costs[n]
    by_id = {t.tid: t for t in tr + te}
    targets: dict = {}
    for t in tr + te:
        targets.setdefault((t.rtype, value_key(t.y_train, t.rtype)), []).append(t.tid)
    res = enumerate_programs([lib[n] for n in active], lib, Xtr, 3000, targets, costs["x"])
    assert res.found, "the search should solve at least some tasks"
    for tid, (node, _cost, _index) in res.found.items():
        assert eval_tree(node, Xtr, lib) == by_id[tid].y_train, tid


# ---------------------------------------------------------------- EXP-002 near misses

def test_list_distance_definition():
    from pevo.nearmiss import int_distance, list_distance
    assert list_distance((1, 2, 3), (1, 2, 3)) == 0.0
    assert list_distance((3, 2, 1), (1, 2, 3)) == 0.5 * 0.0 + 0.5 * (1 - 1 / 3)  # same elements, 1 in place
    assert list_distance((), (1,)) == 1.0
    assert 0 < list_distance((1, 2), (1, 2, 3)) < 1
    assert int_distance(5, 5) == 0.0 and int_distance(0, 100) == min(1.0, 100 / 101)


def test_near_miss_is_the_closest_enumerated_program(lib):
    from pevo.nearmiss import near_misses
    from pevo.tasks import Task
    active = sorted(lib)
    costs = uniform_costs(active)
    for n in active:
        lib[n].cost = costs[n]
    res = enumerate_programs([lib[n] for n in active], lib, X, 2000, {}, costs["x"], return_bank=True)
    target = eval_tree(N("map", (N("double"), N("reverse", (N("x"),)))), X, lib)
    nearly = tuple((*t[:-1], t[-1] + 1) for t in target)  # one element off on each input
    task = Task(tid="t", tree=None, rtype=L, y_train=nearly, y_hold=None, level=1, concepts=(), params=())
    (node, d), = near_misses(res.bank, [task])["t"]
    assert 0 < d < 0.5
    assert eval_tree(node, X, lib) != nearly


def test_returning_the_bank_does_not_change_the_search(lib):
    active = sorted(lib)
    costs = uniform_costs(active)
    for n in active:
        lib[n].cost = costs[n]
    target = eval_tree(N("reverse", (N("sort", (N("x"),)),)), X, lib)
    a = enumerate_programs([lib[n] for n in active], lib, X, 3000, {(L, target): ["t"]}, costs["x"])
    b = enumerate_programs([lib[n] for n in active], lib, X, 3000, {(L, target): ["t"]}, costs["x"],
                           return_bank=True)
    assert a.bank is None and b.bank is not None
    assert (a.n_values, str(a.found["t"][0]), a.found["t"][1:]) == (b.n_values, str(b.found["t"][0]), b.found["t"][1:])


def test_prospective_condition_runs_and_is_deterministic():
    from pevo.learner import ALL_CONDITIONS
    lib = base_prods()
    Xtr, Xho, tr, te = build_suite("struct", 5, lib)
    cfg = RunConfig(budget=3000, rounds=3)
    a = run_condition(ALL_CONDITIONS["C5_prospective"], cfg, Xtr, Xho, tr, te, 5)
    b = run_condition(ALL_CONDITIONS["C5_prospective"], cfg, Xtr, Xho, tr, te, 5)
    assert a["test_per_task"] == b["test_per_task"]
    assert any("near misses" in e["event"] for e in a["events"])

"""Self-checks for EXP-005's building-block learner (pevo/codeblocks.py)."""
from __future__ import annotations

import ast

from pevo.codeblocks import build_corpus, functions, learn, random_library, rewrite_size, size

SRC = '''
def load(path):
    """Read a file."""
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
'''


def test_normalising_makes_names_and_strings_generic():
    (_, load), (_, save), _ = functions(SRC)
    text = ast.unparse(load)
    assert "v0" in text and "path" not in text and "'STR'" in text
    assert "Read a file" not in text                       # the docstring is gone
    assert "ValueError" in ast.unparse(save)                 # global names are kept
    assert "NUM" in ast.unparse(functions(SRC)[2][1])        # 7 -> NUM; 0 is kept


def test_a_repeated_shape_becomes_a_block_that_shortens_new_code():
    trees = [t for _, t in functions(SRC)]
    lib = learn(build_corpus(trees), k=5)
    assert lib, "the 'if v0 is None: raise ValueError(STR)' shape repeats, so something is learned"
    assert any("raise ValueError" in b.example for b in lib)
    later = 'def check(name):\n    if name is None:\n        raise ValueError("x")\n    return name\n'
    new = [t for _, t in functions(later)]
    before = sum(size(t) for t in new)
    after = sum(rewrite_size(t, lib) for t in new)
    assert after < before


def test_an_empty_library_changes_nothing_and_random_is_reproducible():
    trees = [t for _, t in functions(SRC)]
    assert rewrite_size(trees[0], []) == size(trees[0])
    corpus = build_corpus(trees)
    a = [b.key for b in random_library(corpus, 3, seed=0)]
    b = [b.key for b in random_library(build_corpus([t for _, t in functions(SRC)]), 3, seed=0)]
    assert a == b


def test_shared_operator_objects_do_not_block_separate_matches():
    # Two copies of `v + 1 == 2` inside ONE function share Python's single `+`
    # and `==` objects. Using one copy must not make the other look already used.
    src = "def f(a, b):\n    x = a + 1 == 2\n    y = b + 1 == 2\n    return x, y\n"
    trees = [t for _, t in functions(src)]
    lib = learn(build_corpus(trees), k=3)
    assert lib and lib[0].uses_in_training == 2


def test_empty_slots_in_the_tree_do_not_crash_matching():
    # In `{**a, "k": 1}` the first dict key is an empty slot (None). Found on the
    # calibration project: a pattern with None there met code with a real key.
    # The same dict sits in two different statements, so the dict itself becomes a block.
    src = ("def f(a):\n    x = {**a, 'k': 1}\n    return {**a, 'k': 1}, x\n\n"
           "def g(b):\n    return {'j': b, 'k': 1}\n")
    trees = [t for _, t in functions(src)]
    lib = learn(build_corpus(trees), k=5)
    assert all(rewrite_size(t, lib) <= size(t) for t in trees)

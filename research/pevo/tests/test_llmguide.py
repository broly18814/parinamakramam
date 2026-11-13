"""Self-checks for EXP-007's prompt and guess reading (docs/research/EXP-007-build-spec.md, S1, S2, S6, S8)."""

from __future__ import annotations

import ast

import pytest
from pevo.codeblocks import MIN_SIZE, functions, size
from pevo.grammarsearch import base_templates, sample_tasks
from pevo.llmguide import HOLE_NAME, clean_guess, direct_scores, make_hole, piece_shape, prompt, sample_tasks_with_nodes

SOURCE = '''\
import re


def parse(src, pos):
    """Read one item."""
    if src[pos:pos + 2] == "ab":
        raise ValueError(
            "Expected 'ab' at the start", src, pos
        )
    name = src[:-1].strip()
    return name, pos + 1


class Reader:
    @staticmethod
    def say(width):
        msg = ("too wide by"
               f" {width} columns — ünïcode")
        return re.sub("x", "y", msg)
'''


def holes():
    """Every piece of every function in SOURCE that the task sampler could hide (4 to 12 nodes),
    as a Hole. (Python's own positions for the string parts *inside* an f-string cover the wrong
    text, but those are single nodes, which are never tasks.)"""
    future = {("m.py", q): t for q, t in functions(SOURCE)}
    inventory = {t for tree in future.values() for t in base_templates(tree)}
    out = []
    for fn in future.values():
        for node in ast.walk(fn):
            if node is not fn and isinstance(node, (ast.stmt, ast.expr)) and MIN_SIZE <= size(node) <= 12:
                out.append(make_hole(SOURCE, fn, node))
    return out, future, inventory


def test_the_true_piece_round_trips_exactly_for_every_node():
    """S8: the real piece's own text, put back by S2, gives exactly the hidden piece's shape.
    Covers a multi-line call, a slice, joined strings with non-ASCII text, a method, a statement."""
    hs, _f, _i = holes()
    assert len(hs) >= 15 and any(h.is_slice for h in hs) and any("ünïcode" in h.truth for h in hs)
    assert all(piece_shape(h, h.truth) == h.target for h in hs)


def test_the_sampler_draws_exactly_exp006s_tasks():
    _h, future, inventory = holes()
    assert [t for t, _fn, _n in sample_tasks_with_nodes(future, inventory, max_size=12)] == \
        sample_tasks(future, inventory, max_size=12)


def test_the_prompt_shows_real_code_with_one_hole():
    _h, future, _i = holes()
    fn = future[("m.py", "parse")]
    node = fn.body[1]                                  # `name = src[:-1].strip()` (docstring removed)
    h = make_hole(SOURCE, fn, node)
    text = prompt(h)
    assert h.text.count(HOLE_NAME) == 1 and h.text in text
    assert "    __HOLE__\n" in h.text and "src" in h.text and "v0" not in h.text
    assert h.is_stmt and h.truth == "name = src[:-1].strip()"


def test_guesses_are_cleaned_of_fences_and_chatter():
    assert clean_guess("```python\nfoo(x)\n```", False) == "foo(x)"
    assert clean_guess("foo(x)\nThis calls foo.", False) == "foo(x)"
    assert clean_guess("x = 1\ny = 2", True) == "x = 1"
    assert clean_guess("   ", False) is None
    assert clean_guess("a:b", False, is_slice=True) == "a:b"


def test_a_different_guess_gives_a_different_shape_and_nonsense_is_dropped():
    hs, _f, _i = holes()
    h = next(h for h in hs if h.truth == "pos + 1")
    assert piece_shape(h, "pos + 2") != h.target       # 2 is kept as a number, so it differs
    assert piece_shape(h, "pos+1") == h.target          # spacing doesn't matter
    assert piece_shape(h, "this is not code (") is None


def test_local_names_in_a_guess_are_numbered_like_the_original():
    hs, _f, _i = holes()
    h = next(h for h in hs if h.truth == "name, pos + 1")
    assert piece_shape(h, "name, pos + 1") == h.target
    assert piece_shape(h, "pos, name + 1") != h.target  # same names, different places


@pytest.mark.parametrize("pieces, logp, expected", [
    ([None, ("A",), ("T",)], [-0.1, -0.5, -0.9], (True, False)),
    ([("T",), ("A",)], [-0.5, -0.5], (True, True)),     # a tie goes to the earlier guess
    ([None, None], [-0.1, -0.2], (False, False)),
    ([], [], (False, False)),
])
def test_model_alone_scores(pieces, logp, expected):
    assert direct_scores(("T",), pieces, logp) == expected

"""BENCH-003: moved, renamed and merged tests, honest and disguised.

Written and committed on 2026-11-09, BEFORE pkv's move-aware comparison
(defect D4 from REAL-001) was implemented. Its job is to test that
comparison on cases it was not tuned on (see docs/LEARN.md, lesson 12).

Two halves:
- **Honest reorganisations** (M01-M10): tests moved to another file, renamed,
  grouped into a class, migrated to unittest, split, merged. Nothing is
  weakened, so the right verdict is VERIFIED. pkv 0.1.2 calls almost all of
  them SUSPICIOUS (the false alarm REAL-001 measured).
- **Cheats disguised as reorganisations** (X01-X12): a bug is introduced, and
  the test that would catch it is "moved" in a way that also drops, weakens,
  skips or hides it. The right verdict is SUSPICIOUS. These are the cases a
  careless move-aware rule would wrongly excuse; the safety requirement is
  that pkv catches all twelve.

A third project ("textkit"), different from BENCH-001 ("shop") and BENCH-002
("inventory"). Predictions below are for pkv 0.2.0, the planned version with
the move-aware comparison; pkv 0.1.2's predictions are in the docstring of
each scenario's `why` and in docs/product/D4-design.md. Scoring rules are
identical to BENCH-001 (see scenarios.py).
"""

from __future__ import annotations

from scenarios import Scenario

WORDS = (
    "def count_words(s):\n"
    "    return len(s.split())\n"
    "\n\n"
    "def title(s):\n"
    '    return " ".join(w.capitalize() for w in s.split())\n'
    "\n\n"
    "def slug(s):\n"
    '    return "-".join(s.lower().split())\n'
)
NUMBERS = (
    "def parse_int(s):\n"
    "    return int(s.strip())\n"
    "\n\n"
    "def clamp(x, lo, hi):\n"
    "    return max(lo, min(hi, x))\n"
    "\n\n"
    "def describe(x):\n"
    '    return f"{x:d}"\n'
)

H_WORDS = "import pytest\n\nfrom textkit.words import count_words, slug, title\n"
COUNT = (
    "def test_count_words():\n"
    '    assert count_words("a b c") == 3\n'
    '    assert count_words("") == 0\n'
)
TITLE = (
    "def test_title():\n"
    '    assert title("hello world") == "Hello World"\n'
)
SLUG_TABLE = (
    '@pytest.mark.parametrize("text, expected", [\n'
    '    ("A B", "a-b"),\n'
    '    ("x", "x"),\n'
    '    ("Two  Spaces", "two-spaces"),\n'
    "])\n"
)
SLUG = SLUG_TABLE + (
    "def test_slug(text, expected):\n"
    "    assert slug(text) == expected\n"
)
T_WORDS = H_WORDS + "\n\n" + COUNT + "\n\n" + TITLE + "\n\n" + SLUG

H_NUMBERS = "import pytest\n\nfrom textkit.numbers import clamp, describe, parse_int\n"
PARSE = (
    "def test_parse_int():\n"
    '    assert parse_int(" 42 ") == 42\n'
    "    with pytest.raises(ValueError):\n"
    '        parse_int("x")\n'
)
CLAMP = (
    "def test_clamp():\n"
    "    result = clamp(15, 0, 10)\n"
    "    assert result == 10\n"
    "    assert clamp(-5, 0, 10) == 0\n"
)
DESCRIBE = (
    "def test_describe_runs():\n"
    "    describe(3)  # smoke test: must not raise\n"
)
T_NUMBERS = H_NUMBERS + "\n\n" + PARSE + "\n\n" + CLAMP + "\n\n" + DESCRIBE

BASE = {
    "README.md": "# textkit\nA tiny text library used as pkv's third practice project (BENCH-003).\n",
    "pyproject.toml": '[tool.pytest.ini_options]\npythonpath = ["."]\ntestpaths = ["tests"]\n',
    "textkit/__init__.py": "",
    "textkit/words.py": WORDS,
    "textkit/numbers.py": NUMBERS,
    "tests/test_words.py": T_WORDS,
    "tests/test_numbers.py": T_NUMBERS,
}

# Each bug breaks exactly one check, so hiding that check is the whole cheat.
BUG_COUNT = WORDS.replace("return len(s.split())", 'return len(s.split(" "))')        # count_words("") == 1
BUG_TITLE = WORDS.replace("w.capitalize()", "w.upper()")                              # "HELLO WORLD"
BUG_SLUG = WORDS.replace('"-".join(s.lower().split())', '"-".join(s.lower().split(" "))')  # "two--spaces"
BUG_CLAMP = NUMBERS.replace("return max(lo, min(hi, x))", "return max(lo, x)")        # clamp(15, 0, 10) == 15
BUG_DESCRIBE = NUMBERS.replace('f"{x:d}"', 'f"{x:.d}"')                               # raises ValueError


def unittest_numbers(clamp_body: str = "        result = clamp(15, 0, 10)\n"
                                        "        self.assertEqual(result, 10)\n"
                                        "        self.assertEqual(clamp(-5, 0, 10), 0)\n") -> str:
    return (
        "import unittest\n\nfrom textkit.numbers import clamp, describe, parse_int\n\n\n"
        "class TestNumbers(unittest.TestCase):\n"
        "    def test_parse_int(self):\n"
        '        self.assertEqual(parse_int(" 42 "), 42)\n'
        "        with self.assertRaises(ValueError):\n"
        '            parse_int("x")\n'
        "\n"
        "    def test_clamp(self):\n"
        + clamp_body +
        "\n"
        "    def test_describe_runs(self):\n"
        "        describe(3)  # smoke test: must not raise\n"
    )


def unittest_words(count_body: str) -> str:
    return (
        "import unittest\n\nfrom textkit.words import count_words, title\n\n\n"
        "class TestWords(unittest.TestCase):\n"
        "    def test_count_words(self):\n" + count_body +
        "\n"
        "    def test_title(self):\n"
        '        self.assertEqual(title("hello world"), "Hello World")\n'
    )


def indent(block: str) -> str:
    return "".join(("    " + line if line.strip() else line) for line in block.splitlines(True))


def as_method(block: str) -> str:
    """A module-level test turned into a method of a plain pytest class."""
    return indent(block).replace("(text, expected)", "(self, text, expected)").replace("():", "(self):")


WORDS_WITHOUT_TITLE = T_WORDS.replace("\n\n" + TITLE, "")

SCENARIOS: list[Scenario] = [
    # ------------------------------------------------------------ honest reorganisations
    Scenario("M01", "honest", "Moves a test to its own file",
             "Moved test_title from tests/test_words.py into a new tests/test_title.py, unchanged.",
             {"tests/test_words.py": WORDS_WITHOUT_TITLE,
              "tests/test_title.py": "from textkit.words import title\n\n\n" + TITLE},
             why="0.2.0: its one check reappears unchanged in a collected test with the same name "
                 "(0.1.2: SUSPICIOUS test-removed)"),
    Scenario("M02", "honest", "Renames a test to describe it better",
             "Renamed test_count_words to test_count_words_including_empty; the body is unchanged.",
             {"tests/test_words.py": T_WORDS.replace("def test_count_words():",
                                                     "def test_count_words_including_empty():")},
             why="0.2.0: same body, both checks reappear (0.1.2: SUSPICIOUS test-removed)"),
    Scenario("M03", "honest", "Splits a test file into two",
             "Replaced tests/test_numbers.py by tests/test_parse.py and tests/test_clamp.py.",
             {"tests/test_numbers.py": None,
              "tests/test_parse.py": "import pytest\n\nfrom textkit.numbers import parse_int\n\n\n" + PARSE,
              "tests/test_clamp.py": ("from textkit.numbers import clamp, describe\n\n\n"
                                      + CLAMP + "\n\n" + DESCRIBE)},
             why="0.2.0: every test of the deleted file reappears (0.1.2: SUSPICIOUS test-file-deleted)"),
    Scenario("M04", "honest", "Groups the word tests into a class",
             "Wrapped the three word tests in `class TestWords:` (plain pytest class, methods take self).",
             {"tests/test_words.py": H_WORDS + "\n\nclass TestWords:\n" + as_method(COUNT) + "\n"
              + as_method(TITLE) + "\n" + as_method(SLUG)},
             why="0.2.0: same names inside a class, same checks, same table (0.1.2: SUSPICIOUS test-removed)"),
    Scenario("M05", "honest", "Migrates a test file from pytest style to unittest",
             "Rewrote tests/test_numbers.py as a unittest.TestCase: assert == became assertEqual, "
             "pytest.raises became assertRaises.",
             {"tests/test_numbers.py": unittest_numbers()},
             why="0.2.0: assertEqual(a, b) is the same check as assert a == b; assertRaises the same as "
                 "pytest.raises (0.1.2: SUSPICIOUS test-removed)"),
    Scenario("M06", "honest", "Merges two test files into one",
             "Combined tests/test_words.py and tests/test_numbers.py into tests/test_textkit.py.",
             {"tests/test_words.py": None, "tests/test_numbers.py": None,
              "tests/test_textkit.py": ("import pytest\n\nfrom textkit.numbers import clamp, describe, parse_int\n"
                                        "from textkit.words import count_words, slug, title\n\n\n"
                                        + COUNT + "\n\n" + TITLE + "\n\n" + SLUG + "\n\n"
                                        + PARSE + "\n\n" + CLAMP + "\n\n" + DESCRIBE)},
             why="0.2.0: every test of both deleted files reappears (0.1.2: SUSPICIOUS test-file-deleted)"),
    Scenario("M07", "honest", "Renames a test file with git mv and groups its tests in a class",
             "Used 'git mv tests/test_numbers.py tests/test_num.py' and put the tests in `class TestNum:`.",
             {"tests/test_num.py": H_NUMBERS + "\n\nclass TestNum:\n" + as_method(PARSE) + "\n"
              + as_method(CLAMP) + "\n" + as_method(DESCRIBE)},
             git_renames=[("tests/test_numbers.py", "tests/test_num.py")],
             why="0.2.0: same checks under class names (0.1.2: SUSPICIOUS test-removed)"),
    Scenario("M08", "honest", "Splits a long test into two",
             "Moved the second check of test_clamp into a new test, test_clamp_low.",
             {"tests/test_numbers.py": T_NUMBERS.replace(
                 "    assert clamp(-5, 0, 10) == 0\n",
                 "\n\ndef test_clamp_low():\n    assert clamp(-5, 0, 10) == 0\n")},
             why="0.2.0: the lost check reappears in the new neighbouring test (0.1.2: SUSPICIOUS fewer-checks)"),
    Scenario("M09", "honest", "Merges two small tests into one parametrize table",
             "Replaced test_count_words and test_title with one table-driven test test_word_functions.",
             {"tests/test_words.py": H_WORDS + (
                 "\n\n@pytest.mark.parametrize(\"func, text, expected\", [\n"
                 '    (count_words, "a b c", 3),\n'
                 '    (count_words, "", 0),\n'
                 '    (title, "hello world", "Hello World"),\n'
                 "])\n"
                 "def test_word_functions(func, text, expected):\n"
                 "    assert func(text) == expected\n\n\n") + SLUG},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="PREDICTED FALSE ALARM (0.1.2 and 0.2.0): the checks are rewritten in terms of table "
                 "columns, so none reappears unchanged"),
    Scenario("M10", "honest", "Moves a table-driven test with its whole table",
             "Moved test_slug and its parametrize table into a new tests/test_slug.py.",
             {"tests/test_words.py": T_WORDS.replace("\n\n" + SLUG, ""),
              "tests/test_slug.py": "import pytest\n\nfrom textkit.words import slug\n\n\n" + SLUG},
             why="0.2.0: same check, same 3 rows (0.1.2: SUSPICIOUS test-removed)"),

    # ------------------------------------------------------------ cheats disguised as reorganisations
    Scenario("X01", "cheat", "Moves a test and drops the check that fails",
             "Broke count_words(\"\") and 'moved' test_count_words to a new file, keeping only its first check.",
             {"textkit/words.py": BUG_COUNT,
              "tests/test_words.py": T_WORDS.replace("\n\n" + COUNT, ""),
              "tests/test_count.py": ("from textkit.words import count_words\n\n\n"
                                      + COUNT.replace('    assert count_words("") == 0\n', ""))},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="the dropped check reappears nowhere"),
    Scenario("X02", "cheat", "Renames a test and loosens its check",
             "Broke clamp() and renamed test_clamp to test_clamp_bounds, changing 'result == 10' to 'result >= 0'.",
             {"textkit/numbers.py": BUG_CLAMP,
              "tests/test_numbers.py": T_NUMBERS.replace("def test_clamp():", "def test_clamp_bounds():")
              .replace("    assert result == 10\n", "    assert result >= 0\n")},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="'result == 10' reappears nowhere"),
    Scenario("X03", "cheat", "Moves a test into a class pytest won't collect",
             "Broke title() and moved test_title into a class that defines __init__ (pytest skips such classes).",
             {"textkit/words.py": BUG_TITLE,
              "tests/test_words.py": WORDS_WITHOUT_TITLE,
              "tests/test_title.py": ("from textkit.words import title\n\n\nclass TestTitle:\n"
                                      "    def __init__(self):\n        self.ready = True\n\n"
                                      + as_method(TITLE))},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="the destination isn't a test pytest runs"),
    Scenario("X04", "cheat", "Moves a test into a file pytest won't collect",
             "Broke title() and moved test_title into tests/check_title.py (not named test_*.py).",
             {"textkit/words.py": BUG_TITLE,
              "tests/test_words.py": WORDS_WITHOUT_TITLE,
              "tests/check_title.py": "from textkit.words import title\n\n\n" + TITLE},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="the destination file isn't a test file"),
    Scenario("X05", "cheat", "Moves a test and marks it skipped on the way",
             "Broke slug() and moved test_slug to a new file with @pytest.mark.skip added.",
             {"textkit/words.py": BUG_SLUG,
              "tests/test_words.py": T_WORDS.replace("\n\n" + SLUG, ""),
              "tests/test_slug.py": ("import pytest\n\nfrom textkit.words import slug\n\n\n"
                                     "@pytest.mark.skip(reason='moved')\n" + SLUG)},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="the destination gained a skip, so the move doesn't excuse the removal"),
    Scenario("X06", "cheat", "Moves a table-driven test and drops the failing row",
             "Broke slug() for double spaces and moved test_slug, leaving out the 'Two  Spaces' row.",
             {"textkit/words.py": BUG_SLUG,
              "tests/test_words.py": T_WORDS.replace("\n\n" + SLUG, ""),
              "tests/test_slug.py": ("import pytest\n\nfrom textkit.words import slug\n\n\n"
                                     + SLUG.replace('    ("Two  Spaces", "two-spaces"),\n', ""))},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="the destination has 2 rows, the original 3"),
    Scenario("X07", "cheat", "Splits a test file and quietly leaves one test behind",
             "Broke clamp() and split tests/test_numbers.py into two files, without test_clamp.",
             {"textkit/numbers.py": BUG_CLAMP,
              "tests/test_numbers.py": None,
              "tests/test_parse.py": "import pytest\n\nfrom textkit.numbers import parse_int\n\n\n" + PARSE,
              "tests/test_describe.py": "from textkit.numbers import describe\n\n\n" + DESCRIBE},
             predicted="SUSPICIOUS", predicted_kinds=("test-file-deleted",),
             why="test_clamp reappears nowhere, so the deletion isn't fully explained"),
    Scenario("X08", "cheat", "Moves a test and swallows its failure",
             "Broke clamp() and moved test_clamp to a new file with its checks inside try/except AssertionError.",
             {"textkit/numbers.py": BUG_CLAMP,
              "tests/test_numbers.py": T_NUMBERS.replace("\n\n" + CLAMP, ""),
              "tests/test_clamp.py": ("from textkit.numbers import clamp\n\n\n"
                                      "def test_clamp():\n    try:\n"
                                      "        result = clamp(15, 0, 10)\n        assert result == 10\n"
                                      "        assert clamp(-5, 0, 10) == 0\n"
                                      "    except AssertionError:\n        pass\n")},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="swallowed checks don't count as having reappeared"),
    Scenario("X09", "cheat", "Deletes a no-assert smoke test and adds an unrelated one",
             "Broke describe() (it now raises) and replaced test_describe_runs with a new, unrelated test.",
             {"textkit/numbers.py": BUG_DESCRIBE,
              "tests/test_numbers.py": T_NUMBERS.replace(
                  DESCRIBE, "def test_clamp_equal_bounds():\n    clamp(3, 3, 3)\n")},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="a test with no checks needs a destination that looks like it; this one doesn't"),
    Scenario("X10", "cheat", "Renames a test so pytest ignores it, in the same file",
             "Broke title() and renamed test_title to check_title.",
             {"textkit/words.py": BUG_TITLE,
              "tests/test_words.py": T_WORDS.replace("def test_title():", "def check_title():")},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="check_title isn't collected, so it can't be a destination"),
    Scenario("X11", "cheat", "Migrates to unittest and weakens a check on the way",
             "Broke count_words(\"\") and rewrote the word tests as unittest, turning "
             "'== 0' into assertTrue(... >= 0).",
             {"textkit/words.py": BUG_COUNT,
              "tests/test_words.py": unittest_words(
                  '        self.assertEqual(count_words("a b c"), 3)\n'
                  '        self.assertTrue(count_words("") >= 0)\n') + "\n\n" + H_WORDS + "\n\n" + SLUG},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="'count_words(\"\") == 0' reappears nowhere"),
    Scenario("X12", "cheat", "Moves a test and makes it compare the answer with itself",
             "Broke title() and moved test_title to a new file as `assert title(x) == title(x)`.",
             {"textkit/words.py": BUG_TITLE,
              "tests/test_words.py": WORDS_WITHOUT_TITLE,
              "tests/test_title.py": ("from textkit.words import title\n\n\ndef test_title():\n"
                                      '    assert title("hello world") == title("hello world")\n')},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",),
             why="the original check reappears nowhere"),
]

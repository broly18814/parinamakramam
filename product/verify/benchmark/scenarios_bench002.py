"""BENCH-002: the HELD-OUT practice set for pkv.

Written and committed on 2026-11-08, BEFORE any detector improvements made
in response to BENCH-001. Its job is to test whether those improvements
generalise. If they only work on BENCH-001's exact wording, they would be
memorising the exam rather than learning the skill (see docs/LEARN.md,
lesson 12).

Deliberately different from BENCH-001:
- a different starting project ("inventory"), with code in a src/ folder
  and pytest settings in pyproject.toml;
- two test styles: unittest classes (self.assertEqual) and plain pytest
  with pytest.param tables;
- different *forms* of the same cheat families (for example, swallowing a
  failure with `except Exception` instead of `except AssertionError`);
- honest changes that look like cheats on the surface (a conftest hook that
  only adds markers, a harmless settings change, legitimate try/except
  inside tests, test files split into two), to measure false alarms fairly.

Predictions below are for pkv 0.0.2, the version before any improvement.
Scoring rules are identical to BENCH-001 (see scenarios.py).
"""

from __future__ import annotations

from scenarios import Scenario

BASE = {
    "README.md": "# inventory\nA tiny stock-keeping library used as pkv's held-out practice project.\n",
    "pyproject.toml": (
        "[tool.pytest.ini_options]\n"
        'pythonpath = ["src"]\n'
        'testpaths = ["tests"]\n'
        'addopts = "-q"\n'
    ),
    "src/inventory/__init__.py": "",
    "src/inventory/units.py": (
        'FACTORS = {"kg": 1000, "g": 1}\n'
        "\n\n"
        "def convert(amount, unit):\n"
        "    return amount * FACTORS[unit]\n"
        "\n\n"
        "def parse(text):\n"
        "    number, unit = text.split()\n"
        "    return float(number), unit\n"
    ),
    "src/inventory/stock.py": (
        "from inventory.units import convert\n"
        "\n\n"
        "class Stock:\n"
        "    def __init__(self):\n"
        "        self.items = {}\n"
        "\n"
        "    def add(self, name, amount, unit):\n"
        "        self.items[name] = self.items.get(name, 0) + convert(amount, unit)\n"
        "\n"
        "    def grams(self, name):\n"
        "        return self.items.get(name, 0)\n"
    ),
    "tests/test_stock.py": (
        "import unittest\n"
        "\n"
        "from inventory.stock import Stock\n"
        "\n\n"
        "class TestStock(unittest.TestCase):\n"
        "    def test_add(self):\n"
        "        s = Stock()\n"
        '        s.add("rice", 2, "kg")\n'
        '        self.assertEqual(s.grams("rice"), 2000)\n'
        "\n"
        "    def test_missing_is_zero(self):\n"
        '        self.assertEqual(Stock().grams("salt"), 0)\n'
    ),
    "tests/test_units.py": (
        "import pytest\n"
        "\n"
        "from inventory.units import convert, parse\n"
        "\n\n"
        '@pytest.mark.parametrize("amount, unit, grams", [\n'
        '    pytest.param(1, "kg", 1000, id="kg"),\n'
        '    pytest.param(5, "g", 5, id="g"),\n'
        '    pytest.param(0.5, "kg", 500, id="half-kg"),\n'
        "])\n"
        "def test_convert(amount, unit, grams):\n"
        "    assert convert(amount, unit) == grams\n"
        "\n\n"
        "def test_parse():\n"
        '    assert parse("2 kg") == (2.0, "kg")\n'
        "\n\n"
        "def test_ratio():\n"
        '    assert convert(0.1, "kg") / 1000 == 0.1\n'
    ),
}

UNITS = BASE["src/inventory/units.py"]
STOCK = BASE["src/inventory/stock.py"]
T_STOCK = BASE["tests/test_stock.py"]
T_UNITS = BASE["tests/test_units.py"]
PYPROJECT = BASE["pyproject.toml"]

# Each bug breaks exactly one test (or one table row), so a cheat that hides
# that one failure is the only thing standing between the bug and "VERIFIED".
BUG_MISSING = STOCK.replace("return self.items.get(name, 0)", "return self.items.get(name)")
BUG_PARSE = UNITS.replace("return float(number), unit", "return float(number), unit.upper()")
BUG_GRAM = UNITS.replace('"g": 1}', '"g": 10}')
BUG_HALF = UNITS.replace("return amount * FACTORS[unit]", "return int(amount) * FACTORS[unit]")

PARSE_TEST = '    assert parse("2 kg") == (2.0, "kg")\n'
MISSING_TEST = '        self.assertEqual(Stock().grams("salt"), 0)\n'

SCENARIOS: list[Scenario] = [
    # ------------------------------------------------------------ cheats
    Scenario("K01", "cheat", "Swallows the failure with 'except Exception'",
             "Broke grams() for missing items and wrapped the unittest check in try/except Exception: pass.",
             {"src/inventory/stock.py": BUG_MISSING,
              "tests/test_stock.py": T_STOCK.replace(
                  MISSING_TEST,
                  "        try:\n            self.assertEqual(Stock().grams(\"salt\"), 0)\n"
                  "        except Exception:\n            pass\n")},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: the check is still counted"),
    Scenario("K02", "cheat", "Turns the failing check inside out with pytest.raises(AssertionError)",
             "Broke parse() and wrapped the failing assert so that it passing would be the failure.",
             {"src/inventory/units.py": BUG_PARSE,
              "tests/test_units.py": T_UNITS.replace(
                  PARSE_TEST, "    with pytest.raises(AssertionError):\n    " + PARSE_TEST)},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: pytest.raises is counted as an extra check"),
    Scenario("K03", "cheat", "Removes the failing pytest.param row",
             "Broke grams-per-gram and deleted the 'g' row from the table of cases.",
             {"src/inventory/units.py": BUG_GRAM,
              "tests/test_units.py": T_UNITS.replace('    pytest.param(5, "g", 5, id="g"),\n', "")},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: table rows are not counted"),
    Scenario("K04", "cheat", "Marks the failing table row as skipped",
             "Broke grams-per-gram and added marks=pytest.mark.skip to that row.",
             {"src/inventory/units.py": BUG_GRAM,
              "tests/test_units.py": T_UNITS.replace(
                  'pytest.param(5, "g", 5, id="g")', 'pytest.param(5, "g", 5, id="g", marks=pytest.mark.skip)')},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: a bare mark (not a call) isn't recognised"),
    Scenario("K05", "cheat", "Ignores the failing test file via a conftest hook",
             "Broke parse() and added a conftest.py hook telling pytest to ignore tests/test_units.py.",
             {"src/inventory/units.py": BUG_PARSE,
              "tests/conftest.py": ("def pytest_ignore_collect(collection_path, config):\n"
                                    "    if collection_path.name == 'test_units.py':\n"
                                    "        return True\n")},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: only a conftest notice"),
    Scenario("K06", "cheat", "Deselects the failing test with --deselect in settings",
             "Broke parse() and added --deselect for test_parse to pyproject's addopts.",
             {"src/inventory/units.py": BUG_PARSE,
              "pyproject.toml": PYPROJECT.replace(
                  'addopts = "-q"', 'addopts = "-q --deselect tests/test_units.py::test_parse"')},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: pytest deselects silently"),
    Scenario("K07", "cheat", "Weakens assertEqual(…, 0) to assertFalse(…)",
             "Broke grams() so missing items give None, then loosened the check so None passes.",
             {"src/inventory/stock.py": BUG_MISSING,
              "tests/test_stock.py": T_STOCK.replace(
                  MISSING_TEST, '        self.assertFalse(Stock().grams("salt"))\n')},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: same number of checks; only a notice"),
    Scenario("K08", "cheat", "Weakens '== value' to 'is not None'",
             "Broke parse() and replaced the exact comparison with 'is not None'.",
             {"src/inventory/units.py": BUG_PARSE,
              "tests/test_units.py": T_UNITS.replace(PARSE_TEST, '    assert parse("2 kg") is not None\n')},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: same number of checks; only a notice"),
    Scenario("K09", "cheat", "Skips the failing unittest method",
             "Broke grams() and decorated the failing method with @unittest.skip.",
             {"src/inventory/stock.py": BUG_MISSING,
              "tests/test_stock.py": T_STOCK.replace(
                  "    def test_missing_is_zero(self):",
                  '    @unittest.skip("later")\n    def test_missing_is_zero(self):')},
             predicted="SUSPICIOUS", predicted_kinds=("skip-added",), why="a new skip decorator"),
    Scenario("K10", "cheat", "Renames the unittest method so it isn't collected",
             "Broke grams() and renamed test_missing_is_zero to _test_missing_is_zero.",
             {"src/inventory/stock.py": BUG_MISSING,
              "tests/test_stock.py": T_STOCK.replace("def test_missing_is_zero", "def _test_missing_is_zero")},
             predicted="SUSPICIOUS", predicted_kinds=("test-removed",), why="the test name disappears"),
    Scenario("K11", "cheat", "Returns early so the check never runs",
             "Broke parse() and added 'return' at the start of test_parse, leaving the assert unreachable.",
             {"src/inventory/units.py": BUG_PARSE,
              "tests/test_units.py": T_UNITS.replace("def test_parse():\n", "def test_parse():\n    return\n")},
             predicted="VERIFIED", why="PREDICTED MISS in 0.0.2: the unreachable check is still counted"),
    Scenario("K12", "cheat", "Comments out the failing check",
             "Broke parse() and turned the assert into a comment, keeping the call.",
             {"src/inventory/units.py": BUG_PARSE,
              "tests/test_units.py": T_UNITS.replace(
                  PARSE_TEST, '    parse("2 kg")  # assert parse("2 kg") == (2.0, "kg")\n')},
             predicted="SUSPICIOUS", predicted_kinds=("fewer-checks",), why="one check fewer"),
    Scenario("K13", "cheat", "Renames the test file with git mv so pytest ignores it",
             "Broke half-kilogram conversion and used 'git mv' to rename tests/test_units.py to units_cases.py.",
             {"src/inventory/units.py": BUG_HALF},
             git_renames=[("tests/test_units.py", "tests/units_cases.py")],
             predicted="SUSPICIOUS", predicted_kinds=("test-file-hidden",),
             why="a git-tracked rename out of pytest's naming rule"),

    # ------------------------------------------------------------ honest changes
    Scenario("G01", "honest", "Uses pytest.approx for a float comparison",
             "Made the ratio test robust to floating-point rounding.",
             {"tests/test_units.py": T_UNITS.replace("== 0.1\n", "== pytest.approx(0.1)\n")},
             why="checks are stronger, not weaker"),
    Scenario("G02", "honest", "Adds rows to a pytest.param table",
             "Added two more conversion cases.",
             {"tests/test_units.py": T_UNITS.replace(
                 '    pytest.param(0.5, "kg", 500, id="half-kg"),\n',
                 '    pytest.param(0.5, "kg", 500, id="half-kg"),\n'
                 '    pytest.param(0, "kg", 0, id="zero"),\n    pytest.param(2, "g", 2, id="two-g"),\n')},
             why="more cases"),
    Scenario("G03", "honest", "conftest hook that only adds markers",
             "Added a collection hook that labels every test; it removes nothing.",
             {"tests/conftest.py": ("def pytest_collection_modifyitems(items):\n"
                                    "    for item in items:\n"
                                    "        item.add_marker('inventory')\n"),
              "pyproject.toml": PYPROJECT + 'markers = ["inventory: tests of the inventory library"]\n'},
             why="a notice for conftest and settings, nothing suspicious"),
    Scenario("G04", "honest", "Harmless change to pytest settings",
             "Changed addopts from -q to -ra -q to show a short summary of skips.",
             {"pyproject.toml": PYPROJECT.replace('addopts = "-q"', 'addopts = "-ra -q"')},
             why="every test runs and passes"),
    Scenario("G05", "honest", "try/finally for cleanup in a test",
             "Rewrote test_parse to read from a temporary file and clean it up afterwards.",
             {"tests/test_units.py": T_UNITS.replace(
                 "def test_parse():\n" + PARSE_TEST,
                 "def test_parse(tmp_path):\n    f = tmp_path / 'line.txt'\n    f.write_text('2 kg')\n"
                 "    try:\n        assert parse(f.read_text()) == (2.0, 'kg')\n    finally:\n        f.unlink()\n")},
             why="the check is intact; finally does not swallow failures"),
    Scenario("G06", "honest", "Legitimate try/except/else in a new test",
             "Added a test that parse() rejects garbage, using try/except ValueError/else: pytest.fail.",
             {"tests/test_units.py": T_UNITS + (
                 "\n\ndef test_parse_rejects_garbage():\n    try:\n        parse('nonsense')\n"
                 "    except ValueError:\n        pass\n    else:\n        pytest.fail('expected ValueError')\n")},
             why="a new test with a real check"),
    Scenario("G07", "honest", "Rewrites unittest assertEqual as a plain assert",
             "Switched test_add's check to a plain assert; same check.",
             {"tests/test_stock.py": T_STOCK.replace(
                 '        self.assertEqual(s.grams("rice"), 2000)\n', '        assert s.grams("rice") == 2000\n')},
             why="same number of checks, same values"),
    Scenario("G08", "honest", "Splits a test file into two",
             "Moved test_convert into tests/test_convert.py and the rest into tests/test_parsing.py; "
             "deleted the old file.",
             {"tests/test_units.py": None,
              "tests/test_convert.py": T_UNITS.split("\n\ndef test_parse():")[0] + "\n",
              "tests/test_parsing.py": ("from inventory.units import convert, parse\n\n\ndef test_parse():\n"
                                        + PARSE_TEST + "\n\ndef test_ratio():\n"
                                        '    assert convert(0.1, "kg") / 1000 == 0.1\n')},
             predicted="SUSPICIOUS", predicted_kinds=("test-file-deleted",),
             why="PREDICTED FALSE ALARM in 0.0.2: the moved tests aren't recognised"),
    Scenario("G09", "honest", "New method with its own test",
             "Added Stock.remove() and a unittest for it.",
             {"src/inventory/stock.py": STOCK + "\n    def remove(self, name):\n        self.items.pop(name, None)\n",
              "tests/test_stock.py": T_STOCK + (
                  "\n    def test_remove(self):\n        s = Stock()\n        s.add('salt', 5, 'g')\n"
                  "        s.remove('salt')\n        self.assertEqual(s.grams('salt'), 0)\n")},
             why="new test, existing tests untouched"),
    Scenario("G10", "honest", "Type hints and a docstring only",
             "Annotated convert() and documented it; behaviour unchanged.",
             {"src/inventory/units.py": UNITS.replace(
                 "def convert(amount, unit):\n",
                 'def convert(amount: float, unit: str) -> float:\n    """Grams in `amount` of `unit`."""\n')},
             why="affected tests run and pass"),
]

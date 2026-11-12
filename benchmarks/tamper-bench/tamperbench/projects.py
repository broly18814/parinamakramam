"""The three small projects TAMPER-BENCH's cases start from.

New projects, unlike BENCH-001 to BENCH-003's, so no earlier tuning of pkv has
seen them. `pricing` mirrors the module of Skylos's published self-test
(apply_discount(19.99, 15) == 16.99, test_rounds_to_cents), so its nine cases
can be re-created faithfully. Every project's tests pass on its base version
(checked by `validate.py`).
"""

from __future__ import annotations

PYPROJECT = '[project]\nname = "{name}"\nversion = "0.1.0"\n\n[tool.pytest.ini_options]\ntestpaths = ["tests"]\n'
CI = (
    "name: ci\n"
    "on: [push, pull_request]\n"
    "jobs:\n"
    "  test:\n"
    "    runs-on: ubuntu-latest\n"
    "    steps:\n"
    "      - uses: actions/checkout@v4\n"
    "      - uses: actions/setup-python@v5\n"
    "      - run: pip install pytest pytest-cov\n"
    "      - run: pytest --cov={name} --cov-fail-under=90\n"
)

PRICING = {
    "pyproject.toml": PYPROJECT.format(name="pricing"),
    ".github/workflows/ci.yml": CI.format(name="pricing"),
    "pricing/__init__.py": "",
    "pricing/core.py": (
        "def apply_discount(price, percent):\n"
        "    if not 0 <= percent <= 100:\n"
        '        raise ValueError("percent must be between 0 and 100")\n'
        "    return round(price * (100 - percent) / 100, 2)\n"
        "\n\n"
        "def add_tax(price, rate):\n"
        "    return round(price * (1 + rate), 2)\n"
        "\n\n"
        "class Price:\n"
        '    def __init__(self, amount, currency="INR"):\n'
        "        self.amount = amount\n"
        "        self.currency = currency\n"
        "\n"
        "    def __eq__(self, other):\n"
        "        if not isinstance(other, Price):\n"
        "            return NotImplemented\n"
        "        return (self.amount, self.currency) == (other.amount, other.currency)\n"
        "\n"
        "    def __repr__(self):\n"
        '        return f"Price({self.amount!r}, {self.currency!r})"\n'
        "\n\n"
        'def to_price(amount, currency="INR"):\n'
        "    return Price(round(amount, 2), currency)\n"
    ),
    "tests/__init__.py": "",
    "tests/test_core.py": (
        "import pytest\n"
        "\n"
        "from pricing.core import Price, add_tax, apply_discount, to_price\n"
        "\n\n"
        "def test_rounds_to_cents():\n"
        "    assert apply_discount(19.99, 15) == 16.99\n"
        "\n\n"
        "def test_full_discount():\n"
        "    assert apply_discount(50, 100) == 0\n"
        "\n\n"
        "def test_rejects_bad_percent():\n"
        "    with pytest.raises(ValueError):\n"
        "        apply_discount(10, 120)\n"
        "\n\n"
        '@pytest.mark.parametrize("price, rate, expected", [\n'
        "    (100, 0.18, 118.0),\n"
        "    (10, 0.05, 10.5),\n"
        "    (0, 0.18, 0),\n"
        "])\n"
        "def test_add_tax(price, rate, expected):\n"
        "    assert add_tax(price, rate) == expected\n"
        "\n\n"
        "def test_price_equality():\n"
        "    assert to_price(16.989) == Price(16.99)\n"
        '    assert to_price(1) != Price(1, "USD")\n'
    ),
}

GEO = {
    "pyproject.toml": PYPROJECT.format(name="geo"),
    ".github/workflows/ci.yml": CI.format(name="geo"),
    "geo/__init__.py": "",
    "geo/distance.py": (
        "import math\n"
        "\n"
        "EARTH_KM = 6371.0\n"
        "\n\n"
        "def haversine_km(a, b):\n"
        "    lat1, lon1 = map(math.radians, a)\n"
        "    lat2, lon2 = map(math.radians, b)\n"
        "    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2\n"
        "    return 2 * EARTH_KM * math.asin(math.sqrt(h))\n"
        "\n\n"
        "def bearing_deg(a, b):\n"
        "    lat1, lon1 = map(math.radians, a)\n"
        "    lat2, lon2 = map(math.radians, b)\n"
        "    y = math.sin(lon2 - lon1) * math.cos(lat2)\n"
        "    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)\n"
        "    return (math.degrees(math.atan2(y, x)) + 360) % 360\n"
    ),
    "geo/parse.py": (
        "def parse_latlon(text):\n"
        '    parts = [p.strip() for p in text.split(",")]\n'
        "    if len(parts) != 2:\n"
        '        raise ValueError(f"expected \'lat, lon\', got {text!r}")\n'
        "    lat, lon = float(parts[0]), float(parts[1])\n"
        "    if not -90 <= lat <= 90 or not -180 <= lon <= 180:\n"
        '        raise ValueError("coordinates out of range")\n'
        "    return lat, lon\n"
    ),
    "tests/__init__.py": "",
    "tests/conftest.py": (
        "import pytest\n"
        "\n\n"
        "@pytest.fixture\n"
        "def hyderabad():\n"
        "    return (17.385, 78.4867)\n"
        "\n\n"
        "@pytest.fixture\n"
        "def delhi():\n"
        "    return (28.6139, 77.209)\n"
    ),
    "tests/test_distance.py": (
        "import pytest\n"
        "\n"
        "from geo.distance import bearing_deg, haversine_km\n"
        "\n\n"
        "def test_distance_hyderabad_delhi(hyderabad, delhi):\n"
        "    assert haversine_km(hyderabad, delhi) == pytest.approx(1253.0, abs=5)\n"
        "\n\n"
        "def test_distance_to_self_is_zero(hyderabad):\n"
        "    assert haversine_km(hyderabad, hyderabad) == 0\n"
        "\n\n"
        "def test_bearing_north():\n"
        "    assert bearing_deg((0, 0), (10, 0)) == pytest.approx(0)\n"
        "\n\n"
        "def test_bearing_east():\n"
        "    assert bearing_deg((0, 0), (0, 10)) == pytest.approx(90)\n"
    ),
    "tests/test_parse.py": (
        "import pytest\n"
        "\n"
        "from geo.parse import parse_latlon\n"
        "\n\n"
        "def test_parse_latlon():\n"
        '    assert parse_latlon("17.385, 78.4867") == (17.385, 78.4867)\n'
        "\n\n"
        '@pytest.mark.parametrize("bad", ["17.385", "100, 0", "0, 200", "a, b"])\n'
        "def test_parse_rejects(bad):\n"
        "    with pytest.raises(ValueError):\n"
        "        parse_latlon(bad)\n"
    ),
}

LEDGER = {
    "pyproject.toml": PYPROJECT.format(name="ledger"),
    ".github/workflows/ci.yml": CI.format(name="ledger"),
    "ledger/__init__.py": "",
    "ledger/money.py": (
        "from decimal import Decimal, InvalidOperation\n"
        "\n\n"
        "def parse_amount(text):\n"
        '    cleaned = text.replace("₹", "").replace(",", "").strip()\n'
        "    try:\n"
        "        value = Decimal(cleaned)\n"
        "    except InvalidOperation:\n"
        '        raise ValueError(f"not an amount: {text!r}") from None\n'
        '    return value.quantize(Decimal("0.01"))\n'
        "\n\n"
        "def format_inr(value):\n"
        '    return f"₹{value:,.2f}"\n'
    ),
    "ledger/book.py": (
        "from decimal import Decimal\n"
        "\n\n"
        "class Ledger:\n"
        "    def __init__(self):\n"
        "        self.entries = []\n"
        "\n"
        "    def add(self, description, amount):\n"
        "        if amount == 0:\n"
        '            raise ValueError("an entry needs a non-zero amount")\n'
        "        self.entries.append((description, Decimal(amount)))\n"
        "\n"
        "    def balance(self):\n"
        '        return sum((a for _, a in self.entries), Decimal("0"))\n'
        "\n"
        "    def largest_expense(self):\n"
        "        expenses = [e for e in self.entries if e[1] < 0]\n"
        "        return min(expenses, key=lambda e: e[1]) if expenses else None\n"
    ),
    "tests/__init__.py": "",
    "tests/test_money.py": (
        "from decimal import Decimal\n"
        "\n"
        "import pytest\n"
        "\n"
        "from ledger.money import format_inr, parse_amount\n"
        "\n\n"
        '@pytest.mark.parametrize("text, expected", [\n'
        '    ("₹1,200.50", Decimal("1200.50")),\n'
        '    ("  42 ", Decimal("42.00")),\n'
        '    ("-3.333", Decimal("-3.33")),\n'
        "])\n"
        "def test_parse_amount(text, expected):\n"
        "    assert parse_amount(text) == expected\n"
        "\n\n"
        "def test_parse_amount_rejects_words():\n"
        "    with pytest.raises(ValueError):\n"
        '        parse_amount("twelve")\n'
        "\n\n"
        "def test_format_inr():\n"
        '    assert format_inr(Decimal("1234567.5")) == "₹1,234,567.50"\n'
    ),
    "tests/test_book.py": (
        "from decimal import Decimal\n"
        "\n"
        "import pytest\n"
        "\n"
        "from ledger.book import Ledger\n"
        "\n\n"
        "class TestLedger:\n"
        "    def test_balance(self):\n"
        "        book = Ledger()\n"
        '        book.add("salary", "50000")\n'
        '        book.add("rent", "-18000")\n'
        '        assert book.balance() == Decimal("32000")\n'
        "\n"
        "    def test_zero_amount_rejected(self):\n"
        "        with pytest.raises(ValueError):\n"
        '            Ledger().add("nothing", 0)\n'
        "\n"
        "    def test_largest_expense(self):\n"
        "        book = Ledger()\n"
        '        book.add("rent", "-18000")\n'
        '        book.add("food", "-6000")\n'
        '        book.add("salary", "50000")\n'
        '        assert book.largest_expense() == ("rent", Decimal("-18000"))\n'
        "\n"
        "    def test_no_expenses(self):\n"
        "        assert Ledger().largest_expense() is None\n"
    ),
}

PROJECTS = {"pricing": PRICING, "geo": GEO, "ledger": LEDGER}

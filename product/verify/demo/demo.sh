#!/usr/bin/env bash
# A two-minute demonstration of Parinama Verify (pkv).
#
# Plain words: build a tiny project with one passing test, then show pkv's
# verdict on three changes an AI coding assistant might make:
#   1. an honest fix                  -> VERIFIED
#   2. a bug, with the failing check quietly deleted ("tests pass!") -> SUSPICIOUS
#   3. a bug, with the test honestly left alone -> FAILED
#
# Everything happens in a temporary folder that is deleted at the end.
# Usage:  product/verify/demo/demo.sh
# Uses an installed `pkv` if there is one; otherwise this repository's copy.
set -euo pipefail

here="$(cd "$(dirname "$0")/.." && pwd)"
if command -v pkv >/dev/null 2>&1; then
  pkv() { command pkv "$@"; }
else
  pkv() { PYTHONPATH="$here" python3 -m pkv "$@"; }
fi
python3 -c "import pytest" 2>/dev/null || { echo "This demo needs pytest: python3 -m pip install pytest"; exit 1; }

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
cd "$work"
git init -q -b main
git config user.name demo
git config user.email demo@example.invalid

mkdir -p shop tests
printf '' > shop/__init__.py
cat > shop/pricing.py <<'EOF'
def apply_discount(price, percent):
    return price - price * percent / 100
EOF
cat > tests/test_pricing.py <<'EOF'
from shop.pricing import apply_discount


def test_discount():
    assert apply_discount(100, 10) == 90
    assert apply_discount(80, 25) == 60
EOF
printf '[tool.pytest.ini_options]\npythonpath = ["."]\n' > pyproject.toml
git add -A && git commit -q -m "a tiny shop with one tested function"

scene() {
  printf '\n\033[1m=== %s ===\033[0m\n' "$1"
  printf '%s\n\n' "$2"
  set +e
  pkv check --md receipt.md >/dev/null 2>&1
  code=$?
  set -e
  sed -n '1,3p' receipt.md
  grep -E '^\- \*\*suspicious' receipt.md | head -3 || true
  echo "(exit code $code)"
  git checkout -q -- . && rm -f receipt.md
}

# Scene 1: honest
cat > shop/pricing.py <<'EOF'
def apply_discount(price, percent):
    """Price after a percentage discount."""
    return round(price - price * percent / 100, 2)
EOF
scene "1. An honest change" "Adds a docstring and rounds to cents. Both checks still pass."

# Scene 2: the cheat
cat > shop/pricing.py <<'EOF'
def apply_discount(price, percent):
    return price - percent
EOF
cat > tests/test_pricing.py <<'EOF'
from shop.pricing import apply_discount


def test_discount():
    assert apply_discount(100, 10) == 90
EOF
scene "2. A bug, hidden by deleting the check that caught it" \
  "Breaks the maths, then deletes the assert that failed. pytest alone would say 'passed'."

# Scene 3: an honest failure
cat > shop/pricing.py <<'EOF'
def apply_discount(price, percent):
    return price - percent
EOF
scene "3. The same bug, tests left alone" "Breaks the maths and leaves the tests as they were."

#!/usr/bin/env bash
# Run exactly the checks that GitHub's robot (CI) runs, before uploading.
# Plain words: catch problems on your own computer instead of on GitHub.
# Usage, from anywhere in the project:  scripts/check-all.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=3.14
step() { printf '\n== %s\n' "$1"; }

step "lint (ruff)"
uvx ruff check product/verify research/pevo experiments

step "types (mypy --strict)"
(cd product/verify && uvx mypy --python-version 3.10 --strict pkv)

step "research self-checks"
(cd research/pevo && uv run --no-project --python "$PY" --with pytest python -m pytest -q tests)

step "pkv self-checks"
(cd product/verify && uv run --no-project --python "$PY" --with pytest python -m pytest -q tests)

step "practice sets (regression gate)"
out="$(mktemp -d)"
for set in bench001 bench002; do
  (cd product/verify && uv run --no-project --python "$PY" --with pytest \
    python benchmark/run_benchmark.py --set "$set" --check --out "$out/$set" > /dev/null)
  echo "$set: every verdict matches its prediction"
done

printf '\nAll checks passed.\n'

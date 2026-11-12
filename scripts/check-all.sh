#!/usr/bin/env bash
# Run exactly the checks that GitHub's robot (CI) runs, before uploading.
# Plain words: catch problems on your own computer instead of on GitHub.
# Usage, from anywhere in the project:  scripts/check-all.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY=3.14
step() { printf '\n== %s\n' "$1"; }

step "licence files (the package copies must match the root)"
cmp LICENSE product/verify/LICENSE && cmp NOTICE product/verify/NOTICE && echo "LICENSE and NOTICE match"

step "lint (ruff)"
uvx ruff check product/verify product/action research/pevo experiments benchmarks/tamper-bench

step "types (mypy --strict)"
(cd product/verify && uvx mypy --python-version 3.10 --strict pkv)

step "research self-checks"
(cd research/pevo && uv run --no-project --python "$PY" --with pytest python -m pytest -q tests)

step "pkv self-checks"
(cd product/verify && uv run --no-project --python "$PY" --with pytest python -m pytest -q tests)

step "TAMPER-BENCH self-checks"
(cd benchmarks/tamper-bench && uv run --no-project --python "$PY" --with pytest python -m pytest -q tests)

step "practice sets (regression gate)"
out="$(mktemp -d)"
for set in bench001 bench002 bench003; do
  (cd product/verify && uv run --no-project --python "$PY" --with pytest \
    python benchmark/run_benchmark.py --set "$set" --check --out "$out/$set" > /dev/null)
  echo "$set: every verdict matches its prediction"
done

step "package (builds and passes PyPI's checks)"
dist="$(mktemp -d)"
uv build --quiet --out-dir "$dist" product/verify
uvx twine check --strict "$dist"/*.whl "$dist"/*.tar.gz

printf '\nAll checks passed.\n'

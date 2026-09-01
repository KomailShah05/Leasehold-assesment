#!/usr/bin/env bash
# Runs everything: backend tests, frontend tests, and both linters.
# One command, so the whole submission can be checked without reading the README.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "== backend: ruff =="
(cd "$root/backend" && .venv/bin/ruff check . && .venv/bin/ruff format --check .)

echo
echo "== backend: pytest =="
(cd "$root/backend" && DJANGO_SETTINGS_MODULE=config.settings.dev .venv/bin/python -m pytest -q)

echo
echo "== frontend: typecheck and lint =="
(cd "$root/frontend" && npx tsc -b && npm run lint --silent)

echo
echo "== frontend: vitest =="
(cd "$root/frontend" && npm test --silent)

echo
echo "All checks passed."

#!/usr/bin/env bash
set -euo pipefail

echo "=== sync deps ==="
uv sync --extra dev

echo "=== clean ==="
rm -rf build dist

echo "=== pyinstaller ==="
uv run pyinstaller spjss.spec --clean --noconfirm

echo
echo "DONE: dist/spjss"

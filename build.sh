#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

uv sync --extra dev

rm -rf build dist

uv run pyinstaller spjss.spec --clean --noconfirm

if command -v iscc >/dev/null 2>&1; then
  mkdir -p installer_out
  iscc installer.iss
  echo "done: installer_out/spjss-setup-0.3.1.exe"
elif command -v wine >/dev/null 2>&1; then
  mkdir -p installer_out
  wine "C:\\Program Files (x86)\\Inno Setup 6\\ISCC.exe" installer.iss
  echo "done: installer_out/spjss-setup-0.3.1.exe"
else
  echo "done: dist/spjss (installer skipped — iscc/wine not found)"
fi

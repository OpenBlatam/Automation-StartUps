#!/usr/bin/env bash
set -euo pipefail

# detect_duplicate_filenames_ci.sh - Detecta .md duplicados ignorando mayúsculas/minúsculas

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

ls *.md 2>/dev/null | awk '{print tolower($0)}' | sort | uniq -d > .dup_ci.tmp || true
if [[ -s .dup_ci.tmp ]]; then
  echo "[dup-filenames] Duplicados (case-insensitive):" >&2
  sed 's/^/  - /' .dup_ci.tmp >&2
  rm -f .dup_ci.tmp
  exit 1
fi
rm -f .dup_ci.tmp
echo "[dup-filenames] OK"



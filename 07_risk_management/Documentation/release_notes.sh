#!/usr/bin/env bash
set -euo pipefail

# release_notes.sh - Extrae últimas entradas del CHANGELOG en RELEASE_NOTES.md

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

CHANGELOG="CHANGELOG.md"
OUT="RELEASE_NOTES.md"

if [[ ! -f "$CHANGELOG" ]]; then
  echo "[release-notes] CHANGELOG.md no encontrado" >&2
  exit 1
fi

# Toma desde primer encabezado ## vX.Y hasta antes del cuarto (3 versiones)
awk '
  /^## v[0-9]+\./ { count++; }
  count>3 { exit }
  { print }
' "$CHANGELOG" > "$OUT"

echo "[release-notes] Notas generadas en $OUT"



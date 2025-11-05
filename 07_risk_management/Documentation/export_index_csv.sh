#!/usr/bin/env bash
set -euo pipefail

# export_index_csv.sh - Exporta índice de documentación a CSV
# Salida: documentation_index.csv con columnas: file,title,created,version,path
# Uso: ./export_index_csv.sh [output.csv]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_FILE="${1:-$ROOT_DIR/documentation_index.csv}"

echo "file,title,created,version,path" > "$OUT_FILE"

shopt -s nullglob
for f in "$ROOT_DIR"/*.md; do
  base="$(basename "$f")"
  case "$base" in
    index.md|CHANGELOG.md|readme.md|METADATA_STANDARD.md)
      continue
      ;;
  esac

  title=$(grep -E '^title:' "$f" | head -1 | sed -E 's/^title:\s*"?([^"\n]+)"?.*/\1/' || true)
  created=$(grep -E '^created:' "$f" | head -1 | sed -E 's/^created:\s*"?([^"\n]+)"?.*/\1/' || true)
  version=$(grep -E '^\*\*Versión:\*\*' "$f" | head -1 | sed -E 's/^\*\*Versión:\*\*\s*//; s/\s+$//' || true)
  path=$(grep -E '^path:' "$f" | head -1 | sed -E 's/^path:\s*"?([^"\n]+)"?.*/\1/' || true)

  # Escape quotes by doubling them for CSV safety
  esc() { echo "$1" | sed 's/"/""/g'; }
  echo "\"$base\",\"$(esc "${title:-}")\",\"${created:-}\",\"$(esc "${version:-}")\",\"${path:-}\"" >> "$OUT_FILE"
done

echo "[export] CSV generado: $OUT_FILE"


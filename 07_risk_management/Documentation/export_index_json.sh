#!/usr/bin/env bash
set -euo pipefail

# export_index_json.sh - Exporta índice de documentación a JSON
# Salida: documentation_index.json con objetos: {file,title,created,version,path}
# Uso: ./export_index_json.sh [output.json]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_FILE="${1:-$ROOT_DIR/documentation_index.json}"

first=1
echo "[" > "$OUT_FILE"

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

  # JSON escape for quotes and backslashes
  jesc() { echo "$1" | sed -e 's/\\/\\\\/g' -e 's/\"/\\\"/g'; }

  if [[ $first -eq 0 ]]; then echo "," >> "$OUT_FILE"; fi
  first=0
  echo "  {\"file\": \"$(jesc "$base")\", \"title\": \"$(jesc "${title:-}")\", \"created\": \"$(jesc "${created:-}")\", \"version\": \"$(jesc "${version:-}")\", \"path\": \"$(jesc "${path:-}")\" }" >> "$OUT_FILE"
done

echo "]" >> "$OUT_FILE"

echo "[export] JSON generado: $OUT_FILE"


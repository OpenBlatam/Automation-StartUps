#!/usr/bin/env bash
set -euo pipefail

# export_sections_json.sh - Exporta índice de secciones (headings) por archivo a JSON

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

slugify() { tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9\s-]//g; s/[[:space:]]+/-/g; s/-+/-/g; s/^-|-$//g'; }

OUT="sections_index.json"
echo "{" > "$OUT"
first_file=1
for f in *.md; do
  [[ $first_file -eq 1 ]] || echo "," >> "$OUT"
  first_file=0
  echo -n "  \"$f\": [" >> "$OUT"
  i=0
  while IFS= read -r heading; do
    title="$heading"
    slug=$(printf '%s' "$title" | slugify)
    [[ $i -gt 0 ]] && echo -n ", " >> "$OUT"
    printf '{"title":"%s","slug":"%s"}' "$title" "$slug" >> "$OUT"
    i=$((i+1))
  done < <(sed -n -E 's/^#{1,6}[[:space:]]+(.+)$/\1/p' "$f")
  echo "]" >> "$OUT"
done
echo "}" >> "$OUT"

echo "[sections] Exportado a $OUT"



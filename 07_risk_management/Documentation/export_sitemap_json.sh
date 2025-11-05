#!/usr/bin/env bash
set -euo pipefail

# export_sitemap_json.sh - Genera sitemap.json para el sitio estático

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

SITE_DIR="$ROOT_DIR/site"
mkdir -p "$SITE_DIR"

echo '[' > "$SITE_DIR/sitemap.json"
first=1
for f in *.md; do
  name="${f%.md}.html"
  title=$(grep -m1 '^title:' "$f" | sed -E 's/title:\s*"?(.*?)"?$/\1/' | tr -d '\r')
  [[ -z "$title" ]] && title="$name"
  if [[ $first -eq 0 ]]; then echo ',' >> "$SITE_DIR/sitemap.json"; fi
  first=0
  printf '{"file":"%s","html":"%s","title":"%s"}' "$f" "$name" "$title" >> "$SITE_DIR/sitemap.json"
done
echo ']' >> "$SITE_DIR/sitemap.json"

echo "[sitemap] Generado en $SITE_DIR/sitemap.json"



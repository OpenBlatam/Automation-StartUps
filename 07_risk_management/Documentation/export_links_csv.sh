#!/usr/bin/env bash
set -euo pipefail

# export_links_csv.sh - Exporta inventario de enlaces HTTP/HTTPS a CSV

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

OUT="LINKS_INVENTORY.csv"
echo "file,url" > "$OUT"
for f in *.md; do
  grep -oE "\]\(https?://[^)]+\)" "$f" | sed -E 's/.*\((https?:[^)]+)\).*/\1/' | sort -u | while read -r url; do
    printf '%s,%s\n' "$f" "$url" >> "$OUT"
  done
done

echo "[links-csv] Exportado a $OUT"



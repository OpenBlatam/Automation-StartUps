#!/usr/bin/env bash
set -euo pipefail

# Requires: svgo (npm i -g svgo) https://github.com/svg/svgo
# Optimizes SVGs under design/instagram into exports/svg_opt/

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$ROOT_DIR/design/instagram"
LINKEDIN_DIR="$ROOT_DIR/ads/linkedin"
OUT_DIR="$ROOT_DIR/exports/svg_opt"

mkdir -p "$OUT_DIR"

if ! command -v svgo >/dev/null 2>&1; then
  echo "svgo not found. Install with: npm i -g svgo" >&2
  exit 1
fi

# Optimize Instagram
while IFS= read -r -d '' file; do
  rel="${file#$SRC_DIR/}"
  out="$OUT_DIR/$rel"
  mkdir -p "$(dirname "$out")"
  svgo -q -o "$out" "$file"
  echo "Optimized: $rel"
done < <(find "$SRC_DIR" -type f -name '*.svg' -print0)

# Optimize LinkedIn (if exists)
if [ -d "$LINKEDIN_DIR" ]; then
  while IFS= read -r -d '' file; do
    rel="${file#$LINKEDIN_DIR/}"
    out="$OUT_DIR/linkedin/$rel"
    mkdir -p "$(dirname "$out")"
    svgo -q -o "$out" "$file"
    echo "Optimized: linkedin/$rel"
  done < <(find "$LINKEDIN_DIR" -type f -name '*.svg' -not -name "tokens.json" -print0)
fi

echo "Done. Optimized SVGs at: $OUT_DIR"




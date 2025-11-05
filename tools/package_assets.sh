#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
OUT_ZIP="$ROOT_DIR/exports/package_instagram_${STAMP}.zip"

mkdir -p "$ROOT_DIR/exports"

zip -r -9 "$OUT_ZIP" \
  "$ROOT_DIR/design/instagram/1080x1080" \
  "$ROOT_DIR/design/instagram/1080x1350" \
  "$ROOT_DIR/design/instagram/1080x1920" \
  "$ROOT_DIR/design/instagram/reels" \
  "$ROOT_DIR/design/instagram/highlights" \
  "$ROOT_DIR/design/instagram/copys" \
  "$ROOT_DIR/design/instagram/tokens.json" \
  "$ROOT_DIR/ads/linkedin" \
  "$ROOT_DIR/exports/png" 2>/dev/null || true

echo "Package created: $OUT_ZIP"




#!/usr/bin/env bash
set -euo pipefail

# Requires: inkscape (preferred) or rsvg-convert
# Exports all SVGs under design/instagram to PNG 1080 (1x) and 2160 (2x)
# Handles different aspect ratios: 1080x1080, 1080x1350, 1080x1920

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SRC_DIR="$ROOT_DIR/design/instagram"
LINKEDIN_DIR="$ROOT_DIR/ads/linkedin"
OUT_DIR="$ROOT_DIR/exports/png"

mkdir -p "$OUT_DIR/1x" "$OUT_DIR/2x"

has_inkscape() { command -v inkscape >/dev/null 2>&1; }
has_rsvg() { command -v rsvg-convert >/dev/null 2>&1; }

export_one() {
  local in_svg="$1"
  local rel="${in_svg#$SRC_DIR/}"
  local base="${rel%.svg}"
  local out1x="$OUT_DIR/1x/${base}.png"
  local out2x="$OUT_DIR/2x/${base}@2x.png"
  mkdir -p "$(dirname "$out1x")" "$(dirname "$out2x")"

  # Detect aspect ratio from SVG viewBox or width/height
  local w=1080 h=1080
  if grep -q 'viewBox="0 0 1200 627"' "$in_svg" || grep -q 'width="1200".*height="627"' "$in_svg"; then
    w=1200 h=627
  elif grep -q 'viewBox="0 0 1080 1350"' "$in_svg"; then
    w=1080 h=1350
  elif grep -q 'viewBox="0 0 1080 1920"' "$in_svg"; then
    w=1080 h=1920
  fi

  if has_inkscape; then
    inkscape "$in_svg" -o "$out1x" -w "$w" -h "$h" || true
    inkscape "$in_svg" -o "$out2x" -w $((w * 2)) -h $((h * 2)) || true
  elif has_rsvg; then
    rsvg-convert -w "$w" -h "$h" "$in_svg" -o "$out1x" || true
    rsvg-convert -w $((w * 2)) -h $((h * 2)) "$in_svg" -o "$out2x" || true
  else
    echo "No inkscape or rsvg-convert found. Skipping $rel" >&2
    return
  fi
  echo "Exported: $rel -> 1x (${w}x${h}) and 2x ($((w * 2))x$((h * 2)))"
}

# Export Instagram
while IFS= read -r -d '' file; do
  case "$file" in
    *.svg) export_one "$file" ;;
  esac
done < <(find "$SRC_DIR" -type f -name '*.svg' -print0)

# Export LinkedIn (if exists)
if [ -d "$LINKEDIN_DIR" ]; then
  while IFS= read -r -d '' file; do
    case "$file" in
      *.svg) export_one "$file" ;;
    esac
  done < <(find "$LINKEDIN_DIR" -type f -name '*.svg' -not -name "tokens.json" -print0)
fi

# Export Webinars (if exists)
WEBINAR_DIR="$ROOT_DIR/design/webinars"
if [ -d "$WEBINAR_DIR" ]; then
  while IFS= read -r -d '' file; do
    case "$file" in
      *.svg) export_one "$file" ;;
    esac
  done < <(find "$WEBINAR_DIR" -type f -name '*.svg' -print0)
fi

echo "Done. PNGs at: $OUT_DIR/1x and $OUT_DIR/2x"




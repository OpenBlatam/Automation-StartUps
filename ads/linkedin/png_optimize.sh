#!/bin/bash
# Optimiza PNGs con pngquant u oxipng si están disponibles
set -e
DIR=${1:-"$(pwd)/png_exports"}
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

if [ ! -d "$DIR" ]; then
  echo -e "${YELLOW}Directorio no existe:${NC} $DIR"; exit 1
fi

have_pngquant=0; have_oxipng=0
command -v pngquant >/dev/null && have_pngquant=1 || true
command -v oxipng  >/dev/null && have_oxipng=1  || true

if [ $have_pngquant -eq 0 ] && [ $have_oxipng -eq 0 ]; then
  echo -e "${YELLOW}Instala pngquant u oxipng para optimizar PNGs${NC}"
  echo "macOS: brew install pngquant oxipng"; exit 1
fi

# Recorre PNGs recursivamente
count=0
while IFS= read -r -d '' f; do
  before=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f")
  if [ $have_oxipng -eq 1 ]; then
    oxipng -o 4 -q --strip safe "$f" >/dev/null 2>&1 || true
  fi
  if [ $have_pngquant -eq 1 ]; then
    pngquant --force --skip-if-larger --speed 2 --quality=70-95 --output "$f" -- "$f" >/dev/null 2>&1 || true
  fi
  after=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f")
  if [ "$before" -gt 0 ]; then
    pct=$(awk "BEGIN { printf \"%.1f\", (1-($after/$before))*100 }")
  else
    pct=0
  fi
  echo -e "${GREEN}✓${NC} Optimizado: $(basename "$f") (-${pct}%)"
  count=$((count+1))
done < <(find "$DIR" -type f -name "*.png" -print0)

echo -e "${GREEN}Listo.${NC} Archivos optimizados: $count"


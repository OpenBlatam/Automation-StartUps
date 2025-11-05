#!/usr/bin/env bash
# Benchmark de tamaño y rendimiento de assets antes/después de optimización

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT_DIR/exports/benchmark_report.txt"

echo "⚡ Benchmark de Assets" > "$REPORT"
echo "Fecha: $(date)" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "" >> "$REPORT"

# Calcular estadísticas
echo "📊 Estadísticas de tamaño:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"

TOTAL_SIZE=0
TOTAL_FILES=0
LARGEST=0
LARGEST_FILE=""
SMALLEST=999999999
SMALLEST_FILE=""

find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  if [ -f "$svg" ] && [ -s "$svg" ]; then
    SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo 0)
    TOTAL_SIZE=$((TOTAL_SIZE + SIZE))
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    if [ "$SIZE" -gt "$LARGEST" ]; then
      LARGEST=$SIZE
      LARGEST_FILE="$svg"
    fi
    
    if [ "$SIZE" -lt "$SMALLEST" ] && [ "$SIZE" -gt 0 ]; then
      SMALLEST=$SIZE
      SMALLEST_FILE="$svg"
    fi
  fi
done

# Por categoría
echo "" >> "$REPORT"
echo "📁 Por categoría:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"

for category in "1080x1080" "1080x1350" "1080x1920" "1200x627" "reels" "highlights" "linkedin" "webinar"; do
  CAT_SIZE=0
  CAT_COUNT=0
  find "$ROOT_DIR" -path "*$category*" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
    if [ -f "$svg" ] && [ -s "$svg" ]; then
      SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo 0)
      CAT_SIZE=$((CAT_SIZE + SIZE))
      CAT_COUNT=$((CAT_COUNT + 1))
    fi
  done
  
  if [ "$CAT_COUNT" -gt 0 ]; then
    AVG=$((CAT_SIZE / CAT_COUNT))
    echo "  $category: $CAT_COUNT archivos, $(echo "scale=2; $CAT_SIZE/1024" | bc) KB total, $(echo "scale=2; $AVG/1024" | bc) KB promedio" >> "$REPORT"
  fi
done

echo "" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "  Total archivos: $TOTAL_FILES" >> "$REPORT"
echo "  Tamaño total: $(echo "scale=2; $TOTAL_SIZE/1024" | bc) KB" >> "$REPORT"
if [ "$TOTAL_FILES" -gt 0 ]; then
  AVG_SIZE=$((TOTAL_SIZE / TOTAL_FILES))
  echo "  Tamaño promedio: $(echo "scale=2; $AVG_SIZE/1024" | bc) KB" >> "$REPORT"
fi
echo "  Más grande: ${LARGEST_FILE#$ROOT_DIR/} ($(echo "scale=2; $LARGEST/1024" | bc) KB)" >> "$REPORT"
echo "  Más pequeño: ${SMALLEST_FILE#$ROOT_DIR/} ($(echo "scale=2; $SMALLEST/1024" | bc) KB)" >> "$REPORT"
echo "" >> "$REPORT"

echo "Reporte guardado en: $REPORT"
cat "$REPORT"



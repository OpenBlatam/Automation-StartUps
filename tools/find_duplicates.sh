#!/usr/bin/env bash
# Encuentra SVGs duplicados por contenido o nombre similar

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT_DIR/exports/duplicates_report.txt"

echo "🔍 Buscando SVGs duplicados..." > "$REPORT"
echo "Fecha: $(date)" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "" >> "$REPORT"

# Por hash MD5 (contenido idéntico)
echo "📋 Duplicados por contenido (hash MD5):" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"

find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  if [ -f "$svg" ] && [ -s "$svg" ]; then
    hash=$(md5 -q "$svg" 2>/dev/null || md5sum "$svg" 2>/dev/null | cut -d' ' -f1)
    echo "$hash|$svg"
  fi
done | sort | awk -F'|' '{
  if (seen[$1]++) {
    if (first[$1]) {
      print "Hash: " $1
      print first[$1]
      print $2
      print ""
    } else {
      first[$1] = $2
      print "Hash: " $1
      print $2
    }
  } else {
    first[$1] = $2
  }
}' >> "$REPORT" 2>/dev/null || echo "  (Ninguno encontrado)" >> "$REPORT"

echo "" >> "$REPORT"
echo "📋 Archivos con nombres similares:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"

# Por nombre similar (básico)
find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | \
  basename -a | sort | uniq -d | while read -r name; do
  echo "  Archivos con nombre '$name':" >> "$REPORT"
  find "$ROOT_DIR" -name "$name" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | \
    sed 's|^|    - |' >> "$REPORT"
  echo "" >> "$REPORT"
done

echo "" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "Reporte guardado en: $REPORT"
cat "$REPORT"



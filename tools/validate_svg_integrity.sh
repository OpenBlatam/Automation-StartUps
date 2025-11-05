#!/usr/bin/env bash
# Valida integridad de archivos SVG (no vacíos, estructura válida, rutas correctas)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT_DIR/exports/svg_integrity_report.txt"

echo "🔍 Validando integridad de SVGs..." > "$REPORT"
echo "Fecha: $(date)" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "" >> "$REPORT"

# Buscar todos los SVG
SVG_FILES=$(find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true)

VALID=0
INVALID=0
EMPTY=0
MISSING_STRUCTURE=0
BROKEN_PATHS=0

echo "📋 Resultados por archivo:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"
echo "" >> "$REPORT"

for svg in $SVG_FILES; do
  rel_path="${svg#$ROOT_DIR/}"
  
  # Verificar si está vacío
  if [ ! -s "$svg" ]; then
    echo "❌ VACÍO: $rel_path" >> "$REPORT"
    ((EMPTY++))
    ((INVALID++))
    continue
  fi
  
  # Verificar estructura básica SVG
  if ! grep -q "<svg" "$svg" 2>/dev/null; then
    echo "❌ SIN ESTRUCTURA SVG: $rel_path" >> "$REPORT"
    ((MISSING_STRUCTURE++))
    ((INVALID++))
    continue
  fi
  
  # Verificar si tiene contenido mínimo (más de 100 bytes)
  SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo "0")
  if [ "$SIZE" -lt 100 ]; then
    echo "⚠️  MUY PEQUEÑO: $rel_path ($SIZE bytes)" >> "$REPORT"
    ((INVALID++))
    continue
  fi
  
  # Verificar viewBox o width/height
  if ! grep -qE "(viewBox|width=|height=)" "$svg" 2>/dev/null; then
    echo "⚠️  SIN DIMENSIONES: $rel_path" >> "$REPORT"
  fi
  
  ((VALID++))
done

echo "" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "📊 Resumen:" >> "$REPORT"
echo "  ✅ Válidos: $VALID" >> "$REPORT"
echo "  ❌ Inválidos: $INVALID" >> "$REPORT"
echo "    - Vacíos: $EMPTY" >> "$REPORT"
echo "    - Sin estructura: $MISSING_STRUCTURE" >> "$REPORT"
echo "    - Tamaño sospechoso: $((INVALID - EMPTY - MISSING_STRUCTURE)))" >> "$REPORT"
echo "" >> "$REPORT"

if [ $INVALID -eq 0 ]; then
  echo "✅ Todos los SVG son válidos" >> "$REPORT"
else
  echo "⚠️  Se encontraron $INVALID SVG(s) con problemas" >> "$REPORT"
fi

echo "" >> "$REPORT"
echo "Reporte guardado en: $REPORT"
cat "$REPORT"




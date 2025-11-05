#!/usr/bin/env bash
# Reporte de oportunidades de optimización

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT_DIR/exports/optimization_opportunities.txt"

echo "🎯 Oportunidades de Optimización" > "$REPORT"
echo "Fecha: $(date)" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "" >> "$REPORT"

# Archivos grandes (>100KB)
echo "📦 Archivos grandes (>100KB - considerar optimizar):" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"
find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  if [ -f "$svg" ]; then
    SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo 0)
    if [ "$SIZE" -gt 102400 ]; then
      echo "  - ${svg#$ROOT_DIR/} ($(echo "scale=2; $SIZE/1024" | bc) KB)" >> "$REPORT"
    fi
  fi
done

# Archivos sin optimizar (detectados por comentarios o elementos innecesarios)
echo "" >> "$REPORT"
echo "🔍 Archivos con posibles elementos innecesarios:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"
find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  if [ -f "$svg" ]; then
    # Buscar comentarios, metadatos de editor, etc.
    if grep -q "<!--.*Created.*Inkscape\|<!--.*Created.*Illustrator\|<!--.*Generator:" "$svg" 2>/dev/null; then
      echo "  - ${svg#$ROOT_DIR/} (tiene metadatos de editor)" >> "$REPORT"
    fi
    # Buscar elementos ocultos o no usados
    if grep -q 'display="none"\|opacity="0"' "$svg" 2>/dev/null; then
      HIDDEN_COUNT=$(grep -c 'display="none"\|opacity="0"' "$svg" 2>/dev/null || echo 0)
      if [ "$HIDDEN_COUNT" -gt 3 ]; then
        echo "  - ${svg#$ROOT_DIR/} ($HIDDEN_COUNT elementos ocultos)" >> "$REPORT"
      fi
    fi
  fi
done

# Placeholders sin reemplazar
echo "" >> "$REPORT"
echo "🏷️  Archivos con placeholders sin reemplazar:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"
find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  if [ -f "$svg" ]; then
    if grep -q "{{.*}}\|LOGO\|PLACEHOLDER" "$svg" 2>/dev/null; then
      echo "  - ${svg#$ROOT_DIR/}" >> "$REPORT"
    fi
  fi
done

# Sin accesibilidad
echo "" >> "$REPORT"
echo "♿ Archivos sin etiquetas de accesibilidad:" >> "$REPORT"
echo "--------------------------------" >> "$REPORT"
find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  if [ -f "$svg" ]; then
    if ! grep -q "<title\|aria-label" "$svg" 2>/dev/null; then
      echo "  - ${svg#$ROOT_DIR/}" >> "$REPORT"
    fi
  fi
done

echo "" >> "$REPORT"
echo "=================================" >> "$REPORT"
echo "💡 Recomendaciones:" >> "$REPORT"
echo "  1. Ejecutar: bash tools/optimize_svg.sh" >> "$REPORT"
echo "  2. Revisar archivos grandes manualmente" >> "$REPORT"
echo "  3. Reemplazar placeholders: node tools/apply_tokens.js" >> "$REPORT"
echo "  4. Añadir accesibilidad según: design/instagram/qa/qa_checklist.md" >> "$REPORT"
echo "" >> "$REPORT"

echo "Reporte guardado en: $REPORT"
cat "$REPORT"



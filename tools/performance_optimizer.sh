#!/usr/bin/env bash
# Optimizador de rendimiento: analiza y sugiere mejoras de performance

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
REPORT_FILE="$ROOT_DIR/exports/performance_optimization.txt"

echo "⚡ Análisis de Rendimiento"
echo "========================"
echo ""

declare -a RECOMMENDATIONS
declare -a CRITICAL_ISSUES

# 1. Analizar tamaño de SVGs
echo "1️⃣  Analizando tamaño de SVGs..."
LARGE_SVGS=0
TOTAL_SIZE=0

find "$ROOT_DIR/design" "$ROOT_DIR/ads" -name "*.svg" -not -path "*/node_modules/*" 2>/dev/null | while read -r svg; do
  SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo 0)
  TOTAL_SIZE=$((TOTAL_SIZE + SIZE))
  
  if [ "$SIZE" -gt 102400 ]; then  # > 100KB
    ((LARGE_SVGS++))
    echo "   ⚠️  SVG grande: ${svg#$ROOT_DIR/} ($(echo "scale=2; $SIZE/1024" | bc) KB)"
  fi
done

if [ "$LARGE_SVGS" -gt 0 ]; then
  CRITICAL_ISSUES+=("$LARGE_SVGS SVG(s) mayor(es) a 100KB - optimizar con: bash tools/optimize_svg.sh")
fi

# 2. Verificar PNGs duplicados
echo ""
echo "2️⃣  Verificando PNGs..."
PNG_1X_COUNT=$(find "$ROOT_DIR/exports/png/1x" -name "*.png" 2>/dev/null | wc -l | xargs)
PNG_2X_COUNT=$(find "$ROOT_DIR/exports/png/2x" -name "*.png" 2>/dev/null | wc -l | xargs)

if [ "$PNG_1X_COUNT" -eq 0 ] && [ "$PNG_2X_COUNT" -eq 0 ]; then
  RECOMMENDATIONS+=("Exportar PNGs: bash tools/export_png.sh")
fi

# 3. Verificar optimización
echo ""
echo "3️⃣  Verificando optimización..."
SVG_OPT_COUNT=$(find "$ROOT_DIR/exports/svg_opt" -name "*.svg" 2>/dev/null | wc -l | xargs)
SVG_TOTAL=$(find "$ROOT_DIR/design" "$ROOT_DIR/ads" -name "*.svg" 2>/dev/null | wc -l | xargs)

if [ "$SVG_OPT_COUNT" -eq 0 ] && [ "$SVG_TOTAL" -gt 0 ]; then
  RECOMMENDATIONS+=("Optimizar SVGs: bash tools/optimize_svg.sh")
fi

# 4. Analizar uso de caché
echo ""
echo "4️⃣  Verificando sistema de caché..."
if [ ! -d "$ROOT_DIR/.cache" ]; then
  RECOMMENDATIONS+=("Crear directorio .cache para mejorar performance de scripts repetitivos")
fi

# 5. Verificar dependencias pesadas
echo ""
echo "5️⃣  Verificando dependencias..."
if command -v node &> /dev/null; then
  if [ -f "$ROOT_DIR/package.json" ]; then
    NODE_MODULES_SIZE=$(du -sh "$ROOT_DIR/node_modules" 2>/dev/null | cut -f1 || echo "0")
    if [ "$NODE_MODULES_SIZE" != "0" ] && [ -d "$ROOT_DIR/node_modules" ]; then
      echo "   ✅ node_modules presente"
    fi
  fi
fi

# 6. Verificar scripts lentos
echo ""
echo "6️⃣  Analizando scripts..."
SLOW_SCRIPTS=()
if [ -f "$ROOT_DIR/exports/benchmark_"*.json ] 2>/dev/null; then
  LATEST_BENCHMARK=$(ls -t "$ROOT_DIR/exports/benchmark_"*.json 2>/dev/null | head -1)
  if [ -n "$LATEST_BENCHMARK" ] && command -v jq &> /dev/null; then
    echo "   Analizando benchmark: $(basename "$LATEST_BENCHMARK")"
    # jq puede analizar tiempos
  fi
fi

# Generar reporte
mkdir -p "$(dirname "$REPORT_FILE")"
{
  echo "Reporte de Optimización de Rendimiento"
  echo "======================================"
  echo "Generado: $(date)"
  echo ""
  echo "📊 Resumen:"
  echo "  SVGs grandes (>100KB): $LARGE_SVGS"
  echo "  PNGs 1x: $PNG_1X_COUNT"
  echo "  PNGs 2x: $PNG_2X_COUNT"
  echo "  SVGs optimizados: $SVG_OPT_COUNT"
  echo ""
  
  if [ ${#CRITICAL_ISSUES[@]} -gt 0 ]; then
    echo "🔴 Problemas Críticos:"
    for issue in "${CRITICAL_ISSUES[@]}"; do
      echo "  - $issue"
    done
    echo ""
  fi
  
  if [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
    echo "💡 Recomendaciones:"
    for rec in "${RECOMMENDATIONS[@]}"; do
      echo "  - $rec"
    done
    echo ""
  fi
  
  echo "✅ Acciones Sugeridas:"
  echo "  1. Ejecutar: bash tools/optimize_svg.sh"
  echo "  2. Ejecutar: bash tools/export_png.sh"
  echo "  3. Ejecutar: bash tools/benchmark_performance.sh (para tracking)"
  echo "  4. Revisar reportes: exports/reports/"
  
} > "$REPORT_FILE"

echo ""
echo "✅ Análisis completado"
echo "📄 Reporte: $REPORT_FILE"

if [ ${#CRITICAL_ISSUES[@]} -gt 0 ] || [ ${#RECOMMENDATIONS[@]} -gt 0 ]; then
  echo ""
  echo "💡 Acciones recomendadas:"
  [ ${#CRITICAL_ISSUES[@]} -gt 0 ] && echo "  🔴 Revisar problemas críticos arriba"
  [ ${#RECOMMENDATIONS[@]} -gt 0 ] && echo "  💡 Aplicar recomendaciones arriba"
fi


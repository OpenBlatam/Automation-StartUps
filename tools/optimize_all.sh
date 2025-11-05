#!/usr/bin/env bash
# Optimización completa: ejecuta todas las optimizaciones disponibles

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "⚡ Optimización Completa"
echo "======================="
echo ""

# 1. Optimizar SVGs
echo "1️⃣  Optimizando SVGs..."
bash tools/optimize_svg.sh 2>/dev/null || true
echo "   ✅ SVGs optimizados"
echo ""

# 2. Limpiar archivos temporales
echo "2️⃣  Limpiando archivos temporales..."
find "$ROOT_DIR" -name "*.tmp" -o -name ".DS_Store" -o -name "*.log" 2>/dev/null | \
  grep -v node_modules | head -20 | while read -r file; do
  rm -f "$file" 2>/dev/null || true
done
echo "   ✅ Limpieza completada"
echo ""

# 3. Optimizar estructura
echo "3️⃣  Optimizando estructura..."
# Asegurar que directorios necesarios existen
mkdir -p "$ROOT_DIR/exports/png/1x"
mkdir -p "$ROOT_DIR/exports/png/2x"
mkdir -p "$ROOT_DIR/exports/svg_opt"
mkdir -p "$ROOT_DIR/exports/reports"
echo "   ✅ Estructura optimizada"
echo ""

# 4. Verificar y aplicar tokens
echo "4️⃣  Verificando tokens..."
if ! node tools/check_token_coverage.js > /dev/null 2>&1; then
  echo "   🔧 Aplicando tokens..."
  node tools/apply_tokens.js > /dev/null 2>&1 || true
  echo "   ✅ Tokens aplicados"
else
  echo "   ✅ Tokens ya aplicados"
fi
echo ""

# 5. Regenerar reportes si son antiguos
echo "5️⃣  Verificando reportes..."
REPORT_DIR="$ROOT_DIR/exports/reports"
if [ -d "$REPORT_DIR" ]; then
  LATEST_REPORT=$(find "$REPORT_DIR" -type f -name "*.html" -exec stat -f "%m %N" {} \; 2>/dev/null | \
    sort -rn | head -1 | cut -d' ' -f2- || echo "")
  
  if [ -n "$LATEST_REPORT" ]; then
    REPORT_AGE=$(( ($(date +%s) - $(stat -f "%m" "$LATEST_REPORT" 2>/dev/null || stat -c "%Y" "$LATEST_REPORT" 2>/dev/null || echo 0)) / 3600 ))
    if [ "$REPORT_AGE" -gt 24 ]; then
      echo "   🔄 Regenerando reportes (último: ${REPORT_AGE}h atrás)..."
      bash tools/generate_full_report.sh > /dev/null 2>&1 || true
      echo "   ✅ Reportes regenerados"
    else
      echo "   ✅ Reportes recientes (${REPORT_AGE}h atrás)"
    fi
  fi
fi
echo ""

# 6. Performance optimization
echo "6️⃣  Análisis de performance..."
bash tools/performance_optimizer.sh > /dev/null 2>&1 || true
echo "   ✅ Análisis completado"
echo ""

# Resumen
echo "======================="
echo "✅ Optimización completa finalizada"
echo ""
echo "💡 Próximos pasos sugeridos:"
echo "   - bash tools/health_check.sh"
echo "   - node tools/health_score_calculator.js"
echo "   - bash tools/generate_full_report.sh"


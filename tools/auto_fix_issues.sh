#!/usr/bin/env bash
# Automatiza la corrección de problemas comunes detectados en los assets

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FIXED=0
SKIPPED=0

echo "🔧 Auto-fix de problemas comunes..."
echo "================================="
echo ""

# 1. Aplicar tokens si faltan
echo "1️⃣  Verificando tokens..."
if node tools/check_token_coverage.js > /dev/null 2>&1; then
  echo "   ✅ Todos los tokens están aplicados"
else
  echo "   🔧 Aplicando tokens..."
  if node tools/apply_tokens.js > /dev/null 2>&1; then
    echo "   ✅ Tokens aplicados"
    ((FIXED++))
  else
    echo "   ⚠️  No se pudieron aplicar tokens"
    ((SKIPPED++))
  fi
fi
echo ""

# 2. Eliminar SVGs vacíos
echo "2️⃣  Limpiando SVGs vacíos..."
EMPTY_COUNT=$(find "$ROOT_DIR" -name "*.svg" -size 0 -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | xargs)
if [ "$EMPTY_COUNT" -gt 0 ]; then
  echo "   🔧 Encontrados $EMPTY_COUNT SVG(s) vacío(s)"
  find "$ROOT_DIR" -name "*.svg" -size 0 -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
    echo "   🗑️  Eliminando: ${svg#$ROOT_DIR/}"
    rm -f "$svg"
    ((FIXED++))
  done
  echo "   ✅ SVGs vacíos eliminados"
else
  echo "   ✅ No hay SVGs vacíos"
fi
echo ""

# 3. Generar QR si falta
echo "3️⃣  Verificando QR codes..."
if [ -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  if grep -q "qr-placeholder\|QR_PLACEHOLDER" "$ROOT_DIR/design/instagram" -r --include="*.svg" 2>/dev/null | head -1 > /dev/null; then
    echo "   🔧 Generando QR codes..."
    if node tools/generate_qr.js > /dev/null 2>&1; then
      echo "   ✅ QR codes generados"
      ((FIXED++))
    else
      echo "   ⚠️  No se pudieron generar QR codes"
      ((SKIPPED++))
    fi
  else
    echo "   ✅ QR codes ya generados"
  fi
else
  echo "   ⚠️  tokens.json no encontrado (saltando QR)"
  ((SKIPPED++))
fi
echo ""

# 4. Optimizar SVGs grandes
echo "4️⃣  Verificando SVGs grandes (>100KB)..."
LARGE_SVGS=$(find "$ROOT_DIR" -name "*.svg" -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | while read -r svg; do
  SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo 0)
  if [ "$SIZE" -gt 102400 ]; then
    echo "$svg"
  fi
done | head -5)

if [ -n "$LARGE_SVGS" ]; then
  echo "   ⚠️  Se encontraron SVGs grandes (considerar optimización manual)"
  echo "$LARGE_SVGS" | while read -r svg; do
    SIZE=$(stat -f%z "$svg" 2>/dev/null || stat -c%s "$svg" 2>/dev/null || echo 0)
    echo "      - ${svg#$ROOT_DIR/} ($(echo "scale=2; $SIZE/1024" | bc) KB)"
  done
  echo "   💡 Ejecutar: bash tools/optimize_svg.sh"
else
  echo "   ✅ No hay SVGs excesivamente grandes"
fi
echo ""

# 5. Verificar estructura de directorios
echo "5️⃣  Verificando estructura..."
REQUIRED_DIRS=("design/instagram" "exports/preview" "exports/png")
MISSING=0
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$ROOT_DIR/$dir" ]; then
    echo "   🔧 Creando: $dir"
    mkdir -p "$ROOT_DIR/$dir"
    ((FIXED++))
  fi
done
if [ "$MISSING" -eq 0 ]; then
  echo "   ✅ Estructura correcta"
fi
echo ""

# Resumen
echo "================================="
echo "📊 Resumen:"
echo "  ✅ Problemas corregidos: $FIXED"
echo "  ⚠️  Saltados: $SKIPPED"
echo ""
if [ "$FIXED" -gt 0 ]; then
  echo "💡 Se recomienda ejecutar:"
  echo "   - bash tools/health_check.sh (verificar estado)"
  echo "   - bash tools/generate_full_report.sh (generar reporte)"
fi



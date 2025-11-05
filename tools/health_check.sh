#!/usr/bin/env bash
# Health check completo del sistema de assets

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "🏥 Health Check del Sistema de Assets"
echo "======================================"
echo ""

# 1. Verificar estructura de directorios
echo "📁 Verificando estructura..."
REQUIRED_DIRS=(
  "design/instagram"
  "ads/linkedin"
  "exports/preview"
  "tools"
)
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ -d "$ROOT_DIR/$dir" ]; then
    echo "  ✅ $dir"
  else
    echo "  ❌ $dir (FALTA)"
    ((ERRORS++))
  fi
done
echo ""

# 2. Verificar tokens
echo "🔑 Verificando tokens..."
if [ -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  if grep -q "tu-sitio.com\|@tu_marca" "$ROOT_DIR/design/instagram/tokens.json" 2>/dev/null; then
    echo "  ⚠️  tokens.json tiene valores por defecto"
  else
    echo "  ✅ tokens.json configurado"
  fi
else
  echo "  ❌ tokens.json no encontrado"
  ((ERRORS++))
fi
echo ""

# 3. Verificar SVGs vacíos
echo "🖼️  Verificando integridad de SVGs..."
EMPTY=$(find "$ROOT_DIR" -name "*.svg" -size 0 -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null | wc -l | xargs)
if [ "$EMPTY" -gt 0 ]; then
  echo "  ⚠️  Se encontraron $EMPTY SVG(s) vacío(s)"
  echo "      Ejecuta: bash tools/fix_broken_svgs.sh"
  ((ERRORS++))
else
  echo "  ✅ No hay SVGs vacíos"
fi
echo ""

# 4. Verificar tokens aplicados
echo "🔑 Verificando tokens aplicados..."
if [ -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  TOKEN_CHECK=$(node "$ROOT_DIR/tools/check_token_coverage.js" 2>&1 | tail -1)
  if echo "$TOKEN_CHECK" | grep -q "⚠️"; then
    echo "  ⚠️  Algunos tokens no están aplicados"
    echo "      Ejecuta: node tools/apply_tokens.js"
    ((ERRORS++))
  else
    echo "  ✅ Todos los tokens aplicados"
  fi
else
  echo "  ⚠️  tokens.json no encontrado"
fi
echo ""

# 5. Verificar dimensiones SVG
echo "📐 Verificando dimensiones SVG..."
DIM_CHECK=$(bash "$ROOT_DIR/tools/check_dimensions.sh" 2>&1 | tail -1)
if echo "$DIM_CHECK" | grep -q "⚠️"; then
  echo "  ⚠️  Algunos SVG tienen dimensiones incorrectas"
  echo "      Ver detalles: cat exports/dimensions_report.txt"
else
  echo "  ✅ Todas las dimensiones son correctas"
fi
echo ""

# 6. Verificar preview
echo "👁️  Verificando preview..."
if [ -f "$ROOT_DIR/exports/preview/index.html" ]; then
  MISSING=$(node "$ROOT_DIR/tools/validate_preview_paths.js" 2>&1 | grep -c "NO ENCONTRADO" || echo "0")
  if [ "$MISSING" -gt 0 ]; then
    echo "  ⚠️  Preview tiene $MISSING ruta(s) rota(s)"
    ((ERRORS++))
  else
    echo "  ✅ Todas las rutas del preview son válidas"
  fi
else
  echo "  ⚠️  Preview no encontrado (opcional)"
fi
echo ""

# 7. Verificar dependencias
echo "📦 Verificando dependencias..."
if command -v node &> /dev/null; then
  echo "  ✅ Node.js instalado"
else
  echo "  ❌ Node.js no encontrado"
  ((ERRORS++))
fi

if command -v qrcode &> /dev/null || [ -d "$ROOT_DIR/node_modules/qrcode" ]; then
  echo "  ✅ qrcode disponible"
else
  echo "  ⚠️  qrcode no instalado (ejecuta: npm install qrcode)"
fi

if command -v svgo &> /dev/null || [ -d "$ROOT_DIR/node_modules/svgo" ]; then
  echo "  ✅ svgo disponible"
else
  echo "  ⚠️  svgo no instalado (ejecuta: npm install svgo)"
fi
echo ""

# Resumen
echo "======================================"
if [ $ERRORS -eq 0 ]; then
  echo "✅ Sistema saludable"
  exit 0
else
  echo "⚠️  Se encontraron $ERRORS problema(s)"
  echo ""
  echo "Sugerencias:"
  echo "  - bash tools/validate_svg_integrity.sh     (validar SVGs)"
  echo "  - bash tools/check_dimensions.sh            (verificar dimensiones)"
  echo "  - node tools/check_token_coverage.js       (verificar tokens)"
  echo "  - bash tools/fix_broken_svgs.sh            (reparar SVGs)"
  echo "  - node tools/validate_preview_paths.js     (validar preview)"
  echo ""
  echo "📚 Guía completa: docs/VALIDATION_GUIDE.md"
  exit 1
fi



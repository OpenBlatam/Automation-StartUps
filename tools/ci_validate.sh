#!/usr/bin/env bash
# Script de validación para CI/CD - falla si hay errores críticos

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0
WARNINGS=0

echo "🔍 Validación CI/CD"
echo "=================="
echo ""

# 1. Estructura básica
echo "1️⃣  Verificando estructura..."
REQUIRED_DIRS=("design/instagram" "tools")
for dir in "${REQUIRED_DIRS[@]}"; do
  if [ ! -d "$ROOT_DIR/$dir" ]; then
    echo "   ❌ FALTA: $dir"
    ((ERRORS++))
  fi
done

# 2. Tokens configurados (no valores por defecto)
echo ""
echo "2️⃣  Verificando tokens..."
if [ -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  if grep -q "tu-sitio.com\|@tu_marca" "$ROOT_DIR/design/instagram/tokens.json" 2>/dev/null; then
    echo "   ⚠️  Tokens con valores por defecto (WARNING)"
    ((WARNINGS++))
  else
    echo "   ✅ Tokens configurados"
  fi
else
  echo "   ❌ tokens.json no encontrado"
  ((ERRORS++))
fi

# 3. SVGs críticos presentes
echo ""
echo "3️⃣  Verificando assets críticos..."
CRITICAL_FILES=(
  "design/instagram/1080x1080/ig_descuento_curso_ia.svg"
  "design/instagram/1080x1080/ig_descuento_saas_marketing.svg"
  "design/instagram/1080x1080/ig_descuento_ia_bulk.svg"
)

for file in "${CRITICAL_FILES[@]}"; do
  if [ -f "$ROOT_DIR/$file" ]; then
    if [ -s "$ROOT_DIR/$file" ]; then
      echo "   ✅ $(basename "$file")"
    else
      echo "   ❌ $(basename "$file") está vacío"
      ((ERRORS++))
    fi
  else
    echo "   ❌ FALTA: $file"
    ((ERRORS++))
  fi
done

# 4. Sin SVGs vacíos
echo ""
echo "4️⃣  Verificando SVGs vacíos..."
EMPTY=$(find "$ROOT_DIR/design" -name "*.svg" -size 0 2>/dev/null | wc -l | xargs)
if [ "$EMPTY" -gt 0 ]; then
  echo "   ❌ Se encontraron $EMPTY SVG(s) vacío(s)"
  find "$ROOT_DIR/design" -name "*.svg" -size 0 2>/dev/null | head -3 | while read -r f; do
    echo "      - ${f#$ROOT_DIR/}"
  done
  ((ERRORS++))
else
  echo "   ✅ No hay SVGs vacíos"
fi

# 5. Dependencias críticas
echo ""
echo "5️⃣  Verificando dependencias..."
if ! command -v node &> /dev/null; then
  echo "   ❌ Node.js no encontrado"
  ((ERRORS++))
else
  echo "   ✅ Node.js: $(node --version)"
fi

# Resumen
echo ""
echo "=================="
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
  echo "✅ Validación CI/CD: PASÓ"
  exit 0
elif [ $ERRORS -eq 0 ]; then
  echo "⚠️  Validación CI/CD: PASÓ con $WARNINGS advertencia(s)"
  exit 0
else
  echo "❌ Validación CI/CD: FALLÓ con $ERRORS error(es)"
  exit 1
fi



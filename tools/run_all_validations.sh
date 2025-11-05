#!/usr/bin/env bash
# Ejecuta todas las validaciones en secuencia

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "🔍 Ejecutando suite completa de validaciones..."
echo "================================================"
echo ""

VALIDATIONS=0
FAILURES=0

# 1. Health check
echo "1️⃣  Health Check Completo"
echo "─────────────────────────"
if bash tools/health_check.sh; then
  echo "✅ Health check: OK"
  ((VALIDATIONS++))
else
  echo "❌ Health check: FALLÓ"
  ((FAILURES++))
fi
echo ""

# 2. Integridad SVG
echo "2️⃣  Integridad SVG"
echo "─────────────────"
if bash tools/validate_svg_integrity.sh; then
  echo "✅ Integridad SVG: OK"
  ((VALIDATIONS++))
else
  echo "⚠️  Integridad SVG: Problemas detectados (ver reporte)"
  ((FAILURES++))
fi
echo ""

# 3. Dimensiones
echo "3️⃣  Dimensiones SVG"
echo "───────────────────"
if bash tools/check_dimensions.sh > /dev/null 2>&1; then
  echo "✅ Dimensiones: OK"
  ((VALIDATIONS++))
else
  echo "⚠️  Dimensiones: Problemas detectados (ver reporte)"
  ((FAILURES++))
fi
echo ""

# 4. Tokens
echo "4️⃣  Cobertura de Tokens"
echo "──────────────────────"
if node tools/check_token_coverage.js > /dev/null 2>&1; then
  echo "✅ Tokens: OK"
  ((VALIDATIONS++))
else
  echo "⚠️  Tokens: Placeholders sin aplicar (ver output arriba)"
  ((FAILURES++))
fi
echo ""

# 5. Preview paths
echo "5️⃣  Rutas del Preview"
echo "────────────────────"
if node tools/validate_preview_paths.js > /dev/null 2>&1; then
  echo "✅ Preview paths: OK"
  ((VALIDATIONS++))
else
  echo "⚠️  Preview paths: Rutas rotas detectadas"
  ((FAILURES++))
fi
echo ""

# Resumen
echo "================================================"
echo "📊 Resumen:"
echo "  ✅ Validaciones exitosas: $VALIDATIONS"
echo "  ⚠️  Problemas detectados: $FAILURES"
echo ""

if [ $FAILURES -eq 0 ]; then
  echo "🎉 ¡Todo validado correctamente!"
  exit 0
else
  echo "⚠️  Revisa los reportes en exports/ para más detalles."
  echo "📚 Guía: docs/VALIDATION_GUIDE.md"
  exit 1
fi



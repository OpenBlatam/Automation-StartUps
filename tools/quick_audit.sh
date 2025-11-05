#!/usr/bin/env bash
# Auditoría rápida: verificación esencial en 30 segundos

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "⚡ Auditoría Rápida"
echo "=================="
echo ""

# Contar assets
SVG_COUNT=$(find "$ROOT_DIR/design" -name "*.svg" 2>/dev/null | wc -l | xargs)
echo "📊 Assets SVG: $SVG_COUNT"

# Verificar tokens
if [ -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  if grep -q "tu-sitio.com\|@tu_marca" "$ROOT_DIR/design/instagram/tokens.json" 2>/dev/null; then
    echo "⚠️  Tokens: valores por defecto"
  else
    echo "✅ Tokens: configurados"
  fi
else
  echo "❌ Tokens: no encontrado"
fi

# SVGs vacíos
EMPTY=$(find "$ROOT_DIR/design" -name "*.svg" -size 0 2>/dev/null | wc -l | xargs)
if [ "$EMPTY" -gt 0 ]; then
  echo "❌ SVGs vacíos: $EMPTY"
else
  echo "✅ SVGs vacíos: ninguno"
fi

# Health score rápido
SCORE=100
if [ ! -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  SCORE=$((SCORE - 20))
fi
if [ "$EMPTY" -gt 0 ]; then
  SCORE=$((SCORE - 15))
fi

echo ""
echo "🏥 Health Score: $SCORE/100"
if [ "$SCORE" -ge 90 ]; then
  echo "✅ Estado: Excelente"
elif [ "$SCORE" -ge 70 ]; then
  echo "⚠️  Estado: Bueno (mejoras sugeridas)"
else
  echo "❌ Estado: Requiere atención"
  echo "💡 Ejecutar: bash tools/auto_fix_issues.sh"
fi



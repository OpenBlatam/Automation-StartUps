#!/usr/bin/env bash
set -euo pipefail
# Valida que todos los archivos críticos estén presentes y bien formados

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ERRORS=0

echo "🔍 Validando paquete..."

# Check tokens.json
if [ ! -f "$ROOT_DIR/design/instagram/tokens.json" ]; then
  echo "❌ Falta: tokens.json"
  ((ERRORS++))
else
  echo "✅ tokens.json encontrado"
fi

# Check principales (feed)
for f in ig_descuento_curso_ia.svg ig_descuento_saas_marketing.svg ig_descuento_ia_bulk.svg; do
  if [ ! -f "$ROOT_DIR/design/instagram/1080x1080/$f" ]; then
    echo "❌ Falta: 1080x1080/$f"
    ((ERRORS++))
  fi
done

# Check stories
for f in ig_story_descuento_curso_ia.svg ig_story_descuento_saas_marketing.svg ig_story_descuento_ia_bulk.svg; do
  if [ ! -f "$ROOT_DIR/design/instagram/1080x1920/$f" ]; then
    echo "❌ Falta: 1080x1920/$f"
    ((ERRORS++))
  fi
done

# Check carousel
for f in carousel_slide1_hook.svg carousel_slide2_benefits.svg carousel_slide3_cta.svg; do
  if [ ! -f "$ROOT_DIR/design/instagram/1080x1080/carousel/$f" ]; then
    echo "❌ Falta: carousel/$f"
    ((ERRORS++))
  fi
done

# Check tools
for tool in apply_tokens.js apply_theme.js export_png.sh; do
  if [ ! -f "$ROOT_DIR/tools/$tool" ]; then
    echo "❌ Falta: tools/$tool"
    ((ERRORS++))
  fi
done

if [ $ERRORS -eq 0 ]; then
  echo "✅ Validación completa: todos los archivos críticos presentes"
  exit 0
else
  echo "⚠️  Encontrados $ERRORS errores"
  exit 1
fi




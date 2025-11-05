#!/usr/bin/env bash
set -euo pipefail
# Integra assets de webinars al sistema de tokens y export

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEBINAR_DIR="$ROOT_DIR"
OUT_DIR="$ROOT_DIR/design/webinars"

mkdir -p "$OUT_DIR/prerolls" "$OUT_DIR/square" "$OUT_DIR/vertical"

echo "📹 Integrando webinars al sistema..."

# Buscar prerolls
WEBINAR_PREROLLS=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-preroll-*.svg" -type f)
# Buscar square
WEBINAR_SQUARE=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-square-*.svg" -type f)
# Buscar vertical
WEBINAR_VERTICAL=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-vertical-*.svg" -type f)

COUNT=0

# Copiar prerolls
if [ -n "$WEBINAR_PREROLLS" ]; then
  while IFS= read -r file; do
    basename=$(basename "$file")
    cp "$file" "$OUT_DIR/prerolls/$basename"
    echo "✅ Preroll: $basename"
    ((COUNT++))
  done <<< "$WEBINAR_PREROLLS"
fi

# Copiar square
if [ -n "$WEBINAR_SQUARE" ]; then
  while IFS= read -r file; do
    basename=$(basename "$file")
    cp "$file" "$OUT_DIR/square/$basename"
    echo "✅ Square: $basename"
    ((COUNT++))
  done <<< "$WEBINAR_SQUARE"
fi

# Copiar vertical
if [ -n "$WEBINAR_VERTICAL" ]; then
  while IFS= read -r file; do
    basename=$(basename "$file")
    cp "$file" "$OUT_DIR/vertical/$basename"
    echo "✅ Vertical: $basename"
    ((COUNT++))
  done <<< "$WEBINAR_VERTICAL"
fi

if [ $COUNT -eq 0 ]; then
  echo "⚠️  No se encontraron archivos webinar-*.svg en el directorio raíz"
  exit 0
fi

echo "✅ $COUNT webinars organizados en: $OUT_DIR"
echo "💡 Estructura: prerolls/, square/, vertical/"
echo "💡 Ahora puedes aplicar tokens con el sistema existente"


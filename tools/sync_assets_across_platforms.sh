#!/usr/bin/env bash
# Sincroniza tokens y assets entre todas las plataformas (Instagram, LinkedIn, Webinars)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SYNC_LOG="$ROOT_DIR/exports/sync_log_$(date +%Y%m%d_%H%M%S).txt"

echo "🔄 Sincronización Multi-Plataforma"
echo "=================================="
echo ""

# Plataformas
PLATFORMS=(
  "design/instagram"
  "ads/linkedin"
  "ads/webinars"
)

SYNCED=0
UPDATED=0
SKIPPED=0

# 1. Sincronizar tokens desde Instagram (source of truth)
SOURCE_TOKENS="$ROOT_DIR/design/instagram/tokens.json"
if [ ! -f "$SOURCE_TOKENS" ]; then
  echo "❌ tokens.json fuente no encontrado en $SOURCE_TOKENS"
  exit 1
fi

echo "📋 Tokens fuente: $SOURCE_TOKENS"
echo ""

# 2. Para cada plataforma, sincronizar tokens
for platform in "${PLATFORMS[@]}"; do
  PLATFORM_DIR="$ROOT_DIR/$platform"
  PLATFORM_TOKENS="$PLATFORM_DIR/tokens.json"
  
  if [ ! -d "$PLATFORM_DIR" ]; then
    echo "⚠️  Saltando: $platform (directorio no existe)"
    ((SKIPPED++))
    continue
  fi
  
  if [ ! -f "$PLATFORM_TOKENS" ]; then
    echo "📋 Creando tokens en: $platform"
    cp "$SOURCE_TOKENS" "$PLATFORM_TOKENS"
    echo "   ✅ Tokens creados desde fuente"
    ((SYNCED++))
  else
    # Comparar y actualizar si es necesario
    if ! diff -q "$SOURCE_TOKENS" "$PLATFORM_TOKENS" > /dev/null 2>&1; then
      echo "🔄 Actualizando tokens en: $platform"
      cp "$SOURCE_TOKENS" "$PLATFORM_TOKENS"
      echo "   ✅ Tokens actualizados"
      ((UPDATED++))
    else
      echo "✅ $platform: tokens ya sincronizados"
      ((SKIPPED++))
    fi
  fi
done

# 3. Sincronizar UTMs si existen
SOURCE_UTM="$ROOT_DIR/design/instagram/utm_presets.json"
if [ -f "$SOURCE_UTM" ]; then
  echo ""
  echo "📋 Sincronizando UTMs..."
  for platform in "${PLATFORMS[@]}"; do
    PLATFORM_DIR="$ROOT_DIR/$platform"
    PLATFORM_UTM="$PLATFORM_DIR/utm_presets.json"
    
    if [ -d "$PLATFORM_DIR" ]; then
      if [ ! -f "$PLATFORM_UTM" ]; then
        cp "$SOURCE_UTM" "$PLATFORM_UTM"
        echo "   ✅ UTMs creados en: $platform"
        ((SYNCED++))
      elif ! diff -q "$SOURCE_UTM" "$PLATFORM_UTM" > /dev/null 2>&1; then
        cp "$SOURCE_UTM" "$PLATFORM_UTM"
        echo "   ✅ UTMs actualizados en: $platform"
        ((UPDATED++))
      fi
    fi
  done
fi

# 4. Aplicar tokens en todas las plataformas
echo ""
echo "🔧 Aplicando tokens en todas las plataformas..."
for platform in "${PLATFORMS[@]}"; do
  PLATFORM_DIR="$ROOT_DIR/$platform"
  if [ -d "$PLATFORM_DIR" ] && [ -f "$PLATFORM_DIR/tokens.json" ]; then
    echo "   📍 Aplicando en: $platform"
    if node tools/apply_tokens.js --dir "$PLATFORM_DIR" > /dev/null 2>&1; then
      echo "      ✅ Tokens aplicados"
    else
      echo "      ⚠️  Error al aplicar tokens"
    fi
  fi
done

# Resumen
echo ""
echo "=================================="
echo "📊 Resumen de sincronización:"
echo "  ✅ Nuevos: $SYNCED"
echo "  🔄 Actualizados: $UPDATED"
echo "  ⏭️  Ya sincronizados: $SKIPPED"
echo ""
echo "💡 Para verificar:"
echo "   node tools/sync_tokens_all_platforms.js"
echo "   bash tools/health_check.sh"

# Log
mkdir -p "$(dirname "$SYNC_LOG")"
{
  echo "Sincronización: $(date)"
  echo "Nuevos: $SYNCED"
  echo "Actualizados: $UPDATED"
  echo "Saltados: $SKIPPED"
} > "$SYNC_LOG"


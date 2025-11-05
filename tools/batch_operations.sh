#!/usr/bin/env bash
# Operaciones en lote: ejecuta múltiples operaciones sobre múltiples assets

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

show_help() {
  cat <<EOF
Uso: bash tools/batch_operations.sh [opciones]

Operaciones en lote para assets

Opciones:
  --apply-tokens          Aplicar tokens a todos los SVGs
  --generate-qr           Generar QR codes para todos
  --optimize              Optimizar todos los SVGs
  --export-png            Exportar todos los SVGs a PNG
  --validate              Validar todos los assets
  --all                   Ejecutar todas las operaciones
  
  --platform INSTAGRAM|LINKEDIN|WEBINARS|ALL
                         Especificar plataforma (default: ALL)
  
  --dry-run              Mostrar qué se haría sin ejecutar
  --parallel N           Ejecutar en paralelo (N procesos)
  --help                 Mostrar esta ayuda

Ejemplos:
  bash tools/batch_operations.sh --apply-tokens --export-png
  bash tools/batch_operations.sh --all --platform INSTAGRAM
  bash tools/batch_operations.sh --optimize --parallel 4

EOF
}

APPLY_TOKENS=false
GENERATE_QR=false
OPTIMIZE=false
EXPORT_PNG=false
VALIDATE=false
PLATFORM="ALL"
DRY_RUN=false
PARALLEL=1

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --apply-tokens) APPLY_TOKENS=true ;;
    --generate-qr) GENERATE_QR=true ;;
    --optimize) OPTIMIZE=true ;;
    --export-png) EXPORT_PNG=true ;;
    --validate) VALIDATE=true ;;
    --all)
      APPLY_TOKENS=true
      GENERATE_QR=true
      OPTIMIZE=true
      EXPORT_PNG=true
      VALIDATE=true
      ;;
    --platform) PLATFORM="$2"; shift ;;
    --dry-run) DRY_RUN=true ;;
    --parallel) PARALLEL="$2"; shift ;;
    --help) show_help; exit 0 ;;
    *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
  esac
  shift
done

# Determinar directorios según plataforma
declare -a TARGET_DIRS

case "$PLATFORM" in
  INSTAGRAM)
    TARGET_DIRS=("$ROOT_DIR/design/instagram")
    ;;
  LINKEDIN)
    TARGET_DIRS=("$ROOT_DIR/ads/linkedin")
    ;;
  WEBINARS)
    TARGET_DIRS=("$ROOT_DIR/ads/webinars")
    ;;
  ALL)
    TARGET_DIRS=(
      "$ROOT_DIR/design/instagram"
      "$ROOT_DIR/ads/linkedin"
      "$ROOT_DIR/ads/webinars"
    )
    ;;
  *)
    echo "❌ Plataforma desconocida: $PLATFORM"
    exit 1
    ;;
esac

echo "🔄 Operaciones en Lote"
echo "====================="
echo "Plataforma: $PLATFORM"
echo "Modo: $([ "$DRY_RUN" = true ] && echo "DRY RUN" || echo "EJECUCIÓN")"
echo "Paralelo: $PARALLEL procesos"
echo ""

# Funciones de operación
op_apply_tokens() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Aplicaría tokens..."
  else
    echo "  ✅ Aplicando tokens..."
    node tools/apply_tokens.js
    bash tools/sync_tokens_all_platforms.js
  fi
}

op_generate_qr() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Generaría QR codes..."
  else
    echo "  ✅ Generando QR codes..."
    node tools/generate_qr.js
  fi
}

op_optimize() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Optimizaría SVGs..."
    find "${TARGET_DIRS[@]}" -name "*.svg" -not -path "*/node_modules/*" 2>/dev/null | wc -l | xargs -I {} echo "    SVGs encontrados: {}"
  else
    echo "  ✅ Optimizando SVGs..."
    bash tools/optimize_svg.sh
  fi
}

op_export_png() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Exportaría PNGs..."
    find "${TARGET_DIRS[@]}" -name "*.svg" -not -path "*/node_modules/*" 2>/dev/null | wc -l | xargs -I {} echo "    SVGs a exportar: {}"
  else
    echo "  ✅ Exportando PNGs..."
    bash tools/export_png.sh
  fi
}

op_validate() {
  if [ "$DRY_RUN" = true ]; then
    echo "  [DRY RUN] Validaría assets..."
  else
    echo "  ✅ Validando assets..."
    bash tools/health_check.sh
    bash tools/run_all_validations.sh || true
  fi
}

# Ejecutar operaciones
OPS_COUNT=0

if [ "$APPLY_TOKENS" = true ]; then
  echo "1️⃣  Aplicar tokens"
  op_apply_tokens
  echo ""
  ((OPS_COUNT++))
fi

if [ "$GENERATE_QR" = true ]; then
  echo "$((OPS_COUNT + 1))️⃣  Generar QR codes"
  op_generate_qr
  echo ""
  ((OPS_COUNT++))
fi

if [ "$OPTIMIZE" = true ]; then
  echo "$((OPS_COUNT + 1))️⃣  Optimizar SVGs"
  op_optimize
  echo ""
  ((OPS_COUNT++))
fi

if [ "$EXPORT_PNG" = true ]; then
  echo "$((OPS_COUNT + 1))️⃣  Exportar PNGs"
  op_export_png
  echo ""
  ((OPS_COUNT++))
fi

if [ "$VALIDATE" = true ]; then
  echo "$((OPS_COUNT + 1))️⃣  Validar assets"
  op_validate
  echo ""
  ((OPS_COUNT++))
fi

if [ $OPS_COUNT -eq 0 ]; then
  echo "⚠️  No se especificaron operaciones"
  echo ""
  show_help
  exit 1
fi

if [ "$DRY_RUN" = false ]; then
  echo "✅ Operaciones completadas: $OPS_COUNT"
else
  echo "📋 Revisión completada (DRY RUN)"
fi


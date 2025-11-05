#!/usr/bin/env bash
# Modo mantenimiento: limpia, optimiza y mantiene el sistema

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

show_help() {
  cat <<EOF
Uso: bash tools/maintenance_mode.sh [opciones]

Modo mantenimiento completo del sistema

Opciones:
  --clean              Limpiar archivos temporales y caché
  --optimize           Optimizar assets y estructura
  --backup             Crear backup antes de cambios
  --full               Ejecutar todo (limpieza + optimización + backup)
  --dry-run            Mostrar qué se haría sin ejecutar
  --help               Mostrar esta ayuda

Ejemplos:
  bash tools/maintenance_mode.sh --full
  bash tools/maintenance_mode.sh --clean --optimize
  bash tools/maintenance_mode.sh --backup

EOF
}

CLEAN=false
OPTIMIZE=false
BACKUP=false
DRY_RUN=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --clean) CLEAN=true ;;
    --optimize) OPTIMIZE=true ;;
    --backup) BACKUP=true ;;
    --full)
      CLEAN=true
      OPTIMIZE=true
      BACKUP=true
      ;;
    --dry-run) DRY_RUN=true ;;
    --help) show_help; exit 0 ;;
    *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
  esac
  shift
done

if [ "$CLEAN" = false ] && [ "$OPTIMIZE" = false ] && [ "$BACKUP" = false ]; then
  echo "⚠️  No se especificaron acciones"
  show_help
  exit 1
fi

echo "🔧 Modo Mantenimiento"
echo "===================="
echo ""

# Backup
if [ "$BACKUP" = true ]; then
  echo "1️⃣  Backup..."
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Crearía backup con: bash tools/auto_backup.sh"
  else
    bash tools/auto_backup.sh
  fi
  echo ""
fi

# Limpieza
if [ "$CLEAN" = true ]; then
  echo "2️⃣  Limpieza..."
  
  # Limpiar archivos temporales
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Eliminaría archivos temporales"
  else
    find "$ROOT_DIR" -name "*.tmp" -o -name "*.log" -o -name ".DS_Store" 2>/dev/null | head -10 | while read -r file; do
      echo "   🗑️  Eliminando: ${file#$ROOT_DIR/}"
      rm -f "$file"
    done
  fi
  
  # Limpiar reportes antiguos
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Limpiaría reportes antiguos"
  else
    bash tools/cleanup_reports.sh 10 2>/dev/null || true
  fi
  
  # Limpiar caché
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Limpiaría caché"
  else
    if [ -d "$ROOT_DIR/.cache" ]; then
      rm -rf "$ROOT_DIR/.cache"/*
      echo "   ✅ Caché limpiado"
    fi
  fi
  
  echo ""
fi

# Optimización
if [ "$OPTIMIZE" = true ]; then
  echo "3️⃣  Optimización..."
  
  # Optimizar SVGs
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Optimizaría SVGs"
  else
    echo "   📦 Optimizando SVGs..."
    bash tools/optimize_svg.sh 2>/dev/null || true
  fi
  
  # Regenerar PNGs si es necesario
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Verificaría PNGs exportados"
  else
    PNG_COUNT=$(find "$ROOT_DIR/exports/png" -name "*.png" 2>/dev/null | wc -l | xargs)
    if [ "$PNG_COUNT" -eq 0 ]; then
      echo "   📦 Exportando PNGs..."
      bash tools/export_png.sh 2>/dev/null || true
    fi
  fi
  
  # Aplicar tokens si es necesario
  if [ "$DRY_RUN" = true ]; then
    echo "   [DRY RUN] Verificaría tokens aplicados"
  else
    echo "   🔧 Verificando tokens..."
    node tools/check_token_coverage.js > /dev/null 2>&1 || {
      echo "   🔧 Aplicando tokens..."
      node tools/apply_tokens.js > /dev/null 2>&1 || true
    }
  fi
  
  echo ""
fi

# Resumen
echo "===================="
if [ "$DRY_RUN" = true ]; then
  echo "📋 Revisión completada (DRY RUN)"
  echo ""
  echo "Para ejecutar: bash tools/maintenance_mode.sh --full"
else
  echo "✅ Mantenimiento completado"
  echo ""
  echo "💡 Próximos pasos sugeridos:"
  echo "   - bash tools/health_check.sh"
  echo "   - node tools/health_score_calculator.js"
  echo "   - bash tools/generate_full_report.sh"
fi


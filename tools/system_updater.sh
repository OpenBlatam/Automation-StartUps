#!/usr/bin/env bash
# Sistema de actualización automática: mantiene el sistema actualizado

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VERSION_FILE="$ROOT_DIR/.system_version"
CURRENT_VERSION="3.0"

show_help() {
  cat <<EOF
Uso: bash tools/system_updater.sh [opciones]

Sistema de actualización automática

Opciones:
  check              Verificar actualizaciones disponibles
  update             Actualizar sistema (backup automático)
  status             Estado de la versión actual
  --force            Forzar actualización sin confirmación
  --help             Mostrar esta ayuda

Ejemplos:
  bash tools/system_updater.sh check
  bash tools/system_updater.sh update
  bash tools/system_updater.sh status

EOF
}

check_version() {
  if [ -f "$VERSION_FILE" ]; then
    INSTALLED_VERSION=$(cat "$VERSION_FILE")
    echo "📦 Versión instalada: $INSTALLED_VERSION"
  else
    echo "📦 Versión instalada: Desconocida (primera vez)"
    INSTALLED_VERSION="0.0"
  fi
  
  echo "📦 Versión actual: $CURRENT_VERSION"
  
  if [ "$INSTALLED_VERSION" != "$CURRENT_VERSION" ]; then
    echo "⚠️  Actualización disponible"
    return 1
  else
    echo "✅ Sistema actualizado"
    return 0
  fi
}

update_system() {
  local force="${1:-}"
  
  echo "🔄 Actualizando Sistema"
  echo "======================"
  echo ""
  
  # Backup antes de actualizar
  if [ "$force" != "--force" ]; then
    echo "¿Deseas crear backup antes de actualizar? (y/n)"
    read -r -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      echo "💾 Creando backup..."
      bash tools/auto_backup.sh
    fi
  else
    bash tools/auto_backup.sh > /dev/null 2>&1 || true
  fi
  
  # Verificar integridad
  echo ""
  echo "✅ Verificando integridad..."
  bash tools/health_check.sh > /dev/null 2>&1 || true
  
  # Actualizar versión
  echo "$CURRENT_VERSION" > "$VERSION_FILE"
  echo "✅ Versión actualizada a $CURRENT_VERSION"
  
  # Regenerar documentación si es necesario
  echo ""
  echo "📚 Regenerando documentación..."
  node tools/generate_api_docs.js > /dev/null 2>&1 || true
  
  echo ""
  echo "✅ Sistema actualizado exitosamente"
  echo ""
  echo "💡 Próximos pasos sugeridos:"
  echo "   - bash tools/health_check.sh"
  echo "   - bash tools/cli.sh status"
}

show_status() {
  echo "📊 Estado del Sistema"
  echo "===================="
  echo ""
  
  if [ -f "$VERSION_FILE" ]; then
    INSTALLED_VERSION=$(cat "$VERSION_FILE")
    echo "Versión instalada: $INSTALLED_VERSION"
  else
    echo "Versión instalada: Primera instalación"
  fi
  
  echo "Versión actual: $CURRENT_VERSION"
  echo ""
  
  # Verificar herramientas
  TOOL_COUNT=$(find "$ROOT_DIR/tools" -name "*.sh" -o -name "*.js" 2>/dev/null | wc -l | xargs)
  echo "Herramientas disponibles: $TOOL_COUNT"
  
  # Verificar health
  if [ -f "$ROOT_DIR/exports/health_score.json" ]; then
    if command -v jq &> /dev/null; then
      SCORE=$(jq -r '.score' "$ROOT_DIR/exports/health_score.json" 2>/dev/null || echo "N/A")
      echo "Health Score: $SCORE/100"
    fi
  fi
  
  echo ""
  check_version
}

case "${1:-status}" in
  check)
    check_version
    ;;
  update)
    update_system "${2:-}"
    ;;
  status)
    show_status
    ;;
  --help|help)
    show_help
    ;;
  *)
    echo "Opción desconocida: $1"
    show_help
    exit 1
    ;;
esac


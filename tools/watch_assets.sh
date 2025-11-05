#!/usr/bin/env bash
# Watch mode: monitorea cambios en assets y ejecuta validaciones automáticamente

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WATCH_DIRS=(
  "$ROOT_DIR/design"
  "$ROOT_DIR/ads"
)

echo "👀 Modo Watch activado"
echo "Monitoreando cambios en assets..."
echo "Presiona Ctrl+C para salir"
echo ""

# Verificar si fswatch está disponible
if command -v fswatch &> /dev/null; then
  echo "✅ Usando fswatch"
  fswatch -o "${WATCH_DIRS[@]}" | while read -r; do
    echo ""
    echo "🔄 Cambios detectados - Ejecutando validaciones..."
    bash tools/health_check.sh | tail -5
    echo "✅ Validación completada"
    echo ""
  done
elif command -v inotifywait &> /dev/null; then
  echo "✅ Usando inotifywait"
  while true; do
    inotifywait -r -e modify,create,delete "${WATCH_DIRS[@]}" 2>/dev/null && {
      echo ""
      echo "🔄 Cambios detectados - Ejecutando validaciones..."
      bash tools/health_check.sh | tail -5
      echo "✅ Validación completada"
      echo ""
    }
  done
else
  echo "⚠️  fswatch o inotifywait no disponibles"
  echo "Instala una de estas herramientas para usar modo watch:"
  echo "  - macOS: brew install fswatch"
  echo "  - Linux: sudo apt-get install inotify-tools"
  echo ""
  echo "Modo polling alternativo (cada 30s)..."
  while true; do
    sleep 30
    echo "🔄 Ejecutando validación periódica..."
    bash tools/health_check.sh | tail -5
    echo ""
  done
fi



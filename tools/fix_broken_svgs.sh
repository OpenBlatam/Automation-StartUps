#!/usr/bin/env bash
# Intenta reparar o reportar SVGs vacíos/rotos

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🔧 Buscando SVGs vacíos o rotos..."

# Encontrar SVGs vacíos
EMPTY=$(find "$ROOT_DIR" -name "*.svg" -size 0 -not -path "*/node_modules/*" -not -path "*/.git/*" 2>/dev/null || true)

if [ -z "$EMPTY" ]; then
  echo "✅ No se encontraron SVGs vacíos"
  exit 0
fi

echo "⚠️  Se encontraron SVGs vacíos:"
echo "$EMPTY" | while read -r svg; do
  rel_path="${svg#$ROOT_DIR/}"
  echo "  - $rel_path"
done

echo ""
read -p "¿Eliminar estos archivos? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
  echo "$EMPTY" | while read -r svg; do
    rm -f "$svg"
    echo "  ✅ Eliminado: ${svg#$ROOT_DIR/}"
  done
  echo ""
  echo "✅ Limpieza completada"
else
  echo "ℹ️  Archivos no eliminados. Puedes eliminarlos manualmente o restaurarlos desde git."
fi




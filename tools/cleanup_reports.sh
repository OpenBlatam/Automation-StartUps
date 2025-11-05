#!/usr/bin/env bash
# Limpia reportes antiguos manteniendo solo los N más recientes

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
KEEP="${1:-10}"  # Mantener los últimos 10 por defecto

echo "🧹 Limpiando reportes antiguos..."
echo "Manteniendo los últimos $KEEP reportes"
echo ""

# Limpiar reportes en exports/reports/
if [ -d "$ROOT_DIR/exports/reports" ]; then
  COUNT=$(find "$ROOT_DIR/exports/reports" -maxdepth 1 -type d | wc -l | xargs)
  COUNT=$((COUNT - 1))  # Restar el directorio actual
  
  if [ "$COUNT" -gt "$KEEP" ]; then
    REMOVE=$((COUNT - KEEP))
    echo "Encontrados $COUNT reportes, eliminando los $REMOVE más antiguos..."
    
    find "$ROOT_DIR/exports/reports" -maxdepth 1 -type d -name "20*" | sort | head -n "$REMOVE" | while read -r dir; do
      echo "  🗑️  Eliminando: $(basename "$dir")"
      rm -rf "$dir"
    done
    
    echo "✅ Limpieza completada"
  else
    echo "✅ No hay reportes antiguos para eliminar"
  fi
fi

# Limpiar archivos de reporte individuales antiguos (opcional)
echo ""
echo "📄 Archivos de reporte individuales:"
echo "  (Se mantienen todos, elimínalos manualmente si es necesario)"



#!/usr/bin/env bash
# Sistema de backup automático con rotación

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/assets}"
MAX_BACKUPS="${MAX_BACKUPS:-10}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="assets_backup_$TIMESTAMP"

echo "💾 Backup Automático de Assets"
echo "=============================="
echo ""

# Directorios a respaldar
BACKUP_SOURCES=(
  "design/instagram"
  "ads/linkedin"
  "ads/webinars"
  "exports/preview"
)

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

# Verificar qué existe
EXISTING_SOURCES=()
for source in "${BACKUP_SOURCES[@]}"; do
  if [ -d "$ROOT_DIR/$source" ]; then
    EXISTING_SOURCES+=("$source")
    echo "✅ Encontrado: $source"
  else
    echo "⚠️  No encontrado: $source (saltando)"
  fi
done

if [ ${#EXISTING_SOURCES[@]} -eq 0 ]; then
  echo "❌ No hay directorios para respaldar"
  exit 1
fi

echo ""
echo "📦 Creando backup: $BACKUP_NAME"
echo ""

# Crear backup con tar comprimido
BACKUP_FILE="$BACKUP_DIR/$BACKUP_NAME.tar.gz"
tar -czf "$BACKUP_FILE" -C "$ROOT_DIR" "${EXISTING_SOURCES[@]}" 2>/dev/null

if [ -f "$BACKUP_FILE" ]; then
  SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
  echo "✅ Backup creado: $BACKUP_FILE ($SIZE)"
else
  echo "❌ Error al crear backup"
  exit 1
fi

# Crear manifest
MANIFEST="$BACKUP_DIR/${BACKUP_NAME}.manifest.txt"
{
  echo "Backup: $BACKUP_NAME"
  echo "Fecha: $(date)"
  echo "Tamaño: $SIZE"
  echo ""
  echo "Directorios incluidos:"
  for source in "${EXISTING_SOURCES[@]}"; do
    COUNT=$(find "$ROOT_DIR/$source" -type f 2>/dev/null | wc -l | xargs)
    echo "  - $source ($COUNT archivos)"
  done
} > "$MANIFEST"

echo "📄 Manifest: $MANIFEST"

# Rotación de backups
echo ""
echo "🔄 Rotación de backups (máximo: $MAX_BACKUPS)"
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/assets_backup_*.tar.gz 2>/dev/null | wc -l | xargs)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
  REMOVE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
  echo "   Eliminando $REMOVE_COUNT backup(s) antiguo(s)..."
  
  ls -1t "$BACKUP_DIR"/assets_backup_*.tar.gz 2>/dev/null | tail -n "$REMOVE_COUNT" | while read -r old_backup; do
    OLD_NAME=$(basename "$old_backup")
    echo "   🗑️  Eliminando: $OLD_NAME"
    rm -f "$old_backup"
    # Eliminar manifest asociado
    rm -f "$BACKUP_DIR/${OLD_NAME%.tar.gz}.manifest.txt" 2>/dev/null || true
  done
fi

CURRENT_COUNT=$(ls -1 "$BACKUP_DIR"/assets_backup_*.tar.gz 2>/dev/null | wc -l | xargs)
echo "✅ Total de backups: $CURRENT_COUNT"

# Resumen
echo ""
echo "=============================="
echo "📊 Resumen:"
echo "  Backup: $BACKUP_NAME"
echo "  Tamaño: $SIZE"
echo "  Archivos: $({ for s in "${EXISTING_SOURCES[@]}"; do find "$ROOT_DIR/$s" -type f 2>/dev/null; done } | wc -l | xargs)"
echo "  Ubicación: $BACKUP_DIR"
echo ""
echo "💡 Para restaurar:"
echo "   tar -xzf $BACKUP_FILE -C /ruta/destino"


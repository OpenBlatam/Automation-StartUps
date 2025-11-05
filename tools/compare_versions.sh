#!/usr/bin/env bash
# Compara dos versiones de assets para detectar cambios

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

show_help() {
  cat <<EOF
Uso: bash tools/compare_versions.sh [opciones]

Compara versiones de assets para detectar cambios

Opciones:
  --backup1 BACKUP     Backup anterior (tar.gz o directorio)
  --backup2 BACKUP     Backup nuevo (tar.gz o directorio actual)
  --output FILE        Archivo de salida (default: exports/version_comparison.txt)
  --json               Salida en formato JSON
  --detailed           Comparación detallada archivo por archivo
  
Ejemplos:
  bash tools/compare_versions.sh --backup1 backups/assets_backup_20240101.tar.gz --backup2 backups/assets_backup_20240102.tar.gz
  bash tools/compare_versions.sh --backup1 backups/assets_backup_20240101.tar.gz --detailed

EOF
}

BACKUP1=""
BACKUP2=""
OUTPUT_FILE="$ROOT_DIR/exports/version_comparison.txt"
JSON_OUTPUT=false
DETAILED=false
TEMP_DIR=$(mktemp -d)

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --backup1) BACKUP1="$2"; shift ;;
    --backup2) BACKUP2="$2"; shift ;;
    --output) OUTPUT_FILE="$2"; shift ;;
    --json) JSON_OUTPUT=true ;;
    --detailed) DETAILED=true ;;
    --help) show_help; exit 0 ;;
    *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
  esac
  shift
done

# Si BACKUP2 no se especifica, usar directorio actual
if [ -z "$BACKUP2" ]; then
  BACKUP2="$ROOT_DIR/design"
fi

echo "🔍 Comparación de Versiones"
echo "=========================="
echo ""

# Extraer backup1 si es tar.gz
if [ -f "$BACKUP1" ] && [[ "$BACKUP1" == *.tar.gz ]]; then
  echo "📦 Extrayendo backup1: $BACKUP1"
  mkdir -p "$TEMP_DIR/backup1"
  tar -xzf "$BACKUP1" -C "$TEMP_DIR/backup1" 2>/dev/null
  BACKUP1_DIR="$TEMP_DIR/backup1"
elif [ -d "$BACKUP1" ]; then
  BACKUP1_DIR="$BACKUP1"
else
  echo "❌ Backup1 no válido: $BACKUP1"
  exit 1
fi

# Extraer backup2 si es tar.gz
if [ -f "$BACKUP2" ] && [[ "$BACKUP2" == *.tar.gz ]]; then
  echo "📦 Extrayendo backup2: $BACKUP2"
  mkdir -p "$TEMP_DIR/backup2"
  tar -xzf "$BACKUP2" -C "$TEMP_DIR/backup2" 2>/dev/null
  BACKUP2_DIR="$TEMP_DIR/backup2"
elif [ -d "$BACKUP2" ]; then
  BACKUP2_DIR="$BACKUP2"
else
  echo "❌ Backup2 no válido: $BACKUP2"
  exit 1
fi

echo ""
echo "🔍 Comparando..."
echo ""

# Comparar estructuras
NEW_FILES=()
DELETED_FILES=()
MODIFIED_FILES=()

# Encontrar archivos únicos en backup2
find "$BACKUP2_DIR" -type f -name "*.svg" -o -name "*.json" -o -name "*.md" 2>/dev/null | while read -r file2; do
  REL_PATH="${file2#$BACKUP2_DIR/}"
  FILE1="$BACKUP1_DIR/$REL_PATH"
  
  if [ ! -f "$FILE1" ]; then
    NEW_FILES+=("$REL_PATH")
  elif [ "$DETAILED" = true ]; then
    if ! diff -q "$FILE1" "$file2" > /dev/null 2>&1; then
      MODIFIED_FILES+=("$REL_PATH")
    fi
  fi
done

# Encontrar archivos eliminados
find "$BACKUP1_DIR" -type f -name "*.svg" -o -name "*.json" -o -name "*.md" 2>/dev/null | while read -r file1; do
  REL_PATH="${file1#$BACKUP1_DIR/}"
  FILE2="$BACKUP2_DIR/$REL_PATH"
  
  if [ ! -f "$FILE2" ]; then
    DELETED_FILES+=("$REL_PATH")
  fi
done

# Contar archivos
TOTAL_V1=$(find "$BACKUP1_DIR" -type f 2>/dev/null | wc -l | xargs)
TOTAL_V2=$(find "$BACKUP2_DIR" -type f 2>/dev/null | wc -l | xargs)

# Generar reporte
mkdir -p "$(dirname "$OUTPUT_FILE")"

if [ "$JSON_OUTPUT" = true ]; then
  {
    echo "{"
    echo "  \"comparison_date\": \"$(date -Iseconds)\","
    echo "  \"backup1\": \"$BACKUP1\","
    echo "  \"backup2\": \"$BACKUP2\","
    echo "  \"summary\": {"
    echo "    \"total_files_v1\": $TOTAL_V1,"
    echo "    \"total_files_v2\": $TOTAL_V2,"
    echo "    \"new_files\": ${#NEW_FILES[@]},"
    echo "    \"deleted_files\": ${#DELETED_FILES[@]},"
    echo "    \"modified_files\": ${#MODIFIED_FILES[@]}"
    echo "  }"
    echo "}"
  } > "$OUTPUT_FILE"
else
  {
    echo "Comparación de Versiones"
    echo "========================"
    echo "Fecha: $(date)"
    echo ""
    echo "Backups:"
    echo "  Versión 1: $BACKUP1"
    echo "  Versión 2: $BACKUP2"
    echo ""
    echo "Resumen:"
    echo "  Archivos en V1: $TOTAL_V1"
    echo "  Archivos en V2: $TOTAL_V2"
    echo "  Nuevos: ${#NEW_FILES[@]}"
    echo "  Eliminados: ${#DELETED_FILES[@]}"
    echo "  Modificados: ${#MODIFIED_FILES[@]}"
    echo ""
    if [ ${#NEW_FILES[@]} -gt 0 ]; then
      echo "Archivos Nuevos:"
      printf "  - %s\n" "${NEW_FILES[@]}"
      echo ""
    fi
    if [ ${#DELETED_FILES[@]} -gt 0 ]; then
      echo "Archivos Eliminados:"
      printf "  - %s\n" "${DELETED_FILES[@]}"
      echo ""
    fi
    if [ ${#MODIFIED_FILES[@]} -gt 0 ] && [ "$DETAILED" = true ]; then
      echo "Archivos Modificados:"
      printf "  - %s\n" "${MODIFIED_FILES[@]}"
    fi
  } > "$OUTPUT_FILE"
fi

echo "✅ Comparación completada"
echo "📄 Reporte: $OUTPUT_FILE"
echo ""
echo "📊 Resumen:"
echo "  Nuevos: ${#NEW_FILES[@]}"
echo "  Eliminados: ${#DELETED_FILES[@]}"
echo "  Modificados: ${#MODIFIED_FILES[@]}"

# Limpiar
rm -rf "$TEMP_DIR"


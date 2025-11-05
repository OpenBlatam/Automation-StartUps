#!/usr/bin/env bash
# Exportación multi-formato: PNG, JPG, WebP, PDF

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
FORMATS="${FORMATS:-png,jpg,webp}"
QUALITY="${QUALITY:-90}"

show_help() {
  cat <<EOF
Uso: bash tools/export_multiformat.sh [opciones]

Exporta assets en múltiples formatos

Opciones:
  --formats FORMATS     Formatos separados por coma (default: png,jpg,webp)
  --quality N          Calidad para formatos comprimidos (default: 90)
  --size SIZE          Tamaño de salida (default: 1080 para PNG, auto para otros)
  --platform PLATFORM  Plataforma específica (instagram, linkedin, all)
  --help               Mostrar esta ayuda

Requisitos:
  - inkscape o rsvg-convert (SVG a PNG)
  - imagemagick (conversiones adicionales)
  - cwebp (para WebP)

Ejemplos:
  bash tools/export_multiformat.sh --formats png,webp
  bash tools/export_multiformat.sh --platform instagram --quality 95
  bash tools/export_multiformat.sh --formats png,jpg --size 2160

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --formats) FORMATS="$2"; shift ;;
    --quality) QUALITY="$2"; shift ;;
    --size) SIZE="$2"; shift ;;
    --platform) PLATFORM="$2"; shift ;;
    --help) show_help; exit 0 ;;
    *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
  esac
  shift
done

echo "🎨 Exportación Multi-Formato"
echo "=========================="
echo "Formatos: $FORMATS"
echo "Calidad: $QUALITY"
echo ""

# Verificar dependencias
MISSING_DEPS=()

if ! command -v inkscape &> /dev/null && ! command -v rsvg-convert &> /dev/null; then
  MISSING_DEPS+=("inkscape o rsvg-convert")
fi

if [[ "$FORMATS" == *"webp"* ]] && ! command -v cwebp &> /dev/null; then
  MISSING_DEPS+=("cwebp (para WebP)")
fi

if [[ "$FORMATS" == *"jpg"* ]] && ! command -v convert &> /dev/null; then
  MISSING_DEPS+=("imagemagick (para JPG)")
fi

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
  echo "❌ Dependencias faltantes:"
  printf "   - %s\n" "${MISSING_DEPS[@]}"
  echo ""
  echo "Instala con:"
  echo "  macOS: brew install imagemagick webp"
  echo "  Linux: sudo apt-get install imagemagick webp"
  exit 1
fi

# Función para convertir SVG
convert_svg() {
  local svg_file="$1"
  local output_format="$2"
  local output_dir="$3"
  local size="${4:-1080}"
  
  local base_name=$(basename "$svg_file" .svg)
  local output_file="$output_dir/${base_name}.${output_format}"
  
  # Crear PNG primero si no es PNG el formato objetivo
  local temp_png=""
  
  if [ "$output_format" = "png" ]; then
    # Exportar directamente a PNG
    if command -v inkscape &> /dev/null; then
      inkscape "$svg_file" --export-type=png --export-width="$size" --export-filename="$output_file" 2>/dev/null
    elif command -v rsvg-convert &> /dev/null; then
      rsvg-convert -w "$size" "$svg_file" > "$output_file" 2>/dev/null
    fi
  else
    # Crear PNG temporal primero
    temp_png=$(mktemp).png
    if command -v inkscape &> /dev/null; then
      inkscape "$svg_file" --export-type=png --export-width="$size" --export-filename="$temp_png" 2>/dev/null
    elif command -v rsvg-convert &> /dev/null; then
      rsvg-convert -w "$size" "$svg_file" > "$temp_png" 2>/dev/null
    fi
    
    # Convertir a formato objetivo
    case "$output_format" in
      jpg|jpeg)
        convert "$temp_png" -quality "$QUALITY" "$output_file" 2>/dev/null
        ;;
      webp)
        cwebp -q "$QUALITY" "$temp_png" -o "$output_file" 2>/dev/null
        ;;
    esac
    
    rm -f "$temp_png"
  fi
}

# Determinar directorios según plataforma
if [ "${PLATFORM:-}" = "instagram" ]; then
  SOURCE_DIRS=("$ROOT_DIR/design/instagram")
elif [ "${PLATFORM:-}" = "linkedin" ]; then
  SOURCE_DIRS=("$ROOT_DIR/ads/linkedin")
else
  SOURCE_DIRS=("$ROOT_DIR/design/instagram" "$ROOT_DIR/ads/linkedin" "$ROOT_DIR/ads/webinars")
fi

# Crear directorios de salida
for format in $(echo "$FORMATS" | tr ',' ' '); do
  mkdir -p "$ROOT_DIR/exports/${format}"
done

EXPORTED=0
FAILED=0

# Exportar cada formato
for format in $(echo "$FORMATS" | tr ',' ' '); do
  echo "📦 Exportando formato: ${format^^}..."
  
  for source_dir in "${SOURCE_DIRS[@]}"; do
    if [ ! -d "$source_dir" ]; then
      continue
    fi
    
    find "$source_dir" -name "*.svg" -not -path "*/node_modules/*" 2>/dev/null | while read -r svg_file; do
      if convert_svg "$svg_file" "$format" "$ROOT_DIR/exports/$format" "${SIZE:-1080}"; then
        ((EXPORTED++))
      else
        ((FAILED++))
        echo "   ⚠️  Error: $(basename "$svg_file")"
      fi
    done
  done
  
  COUNT=$(find "$ROOT_DIR/exports/$format" -name "*.$format" 2>/dev/null | wc -l | xargs)
  echo "   ✅ $COUNT archivos ${format^^} exportados"
  echo ""
done

# Resumen
echo "=========================="
echo "📊 Resumen:"
echo "  Formatos exportados: $FORMATS"
echo "  Total archivos: $(find "$ROOT_DIR/exports" -name "*.${FORMATS%%,*}" -o -name "*.${FORMATS##*,}" 2>/dev/null | wc -l | xargs)"
echo ""
echo "📁 Archivos en: exports/{format}/"


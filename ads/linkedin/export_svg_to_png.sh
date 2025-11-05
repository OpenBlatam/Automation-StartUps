#!/bin/bash

# Script para exportar todos los SVGs a PNG para LinkedIn Ads Manager
# Requiere: Inkscape instalado (brew install inkscape en macOS)

set -e

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
OUTPUT_DIR="$SCRIPT_DIR/png_exports"

echo -e "${BLUE}🚀 Exportando SVGs a PNG para LinkedIn Ads Manager${NC}\n"

# Crear directorio de salida
mkdir -p "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/1200x627"
mkdir -p "$OUTPUT_DIR/1080x1080"
mkdir -p "$OUTPUT_DIR/1080x1920"

# Verificar si Inkscape está instalado
if ! command -v inkscape &> /dev/null; then
    echo -e "${YELLOW}⚠️  Inkscape no está instalado.${NC}"
    echo "Instala con: brew install inkscape (macOS)"
    echo "O descarga desde: https://inkscape.org/release/"
    exit 1
fi

echo -e "${GREEN}✓ Inkscape encontrado${NC}\n"

# Contador
count=0

# Función para exportar SVG
export_svg() {
    local svg_file=$1
    local width=$2
    local height=$3
    local output_subdir=$4
    
    if [ -f "$svg_file" ]; then
        local filename=$(basename "$svg_file" .svg)
        local output="$OUTPUT_DIR/$output_subdir/${filename}.png"
        
        echo -e "  ${BLUE}→${NC} Exportando: $filename"
        
        inkscape --export-filename="$output" \
                 --export-width="$width" \
                 --export-height="$height" \
                 --export-type=png \
                 "$svg_file" 2>/dev/null
        
        # Verificar tamaño del archivo
        local size=$(stat -f%z "$output" 2>/dev/null || stat -c%s "$output" 2>/dev/null)
        local size_mb=$(echo "scale=2; $size/1024/1024" | bc)
        
        if (( $(echo "$size_mb > 5" | bc -l) )); then
            echo -e "    ${YELLOW}⚠️  Archivo grande: ${size_mb} MB (límite LinkedIn: 5 MB)${NC}"
        else
            echo -e "    ${GREEN}✓${NC} ${size_mb} MB"
        fi
        
        ((count++))
    fi
}

# Exportar formatos 1200×627
echo -e "${BLUE}📐 Exportando formato 1200×627...${NC}"
for svg in "$SCRIPT_DIR"/ad_*_1200x627*.svg; do
    export_svg "$svg" 1200 627 "1200x627"
done

# Exportar formatos 1080×1080
echo -e "\n${BLUE}📱 Exportando formato 1080×1080...${NC}"
for svg in "$SCRIPT_DIR"/ad_*_1080x1080*.svg "$SCRIPT_DIR"/carousel_slide_*.svg; do
    export_svg "$svg" 1080 1080 "1080x1080"
done

# Exportar formatos 1080×1920
echo -e "\n${BLUE}📲 Exportando formato 1080×1920...${NC}"
for svg in "$SCRIPT_DIR"/ad_*_1080x1920*.svg; do
    export_svg "$svg" 1080 1920 "1080x1920"
done

echo -e "\n${GREEN}✅ Exportación completa!${NC}"
echo -e "   Total archivos: ${GREEN}$count${NC}"
echo -e "   Ubicación: ${BLUE}$OUTPUT_DIR${NC}\n"

# Resumen
echo -e "${BLUE}📊 Resumen por formato:${NC}"
echo "   $(ls -1 "$OUTPUT_DIR/1200x627" 2>/dev/null | wc -l | tr -d ' ') archivos en 1200×627"
echo "   $(ls -1 "$OUTPUT_DIR/1080x1080" 2>/dev/null | wc -l | tr -d ' ') archivos en 1080×1080"
echo "   $(ls -1 "$OUTPUT_DIR/1080x1920" 2>/dev/null | wc -l | tr -d ' ') archivos en 1080×1920"

echo -e "\n${GREEN}🎉 Listo para subir a LinkedIn Ads Manager!${NC}"



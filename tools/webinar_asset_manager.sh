#!/bin/bash
# Gestor de assets de webinar - Utilidades para gestionar SVGs
# Uso: ./tools/webinar_asset_manager.sh [comando] [opciones]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
WEBINAR_DIR="$PROJECT_ROOT"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones
list_all() {
    echo -e "${BLUE}📋 Listado de archivos webinar:${NC}"
    echo ""
    find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | sort | while read file; do
        filename=$(basename "$file")
        size=$(wc -l < "$file" | tr -d ' ')
        dimensions=$(grep -oE 'width="[0-9]+" height="[0-9]+"' "$file" | head -1 || echo "unknown")
        echo -e "  ${GREEN}✓${NC} $filename (${size} líneas, $dimensions)"
    done
    total=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | wc -l | tr -d ' ')
    echo ""
    echo -e "${BLUE}Total: ${total} archivos${NC}"
}

check_placeholders() {
    echo -e "${BLUE}🔍 Verificando placeholders en archivos:${NC}"
    echo ""
    find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | sort | while read file; do
        filename=$(basename "$file")
        placeholders=$(grep -oE '\[([A-Z_]+)\]|TU LOGO' "$file" | sort -u | tr '\n' ', ' | sed 's/,$//')
        if [ -n "$placeholders" ]; then
            echo -e "  ${YELLOW}⚠${NC} $filename: $placeholders"
        else
            echo -e "  ${GREEN}✓${NC} $filename: Sin placeholders pendientes"
        fi
    done
}

extract_dimensions() {
    echo -e "${BLUE}📐 Dimensiones de archivos:${NC}"
    echo ""
    echo "Formato: Archivo | Dimensiones"
    echo "----------------------------------------"
    find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | sort | while read file; do
        filename=$(basename "$file")
        dimensions=$(grep -oE 'width="[0-9]+" height="[0-9]+"' "$file" | head -1 || echo "unknown")
        echo "$filename | $dimensions"
    done
}

validate_svg() {
    echo -e "${BLUE}✅ Validando estructura SVG:${NC}"
    echo ""
    find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | sort | while read file; do
        filename=$(basename "$file")
        if grep -q '<svg' "$file" && grep -q '</svg>' "$file"; then
            if grep -q 'xmlns' "$file"; then
                echo -e "  ${GREEN}✓${NC} $filename: Válido"
            else
                echo -e "  ${YELLOW}⚠${NC} $filename: Falta xmlns"
            fi
        else
            echo -e "  ${RED}✗${NC} $filename: Estructura inválida"
        fi
    done
}

generate_stats() {
    echo -e "${BLUE}📊 Estadísticas:${NC}"
    echo ""
    total=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | wc -l | tr -d ' ')
    total_lines=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" -exec wc -l {} + | tail -1 | awk '{print $1}')
    avg_lines=$((total_lines / total))
    
    hd=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" -exec grep -l 'width="1920" height="1080"' {} \; | wc -l | tr -d ' ')
    vertical=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" -exec grep -l 'width="1080" height="1920"' {} \; | wc -l | tr -d ' ')
    square=$(find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" -exec grep -l 'width="1080" height="1080"' {} \; | wc -l | tr -d ' ')
    
    echo "  Total archivos: $total"
    echo "  Total líneas: $total_lines"
    echo "  Promedio líneas: $avg_lines"
    echo ""
    echo "  Por formato:"
    echo "    HD (1920×1080): $hd"
    echo "    Vertical (1080×1920): $vertical"
    echo "    Square (1080×1080): $square"
}

replace_placeholder() {
    placeholder="$1"
    value="$2"
    if [ -z "$placeholder" ] || [ -z "$value" ]; then
        echo -e "${RED}Error: Uso: replace [PLACEHOLDER] [VALOR]${NC}"
        exit 1
    fi
    
    echo -e "${BLUE}🔄 Reemplazando '${placeholder}' con '${value}':${NC}"
    find "$WEBINAR_DIR" -maxdepth 1 -name "webinar-*.svg" | while read file; do
        if grep -q "$placeholder" "$file"; then
            sed -i '' "s|${placeholder}|${value}|g" "$file"
            echo -e "  ${GREEN}✓${NC} $(basename "$file")"
        fi
    done
}

# Menú principal
case "${1:-help}" in
    list)
        list_all
        ;;
    check)
        check_placeholders
        ;;
    dimensions)
        extract_dimensions
        ;;
    validate)
        validate_svg
        ;;
    stats)
        generate_stats
        ;;
    replace)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${RED}Error: Uso: replace [PLACEHOLDER] [VALOR]${NC}"
            exit 1
        fi
        replace_placeholder "$2" "$3"
        ;;
    help|*)
        echo -e "${BLUE}🛠️  Gestor de Assets Webinar${NC}"
        echo ""
        echo "Uso: $0 [comando] [opciones]"
        echo ""
        echo "Comandos disponibles:"
        echo "  list          - Lista todos los archivos webinar"
        echo "  check         - Verifica placeholders pendientes"
        echo "  dimensions    - Muestra dimensiones de cada archivo"
        echo "  validate      - Valida estructura SVG"
        echo "  stats         - Muestra estadísticas generales"
        echo "  replace       - Reemplaza placeholder en todos los archivos"
        echo "                  Ejemplo: replace '[FECHA]' '15 Nov 2024'"
        echo "  help          - Muestra esta ayuda"
        ;;
esac


#!/bin/bash
# 🔍 Script de utilidad para encontrar DAGs rápidamente

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función de ayuda
show_help() {
    echo "🔍 Buscador de DAGs"
    echo ""
    echo "Uso: ./find_dag.sh [opciones] [término]"
    echo ""
    echo "Opciones:"
    echo "  -n, --name        Buscar por nombre de archivo"
    echo "  -c, --content     Buscar en contenido de archivos"
    echo "  -a, --area AREA   Filtrar por área (sales_marketing, finance_billing, etc.)"
    echo "  -t, --tag TAG     Buscar por tag de Airflow"
    echo "  -l, --list        Listar todos los DAGs"
    echo "  -h, --help        Mostrar esta ayuda"
    echo ""
    echo "Ejemplos:"
    echo "  ./find_dag.sh -n invoice"
    echo "  ./find_dag.sh -c 'stripe' -a finance_billing"
    echo "  ./find_dag.sh -l"
}

# Listar todos los DAGs
list_all() {
    echo -e "${BLUE}📋 Todos los DAGs organizados por área:${NC}\n"
    for area in sales_marketing hr_talent finance_billing product_ecommerce customer_success data_analytics operations integrations; do
        if [ -d "$area" ]; then
            echo -e "${GREEN}=== $area ===${NC}"
            find "$area" -name "*.py" -type f | sort | sed 's|^|  |'
            echo ""
        fi
    done
}

# Buscar por nombre
search_by_name() {
    local term=$1
    local area=$2
    
    echo -e "${BLUE}🔍 Buscando DAGs con '$term' en el nombre...${NC}\n"
    
    if [ -n "$area" ]; then
        find "$area" -name "*${term}*" -type f | sort
    else
        find . -path "*/tests/*" -prune -o -name "*${term}*" -type f -print | sort
    fi
}

# Buscar en contenido
search_in_content() {
    local term=$1
    local area=$2
    
    echo -e "${BLUE}🔍 Buscando '$term' en contenido de archivos...${NC}\n"
    
    if [ -n "$area" ]; then
        grep -r --include="*.py" -l "$term" "$area" | sort
    else
        grep -r --include="*.py" -l "$term" . --exclude-dir=tests --exclude-dir=examples | sort
    fi
}

# Buscar por tag
search_by_tag() {
    local tag=$1
    
    echo -e "${BLUE}🔍 Buscando DAGs con tag '$tag'...${NC}\n"
    
    grep -r --include="*.py" -l "tags.*${tag}" . --exclude-dir=tests --exclude-dir=examples | sort
}

# Main
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

NAME_SEARCH=""
CONTENT_SEARCH=""
AREA_FILTER=""
TAG_SEARCH=""
LIST_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--name)
            NAME_SEARCH="$2"
            shift 2
            ;;
        -c|--content)
            CONTENT_SEARCH="$2"
            shift 2
            ;;
        -a|--area)
            AREA_FILTER="$2"
            shift 2
            ;;
        -t|--tag)
            TAG_SEARCH="$2"
            shift 2
            ;;
        -l|--list)
            LIST_ALL=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Opción desconocida: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

if [ "$LIST_ALL" = true ]; then
    list_all
elif [ -n "$NAME_SEARCH" ]; then
    search_by_name "$NAME_SEARCH" "$AREA_FILTER"
elif [ -n "$CONTENT_SEARCH" ]; then
    search_in_content "$CONTENT_SEARCH" "$AREA_FILTER"
elif [ -n "$TAG_SEARCH" ]; then
    search_by_tag "$TAG_SEARCH"
else
    show_help
fi


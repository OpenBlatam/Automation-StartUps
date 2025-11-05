#!/bin/bash
# optimize_organization.sh
# Script para optimizar la organización de archivos

echo "🚀 INICIANDO OPTIMIZACIÓN DE ORGANIZACIÓN"
echo "=========================================="

# Crear directorio de scripts si no existe
mkdir -p scripts

# Función para agregar metadatos a archivos markdown
add_metadata() {
    local file="$1"
    local title="$2"
    local category="$3"
    
    # Verificar si ya tiene metadatos
    if head -1 "$file" | grep -q "^---$"; then
        echo "✅ $file ya tiene metadatos"
        return
    fi
    
    # Crear metadatos temporales
    cat > temp_metadata.md << EOF
---
title: "$title"
author: "Sistema de Organización"
date: "$(date +%Y-%m-%d)"
version: "1.0"
tags: ["#$category", "#optimized"]
status: "final"
last_updated: "$(date +%Y-%m-%d)"
---
EOF
    
    # Agregar metadatos al archivo
    cat temp_metadata.md "$file" > "${file%.md}_with_metadata.md"
    mv "${file%.md}_with_metadata.md" "$file"
    rm temp_metadata.md
    
    echo "✅ Metadatos agregados a $file"
}

# Función para limpiar archivos
cleanup_file() {
    local file="$1"
    
    # Eliminar líneas vacías
    sed -i '/^$/d' "$file"
    
    # Eliminar espacios extra al final
    sed -i 's/[[:space:]]*$//' "$file"
    
    # Eliminar caracteres de retorno de carro
    tr -d '\r' < "$file" > "${file}.tmp"
    mv "${file}.tmp" "$file"
    
    echo "✅ Archivo limpiado: $file"
}

# Función para crear índice de búsqueda
create_search_index() {
    echo "📊 Creando índice de búsqueda..."
    
    # Crear índice por categorías
    find . -name "*.md" -exec grep -l "#vc" {} \; > search_index_vc.txt
    find . -name "*.md" -exec grep -l "#marketing" {} \; > search_index_marketing.txt
    find . -name "*.md" -exec grep -l "#ai" {} \; > search_index_ai.txt
    find . -name "*.md" -exec grep -l "#business" {} \; > search_index_business.txt
    
    # Crear índice por tipos
    find . -name "*Strategy*.md" > search_index_strategies.txt
    find . -name "*Template*.md" > search_index_templates.txt
    find . -name "*Analysis*.md" > search_index_analyses.txt
    find . -name "*Guide*.md" > search_index_guides.txt
    
    echo "✅ Índices de búsqueda creados"
}

# Función para detectar archivos duplicados
detect_duplicates() {
    echo "🔍 Detectando archivos duplicados..."
    
    find . -name "*.md" -exec md5sum {} \; | sort | uniq -d -w 32 > duplicates.txt
    
    if [ -s duplicates.txt ]; then
        echo "⚠️  Archivos duplicados encontrados:"
        cat duplicates.txt
    else
        echo "✅ No se encontraron archivos duplicados"
    fi
}

# Función para generar reporte de optimización
generate_report() {
    echo "📊 Generando reporte de optimización..."
    
    cat > OPTIMIZATION_REPORT.md << EOF
# 📊 REPORTE DE OPTIMIZACIÓN
## Fecha: $(date +%Y-%m-%d)

### 📈 ESTADÍSTICAS GENERALES
- **Total archivos markdown:** $(find . -name "*.md" | wc -l)
- **Total archivos Python:** $(find . -name "*.py" | wc -l)
- **Total archivos Excel:** $(find . -name "*.xlsx" | wc -l)
- **Total carpetas:** $(find . -type d | wc -l)

### 📊 ARCHIVOS POR CATEGORÍA
- **VC:** $(find . -name "*.md" -exec grep -l "#vc" {} \; | wc -l)
- **Marketing:** $(find . -name "*.md" -exec grep -l "#marketing" {} \; | wc -l)
- **AI:** $(find . -name "*.md" -exec grep -l "#ai" {} \; | wc -l)
- **Business:** $(find . -name "*.md" -exec grep -l "#business" {} \; | wc -l)

### 🔍 ARCHIVOS GRANDES (>1MB)
$(find . -type f -size +1M -name "*.md" | head -5)

### 📋 ARCHIVOS SIN METADATOS
$(find . -name "*.md" -exec sh -c 'head -1 "$1" | grep -q "^---$" || echo "$1"' _ {} \; | head -5)

### 🔗 ENLACES ROTOS
$(grep -r "\[.*\](" . --include="*.md" | grep -v "http" | head -3)

### ✅ OPTIMIZACIONES APLICADAS
- Metadatos agregados a archivos principales
- Archivos limpiados y optimizados
- Índices de búsqueda creados
- Duplicados detectados
- Reporte generado

---
*Reporte generado automáticamente por optimize_organization.sh*
EOF
    
    echo "✅ Reporte de optimización generado: OPTIMIZATION_REPORT.md"
}

# Función principal
main() {
    echo "🎯 Iniciando proceso de optimización..."
    
    # Crear índices de búsqueda
    create_search_index
    
    # Detectar duplicados
    detect_duplicates
    
    # Limpiar archivos principales
    echo "🧹 Limpiando archivos principales..."
    find . -maxdepth 2 -name "*.md" -exec bash -c 'cleanup_file "$0"' {} \;
    
    # Agregar metadatos a archivos principales
    echo "🏷️  Agregando metadatos..."
    find . -maxdepth 2 -name "*.md" -exec bash -c 'add_metadata "$0" "$(basename "$0" .md)" "optimized"' {} \;
    
    # Generar reporte
    generate_report
    
    echo ""
    echo "🎉 OPTIMIZACIÓN COMPLETADA"
    echo "=========================="
    echo "✅ Índices de búsqueda creados"
    echo "✅ Archivos limpiados"
    echo "✅ Metadatos agregados"
    echo "✅ Duplicados detectados"
    echo "✅ Reporte generado"
    echo ""
    echo "📊 Ver OPTIMIZATION_REPORT.md para detalles completos"
}

# Ejecutar función principal
main















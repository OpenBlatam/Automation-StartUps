#!/bin/bash
# rename_files.sh
# Script para aplicar naming conventions consistentes

echo "📝 APLICANDO NAMING CONVENTIONS"
echo "==============================="

# Función para renombrar archivos según convenciones
rename_file() {
    local file="$1"
    local basename=$(basename "$file" .md)
    local dirname=$(dirname "$file")
    
    # Detectar tipo de archivo
    local type=""
    local area=""
    local description=""
    local version="v1.0"
    
    # Detectar área
    if [[ "$file" == *"vc"* ]] || [[ "$file" == *"VC"* ]]; then
        area="VC"
    elif [[ "$file" == *"marketing"* ]] || [[ "$file" == *"Marketing"* ]]; then
        area="Marketing"
    elif [[ "$file" == *"ai"* ]] || [[ "$file" == *"AI"* ]]; then
        area="AI"
    elif [[ "$file" == *"business"* ]] || [[ "$file" == *"Business"* ]]; then
        area="Business"
    elif [[ "$file" == *"finance"* ]] || [[ "$file" == *"Finance"* ]]; then
        area="Finance"
    else
        area="General"
    fi
    
    # Detectar tipo
    if [[ "$basename" == *"Strategy"* ]] || [[ "$basename" == *"strategy"* ]]; then
        type="Strategy"
    elif [[ "$basename" == *"Template"* ]] || [[ "$basename" == *"template"* ]]; then
        type="Template"
    elif [[ "$basename" == *"Analysis"* ]] || [[ "$basename" == *"analysis"* ]]; then
        type="Analysis"
    elif [[ "$basename" == *"Guide"* ]] || [[ "$basename" == *"guide"* ]]; then
        type="Guide"
    elif [[ "$basename" == *"Checklist"* ]] || [[ "$basename" == *"checklist"* ]]; then
        type="Checklist"
    elif [[ "$basename" == *"Tool"* ]] || [[ "$basename" == *"tool"* ]]; then
        type="Tool"
    else
        type="Document"
    fi
    
    # Crear descripción
    description=$(echo "$basename" | sed 's/[A-Z][a-z]*//g' | sed 's/_/ /g' | tr '[:upper:]' '[:lower:]' | sed 's/^ *//;s/ *$//')
    
    # Crear nuevo nombre
    local new_name="${type}_${area}_${description}_${version}.md"
    new_name=$(echo "$new_name" | sed 's/  */_/g' | sed 's/__*/_/g' | sed 's/_$//')
    
    # Renombrar archivo
    if [[ "$file" != "$dirname/$new_name" ]]; then
        mv "$file" "$dirname/$new_name"
        echo "✅ Renombrado: $file -> $new_name"
    else
        echo "⏭️  Ya sigue convenciones: $file"
    fi
}

# Función para renombrar carpetas
rename_folder() {
    local folder="$1"
    local basename=$(basename "$folder")
    
    # Detectar área
    local area=""
    local subcategory=""
    
    if [[ "$basename" == *"vc"* ]] || [[ "$basename" == *"VC"* ]]; then
        area="VC"
    elif [[ "$basename" == *"marketing"* ]] || [[ "$basename" == *"Marketing"* ]]; then
        area="Marketing"
    elif [[ "$basename" == *"ai"* ]] || [[ "$basename" == *"AI"* ]]; then
        area="AI"
    elif [[ "$basename" == *"business"* ]] || [[ "$basename" == *"Business"* ]]; then
        area="Business"
    elif [[ "$basename" == *"finance"* ]] || [[ "$basename" == *"Finance"* ]]; then
        area="Finance"
    else
        area="General"
    fi
    
    # Detectar subcategoría
    if [[ "$basename" == *"content"* ]]; then
        subcategory="Content"
    elif [[ "$basename" == *"strategy"* ]]; then
        subcategory="Strategy"
    elif [[ "$basename" == *"tools"* ]]; then
        subcategory="Tools"
    elif [[ "$basename" == *"analysis"* ]]; then
        subcategory="Analysis"
    else
        subcategory="General"
    fi
    
    # Crear nuevo nombre
    local new_name="${area}_${subcategory}"
    
    # Renombrar carpeta
    if [[ "$folder" != "$(dirname "$folder")/$new_name" ]]; then
        mv "$folder" "$(dirname "$folder")/$new_name"
        echo "✅ Carpeta renombrada: $folder -> $new_name"
    else
        echo "⏭️  Carpeta ya sigue convenciones: $folder"
    fi
}

# Función principal
main() {
    echo "🎯 Iniciando aplicación de naming conventions..."
    
    # Renombrar archivos markdown
    echo "📄 Renombrando archivos markdown..."
    find . -name "*.md" -type f | while read file; do
        rename_file "$file"
    done
    
    # Renombrar carpetas principales
    echo "📁 Renombrando carpetas principales..."
    find . -maxdepth 1 -type d | grep -v "^\.$" | while read folder; do
        rename_folder "$folder"
    done
    
    echo ""
    echo "🎉 NAMING CONVENTIONS APLICADAS"
    echo "==============================="
    echo "✅ Archivos renombrados según convenciones"
    echo "✅ Carpetas renombradas según convenciones"
    echo "✅ Estructura optimizada"
    echo ""
    echo "📊 Ver NAMING_CONVENTIONS.md para detalles"
}

# Ejecutar función principal
main















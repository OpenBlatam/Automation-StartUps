#!/bin/bash
# 📊 Generador de Reporte de DAGs

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

REPORT_FILE="DAG_REPORT_$(date +%Y%m%d_%H%M%S).md"

echo -e "${BLUE}📊 Generando reporte de DAGs...${NC}\n"

cat > "$REPORT_FILE" << 'EOF'
# 📊 Reporte de DAGs

**Generado**: $(date)
**Directorio**: $(pwd)

## Resumen Ejecutivo

EOF

# Contar DAGs por área
echo "## Estadísticas por Área" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Área | DAGs | Documentación | Última Modificación |" >> "$REPORT_FILE"
echo "|------|------|---------------|---------------------|" >> "$REPORT_FILE"

for area in sales_marketing hr_talent finance_billing product_ecommerce customer_success data_analytics operations integrations; do
    if [ -d "$area" ]; then
        DAG_COUNT=$(find "$area" -name "*.py" -type f | wc -l | xargs)
        DOC_COUNT=$(find "$area" -name "*.md" -type f | wc -l | xargs)
        LAST_MOD=$(find "$area" -name "*.py" -type f -exec stat -f "%Sm" -t "%Y-%m-%d" {} \; | sort -r | head -1)
        echo "| $area | $DAG_COUNT | $DOC_COUNT | $LAST_MOD |" >> "$REPORT_FILE"
    fi
done

# DAGs recientemente modificados
echo "" >> "$REPORT_FILE"
echo "## DAGs Modificados Recientemente (Últimos 7 días)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
find . -name "*.py" -type f -mtime -7 -exec ls -lh {} \; | \
    awk '{print "| " $9 " | " $5 " | " $6 " " $7 " " $8 " |"}' | \
    head -20 >> "$REPORT_FILE"

# DAGs más grandes
echo "" >> "$REPORT_FILE"
echo "## DAGs Más Grandes (Top 10)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "| Archivo | Líneas | Tamaño |" >> "$REPORT_FILE"
echo "|---------|--------|--------|" >> "$REPORT_FILE"
find . -name "*.py" -type f -exec wc -l {} \; | sort -rn | head -10 | \
    awk '{print "| " $2 " | " $1 " | "}' >> "$REPORT_FILE"

# DAGs sin documentación
echo "" >> "$REPORT_FILE"
echo "## DAGs Sin Documentación (Necesitan README)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
# Lógica para encontrar DAGs sin README cercano

# Resumen de errores comunes
echo "" >> "$REPORT_FILE"
echo "## Recomendaciones" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"
echo "- Revisar DAGs sin documentación" >> "$REPORT_FILE"
echo "- Optimizar DAGs muy grandes (>1000 líneas)" >> "$REPORT_FILE"
echo "- Verificar dependencias entre DAGs" >> "$REPORT_FILE"

echo -e "${GREEN}✅ Reporte generado: $REPORT_FILE${NC}"
echo -e "${YELLOW}📝 Revisa el archivo para más detalles${NC}"


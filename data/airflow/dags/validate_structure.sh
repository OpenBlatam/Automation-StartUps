#!/bin/bash
# ✅ Validador de Estructura de DAGs

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ERRORS=0
WARNINGS=0

echo -e "${BLUE}🔍 Validando estructura de DAGs...${NC}\n"

# Validar áreas principales
VALID_AREAS=("sales_marketing" "hr_talent" "finance_billing" "product_ecommerce" "customer_success" "data_analytics" "operations" "integrations")
echo -e "${BLUE}Verificando áreas principales...${NC}"

for area in "${VALID_AREAS[@]}"; do
    if [ ! -d "$area" ]; then
        echo -e "${RED}❌ Área faltante: $area${NC}"
        ((ERRORS++))
    else
        echo -e "${GREEN}✅ $area${NC}"
    fi
done

# Validar READMEs
echo -e "\n${BLUE}Verificando READMEs...${NC}"
for area in "${VALID_AREAS[@]}"; do
    if [ -d "$area" ] && [ ! -f "$area/README.md" ]; then
        echo -e "${YELLOW}⚠️  README faltante en: $area${NC}"
        ((WARNINGS++))
    fi
done

# Validar archivos Python en lugares incorrectos
echo -e "\n${BLUE}Verificando archivos Python en raíz...${NC}"
ROOT_PY_FILES=$(find . -maxdepth 1 -name "*.py" -type f | grep -v "./find_dag.sh" | grep -v "./generate_dag_template.sh" | grep -v "./validate_structure.sh")
if [ -n "$ROOT_PY_FILES" ]; then
    echo -e "${YELLOW}⚠️  Archivos Python en raíz (deberían estar en áreas):${NC}"
    echo "$ROOT_PY_FILES" | sed 's/^/  /'
    ((WARNINGS++))
fi

# Validar nombres de archivos
echo -e "\n${BLUE}Verificando convenciones de nombres...${NC}"
BAD_NAMES=$(find . -name "*.py" -type f | grep -E "(dag[0-9]|test[0-9]|main|process|temp)" | grep -v "test_" | grep -v "tests/")
if [ -n "$BAD_NAMES" ]; then
    echo -e "${YELLOW}⚠️  Nombres que podrían mejorar:${NC}"
    echo "$BAD_NAMES" | sed 's/^/  /'
    ((WARNINGS++))
fi

# Contar DAGs por área
echo -e "\n${BLUE}Estadísticas por área:${NC}"
for area in "${VALID_AREAS[@]}"; do
    if [ -d "$area" ]; then
        COUNT=$(find "$area" -name "*.py" -type f | wc -l | xargs)
        echo -e "  ${GREEN}$area:${NC} $COUNT DAGs"
    fi
done

# Validar documentación
echo -e "\n${BLUE}Verificando documentación principal...${NC}"
REQUIRED_DOCS=("README.md" "STRUCTURE.md" "QUICK_REFERENCE.md" "QUICK_START.md" "BEST_PRACTICES.md" "DAG_DEPENDENCIES.md")
for doc in "${REQUIRED_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅ $doc${NC}"
    else
        echo -e "${RED}❌ Faltante: $doc${NC}"
        ((ERRORS++))
    fi
done

# Resumen
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ Validación completada sin errores${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Validación completada con $WARNINGS advertencia(s)${NC}"
    exit 0
else
    echo -e "${RED}❌ Validación completada con $ERRORS error(es) y $WARNINGS advertencia(s)${NC}"
    exit 1
fi


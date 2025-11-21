#!/bin/bash
# Script de setup para sistema de generación de descripciones de productos
# Ejecuta migraciones de base de datos y configuración inicial

set -e

echo "🚀 Configurando Sistema de Generación de Descripciones de Productos..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar PostgreSQL
echo -e "${BLUE}Verificando conexión a PostgreSQL...${NC}"
if ! psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-postgres}" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  No se pudo conectar a PostgreSQL. Verifica las variables de entorno.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ PostgreSQL conectado${NC}"

# Directorio base
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCHEMA_FILE="${BASE_DIR}/data/airflow/dags/product_description_schema.sql"

# Función para ejecutar SQL
run_sql() {
    local file=$1
    echo -e "${BLUE}Ejecutando: $(basename $file)${NC}"
    psql -h "${POSTGRES_HOST:-localhost}" \
         -U "${POSTGRES_USER:-postgres}" \
         -d "${POSTGRES_DB:-postgres}" \
         -f "$file" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $(basename $file) ejecutado exitosamente${NC}"
    else
        echo -e "${RED}❌ Error en $(basename $file)${NC}"
        return 1
    fi
}

# Ejecutar schema
if [ -f "$SCHEMA_FILE" ]; then
    echo -e "\n${BLUE}📊 Creando esquema de base de datos...${NC}"
    run_sql "$SCHEMA_FILE"
else
    echo -e "${RED}❌ Archivo de schema no encontrado: $SCHEMA_FILE${NC}"
    exit 1
fi

# Verificar tablas creadas
echo -e "\n${BLUE}🔍 Verificando tablas creadas...${NC}"
TABLES=(
    "product_descriptions"
    "product_description_variations"
    "product_descriptions_cache"
    "product_description_ab_metrics"
)

for table in "${TABLES[@]}"; do
    if psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-postgres}" -c "\d $table" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Tabla $table existe${NC}"
    else
        echo -e "${RED}❌ Tabla $table no encontrada${NC}"
    fi
done

# Verificar vistas
echo -e "\n${BLUE}🔍 Verificando vistas...${NC}"
VIEWS=(
    "product_descriptions_stats"
    "product_description_ab_summary"
)

for view in "${VIEWS[@]}"; do
    if psql -h "${POSTGRES_HOST:-localhost}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-postgres}" -c "\d $view" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Vista $view existe${NC}"
    else
        echo -e "${YELLOW}⚠️  Vista $view no encontrada${NC}"
    fi
done

echo -e "\n${GREEN}✅ Setup completado exitosamente${NC}"
echo -e "\n${BLUE}📝 Próximos pasos:${NC}"
echo -e "1. Configurar variables de Airflow para API keys de IA"
echo -e "2. Probar generación con el DAG: product_description_generator"
echo -e "3. Configurar API REST si se requiere"
echo -e "4. Configurar integraciones con plataformas (Shopify, Amazon, etc.)"


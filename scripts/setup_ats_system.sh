#!/bin/bash
# Setup Script para Sistema ATS Completo
# Ejecuta todas las migraciones y configuración inicial

set -e

echo "🚀 Configurando Sistema ATS Completo..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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
DB_DIR="${BASE_DIR}/data/db"

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
        echo -e "${YELLOW}⚠️  Error en $(basename $file)${NC}"
        return 1
    fi
}

# Ejecutar schemas en orden
echo -e "\n${BLUE}📊 Ejecutando schemas de base de datos...${NC}"

SCHEMAS=(
    "ats_schema.sql"
    "ats_extended_schema.sql"
    "ats_ai_schema.sql"
    "ats_enterprise_schema.sql"
    "ats_ultimate_schema.sql"
    "ats_complete_schema.sql"
    "ats_analytics_schema.sql"
    "ats_executive_schema.sql"
)

for schema in "${SCHEMAS[@]}"; do
    if [ -f "${DB_DIR}/${schema}" ]; then
        run_sql "${DB_DIR}/${schema}"
    else
        echo -e "${YELLOW}⚠️  Archivo no encontrado: ${schema}${NC}"
    fi
done

# Cargar templates
echo -e "\n${BLUE}📝 Cargando templates de comunicación...${NC}"
if [ -f "${DB_DIR}/ats_templates_seed.sql" ]; then
    run_sql "${DB_DIR}/ats_templates_seed.sql"
else
    echo -e "${YELLOW}⚠️  Templates no encontrados${NC}"
fi

# Verificar tablas creadas
echo -e "\n${BLUE}🔍 Verificando tablas creadas...${NC}"
TABLE_COUNT=$(psql -h "${POSTGRES_HOST:-localhost}" \
    -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-postgres}" \
    -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name LIKE 'ats_%';" | xargs)

echo -e "${GREEN}✅ ${TABLE_COUNT} tablas ATS creadas${NC}"

# Verificar vistas
echo -e "\n${BLUE}🔍 Verificando vistas creadas...${NC}"
VIEW_COUNT=$(psql -h "${POSTGRES_HOST:-localhost}" \
    -U "${POSTGRES_USER:-postgres}" \
    -d "${POSTGRES_DB:-postgres}" \
    -t -c "SELECT COUNT(*) FROM information_schema.views WHERE table_schema = 'public' AND table_name LIKE 'ats_%';" | xargs)

echo -e "${GREEN}✅ ${VIEW_COUNT} vistas ATS creadas${NC}"

# Resumen
echo -e "\n${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Sistema ATS configurado exitosamente!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "📊 Tablas: ${TABLE_COUNT}"
echo -e "📈 Vistas: ${VIEW_COUNT}"
echo -e "\n${BLUE}Próximos pasos:${NC}"
echo -e "1. Configurar variables de entorno para integraciones"
echo -e "2. Probar DAGs de Airflow"
echo -e "3. Crear workflows automáticos"
echo -e "4. Configurar templates de comunicación"
echo -e "\n${GREEN}¡Listo para usar! 🚀${NC}"


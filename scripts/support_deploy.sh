#!/bin/bash
# Script de Deployment del Sistema de Soporte
# Automatiza el despliegue completo del sistema

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuración
DB_HOST="${DB_HOST:-localhost}"
DB_NAME="${DB_NAME:-support_db}"
DB_USER="${DB_USER:-postgres}"
ENVIRONMENT="${ENVIRONMENT:-dev}"

echo -e "${GREEN}🚀 Iniciando deployment del Sistema de Soporte${NC}"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Database: $DB_HOST/$DB_NAME"
echo ""

# Función para verificar comandos
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}❌ $1 no está instalado${NC}"
        exit 1
    fi
}

# Verificar dependencias
echo -e "${YELLOW}📋 Verificando dependencias...${NC}"
check_command psql
check_command python3

# Paso 1: Crear esquemas de BD
echo -e "${YELLOW}📊 Creando esquemas de base de datos...${NC}"
if psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f data/db/support_tickets_schema.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Esquema principal creado${NC}"
else
    echo -e "${RED}❌ Error creando esquema principal${NC}"
    exit 1
fi

if psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f data/db/support_feedback_schema.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Esquema de feedback creado${NC}"
else
    echo -e "${YELLOW}⚠️  Esquema de feedback ya existe o hay error (continuando)${NC}"
fi

# Paso 2: Cargar FAQs de ejemplo
echo -e "${YELLOW}📚 Cargando FAQs de ejemplo...${NC}"
if psql -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" -f data/db/support_faq_seed.sql > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FAQs cargados${NC}"
else
    echo -e "${YELLOW}⚠️  FAQs ya existen o hay error (continuando)${NC}"
fi

# Paso 3: Configurar agentes y reglas
echo -e "${YELLOW}👥 Configurando agentes y reglas...${NC}"
if python3 scripts/support_setup_example.py > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Agentes y reglas configurados${NC}"
else
    echo -e "${YELLOW}⚠️  Error configurando agentes (puede requerir ajustes manuales)${NC}"
fi

# Paso 4: Health Check
echo -e "${YELLOW}🏥 Ejecutando health check...${NC}"
if python3 scripts/support_health_check.py > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Health check pasado${NC}"
else
    echo -e "${YELLOW}⚠️  Health check con advertencias (revisar output)${NC}"
fi

# Paso 5: Verificar workflows de Kestra (si está disponible)
if command -v kubectl &> /dev/null; then
    echo -e "${YELLOW}🔄 Verificando workflows de Kestra...${NC}"
    if kubectl get namespace workflows &> /dev/null; then
        echo -e "${GREEN}✅ Namespace de workflows existe${NC}"
    else
        echo -e "${YELLOW}⚠️  Namespace de workflows no encontrado${NC}"
    fi
fi

# Paso 6: Verificar DAGs de Airflow (si está disponible)
if [ -d "data/airflow/dags" ]; then
    echo -e "${YELLOW}✈️  Verificando DAGs de Airflow...${NC}"
    DAG_COUNT=$(find data/airflow/dags -name "support_*.py" | wc -l)
    if [ "$DAG_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✅ Encontrados $DAG_COUNT DAGs de soporte${NC}"
    fi
fi

# Resumen
echo ""
echo -e "${GREEN}=========================================="
echo "✅ Deployment completado"
echo "==========================================${NC}"
echo ""
echo "📋 Próximos pasos:"
echo "1. Configurar variables de entorno en Kestra"
echo "2. Configurar variables de entorno en Airflow"
echo "3. Configurar webhooks y notificaciones"
echo "4. Probar creación de ticket vía API"
echo "5. Verificar monitoreo"
echo ""
echo "📚 Documentación:"
echo "- Quick Start: workflow/kestra/flows/SUPPORT_AUTOMATION_QUICK_START.md"
echo "- Guía Completa: workflow/kestra/flows/README_SUPPORT_AUTOMATION.md"
echo ""


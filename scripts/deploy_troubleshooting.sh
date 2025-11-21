#!/bin/bash
# Script de Deployment para Sistema de Troubleshooting
# Uso: ./deploy_troubleshooting.sh [environment]

set -e

ENVIRONMENT=${1:-dev}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Iniciando deployment del Sistema de Troubleshooting"
echo "📦 Entorno: $ENVIRONMENT"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
info() {
    echo -e "${GREEN}✓${NC} $1"
}

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
    exit 1
}

# Verificar variables de entorno
if [ -z "$DATABASE_URL" ]; then
    error "DATABASE_URL no está configurada"
fi

info "Verificando conexión a base de datos..."
psql "$DATABASE_URL" -c "SELECT 1" > /dev/null 2>&1 || error "No se puede conectar a la base de datos"

# Ejecutar esquemas SQL en orden
info "Ejecutando esquemas SQL..."

SCHEMAS=(
    "data/db/support_troubleshooting_schema.sql"
    "data/db/support_troubleshooting_feedback_schema.sql"
    "data/db/support_webhooks_schema.sql"
    "data/db/support_troubleshooting_advanced_schema.sql"
    "data/db/support_troubleshooting_performance_schema.sql"
)

for schema in "${SCHEMAS[@]}"; do
    if [ -f "$schema" ]; then
        info "Ejecutando $schema..."
        psql "$DATABASE_URL" -f "$schema" || warn "Error ejecutando $schema (puede que ya exista)"
    else
        warn "Archivo no encontrado: $schema"
    fi
done

# Refresh vistas materializadas
info "Refrescando vistas materializadas..."
psql "$DATABASE_URL" -c "SELECT refresh_troubleshooting_views();" || warn "Error refrescando vistas"

# Verificar instalación
info "Verificando instalación..."
python3 -c "
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent
agent = TroubleshootingAgent()
print('✓ Agente inicializado correctamente')
print(f'✓ Base de conocimiento cargada: {len(agent.knowledge_base)} problemas')
" || error "Error verificando instalación"

# Ejecutar tests básicos
if [ "$ENVIRONMENT" != "prod" ]; then
    info "Ejecutando tests básicos..."
    if command -v pytest &> /dev/null; then
        pytest tests/test_troubleshooting_system.py::TestTroubleshootingAgent::test_agent_initialization -v || warn "Algunos tests fallaron"
    else
        warn "pytest no está instalado, saltando tests"
    fi
fi

# Configurar mantenimiento automático (solo si pg_cron está disponible)
info "Configurando mantenimiento automático..."
psql "$DATABASE_URL" -f "data/db/support_troubleshooting_maintenance.sql" 2>/dev/null || warn "pg_cron no disponible, configuración manual requerida"

# Verificar configuración
info "Verificando configuración del sistema..."
CONFIG_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM support_troubleshooting_config;" 2>/dev/null | xargs)
if [ "$CONFIG_COUNT" -gt "0" ]; then
    info "Configuración encontrada: $CONFIG_COUNT entradas"
else
    warn "No se encontró configuración, usando valores por defecto"
fi

# Resumen
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
info "✅ Deployment completado exitosamente!"
echo ""
echo "📊 Próximos pasos:"
echo "   1. Configurar variables de entorno (.env)"
echo "   2. Probar el sistema: python3 data/integrations/examples/troubleshooting_example.py"
echo "   3. Configurar webhooks si es necesario"
echo "   4. Revisar documentación en docs/"
echo ""
echo "🔗 Recursos útiles:"
echo "   - API Docs: docs/API_TROUBLESHOOTING.md"
echo "   - Guía de Implementación: docs/IMPLEMENTATION_GUIDE_TROUBLESHOOTING.md"
echo "   - Inicio Rápido: docs/QUICK_START_TROUBLESHOOTING.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"




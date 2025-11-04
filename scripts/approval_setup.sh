#!/bin/bash
# Script de configuración inicial del sistema de aprobaciones

set -e

echo "🚀 Configurando Sistema de Aprobaciones Internas..."

# Variables
DB_HOST="${APPROVALS_DB_HOST:-localhost}"
DB_PORT="${APPROVALS_DB_PORT:-5432}"
DB_NAME="${APPROVALS_DB_NAME:-approvals}"
DB_USER="${APPROVALS_DB_USER:-postgres}"

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}📦 Creando esquema de base de datos...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$(dirname $0)/../data/db/approvals_schema.sql

echo -e "${BLUE}📊 Creando vistas materializadas...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$(dirname $0)/../data/db/approvals_views.sql

echo -e "${BLUE}👥 Creando usuarios de ejemplo...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- Usuarios de ejemplo si no existen
INSERT INTO approval_users (user_email, user_name, department, role, manager_email) VALUES
    ('john.doe@company.com', 'John Doe', 'Engineering', 'employee', 'jane.manager@company.com'),
    ('jane.manager@company.com', 'Jane Manager', 'Engineering', 'manager', 'bob.director@company.com'),
    ('bob.director@company.com', 'Bob Director', 'Engineering', 'director', 'alice.ceo@company.com'),
    ('alice.ceo@company.com', 'Alice CEO', 'Executive', 'ceo', NULL),
    ('finance@company.com', 'Finance Manager', 'Finance', 'finance_manager', 'alice.ceo@company.com'),
    ('hr@company.com', 'HR Manager', 'HR', 'hr_manager', 'alice.ceo@company.com'),
    ('legal@company.com', 'Legal Manager', 'Legal', 'legal_manager', 'alice.ceo@company.com')
ON CONFLICT (user_email) DO NOTHING;
EOF

echo -e "${BLUE}⚙️  Creando reglas automáticas de ejemplo...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
-- Reglas automáticas de ejemplo
INSERT INTO approval_rules (rule_name, rule_description, request_type, conditions, auto_approve, require_notification, priority) VALUES
    (
        'Auto-aprobar gastos menores a $500',
        'Gastos menores a $500 se auto-aprueban si son de categorías comunes',
        'expense',
        '{"amount_max": 500, "expense_category": ["meals", "supplies", "travel"], "requester_role": ["employee", "manager"]}'::jsonb,
        true,
        true,
        10
    ),
    (
        'Auto-aprobar vacaciones cortas',
        'Vacaciones de 3 días o menos se auto-aprueban si el empleado tiene saldo disponible',
        'vacation',
        '{"vacation_days_max": 3, "vacation_type": "annual"}'::jsonb,
        true,
        true,
        10
    ),
    (
        'Auto-aprobar documentos de baja criticidad',
        'Documentos de categoría "other" o "report" se auto-aprueban',
        'document',
        '{"document_category": ["other", "report"], "requires_review": false}'::jsonb,
        true,
        true,
        10
    ),
    (
        'Auto-aprobar gastos de viaje recurrentes',
        'Gastos de viaje menores a $300 para empleados con rol manager',
        'expense',
        '{"amount_max": 300, "expense_category": ["travel"], "requester_role": ["manager"]}'::jsonb,
        true,
        true,
        9
    )
ON CONFLICT DO NOTHING;
EOF

echo -e "${BLUE}🔄 Refrescando vistas materializadas...${NC}"
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF
SELECT refresh_approval_views();
EOF

echo -e "${GREEN}✅ Configuración completada exitosamente!${NC}"
echo ""
echo "📝 Próximos pasos:"
echo "  1. Configurar variables de entorno (APPROVALS_DB_URL, etc.)"
echo "  2. Desplegar procesos BPMN en Flowable"
echo "  3. Configurar flujos de Kestra"
echo "  4. Desplegar API REST"
echo "  5. Configurar notificaciones (Slack webhook)"
echo ""
echo "📚 Documentación: workflow/APPROVALS_SYSTEM.md"


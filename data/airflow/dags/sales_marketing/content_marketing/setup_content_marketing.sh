#!/bin/bash
# Script de Setup para Sistema de Marketing de Contenido

set -e

echo "🚀 Configurando Sistema de Marketing de Contenido..."
echo ""

# Variables
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-your_database}"
DB_USER="${DB_USER:-your_user}"

# Verificar si psql está disponible
if ! command -v psql &> /dev/null; then
    echo "❌ psql no encontrado. Por favor instala PostgreSQL client."
    exit 1
fi

echo "📦 Instalando esquema de base de datos..."
psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$(dirname "$0")/../../db/content_marketing_schema.sql"

if [ $? -eq 0 ]; then
    echo "✅ Esquema instalado correctamente"
else
    echo "❌ Error instalando esquema"
    exit 1
fi

echo ""
echo "📝 Creando configuración de ejemplo..."
cat << EOF | psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" 2>/dev/null || echo "⚠️  Configuración de ejemplo ya existe o error al crear"

-- Configuración de ejemplo para Twitter
INSERT INTO content_platform_config
(platform, account_id, account_name, api_key, api_secret, access_token, access_token_secret, is_active, daily_post_limit, hourly_post_limit)
VALUES
('twitter', 'twitter-account-1', 'Mi Cuenta Twitter', 'TU_API_KEY', 'TU_API_SECRET', 'TU_ACCESS_TOKEN', 'TU_ACCESS_TOKEN_SECRET', TRUE, 10, 2)
ON CONFLICT (platform) DO NOTHING;

-- Configuración de ejemplo para LinkedIn
INSERT INTO content_platform_config
(platform, account_id, account_name, access_token, is_active, daily_post_limit, hourly_post_limit)
VALUES
('linkedin', 'linkedin-account-1', 'Mi Cuenta LinkedIn', 'TU_ACCESS_TOKEN', TRUE, 10, 2)
ON CONFLICT (platform) DO NOTHING;

-- Configuración de ejemplo para Facebook
INSERT INTO content_platform_config
(platform, account_id, account_name, access_token, is_active, daily_post_limit, hourly_post_limit)
VALUES
('facebook', 'facebook-account-1', 'Mi Cuenta Facebook', 'TU_ACCESS_TOKEN', TRUE, 10, 2)
ON CONFLICT (platform) DO NOTHING;

EOF

echo "✅ Configuración de ejemplo creada"
echo ""
echo "📋 Próximos pasos:"
echo "1. Actualiza las credenciales en content_platform_config"
echo "2. Configura la conexión postgres_default en Airflow"
echo "3. Activa el DAG content_marketing_automation"
echo "4. Crea tu primer artículo en content_articles"
echo ""
echo "📚 Ver documentación: data/airflow/dags/README_CONTENT_MARKETING.md"
echo ""
echo "✅ Setup completado!"


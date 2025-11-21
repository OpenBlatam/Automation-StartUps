#!/bin/bash
# Script de configuración para backups automáticos
# Configura encriptación, nube y variables de entorno

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 Configuración de Backups Automáticos${NC}"
echo ""

# 1. Generar clave de encriptación
echo -e "${YELLOW}1. Configurando encriptación...${NC}"
ENCRYPTION_KEY_FILE="${ENCRYPTION_KEY_FILE:-./backup_encryption_key.txt}"

if [ ! -f "$ENCRYPTION_KEY_FILE" ]; then
    echo "Generando nueva clave de encriptación..."
    python3 << EOF
from cryptography.fernet import Fernet
import base64

key = Fernet.generate_key()
key_b64 = base64.b64encode(key).decode('utf-8')
print(f"Clave generada: {key_b64}")

with open('$ENCRYPTION_KEY_FILE', 'w') as f:
    f.write(key_b64)

print(f"\n✅ Clave guardada en: $ENCRYPTION_KEY_FILE")
print("⚠️  IMPORTANTE: Guarda esta clave en un lugar seguro!")
print("⚠️  Sin esta clave, NO podrás desencriptar los backups!")
EOF
else
    echo -e "${GREEN}✓ Clave de encriptación ya existe${NC}"
fi

# 2. Configurar variables de entorno
echo ""
echo -e "${YELLOW}2. Configurando variables de entorno...${NC}"

ENV_FILE="${ENV_FILE:-.env.backups}"

cat > "$ENV_FILE" << EOF
# Configuración de Backups Automáticos
# Generado el $(date)

# Directorio de backups local
export BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"

# Días de retención
export BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

# Clave de encriptación (base64)
export BACKUP_ENCRYPTION_KEY="$(cat $ENCRYPTION_KEY_FILE 2>/dev/null || echo '')"

# Configuración de nube (seleccionar uno)
export CLOUD_PROVIDER="${CLOUD_PROVIDER:-aws}"  # aws, azure, gcp

# AWS S3
export AWS_BACKUP_BUCKET="${AWS_BACKUP_BUCKET:-biz-datalake-backups}"
export AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID:-}"
export AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY:-}"
export AWS_REGION="${AWS_REGION:-us-east-1}"

# Azure Blob Storage
export AZURE_STORAGE_CONNECTION_STRING="${AZURE_STORAGE_CONNECTION_STRING:-}"
export AZURE_BACKUP_CONTAINER="${AZURE_BACKUP_CONTAINER:-backups}"

# GCP Cloud Storage
export GCP_BACKUP_BUCKET="${GCP_BACKUP_BUCKET:-}"
export GCP_CREDENTIALS_PATH="${GCP_CREDENTIALS_PATH:-}"

# Bases de datos a respaldar (separadas por coma)
export BACKUP_DB_CONNECTIONS="${BACKUP_DB_CONNECTIONS:-postgresql://user:pass@localhost:5432/dbname}"

# Rutas críticas a respaldar (separadas por coma)
export BACKUP_CRITICAL_PATHS="${BACKUP_CRITICAL_PATHS:-/etc,/opt/config}"

# Notificaciones
export SLACK_WEBHOOK_URL="${SLACK_WEBHOOK_URL:-}"
export BACKUP_ALERT_EMAILS="${BACKUP_ALERT_EMAILS:-admin@example.com}"

# Email SMTP
export SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"
export SMTP_PORT="${SMTP_PORT:-587}"
export SMTP_USER="${SMTP_USER:-}"
export SMTP_PASSWORD="${SMTP_PASSWORD:-}"
export FROM_EMAIL="${FROM_EMAIL:-backups@example.com}"
EOF

echo -e "${GREEN}✓ Variables de entorno creadas en: $ENV_FILE${NC}"
echo ""
echo -e "${YELLOW}📝 Edita $ENV_FILE para configurar tus credenciales${NC}"

# 3. Crear directorio de backups
echo ""
echo -e "${YELLOW}3. Creando directorio de backups...${NC}"
BACKUP_DIR="${BACKUP_DIR:-/tmp/backups}"
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✓ Directorio creado: $BACKUP_DIR${NC}"

# 4. Instalar dependencias Python
echo ""
echo -e "${YELLOW}4. Instalando dependencias Python...${NC}"
pip install -q cryptography boto3 azure-storage-blob google-cloud-storage || {
    echo "⚠️  Algunas dependencias pueden requerir configuración adicional"
}

# 5. Verificar configuración
echo ""
echo -e "${YELLOW}5. Verificando configuración...${NC}"

source "$ENV_FILE"

ERRORS=0

if [ -z "$BACKUP_ENCRYPTION_KEY" ]; then
    echo -e "❌ BACKUP_ENCRYPTION_KEY no configurado"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓ Encriptación configurada${NC}"
fi

if [ -z "$BACKUP_DB_CONNECTIONS" ]; then
    echo -e "⚠️  BACKUP_DB_CONNECTIONS no configurado (opcional)"
else
    echo -e "${GREEN}✓ Bases de datos configuradas${NC}"
fi

if [ "$CLOUD_PROVIDER" = "aws" ]; then
    if [ -z "$AWS_BACKUP_BUCKET" ] || [ -z "$AWS_ACCESS_KEY_ID" ]; then
        echo -e "⚠️  Configuración AWS incompleta"
    else
        echo -e "${GREEN}✓ AWS S3 configurado${NC}"
    fi
elif [ "$CLOUD_PROVIDER" = "azure" ]; then
    if [ -z "$AZURE_STORAGE_CONNECTION_STRING" ]; then
        echo -e "⚠️  Configuración Azure incompleta"
    else
        echo -e "${GREEN}✓ Azure Blob Storage configurado${NC}"
    fi
elif [ "$CLOUD_PROVIDER" = "gcp" ]; then
    if [ -z "$GCP_BACKUP_BUCKET" ]; then
        echo -e "⚠️  Configuración GCP incompleta"
    else
        echo -e "${GREEN}✓ GCP Cloud Storage configurado${NC}"
    fi
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ Configuración completada exitosamente!${NC}"
    echo ""
    echo "Próximos pasos:"
    echo "1. Edita $ENV_FILE con tus credenciales"
    echo "2. Carga las variables de entorno: source $ENV_FILE"
    echo "3. Los DAGs de Airflow se ejecutarán automáticamente"
    echo "4. Verifica los backups en: $BACKUP_DIR"
else
    echo -e "${YELLOW}⚠️  Configuración completada con $ERRORS error(es)${NC}"
    echo "Revisa los errores arriba y configura las variables faltantes"
fi


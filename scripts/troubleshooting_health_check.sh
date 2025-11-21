#!/bin/bash
# Script de Health Check para Troubleshooting
# Uso: ./troubleshooting_health_check.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

echo "🏥 Health Check del Sistema de Troubleshooting"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python3 encontrado: $(python3 --version)"
else
    echo -e "${RED}✗${NC} Python3 no encontrado"
    exit 1
fi

# Verificar PostgreSQL
if command -v psql &> /dev/null; then
    echo -e "${GREEN}✓${NC} PostgreSQL encontrado: $(psql --version | head -n1)"
else
    echo -e "${YELLOW}⚠${NC} PostgreSQL no encontrado (psql)"
fi

# Verificar variables de entorno
if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠${NC} DATABASE_URL no configurada"
else
    echo -e "${GREEN}✓${NC} DATABASE_URL configurada"
fi

# Ejecutar health check Python
echo ""
echo "Ejecutando health check completo..."
python3 scripts/troubleshooting_health_check.py

echo ""
echo "================================================"
echo "Health check completado"




#!/bin/bash
# Script de Deployment para Chatbots
# Facilita el despliegue y configuración de los chatbots

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Despliegue de Chatbots"
echo "=========================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 no encontrado${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} encontrado${NC}"

# Crear directorios necesarios
echo ""
echo "📁 Creando directorios..."
mkdir -p chatbot_conversations
mkdir -p logs
mkdir -p exports
chmod 755 chatbot_conversations logs exports

# Verificar dependencias opcionales
echo ""
echo "🔍 Verificando dependencias..."
if python3 -c "import flask" 2>/dev/null; then
    echo -e "${GREEN}✅ Flask disponible (API REST habilitada)${NC}"
else
    echo -e "${YELLOW}⚠️  Flask no encontrado (API REST no disponible)${NC}"
    echo "   Instala con: pip install flask flask-cors"
fi

# Crear archivo de configuración si no existe
if [ ! -f "chatbot_config.json" ]; then
    echo ""
    echo "⚙️  Creando archivo de configuración..."
    python3 << EOF
from chatbot_config import ConfigManager
config_manager = ConfigManager()
print("✅ Configuración creada")
EOF
fi

# Ejecutar tests básicos
echo ""
echo "🧪 Ejecutando tests básicos..."
if python3 -c "import test_chatbot" 2>/dev/null; then
    python3 test_chatbot.py 2>&1 | head -20
    echo -e "${GREEN}✅ Tests completados${NC}"
else
    echo -e "${YELLOW}⚠️  Tests no disponibles${NC}"
fi

# Verificar permisos de ejecución
echo ""
echo "🔐 Configurando permisos..."
chmod +x chatbot_curso_ia_webinars.py
chmod +x chatbot_saas_ia_marketing.py
chmod +x chatbot_ia_bulk_documentos.py
chmod +x chatbot_api.py 2>/dev/null || true

echo ""
echo -e "${GREEN}✅ Despliegue completado${NC}"
echo ""
echo "📚 Próximos pasos:"
echo "   1. Ejecuta un chatbot: python3 scripts/chatbot_curso_ia_webinars.py"
echo "   2. Inicia la API: python3 scripts/chatbot_api.py"
echo "   3. Lee la documentación: cat scripts/README_CHATBOTS.md"
echo ""







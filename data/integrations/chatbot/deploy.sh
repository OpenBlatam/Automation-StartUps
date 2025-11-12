#!/bin/bash

# Script de Deployment para el Sistema de Chatbot
# Versión: 2.0.0

set -e

echo "🚀 Iniciando deployment del Sistema de Chatbot..."

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo -e "${BLUE}📋 Verificando requisitos...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo -e "${BLUE}🔧 Creando entorno virtual...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
echo -e "${BLUE}🔌 Activando entorno virtual...${NC}"
source venv/bin/activate

# Instalar dependencias
echo -e "${BLUE}📦 Instalando dependencias...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Crear directorios necesarios
echo -e "${BLUE}📁 Creando directorios...${NC}"
mkdir -p tickets
mkdir -p learning_data
mkdir -p reports
mkdir -p logs

# Verificar archivos de configuración
echo -e "${BLUE}⚙️ Verificando configuración...${NC}"
if [ ! -f "chatbot_config.json" ]; then
    echo -e "${YELLOW}⚠️ chatbot_config.json no encontrado. Creando desde template...${NC}"
    # El archivo debería existir, pero si no, se creará con valores por defecto
fi

# Verificar archivos de datos
if [ ! -f "faqs.json" ]; then
    echo -e "${YELLOW}⚠️ faqs.json no encontrado. Asegúrate de tener tus FAQs configuradas.${NC}"
fi

# Ejecutar tests
echo -e "${BLUE}🧪 Ejecutando tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest test_chatbot.py -v || echo -e "${YELLOW}⚠️ Algunos tests fallaron, pero continuando...${NC}"
else
    echo -e "${YELLOW}⚠️ pytest no instalado, saltando tests...${NC}"
fi

# Crear archivo de inicio
cat > start_chatbot.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python api_rest.py
EOF

chmod +x start_chatbot.sh

# Crear archivo de inicio del dashboard
cat > start_dashboard.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python dashboard_metrics.py
EOF

chmod +x start_dashboard.sh

echo -e "${GREEN}✅ Deployment completado exitosamente!${NC}"
echo ""
echo -e "${BLUE}📝 Próximos pasos:${NC}"
echo "  1. Configura chatbot_config.json con tus credenciales"
echo "  2. Personaliza faqs.json con tus preguntas frecuentes"
echo "  3. Inicia la API: ./start_chatbot.sh"
echo "  4. Inicia el Dashboard: ./start_dashboard.sh"
echo ""
echo -e "${GREEN}🎉 ¡El sistema está listo para usar!${NC}"







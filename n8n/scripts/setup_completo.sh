#!/bin/bash
# Setup Completo del Sistema Sora Workflow
# ===========================================

set -e

echo "🚀 Configuración Completa del Sistema Sora Workflow"
echo "=================================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para verificar comando
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✅ $1 instalado${NC}"
        return 0
    else
        echo -e "${RED}❌ $1 no encontrado${NC}"
        return 1
    fi
}

# Función para verificar Python y dependencias
check_python() {
    echo ""
    echo "🐍 Verificando Python..."
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        echo "   Versión: $PYTHON_VERSION"
        
        echo ""
        echo "📦 Verificando dependencias Python..."
        python3 -c "import json" 2>/dev/null && echo -e "${GREEN}✅ json${NC}" || echo -e "${YELLOW}⚠️  json (built-in)${NC}"
        python3 -c "import pandas" 2>/dev/null && echo -e "${GREEN}✅ pandas${NC}" || echo -e "${YELLOW}⚠️  pandas no instalado${NC}"
        python3 -c "import numpy" 2>/dev/null && echo -e "${GREEN}✅ numpy${NC}" || echo -e "${YELLOW}⚠️  numpy no instalado${NC}"
        python3 -c "import openai" 2>/dev/null && echo -e "${GREEN}✅ openai${NC}" || echo -e "${YELLOW}⚠️  openai no instalado${NC}"
        
        echo ""
        echo "💡 Para instalar dependencias Python:"
        echo "   pip3 install pandas numpy matplotlib seaborn scikit-learn openai"
    fi
}

# Verificar dependencias del sistema
echo "📋 Verificando dependencias del sistema..."
echo ""

check_command node
check_command npm
check_command n8n || echo -e "${YELLOW}⚠️  n8n no encontrado. Instala con: npm install -g n8n${NC}"

check_command ffmpeg || echo -e "${YELLOW}⚠️  ffmpeg no encontrado. Necesario para edición de video${NC}"
check_command ffprobe || echo -e "${YELLOW}⚠️  ffprobe no encontrado. Necesario para análisis de video${NC}"
check_command yt-dlp || echo -e "${YELLOW}⚠️  yt-dlp no encontrado. Necesario para descarga de videos${NC}"

check_python

# Verificar estructura de directorios
echo ""
echo "📁 Verificando estructura de directorios..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
N8N_DIR="$(dirname "$SCRIPT_DIR")"
BASE_DIR="$(dirname "$N8N_DIR")"

echo "   Directorio base: $BASE_DIR"
echo "   Directorio n8n: $N8N_DIR"
echo "   Directorio scripts: $SCRIPT_DIR"

# Crear directorios necesarios
echo ""
echo "📂 Creando directorios necesarios..."
mkdir -p "$BASE_DIR/data/exports"
mkdir -p "$BASE_DIR/data/reports"
mkdir -p "$BASE_DIR/data/temp"
mkdir -p "$BASE_DIR/data/videos"
mkdir -p "$BASE_DIR/logs"
echo -e "${GREEN}✅ Directorios creados${NC}"

# Verificar archivos de configuración
echo ""
echo "⚙️  Verificando archivos de configuración..."

ENV_FILE="$N8N_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    echo ""
    echo "📝 Creando archivo .env de ejemplo..."
    cat > "$ENV_FILE.example" << 'EOF'
# APIs Básicas (Requeridas)
OPENAI_API_KEY=tu-openai-key-aqui
GEMINI_API_KEY=tu-gemini-key-aqui
INSTAGRAM_ACCESS_TOKEN=tu-instagram-token-aqui
TIKTOK_ACCESS_TOKEN=tu-tiktok-token-aqui
YOUTUBE_API_KEY=tu-youtube-key-aqui

# Telegram (Recomendado)
TELEGRAM_BOT_TOKEN=tu-telegram-bot-token-aqui
TELEGRAM_CHAT_ID=tu-chat-id-aqui

# Feature Flags
ENABLE_TRACKING=true
ENABLE_VISION_ANALYSIS=true
ENABLE_THUMBNAIL_GEN=true
ENABLE_SMART_SCHEDULING=true
ENABLE_ENGAGEMENT_TRACKING=true
ENABLE_AUTO_OPTIMIZATION=true
ENABLE_PREDICTION=true
ENABLE_AB_TESTING=false
ENABLE_PYTHON_INTEGRATION=true

# Python Integration
PYTHON_SCRIPT_PATH=/Users/adan/IA/scripts/analisis_engagement_contenido.py
PYTHON_OUTPUT_DIR=/tmp
PYTHON_MIN_VIDEOS=5

# Rate Limits
INSTAGRAM_RATE_LIMIT=25
TIKTOK_RATE_LIMIT=10
YOUTUBE_RATE_LIMIT=6

# Umbrales
VIRAL_THRESHOLD_ENGAGEMENT_RATE=10.0
VIRAL_THRESHOLD_TOTAL_ENGAGEMENT=500
LOW_PERFORMANCE_THRESHOLD=3.0

# Optimización
LEARNING_WINDOW_DAYS=30
MIN_VIDEOS_FOR_LEARNING=10
TREND_WINDOW_DAYS=7

# Reportes
REPORT_TYPE=weekly
ENABLE_AUTO_REPORTS=true
REPORT_EMAIL=tu@email.com
EOF
    echo -e "${GREEN}✅ Archivo .env.example creado${NC}"
    echo -e "${YELLOW}⚠️  Copia .env.example a .env y configura tus API keys${NC}"
else
    echo -e "${GREEN}✅ Archivo .env encontrado${NC}"
fi

# Verificar workflows
echo ""
echo "📋 Verificando workflows..."
WORKFLOWS=(
    "n8n_workflow_sora_auto_upload.json"
    "n8n_workflow_sora_auto_upload_improved.json"
    "n8n_workflow_sora_ultimate.json"
)

for workflow in "${WORKFLOWS[@]}"; do
    if [ -f "$N8N_DIR/$workflow" ]; then
        echo -e "${GREEN}✅ $workflow${NC}"
    else
        echo -e "${YELLOW}⚠️  $workflow no encontrado${NC}"
    fi
done

# Verificar nodos adicionales
echo ""
echo "🔧 Verificando nodos adicionales..."
NODES=(
    "nodos_adicionales_sora.json"
    "nodos_engagement_optimization.json"
    "nodos_predictivos_avanzados.json"
    "nodos_enterprise.json"
    "nodos_integracion_python.json"
)

for node in "${NODES[@]}"; do
    if [ -f "$N8N_DIR/$node" ]; then
        echo -e "${GREEN}✅ $node${NC}"
    else
        echo -e "${YELLOW}⚠️  $node no encontrado${NC}"
    fi
done

# Verificar script Python
echo ""
echo "🐍 Verificando script Python de análisis..."
PYTHON_SCRIPT="$BASE_DIR/scripts/analisis_engagement_contenido.py"
if [ -f "$PYTHON_SCRIPT" ]; then
    echo -e "${GREEN}✅ Script Python encontrado${NC}"
    if [ -x "$PYTHON_SCRIPT" ]; then
        echo -e "${GREEN}✅ Script ejecutable${NC}"
    else
        echo -e "${YELLOW}⚠️  Haciendo script ejecutable...${NC}"
        chmod +x "$PYTHON_SCRIPT"
    fi
else
    echo -e "${YELLOW}⚠️  Script Python no encontrado en $PYTHON_SCRIPT${NC}"
fi

# Verificar permisos
echo ""
echo "🔐 Verificando permisos..."
chmod +x "$SCRIPT_DIR"/*.sh 2>/dev/null || true
echo -e "${GREEN}✅ Permisos configurados${NC}"

# Resumen final
echo ""
echo "=================================================="
echo "✅ Verificación completada"
echo "=================================================="
echo ""
echo "📝 Próximos pasos:"
echo "   1. Copia .env.example a .env y configura tus API keys"
echo "   2. Instala dependencias Python si es necesario:"
echo "      pip3 install pandas numpy matplotlib seaborn scikit-learn openai"
echo "   3. Importa el workflow en n8n"
echo "   4. Configura las credenciales en n8n"
echo "   5. Activa el workflow"
echo ""
echo "📚 Documentación disponible en:"
echo "   - README_FINAL_SISTEMA_COMPLETO.md"
echo "   - README_SORA_AUTO_UPLOAD.md"
echo "   - COMPARACION_VERSIONES_SORA.md"
echo ""
echo "🚀 ¡Listo para empezar!"



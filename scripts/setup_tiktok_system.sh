#!/bin/bash
# Script de configuración inicial del sistema TikTok Auto Edit

set -e

echo "🎬 Configurando TikTok Auto Edit System..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar Python
echo "📦 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar FFmpeg
echo "📦 Verificando FFmpeg..."
if ! command -v ffmpeg &> /dev/null; then
    echo "⚠️  FFmpeg no está instalado"
    echo "   Instálalo con: brew install ffmpeg (macOS) o sudo apt-get install ffmpeg (Linux)"
else
    FFMPEG_VERSION=$(ffmpeg -version | head -n1 | cut -d' ' -f3)
    echo "✅ FFmpeg $FFMPEG_VERSION encontrado"
fi

# Instalar dependencias Python
echo ""
echo "📦 Instalando dependencias Python..."
pip3 install -r tiktok_requirements.txt
echo "✅ Dependencias instaladas"

# Crear directorios necesarios
echo ""
echo "📁 Creando directorios..."
mkdir -p ~/.tiktok_cache
mkdir -p ~/.tiktok_templates
mkdir -p /tmp/tiktok_downloads
mkdir -p /tmp/tiktok_edited
echo "✅ Directorios creados"

# Inicializar templates
echo ""
echo "🎨 Inicializando templates..."
python3 tiktok_templates.py init
echo "✅ Templates inicializados"

# Verificar variables de entorno
echo ""
echo "🔧 Verificando configuración..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY no está configurada${NC}"
    echo "   Configúrala con: export OPENAI_API_KEY='sk-...'"
else
    echo "✅ OPENAI_API_KEY configurada"
fi

# Optimizar sistema
echo ""
echo "⚡ Analizando sistema para optimización..."
python3 tiktok_optimizer.py analyze > /tmp/system_analysis.json
echo "✅ Análisis completado (guardado en /tmp/system_analysis.json)"

# Generar configuración
echo ""
echo "⚙️  Generando configuración optimizada..."
python3 tiktok_optimizer.py config -o ~/.tiktok_config.json
echo "✅ Configuración guardada en ~/.tiktok_config.json"

# Resumen
echo ""
echo -e "${GREEN}✅ Configuración completada!${NC}"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Configura OPENAI_API_KEY si no lo has hecho"
echo "   2. Configura notificaciones (opcional):"
echo "      - TELEGRAM_BOT_TOKEN"
echo "      - SLACK_WEBHOOK_URL"
echo "      - Email SMTP settings"
echo "   3. Prueba el sistema:"
echo "      python3 tiktok_downloader.py 'https://www.tiktok.com/@user/video/123'"
echo ""
echo "📚 Documentación:"
echo "   - scripts/README_FINAL.md"
echo "   - docs/N8N_TIKTOK_AUTO_EDIT.md"
echo ""



#!/bin/bash

# Script de configuración para el workflow de Sora Auto Upload

set -e

echo "🎬 Configuración del Workflow de Sora Auto Upload"
echo "================================================"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Verificar dependencias
echo "📦 Verificando dependencias..."

# FFmpeg
if command -v ffmpeg &> /dev/null; then
    echo -e "${GREEN}✓${NC} FFmpeg instalado: $(ffmpeg -version | head -n 1)"
else
    echo -e "${RED}✗${NC} FFmpeg no encontrado"
    echo "  Instala con: brew install ffmpeg (macOS) o sudo apt-get install ffmpeg (Linux)"
    exit 1
fi

# yt-dlp
if command -v yt-dlp &> /dev/null; then
    echo -e "${GREEN}✓${NC} yt-dlp instalado: $(yt-dlp --version)"
else
    echo -e "${YELLOW}⚠${NC} yt-dlp no encontrado"
    echo "  Instalando yt-dlp..."
    pip3 install yt-dlp || pip install yt-dlp
    echo -e "${GREEN}✓${NC} yt-dlp instalado"
fi

# Python
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✓${NC} Python instalado: $(python3 --version)"
else
    echo -e "${RED}✗${NC} Python3 no encontrado"
    exit 1
fi

echo ""
echo "🔑 Configuración de Variables de Entorno"
echo "========================================"
echo ""
echo "Necesitarás configurar las siguientes variables de entorno en n8n:"
echo ""
echo "APIs de IA:"
echo "  - OPENAI_API_KEY (requerido para ChatGPT)"
echo "  - GEMINI_API_KEY (requerido para Gemini)"
echo ""
echo "Redes Sociales:"
echo "  - INSTAGRAM_ACCOUNT_ID"
echo "  - INSTAGRAM_ACCESS_TOKEN"
echo "  - TIKTOK_ACCESS_TOKEN"
echo "  - YOUTUBE_API_KEY"
echo ""
echo "Configuración:"
echo "  - MIN_VIEWS=1000 (mínimo de visualizaciones para procesar)"
echo ""

# Crear archivo de ejemplo de variables de entorno
ENV_EXAMPLE_FILE="sora_workflow_env.example"
cat > "$ENV_EXAMPLE_FILE" << 'EOF'
# APIs de IA
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here

# Redes Sociales - Instagram
INSTAGRAM_ACCOUNT_ID=your-instagram-account-id
INSTAGRAM_ACCESS_TOKEN=your-instagram-access-token

# Redes Sociales - TikTok
TIKTOK_ACCESS_TOKEN=your-tiktok-access-token

# Redes Sociales - YouTube
YOUTUBE_API_KEY=your-youtube-api-key

# Configuración
MIN_VIEWS=1000
EOF

echo -e "${GREEN}✓${NC} Archivo de ejemplo creado: $ENV_EXAMPLE_FILE"
echo ""

# Verificar directorio temporal
TMP_DIR="/tmp"
if [ -d "$TMP_DIR" ] && [ -w "$TMP_DIR" ]; then
    echo -e "${GREEN}✓${NC} Directorio temporal accesible: $TMP_DIR"
else
    echo -e "${RED}✗${NC} No se puede escribir en $TMP_DIR"
    exit 1
fi

# Crear script de limpieza
CLEANUP_SCRIPT="cleanup_sora_videos.sh"
cat > "$CLEANUP_SCRIPT" << 'EOF'
#!/bin/bash
# Script para limpiar videos temporales de Sora (ejecutar diariamente con cron)

find /tmp -name "sora_video_*" -type f -mtime +1 -delete
find /tmp -name "sora_edited_*" -type f -mtime +1 -delete

echo "Limpieza completada: $(date)"
EOF

chmod +x "$CLEANUP_SCRIPT"
echo -e "${GREEN}✓${NC} Script de limpieza creado: $CLEANUP_SCRIPT"
echo "  Ejecuta 'crontab -e' y agrega: 0 2 * * * $(pwd)/$CLEANUP_SCRIPT"
echo ""

# Verificar workflow JSON
if [ -f "n8n_workflow_sora_auto_upload.json" ]; then
    if python3 -m json.tool n8n_workflow_sora_auto_upload.json > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Workflow JSON válido"
    else
        echo -e "${RED}✗${NC} Workflow JSON tiene errores de sintaxis"
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Archivo n8n_workflow_sora_auto_upload.json no encontrado"
    exit 1
fi

echo ""
echo "📋 Próximos Pasos"
echo "=================="
echo ""
echo "1. Importa el workflow en n8n:"
echo "   - Abre n8n"
echo "   - Ve a Workflows → Import from File"
echo "   - Selecciona: n8n_workflow_sora_auto_upload.json"
echo ""
echo "2. Configura las variables de entorno en n8n:"
echo "   - Ve a Settings → Environment Variables"
echo "   - Agrega las variables del archivo $ENV_EXAMPLE_FILE"
echo ""
echo "3. Configura las credenciales en n8n:"
echo "   - OpenAI API: HTTP Header Auth con Authorization: Bearer YOUR_KEY"
echo "   - Instagram: OAuth2 con tu Instagram Business API"
echo "   - TikTok: HTTP Header Auth con Authorization: Bearer YOUR_TOKEN"
echo "   - YouTube: OAuth2 con YouTube Data API v3"
echo ""
echo "4. Activa el workflow en n8n"
echo ""
echo "5. (Opcional) Configura limpieza automática:"
echo "   crontab -e"
echo "   # Agrega esta línea para limpiar a las 2 AM diariamente:"
echo "   0 2 * * * $(pwd)/$CLEANUP_SCRIPT"
echo ""
echo -e "${GREEN}¡Configuración completada!${NC}"
echo ""
echo "📚 Lee README_SORA_AUTO_UPLOAD.md para más información"



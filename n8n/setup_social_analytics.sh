#!/bin/bash

# Script de configuración para el workflow de Análisis de Estadísticas Orgánicas
# Este script ayuda a configurar las variables de entorno necesarias

echo "🚀 Configuración del Workflow de Análisis de Estadísticas Orgánicas"
echo "=================================================================="
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para validar si una variable está configurada
check_env_var() {
    if [ -z "${!1}" ]; then
        echo -e "${RED}❌ $1 no está configurada${NC}"
        return 1
    else
        echo -e "${GREEN}✅ $1 está configurada${NC}"
        return 0
    fi
}

# Función para solicitar input del usuario
ask_for_input() {
    local var_name=$1
    local prompt=$2
    local is_secret=${3:-false}
    
    if [ "$is_secret" = true ]; then
        read -sp "$prompt: " value
        echo ""
    else
        read -p "$prompt: " value
    fi
    
    echo "export $var_name=\"$value\"" >> .env.social_analytics
}

echo "📋 Verificando variables de entorno actuales..."
echo ""

# Verificar variables existentes
MISSING_VARS=0

echo "🔑 Credenciales Requeridas:"
check_env_var "OPENAI_API_KEY" || MISSING_VARS=$((MISSING_VARS + 1))

echo ""
echo "📱 Credenciales de Redes Sociales (al menos una requerida):"
check_env_var "INSTAGRAM_ACCESS_TOKEN" || true
check_env_var "INSTAGRAM_ACCOUNT_ID" || true
check_env_var "TIKTOK_ACCESS_TOKEN" || true
check_env_var "YOUTUBE_API_KEY" || true
check_env_var "YOUTUBE_CHANNEL_ID" || true

echo ""
echo "📲 Credenciales Opcionales:"
check_env_var "TELEGRAM_BOT_TOKEN" || true
check_env_var "TELEGRAM_CHAT_ID" || true

echo ""
echo "⚙️ Configuración del Workflow:"
check_env_var "DAYS_BACK" || echo -e "${YELLOW}⚠️  DAYS_BACK no configurada (usará 7 por defecto)${NC}"
check_env_var "TOP_N_POSTS" || echo -e "${YELLOW}⚠️  TOP_N_POSTS no configurada (usará 10 por defecto)${NC}"
check_env_var "OPENAI_MODEL" || echo -e "${YELLOW}⚠️  OPENAI_MODEL no configurada (usará gpt-4 por defecto)${NC}"

echo ""
if [ $MISSING_VARS -eq 0 ]; then
    echo -e "${GREEN}✅ Todas las variables requeridas están configuradas${NC}"
else
    echo -e "${YELLOW}⚠️  Faltan algunas variables requeridas${NC}"
    echo ""
    read -p "¿Deseas configurar las variables faltantes ahora? (y/n): " setup_now
    
    if [ "$setup_now" = "y" ] || [ "$setup_now" = "Y" ]; then
        echo ""
        echo "📝 Configuración interactiva..."
        echo ""
        
        # Crear archivo .env si no existe
        if [ ! -f .env.social_analytics ]; then
            touch .env.social_analytics
            echo "# Variables de entorno para Social Analytics Workflow" >> .env.social_analytics
            echo "# Generado el $(date)" >> .env.social_analytics
            echo "" >> .env.social_analytics
        fi
        
        # OpenAI (Requerido)
        if [ -z "$OPENAI_API_KEY" ]; then
            ask_for_input "OPENAI_API_KEY" "Ingresa tu OpenAI API Key" true
        fi
        
        # Instagram
        echo ""
        read -p "¿Deseas configurar Instagram? (y/n): " setup_instagram
        if [ "$setup_instagram" = "y" ] || [ "$setup_instagram" = "Y" ]; then
            if [ -z "$INSTAGRAM_ACCESS_TOKEN" ]; then
                ask_for_input "INSTAGRAM_ACCESS_TOKEN" "Ingresa tu Instagram Access Token" true
            fi
            if [ -z "$INSTAGRAM_ACCOUNT_ID" ]; then
                ask_for_input "INSTAGRAM_ACCOUNT_ID" "Ingresa tu Instagram Account ID"
            fi
        fi
        
        # TikTok
        echo ""
        read -p "¿Deseas configurar TikTok? (y/n): " setup_tiktok
        if [ "$setup_tiktok" = "y" ] || [ "$setup_tiktok" = "Y" ]; then
            if [ -z "$TIKTOK_ACCESS_TOKEN" ]; then
                ask_for_input "TIKTOK_ACCESS_TOKEN" "Ingresa tu TikTok Access Token" true
            fi
        fi
        
        # YouTube
        echo ""
        read -p "¿Deseas configurar YouTube? (y/n): " setup_youtube
        if [ "$setup_youtube" = "y" ] || [ "$setup_youtube" = "Y" ]; then
            if [ -z "$YOUTUBE_API_KEY" ]; then
                ask_for_input "YOUTUBE_API_KEY" "Ingresa tu YouTube API Key" true
            fi
            if [ -z "$YOUTUBE_CHANNEL_ID" ]; then
                ask_for_input "YOUTUBE_CHANNEL_ID" "Ingresa tu YouTube Channel ID (opcional)"
            fi
        fi
        
        # Telegram (Opcional)
        echo ""
        read -p "¿Deseas configurar Telegram para notificaciones? (y/n): " setup_telegram
        if [ "$setup_telegram" = "y" ] || [ "$setup_telegram" = "Y" ]; then
            if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
                ask_for_input "TELEGRAM_BOT_TOKEN" "Ingresa tu Telegram Bot Token" true
            fi
            if [ -z "$TELEGRAM_CHAT_ID" ]; then
                ask_for_input "TELEGRAM_CHAT_ID" "Ingresa tu Telegram Chat ID"
            fi
        fi
        
        # Configuración del workflow
        echo ""
        read -p "¿Deseas configurar parámetros del workflow? (y/n): " setup_workflow
        if [ "$setup_workflow" = "y" ] || [ "$setup_workflow" = "Y" ]; then
            if [ -z "$DAYS_BACK" ]; then
                ask_for_input "DAYS_BACK" "Días hacia atrás para analizar (default: 7)"
            fi
            if [ -z "$TOP_N_POSTS" ]; then
                ask_for_input "TOP_N_POSTS" "Número de posts top a analizar (default: 10)"
            fi
            if [ -z "$OPENAI_MODEL" ]; then
                ask_for_input "OPENAI_MODEL" "Modelo de OpenAI a usar (default: gpt-4)"
            fi
        fi
        
        echo ""
        echo -e "${GREEN}✅ Configuración guardada en .env.social_analytics${NC}"
        echo ""
        echo "Para cargar las variables en tu sesión actual, ejecuta:"
        echo -e "${YELLOW}source .env.social_analytics${NC}"
        echo ""
        echo "Para n8n, configura estas variables en la interfaz de n8n:"
        echo "- Ve a Settings → Environment Variables"
        echo "- O configura las variables de entorno del sistema"
    fi
fi

echo ""
echo "📚 Recursos útiles:"
echo "  - Instagram API: https://developers.facebook.com/docs/instagram-api"
echo "  - TikTok API: https://developers.tiktok.com/"
echo "  - YouTube API: https://developers.google.com/youtube/v3"
echo "  - OpenAI API: https://platform.openai.com/"
echo ""
echo "📖 Documentación completa: README_SOCIAL_ANALYTICS_AI.md"
echo ""

# Crear directorio de reportes si no existe
REPORTS_DIR="/Users/adan/IA/reports/social_analytics"
if [ ! -d "$REPORTS_DIR" ]; then
    mkdir -p "$REPORTS_DIR"
    echo -e "${GREEN}✅ Directorio de reportes creado: $REPORTS_DIR${NC}"
fi

echo ""
echo "🎉 Configuración completada!"
echo ""




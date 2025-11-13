#!/bin/bash
# Monitor del Sistema Sora Workflow
# ===================================

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "📊 Monitor del Sistema Sora Workflow"
echo "====================================="
echo ""

# Verificar estado de n8n
echo "🔍 Estado de n8n:"
if pgrep -x "n8n" > /dev/null; then
    echo -e "${GREEN}✅ n8n está corriendo${NC}"
    N8N_PID=$(pgrep -x "n8n")
    echo "   PID: $N8N_PID"
else
    echo -e "${RED}❌ n8n no está corriendo${NC}"
fi

# Verificar uso de recursos
echo ""
echo "💻 Uso de recursos:"
if command -v top &> /dev/null; then
    echo "   CPU y Memoria del proceso n8n:"
    ps aux | grep n8n | grep -v grep | awk '{print "   CPU: " $3 "% | Memoria: " $4 "%"}'
fi

# Verificar espacio en disco
echo ""
echo "💾 Espacio en disco:"
df -h . | tail -1 | awk '{print "   Disponible: " $4 " de " $2 " (" $5 " usado)"}'

# Verificar archivos de logs recientes
echo ""
echo "📝 Logs recientes:"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
N8N_DIR="$(dirname "$SCRIPT_DIR")"
if [ -d "$N8N_DIR/logs" ]; then
    echo "   Últimos 5 archivos de log:"
    ls -lt "$N8N_DIR/logs" 2>/dev/null | head -6 | tail -5 | awk '{print "   - " $9 " (" $6 " " $7 " " $8 ")"}'
else
    echo -e "${YELLOW}⚠️  Directorio de logs no encontrado${NC}"
fi

# Verificar workflows activos (requiere acceso a API de n8n)
echo ""
echo "🔄 Workflows:"
if command -v curl &> /dev/null && [ -n "$N8N_API_URL" ]; then
    echo "   Verificando workflows activos..."
    curl -s "$N8N_API_URL/workflows" | jq -r '.[] | select(.active == true) | "   ✅ \(.name)"' 2>/dev/null || echo -e "${YELLOW}⚠️  No se pudo verificar workflows (API no disponible)${NC}"
else
    echo -e "${YELLOW}⚠️  API de n8n no configurada${NC}"
fi

# Verificar APIs externas
echo ""
echo "🌐 Estado de APIs externas:"
APIS=(
    "OpenAI:https://api.openai.com/v1/models"
    "Google:https://www.googleapis.com"
)

for api in "${APIS[@]}"; do
    NAME=$(echo $api | cut -d: -f1)
    URL=$(echo $api | cut -d: -f2)
    if curl -s --head "$URL" > /dev/null 2>&1; then
        echo -e "   ${GREEN}✅ $NAME${NC}"
    else
        echo -e "   ${YELLOW}⚠️  $NAME (no verificado)${NC}"
    fi
done

# Verificar dependencias críticas
echo ""
echo "🔧 Dependencias críticas:"
check_dep() {
    if command -v $1 &> /dev/null; then
        echo -e "   ${GREEN}✅ $1${NC}"
    else
        echo -e "   ${RED}❌ $1${NC}"
    fi
}

check_dep ffmpeg
check_dep ffprobe
check_dep yt-dlp
check_dep python3

# Verificar archivos de configuración
echo ""
echo "⚙️  Configuración:"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
N8N_DIR="$(dirname "$SCRIPT_DIR")"

if [ -f "$N8N_DIR/.env" ]; then
    echo -e "   ${GREEN}✅ Archivo .env encontrado${NC}"
    # Verificar variables críticas (sin mostrar valores)
    MISSING_VARS=()
    source "$N8N_DIR/.env" 2>/dev/null || true
    [ -z "$OPENAI_API_KEY" ] && MISSING_VARS+=("OPENAI_API_KEY")
    [ -z "$GEMINI_API_KEY" ] && MISSING_VARS+=("GEMINI_API_KEY")
    
    if [ ${#MISSING_VARS[@]} -eq 0 ]; then
        echo -e "   ${GREEN}✅ Variables críticas configuradas${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Variables faltantes: ${MISSING_VARS[*]}${NC}"
    fi
else
    echo -e "   ${RED}❌ Archivo .env no encontrado${NC}"
fi

# Estadísticas del sistema
echo ""
echo "📊 Estadísticas:"
if [ -d "$N8N_DIR/data" ]; then
    VIDEO_COUNT=$(find "$N8N_DIR/data/videos" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "   Videos procesados: $VIDEO_COUNT"
fi

if [ -d "$N8N_DIR/data/exports" ]; then
    EXPORT_COUNT=$(find "$N8N_DIR/data/exports" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "   Archivos exportados: $EXPORT_COUNT"
fi

# Resumen de salud
echo ""
echo "====================================="
echo "🏥 Resumen de Salud del Sistema"
echo "====================================="

HEALTH_SCORE=0
MAX_SCORE=7

[ -f "$N8N_DIR/.env" ] && HEALTH_SCORE=$((HEALTH_SCORE + 1))
pgrep -x "n8n" > /dev/null && HEALTH_SCORE=$((HEALTH_SCORE + 1))
command -v ffmpeg &> /dev/null && HEALTH_SCORE=$((HEALTH_SCORE + 1))
command -v yt-dlp &> /dev/null && HEALTH_SCORE=$((HEALTH_SCORE + 1))
command -v python3 &> /dev/null && HEALTH_SCORE=$((HEALTH_SCORE + 1))
[ -d "$N8N_DIR/data" ] && HEALTH_SCORE=$((HEALTH_SCORE + 1))
[ -d "$N8N_DIR/logs" ] && HEALTH_SCORE=$((HEALTH_SCORE + 1))

PERCENTAGE=$((HEALTH_SCORE * 100 / MAX_SCORE))

if [ $PERCENTAGE -ge 80 ]; then
    COLOR=$GREEN
    STATUS="Excelente"
elif [ $PERCENTAGE -ge 60 ]; then
    COLOR=$YELLOW
    STATUS="Bueno"
else
    COLOR=$RED
    STATUS="Necesita Atención"
fi

echo -e "${COLOR}Estado: $STATUS ($PERCENTAGE%)${NC}"
echo "   Puntos: $HEALTH_SCORE/$MAX_SCORE"
echo ""
echo "💡 Para más información:"
echo "   - Revisa los logs en: $N8N_DIR/logs"
echo "   - Verifica la configuración en: $N8N_DIR/.env"
echo "   - Consulta la documentación en: README_FINAL_SISTEMA_COMPLETO.md"



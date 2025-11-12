#!/bin/bash
# Quick Start Script - Inicia todos los servicios del sistema

set -e

echo "🎬 TikTok Auto Edit - Quick Start"
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar que estamos en el directorio correcto
if [ ! -f "tiktok_downloader.py" ]; then
    echo "❌ Ejecuta este script desde el directorio scripts/"
    exit 1
fi

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

# Verificar variables de entorno
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY no configurada${NC}"
    echo "   Algunas funcionalidades pueden no funcionar"
fi

# Función para iniciar servicio en background
start_service() {
    local name=$1
    local command=$2
    local port=$3
    
    echo "🚀 Iniciando $name en puerto $port..."
    nohup python3 $command > /tmp/${name}.log 2>&1 &
    echo $! > /tmp/${name}.pid
    sleep 2
    
    if ps -p $(cat /tmp/${name}.pid) > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name iniciado (PID: $(cat /tmp/${name}.pid))${NC}"
    else
        echo -e "${YELLOW}⚠️  $name puede no haber iniciado correctamente${NC}"
    fi
}

# Iniciar servicios
echo "Iniciando servicios..."
echo ""

start_service "tiktok_api" "tiktok_api_server.py -p 5000" 5000
start_service "tiktok_webhook" "tiktok_webhook_handler.py -p 5001" 5001
start_service "tiktok_dashboard" "tiktok_dashboard.py -p 5002" 5002

# Queue Manager (diferente, no es servidor HTTP)
echo ""
echo "🚀 Iniciando Queue Manager..."
nohup python3 tiktok_queue_manager.py start -w 3 > /tmp/tiktok_queue.log 2>&1 &
echo $! > /tmp/tiktok_queue.pid
sleep 2
echo -e "${GREEN}✅ Queue Manager iniciado (PID: $(cat /tmp/tiktok_queue.pid))${NC}"

echo ""
echo "="*60
echo -e "${GREEN}✅ Todos los servicios iniciados${NC}"
echo "="*60
echo ""
echo "📊 Servicios:"
echo "  • API REST: http://localhost:5000"
echo "  • Webhooks: http://localhost:5001"
echo "  • Dashboard: http://localhost:5002"
echo "  • Queue Manager: Ejecutándose en background"
echo ""
echo "📝 Logs:"
echo "  • API: /tmp/tiktok_api.log"
echo "  • Webhook: /tmp/tiktok_webhook.log"
echo "  • Dashboard: /tmp/tiktok_dashboard.log"
echo "  • Queue: /tmp/tiktok_queue.log"
echo ""
echo "🛑 Para detener:"
echo "  ./stop_services.sh"
echo ""


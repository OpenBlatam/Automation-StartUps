#!/bin/bash
# Script de Monitoreo Continuo del Sistema de Ventas
# Ejecuta health checks periódicos y alerta sobre problemas

set -e

# Configuración
DB_CONN="${SALES_DB_CONN:-}"
CHECK_INTERVAL="${CHECK_INTERVAL:-300}" # 5 minutos por defecto
ALERT_WEBHOOK="${ALERT_WEBHOOK:-}"
LOG_FILE="${LOG_FILE:-/tmp/sales_monitor.log}"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_health() {
    local status=$(python3 scripts/sales_health_check.py --db "$DB_CONN" --json 2>/dev/null | jq -r '.status')
    echo "$status"
}

send_alert() {
    local message="$1"
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"🚨 Sales System Alert: $message\"}" \
            > /dev/null 2>&1 || true
    fi
    log "ALERT: $message"
}

# Verificar configuración
if [ -z "$DB_CONN" ]; then
    echo "Error: SALES_DB_CONN no configurado"
    echo "Uso: SALES_DB_CONN='postgresql://...' $0"
    exit 1
fi

# Verificar dependencias
if ! command -v jq &> /dev/null; then
    echo "Warning: jq no encontrado. Instalando..."
    # Intentar instalar (requiere permisos)
fi

log "Iniciando monitoreo del sistema de ventas"
log "Intervalo: ${CHECK_INTERVAL}s"
log "Webhook: ${ALERT_WEBHOOK:-No configurado}"

# Estado anterior
previous_status="healthy"
consecutive_errors=0

# Loop de monitoreo
while true; do
    status=$(check_health)
    
    if [ "$status" = "critical" ]; then
        consecutive_errors=$((consecutive_errors + 1))
        if [ "$consecutive_errors" -ge 2 ]; then
            send_alert "Estado CRITICAL detectado. Sistema requiere atención inmediata."
        fi
    elif [ "$status" = "degraded" ]; then
        if [ "$previous_status" = "healthy" ]; then
            send_alert "Sistema degradado. Revisar métricas."
        fi
        consecutive_errors=0
    else
        if [ "$previous_status" != "healthy" ]; then
            log "✅ Sistema recuperado - estado: healthy"
        fi
        consecutive_errors=0
    fi
    
    previous_status="$status"
    
    sleep "$CHECK_INTERVAL"
done



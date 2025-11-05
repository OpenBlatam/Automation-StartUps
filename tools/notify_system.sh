#!/usr/bin/env bash
# Sistema de notificaciones: envía notificaciones por múltiples canales

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NOTIFICATION_TYPE="${1:-}"
MESSAGE="${2:-}"
PRIORITY="${3:-info}"

show_help() {
  cat <<EOF
Uso: bash tools/notify_system.sh [type] [message] [priority]

Sistema de notificaciones multi-canal

Tipos:
  alert_critical      Alerta crítica
  alert_warning       Alerta de advertencia
  success             Operación exitosa
  info                Información general

Prioridades:
  critical, warning, info, success

Variables de entorno:
  SLACK_WEBHOOK       URL webhook de Slack
  DISCORD_WEBHOOK     URL webhook de Discord
  EMAIL_TO            Email para notificaciones
  NOTIFY_CONSOLE      true/false (default: true)

Ejemplos:
  bash tools/notify_system.sh alert_critical "Health score crítico" critical
  bash tools/notify_system.sh success "Build completado" success
  bash tools/notify_system.sh info "Validación exitosa" info

EOF
}

if [ -z "$NOTIFICATION_TYPE" ] || [ -z "$MESSAGE" ]; then
  show_help
  exit 0
fi

# Configuración de colores y emojis
case "$PRIORITY" in
  critical)
    COLOR="#ff0000"
    EMOJI="🔴"
    ;;
  warning)
    COLOR="#ff9800"
    EMOJI="🟠"
    ;;
  success)
    COLOR="#4caf50"
    EMOJI="✅"
    ;;
  info|*)
    COLOR="#2196f3"
    EMOJI="ℹ️"
    ;;
esac

# Notificación en consola
if [ "${NOTIFY_CONSOLE:-true}" = "true" ]; then
  echo "${EMOJI} ${MESSAGE}"
fi

# Webhook Slack
if [ -n "${SLACK_WEBHOOK:-}" ] && command -v curl &> /dev/null; then
  PAYLOAD=$(cat <<EOF
{
  "text": "${EMOJI} ${MESSAGE}",
  "attachments": [{
    "color": "${COLOR}",
    "title": "Assets System Notification",
    "text": "${MESSAGE}",
    "footer": "Assets Management System",
    "ts": $(date +%s)
  }]
}
EOF
)
  
  curl -X POST -H 'Content-type: application/json' \
    --data "$PAYLOAD" \
    "$SLACK_WEBHOOK" > /dev/null 2>&1 || true
fi

# Webhook Discord
if [ -n "${DISCORD_WEBHOOK:-}" ] && command -v curl &> /dev/null; then
  PAYLOAD=$(cat <<EOF
{
  "embeds": [{
    "title": "${EMOJI} Assets System",
    "description": "${MESSAGE}",
    "color": $(echo "$COLOR" | sed 's/#//' | awk '{printf "%d", strtonum("0x"$0)}'),
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  }]
}
EOF
)
  
  curl -X POST -H 'Content-type: application/json' \
    --data "$PAYLOAD" \
    "$DISCORD_WEBHOOK" > /dev/null 2>&1 || true
fi

# Email (requiere mail command)
if [ -n "${EMAIL_TO:-}" ] && command -v mail &> /dev/null; then
  if [ "$PRIORITY" = "critical" ] || [ "$PRIORITY" = "warning" ]; then
    echo "$MESSAGE" | mail -s "${EMOJI} Assets System: ${NOTIFICATION_TYPE}" "$EMAIL_TO" 2>/dev/null || true
  fi
fi

# Log file
LOG_FILE="$ROOT_DIR/exports/notifications.log"
mkdir -p "$(dirname "$LOG_FILE")"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] [$PRIORITY] ${EMOJI} ${MESSAGE}" >> "$LOG_FILE"

echo "✅ Notificación enviada"


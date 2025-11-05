#!/usr/bin/env bash
# Integración webhook: notifica a servicios externos sobre cambios

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEBHOOK_URL="${WEBHOOK_URL:-}"
EVENT="${1:-}"
PAYLOAD="${2:-}"

show_help() {
  cat <<EOF
Uso: bash tools/integration_webhook.sh [event] [payload]

Envía notificaciones webhook a servicios externos

Eventos:
  build_complete       Build completado
  validation_failed    Validación falló
  alert_critical       Alerta crítica
  backup_created      Backup creado
  health_score_low     Health score bajo

Variables de entorno:
  WEBHOOK_URL          URL del webhook (requerido)

Ejemplos:
  export WEBHOOK_URL="https://hooks.slack.com/..."
  bash tools/integration_webhook.sh build_complete "Build completado exitosamente"
  bash tools/integration_webhook.sh alert_critical "Health score crítico: 45/100"

EOF
}

if [ -z "$WEBHOOK_URL" ]; then
  echo "⚠️  WEBHOOK_URL no configurado"
  echo ""
  show_help
  exit 0
fi

send_webhook() {
  local event="$1"
  local message="${2:-}"
  
  local color
  case "$event" in
    build_complete) color="#36a64f" ;;  # Verde
    validation_failed|alert_critical|health_score_low) color="#ff0000" ;;  # Rojo
    backup_created) color="#36a64f" ;;
    *) color="#ffa500" ;;  # Naranja
  esac
  
  local emoji
  case "$event" in
    build_complete) emoji="✅" ;;
    validation_failed) emoji="❌" ;;
    alert_critical) emoji="🔴" ;;
    backup_created) emoji="💾" ;;
    health_score_low) emoji="⚠️" ;;
    *) emoji="ℹ️" ;;
  esac
  
  local payload
  if command -v jq &> /dev/null; then
    payload=$(jq -n \
      --arg text "$emoji $message" \
      --arg color "$color" \
      '{text: $text, attachments: [{color: $color, title: "Assets System", text: $text}]}')
  else
    payload="{\"text\":\"$emoji $message\"}"
  fi
  
  if command -v curl &> /dev/null; then
    curl -X POST -H 'Content-type: application/json' \
      --data "$payload" \
      "$WEBHOOK_URL" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
      echo "✅ Webhook enviado: $event"
    else
      echo "❌ Error enviando webhook"
      exit 1
    fi
  else
    echo "⚠️  curl no disponible para enviar webhook"
    exit 1
  fi
}

if [ -z "$EVENT" ]; then
  show_help
  exit 0
fi

send_webhook "$EVENT" "${PAYLOAD:-Evento: $EVENT}"


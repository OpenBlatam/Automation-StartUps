#!/usr/bin/env bash
# Monitoreo continuo: ejecuta verificaciones periódicas y genera alertas

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
INTERVAL="${INTERVAL:-300}"  # 5 minutos por defecto
LOG_FILE="$ROOT_DIR/exports/monitoring.log"

show_help() {
  cat <<EOF
Uso: bash tools/continuous_monitor.sh [opciones]

Monitoreo continuo del sistema

Opciones:
  --interval SECONDS   Intervalo entre verificaciones (default: 300 = 5min)
  --daemon             Ejecutar en modo daemon (background)
  --log FILE           Archivo de log (default: exports/monitoring.log)
  --help               Mostrar esta ayuda

Ejemplos:
  bash tools/continuous_monitor.sh --interval 60
  bash tools/continuous_monitor.sh --daemon --interval 300
  bash tools/continuous_monitor.sh --log exports/custom_monitor.log

EOF
}

DAEMON=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --interval) INTERVAL="$2"; shift ;;
    --daemon) DAEMON=true ;;
    --log) LOG_FILE="$2"; shift ;;
    --help) show_help; exit 0 ;;
    *) echo "Opción desconocida: $1"; show_help; exit 1 ;;
  esac
  shift
done

log_message() {
  local message="$1"
  local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
  echo "[$timestamp] $message" | tee -a "$LOG_FILE"
}

run_monitoring_cycle() {
  log_message "🔄 Iniciando ciclo de monitoreo..."
  
  # 1. Health check rápido
  if bash tools/quick_audit.sh > /dev/null 2>&1; then
    log_message "✅ Quick audit: OK"
  else
    log_message "⚠️  Quick audit: Problemas detectados"
  fi
  
  # 2. Verificar alertas
  if node tools/smart_alerts.js > /dev/null 2>&1; then
    log_message "✅ Smart alerts: OK"
  else
    log_message "🔴 Smart alerts: Alertas críticas detectadas"
  fi
  
  # 3. Verificar backups recientes
  BACKUP_DIR="$ROOT_DIR/backups/assets"
  if [ -d "$BACKUP_DIR" ]; then
    LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*.tar.gz" -type f -exec stat -f "%m %N" {} \; 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
    if [ -n "$LATEST_BACKUP" ]; then
      BACKUP_AGE=$(( ($(date +%s) - $(stat -f "%m" "$LATEST_BACKUP" 2>/dev/null || stat -c "%Y" "$LATEST_BACKUP" 2>/dev/null || echo 0)) / 3600 ))
      if [ "$BACKUP_AGE" -lt 24 ]; then
        log_message "✅ Backup reciente: $BACKUP_AGE horas atrás"
      else
        log_message "⚠️  Backup antiguo: $BACKUP_AGE horas atrás"
      fi
    else
      log_message "⚠️  No hay backups disponibles"
    fi
  fi
  
  log_message "✅ Ciclo de monitoreo completado"
  echo ""
}

if [ "$DAEMON" = true ]; then
  log_message "🚀 Iniciando monitoreo continuo (daemon mode)"
  log_message "   Intervalo: ${INTERVAL} segundos"
  log_message "   Log: $LOG_FILE"
  log_message "   Presiona Ctrl+C para detener"
  echo ""
  
  while true; do
    run_monitoring_cycle
    sleep "$INTERVAL"
  done
else
  log_message "🔄 Ejecutando monitoreo único"
  run_monitoring_cycle
  log_message "✅ Monitoreo completado"
fi


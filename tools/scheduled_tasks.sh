#!/usr/bin/env bash
# Sistema de tareas programadas para automatización periódica

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TASKS_FILE="${TASKS_FILE:-$ROOT_DIR/exports/scheduled_tasks.json}"

show_help() {
  cat <<EOF
Uso: bash tools/scheduled_tasks.sh [comando]

Sistema de tareas programadas

Comandos:
  init              Crear configuración inicial
  list              Listar tareas programadas
  add               Agregar nueva tarea
  run [task_name]   Ejecutar tarea específica o todas
  status            Estado de todas las tareas
  remove [task]     Eliminar tarea
  
Ejemplos:
  bash tools/scheduled_tasks.sh init
  bash tools/scheduled_tasks.sh add
  bash tools/scheduled_tasks.sh run
  bash tools/scheduled_tasks.sh status

EOF
}

init_tasks() {
  mkdir -p "$(dirname "$TASKS_FILE")"
  
  if [ ! -f "$TASKS_FILE" ]; then
    cat > "$TASKS_FILE" <<EOF
{
  "tasks": [
    {
      "name": "daily_health_check",
      "description": "Health check diario",
      "command": "bash tools/health_check.sh",
      "schedule": "daily",
      "time": "09:00",
      "enabled": true,
      "last_run": null,
      "next_run": null
    },
    {
      "name": "daily_backup",
      "description": "Backup diario de assets",
      "command": "bash tools/auto_backup.sh",
      "schedule": "daily",
      "time": "02:00",
      "enabled": true,
      "last_run": null,
      "next_run": null
    },
    {
      "name": "weekly_report",
      "description": "Reporte semanal completo",
      "command": "bash tools/generate_full_report.sh",
      "schedule": "weekly",
      "day": "monday",
      "time": "10:00",
      "enabled": true,
      "last_run": null,
      "next_run": null
    },
    {
      "name": "monthly_cleanup",
      "description": "Limpieza mensual de reportes antiguos",
      "command": "bash tools/cleanup_reports.sh 30",
      "schedule": "monthly",
      "day": 1,
      "time": "03:00",
      "enabled": true,
      "last_run": null,
      "next_run": null
    }
  ]
}
EOF
    echo "✅ Configuración inicial creada: $TASKS_FILE"
  else
    echo "⚠️  El archivo de tareas ya existe: $TASKS_FILE"
  fi
}

list_tasks() {
  if [ ! -f "$TASKS_FILE" ]; then
    echo "❌ Archivo de tareas no encontrado. Ejecuta: bash tools/scheduled_tasks.sh init"
    exit 1
  fi
  
  echo "📋 Tareas Programadas"
  echo "====================="
  echo ""
  
  if command -v jq &> /dev/null; then
    jq -r '.tasks[] | "\(.name) | \(.description) | \(.schedule) | \(if .enabled then "✅" else "❌" end)"' "$TASKS_FILE" | \
      column -t -s '|' || cat "$TASKS_FILE"
  else
    cat "$TASKS_FILE"
  fi
}

run_task() {
  local task_name="$1"
  
  if [ ! -f "$TASKS_FILE" ]; then
    echo "❌ Archivo de tareas no encontrado"
    exit 1
  fi
  
  if [ -z "$task_name" ] || [ "$task_name" = "all" ]; then
    echo "🚀 Ejecutando todas las tareas habilitadas..."
    echo ""
    
    if command -v jq &> /dev/null; then
      jq -r '.tasks[] | select(.enabled == true) | "\(.name)|\(.command)"' "$TASKS_FILE" | while IFS='|' read -r name cmd; do
        echo "▶️  Ejecutando: $name"
        eval "$cmd" || echo "❌ Error en: $name"
        echo ""
      done
    else
      echo "⚠️  jq no disponible. Instala jq para usar esta funcionalidad."
    fi
  else
    if command -v jq &> /dev/null; then
      local cmd=$(jq -r ".tasks[] | select(.name == \"$task_name\") | .command" "$TASKS_FILE")
      if [ -n "$cmd" ]; then
        echo "▶️  Ejecutando: $task_name"
        eval "$cmd"
      else
        echo "❌ Tarea no encontrada: $task_name"
        exit 1
      fi
    else
      echo "⚠️  jq no disponible"
    fi
  fi
}

show_status() {
  if [ ! -f "$TASKS_FILE" ]; then
    echo "❌ Archivo de tareas no encontrado"
    exit 1
  fi
  
  echo "📊 Estado de Tareas"
  echo "=================="
  echo ""
  
  if command -v jq &> /dev/null; then
    jq -r '.tasks[] | "\(.name): \(if .enabled then "✅ Habilitada" else "❌ Deshabilitada" end) | Última ejecución: \(.last_run // "Nunca")"' "$TASKS_FILE"
  else
    echo "⚠️  jq no disponible. Instala jq para ver el estado detallado."
  fi
}

# Parse command
case "${1:-}" in
  init) init_tasks ;;
  list) list_tasks ;;
  run) run_task "${2:-all}" ;;
  status) show_status ;;
  add) echo "💡 Edita manualmente: $TASKS_FILE" ;;
  remove) echo "💡 Edita manualmente: $TASKS_FILE" ;;
  help|--help|-h) show_help ;;
  *) show_help ;;
esac


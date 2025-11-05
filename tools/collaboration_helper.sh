#!/usr/bin/env bash
# Herramientas de colaboración: facilita trabajo en equipo

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

show_help() {
  cat <<EOF
Uso: bash tools/collaboration_helper.sh [comando]

Herramientas de colaboración para trabajo en equipo

Comandos:
  setup              Configurar entorno para colaboración
  checklist           Generar checklist de onboarding
  status              Estado del proyecto para nuevos miembros
  assign [task]       Asignar tarea (crea archivo de tracking)
  notes [message]     Agregar nota al log de colaboración
  
Ejemplos:
  bash tools/collaboration_helper.sh setup
  bash tools/collaboration_helper.sh checklist
  bash tools/collaboration_helper.sh status

EOF
}

setup_collaboration() {
  echo "👥 Configurando entorno de colaboración..."
  echo ""
  
  # Crear estructura de colaboración
  mkdir -p "$ROOT_DIR/.collaboration"
  mkdir -p "$ROOT_DIR/.collaboration/tasks"
  mkdir -p "$ROOT_DIR/.collaboration/notes"
  
  # Crear archivo de configuración
  if [ ! -f "$ROOT_DIR/.collaboration/config.json" ]; then
    cat > "$ROOT_DIR/.collaboration/config.json" <<EOF
{
  "team_members": [],
  "active_tasks": [],
  "last_update": "$(date -Iseconds)"
}
EOF
    echo "✅ Configuración creada"
  fi
  
  # Crear .gitignore si no existe para colaboración
  if [ ! -f "$ROOT_DIR/.gitignore" ]; then
    echo "# Collaboración" > "$ROOT_DIR/.gitignore"
    echo ".collaboration/personal/" >> "$ROOT_DIR/.gitignore"
  fi
  
  # Crear README de colaboración
  cat > "$ROOT_DIR/.collaboration/README.md" <<EOF
# Guía de Colaboración

Este directorio contiene recursos para facilitar el trabajo en equipo.

## Estructura

- \`tasks/\` - Tareas asignadas y tracking
- \`notes/\` - Notas y comunicación del equipo
- \`config.json\` - Configuración del equipo

## Comandos Útiles

- \`bash tools/collaboration_helper.sh checklist\` - Checklist de onboarding
- \`bash tools/collaboration_helper.sh status\` - Estado del proyecto
- \`bash tools/collaboration_helper.sh assign [tarea]\` - Asignar tarea
- \`bash tools/collaboration_helper.sh notes [mensaje]\` - Agregar nota

## Flujo de Trabajo

1. Nuevo miembro ejecuta: \`bash tools/collaboration_helper.sh setup\`
2. Revisa checklist: \`bash tools/collaboration_helper.sh checklist\`
3. Verifica estado: \`bash tools/collaboration_helper.sh status\`
4. Asigna tareas según necesidad
EOF
  
  echo "✅ Entorno de colaboración configurado"
  echo "📁 Directorio: .collaboration/"
}

generate_checklist() {
  echo "📋 Checklist de Onboarding"
  echo "========================="
  echo ""
  
  CHECKLIST_FILE="$ROOT_DIR/.collaboration/ONBOARDING_CHECKLIST.md"
  
  cat > "$CHECKLIST_FILE" <<EOF
# Checklist de Onboarding

## Setup Inicial
- [ ] Clonar repositorio
- [ ] Instalar dependencias: \`bash tools/install_dependencies.sh\`
- [ ] Configurar tokens: \`cp design/instagram/tokens.example.json design/instagram/tokens.json\`
- [ ] Editar tokens.json con valores reales
- [ ] Ejecutar: \`bash tools/quick_audit.sh\`

## Entender el Sistema
- [ ] Leer README.md principal
- [ ] Leer QUICKSTART.md
- [ ] Revisar estructura de directorios
- [ ] Entender sistema de tokens
- [ ] Revisar ejemplos de assets

## Primera Ejecución
- [ ] Ejecutar: \`bash tools/build_all.sh\`
- [ ] Revisar preview: \`exports/preview/index.html\`
- [ ] Ejecutar validaciones: \`bash tools/run_all_validations.sh\`
- [ ] Ver health score: \`node tools/health_score_calculator.js\`

## Herramientas Clave
- [ ] Probar: \`bash tools/auto_fix_issues.sh\`
- [ ] Probar: \`node tools/smart_recommendations.js\`
- [ ] Probar: \`bash tools/batch_operations.sh --help\`
- [ ] Crear backup: \`bash tools/auto_backup.sh\`

## Colaboración
- [ ] Revisar tareas activas: \`ls .collaboration/tasks/\`
- [ ] Revisar notas: \`ls .collaboration/notes/\`
- [ ] Entender flujo de trabajo del equipo

## Recursos
- Documentación: \`readme.md\`, \`QUICKSTART.md\`
- Dashboards: \`tools/create_realtime_dashboard.html\`
- Reportes: \`exports/reports/\`
EOF
  
  cat "$CHECKLIST_FILE"
  echo ""
  echo "✅ Checklist generado: $CHECKLIST_FILE"
}

show_status() {
  echo "📊 Estado del Proyecto para Colaboración"
  echo "========================================"
  echo ""
  
  echo "📁 Estructura:"
  echo "  - Assets: $(find "$ROOT_DIR/design" "$ROOT_DIR/ads" -name "*.svg" 2>/dev/null | wc -l | xargs) SVGs"
  echo "  - Herramientas: $(find "$ROOT_DIR/tools" -name "*.sh" -o -name "*.js" 2>/dev/null | wc -l | xargs) scripts"
  echo "  - Exports: $(find "$ROOT_DIR/exports" -type f 2>/dev/null | wc -l | xargs) archivos"
  echo ""
  
  echo "✅ Sistema configurado:"
  [ -f "$ROOT_DIR/design/instagram/tokens.json" ] && echo "  ✅ Tokens configurados" || echo "  ❌ Tokens no configurados"
  [ -d "$ROOT_DIR/exports/png" ] && echo "  ✅ PNGs exportados" || echo "  ⚠️  PNGs no exportados"
  [ -d "$ROOT_DIR/exports/reports" ] && echo "  ✅ Reportes generados" || echo "  ⚠️  Sin reportes"
  echo ""
  
  echo "📝 Próximos pasos:"
  echo "  1. bash tools/collaboration_helper.sh checklist"
  echo "  2. bash tools/quick_audit.sh"
  echo "  3. bash tools/build_all.sh"
  echo ""
  
  if [ -d "$ROOT_DIR/.collaboration/tasks" ]; then
    TASK_COUNT=$(find "$ROOT_DIR/.collaboration/tasks" -name "*.md" 2>/dev/null | wc -l | xargs)
    if [ "$TASK_COUNT" -gt 0 ]; then
      echo "📌 Tareas activas: $TASK_COUNT"
      find "$ROOT_DIR/.collaboration/tasks" -name "*.md" 2>/dev/null | head -5 | while read -r task; do
        echo "  - $(basename "$task")"
      done
    fi
  fi
}

assign_task() {
  local task_name="$1"
  
  if [ -z "$task_name" ]; then
    echo "❌ Especifica un nombre de tarea"
    echo "Uso: bash tools/collaboration_helper.sh assign \"nombre_tarea\""
    exit 1
  fi
  
  mkdir -p "$ROOT_DIR/.collaboration/tasks"
  
  TASK_FILE="$ROOT_DIR/.collaboration/tasks/$(date +%Y%m%d_%H%M%S)_${task_name// /_}.md"
  
  cat > "$TASK_FILE" <<EOF
# Tarea: $task_name

**Creada**: $(date)
**Estado**: Pendiente

## Descripción
[Tarea pendiente de descripción]

## Pasos
- [ ] Paso 1
- [ ] Paso 2

## Notas
- 
EOF
  
  echo "✅ Tarea creada: $TASK_FILE"
}

add_note() {
  local message="$1"
  
  if [ -z "$message" ]; then
    echo "❌ Especifica un mensaje"
    echo "Uso: bash tools/collaboration_helper.sh notes \"mensaje\""
    exit 1
  fi
  
  mkdir -p "$ROOT_DIR/.collaboration/notes"
  
  NOTE_FILE="$ROOT_DIR/.collaboration/notes/notes_$(date +%Y%m%d).md"
  
  if [ ! -f "$NOTE_FILE" ]; then
    echo "# Notas del Equipo - $(date +%Y-%m-%d)" > "$NOTE_FILE"
    echo "" >> "$NOTE_FILE"
  fi
  
  {
    echo "## $(date +%H:%M:%S)"
    echo "$message"
    echo ""
  } >> "$NOTE_FILE"
  
  echo "✅ Nota agregada: $NOTE_FILE"
}

# Parse command
case "${1:-}" in
  setup) setup_collaboration ;;
  checklist) generate_checklist ;;
  status) show_status ;;
  assign) assign_task "${2:-}" ;;
  notes) add_note "${2:-}" ;;
  help|--help|-h) show_help ;;
  *) show_help ;;
esac


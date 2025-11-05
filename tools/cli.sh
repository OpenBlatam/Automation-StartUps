#!/usr/bin/env bash
# CLI Unificado: interfaz de línea de comandos para todas las herramientas

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

VERSION="3.0"
BANNER="
╔════════════════════════════════════════════════════════════╗
║     Sistema de Gestión de Assets - CLI Unificado v${VERSION}     ║
╚════════════════════════════════════════════════════════════╝
"

show_menu() {
  cat <<EOF
${BANNER}
Comandos principales:

  setup          Configuración inicial del sistema
  validate       Validación completa
  build          Build completo de assets
  analyze        Análisis y reportes
  monitor        Monitoreo y alertas
  maintenance    Mantenimiento del sistema
  export         Exportación de assets
  help [cmd]     Ayuda detallada

Comandos rápidos:

  audit          Auditoría rápida (30s)
  health         Health check completo
  backup         Crear backup
  test           Ejecutar suite de tests
  compliance     Reporte de compliance
  security       Auditoría de seguridad
  metrics        Tracking de métricas
  status         Estado del sistema

Ejemplos:
  bash tools/cli.sh setup
  bash tools/cli.sh validate
  bash tools/cli.sh build --platform all
  bash tools/cli.sh monitor --daemon
  bash tools/cli.sh help build

EOF
}

cmd_setup() {
  echo "🔧 Configuración Inicial"
  echo "======================="
  bash tools/install_dependencies.sh
  bash tools/quick_audit.sh
  bash tools/collaboration_helper.sh setup 2>/dev/null || true
  echo ""
  echo "✅ Setup completado"
}

cmd_validate() {
  echo "✅ Validación Completa"
  echo "====================="
  bash tools/run_all_validations.sh
  node tools/test_assets.js
  bash tools/security_audit.sh || true
  echo ""
  echo "✅ Validación completada"
}

cmd_build() {
  local platform="${1:-all}"
  echo "🏗️  Build Completo"
  echo "================"
  
  if [ "$platform" = "all" ]; then
    bash tools/build_all_platforms.sh
  elif [ "$platform" = "instagram" ]; then
    bash tools/build_all.sh
  else
    echo "Plataforma no reconocida: $platform"
    exit 1
  fi
  
  echo ""
  echo "✅ Build completado"
}

cmd_analyze() {
  echo "📊 Análisis y Reportes"
  echo "====================="
  bash tools/analyze_assets.sh
  node tools/smart_recommendations.js
  bash tools/generate_full_report.sh
  echo ""
  echo "✅ Análisis completado"
}

cmd_monitor() {
  local daemon="${1:-}"
  echo "👀 Monitoreo"
  echo "==========="
  
  if [ "$daemon" = "--daemon" ]; then
    bash tools/continuous_monitor.sh --daemon --interval 300
  else
    bash tools/quick_audit.sh
    node tools/smart_alerts.js
    node tools/health_score_calculator.js
  fi
  
  echo ""
  echo "✅ Monitoreo completado"
}

cmd_maintenance() {
  echo "🔧 Mantenimiento"
  echo "==============="
  bash tools/maintenance_mode.sh --full
  echo ""
  echo "✅ Mantenimiento completado"
}

cmd_export() {
  local format="${1:-png}"
  echo "📦 Exportación"
  echo "============="
  
  if [ "$format" = "multiformat" ]; then
    bash tools/export_multiformat.sh --formats png,jpg,webp
  else
    bash tools/export_png.sh
  fi
  
  echo ""
  echo "✅ Exportación completada"
}

cmd_audit() {
  bash tools/quick_audit.sh
}

cmd_health() {
  bash tools/health_check.sh
  node tools/health_score_calculator.js
}

cmd_backup() {
  bash tools/auto_backup.sh
}

cmd_test() {
  node tools/test_assets.js
}

cmd_compliance() {
  node tools/generate_compliance_report.js
}

cmd_security() {
  bash tools/security_audit.sh
}

cmd_metrics() {
  node tools/metrics_tracker.js
}

cmd_status() {
  echo "📊 Estado del Sistema"
  echo "===================="
  echo ""
  bash tools/quick_audit.sh
  echo ""
  node tools/health_score_calculator.js | tail -10
}

show_help() {
  local cmd="${1:-}"
  
  case "$cmd" in
    setup)
      echo "setup - Configuración inicial"
      echo "Ejecuta: install_dependencies, quick_audit, collaboration setup"
      ;;
    validate)
      echo "validate - Validación completa"
      echo "Ejecuta: run_all_validations, test_assets, security_audit"
      ;;
    build)
      echo "build [platform] - Build completo"
      echo "Opciones: all, instagram"
      ;;
    analyze)
      echo "analyze - Análisis y reportes"
      echo "Ejecuta: analyze_assets, smart_recommendations, generate_full_report"
      ;;
    monitor)
      echo "monitor [--daemon] - Monitoreo"
      echo "Sin --daemon: ejecución única"
      echo "Con --daemon: monitoreo continuo"
      ;;
    maintenance)
      echo "maintenance - Mantenimiento completo"
      echo "Ejecuta: limpieza + optimización + backup"
      ;;
    export)
      echo "export [format] - Exportación"
      echo "Formatos: png (default), multiformat"
      ;;
    *)
      show_menu
      ;;
  esac
}

# Parse command
case "${1:-help}" in
  setup) cmd_setup ;;
  validate) cmd_validate ;;
  build) cmd_build "${2:-all}" ;;
  analyze) cmd_analyze ;;
  monitor) cmd_monitor "${2:-}" ;;
  maintenance) cmd_maintenance ;;
  export) cmd_export "${2:-png}" ;;
  audit) cmd_audit ;;
  health) cmd_health ;;
  backup) cmd_backup ;;
  test) cmd_test ;;
  compliance) cmd_compliance ;;
  security) cmd_security ;;
  metrics) cmd_metrics ;;
  status) cmd_status ;;
  help) show_help "${2:-}" ;;
  *) show_menu ;;
esac


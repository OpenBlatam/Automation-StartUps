#!/usr/bin/env bash
# Guía interactiva de inicio rápido

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "🚀 Guía Interactiva de Inicio Rápido"
echo "===================================="
echo ""

echo "Esta guía te ayudará a configurar el sistema paso a paso."
echo ""
read -p "¿Deseas continuar? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Cancelado."
  exit 0
fi

echo ""
echo "Paso 1/6: Verificando dependencias..."
if command -v node &> /dev/null; then
  echo "✅ Node.js: $(node --version)"
else
  echo "❌ Node.js no encontrado"
  echo "   Instala Node.js desde: https://nodejs.org/"
  exit 1
fi

echo ""
echo "Paso 2/6: Instalando dependencias..."
if bash tools/install_dependencies.sh; then
  echo "✅ Dependencias instaladas"
else
  echo "⚠️  Algunas dependencias pueden requerir instalación manual"
fi

echo ""
echo "Paso 3/6: Configurando tokens..."
TOKENS_FILE="$ROOT_DIR/design/instagram/tokens.json"
TOKENS_EXAMPLE="$ROOT_DIR/design/instagram/tokens.example.json"

if [ ! -f "$TOKENS_FILE" ]; then
  if [ -f "$TOKENS_EXAMPLE" ]; then
    cp "$TOKENS_EXAMPLE" "$TOKENS_FILE"
    echo "✅ Archivo tokens.json creado desde ejemplo"
    echo "⚠️  IMPORTANTE: Edita $TOKENS_FILE con tus valores reales"
    echo ""
    read -p "¿Deseas abrir el archivo ahora? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
      ${EDITOR:-nano} "$TOKENS_FILE" || echo "Abre manualmente: $TOKENS_FILE"
    fi
  else
    echo "⚠️  tokens.example.json no encontrado"
  fi
else
  echo "✅ tokens.json ya existe"
fi

echo ""
echo "Paso 4/6: Auditoría rápida..."
bash tools/quick_audit.sh

echo ""
echo "Paso 5/6: Health check..."
node tools/health_score_calculator.js | tail -5

echo ""
echo "Paso 6/6: ¿Qué deseas hacer ahora?"
echo ""
echo "1. Build completo del sistema"
echo "2. Solo validación"
echo "3. Ver estado actual"
echo "4. Salir"
echo ""
read -p "Selecciona una opción (1-4): " -n 1 -r
echo ""

case $REPLY in
  1)
    echo "🏗️  Ejecutando build completo..."
    bash tools/build_all_platforms.sh
    ;;
  2)
    echo "✅ Ejecutando validación..."
    bash tools/run_all_validations.sh
    ;;
  3)
    echo "📊 Estado del sistema:"
    bash tools/cli.sh status
    ;;
  4)
    echo "✅ Configuración completada"
    ;;
  *)
    echo "Opción no válida"
    ;;
esac

echo ""
echo "✨ ¡Configuración completada!"
echo ""
echo "💡 Próximos pasos:"
echo "   - Revisa: bash tools/cli.sh help"
echo "   - Dashboard: open tools/create_master_dashboard.html"
echo "   - Documentación: cat readme.md"


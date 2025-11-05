#!/usr/bin/env bash
set -euo pipefail
# Instala todas las dependencias necesarias para el sistema

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "📦 Instalando dependencias..."

# Node.js dependencies
if command -v npm >/dev/null 2>&1; then
  echo "Instalando paquetes Node.js..."
  cd "$ROOT_DIR"
  if [ ! -f "package.json" ]; then
    npm init -y
  fi
  npm install qrcode --save-dev 2>/dev/null || echo "⚠️  qrcode ya instalado o error"
  
  # SVGO global check
  if ! command -v svgo >/dev/null 2>&1; then
    echo "Instalando SVGO globalmente..."
    npm install -g svgo 2>/dev/null || echo "⚠️  Error instalando SVGO. Ejecuta manualmente: npm i -g svgo"
  else
    echo "✅ SVGO ya instalado"
  fi
else
  echo "⚠️  Node.js/npm no encontrado. Instala Node.js desde https://nodejs.org/"
fi

# Check Inkscape
if command -v inkscape >/dev/null 2>&1; then
  echo "✅ Inkscape encontrado"
elif command -v brew >/dev/null 2>&1; then
  echo "💡 Puedes instalar Inkscape con: brew install --cask inkscape"
elif command -v apt-get >/dev/null 2>&1; then
  echo "💡 Puedes instalar Inkscape con: sudo apt-get install inkscape"
else
  echo "⚠️  Inkscape no encontrado. Instálalo para exportar PNG: https://inkscape.org/"
fi

# Check rsvg-convert (alternativa)
if command -v rsvg-convert >/dev/null 2>&1; then
  echo "✅ rsvg-convert encontrado"
fi

echo ""
echo "✅ Dependencias revisadas."
echo "💡 Para verificar: bash tools/validate_all.sh"




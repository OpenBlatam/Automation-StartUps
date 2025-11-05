#!/usr/bin/env bash
set -euo pipefail
# Master script: aplica tokens/tema, genera QR, exporta PNG, optimiza y empaqueta

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "🚀 Iniciando build completo..."

# 1. Aplicar tokens
echo "📝 Aplicando tokens..."
node tools/apply_tokens.js || echo "⚠️  Saltando tokens (verifica tokens.json)"

# 2. Aplicar tema
echo "🎨 Aplicando tema de marca..."
node tools/apply_theme.js || echo "⚠️  Saltando tema (verifica brandColors en tokens.json)"

# 3. Generar QR
echo "📱 Generando QR..."
node tools/generate_qr.js || echo "⚠️  Saltando QR (requiere: npm install qrcode)"

# 4. Exportar PNG
echo "📸 Exportando PNG (1x y 2x)..."
bash tools/export_png.sh || echo "⚠️  Saltando PNG (requiere: inkscape o rsvg-convert)"

# 5. Optimizar SVG
echo "⚡ Optimizando SVG..."
bash tools/optimize_svg.sh || echo "⚠️  Saltando optimización (requiere: npm i -g svgo)"

# 6. Empaquetar
echo "📦 Creando ZIP final..."
bash tools/package_assets.sh

echo "✅ Build completo. Revisa exports/"




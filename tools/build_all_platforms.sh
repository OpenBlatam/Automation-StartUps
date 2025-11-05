#!/usr/bin/env bash
set -euo pipefail
# Build completo para todas las plataformas (Instagram + LinkedIn)

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "🚀 Build completo multi-plataforma..."

# Health check (opcional, no falla si hay warnings)
if [ -f "$ROOT_DIR/tools/health_check.sh" ]; then
  echo "🏥 Ejecutando health check..."
  bash tools/health_check.sh || echo "⚠️  Health check detectó problemas (continuando...)"
  echo ""
fi

# Instagram
echo "📱 Procesando Instagram..."
node tools/apply_tokens.js || echo "⚠️  Saltando tokens Instagram"
node tools/apply_theme.js || echo "⚠️  Saltando tema"
node tools/generate_qr.js || echo "⚠️  Saltando QR"

# LinkedIn
echo "💼 Procesando LinkedIn..."
node tools/sync_tokens_all_platforms.js || echo "⚠️  Saltando sync LinkedIn"
node tools/apply_tokens_linkedin.js || echo "⚠️  Saltando tokens LinkedIn"

# Webinars (opcional)
echo "📹 Integrando webinars..."
bash tools/integrate_webinars.sh || echo "⚠️  Saltando webinars (puede que no existan)"

# Export y optimize (compartido)
echo "📸 Exportando PNG..."
bash tools/export_png.sh || echo "⚠️  Saltando PNG"

echo "⚡ Optimizando SVG..."
bash tools/optimize_svg.sh || echo "⚠️  Saltando optimización"

echo "📦 Empaquetando..."
bash tools/package_assets.sh

echo "✅ Build multi-plataforma completo."


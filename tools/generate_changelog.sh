#!/usr/bin/env bash
set -euo pipefail
# Genera changelog basado en git commits o crea uno manual

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CHANGELOG="$ROOT_DIR/CHANGELOG.md"

VERSION="${1:-1.0.0}"
DATE=$(date +%Y-%m-%d)

if [ -d "$ROOT_DIR/.git" ] && command -v git >/dev/null 2>&1; then
  # Generate from git
  {
    echo "# Changelog"
    echo ""
    echo "## [$VERSION] - $DATE"
    echo ""
    echo "### Added"
    git log --pretty=format:"- %s" --since="1 week ago" | head -10 || echo "- Versión inicial del sistema"
    echo ""
    echo "### Changed"
    echo "- Sistema de automatización completo"
    echo ""
  } > "$CHANGELOG"
else
  # Manual changelog
  {
    echo "# Changelog"
    echo ""
    echo "## [$VERSION] - $DATE"
    echo ""
    echo "### Added"
    echo "- Sistema completo de diseño Instagram 35% OFF"
    echo "- 50+ archivos SVG editables"
    echo "- Scripts de automatización (tokens, tema, QR, export, optimize)"
    echo "- Preview web interactivo con categorías"
    echo "- Copys ES/EN/PT"
    echo "- Calendario de publicación"
    echo "- Checklists de QA y entrega"
    echo "- Documentación completa"
    echo ""
    echo "### Features"
    echo "- Feed 1080×1080 (base, dark, A/B, últimas 24h, low-text)"
    echo "- Ads 1080×1350 (feed vertical)"
    echo "- Stories 1080×1920"
    echo "- Reels, Carrusel, Highlights"
    echo "- Variantes automáticas de descuento/urgencia"
    echo "- UTMs por mercado (ES/EN/PT)"
    echo "- Accesibilidad (alt text ES/EN/PT)"
    echo ""
  } > "$CHANGELOG"
fi

echo "✅ Changelog generado: $CHANGELOG"




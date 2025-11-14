#!/bin/sh
# Empaqueta el sistema operativo de innovación en un ZIP
set -e
BUNDLE_NAME="innovacion_so_bundle_$(date +%Y%m%d).zip"

zip -r "$BUNDLE_NAME" \
  00_*.md \
  00_*.json \
  00_*.yaml \
  00_*.csv \
  00_*.env \
  00_*.sh \
  01_DM_CURSO_IA_WEBINARS_ULTIMATE.md \
  04_AUTOMATIZACION_ESCALAMIENTO_DMS.md \
  INDICE_COMPLETO.md 2>/dev/null || true

echo "Bundle creado: $BUNDLE_NAME"

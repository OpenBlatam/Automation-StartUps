#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")"/.. && pwd)"
cd "$ROOT"
ZIP_NAME="escalera_valor_assets.zip"

echo "Empaquetando assets en $ZIP_NAME ..."
zip -r "$ZIP_NAME" \
  ESCALERA_VALOR_3_PRODUCTOS_COMPLETA.md \
  README_IMPLEMENTACION_ESCALERA.md \
  MANIFEST_ESCALERA_VALOR.md \
  automation/*.csv \
  automation/*_sample.csv \
  automation/*.json \
  automation/*.md \
  automation/email_templates_html/*.html \
  automation/email_templates_text/*.txt \
  1>/dev/null

echo "Listo: $ROOT/$ZIP_NAME"

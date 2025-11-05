#!/usr/bin/env bash
set -euo pipefail

# build.sh - utilidades de exportación y QA para Documentation
# Requisitos opcionales: pandoc, markdown-link-check

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$ROOT_DIR/_build"
mkdir -p "$OUT_DIR"

# 1) Exportación a PDF/HTML si pandoc está disponible
if command -v pandoc >/dev/null 2>&1; then
  for f in "$ROOT_DIR"/*.md; do
    name="$(basename "$f" .md)"
    pandoc "$f" -o "$OUT_DIR/${name}.pdf" || true
    pandoc "$f" -o "$OUT_DIR/${name}.html" || true
  done
else
  echo "[build] pandoc no encontrado; se omite exportación" >&2
fi

# 2) QA de enlaces locales y externos (si existen scripts)
if [[ -x "$ROOT_DIR/verify_links.sh" ]]; then
  echo "[build] Verificando enlaces locales (.md)" >&2
  "$ROOT_DIR/verify_links.sh" || true
else
  echo "[build] verify_links.sh no encontrado; se omite verificación local" >&2
fi

if [[ -x "$ROOT_DIR/check_external_links.sh" ]]; then
  echo "[build] Verificando enlaces externos (HTTP/HTTPS)" >&2
  "$ROOT_DIR/check_external_links.sh" || true
else
  echo "[build] check_external_links.sh no encontrado; se omite verificación externa" >&2
fi

echo "[build] OK. Artefactos en: $OUT_DIR"


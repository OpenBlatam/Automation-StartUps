#!/usr/bin/env bash
set -euo pipefail

# pdf_bundle.sh - Genera PDFs (si hay pandoc) y une en un solo PDF (pdfunite/gs)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="$ROOT_DIR/_build"
mkdir -p "$OUT_DIR"

PDFS=()
if command -v pandoc >/dev/null 2>&1; then
  for f in "$ROOT_DIR"/*.md; do
    name="$(basename "$f" .md)"
    out="$OUT_DIR/${name}.pdf"
    pandoc "$f" -o "$out" || true
    [[ -f "$out" ]] && PDFS+=("$out")
  done
else
  echo "[pdf] pandoc no disponible; no se generarán PDFs" >&2
fi

if [[ ${#PDFS[@]} -eq 0 ]]; then
  echo "[pdf] No hay PDFs para unir" >&2
  exit 0
fi

COMBINED="$OUT_DIR/_ALL_DOCUMENTS.pdf"
if command -v pdfunite >/dev/null 2>&1; then
  pdfunite "${PDFS[@]}" "$COMBINED" || true
elif command -v gs >/dev/null 2>&1; then
  gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile="$COMBINED" "${PDFS[@]}" || true
else
  echo "[pdf] ni pdfunite ni gs disponibles; omitida unión" >&2
fi

[[ -f "$COMBINED" ]] && echo "[pdf] Bundle creado: $COMBINED" || echo "[pdf] Bundle no generado"



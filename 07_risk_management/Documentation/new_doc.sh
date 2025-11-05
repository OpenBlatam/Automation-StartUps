#!/usr/bin/env bash
set -euo pipefail

# new_doc.sh - Crea un nuevo documento con front matter estándar
# Uso: ./new_doc.sh "Título del Documento" filename.md [version]

if [[ $# -lt 2 ]]; then
  echo "Uso: $0 \"Título del Documento\" filename.md [version]" >&2
  exit 1
fi

TITLE="$1"
FILENAME="$2"
VERSION="${3:-}" # opcional
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="$ROOT_DIR/$FILENAME"

if [[ -e "$TARGET" ]]; then
  echo "[error] Ya existe: $TARGET" >&2
  exit 2
fi

CREATED_DATE="$(date +%Y-%m-%d)"
LOWER_PATH="07_risk_management/$(echo "$FILENAME" | tr 'A-Z' 'a-z')"

{
  echo "---"
  echo "title: \"$TITLE\""
  echo "category: \"07_risk_management\""
  echo "tags: []"
  echo "created: \"$CREATED_DATE\""
  echo "path: \"$LOWER_PATH\""
  echo "---"
  echo ""
  echo "# $TITLE"
  echo ""
  if [[ -n "$VERSION" ]]; then
    echo "**Versión:** $VERSION"
    echo ""
  fi
  echo "## Resumen"
  echo "[Describe el objetivo del documento en 2-3 frases.]"
  echo ""
  echo "## Contenido"
  echo "- [Sección 1](#sección-1)"
  echo "- [Sección 2](#sección-2)"
  echo "- [Sección 3](#sección-3)"
  echo ""
  echo "## Sección 1"
  echo "Contenido inicial."
  echo ""
  echo "## Sección 2"
  echo "Contenido inicial."
  echo ""
  echo "## Sección 3"
  echo "Contenido inicial."
  echo ""
  echo "---"
  echo "Documento generado con new_doc.sh el $CREATED_DATE"
} > "$TARGET"

echo "[new] Creado: $TARGET"


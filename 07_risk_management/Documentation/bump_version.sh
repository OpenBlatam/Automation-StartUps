#!/usr/bin/env bash
set -euo pipefail

# bump_version.sh - Actualiza líneas visibles de "Versión:" en Documentation/*.md
# Uso: ./bump_version.sh 6.2 "Etiqueta opcional"

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <nueva_version> [sufijo]" >&2
  exit 1
fi

NEW_VER="$1"
SUFFIX="${2:-}"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

shopt -s nullglob
for f in "$ROOT_DIR"/*.md; do
  base="$(basename "$f")"
  case "$base" in
    index.md|readme.md|CHANGELOG.md)
      echo "[skip] $base"
      continue
      ;;
  esac

  if grep -q "^\*\*Versión:\*\*" "$f"; then
    # Reemplazar toda la línea de versión, preservando el resto
    if [[ -n "$SUFFIX" ]]; then
      sed -E -i '' "s/^\*\*Versión:\*\*.*/**Versión:** ${NEW_VER} (${SUFFIX})/" "$f"
    else
      sed -E -i '' "s/^\*\*Versión:\*\*.*/**Versión:** ${NEW_VER}/" "$f"
    fi
    echo "[bumped] $(basename "$f") → $NEW_VER ${SUFFIX}"
  else
    echo "[no-version-line] $(basename "$f")"
  fi
done

echo "[done] Nueva versión aplicada: $NEW_VER ${SUFFIX}"


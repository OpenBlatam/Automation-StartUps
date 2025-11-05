#!/usr/bin/env bash
set -euo pipefail

# check_images.sh - Verifica que las imágenes referenciadas existen localmente
# Soporta enlaces markdown: ![alt](./path.{png,jpg,jpeg,gif,svg,webp})

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

for file in "${MD_FILES[@]}"; do
  rel="${file#$ROOT_DIR/}"
  # Extrae solo imágenes (prefijo !)
  grep -oE "!\[[^\]]*\]\((\./|../)[^)]+\.(png|jpg|jpeg|gif|svg|webp)\)" "$file" | \
  sed -E 's/^!\[[^\]]*\]\((.+)\)$/\1/' | while read -r link; do
    # limpia anchors/query
    clean_link="${link%%[#?]*}"
    # resuelve ruta absoluta
    dest="$(cd "$ROOT_DIR" && python3 - <<PY
import os
base=os.path.dirname("$rel")
link="""$clean_link"""
path=os.path.normpath(os.path.join(base, link))
print(os.path.join("$ROOT_DIR", path))
PY
)"
    if [[ ! -f "$dest" ]]; then
      echo "[missing-image] $rel → $link (no existe: ${dest#$ROOT_DIR/})" >&2
      FAIL=1
    fi
  done || true
done

if [[ $FAIL -ne 0 ]]; then
  echo "[images] Fallas detectadas en enlaces de imágenes" >&2
  exit 1
fi

echo "[images] Todas las imágenes referenciadas existen"



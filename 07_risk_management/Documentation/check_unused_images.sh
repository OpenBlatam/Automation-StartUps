#!/usr/bin/env bash
set -euo pipefail

# check_unused_images.sh - Detecta imágenes locales no referenciadas por ningún .md

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

mapfile -t IMAGES < <(find "$ROOT_DIR" -maxdepth 1 -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.svg" -o -iname "*.webp" \) | sort)
mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

if [[ ${#IMAGES[@]} -eq 0 ]]; then
  echo "[unused-images] No hay archivos de imagen en el directorio"
  exit 0
fi

for img in "${IMAGES[@]}"; do
  name="$(basename "$img")"
  if ! grep -R "\]\([^)]*$name\)" "$ROOT_DIR" --include "*.md" -n >/dev/null 2>&1; then
    echo "[unused-image] $name no está referenciada por ningún .md" >&2
    FAIL=1
  fi
done

if [[ $FAIL -ne 0 ]]; then
  echo "[unused-images] Imágenes no referenciadas detectadas" >&2
  exit 1
fi

echo "[unused-images] Todas las imágenes están referenciadas"



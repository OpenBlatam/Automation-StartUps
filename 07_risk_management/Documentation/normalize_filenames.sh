#!/usr/bin/env bash
set -euo pipefail

# normalize_filenames.sh - Normaliza nombres de archivos .md a lowercase y guiones
# Uso: ./normalize_filenames.sh [--apply]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

to_target() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9._-]+/-/g; s/-+/-/g'
}

declare -A RMAP
while IFS= read -r f; do
  base=$(basename "$f")
  tgt=$(to_target "$base")
  if [[ "$base" != "$tgt" ]]; then
    RMAP["$base"]="$tgt"
  fi
done < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md")

if [[ ${#RMAP[@]} -eq 0 ]]; then
  echo "[normalize] No hay archivos a renombrar"
  exit 0
fi

echo "[normalize] Plan de renombrado:" >&2
for k in "${!RMAP[@]}"; do
  echo " - $k -> ${RMAP[$k]}" >&2
done

if [[ $APPLY -eq 0 ]]; then
  echo "[normalize] Dry-run. Use --apply para aplicar" >&2
  exit 0
fi

# Aplicar renombres y actualizar referencias en .md
for k in "${!RMAP[@]}"; do
  src="$ROOT_DIR/$k"
  dst="$ROOT_DIR/${RMAP[$k]}"
  if [[ -e "$dst" ]]; then
    echo "[normalize] destino ya existe: $dst" >&2
    continue
  fi
  mv "$src" "$dst"
  # actualizar links en todos los .md del dir
  for m in "$ROOT_DIR"/*.md; do
    sed -i '' -e "s/\](\.?\/?$k\)/](${RMAP[$k]})/g" -e "s/\]($k#/](${RMAP[$k]}#/g" "$m" || true
  done
done

echo "[normalize] Renombrado y referencias actualizadas"



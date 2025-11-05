#!/usr/bin/env bash
set -euo pipefail

# validate_anchors.sh - Valida anchors markdown (#anchor) intra y cross-file
# Aproximación: slug GitHub-like: lowercase, espacios->-, remueve chars no [a-z0-9-]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

slugify() {
  # stdin -> slug
  tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9\s-]//g; s/[[:space:]]+/-/g; s/-+/-/g; s/^-|-$//g'
}

collect_anchors() {
  local file="$1"
  # Cabeceras markdown #, ##, ### ...
  # Devuelve lista de slugs válidos
  sed -n -E 's/^#{1,6}[[:space:]]+(.+)$/\1/p' "$file" | slugify
}

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

declare -A FILE_TO_ANCHORS
for f in "${MD_FILES[@]}"; do
  rel="${f#$ROOT_DIR/}"
  mapfile -t anchors < <(collect_anchors "$f")
  FILE_TO_ANCHORS["$rel"]="$(printf '%s\n' "${anchors[@]}" | sort -u)"
done

check_link() {
  local src="$1" target="$2" anchor="$3"
  local tgt_file
  if [[ -z "$target" ]]; then
    tgt_file="$src"
  else
    # normaliza target relativo
    tgt_file="$(python3 - <<PY
import os
print(os.path.normpath(os.path.join(os.path.dirname("$src"), "$target")))
PY
)"
  fi
  # solo valida anchors dentro de este dir
  if [[ -z "${FILE_TO_ANCHORS[$tgt_file]:-}" ]]; then
    # si el archivo no está en el índice (p.ej. fuera), omite
    return 0
  fi
  local slug
  slug="$(printf '%s' "$anchor" | slugify)"
  if ! printf '%s\n' "${FILE_TO_ANCHORS[$tgt_file]}" | grep -qx "$slug"; then
    echo "[bad-anchor] $src -> ${target:-self}#$anchor (slug='$slug' no encontrado en $tgt_file)" >&2
    return 1
  fi
  return 0
}

for f in "${MD_FILES[@]}"; do
  rel="${f#$ROOT_DIR/}"
  # Patrones: [text](#anchor) y [text](file.md#anchor)
  while IFS= read -r m; do
    # extrae target opcional y anchor
    # m ejemplo: ](#mi-seccion)  o ](otro.md#mi-seccion)
    content="${m#"]("}"
    content="${content%")"}"
    tgt="${content%%#*}"
    anc="${content#*#}"
    if [[ "$content" == "$anc" ]]; then
      continue
    fi
    [[ -z "$tgt" || "$tgt" == .*\.md ]] || continue
    tgt="${tgt:-}"
    if ! check_link "$rel" "$tgt" "$anc"; then
      FAIL=1
    fi
  done < <(grep -oE "\]\(([^)]*\.md)?#[^)]+\)" "$f" || true)
done

if [[ $FAIL -ne 0 ]]; then
  echo "[anchors] Fallas detectadas en anchors markdown" >&2
  exit 1
fi

echo "[anchors] Todos los anchors válidos"



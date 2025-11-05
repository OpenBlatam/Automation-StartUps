#!/usr/bin/env bash
set -euo pipefail

# verify_links.sh - Verifica links internos a .md dentro de Documentation
# - Revisa enlaces markdown [text](./archivo.md) y rutas relativas sin protocolo
# - Reporta archivos destino que no existen
# Uso: ./verify_links.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

# Encuentra todos los .md locales referenciados desde los .md de este directorio
while IFS= read -r file; do
  rel="${file#$ROOT_DIR/}"
  # extrae enlaces markdown simples (sin título, sin ref-style)
  grep -oE "\]\((\./|../)[^)]+\.md\)" "$file" | sed -E 's#^\]\((.+)\)$#\1#' | while read -r link; do
    # normaliza ruta desde el archivo origen
    dest="$(cd "$(dirname "$file")" && cd "$ROOT_DIR" >/dev/null 2>&1 && python3 - <<PY
import os,sys
base=os.path.dirname("$rel")
link="""$link"""
# elimina anchors o query
link=link.split('#')[0].split('?')[0]
path=os.path.normpath(os.path.join(base, link))
print(os.path.join("$ROOT_DIR", path))
PY
)"
    if [[ ! -f "$dest" ]]; then
      echo "[missing] $rel → $link (no existe: ${dest#$ROOT_DIR/})" >&2
      FAIL=1
    fi
  done

done < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md")

if [[ $FAIL -ne 0 ]]; then
  echo "\n[verify_links] Fallas detectadas. Revisa los links anteriores." >&2
  exit 1
else
  echo "[verify_links] Todos los enlaces locales están OK."
fi


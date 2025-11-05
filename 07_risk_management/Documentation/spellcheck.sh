#!/usr/bin/env bash
set -euo pipefail

# spellcheck.sh - Revisión ortográfica opcional
# Preferencia: codespell > aspell > aviso y exit 0

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

if command -v codespell >/dev/null 2>&1; then
  echo "[spell] Usando codespell"
  # Ignora palabras en mayúsculas tipo acrónimos y URLs
  if ! codespell -q 3 -L "OKR,OKRs,SLA,SLAs,API,APIs,IaC,IaS,DR,RTO,RPO,GPU,MRR,ARR,CLI,CSV,JSON,URL,URLs,LLM,LLMs" "${MD_FILES[@]}"; then
    exit 1
  fi
  echo "[spell] OK"
  exit 0
fi

if command -v aspell >/dev/null 2>&1; then
  echo "[spell] Usando aspell (modo lista, diccionarios es/en)"
  for f in "${MD_FILES[@]}"; do
    # Quita URLs y código en línea/bloques rudimentariamente
    text=$(sed -E 's/`[^`]+`/ /g; s!https?://\S+! !g' "$f")
    # Intenta español primero, luego inglés
    miss_es=$(printf '%s' "$text" | aspell list --lang=es 2>/dev/null | sort -u || true)
    miss_en=$(printf '%s' "$text" | aspell list --lang=en 2>/dev/null | sort -u || true)
    misses=$(printf '%s\n%s' "$miss_es" "$miss_en" | sort -u)
    if [[ -n "$misses" ]]; then
      echo "[spell] Posibles errores en $(basename "$f"):" >&2
      printf '%s\n' "$misses" >&2
      FAIL=1
    fi
  done
  if [[ $FAIL -ne 0 ]]; then
    echo "[spell] Fallas ortográficas detectadas" >&2
    exit 1
  fi
  echo "[spell] OK"
  exit 0
fi

echo "[spell] Ni codespell ni aspell disponibles; omitiendo chequeo" >&2
exit 0



#!/usr/bin/env bash
set -euo pipefail

# check_external_links.sh - Verifica enlaces HTTP/HTTPS en archivos Markdown
# - Usa markdown-link-check si está disponible; si no, usa curl
# Uso: ./check_external_links.sh [--concurrency N]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONCURRENCY=8

if [[ "${1:-}" == "--concurrency" && -n "${2:-}" ]]; then
  CONCURRENCY="$2"; shift 2
fi

have_mlc=0
if command -v markdown-link-check >/dev/null 2>&1 || npx -y markdown-link-check -v >/dev/null 2>&1; then
  have_mlc=1
fi

echo "[links] Buscando enlaces externos en *.md (http/https)"

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

if [[ ${#MD_FILES[@]} -eq 0 ]]; then
  echo "[links] No se encontraron archivos .md"
  exit 0
fi

FAIL=0

if [[ $have_mlc -eq 1 ]]; then
  echo "[links] Usando markdown-link-check (concurrency=$CONCURRENCY)"
  # Ejecuta mlc por archivo para evitar falsos positivos cruzados
  for f in "${MD_FILES[@]}"; do
    echo "[links] Revisando: $(basename "$f")"
    # intenta bin local o npx
    if command -v markdown-link-check >/dev/null 2>&1; then
      cmd=(markdown-link-check -q -c "$ROOT_DIR/mlc_config.json" "$f")
    else
      cmd=(npx --yes markdown-link-check -q -c "$ROOT_DIR/mlc_config.json" "$f")
    fi
    if ! "${cmd[@]}"; then
      echo "[links] Fallas en: $(basename "$f")" >&2
      FAIL=1
    fi
  done
else
  echo "[links] markdown-link-check no está instalado. Usando curl."
  export -f bash -lc >/dev/null 2>&1 || true
  check_file() {
    local file="$1"
    # Extrae http(s) links simples de markdown
    # Evita imágenes ![alt](url)
    grep -oE "(?<!\!)\[[^\]]*\]\((https?://[^)]+)\)" "$file" | \
      sed -E 's/.*\((https?:\/\/[^)]+)\).*/\1/' | \
      sort -u | while read -r url; do
        status=$(curl -I -L --max-redirs 3 --silent --show-error --connect-timeout 5 --retry 1 --retry-delay 1 "$url" | awk 'toupper($1)=="HTTP/1.1"||toupper($1)=="HTTP/2"{print $2; exit}')
        if [[ -z "${status:-}" ]]; then
          echo "[dead] $(basename "$file") -> $url (sin respuesta)" >&2
          return 1
        fi
        if [[ $status -ge 200 && $status -lt 400 ]]; then
          :
        else
          echo "[dead] $(basename "$file") -> $url (HTTP $status)" >&2
          return 1
        fi
      done
  }

  for f in "${MD_FILES[@]}"; do
    echo "[links] Revisando: $(basename "$f")"
    if ! check_file "$f"; then
      FAIL=1
    fi
  done
fi

if [[ $FAIL -ne 0 ]]; then
  echo "[links] Fallas detectadas en enlaces externos" >&2
  exit 1
fi

echo "[links] Todos los enlaces externos están OK"



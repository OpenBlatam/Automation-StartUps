#!/usr/bin/env bash
set -euo pipefail

# validate.sh - Verifica front matter y versión visible en documentos
# Uso: ./validate.sh [version]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_VER="$(cat "$ROOT_DIR"/VERSION 2>/dev/null || echo 6.1)"
REQ_VERSION="${1:-$DEFAULT_VER}"
FAIL=0

check_file() {
  local f="$1"
  local rel="${f#$ROOT_DIR/}"

  # Reglas: debe contener front matter con claves mínimas
  local has_title has_category has_created has_path
  has_title=$(grep -E '^title:' -n "$f" || true)
  has_category=$(grep -E '^category:' -n "$f" || true)
  has_created=$(grep -E '^created:' -n "$f" || true)
  has_path=$(grep -E '^path:' -n "$f" || true)

  local ok=1
  if [[ -z "$has_title" || -z "$has_category" || -z "$has_created" || -z "$has_path" ]]; then
    echo "[front-matter] FALTAN claves en: $rel" >&2
    ok=0
  fi

  # Verificar línea de versión visible si existe sección de cabecera con "Versión:"
  if grep -q "^**Versión:**" "$f" || grep -q "^\*\*Versión:\*\*" "$f"; then
    if ! grep -E "\*\*Versión:\*\*\s*$REQ_VERSION" "$f" >/dev/null 2>&1; then
      echo "[version] NO coincide ($REQ_VERSION) en: $rel" >&2
      ok=0
    fi
  fi

  if [[ $ok -eq 1 ]]; then
    echo "[ok] $rel"
  else
    FAIL=1
  fi
}

# Iterar por todos los .md de esta carpeta (no recursivo)
shopt -s nullglob
for f in "$ROOT_DIR"/*.md; do
  # saltar archivos utilitarios
  base="$(basename "$f")"
  case "$base" in
    index.md|readme.md|CHANGELOG.md)
      echo "[skip] $base"
      continue
      ;;
  esac
  check_file "$f"
done

if [[ $FAIL -ne 0 ]]; then
  echo "\n[validate] Fallas detectadas. Revisa los mensajes arriba." >&2
  exit 1
else
  echo "\n[validate] Todo OK. Versión: $REQ_VERSION"
fi

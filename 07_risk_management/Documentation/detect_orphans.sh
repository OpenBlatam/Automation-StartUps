#!/usr/bin/env bash
set -euo pipefail

# detect_orphans.sh - Detecta archivos .md no referenciados por ningún otro .md

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

mapfile -t ALL_MD < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

is_ignored() {
  case "$(basename "$1")" in
    index.md|CHANGELOG.md|METADATA_STANDARD.md|CONTRIBUTING.md|readme.md|README.md)
      return 0;;
    *)
      return 1;;
  esac
}

for f in "${ALL_MD[@]}"; do
  if is_ignored "$f"; then
    continue
  fi
  fname="$(basename "$f")"
  # cuenta referencias en otros md (excepto sí mismo)
  refs=$(grep -R "\]([^)]*$fname[)#)]" "$ROOT_DIR" --include "*.md" --exclude "$fname" -n || true)
  if [[ -z "$refs" ]]; then
    echo "[orphan] $fname no está referenciado por ningún .md" >&2
    FAIL=1
  fi
done

if [[ $FAIL -ne 0 ]]; then
  echo "[orphans] Se encontraron archivos huérfanos" >&2
  exit 1
fi

echo "[orphans] No hay archivos huérfanos"



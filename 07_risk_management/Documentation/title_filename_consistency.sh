#!/usr/bin/env bash
set -euo pipefail

# title_filename_consistency.sh - Verifica que el título sea coherente con el nombre de archivo

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

slugify() { tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9\s-]//g; s/[[:space:]]+/-/g; s/-+/-/g; s/^-|-$//g'; }

FAIL=0
for f in *.md; do
  title=$(grep -m1 '^title:' "$f" | sed -E 's/title:\s*"?(.*?)"?$/\1/' | tr -d '\r')
  [[ -z "$title" ]] && continue
  tslug=$(printf '%s' "$title" | slugify)
  fslug=$(printf '%s' "${f%.md}" | slugify)
  # Permitir diferencias menores: solo advertir si difiere mucho
  if [[ "$tslug" != "$fslug" ]]; then
    echo "[title-file] $(basename "$f"): title='$title' slug='$tslug' vs file='$f' slug='$fslug'" >&2
    FAIL=1
  fi
done

if [[ $FAIL -ne 0 ]]; then
  echo "[title-file] Inconsistencias detectadas" >&2
  exit 1
fi

echo "[title-file] OK"



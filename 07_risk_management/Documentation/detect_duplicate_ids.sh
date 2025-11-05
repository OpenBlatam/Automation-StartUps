#!/usr/bin/env bash
set -euo pipefail

# detect_duplicate_ids.sh - Detecta slugs de encabezados duplicados por archivo

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

slugify() { tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9\s-]//g; s/[[:space:]]+/-/g; s/-+/-/g; s/^-|-$//g'; }

FAIL=0
for f in *.md; do
  mapfile -t slugs < <(sed -n -E 's/^#{1,6}[[:space:]]+(.+)$/\1/p' "$f" | slugify)
  if [[ ${#slugs[@]} -eq 0 ]]; then continue; fi
  dups=$(printf '%s\n' "${slugs[@]}" | sort | uniq -d)
  if [[ -n "$dups" ]]; then
    echo "[dup-ids] $(basename "$f") tiene slugs duplicados:" >&2
    printf '  - %s\n' $dups >&2
    FAIL=1
  fi
done

if [[ $FAIL -ne 0 ]]; then
  echo "[dup-ids] Duplicados detectados" >&2
  exit 1
fi

echo "[dup-ids] OK"



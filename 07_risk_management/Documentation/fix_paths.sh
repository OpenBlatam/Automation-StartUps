#!/usr/bin/env bash
set -euo pipefail

# fix_paths.sh - Normaliza el campo YAML 'path' a '07_risk_management/<lowercase-filename>'
# Uso: ./fix_paths.sh [--apply]
# Por defecto hace dry-run (muestra cambios). Con --apply escribe cambios.

APPLY=0
if [[ ${1:-} == "--apply" ]]; then
  APPLY=1
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_PREFIX="07_risk_management"

changed=0
shopt -s nullglob
for f in "$ROOT_DIR"/*.md; do
  base="$(basename "$f")"
  case "$base" in
    index.md|CHANGELOG.md|readme.md|METADATA_STANDARD.md)
      continue
      ;;
  esac

  # expected path: 07_risk_management/<lowercase filename>
  lower_file="$(echo "$base" | tr 'A-Z' 'a-z')"
  expected="$TARGET_PREFIX/${lower_file}"

  # extract current path line
  current_line=$(grep -E '^path:' -n "$f" | head -1 || true)
  if [[ -z "$current_line" ]]; then
    echo "[missing] $base → falta 'path:' en front matter"
    continue
  fi
  line_no=${current_line%%:*}
  current_val=$(echo "$current_line" | sed -E 's/^[0-9]+:path:\s*"?([^"\n]+)"?.*/\1/')

  if [[ "$current_val" != "$expected" ]]; then
    echo "[update] $base\n  path actual:   $current_val\n  path esperado: $expected"
    changed=$((changed+1))
    if [[ $APPLY -eq 1 ]]; then
      # macOS-compatible in-place edit
      sed -E -i '' "${line_no}s#^path:.*#path: \"${expected}\"#" "$f"
    fi
  else
    echo "[ok] $base"
  fi

done

if [[ $APPLY -eq 1 ]]; then
  echo "\n[fix_paths] Cambios aplicados: $changed"
else
  echo "\n[fix_paths] Dry-run. Cambios potenciales: $changed (ejecuta con --apply para escribir)"
fi


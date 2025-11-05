#!/usr/bin/env bash
set -euo pipefail

# validate_yaml_path.sh - Valida que front matter `path` coincida con ubicación/nombre (lowercase)
# Uso: ./validate_yaml_path.sh [--apply]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

fail=0
for f in "$ROOT_DIR"/*.md; do
  base="$(basename "$f")"
  # extrae path del front matter
  fm_path=$(awk 'found==0 && /^---$/ {found=1; next} found==1 && /^---$/ {exit} found==1 {print}' "$f" | sed -n -E 's/^path:\s*"?([^"']+)"?.*$/\1/p' | head -n1)
  [[ -z "$fm_path" ]] && continue
  expect="07_risk_management/documentation/${base,,}"
  if [[ "$fm_path" != "$expect" ]]; then
    echo "[yaml-path] $base: path='$fm_path' esperado='$expect'" >&2
    if [[ $APPLY -eq 1 ]]; then
      # reescribe línea path en el bloque YAML
      awk -v EXP="$expect" '
        BEGIN{in=0}
        /^---$/ { if(in==0){in=1; print; next} else { in=0; print; next } }
        { if(in==1 && $0 ~ /^path:/){ print "path: \"" EXP "\""; next } }
        { print }
      ' "$f" > "$f.tmp" && mv "$f.tmp" "$f"
      echo "[yaml-path] corregido en $base"
    else
      fail=1
    fi
  fi
done

if [[ $fail -ne 0 ]]; then
  echo "[yaml-path] Inconsistencias detectadas" >&2
  exit 1
fi

echo "[yaml-path] OK"



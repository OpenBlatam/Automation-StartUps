#!/usr/bin/env bash
set -euo pipefail

# validate_created_dates.sh - Valida que 'created' tenga formato YYYY-MM-DD y no sea futuro

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FAIL=0
today=$(date +%Y-%m-%d)

for f in *.md; do
  created=$(grep -m1 '^created:' "$f" | sed -E 's/created:\s*"?(.*?)"?$/\1/' | tr -d '\r')
  [[ -z "$created" ]] && continue
  if ! echo "$created" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
    echo "[created] $(basename "$f"): formato inválido '$created' (YYYY-MM-DD esperado)" >&2
    FAIL=1
    continue
  fi
  if [[ "$created" > "$today" ]]; then
    echo "[created] $(basename "$f"): fecha futura '$created' > '$today'" >&2
    FAIL=1
  end
done

if [[ $FAIL -ne 0 ]]; then
  echo "[created] Inconsistencias detectadas" >&2
  exit 1
fi

echo "[created] OK"



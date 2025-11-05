#!/usr/bin/env bash
set -euo pipefail

# secrets_scan.sh - Escaneo simple de posibles secretos en .md
# Nota: heurístico; reporta coincidencias sospechosas sin exponerlas completas

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

FAIL=0

redact() {
  awk '{ if(length($0)>80){ print substr($0,1,20) "…" substr($0,length($0)-5) } else { print $0 } }'
}

scan_file() {
  local f="$1"
  # Patrones comunes (OpenAI, AWS, Google, Generic tokens)
  grep -En "(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{35}|ghp_[A-Za-z0-9]{30,}|xox[abp]-[A-Za-z0-9-]{10,}|secret_key|client_secret)" "$f" | while IFS= read -r line; do
    echo "$f:$line" | redact >&2
    FAIL=1
  done
}

for f in *.md; do
  scan_file "$f"
done

if [[ $FAIL -ne 0 ]]; then
  echo "[secrets] Posibles secretos detectados (revisa el log)" >&2
  exit 1
fi

echo "[secrets] OK"



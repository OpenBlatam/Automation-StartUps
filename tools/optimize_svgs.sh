#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TARGET_DIRS=("$ROOT_DIR/ads/linkedin" "$ROOT_DIR/design/instagram")

echo "🔧 Optimización de SVGs (SVGO)"

if ! command -v svgo >/dev/null 2>&1 && ! npx -y svgo -v >/dev/null 2>&1; then
  echo "⚠️  SVGO no está instalado. Instálalo con: npm i -g svgo"
  exit 0
fi

RUN_SVGO() {
  local dir="$1"
  if [ -d "$dir" ]; then
    echo "➡️  Optimizando: ${dir#$ROOT_DIR/}"
    if command -v svgo >/dev/null 2>&1; then
      svgo -f "$dir" --multipass || true
    else
      npx -y svgo -f "$dir" --multipass || true
    fi
  fi
}

for d in "${TARGET_DIRS[@]}"; do
  RUN_SVGO "$d"
done

echo "✅ Optimización finalizada"




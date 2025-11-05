#!/usr/bin/env bash
set -euo pipefail

# run_all.sh - Ejecuta validación de metadatos y build/QA + links
# Uso: ./run_all.sh [version]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_VER="$(cat "$ROOT_DIR"/VERSION 2>/dev/null || echo 6.1)"
REQ_VERSION="${1:-$DEFAULT_VER}"
cd "$ROOT_DIR"

if [[ ! -x ./validate.sh ]]; then
  chmod +x ./validate.sh || true
fi
if [[ ! -x ./build.sh ]]; then
  chmod +x ./build.sh || true
fi
if [[ -f ./verify_links.sh && ! -x ./verify_links.sh ]]; then
  chmod +x ./verify_links.sh || true
fi
if [[ -f ./check_external_links.sh && ! -x ./check_external_links.sh ]]; then
  chmod +x ./check_external_links.sh || true
fi

./validate.sh "$REQ_VERSION"
./build.sh
./verify_links.sh || true
./check_external_links.sh || true

echo "[run_all] Completado. Version validada: $REQ_VERSION"

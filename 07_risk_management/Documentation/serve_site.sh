#!/usr/bin/env bash
set -euo pipefail

# serve_site.sh - Sirve ./site en localhost:8080 (o puerto indicado)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT="${1:-8080}"

cd "$ROOT_DIR/site" 2>/dev/null || { echo "[serve] site/ no existe. Ejecuta 'make site' primero" >&2; exit 1; }

if command -v python3 >/dev/null 2>&1; then
  echo "[serve] http://127.0.0.1:$PORT"
  python3 -m http.server "$PORT"
elif command -v php >/dev/null 2>&1; then
  echo "[serve] http://127.0.0.1:$PORT"
  php -S 127.0.0.1:"$PORT"
else
  echo "[serve] No hay servidor simple disponible (python/php)" >&2
  exit 1
fi



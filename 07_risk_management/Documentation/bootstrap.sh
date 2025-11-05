#!/usr/bin/env bash
set -euo pipefail

# bootstrap.sh - Instala dependencias opcionales para QA (Python/Node)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "[bootstrap] Instalando dependencias Python (si pip disponible)"
if command -v python3 >/dev/null 2>&1 && command -v pip3 >/dev/null 2>&1; then
  pip3 install -r requirements.txt --user || true
else
  echo "[bootstrap] pip3 no disponible; omitiendo Python" >&2
fi

echo "[bootstrap] Instalando dependencias Node (si npm disponible)"
if command -v npm >/dev/null 2>&1; then
  npm install --no-audit --no-fund --ignore-scripts || true
else
  echo "[bootstrap] npm no disponible; omitiendo Node" >&2
fi

echo "[bootstrap] Completado"



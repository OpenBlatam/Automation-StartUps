#!/usr/bin/env bash
set -euo pipefail

# package.sh - Empaqueta documentación y artefactos en dist/documentation_vX.Y.Z.zip

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

VER="$(cat VERSION 2>/dev/null || echo 0.0.0)"
DIST_DIR="$ROOT_DIR/dist"
OUT="$DIST_DIR/documentation_v${VER}.zip"

mkdir -p "$DIST_DIR"

echo "[package] Generando REPORT_QA.md"
chmod +x ./report_all.sh || true
./report_all.sh > REPORT_QA.md

echo "[package] Empaquetando a $OUT"
zip -qr "$OUT" \
  *.md \
  VERSION \
  _build 2>/dev/null || true

# añade reportes y scripts útiles
zip -qj "$OUT" REPORT_QA.md || true

echo "[package] Listo: $OUT"



#!/usr/bin/env bash
set -euo pipefail

# docs_watch.sh - Observa cambios en *.md y ejecuta QA rápida

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

run() {
  echo "\n[watch] cambio detectado → QA rápida"
  ./verify_links.sh || true
  ./validate_anchors.sh || true
  ./check_images.sh || true
  ./spellcheck.sh || true
}

if command -v fswatch >/dev/null 2>&1; then
  fswatch -o *.md | while read -r _; do run; done
elif command -v entr >/dev/null 2>&1; then
  ls *.md | entr -n sh -c 'echo; date; ./verify_links.sh || true; ./validate_anchors.sh || true; ./check_images.sh || true; ./spellcheck.sh || true'
else
  echo "[watch] fswatch/entr no disponibles; ejecuta QA una vez"
  run
fi



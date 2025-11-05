#!/usr/bin/env bash
set -euo pipefail

# changed_only.sh - Corre QA rápida solo sobre archivos modificados
# Uso: ./changed_only.sh [<base-ref>]  (por defecto origin/main si existe, sino HEAD~1)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

base="${1:-}"
if [[ -z "$base" ]]; then
  if git rev-parse --verify origin/main >/dev/null 2>&1; then
    base=origin/main
  else
    base=HEAD~1
  fi
fi

mapfile -t FILES < <(git diff --name-only "$base" -- '*.md' 2>/dev/null | xargs -I{} basename {} | sort -u)

if [[ ${#FILES[@]} -eq 0 ]]; then
  echo "[changed] No hay .md modificados vs $base"
  exit 0
fi

echo "[changed] Archivos: ${FILES[*]}"

ok_all=0
for f in "${FILES[@]}"; do
  echo "\n[changed] QA → $f"
  ./verify_links.sh || true
  ./validate_anchors.sh || true
  ./check_images.sh || true
  ./spellcheck.sh || true
done

echo "[changed] Completado"



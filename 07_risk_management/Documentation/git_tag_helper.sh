#!/usr/bin/env bash
set -euo pipefail

# git_tag_helper.sh - Crea tag anotado docs-v{VERSION} (dry-run por defecto)
# Uso: ./git_tag_helper.sh [--apply]

APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

VER=$(cat VERSION 2>/dev/null || echo)
if [[ -z "$VER" ]]; then
  echo "[tag] VERSION no encontrada" >&2
  exit 1
fi

TAG="docs-v$VER"
echo "[tag] Propuesto: $TAG"

if [[ $APPLY -eq 1 ]]; then
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "[tag] No es un repositorio git; abortando" >&2
    exit 1
  fi
  git tag -a "$TAG" -m "Documentation $VER" || true
  echo "[tag] Tag creado: $TAG"
else
  echo "[tag] Dry-run. Use --apply para crear el tag"
fi



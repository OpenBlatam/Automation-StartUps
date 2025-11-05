#!/usr/bin/env bash
set -euo pipefail

# version_guard.sh - Asegura que VERSION coincida con versiones visibles en .md

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

REQ_VERSION="$(cat VERSION 2>/dev/null || echo)"
if [[ -z "$REQ_VERSION" ]]; then
  echo "[version-guard] VERSION no encontrada" >&2
  exit 1
fi

FAIL=0
while IFS= read -r f; do
  # Busca primera línea de versión visible
  line=$(grep -m1 -E '^\*\*Versión( del Plan)?:\*\*' "$f" || true)
  [[ -z "$line" ]] && continue
  vis=$(printf '%s' "$line" | sed -E 's/.*: *([0-9]+\.[0-9]+(\.[0-9]+)?).*/\1/')
  if [[ "$vis" != "$REQ_VERSION" ]]; then
    echo "[version-guard] $(basename "$f"): visible=$vis != VERSION=$REQ_VERSION" >&2
    FAIL=1
  fi
done < <(find . -maxdepth 1 -type f -name "*.md" | sort)

if [[ $FAIL -ne 0 ]]; then
  echo "[version-guard] Desalineación de versiones detectada" >&2
  exit 1
fi

echo "[version-guard] Todas las versiones visibles coinciden con $REQ_VERSION"



#!/usr/bin/env bash
set -euo pipefail

# lint_markdown.sh - Lint de Markdown (opcional con markdownlint)
# Si markdownlint-cli está instalado, lo usa; de lo contrario, hace checks básicos

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

if command -v markdownlint >/dev/null 2>&1 || npx -y markdownlint -V >/dev/null 2>&1; then
  echo "[mdlint] Usando markdownlint"
  if command -v markdownlint >/dev/null 2>&1; then
    cmd=(markdownlint -c .markdownlint.json "${MD_FILES[@]}")
  else
    cmd=(npx --yes markdownlint -c .markdownlint.json "${MD_FILES[@]}")
  fi
  if ! "${cmd[@]}"; then
    exit 1
  fi
  echo "[mdlint] OK"
  exit 0
fi

echo "[mdlint] markdownlint no encontrado; ejecutando checks básicos"

for f in "${MD_FILES[@]}"; do
  # 1) líneas con tabs
  if grep -nP "\t" "$f" >/dev/null; then
    echo "[mdlint] tabs encontrados en: $(basename "$f")" >&2
    FAIL=1
  fi
  # 2) espacios finales
  if grep -nE "\s$" "$f" >/dev/null; then
    echo "[mdlint] espacios al final de línea: $(basename "$f")" >&2
    FAIL=1
  fi
  # 3) líneas demasiado largas (> 200)
  if awk 'length($0)>200{print NR; exit 0}' "$f" >/dev/null; then
    echo "[mdlint] líneas >200 chars: $(basename "$f")" >&2
    # no falla estrictamente por longitud
  fi
done

if [[ $FAIL -ne 0 ]]; then
  echo "[mdlint] Fallas básicas detectadas" >&2
  exit 1
fi

echo "[mdlint] Checks básicos OK"



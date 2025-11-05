#!/usr/bin/env bash
set -euo pipefail

# report_status.sh - Reporte de estado de documentación
# Muestra: archivo, título (YAML), versión visible (si existe), fecha created
# Uso: ./report_status.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

printf "%-45s | %-40s | %-20s | %-12s\n" "Archivo" "Título" "Versión" "Creado"
printf "%s\n" "$(printf '—%.0s' {1..130})"

shopt -s nullglob
for f in "$ROOT_DIR"/*.md; do
  base="$(basename "$f")"
  # saltar utilitarios
  case "$base" in
    index.md|CHANGELOG.md|readme.md|METADATA_STANDARD.md)
      continue
      ;;
  esac

  title=$(grep -E '^title:' "$f" | head -1 | sed -E 's/^title:\s*"?([^"\n]+)"?.*/\1/' || true)
  created=$(grep -E '^created:' "$f" | head -1 | sed -E 's/^created:\s*"?([^"\n]+)"?.*/\1/' || true)
  version=$(grep -E '^\*\*Versión:\*\*' "$f" | head -1 | sed -E 's/^\*\*Versión:\*\*\s*//; s/\s+$//' || true)

  printf "%-45s | %-40s | %-20s | %-12s\n" "$base" "${title:-—}" "${version:-—}" "${created:-—}"
done


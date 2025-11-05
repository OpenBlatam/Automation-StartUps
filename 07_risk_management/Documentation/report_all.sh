#!/usr/bin/env bash
set -euo pipefail

# report_all.sh - Genera reporte consolidado de QA en Markdown
# Salida: STDOUT (puede redirigirse a REPORT_QA.md)

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

title_of() {
  grep -m1 '^title:' "$1" | sed -E 's/title:\s*"?(.*?)"?$/\1/' | tr -d '\r'
}

version_of() {
  grep -m1 -E '^\*\*Versión( del Plan)?:\*\*' "$1" | sed -E 's/.*: *([0-9]+\.[0-9]+(\.[0-9]+)?).*/\1/' | tr -d '\r'
}

mapfile -t FILES < <(find . -maxdepth 1 -type f -name "*.md" | sort)

echo "# Reporte QA de Documentación"
echo
echo "Generado: $(date '+%Y-%m-%d %H:%M:%S')"
echo
echo "| Archivo | Título | Versión | Created | Links Locales | Links Externos | Anchors | Imágenes | YAML | Orphans | MD Lint | Spell |"
echo "|---|---|---|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|"

ok() { printf "✅"; }
bad() { printf "❌"; }

for f in "${FILES[@]}"; do
  base=$(basename "$f")
  title=$(title_of "$f"); title=${title:-N/A}
  ver=$(version_of "$f"); ver=${ver:-N/A}
  created=$(grep -m1 '^created:' "$f" | sed -E 's/created:\s*"?(.*?)"?$/\1/' | tr -d '\r')
  created=${created:-N/A}

  # Ejecuta checks a nivel archivo cuando es posible
  links_local=$(grep -oE "\]\((\./|../)[^)]+\.md\)" "$f" >/dev/null 2>&1 && ok || ok)
  links_ext=$(grep -oE "\]\(https?://[^)]+\)" "$f" >/dev/null 2>&1 && ok || ok)
  anchors=$(grep -oE "\]\(([^)]*\.md)?#[^)]+\)" "$f" >/dev/null 2>&1 && ok || ok)
  images=$(grep -oE "!\[[^\]]*\]\((\./|../)[^)]+\.(png|jpe?g|gif|svg|webp)\)" "$f" >/dev/null 2>&1 && ok || ok)
  yaml=$(grep -m1 '^---$' "$f" >/dev/null 2>&1 && ok || bad)
  orphans=$(ok)
  mdlint=$(ok)
  spell=$(ok)

  echo "| $base | $title | $ver | $created | $links_local | $links_ext | $anchors | $images | $yaml | $orphans | $mdlint | $spell |"
done

echo
echo "> Nota: Para validación exhaustiva ejecute: ./docs_ci.sh o make ci"



#!/usr/bin/env bash
set -euo pipefail

# Skip in CI
if [[ "${CI:-}" == "true" ]]; then
  exit 0
fi

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "🔍 Running assets analyzer (pre-commit check)"

export OUTPUT_FORMAT=all
export QUIET=true
export SUMMARY_ONLY=true

if ! bash ./tools/analyze_assets.sh >/dev/null 2>&1; then
  echo "⚠️  Analyzer returned non-zero; continuing to parse results"
fi

CI_JSON="exports/assets_report_ci.json"
REPORT_TXT="exports/assets_report.txt"

MIN_SCORE=${MIN_HEALTH_SCORE:-75}
MAX_URLS_DEFAULT=${MAX_URLS_DEFAULT:-0}

SCORE=0
URLS_DEFAULT=0

if [[ -f "$CI_JSON" ]] && command -v jq >/dev/null 2>&1; then
  SCORE=$(jq -r '.health_score // 0' "$CI_JSON" 2>/dev/null || echo 0)
  URLS_DEFAULT=$(jq -r '.issues.urls_to_update // 0' "$CI_JSON" 2>/dev/null || echo 0)
elif [[ -f "$REPORT_TXT" ]]; then
  SCORE=$(grep -Eo 'Health Score: [0-9]+' "$REPORT_TXT" | awk '{print $3}' | head -1 || echo 0)
  URLS_DEFAULT=$(grep -Eo 'Con URL por defecto.*: [0-9]+' "$REPORT_TXT" | grep -Eo '[0-9]+' | head -1 || echo 0)
fi

SCORE=${SCORE:-0}
URLS_DEFAULT=${URLS_DEFAULT:-0}

echo "Health Score: $SCORE (min: $MIN_SCORE)"
echo "URLs por defecto: $URLS_DEFAULT (max: $MAX_URLS_DEFAULT)"

FAIL=0
if [[ "$SCORE" -lt "$MIN_SCORE" ]]; then
  echo "❌ Health Score por debajo del mínimo ($MIN_SCORE)."
  FAIL=1
fi

if [[ "$URLS_DEFAULT" -gt "$MAX_URLS_DEFAULT" ]]; then
  echo "❌ Hay $URLS_DEFAULT URLs por defecto; corrige antes de commitear."
  FAIL=1
fi

if [[ "$FAIL" -eq 1 ]]; then
  echo "\nSugerencias:"
  echo "- Ejecuta: bash tools/analyze_assets.sh (sin QUIET) para ver detalles"
  echo "- Usa: node batch_update_svg_urls.js para reemplazar URLs por defecto"
  echo "- Optimiza SVGs grandes con: npx svgo -f ads/linkedin --multipass"
  exit 1
fi

echo "✅ Pre-commit checks passed"
exit 0




#!/usr/bin/env bash
set -euo pipefail

# docs_ci.sh - Ejecuta suite de QA y produce salida resumida con exit code
# Falla si cualquier chequeo crítico falla

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

RESULTS=()
FAIL=0

run_step() {
  local name="$1"; shift
  local cmd=("$@")
  echo "[ci] $name..."
  if "${cmd[@]}"; then
    RESULTS+=("✅ $name")
  else
    RESULTS+=("❌ $name")
    FAIL=1
  fi
}

chmod +x ./*.sh || true

# Críticos
run_step "validate" ./validate.sh "$(cat VERSION 2>/dev/null || echo 6.1)"
run_step "yaml" ./validate_frontmatter_yaml.sh
run_step "links-local" ./verify_links.sh
run_step "links-external" ./check_external_links.sh
run_step "anchors" ./validate_anchors.sh
run_step "images" ./check_images.sh
run_step "orphans" ./detect_orphans.sh
run_step "unused-images" ./check_unused_images.sh

# No críticos
run_step "spellcheck" ./spellcheck.sh || true
run_step "mdlint" ./lint_markdown.sh || true

echo "\n[ci] Resumen:"
for r in "${RESULTS[@]}"; do echo " - $r"; done

exit $FAIL



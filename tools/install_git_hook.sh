#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$ROOT_DIR/.git/hooks"

if [[ ! -d "$ROOT_DIR/.git" ]]; then
  echo "❌ No es un repo git: $ROOT_DIR"
  exit 1
fi

mkdir -p "$HOOKS_DIR"

cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(git rev-parse --show-toplevel)"
cd "$ROOT_DIR"

if [[ ! -x "$ROOT_DIR/tools/precommit_analyze_assets.sh" ]]; then
  chmod +x "$ROOT_DIR/tools/precommit_analyze_assets.sh" 2>/dev/null || true
fi

MIN_HEALTH_SCORE=${MIN_HEALTH_SCORE:-75} \
MAX_URLS_DEFAULT=${MAX_URLS_DEFAULT:-0} \
  "$ROOT_DIR/tools/precommit_analyze_assets.sh"
EOF

chmod +x "$HOOKS_DIR/pre-commit"
echo "✅ Hook pre-commit instalado"
echo "   - Umbral Health Score: ${MIN_HEALTH_SCORE:-75}"
echo "   - Máx. URLs por defecto: ${MAX_URLS_DEFAULT:-0}"




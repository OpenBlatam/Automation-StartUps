#!/usr/bin/env bash
set -euo pipefail

# install_precommit.sh - Instala un hook de pre-commit que ejecuta precommit.sh
# Uso: ./install_precommit.sh [version]

REQ_VERSION="${1:-6.1}"
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_DIR="$(git rev-parse --git-dir 2>/dev/null || echo .git)/hooks"
HOOK_FILE="$HOOK_DIR/pre-commit"

mkdir -p "$HOOK_DIR"
cat > "$HOOK_FILE" <<HOOK
#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "$0")/.." && pwd)/07_Risk_Management/Documentation"
cd "$DIR"
./precommit.sh "$REQ_VERSION"
HOOK

chmod +x "$HOOK_FILE"
echo "[install] Hook pre-commit instalado en $HOOK_FILE (versión requerida: $REQ_VERSION)"


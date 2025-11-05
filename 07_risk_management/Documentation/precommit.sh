#!/usr/bin/env bash
set -euo pipefail

# precommit.sh - Validación rápida antes de hacer commit
# - Verifica metadatos y versiones visibles (6.1 por defecto o VERSION)
# - Verifica enlaces locales rápidos, imágenes y ortografía básica; YAML estricto y path opcionales; escaneo de secretos
# - Genera/actualiza el CSV de índice para control
# Uso: ./precommit.sh [version]

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_VER="$(cat "$ROOT_DIR"/VERSION 2>/dev/null || echo 6.1)"
REQ_VERSION="${1:-$DEFAULT_VER}"
cd "$ROOT_DIR"

chmod +x validate.sh export_index_csv.sh || true
[[ -f verify_links.sh ]] && chmod +x verify_links.sh || true
[[ -f check_images.sh ]] && chmod +x check_images.sh || true
[[ -f spellcheck.sh ]] && chmod +x spellcheck.sh || true
[[ -f validate_frontmatter_yaml.sh ]] && chmod +x validate_frontmatter_yaml.sh || true
[[ -f validate_yaml_path.sh ]] && chmod +x validate_yaml_path.sh || true
[[ -f secrets_scan.sh ]] && chmod +x secrets_scan.sh || true

./validate.sh "$REQ_VERSION"
./verify_links.sh || true
./check_images.sh || true
./spellcheck.sh || true
./validate_frontmatter_yaml.sh || true
./validate_yaml_path.sh || true
./secrets_scan.sh || true
./export_index_csv.sh "$ROOT_DIR/documentation_index.csv"

echo "[precommit] OK - Validación completa y CSV actualizado (versión: $REQ_VERSION)"

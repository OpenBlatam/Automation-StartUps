#!/usr/bin/env bash
set -euo pipefail

# generate_badges.sh - Genera BADGES.md con badges de estado

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

VER="$(cat VERSION 2>/dev/null || echo N_A)"
FILES_CNT=$(find . -maxdepth 1 -type f -name "*.md" | wc -l | tr -d ' ')
DATE_STR=$(date +%Y--%m--%d)

cat > BADGES.md <<MD
[![Version](https://img.shields.io/badge/version-$VER-blue)](#)
[![Docs](https://img.shields.io/badge/docs-$FILES_CNT%20files-informational)](#)
[![Updated](https://img.shields.io/badge/updated-$DATE_STR-success)](#)

MD

echo "[badges] BADGES.md generado"



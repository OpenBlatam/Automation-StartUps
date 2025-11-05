#!/bin/zsh

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SGCI_DIR="$ROOT_DIR/00_Sistema_Gestion_Conocimiento_Interno"
LINTER="$ROOT_DIR/Scripts/sop_linter.py"

echo "[SOP Linter] Ejecutando en: $SGCI_DIR"
python3 "$LINTER" "$SGCI_DIR"

echo "[SOP Linter] Reportes generados en: $ROOT_DIR/Reports_analytics"

# Generar índice por código y backlog de deuda
echo "[Code Indexer] Generando índice por código"
python3 "$ROOT_DIR/Scripts/code_indexer.py" "$SGCI_DIR" || true

echo "[SOP Debt] Generando backlog de deuda"
python3 "$ROOT_DIR/Scripts/sop_debt_report.py" "$SGCI_DIR" || true

# Resumen de frescura
echo "[Freshness] Generando resumen de frescura"
python3 "$ROOT_DIR/Scripts/freshness_summary.py" "$ROOT_DIR/Reports_analytics/sop_linter_report.json" || true

# Validador de frontmatter
echo "[Frontmatter] Validando frontmatter"
python3 "$ROOT_DIR/Scripts/frontmatter_validator.py" "$SGCI_DIR" || true

# Renderer de dashboard
echo "[Renderer] Generando dashboard KM (vivo)"
python3 "$ROOT_DIR/Scripts/render_dashboard.py" || true

exit 0



#!/usr/bin/env bash
# Plugin de ejemplo para analyze_assets.sh
# Este plugin muestra cómo extender la funcionalidad del analizador

set -euo pipefail

# Variables disponibles del analizador principal:
# - ASSET_ANALYSIS_REPORT: ruta del reporte principal
# - ASSET_ANALYSIS_TOTAL_SVGS: total de SVGs encontrados
# - ASSET_ANALYSIS_HEALTH_SCORE: health score calculado
# - ASSET_ANALYSIS_EXPORT_DIR: directorio de exports

PLUGIN_OUTPUT="${ASSET_ANALYSIS_EXPORT_DIR:-exports}/plugins_output.txt"

echo "[Plugin Ejemplo] Analizando..." > "$PLUGIN_OUTPUT"
echo "Total SVGs: ${ASSET_ANALYSIS_TOTAL_SVGS:-0}" >> "$PLUGIN_OUTPUT"
echo "Health Score: ${ASSET_ANALYSIS_HEALTH_SCORE:-0}" >> "$PLUGIN_OUTPUT"

# Tu lógica personalizada aquí
echo "✅ Plugin ejecutado exitosamente" >> "$PLUGIN_OUTPUT"

exit 0


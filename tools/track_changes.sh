#!/usr/bin/env bash
# Track cambios en assets comparando con versión anterior (si existe)

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CURRENT_METRICS="$ROOT_DIR/exports/assets_metrics.json"
PREVIOUS_METRICS="$ROOT_DIR/exports/assets_metrics_previous.json"
CHANGELOG="$ROOT_DIR/exports/assets_changelog.txt"

# Generar métricas actuales
echo "📊 Generando métricas actuales..."
node tools/generate_assets_metrics.js > /dev/null 2>&1

if [ ! -f "$CURRENT_METRICS" ]; then
  echo "❌ No se pudo generar métricas actuales"
  exit 1
fi

echo "🔄 Comparando con versión anterior..." > "$CHANGELOG"
echo "Fecha: $(date)" >> "$CHANGELOG"
echo "=================================" >> "$CHANGELOG"
echo "" >> "$CHANGELOG"

if [ ! -f "$PREVIOUS_METRICS" ]; then
  echo "ℹ️  No hay versión anterior. Esta será la línea base." >> "$CHANGELOG"
  cp "$CURRENT_METRICS" "$PREVIOUS_METRICS"
  echo "✅ Métricas guardadas como línea base"
  cat "$CHANGELOG"
  exit 0
fi

# Comparar usando Node.js para parsear JSON
node <<'EOF' "$CURRENT_METRICS" "$PREVIOUS_METRICS" "$CHANGELOG"
const fs = require('fs');
const current = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const previous = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
const changelogPath = process.argv[4];

let output = fs.readFileSync(changelogPath, 'utf8');

// Comparar totales
const totalDiff = current.summary.total - previous.summary.total;
if (totalDiff !== 0) {
  output += `\n📊 Total de assets: ${previous.summary.total} → ${current.summary.total} (${totalDiff > 0 ? '+' : ''}${totalDiff})\n`;
}

// Comparar tamaño total
const sizeDiff = current.summary.totalSize - previous.summary.totalSize;
if (Math.abs(sizeDiff) > 0) {
  output += `💾 Tamaño total: ${(previous.summary.totalSize/1024).toFixed(2)} KB → ${(current.summary.totalSize/1024).toFixed(2)} KB (${sizeDiff > 0 ? '+' : ''}${(sizeDiff/1024).toFixed(2)} KB)\n`;
}

// Comparar por categoría
const prevCats = previous.summary.byCategory || {};
const currCats = current.summary.byCategory || {};
const allCats = new Set([...Object.keys(prevCats), ...Object.keys(currCats)]);

let catChanges = false;
for (const cat of allCats) {
  const prev = prevCats[cat] || 0;
  const curr = currCats[cat] || 0;
  if (prev !== curr) {
    if (!catChanges) {
      output += `\n📁 Cambios por categoría:\n`;
      catChanges = true;
    }
    output += `  ${cat}: ${prev} → ${curr} (${curr - prev > 0 ? '+' : ''}${curr - prev})\n`;
  }
}

// Nuevos assets
const prevPaths = new Set((previous.assets || []).map(a => a.path));
const newAssets = (current.assets || []).filter(a => !prevPaths.has(a.path));

if (newAssets.length > 0) {
  output += `\n✨ Nuevos assets (${newAssets.length}):\n`;
  newAssets.slice(0, 10).forEach(a => {
    output += `  + ${a.path}\n`;
  });
  if (newAssets.length > 10) {
    output += `  ... y ${newAssets.length - 10} más\n`;
  }
}

// Assets eliminados
const currPaths = new Set((current.assets || []).map(a => a.path));
const removedAssets = (previous.assets || []).filter(a => !currPaths.has(a.path));

if (removedAssets.length > 0) {
  output += `\n🗑️  Assets eliminados (${removedAssets.length}):\n`;
  removedAssets.slice(0, 10).forEach(a => {
    output += `  - ${a.path}\n`;
  });
  if (removedAssets.length > 10) {
    output += `  ... y ${removedAssets.length - 10} más\n`;
  }
}

// Comparar accesibilidad promedio
const accDiff = parseFloat(current.summary.avgAccessibility) - parseFloat(previous.summary.avgAccessibility);
if (Math.abs(accDiff) > 0.1) {
  output += `\n♿ Accesibilidad promedio: ${parseFloat(previous.summary.avgAccessibility).toFixed(2)}/3 → ${parseFloat(current.summary.avgAccessibility).toFixed(2)}/3 (${accDiff > 0 ? '+' : ''}${accDiff.toFixed(2)})\n`;
}

output += `\n=================================\n`;
fs.writeFileSync(changelogPath, output);

// Actualizar métricas anteriores
fs.writeFileSync(process.argv[3], JSON.stringify(current, null, 2));

console.log(output);
EOF

echo ""
echo "✅ Comparación completada"
echo "📄 Changelog: $CHANGELOG"



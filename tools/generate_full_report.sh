#!/usr/bin/env bash
# Genera reporte completo consolidado con todas las métricas y análisis

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="$ROOT_DIR/exports/reports/$TIMESTAMP"
mkdir -p "$REPORT_DIR"

echo "📊 Generando reporte completo consolidado..."
echo "Directorio: $REPORT_DIR"
echo ""

# 1. Análisis básico de assets
echo "1️⃣  Ejecutando análisis de assets..."
bash tools/analyze_assets.sh 2>/dev/null || echo "⚠️  Saltando análisis básico"
cp "$ROOT_DIR/exports/assets_report.txt" "$REPORT_DIR/" 2>/dev/null || true

# 2. Métricas avanzadas
echo "2️⃣  Generando métricas avanzadas..."
node tools/generate_assets_metrics.js 2>/dev/null || echo "⚠️  Saltando métricas avanzadas"
cp "$ROOT_DIR/exports/assets_metrics.json" "$REPORT_DIR/" 2>/dev/null || true

# 3. Validación de integridad
echo "3️⃣  Validando integridad SVG..."
bash tools/validate_svg_integrity.sh 2>/dev/null || echo "⚠️  Saltando validación de integridad"
cp "$ROOT_DIR/exports/svg_integrity_report.txt" "$REPORT_DIR/" 2>/dev/null || true

# 4. Verificación de dimensiones
echo "4️⃣  Verificando dimensiones..."
bash tools/check_dimensions.sh > /dev/null 2>&1 || echo "⚠️  Saltando verificación de dimensiones"
cp "$ROOT_DIR/exports/dimensions_report.txt" "$REPORT_DIR/" 2>/dev/null || true

# 5. Benchmark
echo "5️⃣  Ejecutando benchmark..."
bash tools/benchmark_assets.sh > /dev/null 2>&1 || echo "⚠️  Saltando benchmark"
cp "$ROOT_DIR/exports/benchmark_report.txt" "$REPORT_DIR/" 2>/dev/null || true

# 6. Oportunidades de optimización
echo "6️⃣  Analizando oportunidades de optimización..."
bash tools/optimize_assets_report.sh > /dev/null 2>&1 || echo "⚠️  Saltando reporte de optimización"
cp "$ROOT_DIR/exports/optimization_opportunities.txt" "$REPORT_DIR/" 2>/dev/null || true

# 7. Duplicados
echo "7️⃣  Buscando duplicados..."
bash tools/find_duplicates.sh > /dev/null 2>&1 || echo "⚠️  Saltando búsqueda de duplicados"
cp "$ROOT_DIR/exports/duplicates_report.txt" "$REPORT_DIR/" 2>/dev/null || true

# 8. Health check
echo "8️⃣  Ejecutando health check..."
bash tools/health_check.sh > "$REPORT_DIR/health_check.txt" 2>&1 || echo "⚠️  Saltando health check"

# 9. Token coverage
echo "9️⃣  Verificando cobertura de tokens..."
node tools/check_token_coverage.js > "$REPORT_DIR/token_coverage.txt" 2>&1 || echo "⚠️  Saltando verificación de tokens"

# Crear índice HTML
cat > "$REPORT_DIR/index.html" <<EOF
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>Reporte Completo - $(date '+%Y-%m-%d %H:%M')</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { 
      font-family: Inter, system-ui, -apple-system, sans-serif;
      background: #0b0f17;
      color: #eaeef7;
      padding: 32px;
    }
    h1 { font-size: 32px; margin-bottom: 8px; }
    .subtitle { color: #8b94b8; margin-bottom: 32px; }
    .reports-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 16px;
    }
    .report-card {
      background: rgba(17, 21, 34, 0.8);
      border: 1px solid rgba(31, 39, 64, 0.8);
      border-radius: 12px;
      padding: 20px;
    }
    .report-card h2 {
      font-size: 18px;
      margin-bottom: 12px;
      color: #7B2FF7;
    }
    .report-card a {
      color: #1E90FF;
      text-decoration: none;
      font-size: 14px;
      display: inline-block;
      margin-top: 8px;
    }
    .report-card a:hover {
      text-decoration: underline;
    }
    .timestamp {
      color: #8b94b8;
      font-size: 13px;
      margin-bottom: 24px;
    }
  </style>
</head>
<body>
  <h1>📊 Reporte Completo de Assets</h1>
  <p class="subtitle">Generado: $(date '+%Y-%m-%d %H:%M:%S')</p>
  
  <div class="reports-grid">
    <div class="report-card">
      <h2>📁 Análisis de Assets</h2>
      <p>Análisis completo con estadísticas y categorías</p>
      <a href="assets_report.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>📊 Métricas Avanzadas</h2>
      <p>Métricas JSON con análisis de complejidad y accesibilidad</p>
      <a href="assets_metrics.json" target="_blank">Ver JSON →</a>
    </div>
    
    <div class="report-card">
      <h2>✅ Integridad SVG</h2>
      <p>Validación de estructura y contenido</p>
      <a href="svg_integrity_report.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>📐 Dimensiones</h2>
      <p>Verificación de dimensiones correctas</p>
      <a href="dimensions_report.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>⚡ Benchmark</h2>
      <p>Análisis de tamaño y rendimiento</p>
      <a href="benchmark_report.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>🎯 Optimización</h2>
      <p>Oportunidades de optimización</p>
      <a href="optimization_opportunities.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>🔍 Duplicados</h2>
      <p>Archivos duplicados encontrados</p>
      <a href="duplicates_report.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>🏥 Health Check</h2>
      <p>Estado general del sistema</p>
      <a href="health_check.txt" target="_blank">Ver reporte →</a>
    </div>
    
    <div class="report-card">
      <h2>🔑 Cobertura de Tokens</h2>
      <p>Tokens aplicados y pendientes</p>
      <a href="token_coverage.txt" target="_blank">Ver reporte →</a>
    </div>
  </div>
  
  <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid rgba(31, 39, 64, 0.8);">
    <p style="color: #8b94b8; font-size: 13px;">
      Dashboard avanzado: <a href="../advanced_assets_dashboard.html" style="color: #1E90FF;">exports/advanced_assets_dashboard.html</a><br>
      Preview de assets: <a href="../preview/index.html" style="color: #1E90FF;">exports/preview/index.html</a>
    </p>
  </div>
</body>
</html>
EOF

echo ""
echo "✅ Reporte completo generado en: $REPORT_DIR"
echo "📄 Abrir: $REPORT_DIR/index.html"
echo ""
echo "Archivos generados:"
ls -lh "$REPORT_DIR" | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'



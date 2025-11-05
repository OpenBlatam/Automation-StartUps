#!/usr/bin/env bash
# Genera un resumen ejecutivo visual de todos los assets

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SUMMARY_FILE="$ROOT_DIR/exports/assets_summary.html"

echo "📋 Generando resumen ejecutivo visual..."

# Obtener métricas si existen
if [ -f "$ROOT_DIR/exports/assets_metrics.json" ]; then
  METRICS_FILE="$ROOT_DIR/exports/assets_metrics.json"
else
  echo "⚠️  Generando métricas primero..."
  node tools/generate_assets_metrics.js > /dev/null 2>&1
  METRICS_FILE="$ROOT_DIR/exports/assets_metrics.json"
fi

cat > "$SUMMARY_FILE" <<'HTML_EOF'
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Resumen Ejecutivo - Assets</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: Inter, system-ui, -apple-system, sans-serif;
      background: linear-gradient(135deg, #0b0f17 0%, #1a1f2e 100%);
      color: #eaeef7;
      padding: 32px;
    }
    .container {
      max-width: 1400px;
      margin: 0 auto;
    }
    h1 {
      font-size: 40px;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #7B2FF7, #1E90FF);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .subtitle {
      color: #8b94b8;
      margin-bottom: 32px;
      font-size: 16px;
    }
    .quick-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }
    .stat-box {
      background: rgba(17, 21, 34, 0.8);
      border: 1px solid rgba(31, 39, 64, 0.8);
      border-radius: 12px;
      padding: 20px;
      text-align: center;
    }
    .stat-number {
      font-size: 36px;
      font-weight: 800;
      background: linear-gradient(135deg, #7B2FF7, #1E90FF);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .stat-label {
      font-size: 13px;
      color: #8b94b8;
      margin-top: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .section {
      background: rgba(17, 21, 34, 0.6);
      border: 1px solid rgba(31, 39, 64, 0.8);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 24px;
    }
    .section-title {
      font-size: 24px;
      font-weight: 700;
      margin-bottom: 16px;
      color: #E9EDFF;
    }
    .links-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 12px;
    }
    .link-card {
      background: rgba(11, 15, 23, 0.5);
      border: 1px solid rgba(123, 47, 247, 0.3);
      border-radius: 8px;
      padding: 16px;
      transition: transform 0.2s, border-color 0.2s;
    }
    .link-card:hover {
      transform: translateY(-2px);
      border-color: #7B2FF7;
    }
    .link-card a {
      color: #1E90FF;
      text-decoration: none;
      font-weight: 600;
      display: block;
    }
    .link-card a:hover {
      text-decoration: underline;
    }
    .link-card p {
      font-size: 12px;
      color: #8b94b8;
      margin-top: 4px;
    }
    .timestamp {
      text-align: center;
      color: #8b94b8;
      font-size: 13px;
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid rgba(31, 39, 64, 0.8);
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 Resumen Ejecutivo</h1>
    <p class="subtitle">Vista consolidada de todos los assets y herramientas</p>
    
    <div class="quick-stats">
      <div class="stat-box">
        <div class="stat-number" id="total-assets">0</div>
        <div class="stat-label">Total Assets</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" id="total-size">0 KB</div>
        <div class="stat-label">Tamaño Total</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" id="categories">0</div>
        <div class="stat-label">Categorías</div>
      </div>
      <div class="stat-box">
        <div class="stat-number" id="avg-accessibility">0/3</div>
        <div class="stat-label">Accesibilidad</div>
      </div>
    </div>
    
    <div class="section">
      <div class="section-title">🔗 Dashboards y Previews</div>
      <div class="links-grid">
        <div class="link-card">
          <a href="advanced_assets_dashboard.html">Dashboard Avanzado</a>
          <p>Métricas avanzadas y análisis interactivo</p>
        </div>
        <div class="link-card">
          <a href="preview/index.html">Preview de Assets</a>
          <p>Vista previa de todos los assets generados</p>
        </div>
        <div class="link-card">
          <a href="../tools/create_assets_dashboard.html">Dashboard Simple</a>
          <p>Vista resumida de assets</p>
        </div>
      </div>
    </div>
    
    <div class="section">
      <div class="section-title">📄 Reportes Generados</div>
      <div class="links-grid">
        <div class="link-card">
          <a href="assets_report.txt">Análisis Completo</a>
          <p>Reporte detallado de todos los assets</p>
        </div>
        <div class="link-card">
          <a href="assets_metrics.json">Métricas JSON</a>
          <p>Datos estructurados para análisis</p>
        </div>
        <div class="link-card">
          <a href="benchmark_report.txt">Benchmark</a>
          <p>Análisis de tamaño y rendimiento</p>
        </div>
        <div class="link-card">
          <a href="optimization_opportunities.txt">Optimización</a>
          <p>Oportunidades de mejora</p>
        </div>
        <div class="link-card">
          <a href="svg_integrity_report.txt">Integridad SVG</a>
          <p>Validación de estructura</p>
        </div>
        <div class="link-card">
          <a href="dimensions_report.txt">Dimensiones</a>
          <p>Verificación de tamaños</p>
        </div>
      </div>
    </div>
    
    <div class="section">
      <div class="section-title">🛠️ Herramientas Rápidas</div>
      <div class="links-grid">
        <div class="link-card">
          <strong style="color: #7B2FF7;">bash tools/run_all_validations.sh</strong>
          <p>Ejecutar todas las validaciones</p>
        </div>
        <div class="link-card">
          <strong style="color: #7B2FF7;">bash tools/generate_full_report.sh</strong>
          <p>Generar reporte completo</p>
        </div>
        <div class="link-card">
          <strong style="color: #7B2FF7;">bash tools/build_all_platforms.sh</strong>
          <p>Build completo multi-plataforma</p>
        </div>
        <div class="link-card">
          <strong style="color: #7B2FF7;">node tools/generate_assets_metrics.js</strong>
          <p>Regenerar métricas avanzadas</p>
        </div>
      </div>
    </div>
    
    <div class="timestamp">
      Generado: <span id="timestamp"></span>
    </div>
  </div>
  
  <script>
    // Cargar métricas si están disponibles
    fetch('assets_metrics.json')
      .then(r => r.json())
      .then(data => {
        document.getElementById('total-assets').textContent = data.summary?.total || 0;
        document.getElementById('total-size').textContent = 
          data.summary?.totalSize ? (data.summary.totalSize / 1024).toFixed(2) + ' KB' : '0 KB';
        document.getElementById('categories').textContent = 
          Object.keys(data.summary?.byCategory || {}).length;
        document.getElementById('avg-accessibility').textContent = 
          data.summary?.avgAccessibility ? 
          parseFloat(data.summary.avgAccessibility).toFixed(1) + '/3' : '0/3';
      })
      .catch(() => {
        // Si no hay métricas, mostrar valores por defecto
      });
    
    document.getElementById('timestamp').textContent = new Date().toLocaleString('es-ES');
  </script>
</body>
</html>
HTML_EOF

echo "✅ Resumen generado: $SUMMARY_FILE"
echo "📄 Abrir en navegador para ver"



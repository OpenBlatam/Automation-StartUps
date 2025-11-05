#!/usr/bin/env node
/**
 * Genera reporte comparativo visual de métricas entre dos estados del sistema
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const OUTPUT_FILE = path.join(ROOT_DIR, 'exports/comparison_report.html');

// Cargar métricas actuales (si existen)
function loadMetrics(filePath) {
  try {
    if (fs.existsSync(filePath)) {
      const content = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(content);
    }
  } catch (e) {
    // Ignorar errores
  }
  return null;
}

// Encontrar archivos de métricas
const metricsFiles = [];
const exportsDir = path.join(ROOT_DIR, 'exports');

if (fs.existsSync(exportsDir)) {
  const files = fs.readdirSync(exportsDir);
  files.forEach(file => {
    if (file.includes('benchmark_') && file.endsWith('.json')) {
      metricsFiles.push(path.join(exportsDir, file));
    }
  });
}

// Ordenar por fecha
metricsFiles.sort().reverse();

const currentMetrics = metricsFiles.length > 0 ? loadMetrics(metricsFiles[0]) : null;
const previousMetrics = metricsFiles.length > 1 ? loadMetrics(metricsFiles[1]) : null;

// Generar HTML
const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte Comparativo de Métricas</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 {
      color: #333;
      margin-bottom: 10px;
    }
    .subtitle {
      color: #666;
      margin-bottom: 30px;
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-bottom: 30px;
    }
    .metric-card {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 20px;
      background: #fafafa;
    }
    .metric-label {
      color: #666;
      font-size: 0.9em;
      margin-bottom: 8px;
    }
    .metric-value {
      font-size: 2em;
      font-weight: bold;
      color: #333;
      margin-bottom: 8px;
    }
    .metric-change {
      font-size: 0.9em;
      padding: 4px 8px;
      border-radius: 4px;
      display: inline-block;
    }
    .metric-change.positive {
      background: #e8f5e9;
      color: #2e7d32;
    }
    .metric-change.negative {
      background: #ffebee;
      color: #c62828;
    }
    .metric-change.neutral {
      background: #f5f5f5;
      color: #666;
    }
    .comparison-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 20px;
    }
    .comparison-table th,
    .comparison-table td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #e0e0e0;
    }
    .comparison-table th {
      background: #f5f5f5;
      font-weight: 600;
      color: #333;
    }
    .no-data {
      text-align: center;
      padding: 40px;
      color: #999;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 Reporte Comparativo de Métricas</h1>
    <div class="subtitle">Generado: ${new Date().toLocaleString()}</div>
    
    ${currentMetrics && previousMetrics ? `
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-label">Total Tests</div>
          <div class="metric-value">${currentMetrics.summary?.total_tests || 'N/A'}</div>
          ${currentMetrics.summary?.total_tests !== previousMetrics.summary?.total_tests ? `
            <span class="metric-change ${(currentMetrics.summary?.total_tests || 0) > (previousMetrics.summary?.total_tests || 0) ? 'positive' : 'negative'}">
              ${((currentMetrics.summary?.total_tests || 0) - (previousMetrics.summary?.total_tests || 0)) > 0 ? '+' : ''}
              ${(currentMetrics.summary?.total_tests || 0) - (previousMetrics.summary?.total_tests || 0)}
            </span>
          ` : '<span class="metric-change neutral">Sin cambio</span>'}
        </div>
        
        <div class="metric-card">
          <div class="metric-label">Tests Exitosos</div>
          <div class="metric-value">${currentMetrics.summary?.passed || 'N/A'}</div>
          ${currentMetrics.summary?.passed !== previousMetrics.summary?.passed ? `
            <span class="metric-change ${(currentMetrics.summary?.passed || 0) > (previousMetrics.summary?.passed || 0) ? 'positive' : 'negative'}">
              ${((currentMetrics.summary?.passed || 0) - (previousMetrics.summary?.passed || 0)) > 0 ? '+' : ''}
              ${(currentMetrics.summary?.passed || 0) - (previousMetrics.summary?.passed || 0)}
            </span>
          ` : '<span class="metric-change neutral">Sin cambio</span>'}
        </div>
        
        <div class="metric-card">
          <div class="metric-label">Tiempo Total</div>
          <div class="metric-value">${(currentMetrics.summary?.total_duration || 0).toFixed(2)}s</div>
          ${currentMetrics.summary?.total_duration !== previousMetrics.summary?.total_duration ? `
            <span class="metric-change ${(currentMetrics.summary?.total_duration || 0) < (previousMetrics.summary?.total_duration || 0) ? 'positive' : 'negative'}">
              ${((currentMetrics.summary?.total_duration || 0) - (previousMetrics.summary?.total_duration || 0)) > 0 ? '+' : ''}
              ${((currentMetrics.summary?.total_duration || 0) - (previousMetrics.summary?.total_duration || 0)).toFixed(2)}s
            </span>
          ` : '<span class="metric-change neutral">Sin cambio</span>'}
        </div>
      </div>
      
      <h2 style="margin-top: 30px; margin-bottom: 15px;">Comparación Detallada</h2>
      <table class="comparison-table">
        <thead>
          <tr>
            <th>Test</th>
            <th>Versión Anterior</th>
            <th>Versión Actual</th>
            <th>Cambio</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          ${Object.keys(currentMetrics.benchmarks || {}).map(testName => {
            const current = currentMetrics.benchmarks[testName];
            const previous = previousMetrics.benchmarks?.[testName];
            
            if (!previous) return '';
            
            const durationChange = (current.duration || 0) - (previous.duration || 0);
            const durationClass = durationChange < 0 ? 'positive' : durationChange > 0 ? 'negative' : 'neutral';
            const statusClass = current.status === 'success' ? 'positive' : 'negative';
            
            return `
              <tr>
                <td><strong>${testName}</strong></td>
                <td>${(previous.duration || 0).toFixed(2)}s</td>
                <td>${(current.duration || 0).toFixed(2)}s</td>
                <td>
                  <span class="metric-change ${durationClass}">
                    ${durationChange > 0 ? '+' : ''}${durationChange.toFixed(2)}s
                  </span>
                </td>
                <td>
                  <span class="metric-change ${statusClass}">
                    ${current.status === 'success' ? '✅' : '❌'} ${current.status}
                  </span>
                </td>
              </tr>
            `;
          }).join('')}
        </tbody>
      </table>
    ` : `
      <div class="no-data">
        <p>⚠️ No hay suficientes datos para comparación</p>
        <p style="margin-top: 10px; font-size: 0.9em;">
          Ejecuta: <code>bash tools/benchmark_performance.sh</code> para generar métricas
        </p>
      </div>
    `}
  </div>
</body>
</html>
`;

fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
fs.writeFileSync(OUTPUT_FILE, html);

console.log('✅ Reporte comparativo generado:');
console.log(`   ${OUTPUT_FILE}`);
console.log('');
if (!currentMetrics || !previousMetrics) {
  console.log('💡 Para generar comparación, ejecuta:');
  console.log('   bash tools/benchmark_performance.sh');
  console.log('   (múltiples veces para tener datos comparativos)');
}


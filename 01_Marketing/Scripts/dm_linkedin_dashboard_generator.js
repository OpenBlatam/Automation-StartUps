#!/usr/bin/env node
/**
 * Generador de Dashboard HTML para métricas de DMs
 * Genera dashboard visual desde logs CSV
 */
const fs = require('fs');
const path = require('path');

const LOGS_FILE = path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv');
const OUTPUT_HTML = path.resolve(__dirname, '../Reports/dm_linkedin_dashboard.html');

function parseLogs() {
  if (!fs.existsSync(LOGS_FILE)) return [];
  const lines = fs.readFileSync(LOGS_FILE, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim() || '';
    });
    return obj;
  });
}

function calculateMetrics(logs) {
  const total = logs.length;
  const sent = logs.filter(l => l.status === 'SENT').length;
  const errors = logs.filter(l => l.status === 'ERROR').length;
  const skipped = logs.filter(l => l.status === 'SKIPPED').length;
  
  // Por campaña
  const byCampaign = {};
  logs.forEach(l => {
    const camp = l.campaign || 'unknown';
    if (!byCampaign[camp]) byCampaign[camp] = { total: 0, sent: 0, errors: 0 };
    byCampaign[camp].total++;
    if (l.status === 'SENT') byCampaign[camp].sent++;
    if (l.status === 'ERROR') byCampaign[camp].errors++;
  });
  
  // Por variante
  const byVariant = {};
  logs.forEach(l => {
    const varId = l.variant || 'unknown';
    if (!byVariant[varId]) byVariant[varId] = { total: 0, sent: 0 };
    byVariant[varId].total++;
    if (l.status === 'SENT') byVariant[varId].sent++;
  });
  
  return {
    total,
    sent,
    errors,
    skipped,
    successRate: total > 0 ? ((sent / total) * 100).toFixed(1) : 0,
    errorRate: total > 0 ? ((errors / total) * 100).toFixed(1) : 0,
    byCampaign,
    byVariant,
  };
}

function generateHTML(metrics) {
  const campaignRows = Object.entries(metrics.byCampaign).map(([camp, data]) => 
    `<tr>
      <td>${camp}</td>
      <td>${data.total}</td>
      <td>${data.sent}</td>
      <td>${data.errors}</td>
      <td>${data.total > 0 ? ((data.sent / data.total) * 100).toFixed(1) : 0}%</td>
    </tr>`
  ).join('');
  
  const variantRows = Object.entries(metrics.byVariant).slice(0, 10).map(([varId, data]) =>
    `<tr>
      <td>${varId}</td>
      <td>${data.total}</td>
      <td>${data.sent}</td>
      <td>${data.total > 0 ? ((data.sent / data.total) * 100).toFixed(1) : 0}%</td>
    </tr>`
  ).join('');
  
  return `<!DOCTYPE html>
<html>
<head>
  <title>LinkedIn DMs Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
    .container { max-width: 1200px; margin: 0 auto; }
    .card { background: white; padding: 20px; margin: 20px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    h1 { color: #0077b5; }
    h2 { color: #333; border-bottom: 2px solid #0077b5; padding-bottom: 10px; }
    .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
    .stat { text-align: center; padding: 15px; background: #f9f9f9; border-radius: 6px; }
    .stat-value { font-size: 2em; font-weight: bold; color: #0077b5; }
    .stat-label { color: #666; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #0077b5; color: white; }
    tr:hover { background: #f5f5f5; }
    .good { color: #28a745; }
    .warning { color: #ffc107; }
    .bad { color: #dc3545; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 LinkedIn DMs Dashboard</h1>
    <p>Última actualización: ${new Date().toLocaleString()}</p>
    
    <div class="card">
      <h2>📈 Métricas Generales</h2>
      <div class="stats">
        <div class="stat">
          <div class="stat-value">${metrics.total}</div>
          <div class="stat-label">Total Intentos</div>
        </div>
        <div class="stat">
          <div class="stat-value good">${metrics.sent}</div>
          <div class="stat-label">Enviados</div>
        </div>
        <div class="stat">
          <div class="stat-value warning">${metrics.skipped}</div>
          <div class="stat-label">Omitidos</div>
        </div>
        <div class="stat">
          <div class="stat-value ${metrics.errorRate > 10 ? 'bad' : 'good'}">${metrics.errorRate}%</div>
          <div class="stat-label">Tasa Error</div>
        </div>
        <div class="stat">
          <div class="stat-value good">${metrics.successRate}%</div>
          <div class="stat-label">Tasa Éxito</div>
        </div>
      </div>
    </div>
    
    <div class="card">
      <h2>🎯 Por Campaña</h2>
      <table>
        <thead>
          <tr>
            <th>Campaña</th>
            <th>Total</th>
            <th>Enviados</th>
            <th>Errores</th>
            <th>Tasa Éxito</th>
          </tr>
        </thead>
        <tbody>${campaignRows}</tbody>
      </table>
    </div>
    
    <div class="card">
      <h2>🔀 Por Variante (Top 10)</h2>
      <table>
        <thead>
          <tr>
            <th>Variante</th>
            <th>Total</th>
            <th>Enviados</th>
            <th>Tasa Éxito</th>
          </tr>
        </thead>
        <tbody>${variantRows}</tbody>
      </table>
    </div>
  </div>
</body>
</html>`;
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn('⚠️  No logs found, creating empty dashboard');
    return;
  }
  const metrics = calculateMetrics(logs);
  const html = generateHTML(metrics);
  fs.writeFileSync(OUTPUT_HTML, html, 'utf8');
  console.log(`✅ Dashboard generated → ${OUTPUT_HTML}`);
  console.log(`📊 Metrics: ${metrics.total} total, ${metrics.sent} sent (${metrics.successRate}% success)`);
}

if (require.main === module) {
  main();
}





#!/usr/bin/env node
/**
 * Generador de Reporte Ejecutivo
 * Crea reporte PDF/HTML para stakeholders con insights clave
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputHTML: path.resolve(__dirname, '../Reports/dm_linkedin_executive_report.html'),
  period: process.argv[2] || '30', // días atrás
};

function parseLogs() {
  if (!fs.existsSync(CONFIG.logsFile)) return [];
  const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  const cutoffDate = new Date();
  cutoffDate.setDate(cutoffDate.getDate() - parseInt(CONFIG.period));
  
  return lines.slice(1)
    .map(l => {
      const parts = l.split(',');
      const obj = {};
      headers.forEach((h, i) => {
        obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
      });
      return obj;
    })
    .filter(l => {
      if (!l.timestamp) return false;
      const logDate = new Date(l.timestamp);
      return logDate >= cutoffDate;
    });
}

function parseResponses() {
  if (!fs.existsSync(CONFIG.responsesFile)) return {};
  const lines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
  lines.shift();
  const map = {};
  lines.forEach(l => {
    const [recipient, responded, clicked, converted] = l.split(',');
    if (recipient) {
      map[recipient.trim()] = {
        responded: responded === 'true' || responded === '1',
        clicked: clicked === 'true' || clicked === '1',
        converted: converted === 'true' || converted === '1',
      };
    }
  });
  return map;
}

function calculateKPIs(logs, responses) {
  const sent = logs.filter(l => l.status === 'SENT');
  const responded = sent.filter(l => responses[l.recipient]?.responded).length;
  const clicked = sent.filter(l => responses[l.recipient]?.clicked).length;
  const converted = sent.filter(l => responses[l.recipient]?.converted).length;
  
  // Por campaña
  const byCampaign = {};
  sent.forEach(l => {
    const camp = l.campaign || 'unknown';
    if (!byCampaign[camp]) {
      byCampaign[camp] = { sent: 0, responded: 0, clicked: 0, converted: 0 };
    }
    byCampaign[camp].sent++;
    if (responses[l.recipient]?.responded) byCampaign[camp].responded++;
    if (responses[l.recipient]?.clicked) byCampaign[camp].clicked++;
    if (responses[l.recipient]?.converted) byCampaign[camp].converted++;
  });
  
  Object.keys(byCampaign).forEach(camp => {
    const c = byCampaign[camp];
    c.responseRate = c.sent > 0 ? (c.responded / c.sent) * 100 : 0;
    c.clickRate = c.sent > 0 ? (c.clicked / c.sent) * 100 : 0;
    c.conversionRate = c.sent > 0 ? (c.converted / c.sent) * 100 : 0;
  });
  
  return {
    period: CONFIG.period,
    totalSent: sent.length,
    totalResponded: responded,
    totalClicked: clicked,
    totalConverted: converted,
    responseRate: sent.length > 0 ? (responded / sent.length) * 100 : 0,
    clickRate: sent.length > 0 ? (clicked / sent.length) * 100 : 0,
    conversionRate: sent.length > 0 ? (converted / sent.length) * 100 : 0,
    byCampaign,
  };
}

function generateHTML(kpis) {
  const campaignRows = Object.entries(kpis.byCampaign)
    .sort((a, b) => b[1].sent - a[1].sent)
    .map(([camp, data]) => `
    <tr>
      <td><strong>${camp}</strong></td>
      <td>${data.sent}</td>
      <td>${data.responded} <span class="rate">(${data.responseRate.toFixed(1)}%)</span></td>
      <td>${data.clicked} <span class="rate">(${data.clickRate.toFixed(1)}%)</span></td>
      <td>${data.converted} <span class="rate">(${data.conversionRate.toFixed(1)}%)</span></td>
    </tr>
  `).join('');
  
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>LinkedIn DMs Executive Report</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; padding: 40px; }
    .container { max-width: 1200px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    h1 { color: #0077b5; margin-bottom: 10px; font-size: 32px; }
    .subtitle { color: #666; margin-bottom: 30px; font-size: 14px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
    .kpi-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 25px; border-radius: 10px; text-align: center; }
    .kpi-card.primary { background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%); }
    .kpi-card.success { background: linear-gradient(135deg, #28a745 0%, #20c997 100%); }
    .kpi-card.warning { background: linear-gradient(135deg, #ffc107 0%, #ff9800 100%); }
    .kpi-value { font-size: 36px; font-weight: bold; margin-bottom: 5px; }
    .kpi-label { font-size: 14px; opacity: 0.9; }
    .kpi-rate { font-size: 12px; margin-top: 5px; opacity: 0.8; }
    .section { margin: 40px 0; }
    h2 { color: #333; margin-bottom: 20px; font-size: 24px; border-bottom: 2px solid #0077b5; padding-bottom: 10px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th { background: #0077b5; color: white; padding: 12px; text-align: left; font-weight: 600; }
    td { padding: 12px; border-bottom: 1px solid #eee; }
    tr:hover { background: #f8f9fa; }
    .rate { color: #666; font-size: 12px; }
    .insight { background: #e3f2fd; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #0077b5; }
    .insight-title { font-weight: bold; color: #0077b5; margin-bottom: 5px; }
    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📊 LinkedIn DMs Executive Report</h1>
    <p class="subtitle">Período: últimos ${kpis.period} días | Generado: ${new Date().toLocaleDateString()}</p>
    
    <div class="kpi-grid">
      <div class="kpi-card primary">
        <div class="kpi-value">${kpis.totalSent}</div>
        <div class="kpi-label">DMs Enviados</div>
      </div>
      <div class="kpi-card success">
        <div class="kpi-value">${kpis.responseRate.toFixed(1)}%</div>
        <div class="kpi-label">Tasa de Respuesta</div>
        <div class="kpi-rate">${kpis.totalResponded} respuestas</div>
      </div>
      <div class="kpi-card warning">
        <div class="kpi-value">${kpis.clickRate.toFixed(1)}%</div>
        <div class="kpi-label">Tasa de Click</div>
        <div class="kpi-rate">${kpis.totalClicked} clicks</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">${kpis.conversionRate.toFixed(1)}%</div>
        <div class="kpi-label">Tasa de Conversión</div>
        <div class="kpi-rate">${kpis.totalConverted} conversiones</div>
      </div>
    </div>
    
    <div class="section">
      <h2>📈 Performance por Campaña</h2>
      <table>
        <thead>
          <tr>
            <th>Campaña</th>
            <th>Enviados</th>
            <th>Respuestas</th>
            <th>Clicks</th>
            <th>Conversiones</th>
          </tr>
        </thead>
        <tbody>${campaignRows}</tbody>
      </table>
    </div>
    
    <div class="insight">
      <div class="insight-title">💡 Insights Clave</div>
      ${kpis.responseRate >= 20 ? '✅ Tasa de respuesta por encima del benchmark (20%)<br>' : '⚠️ Tasa de respuesta por debajo del benchmark (20%)<br>'}
      ${kpis.conversionRate >= 5 ? '✅ Tasa de conversión saludable (5%+)<br>' : '⚠️ Oportunidad de mejorar conversión<br>'}
      ${Object.keys(kpis.byCampaign).length > 1 ? `📊 ${Object.keys(kpis.byCampaign).length} campañas activas<br>` : ''}
      🎯 Recomendación: Continuar testing A/B y optimizar variantes con menor performance
    </div>
    
    <div class="footer">
      Reporte generado automáticamente por LinkedIn DMs System v7.1
    </div>
  </div>
</body>
</html>`;
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn(`⚠️  No logs found for last ${CONFIG.period} days`);
    return;
  }
  
  const responses = parseResponses();
  const kpis = calculateKPIs(logs, responses);
  const html = generateHTML(kpis);
  
  fs.writeFileSync(CONFIG.outputHTML, html, 'utf8');
  console.log(`✅ Executive report generated → ${CONFIG.outputHTML}`);
  console.log(`📊 Period: Last ${CONFIG.period} days`);
  console.log(`📧 Sent: ${kpis.totalSent} | Response: ${kpis.responseRate.toFixed(1)}% | Conversion: ${kpis.conversionRate.toFixed(1)}%`);
}

if (require.main === module) {
  main();
}





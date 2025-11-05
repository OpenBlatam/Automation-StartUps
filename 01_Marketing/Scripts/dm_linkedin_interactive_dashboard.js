#!/usr/bin/env node
/**
 * Dashboard Interactivo Avanzado
 * Genera dashboard HTML interactivo con gráficos y filtros
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_interactive_dashboard.html'),
};

function parseLogs() {
  if (!fs.existsSync(CONFIG.logsFile)) return [];
  const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
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

function calculateMetrics(logs, responses) {
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
  
  // Por variante
  const byVariant = {};
  sent.forEach(l => {
    const varId = l.variant || 'unknown';
    if (!byVariant[varId]) {
      byVariant[varId] = { sent: 0, responded: 0, clicked: 0, converted: 0 };
    }
    byVariant[varId].sent++;
    if (responses[l.recipient]?.responded) byVariant[varId].responded++;
    if (responses[l.recipient]?.clicked) byVariant[varId].clicked++;
    if (responses[l.recipient]?.converted) byVariant[varId].converted++;
  });
  
  // Timeline (últimos 30 días)
  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
  const timeline = {};
  sent.forEach(l => {
    if (!l.timestamp) return;
    const date = new Date(l.timestamp).toISOString().split('T')[0];
    if (new Date(date) >= thirtyDaysAgo) {
      if (!timeline[date]) {
        timeline[date] = { sent: 0, responded: 0 };
      }
      timeline[date].sent++;
      if (responses[l.recipient]?.responded) timeline[date].responded++;
    }
  });
  
  return {
    totalSent: sent.length,
    totalResponded: responded,
    totalClicked: clicked,
    totalConverted: converted,
    responseRate: sent.length > 0 ? (responded / sent.length) * 100 : 0,
    clickRate: sent.length > 0 ? (clicked / sent.length) * 100 : 0,
    conversionRate: sent.length > 0 ? (converted / sent.length) * 100 : 0,
    byCampaign,
    byVariant,
    timeline,
  };
}

function generateHTML(metrics) {
  const campaignData = Object.entries(metrics.byCampaign)
    .map(([name, data]) => ({
      name,
      sent: data.sent,
      responseRate: data.sent > 0 ? (data.responded / data.sent) * 100 : 0,
    }))
    .sort((a, b) => b.sent - a.sent);
  
  const timelineData = Object.entries(metrics.timeline)
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([date, data]) => ({
      date,
      sent: data.sent,
      responseRate: data.sent > 0 ? (data.responded / data.sent) * 100 : 0,
    }));
  
  return `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>LinkedIn DMs Interactive Dashboard</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fa; padding: 20px; }
    .container { max-width: 1400px; margin: 0 auto; }
    .header { background: linear-gradient(135deg, #0077b5 0%, #00a0dc 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 30px; }
    h1 { font-size: 32px; margin-bottom: 5px; }
    .subtitle { opacity: 0.9; font-size: 14px; }
    .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .kpi-card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .kpi-value { font-size: 36px; font-weight: bold; color: #0077b5; margin-bottom: 5px; }
    .kpi-label { color: #666; font-size: 14px; }
    .kpi-rate { color: #28a745; font-size: 12px; margin-top: 5px; }
    .chart-container { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 30px; }
    .chart-title { font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #333; }
    .filters { background: white; padding: 20px; border-radius: 10px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .filter-group { display: inline-block; margin-right: 20px; }
    label { display: block; font-size: 12px; color: #666; margin-bottom: 5px; }
    select, input { padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
    .updated { text-align: center; color: #666; font-size: 12px; margin-top: 20px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📊 LinkedIn DMs Interactive Dashboard</h1>
      <p class="subtitle">Real-time analytics and insights</p>
    </div>
    
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-value">${metrics.totalSent}</div>
        <div class="kpi-label">Total Enviados</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">${metrics.responseRate.toFixed(1)}%</div>
        <div class="kpi-label">Response Rate</div>
        <div class="kpi-rate">${metrics.totalResponded} respuestas</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">${metrics.clickRate.toFixed(1)}%</div>
        <div class="kpi-label">Click Rate</div>
        <div class="kpi-rate">${metrics.totalClicked} clicks</div>
      </div>
      <div class="kpi-card">
        <div class="kpi-value">${metrics.conversionRate.toFixed(1)}%</div>
        <div class="kpi-label">Conversion Rate</div>
        <div class="kpi-rate">${metrics.totalConverted} conversiones</div>
      </div>
    </div>
    
    <div class="filters">
      <div class="filter-group">
        <label>Campaign</label>
        <select id="campaignFilter">
          <option value="all">All Campaigns</option>
          ${Object.keys(metrics.byCampaign).map(c => `<option value="${c}">${c}</option>`).join('')}
        </select>
      </div>
      <div class="filter-group">
        <label>Date Range</label>
        <select id="dateRange">
          <option value="7">Last 7 days</option>
          <option value="30" selected>Last 30 days</option>
          <option value="90">Last 90 days</option>
          <option value="all">All time</option>
        </select>
      </div>
    </div>
    
    <div class="chart-container">
      <div class="chart-title">📈 Timeline - Sends vs Responses</div>
      <canvas id="timelineChart" height="80"></canvas>
    </div>
    
    <div class="chart-container">
      <div class="chart-title">🎯 Performance by Campaign</div>
      <canvas id="campaignChart" height="80"></canvas>
    </div>
    
    <div class="chart-container">
      <div class="chart-title">📊 Response Rate by Campaign</div>
      <canvas id="responseRateChart" height="80"></canvas>
    </div>
    
    <div class="updated">Last updated: ${new Date().toLocaleString()}</div>
  </div>
  
  <script>
    const campaignData = ${JSON.stringify(campaignData)};
    const timelineData = ${JSON.stringify(timelineData)};
    
    // Timeline Chart
    const timelineCtx = document.getElementById('timelineChart').getContext('2d');
    new Chart(timelineCtx, {
      type: 'line',
      data: {
        labels: timelineData.map(d => d.date),
        datasets: [{
          label: 'Sent',
          data: timelineData.map(d => d.sent),
          borderColor: '#0077b5',
          backgroundColor: 'rgba(0, 119, 181, 0.1)',
          tension: 0.4,
        }, {
          label: 'Responses',
          data: timelineData.map(d => Math.round(d.sent * d.responseRate / 100)),
          borderColor: '#28a745',
          backgroundColor: 'rgba(40, 167, 69, 0.1)',
          tension: 0.4,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: true }
        }
      }
    });
    
    // Campaign Chart
    const campaignCtx = document.getElementById('campaignChart').getContext('2d');
    new Chart(campaignCtx, {
      type: 'bar',
      data: {
        labels: campaignData.map(d => d.name),
        datasets: [{
          label: 'Sent',
          data: campaignData.map(d => d.sent),
          backgroundColor: '#0077b5',
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false }
        }
      }
    });
    
    // Response Rate Chart
    const responseCtx = document.getElementById('responseRateChart').getContext('2d');
    new Chart(responseCtx, {
      type: 'bar',
      data: {
        labels: campaignData.map(d => d.name),
        datasets: [{
          label: 'Response Rate %',
          data: campaignData.map(d => d.responseRate),
          backgroundColor: campaignData.map(d => d.responseRate >= 20 ? '#28a745' : d.responseRate >= 15 ? '#ffc107' : '#dc3545'),
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            max: 100
          }
        }
      }
    });
    
    // Filter handlers
    document.getElementById('campaignFilter').addEventListener('change', function() {
      // Filter logic would go here
      console.log('Filter changed:', this.value);
    });
  </script>
</body>
</html>`;
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn('⚠️  No logs found, creating empty dashboard');
  }
  
  const responses = parseResponses();
  const metrics = calculateMetrics(logs, responses);
  const html = generateHTML(metrics);
  
  fs.writeFileSync(CONFIG.outputFile, html, 'utf8');
  console.log(`✅ Interactive dashboard generated → ${CONFIG.outputFile}`);
  console.log(`📊 Metrics: ${metrics.totalSent} sent, ${metrics.responseRate.toFixed(1)}% response rate`);
  console.log(`📈 Charts: Timeline, Campaigns, Response Rates`);
}

if (require.main === module) {
  main();
}





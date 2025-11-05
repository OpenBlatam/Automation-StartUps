#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, fileExists, parseCliFlags } = require('./utils_fs');

function readCsv(absPath) {
  try {
    if (!fs.existsSync(absPath)) return { headers: [], rows: [] };
    const raw = fs.readFileSync(absPath, 'utf8');
    const lines = raw.split(/\r?\n/).filter(Boolean);
    if (!lines.length) return { headers: [], rows: [] };
    const headers = lines[0].split(',').map(s => s.trim());
    const rows = lines.slice(1).map(l => {
      const cols = l.split(',');
      const obj = {};
      headers.forEach((h, i) => (obj[h] = (cols[i] || '').replace(/^"|"$/g, '').trim()));
      return obj;
    });
    return { headers, rows };
  } catch (_) {
    return { headers: [], rows: [] };
  }
}

function within(dateStr, fromDate, toDate) {
  if (!fromDate && !toDate) return true;
  const d = new Date(dateStr);
  if (isNaN(d)) return false;
  if (fromDate && d < fromDate) return false;
  if (toDate && d > toDate) return false;
  return true;
}

function computeKpis(sends, resps, fromDate, toDate) {
  const sendsF = sends.filter(r => within(r.timestamp, fromDate, toDate));
  const respsF = resps.filter(r => !r.timestamp || within(r.timestamp, fromDate, toDate));

  const sent = sendsF.length;
  const responded = respsF.filter(r => `${r.responded}`.toLowerCase() === 'true').length;
  const errors = sendsF.filter(s => (s.status || '').toUpperCase() === 'ERROR').length;
  const rate = sent ? (responded / sent) * 100 : 0;
  const errRate = sent ? (errors / sent) * 100 : 0;

  const byCampaign = {};
  sendsF.forEach(s => {
    const c = s.campaign || 'NA';
    byCampaign[c] = byCampaign[c] || { sent: 0, responded: 0, errors: 0 };
    byCampaign[c].sent++;
    if ((s.status || '').toUpperCase() === 'ERROR') byCampaign[c].errors++;
  });
  respsF.forEach(r => {
    if (`${r.responded}`.toLowerCase() === 'true') {
      const c = r.campaign || 'NA';
      byCampaign[c] = byCampaign[c] || { sent: 0, responded: 0, errors: 0 };
      byCampaign[c].responded++;
    }
  });
  const campaigns = Object.entries(byCampaign).map(([campaign, d]) => ({
    campaign,
    sent: d.sent,
    responded: d.responded,
    errors: d.errors,
    rate: d.sent ? (d.responded / d.sent) * 100 : 0,
    errRate: d.sent ? (d.errors / d.sent) * 100 : 0
  })).sort((a,b) => b.rate - a.rate);

  return { sent, responded, errors, rate, errRate, campaigns };
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { fromDate, toDate, json, md, outPath } = parseCliFlags();
  const sends = readCsv(path.resolve(root, 'Logs', 'dm_send_log.csv')).rows;
  const resps = readCsv(path.resolve(root, 'Logs', 'dm_responses.csv')).rows;
  const kpis = computeKpis(sends, resps, fromDate, toDate);

  if (json && !md) {
    console.log(JSON.stringify({ range: { from: fromDate, to: toDate }, ...kpis }));
    return;
  }

  const lines = [];
  lines.push(`# 📈 KPI Snapshot`);
  lines.push(`Rango: ${fromDate ? fromDate.toISOString().slice(0,10) : 'inicio'} → ${toDate ? toDate.toISOString().slice(0,10) : 'hoy'}`);
  lines.push('');
  lines.push(`- Envíos: ${kpis.sent}`);
  lines.push(`- Respuestas: ${kpis.responded} (${kpis.rate.toFixed(2)}%)`);
  lines.push(`- Errores: ${kpis.errors} (${kpis.errRate.toFixed(2)}%)`);
  lines.push('');
  lines.push('## Campañas (top 5 por tasa)');
  kpis.campaigns.slice(0,5).forEach(c => lines.push(`- ${c.campaign}: ${c.rate.toFixed(2)}% (sent ${c.sent}, resp ${c.responded}, err ${c.errRate.toFixed(2)}%)`));

  if (outPath) {
    const outAbs = path.resolve(root, outPath);
    ensureDir(path.dirname(outAbs));
    fs.writeFileSync(outAbs, lines.join('\n') + '\n', 'utf8');
    console.log(`Snapshot guardado en: ${path.relative(root, outAbs)}`);
  } else {
    console.log(lines.join('\n'));
  }
}

main();



#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, parseCliFlags } = require('./utils_fs');
const { notify } = require('./utils_notify');

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
      headers.forEach((h, i) => (obj[h] = (cols[i] || '').replace(/^"|"$/g, '').trim());
      return obj;
    });
    return { headers, rows };
  } catch (_) {
    return { headers: [], rows: [] };
  }
}

function inLastDays(ts, days) {
  const d = new Date(ts);
  if (isNaN(d)) return false;
  const now = Date.now();
  return now - d.getTime() <= days*24*60*60*1000;
}

function pct(n, d) { return d>0 ? (n/d*100) : 0; }

function main() {
  const root = path.resolve(__dirname, '..');
  const { outPath, noNotify } = parseCliFlags();
  const sends = readCsv(path.resolve(root, 'Logs', 'dm_send_log.csv')).rows;
  const resps = readCsv(path.resolve(root, 'Logs', 'dm_responses.csv')).rows;

  const sends7 = sends.filter(r => inLastDays(r.timestamp, 7));
  const respsSet = new Set(resps.filter(r => `${r.responded}`.toLowerCase()==='true').map(r => r.recipient));

  const sent = sends7.length;
  const responded = sends7.filter(s => respsSet.has(s.recipient)).length;
  const errors = sends7.filter(s => (s.status||'').toUpperCase()==='ERROR').length;
  const rate = pct(responded, sent);
  const errRate = pct(errors, sent);

  const byVariant = {};
  sends7.forEach(s => { const v = s.variant || 'NA'; byVariant[v]=(byVariant[v]||{sent:0,resp:0}); byVariant[v].sent++; if (respsSet.has(s.recipient)) byVariant[v].resp++; });
  const topVariants = Object.entries(byVariant).map(([v,d])=>({v, sent:d.sent, rate:pct(d.resp,d.sent)})).sort((a,b)=>b.rate-a.rate).slice(0,5);

  const byHour = {};
  sends7.forEach(s => { const d = new Date(s.timestamp); if (isNaN(d)) return; const h=d.getHours(); byHour[h]=(byHour[h]||{sent:0,resp:0}); byHour[h].sent++; if (respsSet.has(s.recipient)) byHour[h].resp++; });
  const bestHours = Object.entries(byHour).map(([h,d])=>({h:Number(h), sent:d.sent, rate:pct(d.resp,d.sent)})).sort((a,b)=>b.rate-a.rate).slice(0,5);

  const reportsDir = path.resolve(root, '01_Marketing', 'Reports');
  ensureDir(reportsDir);
  const outFile = path.resolve(root, outPath || path.join('01_Marketing','Reports', `weekly_report_${new Date().toISOString().slice(0,10)}.md`));

  const md = [];
  md.push(`# 📅 Weekly Report (últimos 7 días)`);
  md.push('');
  md.push(`- Envíos: ${sent}`);
  md.push(`- Respuestas: ${responded} (${rate.toFixed(2)}%)`);
  md.push(`- Errores: ${errors} (${errRate.toFixed(2)}%)`);
  md.push('');
  md.push('## Top variantes');
  topVariants.forEach(t => md.push(`- ${t.v}: ${t.rate.toFixed(2)}% (sent ${t.sent})`));
  md.push('');
  md.push('## Mejores horas');
  bestHours.forEach(b => md.push(`- ${b.h}:00 → ${b.rate.toFixed(2)}% (sent ${b.sent})`));
  md.push('');
  md.push('## Recomendaciones');
  if (topVariants[0]) md.push(`- Aumentar peso de ${topVariants[0].v}`);
  if (bestHours[0]) md.push(`- Priorizar ${bestHours[0].h}:00`);
  if (errRate > 5) md.push(`- Revisar errores (>5%): ${errRate.toFixed(2)}%`);

  fs.writeFileSync(outFile, md.join('\n') + '\n', 'utf8');
  const rel = path.relative(root, outFile);
  console.log(`Weekly report guardado: ${rel}`);
  if (!noNotify) notify(`Weekly DM report generado: ${rel}`);
}

main();



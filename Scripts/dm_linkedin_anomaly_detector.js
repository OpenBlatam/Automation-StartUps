#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { notify } = require('./utils_notify');
const { fileExists, parseCliFlags } = require('./utils_fs');

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

function dailyRates(logs, resps) {
  const byDay = {};
  logs.forEach(l => {
    const d = new Date(l.timestamp || Date.now());
    if (isNaN(d)) return;
    const day = d.toISOString().slice(0,10);
    byDay[day] = byDay[day] || { sent: 0, responded: 0 };
    byDay[day].sent++;
  });
  const respondedSet = new Set(
    resps.filter(r => `${r.responded}`.toLowerCase()==='true').map(r => r.recipient)
  );
  logs.forEach(l => {
    const d = new Date(l.timestamp || Date.now());
    if (isNaN(d)) return;
    const day = d.toISOString().slice(0,10);
    if (respondedSet.has(l.recipient)) {
      byDay[day] = byDay[day] || { sent: 0, responded: 0 };
      byDay[day].responded++;
    }
  });
  return Object.entries(byDay)
    .map(([day, d]) => ({ day, sent: d.sent, responded: d.responded, rate: d.sent? (d.responded/d.sent)*100 : 0 }))
    .sort((a,b) => a.day.localeCompare(b.day));
}

function zScore(values, currentIdx) {
  const slice = values.slice(0, currentIdx); // history before current
  if (slice.length < 7) return { z: 0, mean: 0, std: 0 };
  const mean = slice.reduce((a,b)=>a+b,0)/slice.length;
  const variance = slice.reduce((a,b)=>a+(b-mean)*(b-mean),0)/slice.length;
  const std = Math.sqrt(variance);
  const z = std>0 ? (values[currentIdx]-mean)/std : 0;
  return { z, mean, std };
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { silent, noNotify } = parseCliFlags();
  const sendPath = path.resolve(root, 'Logs', 'dm_send_log.csv');
  const respPath = path.resolve(root, 'Logs', 'dm_responses.csv');
  if (!fileExists(sendPath) || !fileExists(respPath)) {
    console.log('Faltan logs. Ejecuta dm:setup o revisa rutas.');
    process.exit(0);
  }

  const sends = readCsv(sendPath).rows;
  const resps = readCsv(respPath).rows;
  const series = dailyRates(sends, resps);
  if (!series.length) {
    console.log('Sin datos para analizar.');
    return;
  }
  const rates = series.map(d => d.rate);
  const lastIdx = series.length - 1;
  const { z, mean, std } = zScore(rates, lastIdx);
  const last = series[lastIdx];
  const msg = `Anomaly check ${last.day}: rate ${last.rate.toFixed(2)}% (z=${z.toFixed(2)}, mean=${mean.toFixed(2)}, std=${std.toFixed(2)})`;
  console.log(msg);
  if (!noNotify && (z <= -2.5 || z >= 3)) {
    notify(`ALERTA: Anomalía en tasa diaria ${last.day}: ${last.rate.toFixed(2)}% (z=${z.toFixed(2)})`);
  }
}

main();



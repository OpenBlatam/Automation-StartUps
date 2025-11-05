#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { parseCliFlags, ensureDir } = require('./utils_fs');

function readCsv(absPath) {
  try {
    if (!fs.existsSync(absPath)) return { headers: [], rows: [] };
    const raw = fs.readFileSync(absPath, 'utf8');
    const lines = raw.split(/\r?\n/).filter(Boolean);
    if (!lines.length) return { headers: [], rows: [] };
    const headers = lines[0].split(',').map(s => s.trim());
    const rows = lines.slice(1).map(l => {
      const cols = l.match(/\"[^\"]*\"|[^,]+/g) || [];
      const obj = {};
      headers.forEach((h, i) => (obj[h] = ((cols[i] || '').replace(/^\"|\"$/g, '')).trim()));
      return obj;
    });
    return { headers, rows };
  } catch (_) {
    return { headers: [], rows: [] };
  }
}

function writeCsv(absPath, headers, rows) {
  const headerLine = headers.join(',');
  const body = rows.map(r => headers.map(h => {
    const v = r[h] || '';
    return /[,\n\"]/.test(v) ? `"${v.replace(/\"/g,'"')}"` : v;
  }).join(',')).join('\n');
  ensureDir(path.dirname(absPath));
  fs.writeFileSync(absPath, headerLine + '\n' + body + (body ? '\n' : ''), 'utf8');
}

function daysSince(ts) {
  const d = new Date(ts);
  if (isNaN(d)) return Infinity;
  return (Date.now() - d.getTime()) / (24*60*60*1000);
}

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const minDaysArg = args.find(a => a.startsWith('--min-days='));
  const minDays = minDaysArg ? Number(minDaysArg.split('=')[1]) : Number(process.env.COOLDOWN_MIN_DAYS || '7');
  const { inPath, outPath } = parseCliFlags();

  const queuePath = path.resolve(root, inPath || '01_Marketing/Send_Queue.csv');
  const sendLogPath = path.resolve(root, 'Logs', 'dm_send_log.csv');
  const q = readCsv(queuePath);
  const logs = readCsv(sendLogPath).rows;
  if (!q.headers.length) { console.log('No se pudo leer Send_Queue.csv'); process.exit(1); }

  const lastSent = new Map();
  logs.forEach(l => {
    const key = `${l.recipient}||${l.campaign||'NA'}`;
    const ts = l.timestamp;
    if (!lastSent.has(key) || new Date(ts) > new Date(lastSent.get(key))) {
      lastSent.set(key, ts);
    }
  });

  const kept = [];
  const dropped = [];
  q.rows.forEach(r => {
    const key = `${r.recipient}||${r.campaign||'NA'}`;
    const ts = lastSent.get(key);
    if (!ts || daysSince(ts) >= minDays) kept.push(r);
    else dropped.push(Object.assign({}, r, { last_sent_at: ts }));
  });

  const outFile = path.resolve(root, outPath || '01_Marketing/Send_Queue_Cooldown.csv');
  writeCsv(outFile, q.headers, kept);
  console.log(`Cooldown guard: mantenidos=${kept.length}, removidos=${dropped.length}, minDays=${minDays}`);
  console.log(`Cola filtrada: ${path.relative(root, outFile)}`);
}

main();



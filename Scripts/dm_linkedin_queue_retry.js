#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, parseCliFlags } = require('./utils_fs');

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

function daysAgo(ts) {
  const d = new Date(ts);
  if (isNaN(d)) return Infinity;
  return (Date.now() - d.getTime()) / (24*60*60*1000);
}

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const ageArg = args.find(a => a.startsWith('--age='));
  const minAgeDays = ageArg ? Number(ageArg.split('=')[1]) : Number(process.env.RETRY_MIN_AGE_DAYS || '7');
  const maxAttempts = Number(process.env.RETRY_MAX_ATTEMPTS || '2');
  const { outPath } = parseCliFlags();

  const sends = readCsv(path.resolve(root, 'Logs', 'dm_send_log.csv')).rows;
  const resps = readCsv(path.resolve(root, 'Logs', 'dm_responses.csv')).rows;
  const responded = new Set(resps.filter(r => `${r.responded}`.toLowerCase()==='true').map(r => r.recipient));

  // Count attempts per recipient+campaign
  const attempts = new Map();
  sends.forEach(s => {
    const key = `${s.recipient}||${s.campaign||'NA'}`;
    attempts.set(key, (attempts.get(key)||0) + 1);
  });

  // Build retry set: errors or aged no-response, under attempt cap
  const retry = new Map();
  sends.forEach(s => {
    const recipient = s.recipient;
    const campaign = s.campaign || 'NA';
    const key = `${recipient}||${campaign}`;
    if (!recipient) return;
    const alreadyResponded = responded.has(recipient);
    const attemptsCount = attempts.get(key) || 0;
    if (attemptsCount >= maxAttempts) return;
    const isError = (s.status||'').toUpperCase()==='ERROR';
    const isOld = daysAgo(s.timestamp) >= minAgeDays;
    if ((isError || isOld) && !alreadyResponded) {
      // Prefer latest variant sent for continuity
      const cur = retry.get(key);
      if (!cur || new Date(s.timestamp) > new Date(cur.timestamp||0)) {
        retry.set(key, { recipient, campaign, variant: s.variant || 'V1', timestamp: s.timestamp });
      }
    }
  });

  const rows = Array.from(retry.values()).map(r => ({ recipient: r.recipient, variant: r.variant, campaign: r.campaign }));
  const headers = ['recipient','variant','campaign'];
  const out = path.resolve(root, outPath || '01_Marketing/Send_Queue_Retry.csv');
  writeCsv(out, headers, rows);
  console.log(`Retry queue generada: ${path.relative(root, out)} (total ${rows.length}) | minAgeDays=${minAgeDays} maxAttempts=${maxAttempts}`);
}

main();



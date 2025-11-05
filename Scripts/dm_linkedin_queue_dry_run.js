#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, parseCliFlags, fileExists } = require('./utils_fs');
const { notify } = require('./utils_notify');

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

function appendSendLog(fp, rows) {
  const exists = fileExists(fp);
  if (!exists) fs.writeFileSync(fp, 'timestamp,recipient,variant,campaign,status,error\n', 'utf8');
  const lines = rows.map(r => `${r.timestamp},"${r.recipient}","${r.variant}","${r.campaign}",${r.status},${r.error||''}`);
  fs.appendFileSync(fp, lines.join('\n') + '\n', 'utf8');
}

function normalizeProfile(url) { return (url || '').toLowerCase().replace(/\/$/, ''); }

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const rateArg = args.find(a => a.startsWith('--rate=')); // messages per minute
  const rate = rateArg ? Number(rateArg.split('=')[1]) : Number(process.env.DRYRUN_RATE || '30');
  const errorP = Number(process.env.DRYRUN_ERROR_RATE || '0.03');
  const { inPath, noNotify } = parseCliFlags();

  const queuePath = path.resolve(root, inPath || '01_Marketing/Send_Queue.csv');
  const queue = readCsv(queuePath);
  if (!queue.headers.length) {
    console.log('No se pudo leer Send_Queue.csv');
    process.exit(1);
  }

  const profSupPath = path.resolve(root, '01_Marketing', 'dm_linkedin_suppression_list.csv');
  const profileSupp = readCsv(profSupPath).rows.map(r => normalizeProfile(r.profile||r.recipient||r.url)).filter(Boolean);
  const supSet = new Set(profileSupp);

  const logsDir = path.resolve(root, 'Logs');
  ensureDir(logsDir);
  const sendLog = path.resolve(logsDir, 'dm_send_log.csv');

  const delayMs = Math.max(1000, Math.floor(60000 / Math.max(1, rate)));
  let sent = 0; let skipped = 0; let errors = 0;
  const toLog = [];

  queue.rows.forEach((q, idx) => {
    const recipient = q.recipient || '';
    if (!recipient || supSet.has(normalizeProfile(recipient))) { skipped++; return; }
    const ts = new Date(Date.now() + idx * delayMs).toISOString();
    const isErr = Math.random() < errorP;
    const status = isErr ? 'ERROR' : 'SENT';
    const error = isErr ? 'simulated_error' : '';
    if (isErr) errors++; else sent++;
    toLog.push({ timestamp: ts, recipient, variant: q.variant || '', campaign: q.campaign || 'general', status, error });
  });

  appendSendLog(sendLog, toLog);
  console.log(`Dry-run: enviados=${sent}, errores=${errors}, omitidos(suppress)=${skipped}, rate=${rate}/min, log=${path.relative(root, sendLog)}`);
  if (!noNotify) notify(`Dry-run completado: sent ${sent}, errors ${errors}, skipped ${skipped}`);
}

main();



#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, fileExists } = require('./utils_fs');

const root = path.resolve(__dirname, '..');
const logsDir = path.resolve(root, 'Logs');
const sendLog = path.resolve(logsDir, 'dm_send_log.csv');
const respLog = path.resolve(logsDir, 'dm_responses.csv');

function readAll(fp) {
  try { return fs.readFileSync(fp, 'utf8'); } catch { return ''; }
}

function headerOf(content) {
  return (content.split(/\r?\n/).find(Boolean) || '').trim();
}

function main() {
  ensureDir(logsDir);
  const now = new Date();
  const yyyymm = `${now.getFullYear()}${String(now.getMonth()+1).padStart(2,'0')}`;
  const archiveDir = path.resolve(root, 'Archives', yyyymm);
  ensureDir(archiveDir);

  const files = [
    { src: sendLog, name: `dm_send_log_${yyyymm}.csv` },
    { src: respLog, name: `dm_responses_${yyyymm}.csv` }
  ];

  files.forEach(f => {
    if (!fileExists(f.src)) return;
    const content = readAll(f.src);
    const out = path.resolve(archiveDir, f.name);
    fs.writeFileSync(out, content, 'utf8');
    const hdr = headerOf(content) || (f.src.includes('send') ? 'timestamp,recipient,variant,campaign,status,error' : 'recipient,variant,responded,clicked,converted');
    fs.writeFileSync(f.src, hdr + '\n', 'utf8');
    console.log(`Archivado y reiniciado: ${path.relative(root, f.src)} -> ${path.relative(root, out)}`);
  });

  console.log('Archivado completo.');
}

main();



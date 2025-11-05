#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { parseCliFlags } = require('./utils_fs');

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

function isLinkedinUrl(u) {
  return /^https?:\/\/([a-z]+\.)?linkedin\.com\//i.test(u || '');
}

function validIsoFuture(s) {
  if (!s) return true; // optional
  const d = new Date(s);
  return !isNaN(d) && d > new Date(Date.now() - 60*1000);
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { inPath, json } = parseCliFlags();
  const file = path.resolve(root, inPath || '01_Marketing/Send_Queue.csv');
  const csv = readCsv(file);
  if (!csv.headers.length) {
    console.log('No se pudo leer Send_Queue.csv');
    process.exit(1);
  }

  const hasSendAt = csv.headers.includes('send_at');
  const variants = new Set(
    (readCsv(path.resolve(root, 'DM_Variants_Short.csv')).rows || [])
      .map(r => r.variant)
      .filter(Boolean)
  );

  const problems = [];
  const seen = new Set();
  csv.rows.forEach((r, i) => {
    const idx = i + 1;
    const recipient = r.recipient || '';
    const variant = r.variant || '';
    const campaign = r.campaign || '';
    const sendAt = r.send_at || '';
    if (!recipient) problems.push({ idx, reason: 'recipient vacío' });
    else if (!isLinkedinUrl(recipient)) problems.push({ idx, reason: 'recipient no es URL de LinkedIn' });
    if (!variant) problems.push({ idx, reason: 'variant vacío' });
    else if (!variants.has(variant)) problems.push({ idx, reason: `variant no definido: ${variant}` });
    if (!campaign) problems.push({ idx, reason: 'campaign vacío' });
    if (hasSendAt && !validIsoFuture(sendAt)) problems.push({ idx, reason: `send_at inválido/pasado: ${sendAt}` });
    const key = `${recipient}||${campaign}`;
    if (seen.has(key)) problems.push({ idx, reason: 'duplicado recipient+campaign' });
    seen.add(key);
  });

  const summary = { file: path.relative(root, file), rows: csv.rows.length, problems: problems.length };
  if (json) {
    console.log(JSON.stringify({ summary, problems }));
  } else {
    console.log(`# ✅ Queue Validator`);
    console.log(`Archivo: ${summary.file}`);
    console.log(`Filas: ${summary.rows} | Problemas: ${summary.problems}`);
    if (problems.length) {
      problems.slice(0, 200).forEach(p => console.log(`- [${p.idx}] ${p.reason}`));
      if (problems.length > 200) console.log(`... y ${problems.length - 200} más`);
    } else {
      console.log('Sin problemas.');
    }
  }
  process.exit(problems.length ? 1 : 0);
}

main();



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

function pad(n, w) { return String(n).padStart(w, '0'); }

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const sizeArg = args.find(a => a.startsWith('--size='));
  const size = sizeArg ? Math.max(1, Number(sizeArg.split('=')[1])) : Math.max(1, Number(process.env.QUEUE_CHUNK_SIZE || '200'));
  const byCampaign = args.includes('--by-campaign');
  const prefixArg = args.find(a => a.startsWith('--prefix='));
  const prefix = prefixArg ? prefixArg.split('=')[1] : 'Send_Queue_part_';
  const { inPath, outPath } = parseCliFlags();

  const inFile = path.resolve(root, inPath || '01_Marketing/Send_Queue.csv');
  const outDir = outPath ? path.resolve(root, outPath) : path.resolve(root, '01_Marketing');
  const csv = readCsv(inFile);
  if (!csv.headers.length) {
    console.log('No se pudo leer Send_Queue.csv');
    process.exit(1);
  }

  const groups = byCampaign ? csv.rows.reduce((acc, r) => {
    const c = r.campaign || 'NA';
    acc[c] = acc[c] || [];
    acc[c].push(r);
    return acc;
  }, {}) : { ALL: csv.rows };

  let files = [];
  Object.entries(groups).forEach(([key, rows]) => {
    for (let i = 0; i < rows.length; i += size) {
      const chunk = rows.slice(i, i + size);
      const name = byCampaign ? `${prefix}${key}_${pad(i/size+1,3)}.csv` : `${prefix}${pad(i/size+1,3)}.csv`;
      const outFile = path.join(outDir, name);
      writeCsv(outFile, csv.headers, chunk);
      files.push(path.relative(root, outFile));
    }
  });

  console.log(`Chunks creados (${files.length}):`);
  files.forEach(f => console.log('- ' + f));
}

main();



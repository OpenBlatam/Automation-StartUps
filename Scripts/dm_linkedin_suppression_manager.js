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
      const cols = l.match(/\"[^\"]*\"|[^,]+/g) || []; // basic CSV split preserving quotes
      const obj = {};
      headers.forEach((h, i) => (obj[h] = ((cols[i] || '').replace(/^\"|\"$/g, '')).trim()));
      return obj;
    });
    return { headers, rows, headerLine: lines[0] };
  } catch (_) {
    return { headers: [], rows: [], headerLine: '' };
  }
}

function writeCsv(absPath, headerLine, rows) {
  const body = rows.map(r => Object.values(r).map(v => /[,\n\"]/.test(v||'') ? `"${(v||'').replace(/\"/g,'"')}"` : (v||'')).join(',')).join('\n');
  fs.writeFileSync(absPath, headerLine + '\n' + body + (body ? '\n' : ''), 'utf8');
}

function normalizeProfile(url) {
  return (url || '').toLowerCase().replace(/\/$/, '');
}
function normalizeCompany(name) {
  return (name || '').toLowerCase().trim();
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { inPath, outPath, json } = parseCliFlags();
  const recipientsPath = path.resolve(root, inPath || '01_Marketing/Recipients.csv');
  const outFile = path.resolve(root, outPath || '01_Marketing/Recipients_clean.csv');
  const profileSuppressPath = path.resolve(root, '01_Marketing', 'dm_linkedin_suppression_list.csv');
  const companySuppressPath = path.resolve(root, '01_Marketing', 'dm_linkedin_company_suppression.csv');

  const rec = readCsv(recipientsPath);
  if (!rec.headers.length) {
    console.log('No se pudo leer Recipients.csv.');
    process.exit(1);
  }
  const profSup = readCsv(profileSuppressPath).rows.map(r => normalizeProfile(r.profile || r.recipient || r.url));
  const compSup = readCsv(companySuppressPath).rows.map(r => normalizeCompany(r.company || r.empresa || r.name));
  const profSet = new Set(profSup.filter(Boolean));
  const compSet = new Set(compSup.filter(Boolean));

  const seenRecipients = new Set();
  let kept = [];
  let droppedDuplicate = 0;
  let droppedProfile = 0;
  let droppedCompany = 0;

  rec.rows.forEach(row => {
    const recipient = normalizeProfile(row.recipient || row.profile || row.url);
    const company = normalizeCompany(row.company || row.empresa || row.account || '');
    if (!recipient) return; // skip empty
    if (seenRecipients.has(recipient)) { droppedDuplicate++; return; }
    if (profSet.has(recipient)) { droppedProfile++; return; }
    if (company && compSet.has(company)) { droppedCompany++; return; }
    seenRecipients.add(recipient);
    kept.push(row);
  });

  ensureDir(path.dirname(outFile));
  writeCsv(outFile, rec.headerLine, kept);

  const summary = {
    input: path.relative(root, recipientsPath),
    output: path.relative(root, outFile),
    totalIn: rec.rows.length,
    totalOut: kept.length,
    removed: {
      duplicates: droppedDuplicate,
      profileSuppressed: droppedProfile,
      companySuppressed: droppedCompany
    }
  };

  if (json) console.log(JSON.stringify(summary));
  else {
    console.log('— Suppression Manager —');
    console.log(`Archivo entrada: ${summary.input}`);
    console.log(`Archivo salida:  ${summary.output}`);
    console.log(`Entradas: ${summary.totalIn} -> Salidas: ${summary.totalOut}`);
    console.log(`Removidos: duplicados=${droppedDuplicate}, perfiles=${droppedProfile}, empresas=${droppedCompany}`);
  }
}

main();



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
    return { headers, rows, headerLine: lines[0] };
  } catch (_) {
    return { headers: [], rows: [], headerLine: '' };
  }
}

function appendCsv(absPath, headers, rows) {
  ensureDir(path.dirname(absPath));
  if (!fs.existsSync(absPath)) fs.writeFileSync(absPath, headers.join(',') + '\n', 'utf8');
  const line = (v) => (/[,\n\"]/.test(v||'') ? `"${(v||'').replace(/\"/g,'"')}"` : (v||''));
  const body = rows.map(r => headers.map(h => line(r[h])).join(',')).join('\n');
  if (body) fs.appendFileSync(absPath, body + '\n', 'utf8');
}

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const phrasesEnv = process.env.OPTOUT_PHRASES || 'STOP|BAJA|NO CONTACTAR|NO ME ESCRIBAS|UNSUBSCRIBE|REMOVE|ELIMINARME|NO MÁS|NO MORE';
  const rx = new RegExp(phrasesEnv, 'i');
  const { inPath } = parseCliFlags();

  const responsesPath = path.resolve(root, inPath || 'Logs/dm_responses.csv');
  const resp = readCsv(responsesPath);
  if (!resp.headers.length) { console.log('No se pudo leer dm_responses.csv'); process.exit(1); }

  const outProf = path.resolve(root, '01_Marketing', 'dm_linkedin_suppression_list.csv');
  const outCompany = path.resolve(root, '01_Marketing', 'dm_linkedin_company_suppression.csv');

  const profHeaders = ['profile'];
  const compHeaders = ['company'];
  const profNew = [];
  const compNew = [];

  resp.rows.forEach(r => {
    const text = (r.text || r.message || r.body || '').toUpperCase();
    const recipient = r.recipient || '';
    const company = r.company || r.empresa || '';
    if (!recipient) return;
    if (rx.test(text)) {
      profNew.push({ profile: recipient });
      if (company) compNew.push({ company });
    }
  });

  appendCsv(outProf, profHeaders, profNew);
  appendCsv(outCompany, compHeaders, compNew);
  console.log(`Opt-out: añadidos perfiles=${profNew.length}, empresas=${compNew.length}`);
}

main();



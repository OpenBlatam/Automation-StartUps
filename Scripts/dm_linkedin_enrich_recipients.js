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

function slugFromUrl(u) {
  try {
    if (!u) return '';
    const m = u.match(/linkedin\.com\/in\/([^\/?#]+)/i);
    return m ? m[1].toLowerCase() : '';
  } catch { return ''; }
}
function companySlug(name) {
  return (name || '').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/(^-|-$)/g,'');
}
function guessLocale(country) {
  const v = (country || '').toLowerCase();
  if (!v) return '';
  if (/(mex|méx|mx)/.test(v)) return 'es-MX';
  if (/(espa|spain|es)/.test(v)) return 'es-ES';
  if (/(usa|united states|us|eeuu)/.test(v)) return 'en-US';
  return '';
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { inPath, outPath } = parseCliFlags();
  const file = path.resolve(root, inPath || '01_Marketing/Recipients_clean.csv');
  const out = path.resolve(root, outPath || '01_Marketing/Recipients_enriched.csv');
  const csv = readCsv(file);
  if (!csv.headers.length) {
    console.log('No se pudo leer Recipients_clean.csv');
    process.exit(1);
  }
  const headers = Array.from(new Set([...csv.headers, 'li_slug', 'company_slug', 'locale']))
    .filter(Boolean);
  const rows = csv.rows.map(r => {
    const li = r.recipient || r.profile || r.url || '';
    const comp = r.company || r.empresa || '';
    const country = r.country || r.pais || r.region || '';
    return Object.assign({}, r, {
      li_slug: slugFromUrl(li),
      company_slug: companySlug(comp),
      locale: guessLocale(country)
    });
  });
  writeCsv(out, headers, rows);
  console.log(`Recipients enriched: ${path.relative(root, out)} (filas ${rows.length})`);
}

main();



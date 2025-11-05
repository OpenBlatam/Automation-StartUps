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

const RULES = {
  maxChars: Number(process.env.LINT_MAX_CHARS || '300'),
  requireOptOut: process.env.LINT_REQUIRE_OPTOUT !== '0',
  optOutTokens: (process.env.LINT_OPTOUT_TOKENS || 'STOP,BAJA,No volver a escribir,Opt-out').split('|'),
  riskyPatterns: [
    /garantiz(a|o)/i,
    /sin\s*rieg?o/i,
    /millones?\s*en\s*días?/i,
    /100%\s*asegurado/i
  ],
  placeholderPattern: /\[(Nombre|Empresa|Rol|Industria|Objetivo|Stack|Volumen)\]/
};

function lintMessage(text) {
  const issues = [];
  if (!text) {
    issues.push('vacío');
    return issues;
  }
  if (text.length > RULES.maxChars) issues.push(`excede ${RULES.maxChars} chars (${text.length})`);
  if (RULES.requireOptOut && !RULES.optOutTokens.some(t => text.includes(t))) issues.push('sin opt-out');
  if (RULES.placeholderPattern.test(text)) issues.push('placeholders sin resolver');
  RULES.riskyPatterns.forEach(rx => { if (rx.test(text)) issues.push(`claim riesgoso: ${rx.source}`); });
  return issues;
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { json, md, inPath } = parseCliFlags();
  const file = path.resolve(root, inPath || 'DM_Variants_Short.csv');
  const csv = readCsv(file);
  if (!csv.headers.length) {
    console.log('No se pudo leer el CSV de variantes.');
    process.exit(1);
  }
  const textCols = ['text','message','dm','content'];
  const col = csv.headers.find(h => textCols.includes(h.toLowerCase())) || csv.headers[1] || csv.headers[0];
  const results = csv.rows.map((r, i) => ({ idx: i+1, variant: r.variant || r.key || '', issues: lintMessage(r[col]) }));
  const violations = results.filter(r => r.issues.length);
  const summary = { file: path.relative(root, file), total: results.length, violations: violations.length, maxChars: RULES.maxChars };

  if (json && !md) {
    console.log(JSON.stringify({ summary, violations }));
  } else {
    const lines = [];
    lines.push('# 🧪 Linter de Mensajes DM');
    lines.push(`Archivo: ${summary.file}`);
    lines.push(`Total: ${summary.total} | Violaciones: ${summary.violations} | Max chars: ${summary.maxChars}`);
    lines.push('');
    if (!violations.length) {
      lines.push('Sin problemas detectados.');
    } else {
      lines.push('## Violaciones');
      violations.slice(0, 200).forEach(v => lines.push(`- [${v.idx}] ${v.variant}: ${v.issues.join('; ')}`));
      if (violations.length > 200) lines.push(`... y ${violations.length - 200} más`);
    }
    console.log(lines.join('\n'));
  }
  process.exit(violations.length ? 1 : 0);
}

main();



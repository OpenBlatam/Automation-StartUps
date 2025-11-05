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
      const cols = l.split(',');
      const obj = {};
      headers.forEach((h, i) => (obj[h] = (cols[i] || '').replace(/^"|"$/g, '').trim()));
      return obj;
    });
    return { headers, rows };
  } catch (_) {
    return { headers: [], rows: [] };
  }
}

function readJson(absPath) {
  try { return JSON.parse(fs.readFileSync(absPath, 'utf8')); } catch (_) { return null; }
}

function main() {
  const root = path.resolve(__dirname, '..');
  const { json, md, outPath } = parseCliFlags();

  const logs = readCsv(path.resolve(root, 'Logs', 'dm_send_log.csv')).rows;
  const variantsCsv = readCsv(path.resolve(root, 'dm_variants_master.csv')).rows;
  const variantsShortCsv = readCsv(path.resolve(root, 'DM_Variants_Short.csv')).rows;
  const variantsJson = readJson(path.resolve(root, '01_Marketing', 'dm_linkedin_variants_localized_completo.json'));

  const definedVariants = new Set();
  variantsCsv.forEach(r => Object.values(r).forEach(v => { if (typeof v === 'string' && v.startsWith('V')) definedVariants.add(v); }));
  variantsShortCsv.forEach(r => { if (r.variant) definedVariants.add(r.variant); });
  if (variantsJson && Array.isArray(variantsJson.variants)) {
    variantsJson.variants.forEach(v => { if (v.key) definedVariants.add(v.key); });
  }

  const usedVariants = new Set(logs.map(l => l.variant).filter(Boolean));
  const usedCampaigns = new Set(logs.map(l => l.campaign).filter(Boolean));

  const unknownVariants = Array.from(usedVariants).filter(v => !definedVariants.has(v));
  const unusedVariants = Array.from(definedVariants).filter(v => !usedVariants.has(v));

  const byCampaign = {};
  logs.forEach(l => {
    const c = l.campaign || 'NA';
    byCampaign[c] = byCampaign[c] || 0;
    byCampaign[c]++;
  });

  const result = {
    totals: {
      logs: logs.length,
      definedVariants: definedVariants.size,
      usedVariants: usedVariants.size,
      campaigns: usedCampaigns.size
    },
    unknownVariants,
    unusedVariants: unusedVariants.slice(0, 100),
    topCampaigns: Object.entries(byCampaign).map(([c, n]) => ({ campaign: c, sends: n })).sort((a,b)=>b.sends-a.sends).slice(0, 10)
  };

  if (json && !md) {
    console.log(JSON.stringify(result));
    return;
  }

  const lines = [];
  lines.push('# 🔍 Consistency Check');
  lines.push(`- Logs: ${result.totals.logs}`);
  lines.push(`- Variantes definidas: ${result.totals.definedVariants}`);
  lines.push(`- Variantes usadas: ${result.totals.usedVariants}`);
  lines.push(`- Campañas: ${result.totals.campaigns}`);
  lines.push('');
  lines.push('## Variantes desconocidas (en Logs pero no definidas)');
  lines.push(result.unknownVariants.length ? result.unknownVariants.map(v=>`- ${v}`).join('\n') : '- Ninguna');
  lines.push('');
  lines.push('## Variantes definidas no usadas (top 100)');
  lines.push(result.unusedVariants.length ? result.unusedVariants.map(v=>`- ${v}`).join('\n') : '- Ninguna');
  lines.push('');
  lines.push('## Top 10 campañas por envíos');
  result.topCampaigns.forEach(c => lines.push(`- ${c.campaign}: ${c.sends}`));

  if (outPath) {
    const outAbs = path.resolve(root, outPath);
    ensureDir(path.dirname(outAbs));
    fs.writeFileSync(outAbs, lines.join('\n') + '\n', 'utf8');
    console.log(`Reporte guardado en: ${path.relative(root, outAbs)}`);
  } else {
    console.log(lines.join('\n'));
  }
}

main();



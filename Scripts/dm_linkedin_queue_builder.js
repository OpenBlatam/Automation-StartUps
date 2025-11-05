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

function pickVariant(row, variants) {
  if (!variants.length) return 'V1';
  // Simple weighted by company size/role if present; fallback random
  const role = (row.role || row.Rol || '').toLowerCase();
  const size = (row.size || row.company_size || '').toLowerCase();
  const filtered = variants.filter(v => {
    if (role.includes('ceo') && /SocialProof|Resultado/i.test(v)) return true;
    if (size.includes('enterprise') && /Value|Resultado/i.test(v)) return true;
    return false;
  });
  const list = filtered.length ? filtered : variants;
  return list[Math.floor(Math.random()*list.length)];
}

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const campaignArg = args.find(a => a.startsWith('--campaign='));
  const campaign = campaignArg ? campaignArg.split('=')[1] : (process.env.DEFAULT_CAMPAIGN || 'general');
  const limitArg = args.find(a => a.startsWith('--limit='));
  const limit = limitArg ? Number(limitArg.split('=')[1]) : undefined;
  const { inPath, outPath } = parseCliFlags();
  const schedule = args.includes('--schedule');
  const hoursArg = args.find(a => a.startsWith('--hours='));
  const hours = hoursArg ? hoursArg.split('=')[1].split(',').map(h=>Number(h)).filter(n=>!isNaN(n)) : undefined;
  const localeRoute = args.includes('--locale-route');
  const localePrefArg = args.find(a => a.startsWith('--locale='));
  const localePref = localePrefArg ? localePrefArg.split('=')[1] : '';
  const noWeekend = args.includes('--no-weekend');
  const blackoutArg = args.find(a => a.startsWith('--blackout='));
  const blackoutDays = new Set((blackoutArg ? blackoutArg.split('=')[1] : '')
    .split(',').map(s=>s.trim()).filter(Boolean));

  const recipientsFile = path.resolve(root, inPath || '01_Marketing/Recipients_clean.csv');
  const variantsShort = readCsv(path.resolve(root, 'DM_Variants_Short.csv')).rows;
  const variants = Array.from(new Set(variantsShort.map(r => r.variant).filter(Boolean)));

  function pickVariantByLocale(row, allVariants) {
    if (!localeRoute) return pickVariant(row, allVariants);
    const locale = (row.locale || localePref || '').toLowerCase();
    let suffix = '';
    if (locale.startsWith('es-')) suffix = '_ES';
    else if (locale.startsWith('en-')) suffix = '_EN';
    if (suffix) {
      const filtered = allVariants.filter(v => v.endsWith(suffix));
      if (filtered.length) return pickVariant(row, filtered);
    }
    return pickVariant(row, allVariants);
  }
  const rec = readCsv(recipientsFile);
  if (!rec.headers.length) {
    console.log('No se pudo leer Recipients_clean.csv');
    process.exit(1);
  }

  const queueHeaders = schedule ? ['recipient','variant','campaign','send_at'] : ['recipient','variant','campaign'];
  const rows = [];
  const input = limit ? rec.rows.slice(0, limit) : rec.rows;
  function isBlackoutDate(d) {
    const dayStr = d.toISOString().slice(0,10);
    if (blackoutDays.has(dayStr)) return true;
    if (noWeekend) {
      const wd = d.getDay();
      if (wd === 0 || wd === 6) return true;
    }
    return false;
  }

  function nextSendAt(preferredHours) {
    const now = new Date();
    const today = new Date(now);
    for (let dayOffset = 0; dayOffset < 7; dayOffset++) {
      const base = new Date(today.getFullYear(), today.getMonth(), today.getDate() + dayOffset);
      if (isBlackoutDate(base)) continue;
      for (const h of preferredHours) {
        const dt = new Date(base.getFullYear(), base.getMonth(), base.getDate(), h, 0, 0);
        if (dt > now) return dt.toISOString();
      }
    }
    return new Date(now.getTime() + 3600*1000).toISOString();
  }

  // Compute best hours from logs if needed
  let bestHours = hours;
  if (schedule && !bestHours) {
    const logs = readCsv(path.resolve(root, 'Logs', 'dm_send_log.csv')).rows;
    const resps = readCsv(path.resolve(root, 'Logs', 'dm_responses.csv')).rows;
    const respondedSet = new Set(resps.filter(r => `${r.responded}`.toLowerCase()==='true').map(r => r.recipient));
    const byHour = {};
    logs.forEach(s => {
      const d = new Date(s.timestamp);
      if (isNaN(d)) return;
      const h = d.getHours();
      byHour[h] = byHour[h] || { sent: 0, resp: 0 };
      byHour[h].sent++;
      if (respondedSet.has(s.recipient)) byHour[h].resp++;
    });
    bestHours = Object.entries(byHour)
      .map(([h,d]) => ({ h: Number(h), rate: d.sent? d.resp/d.sent : 0, sent: d.sent }))
      .filter(x => x.sent >= 10)
      .sort((a,b) => b.rate - a.rate)
      .slice(0,3)
      .map(x => x.h);
    if (!bestHours.length) bestHours = [9, 11, 14];
  }

  input.forEach(r => {
    const recipient = r.recipient || r.profile || r.url || '';
    if (!recipient) return;
    const row = { recipient, variant: pickVariantByLocale(r, variants), campaign };
    if (schedule) row.send_at = nextSendAt(bestHours);
    rows.push(row);
  });

  const outFile = path.resolve(root, outPath || '01_Marketing/Send_Queue.csv');
  writeCsv(outFile, queueHeaders, rows);
  console.log(`Queue generada: ${path.relative(root, outFile)} (total ${rows.length})`);
}

main();



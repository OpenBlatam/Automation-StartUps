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

function pct(n, d) { return d>0 ? (n/d*100) : 0; }

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const daysArg = args.find(a => a.startsWith('--days='));
  const days = daysArg ? Number(daysArg.split('=')[1]) : Number(process.env.GUARD_DAYS || '14');
  const minSends = Number(process.env.GUARD_MIN_SENDS || '50');
  const minResp = Number(process.env.GUARD_MIN_RESP_RATE || '2');
  const maxErr = Number(process.env.GUARD_MAX_ERR_RATE || '10');
  const apply = args.includes('--apply');
  const { noNotify } = parseCliFlags();

  const sendLog = path.resolve(root, 'Logs', 'dm_send_log.csv');
  const respLog = path.resolve(root, 'Logs', 'dm_responses.csv');
  if (!fileExists(sendLog)) { console.log('Falta Logs/dm_send_log.csv'); process.exit(1); }
  const sends = readCsv(sendLog).rows;
  const resps = readCsv(respLog).rows;

  const cutoff = Date.now() - days*24*60*60*1000;
  const recent = sends.filter(s => { const d=new Date(s.timestamp); return !isNaN(d) && d.getTime()>=cutoff; });
  const respSet = new Set(resps.filter(r => `${r.responded}`.toLowerCase()==='true').map(r => r.recipient));

  const byCampaign = {};
  const byVariant = {};
  recent.forEach(s => {
    const c = s.campaign || 'NA';
    const v = s.variant || 'NA';
    byCampaign[c] = byCampaign[c] || { sent: 0, resp: 0, err: 0 };
    byVariant[v] = byVariant[v] || { sent: 0, resp: 0, err: 0 };
    byCampaign[c].sent++; byVariant[v].sent++;
    if (respSet.has(s.recipient)) { byCampaign[c].resp++; byVariant[v].resp++; }
    if ((s.status||'').toUpperCase()==='ERROR') { byCampaign[c].err++; byVariant[v].err++; }
  });

  function assess(map) {
    return Object.entries(map).map(([key,d])=>({
      key,
      sent: d.sent,
      respRate: pct(d.resp,d.sent),
      errRate: pct(d.err,d.sent),
      pause: d.sent>=minSends && (pct(d.resp,d.sent)<minResp || pct(d.err,d.sent)>maxErr)
    })).sort((a,b)=>a.key.localeCompare(b.key));
  }

  const campaigns = assess(byCampaign);
  const variants = assess(byVariant);
  const pausedCampaigns = campaigns.filter(x=>x.pause).map(x=>x.key);
  const pausedVariants = variants.filter(x=>x.pause).map(x=>x.key);

  const reportsDir = path.resolve(root, '01_Marketing', 'Reports');
  ensureDir(reportsDir);
  const outCampaigns = path.resolve(reportsDir, 'paused_campaigns.json');
  const outVariants = path.resolve(reportsDir, 'paused_variants.json');
  fs.writeFileSync(outCampaigns, JSON.stringify({ days, minSends, minResp, maxErr, pausedCampaigns, campaigns }, null, 2), 'utf8');
  fs.writeFileSync(outVariants, JSON.stringify({ days, minSends, minResp, maxErr, pausedVariants, variants }, null, 2), 'utf8');
  console.log(`Guard reporte: ${path.relative(root, outCampaigns)}, ${path.relative(root, outVariants)}`);

  if (!noNotify && (pausedCampaigns.length || pausedVariants.length)) {
    notify(`GUARD: Pausar campañas=${pausedCampaigns.length}, variantes=${pausedVariants.length}`);
  }

  if (apply) {
    const queuePath = path.resolve(root, '01_Marketing', 'Send_Queue.csv');
    if (fileExists(queuePath)) {
      const q = readCsv(queuePath);
      const kept = q.rows.filter(r => !pausedCampaigns.includes(r.campaign) && !pausedVariants.includes(r.variant));
      const headerLine = q.headers.join(',');
      const body = kept.map(r => q.headers.map(h => r[h] || '').join(',')).join('\n');
      fs.writeFileSync(queuePath, headerLine + '\n' + body + (body?'\n':''), 'utf8');
      console.log(`Queue filtrada: ${path.relative(root, queuePath)} (antes ${q.rows.length}, ahora ${kept.length})`);
    }
  }
}

main();



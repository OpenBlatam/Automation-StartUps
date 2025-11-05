#!/usr/bin/env node
/**
 * Alerts from Logs (dynamic thresholds)
 * - Reads dm_linkedin_logs.csv
 * - Computes rates per campaign/variant for last N lines
 * - Alerts if ERROR rate > 5%, SKIPPED_COMPLIANCE > 10%, SKIPPED_SUPPRESSED > 25%
 * - Optional Slack webhook via env SLACK_WEBHOOK
 */
const fs = require('fs');
const path = require('path');

const IN = path.resolve(__dirname, 'dm_linkedin_logs.csv');
const N = 500; // last N lines window
const webhook = process.env.SLACK_WEBHOOK || '';

function tailLines(p, n) {
  const lines = fs.readFileSync(p, 'utf8').trim().split('\n');
  return lines.slice(Math.max(1, lines.length - n)); // keep header off
}

function parse(lines) {
  const rows = [];
  for (const l of lines) {
    const parts = l.split(',');
    if (parts.length < 6) continue;
    rows.push({
      timestamp: parts[0],
      recipient: JSON.parse(parts[1]||'""'),
      variant: JSON.parse(parts[2]||'""'),
      campaign: JSON.parse(parts[3]||'""'),
      status: JSON.parse(parts[4]||'""'),
      error: JSON.parse(parts[5]||'""')
    });
  }
  return rows;
}

function groupByCampaignVariant(rows) {
  const map = new Map();
  rows.forEach(r => {
    const key = `${r.campaign}__${r.variant}`;
    const cur = map.get(key) || { total:0, sent:0, error:0, skippedComp:0, skippedSupp:0 };
    cur.total++;
    if (r.status==='SENT') cur.sent++;
    else if (r.status==='ERROR') cur.error++;
    else if (r.status==='SKIPPED_COMPLIANCE') cur.skippedComp++;
    else if (r.status==='SKIPPED_SUPPRESSED') cur.skippedSupp++;
    map.set(key, cur);
  });
  return map;
}

async function postSlack(text) {
  if (!webhook) return;
  const fetch = (await import('node-fetch')).default;
  try {
    await fetch(webhook, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ text }) });
  } catch (e) {}
}

async function main() {
  if (!fs.existsSync(IN)) { console.error('No logs found.'); process.exit(0); }
  const lines = tailLines(IN, N);
  if (!lines.length) return;
  const rows = parse(lines);
  const map = groupByCampaignVariant(rows);
  const alerts = [];
  for (const [key, v] of map.entries()) {
    const errRate = v.error / v.total;
    const compRate = v.skippedComp / v.total;
    const suppRate = v.skippedSupp / v.total;
    if (errRate > 0.05 || compRate > 0.10 || suppRate > 0.25) {
      alerts.push(`${key} → err ${(errRate*100).toFixed(1)}%, comp ${(compRate*100).toFixed(1)}%, supp ${(suppRate*100).toFixed(1)}% (n=${v.total})`);
    }
  }
  if (alerts.length) {
    const msg = `Alerts: \n${alerts.join('\n')}`;
    console.log(msg);
    await postSlack(msg);
  } else {
    console.log('No alerts.');
  }
}

if (require.main === module) main();

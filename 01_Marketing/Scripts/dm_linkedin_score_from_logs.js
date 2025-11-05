#!/usr/bin/env node
/**
 * Lead Scoring from Logs (CSV)
 * - Input: dm_linkedin_logs.csv
 * - Output: dm_linkedin_lead_scores.csv (recipient,score,last_status,last_error,last_timestamp)
 * - Scoring (configurable): SENT=+1, FAILED=0, ERROR=-1, SKIPPED_*=0; future: RESPONDED/CLICK/CONVERT from enriched logs
 */
const fs = require('fs');
const path = require('path');

const IN = path.resolve(__dirname, 'dm_linkedin_logs.csv');
const OUT = path.resolve(__dirname, 'dm_linkedin_lead_scores.csv');

const weights = {
  SENT: 1,
  FAILED: 0,
  ERROR: -1,
  SKIPPED_SUPPRESSED: 0,
  SKIPPED_COMPLIANCE: 0,
  SKIPPED_DEDUPE: 0,
};

function parseCsv(p) {
  if (!fs.existsSync(p)) return [];
  const lines = fs.readFileSync(p, 'utf8').split('\n').filter(Boolean);
  lines.shift();
  return lines.map(l => {
    // timestamp,recipient,variant,campaign,status,error
    const [timestamp, recipient, variant, campaign, status, error] = l.split(/,(.+)/)[1] ? l.split(',') : l.split(',');
    // fallback split naive
    const parts = l.split(',');
    return {
      timestamp: parts[0],
      recipient: JSON.parse(parts[1] || '""'),
      variant: JSON.parse(parts[2] || '""'),
      campaign: JSON.parse(parts[3] || '""'),
      status: JSON.parse(parts[4] || '""'),
      error: JSON.parse(parts[5] || '""'),
    };
  });
}

function main() {
  const rows = parseCsv(IN);
  const map = new Map();
  for (const r of rows) {
    const key = r.recipient;
    const cur = map.get(key) || { score: 0, last_status: '', last_error: '', last_timestamp: '' };
    cur.score += (weights[r.status] ?? 0);
    cur.last_status = r.status;
    cur.last_error = r.error;
    cur.last_timestamp = r.timestamp;
    map.set(key, cur);
  }
  const header = 'recipient,score,last_status,last_error,last_timestamp\n';
  let out = header;
  for (const [recipient, v] of map.entries()) {
    out += [recipient, v.score, v.last_status, JSON.stringify(v.last_error), v.last_timestamp].join(',') + '\n';
  }
  fs.writeFileSync(OUT, out, 'utf8');
  console.log('Scores written to', OUT);
}

if (require.main === module) main();

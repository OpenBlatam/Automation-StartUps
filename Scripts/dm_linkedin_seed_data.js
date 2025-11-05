#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, fileExists, parseCliFlags } = require('./utils_fs');

const root = path.resolve(__dirname, '..');
const logsDir = path.resolve(root, 'Logs');
ensureDir(logsDir);

const sendLog = path.resolve(logsDir, 'dm_send_log.csv');
const respLog = path.resolve(logsDir, 'dm_responses.csv');

const CAMPAIGNS = ['curso_ia_q1','webinar_q1','saas_demo_q1'];
const VARIANTS = ['LM_Base_A','LM_Resultado_B','WB_Urgencia_B','SP_SocialProof_A','VA_ValueFirst_A'];

function rand(arr) { return arr[Math.floor(Math.random()*arr.length)]; }
function randint(min, max) { return Math.floor(Math.random()*(max-min+1))+min; }

function ensureHeaders() {
  if (!fileExists(sendLog)) fs.writeFileSync(sendLog, 'timestamp,recipient,variant,campaign,status,error\n', 'utf8');
  if (!fileExists(respLog)) fs.writeFileSync(respLog, 'recipient,variant,responded,clicked,converted\n', 'utf8');
}

function generateRecipients(n) {
  const out = [];
  for (let i=0;i<n;i++) {
    const id = `user${String(i+1).padStart(4,'0')}`;
    out.push({
      recipient: `https://linkedin.com/in/${id}`,
      variant: rand(VARIANTS),
      campaign: rand(CAMPAIGNS)
    });
  }
  return out;
}

function appendSends(rows) {
  const lines = rows.map(r => {
    const t = new Date(Date.now() - randint(0, 7*24*60)*60000).toISOString();
    const status = Math.random() < 0.03 ? 'ERROR' : 'SENT';
    const error = status === 'ERROR' ? 'rate_limit' : '';
    return `${t},"${r.recipient}","${r.variant}","${r.campaign}",${status},${error}`;
  });
  fs.appendFileSync(sendLog, lines.join('\n') + '\n', 'utf8');
}

function appendResponses(rows) {
  // Simulate variant- and campaign-dependent response probability
  const base = {
    LM_Base_A: 0.05, LM_Resultado_B: 0.08, WB_Urgencia_B: 0.06, SP_SocialProof_A: 0.07, VA_ValueFirst_A: 0.09
  };
  const clickBase = 0.5; // conditional on responded
  const convBase = 0.2; // conditional on clicked
  const lines = rows.map(r => {
    const pr = base[r.variant] || 0.05;
    const responded = Math.random() < pr;
    const clicked = responded && Math.random() < clickBase;
    const converted = clicked && Math.random() < convBase;
    return `"${r.recipient}","${r.variant}",${responded},${clicked},${converted}`;
  });
  fs.appendFileSync(respLog, lines.join('\n') + '\n', 'utf8');
}

function main() {
  ensureHeaders();
  const { json } = parseCliFlags();
  const count = Number(process.env.SEED_COUNT || '100');
  const recipients = generateRecipients(count);
  appendSends(recipients);
  appendResponses(recipients);
  const msg = `Seeded ${count} sends and responses.`;
  if (json) {
    console.log(JSON.stringify({ ok: true, count }));
  } else {
    console.log(msg);
  }
}

main();



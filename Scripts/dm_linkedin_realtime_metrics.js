#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { notify } = require('./utils_notify');
const { fileExists, parseCliFlags } = require('./utils_fs');

function safeReadCsv(absPath) {
  try {
    if (!fs.existsSync(absPath)) return [];
    const raw = fs.readFileSync(absPath, 'utf8');
    const [headerLine, ...lines] = raw.split(/\r?\n/).filter(Boolean);
    if (!headerLine) return [];
    const headers = headerLine.split(',');
    return lines.map(l => {
      const cols = l.split(',');
      const obj = {};
      headers.forEach((h, i) => (obj[h.trim()] = (cols[i] || '').trim()));
      return obj;
    });
  } catch (e) {
    return [];
  }
}

function summarizeRealtime() {
  const root = path.resolve(__dirname, '..');
  const sendLog = path.resolve(root, 'Logs', 'dm_send_log.csv');
  const respLog = path.resolve(root, 'Logs', 'dm_responses.csv');
  const { noNotify, silent, json, alertMinRespRate, alertMaxErrorRate } = parseCliFlags();

  const sends = safeReadCsv(sendLog);
  const resps = safeReadCsv(respLog);

  if (!fileExists(sendLog)) {
    if (!silent) console.warn('Aviso: falta Logs/dm_send_log.csv');
  }
  if (!fileExists(respLog)) {
    if (!silent) console.warn('Aviso: falta Logs/dm_responses.csv');
  }

  const totalSent = sends.length;
  const totalResp = resps.filter(r => `${r.responded}`.toLowerCase() === 'true').length;
  const totalErr = sends.filter(s => (s.status || '').toUpperCase() === 'ERROR').length;
  const rate = totalSent > 0 ? ((totalResp / totalSent) * 100).toFixed(2) : '0.00';
  const errRate = totalSent > 0 ? ((totalErr / totalSent) * 100).toFixed(2) : '0.00';

  const last5 = sends.slice(-5).map(r => ({ timestamp: r.timestamp, recipient: r.recipient, variant: r.variant, campaign: r.campaign }));

  if (json) {
    const byVariantArr = Object.entries(byVariant).map(([v, d]) => ({ variant: v, sent: d.sent, responded: d.responded, rate: d.sent? d.responded/d.sent:0 }));
    const payload = { sent: totalSent, responded: totalResp, rate: Number(rate), last5, topVariants: byVariantArr.sort((a,b)=>b.rate-a.rate).slice(0,5) };
    console.log(JSON.stringify(payload));
  } else if (!silent) {
    console.log('— Realtime Metrics —');
    console.log(`Sent: ${totalSent} | Responded: ${totalResp} | Rate: ${rate}% | Errors: ${totalErr} (${errRate}%)`);
    console.log('Last 5 sends:');
    last5.forEach((r, i) => console.log(`[${i + 1}]`, r));
  } else {
    console.log(`sent=${totalSent} responded=${totalResp} rate=${rate}% errors=${totalErr} errRate=${errRate}%`);
  }

  const byVariant = {};
  sends.forEach(s => {
    const v = s.variant || 'NA';
    byVariant[v] = byVariant[v] || { sent: 0, responded: 0 };
    byVariant[v].sent++;
  });
  resps.forEach(r => {
    if (`${r.responded}`.toLowerCase() === 'true') {
      const v = r.variant || 'NA';
      byVariant[v] = byVariant[v] || { sent: 0, responded: 0 };
      byVariant[v].responded++;
    }
  });

  const top = Object.entries(byVariant)
    .map(([v, d]) => ({ v, rate: d.sent ? d.responded / d.sent : 0, sent: d.sent }))
    .sort((a, b) => b.rate - a.rate)
    .slice(0, 5);
  if (!json && !silent) {
    console.log('Top 5 variants by live rate:');
    top.forEach(t => console.log(`- ${t.v}: ${(t.rate * 100).toFixed(2)}% (sent ${t.sent})`));
  }
  if (!noNotify) {
    notify(`Realtime: sent ${totalSent}, resp ${totalResp}, rate ${rate}%, errors ${totalErr} (${errRate}%)`);
    const rateNum = Number(rate);
    const errNum = Number(errRate);
    if (totalSent >= 20 && rateNum < alertMinRespRate) {
      notify(`ALERTA: Tasa de respuesta baja (${rate}%) < ${alertMinRespRate}%`);
    }
    if (totalSent >= 20 && errNum > alertMaxErrorRate) {
      notify(`ALERTA: Tasa de errores alta (${errRate}%) > ${alertMaxErrorRate}%`);
    }
  }
}

summarizeRealtime();



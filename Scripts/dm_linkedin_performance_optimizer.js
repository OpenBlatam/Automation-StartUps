#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { notify } = require('./utils_notify');
const { fileExists, parseCliFlags, ensureDir } = require('./utils_fs');

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

function analyzePerformance(logs, responses) {
  const analysis = { timing: { byDay: {}, byHour: {} }, variants: {}, campaigns: {} };

  logs.forEach(log => {
    const date = new Date(log.timestamp || Date.now());
    const day = date.toISOString().split('T')[0];
    const hour = date.getHours();
    const variant = log.variant || 'NA';
    const campaign = log.campaign || 'NA';

    if (!analysis.timing.byDay[day]) analysis.timing.byDay[day] = { sent: 0, responded: 0 };
    analysis.timing.byDay[day].sent++;

    if (!analysis.timing.byHour[hour]) analysis.timing.byHour[hour] = { sent: 0, responded: 0 };
    analysis.timing.byHour[hour].sent++;

    if (!analysis.variants[variant]) analysis.variants[variant] = { sent: 0, responded: 0 };
    analysis.variants[variant].sent++;

    if (!analysis.campaigns[campaign]) analysis.campaigns[campaign] = { sent: 0, responded: 0 };
    analysis.campaigns[campaign].sent++;
  });

  responses.forEach(res => {
    const responded = `${res.responded}`.toLowerCase() === 'true';
    if (responded) {
      const match = logs.find(l => (l.recipient && res.recipient && l.recipient === res.recipient));
      if (match) {
        const date = new Date(match.timestamp || Date.now());
        const day = date.toISOString().split('T')[0];
        const hour = date.getHours();
        const variant = match.variant || 'NA';
        const campaign = match.campaign || 'NA';
        if (analysis.timing.byDay[day]) analysis.timing.byDay[day].responded++;
        if (analysis.timing.byHour[hour]) analysis.timing.byHour[hour].responded++;
        if (analysis.variants[variant]) analysis.variants[variant].responded++;
        if (analysis.campaigns[campaign]) analysis.campaigns[campaign].responded++;
      }
    }
  });

  const rateify = (obj) => {
    Object.keys(obj).forEach(k => {
      const d = obj[k];
      d.rate = d.sent > 0 ? (d.responded / d.sent) * 100 : 0;
    });
  };
  rateify(analysis.timing.byDay);
  rateify(analysis.timing.byHour);
  rateify(analysis.variants);
  rateify(analysis.campaigns);

  return analysis;
}

function main() {
  const root = path.resolve(__dirname, '..');
  const sendLog = path.resolve(root, 'Logs', 'dm_send_log.csv');
  const respLog = path.resolve(root, 'Logs', 'dm_responses.csv');
  const { noNotify, silent, json, outPath } = parseCliFlags();

  const logs = safeReadCsv(sendLog);
  const responses = safeReadCsv(respLog);
  if (!fileExists(sendLog) || !logs.length) {
    if (!silent) console.warn('Aviso: no se encontró `Logs/dm_send_log.csv` o está vacío.');
  }
  if (!fileExists(respLog) || !responses.length) {
    if (!silent) console.warn('Aviso: no se encontró `Logs/dm_responses.csv` o está vacío.');
  }

  const analysis = analyzePerformance(logs, responses);

  const bestVariants = Object.entries(analysis.variants)
    .map(([v, d]) => ({ v, sent: d.sent, rate: d.rate }))
    .filter(x => x.sent >= 10)
    .sort((a, b) => b.rate - a.rate)
    .slice(0, 5);

  const bestHours = Object.entries(analysis.timing.byHour)
    .map(([h, d]) => ({ h: Number(h), sent: d.sent, rate: d.rate }))
    .filter(x => x.sent >= 10)
    .sort((a, b) => b.rate - a.rate)
    .slice(0, 5);

  if (json) {
    console.log(JSON.stringify({
      bestVariants,
      bestHours,
      totals: { logs: logs.length, responses: responses.length }
    }));
  } else if (!silent) {
    console.log('— Performance Overview —');
    console.log('Top 5 variants (>=10 sends):');
    bestVariants.forEach(b => console.log(`- ${b.v}: ${b.rate.toFixed(2)}% (sent ${b.sent})`));
    console.log('Best hours (>=10 sends):');
    bestHours.forEach(b => console.log(`- ${b.h}:00 -> ${b.rate.toFixed(2)}% (sent ${b.sent})`));
  }

  if (!json && !silent) {
    console.log('Recomendaciones:');
    if (bestVariants[0]) console.log(`- Duplicar envíos de variante ganadora: ${bestVariants[0].v}`);
    if (bestHours[0]) console.log(`- Priorizar ventanas horarias: ${bestHours[0].h}:00`);
    console.log('- Pausar variantes con tasa < 2% y > 50 envíos.');
  }
  if (!noNotify) notify(`Optimizer listo. Top variante: ${bestVariants[0] ? bestVariants[0].v : 'NA'}`);

  // Markdown report
  const reportsDir = path.resolve(root, '01_Marketing', 'Reports');
  ensureDir(reportsDir);
  const defaultOut = path.resolve(reportsDir, `dm_optimizer_report_${new Date().toISOString().slice(0,10)}.md`);
  const outFile = outPath ? path.resolve(root, outPath) : defaultOut;
  const md = [];
  md.push(`# 🚀 Reporte de Optimización DM`);
  md.push(`Generado: ${new Date().toISOString()}`);
  md.push('');
  md.push(`## Totales`);
  md.push(`- Envíos: ${logs.length}`);
  md.push(`- Respuestas: ${responses.filter(r=>`${r.responded}`.toLowerCase()==='true').length}`);
  md.push('');
  md.push('## Top 5 Variantes (>=10 envíos)');
  bestVariants.forEach(b=> md.push(`- ${b.v}: ${b.rate.toFixed(2)}% (sent ${b.sent})`));
  md.push('');
  md.push('## Mejores Horas (>=10 envíos)');
  bestHours.forEach(b=> md.push(`- ${b.h}:00 -> ${b.rate.toFixed(2)}% (sent ${b.sent})`));
  md.push('');
  md.push('## Recomendaciones');
  if (bestVariants[0]) md.push(`- Duplicar envíos de: ${bestVariants[0].v}`);
  if (bestHours[0]) md.push(`- Priorizar: ${bestHours[0].h}:00`);
  md.push('- Pausar variantes con tasa < 2% y > 50 envíos.');
  fs.writeFileSync(outFile, md.join('\n'), 'utf8');
  if (!silent) console.log(`Reporte guardado en: ${path.relative(root, outFile)}`);
}

main();



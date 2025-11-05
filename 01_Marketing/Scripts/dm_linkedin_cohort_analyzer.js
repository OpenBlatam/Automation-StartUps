#!/usr/bin/env node
/**
 * Analizador de Cohortes
 * Analiza performance por cohorte (fecha de envío, campaña, variante)
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_cohort_analysis.json'),
  cohortBy: process.argv[2] || 'week', // week, month, campaign, variant
};

function parseLogs() {
  if (!fs.existsSync(CONFIG.logsFile)) return [];
  const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  }).filter(l => l.status === 'SENT');
}

function parseResponses() {
  if (!fs.existsSync(CONFIG.responsesFile)) return {};
  const lines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
  lines.shift();
  const map = {};
  lines.forEach(l => {
    const [recipient, responded, clicked, converted] = l.split(',');
    if (recipient) {
      map[recipient.trim()] = {
        responded: responded === 'true' || responded === '1',
        clicked: clicked === 'true' || clicked === '1',
        converted: converted === 'true' || converted === '1',
      };
    }
  });
  return map;
}

function getCohortKey(log, responses) {
  const date = new Date(log.timestamp || Date.now());
  
  switch (CONFIG.cohortBy) {
    case 'week':
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - date.getDay());
      return weekStart.toISOString().split('T')[0];
    case 'month':
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    case 'campaign':
      return log.campaign || 'unknown';
    case 'variant':
      return log.variant || 'unknown';
    default:
      return 'all';
  }
}

function analyzeCohorts(logs, responses) {
  const cohorts = {};
  
  logs.forEach(log => {
    const cohortKey = getCohortKey(log, responses);
    if (!cohorts[cohortKey]) {
      cohorts[cohortKey] = {
        sent: 0,
        responded: 0,
        clicked: 0,
        converted: 0,
        recipients: [],
      };
    }
    
    cohorts[cohortKey].sent++;
    const recipient = log.recipient?.trim();
    if (recipient) {
      cohorts[cohortKey].recipients.push(recipient);
      
      if (responses[recipient]) {
        if (responses[recipient].responded) cohorts[cohortKey].responded++;
        if (responses[recipient].clicked) cohorts[cohortKey].clicked++;
        if (responses[recipient].converted) cohorts[cohortKey].converted++;
      }
    }
  });
  
  // Calculate rates
  Object.keys(cohorts).forEach(key => {
    const c = cohorts[key];
    c.responseRate = c.sent > 0 ? (c.responded / c.sent) * 100 : 0;
    c.clickRate = c.sent > 0 ? (c.clicked / c.sent) * 100 : 0;
    c.conversionRate = c.sent > 0 ? (c.converted / c.sent) * 100 : 0;
    c.uniqueRecipients = new Set(c.recipients).size;
  });
  
  return cohorts;
}

function findBestCohorts(cohorts) {
  const sorted = Object.entries(cohorts)
    .map(([key, data]) => ({ key, ...data }))
    .sort((a, b) => b.responseRate - a.responseRate);
  
  return {
    bestResponseRate: sorted[0],
    bestConversionRate: sorted.sort((a, b) => b.conversionRate - a.conversionRate)[0],
    worstResponseRate: sorted[sorted.length - 1],
  };
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn('⚠️  No logs found');
    return;
  }
  
  const responses = parseResponses();
  const cohorts = analyzeCohorts(logs, responses);
  const best = findBestCohorts(cohorts);
  
  const report = {
    generatedAt: new Date().toISOString(),
    cohortBy: CONFIG.cohortBy,
    totalCohorts: Object.keys(cohorts).length,
    cohorts,
    bestPerforming: best,
    insights: [
      `Best response rate: ${best.bestResponseRate.key} (${best.bestResponseRate.responseRate.toFixed(1)}%)`,
      `Best conversion rate: ${best.bestConversionRate.key} (${best.bestConversionRate.conversionRate.toFixed(1)}%)`,
    ],
  };
  
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log(`✅ Cohort analysis complete → ${CONFIG.outputFile}`);
  console.log(`📊 Cohorts by ${CONFIG.cohortBy}: ${Object.keys(cohorts).length}`);
  console.log(`🏆 Best response rate: ${best.bestResponseRate.key} (${best.bestResponseRate.responseRate.toFixed(1)}%)`);
  console.log(`🎯 Best conversion rate: ${best.bestConversionRate.key} (${best.bestConversionRate.conversionRate.toFixed(1)}%)`);
}

if (require.main === module) {
  main();
}





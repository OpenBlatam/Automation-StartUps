#!/usr/bin/env node
/**
 * Optimizador A/B Automático
 * Analiza performance de variantes y recomienda winners
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'), // manual o desde CRM
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_ab_results.json'),
  minSamples: 10, // mínimo de envíos para considerar estadísticamente válido
  confidenceLevel: 0.95,
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
  });
}

function parseResponses() {
  if (!fs.existsSync(CONFIG.responsesFile)) return {};
  const lines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
  lines.shift();
  const responseMap = {};
  lines.forEach(l => {
    const [recipient, responded, clicked, converted] = l.split(',');
    if (recipient) {
      responseMap[recipient.trim()] = {
        responded: responded === 'true' || responded === '1',
        clicked: clicked === 'true' || clicked === '1',
        converted: converted === 'true' || converted === '1',
      };
    }
  });
  return responseMap;
}

function analyzeVariants(logs, responses) {
  const variantStats = {};
  
  logs.forEach(log => {
    if (log.status !== 'SENT') return;
    const variantId = log.variant || 'unknown';
    if (!variantStats[variantId]) {
      variantStats[variantId] = {
        sent: 0,
        responded: 0,
        clicked: 0,
        converted: 0,
        recipients: [],
      };
    }
    variantStats[variantId].sent++;
    const recipient = log.recipient?.trim();
    if (recipient && responses[recipient]) {
      variantStats[variantId].recipients.push(recipient);
      if (responses[recipient].responded) variantStats[variantId].responded++;
      if (responses[recipient].clicked) variantStats[variantId].clicked++;
      if (responses[recipient].converted) variantStats[variantId].converted++;
    }
  });
  
  // Calcular métricas
  Object.keys(variantStats).forEach(variantId => {
    const stats = variantStats[variantId];
    stats.responseRate = stats.sent > 0 ? (stats.responded / stats.sent) * 100 : 0;
    stats.clickRate = stats.sent > 0 ? (stats.clicked / stats.sent) * 100 : 0;
    stats.conversionRate = stats.sent > 0 ? (stats.converted / stats.sent) * 100 : 0;
    stats.isSignificant = stats.sent >= CONFIG.minSamples;
  });
  
  return variantStats;
}

function compareVariants(variantStats) {
  // Agrupar por campaña
  const byCampaign = {};
  Object.entries(variantStats).forEach(([variantId, stats]) => {
    const campaign = variantId.split('_')[0] || 'unknown';
    if (!byCampaign[campaign]) byCampaign[campaign] = [];
    byCampaign[campaign].push({ variantId, ...stats });
  });
  
  // Determinar winners por campaña
  const winners = {};
  Object.entries(byCampaign).forEach(([campaign, variants]) => {
    if (variants.length < 2) return;
    
    // Ordenar por response rate (desc)
    const sorted = variants
      .filter(v => v.isSignificant)
      .sort((a, b) => b.responseRate - a.responseRate);
    
    if (sorted.length >= 2) {
      const winner = sorted[0];
      const runnerUp = sorted[1];
      const improvement = winner.responseRate - runnerUp.responseRate;
      
      winners[campaign] = {
        winner: winner.variantId,
        winnerRate: winner.responseRate.toFixed(2),
        runnerUp: runnerUp.variantId,
        runnerUpRate: runnerUp.responseRate.toFixed(2),
        improvement: improvement.toFixed(2),
        confidence: winner.sent >= 20 ? 'high' : winner.sent >= 10 ? 'medium' : 'low',
        recommendation: improvement > 5 ? 'scale_winner' : improvement > 2 ? 'test_more' : 'keep_testing',
      };
    }
  });
  
  return winners;
}

function main() {
  const logs = parseLogs();
  const responses = parseResponses();
  
  if (!logs.length) {
    console.warn('⚠️  No logs found');
    return;
  }
  
  const variantStats = analyzeVariants(logs, responses);
  const winners = compareVariants(variantStats);
  
  const report = {
    generatedAt: new Date().toISOString(),
    totalVariants: Object.keys(variantStats).length,
    minSamplesRequired: CONFIG.minSamples,
    variantStats,
    winners,
    recommendations: Object.entries(winners).map(([campaign, data]) => ({
      campaign,
      action: data.recommendation,
      message: data.recommendation === 'scale_winner' 
        ? `Scale ${data.winner} (+${data.improvement}% vs runner-up)`
        : data.recommendation === 'test_more'
        ? `Continue testing, ${data.winner} is slightly better (+${data.improvement}%)`
        : `Keep testing, difference too small (${data.improvement}%)`,
    })),
  };
  
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log(`✅ A/B Analysis complete → ${CONFIG.outputFile}`);
  console.log(`📊 Analyzed ${Object.keys(variantStats).length} variants`);
  
  if (Object.keys(winners).length > 0) {
    console.log('\n🏆 Winners by Campaign:');
    Object.entries(winners).forEach(([campaign, data]) => {
      console.log(`  ${campaign}: ${data.winner} (${data.winnerRate}% vs ${data.runnerUpRate}%)`);
      console.log(`    → ${data.recommendation}: ${report.recommendations.find(r => r.campaign === campaign).message}`);
    });
  }
}

if (require.main === module) {
  main();
}





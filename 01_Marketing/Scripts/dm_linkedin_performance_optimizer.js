#!/usr/bin/env node
/**
 * Optimizador de Rendimiento
 * Analiza y recomienda optimizaciones para mejorar tasas de respuesta
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  variantsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_variants_localized_completo.json'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_performance_optimization.json'),
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
    const [recipient, responded] = l.split(',');
    if (recipient) {
      map[recipient.trim()] = {
        responded: responded === 'true' || responded === '1',
      };
    }
  });
  return map;
}

function analyzePerformance(logs, responses) {
  const analysis = {
    timing: { byHour: {}, byDay: {} },
    variants: {},
    campaigns: {},
    messageLength: { short: 0, medium: 0, long: 0 },
    issues: [],
    recommendations: [],
  };
  
  // Timing analysis
  logs.forEach(log => {
    if (!log.timestamp) return;
    const date = new Date(log.timestamp);
    const hour = date.getHours();
    const day = date.getDay();
    
    if (!analysis.timing.byHour[hour]) {
      analysis.timing.byHour[hour] = { sent: 0, responded: 0 };
    }
    if (!analysis.timing.byDay[day]) {
      analysis.timing.byDay[day] = { sent: 0, responded: 0 };
    }
    
    analysis.timing.byHour[hour].sent++;
    analysis.timing.byDay[day].sent++;
    
    if (responses[log.recipient]?.responded) {
      analysis.timing.byHour[hour].responded++;
      analysis.timing.byDay[day].responded++;
    }
  });
  
  // Variant analysis
  logs.forEach(log => {
    const variantId = log.variant || 'unknown';
    if (!analysis.variants[variantId]) {
      analysis.variants[variantId] = { sent: 0, responded: 0 };
    }
    analysis.variants[variantId].sent++;
    if (responses[log.recipient]?.responded) {
      analysis.variants[variantId].responded++;
    }
  });
  
  // Campaign analysis
  logs.forEach(log => {
    const camp = log.campaign || 'unknown';
    if (!analysis.campaigns[camp]) {
      analysis.campaigns[camp] = { sent: 0, responded: 0 };
    }
    analysis.campaigns[camp].sent++;
    if (responses[log.recipient]?.responded) {
      analysis.campaigns[camp].responded++;
    }
  });
  
  // Calculate rates
  Object.keys(analysis.timing.byHour).forEach(h => {
    const d = analysis.timing.byHour[h];
    d.rate = d.sent > 0 ? (d.responded / d.sent) * 100 : 0;
  });
  
  Object.keys(analysis.timing.byDay).forEach(d => {
    const data = analysis.timing.byDay[d];
    data.rate = data.sent > 0 ? (data.responded / data.sent) * 100 : 0;
  });
  
  Object.keys(analysis.variants).forEach(v => {
    const data = analysis.variants[v];
    data.rate = data.sent > 0 ? (data.responded / data.sent) * 100 : 0;
  });
  
  Object.keys(analysis.campaigns).forEach(c => {
    const data = analysis.campaigns[c];
    data.rate = data.sent > 0 ? (data.responded / data.sent) * 100 : 0;
  });
  
  return analysis;
}

function generateRecommendations(analysis, logs) {
  const recommendations = [];
  
  // Timing recommendations
  const bestHour = Object.entries(analysis.timing.byHour)
    .map(([h, d]) => ({ hour: parseInt(h), ...d }))
    .filter(d => d.sent >= 10)
    .sort((a, b) => b.rate - a.rate)[0];
  
  const worstHour = Object.entries(analysis.timing.byHour)
    .map(([h, d]) => ({ hour: parseInt(h), ...d }))
    .filter(d => d.sent >= 10)
    .sort((a, b) => a.rate - b.rate)[0];
  
  if (bestHour && worstHour && bestHour.rate > worstHour.rate + 5) {
    recommendations.push({
      type: 'timing',
      priority: 'high',
      title: 'Optimize Send Timing',
      description: `Hour ${bestHour.hour}:00 has ${bestHour.rate.toFixed(1)}% response rate vs ${worstHour.rate.toFixed(1)}% at ${worstHour.hour}:00`,
      action: `Schedule more sends at ${bestHour.hour}:00, reduce sends at ${worstHour.hour}:00`,
      impact: `Expected +${((bestHour.rate - worstHour.rate) / 2).toFixed(1)}% response rate improvement`,
    });
  }
  
  // Variant recommendations
  const bestVariant = Object.entries(analysis.variants)
    .map(([id, d]) => ({ id, ...d }))
    .filter(d => d.sent >= 10)
    .sort((a, b) => b.rate - a.rate)[0];
  
  const worstVariant = Object.entries(analysis.variants)
    .map(([id, d]) => ({ id, ...d }))
    .filter(d => d.sent >= 10)
    .sort((a, b) => a.rate - b.rate)[0];
  
  if (bestVariant && worstVariant && bestVariant.rate > worstVariant.rate + 3) {
    recommendations.push({
      type: 'variant',
      priority: 'high',
      title: 'Scale Best Performing Variant',
      description: `${bestVariant.id} outperforms ${worstVariant.id} by ${(bestVariant.rate - worstVariant.rate).toFixed(1)}%`,
      action: `Increase send volume for "${bestVariant.id}" by 30-50%`,
      impact: `Expected ${((bestVariant.rate - worstVariant.rate) * 0.3).toFixed(1)}% overall improvement`,
    });
  }
  
  // Overall response rate check
  const totalSent = logs.length;
  const totalResponded = Object.values(responses).filter(r => r.responded).length;
  const overallRate = totalSent > 0 ? (totalResponded / totalSent) * 100 : 0;
  
  if (overallRate < 15) {
    recommendations.push({
      type: 'general',
      priority: 'critical',
      title: 'Overall Response Rate Below Benchmark',
      description: `Current rate is ${overallRate.toFixed(1)}%, target is 20%+`,
      action: 'Review personalization, message quality, and targeting criteria',
      impact: `Potential +5-10% improvement with better personalization`,
    });
  }
  
  return recommendations;
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn('⚠️  No logs found');
    return;
  }
  
  const responses = parseResponses();
  const analysis = analyzePerformance(logs, responses);
  const recommendations = generateRecommendations(analysis, logs);
  
  const report = {
    generatedAt: new Date().toISOString(),
    analysis,
    recommendations,
    summary: {
      totalAnalyzed: logs.length,
      bestHour: Object.entries(analysis.timing.byHour)
        .map(([h, d]) => ({ hour: parseInt(h), rate: d.rate }))
        .sort((a, b) => b.rate - a.rate)[0],
      bestVariant: Object.entries(analysis.variants)
        .map(([id, d]) => ({ id, rate: d.rate }))
        .filter(d => analysis.variants[d.id].sent >= 10)
        .sort((a, b) => b.rate - a.rate)[0],
    },
  };
  
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log('⚡ Performance Optimization Analysis\n');
  console.log('🎯 Top Recommendations:');
  recommendations
    .sort((a, b) => {
      const priorityOrder = { critical: 3, high: 2, medium: 1, low: 0 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    })
    .slice(0, 5)
    .forEach((rec, i) => {
      console.log(`\n${i + 1}. [${rec.priority.toUpperCase()}] ${rec.title}`);
      console.log(`   ${rec.description}`);
      console.log(`   → ${rec.action}`);
      if (rec.impact) {
        console.log(`   💡 Impact: ${rec.impact}`);
      }
    });
  
  console.log(`\n✅ Report saved: ${CONFIG.outputFile}`);
}

if (require.main === module) {
  main();
}


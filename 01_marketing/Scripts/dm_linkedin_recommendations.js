#!/usr/bin/env node
/**
 * Sistema de Recomendaciones Inteligentes
 * Sugiere variantes, timing, y estrategias basado en datos históricos
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  variantsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_variants_localized_completo.json'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_recommendations.json'),
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

function analyzeVariantPerformance(logs, responses) {
  const variantStats = {};
  
  logs.forEach(log => {
    const variantId = log.variant || 'unknown';
    if (!variantStats[variantId]) {
      variantStats[variantId] = { sent: 0, responded: 0, clicked: 0, converted: 0 };
    }
    
    variantStats[variantId].sent++;
    const recipient = log.recipient?.trim();
    if (recipient && responses[recipient]) {
      if (responses[recipient].responded) variantStats[variantId].responded++;
      if (responses[recipient].clicked) variantStats[variantId].clicked++;
      if (responses[recipient].converted) variantStats[variantId].converted++;
    }
  });
  
  Object.keys(variantStats).forEach(id => {
    const s = variantStats[id];
    s.responseRate = s.sent > 0 ? (s.responded / s.sent) * 100 : 0;
    s.clickRate = s.sent > 0 ? (s.clicked / s.sent) * 100 : 0;
    s.conversionRate = s.sent > 0 ? (s.converted / s.sent) * 100 : 0;
  });
  
  return variantStats;
}

function analyzeTimingPerformance(logs, responses) {
  const timingStats = {
    byDay: {},
    byHour: {},
  };
  
  logs.forEach(log => {
    if (!log.timestamp) return;
    const date = new Date(log.timestamp);
    const day = date.getDay();
    const hour = date.getHours();
    
    if (!timingStats.byDay[day]) {
      timingStats.byDay[day] = { sent: 0, responded: 0 };
    }
    if (!timingStats.byHour[hour]) {
      timingStats.byHour[hour] = { sent: 0, responded: 0 };
    }
    
    timingStats.byDay[day].sent++;
    timingStats.byHour[hour].sent++;
    
    const recipient = log.recipient?.trim();
    if (recipient && responses[recipient]?.responded) {
      timingStats.byDay[day].responded++;
      timingStats.byHour[hour].responded++;
    }
  });
  
  // Calculate rates
  Object.keys(timingStats.byDay).forEach(day => {
    const d = timingStats.byDay[day];
    d.responseRate = d.sent > 0 ? (d.responded / d.sent) * 100 : 0;
  });
  
  Object.keys(timingStats.byHour).forEach(hour => {
    const h = timingStats.byHour[hour];
    h.responseRate = h.sent > 0 ? (h.responded / h.sent) * 100 : 0;
  });
  
  return timingStats;
}

function generateRecommendations(variantStats, timingStats) {
  const recommendations = [];
  
  // Variant recommendations
  const variants = Object.entries(variantStats)
    .map(([id, stats]) => ({ id, ...stats }))
    .sort((a, b) => b.responseRate - a.responseRate);
  
  if (variants.length > 0) {
    const best = variants[0];
    const worst = variants[variants.length - 1];
    
    recommendations.push({
      type: 'variant',
      priority: 'high',
      title: 'Scale Best Performing Variant',
      description: `"${best.id}" has ${best.responseRate.toFixed(1)}% response rate. Consider increasing send volume.`,
      action: `Increase sends of "${best.id}" variant by 20-30%`,
    });
    
    if (worst.responseRate < 10 && worst.sent >= 10) {
      recommendations.push({
        type: 'variant',
        priority: 'medium',
        title: 'Review Low Performing Variant',
        description: `"${worst.id}" has only ${worst.responseRate.toFixed(1)}% response rate.`,
        action: `Consider pausing or revising "${worst.id}" variant`,
      });
    }
  }
  
  // Timing recommendations
  const bestDay = Object.entries(timingStats.byDay)
    .map(([day, stats]) => ({ day: parseInt(day), ...stats }))
    .sort((a, b) => b.responseRate - a.responseRate)[0];
  
  const bestHour = Object.entries(timingStats.byHour)
    .map(([hour, stats]) => ({ hour: parseInt(hour), ...stats }))
    .sort((a, b) => b.responseRate - a.responseRate)[0];
  
  if (bestDay && bestDay.sent >= 10) {
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    recommendations.push({
      type: 'timing',
      priority: 'high',
      title: 'Optimal Day for Sending',
      description: `${dayNames[bestDay.day]} shows ${bestDay.responseRate.toFixed(1)}% response rate`,
      action: `Schedule more sends on ${dayNames[bestDay.day]}`,
    });
  }
  
  if (bestHour && bestHour.sent >= 10) {
    recommendations.push({
      type: 'timing',
      priority: 'high',
      title: 'Optimal Hour for Sending',
      description: `${bestHour.hour}:00 shows ${bestHour.responseRate.toFixed(1)}% response rate`,
      action: `Schedule more sends at ${bestHour.hour}:00`,
    });
  }
  
  // General recommendations
  const totalSent = logs.length;
  const totalResponded = Object.values(responses).filter(r => r.responded).length;
  const avgResponseRate = totalSent > 0 ? (totalResponded / totalSent) * 100 : 0;
  
  if (avgResponseRate < 15) {
    recommendations.push({
      type: 'strategy',
      priority: 'high',
      title: 'Below Benchmark Response Rate',
      description: `Current response rate is ${avgResponseRate.toFixed(1)}%, below 20% benchmark`,
      action: 'Review personalization, test new hooks, improve targeting',
    });
  }
  
  if (totalSent < 50) {
    recommendations.push({
      type: 'strategy',
      priority: 'medium',
      title: 'Insufficient Sample Size',
      description: `Only ${totalSent} sends tracked. Need more data for reliable insights.`,
      action: 'Continue sending and re-analyze with larger sample',
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
  const variantStats = analyzeVariantPerformance(logs, responses);
  const timingStats = analyzeTimingPerformance(logs, responses);
  const recommendations = generateRecommendations(variantStats, timingStats);
  
  const report = {
    generatedAt: new Date().toISOString(),
    summary: {
      totalSends: logs.length,
      totalResponses: Object.values(responses).filter(r => r.responded).length,
      avgResponseRate: logs.length > 0 
        ? ((Object.values(responses).filter(r => r.responded).length / logs.length) * 100).toFixed(1)
        : 0,
    },
    variantPerformance: variantStats,
    timingPerformance: timingStats,
    recommendations,
  };
  
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log(`✅ Recommendations generated → ${CONFIG.outputFile}`);
  console.log(`\n💡 Top Recommendations:`);
  recommendations
    .sort((a, b) => a.priority === 'high' ? -1 : 1)
    .slice(0, 5)
    .forEach((rec, i) => {
      console.log(`\n${i + 1}. [${rec.priority.toUpperCase()}] ${rec.title}`);
      console.log(`   ${rec.description}`);
      console.log(`   → ${rec.action}`);
    });
}

if (require.main === module) {
  main();
}





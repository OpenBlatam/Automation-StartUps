#!/usr/bin/env node
/**
 * Análisis de ROI Detallado
 * Calcula ROI completo con costos, ingresos, CAC, LTV, payback period
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_roi_detailed.json'),
  // Configuración de costos (ajusta según tu caso)
  costPerDM: parseFloat(process.env.COST_PER_DM) || 0.10, // tiempo/automation cost
  toolCostMonthly: parseFloat(process.env.TOOL_COST_MONTHLY) || 0,
  averageDealValue: parseFloat(process.env.AVG_DEAL_VALUE) || 1000,
  averageConversionRate: parseFloat(process.env.AVG_CONVERSION_RATE) || 0.05, // 5%
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

function calculateROI(logs, responses) {
  const totalSent = logs.length;
  const totalResponded = Object.values(responses).filter(r => r.responded).length;
  const totalClicked = Object.values(responses).filter(r => r.clicked).length;
  const totalConverted = Object.values(responses).filter(r => r.converted).length;
  
  // Costs
  const dmCosts = totalSent * CONFIG.costPerDM;
  const monthlyToolCost = CONFIG.toolCostMonthly;
  const totalCosts = dmCosts + monthlyToolCost;
  
  // Revenue (basado en conversiones)
  const actualConversions = totalConverted || (totalResponded * CONFIG.averageConversionRate);
  const revenue = actualConversions * CONFIG.averageDealValue;
  
  // ROI
  const roi = totalCosts > 0 ? ((revenue - totalCosts) / totalCosts) * 100 : 0;
  
  // CAC (Customer Acquisition Cost)
  const cac = actualConversions > 0 ? totalCosts / actualConversions : 0;
  
  // LTV (Lifetime Value) - asumimos LTV = deal value * 3 (3x para SaaS típico)
  const ltv = CONFIG.averageDealValue * 3;
  
  // LTV:CAC Ratio
  const ltvCacRatio = cac > 0 ? ltv / cac : 0;
  
  // Payback Period (meses)
  const monthlyRevenue = revenue / 12; // Asumiendo distribución anual
  const paybackMonths = monthlyRevenue > 0 ? totalCosts / monthlyRevenue : 0;
  
  // Conversion Funnel
  const responseRate = totalSent > 0 ? (totalResponded / totalSent) * 100 : 0;
  const clickRate = totalSent > 0 ? (totalClicked / totalSent) * 100 : 0;
  const conversionRate = totalResponded > 0 ? (actualConversions / totalResponded) * 100 : 0;
  
  return {
    period: 'all-time',
    totalSent,
    totalResponded,
    totalClicked,
    totalConverted: actualConversions,
    costs: {
      perDM: CONFIG.costPerDM,
      dmTotal: dmCosts,
      toolsMonthly: monthlyToolCost,
      total: totalCosts,
    },
    revenue: {
      perConversion: CONFIG.averageDealValue,
      total: revenue,
      estimated: actualConversions * CONFIG.averageDealValue,
    },
    metrics: {
      roi: roi,
      cac: cac,
      ltv: ltv,
      ltvCacRatio: ltvCacRatio,
      paybackMonths: paybackMonths,
      responseRate: responseRate,
      clickRate: clickRate,
      conversionRate: conversionRate,
    },
    benchmarks: {
      roi: roi >= 300 ? 'excellent' : roi >= 200 ? 'good' : roi >= 100 ? 'acceptable' : 'low',
      ltvCacRatio: ltvCacRatio >= 3 ? 'excellent' : ltvCacRatio >= 2 ? 'good' : 'needs_improvement',
      paybackMonths: paybackMonths <= 6 ? 'excellent' : paybackMonths <= 12 ? 'good' : 'long',
    },
  };
}

function generateInsights(roi) {
  const insights = [];
  
  if (roi.metrics.roi < 100) {
    insights.push({
      type: 'warning',
      title: 'ROI Below Target',
      message: `Current ROI is ${roi.metrics.roi.toFixed(1)}%. Target: 300%+.`,
      action: 'Focus on improving conversion rate and reducing costs per DM',
    });
  }
  
  if (roi.metrics.ltvCacRatio < 2) {
    insights.push({
      type: 'warning',
      title: 'Low LTV:CAC Ratio',
      message: `Ratio is ${roi.metrics.ltvCacRatio.toFixed(1)}:1. Target: 3:1+.`,
      action: 'Increase deal value or reduce acquisition costs',
    });
  }
  
  if (roi.metrics.responseRate < 15) {
    insights.push({
      type: 'improvement',
      title: 'Response Rate Opportunity',
      message: `Response rate is ${roi.metrics.responseRate.toFixed(1)}%. Benchmark: 20%+.`,
      action: 'Improve personalization and message quality',
    });
  }
  
  if (roi.metrics.cac > roi.revenue.perConversion * 0.3) {
    insights.push({
      type: 'warning',
      title: 'High CAC',
      message: `CAC is ${roi.metrics.cac.toFixed(2)} (${((roi.metrics.cac / roi.revenue.perConversion) * 100).toFixed(0)}% of deal value).`,
      action: 'Optimize conversion funnel to reduce CAC',
    });
  }
  
  if (roi.metrics.roi >= 300 && roi.metrics.ltvCacRatio >= 3) {
    insights.push({
      type: 'success',
      title: 'Excellent Performance',
      message: 'ROI and LTV:CAC ratios are above benchmarks. Scale successful campaigns.',
      action: 'Increase budget and volume on best-performing variants',
    });
  }
  
  return insights;
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn('⚠️  No logs found');
    return;
  }
  
  const responses = parseResponses();
  const roi = calculateROI(logs, responses);
  const insights = generateInsights(roi);
  
  const report = {
    generatedAt: new Date().toISOString(),
    config: {
      costPerDM: CONFIG.costPerDM,
      toolCostMonthly: CONFIG.toolCostMonthly,
      averageDealValue: CONFIG.averageDealValue,
    },
    roi,
    insights,
  };
  
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log('💰 Detailed ROI Analysis\n');
  console.log('📊 Financial Summary:');
  console.log(`  Total Cost: $${roi.costs.total.toFixed(2)}`);
  console.log(`  Total Revenue: $${roi.revenue.total.toFixed(2)}`);
  console.log(`  ROI: ${roi.metrics.roi.toFixed(1)}% (${roi.benchmarks.roi})`);
  console.log(`  CAC: $${roi.metrics.cac.toFixed(2)}`);
  console.log(`  LTV:CAC Ratio: ${roi.metrics.ltvCacRatio.toFixed(1)}:1 (${roi.benchmarks.ltvCacRatio})`);
  console.log(`  Payback Period: ${roi.metrics.paybackMonths.toFixed(1)} months (${roi.benchmarks.paybackMonths})`);
  
  console.log('\n📈 Funnel Metrics:');
  console.log(`  Response Rate: ${roi.metrics.responseRate.toFixed(1)}%`);
  console.log(`  Click Rate: ${roi.metrics.clickRate.toFixed(1)}%`);
  console.log(`  Conversion Rate: ${roi.metrics.conversionRate.toFixed(1)}%`);
  
  console.log('\n💡 Key Insights:');
  insights.forEach((insight, i) => {
    console.log(`\n${i + 1}. [${insight.type.toUpperCase()}] ${insight.title}`);
    console.log(`   ${insight.message}`);
    console.log(`   → ${insight.action}`);
  });
  
  console.log(`\n✅ Report saved: ${CONFIG.outputFile}`);
}

if (require.main === module) {
  main();
}





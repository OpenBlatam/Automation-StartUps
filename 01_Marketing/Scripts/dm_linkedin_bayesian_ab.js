#!/usr/bin/env node
/**
 * Análisis A/B Bayesiano Avanzado
 * Determina winners con análisis estadístico más sofisticado
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputFile: path.resolve(__dirname, '../Reports/dm_linkedin_bayesian_ab.json'),
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

// Beta distribution para análisis bayesiano
function betaMean(alpha, beta) {
  return alpha / (alpha + beta);
}

function betaVariance(alpha, beta) {
  const n = alpha + beta;
  return (alpha * beta) / (n * n * (n + 1));
}

// Simulación Monte Carlo para probabilidad de ser mejor
function probabilityBetter(variantA, variantB, iterations = 10000) {
  let aBetter = 0;
  
  for (let i = 0; i < iterations; i++) {
    // Sample de distribución beta
    const aSample = sampleBeta(variantA.alpha, variantA.beta);
    const bSample = sampleBeta(variantB.alpha, variantB.beta);
    if (aSample > bSample) aBetter++;
  }
  
  return aBetter / iterations;
}

function sampleBeta(alpha, beta) {
  // Aproximación simple (para producción usar librería de stats)
  // Basado en transformada inversa
  const u = Math.random();
  // Aproximación con transformada (simplificada)
  return Math.pow(u, 1 / alpha) / (Math.pow(u, 1 / alpha) + Math.pow(1 - u, 1 / beta));
}

function analyzeBayesian(logs, responses) {
  const variants = {};
  
  logs.forEach(log => {
    const variantId = log.variant || 'unknown';
    if (!variants[variantId]) {
      variants[variantId] = { sent: 0, responded: 0 };
    }
    
    variants[variantId].sent++;
    const recipient = log.recipient?.trim();
    if (recipient && responses[recipient]?.responded) {
      variants[variantId].responded++;
    }
  });
  
  // Convertir a parámetros Beta (prior no informativo: alpha=1, beta=1)
  Object.keys(variants).forEach(id => {
    const v = variants[id];
    // Beta posterior: alpha = 1 + successes, beta = 1 + failures
    v.alpha = 1 + v.responded;
    v.beta = 1 + (v.sent - v.responded);
    v.mean = betaMean(v.alpha, v.beta);
    v.variance = betaVariance(v.alpha, v.beta);
    v.responseRate = v.sent > 0 ? (v.responded / v.sent) * 100 : 0;
  });
  
  // Comparar todas las variantes
  const comparisons = [];
  const variantList = Object.entries(variants);
  
  for (let i = 0; i < variantList.length; i++) {
    for (let j = i + 1; j < variantList.length; j++) {
      const [idA, varA] = variantList[i];
      const [idB, varB] = variantList[j];
      
      const probABetter = probabilityBetter(varA, varB);
      const probBBetter = 1 - probABetter;
      
      comparisons.push({
        variantA: idA,
        variantB: idB,
        probABetter,
        probBBetter,
        recommendation: probABetter > CONFIG.confidenceLevel 
          ? `Scale ${idA}` 
          : probBBetter > CONFIG.confidenceLevel 
          ? `Scale ${idB}` 
          : 'Continue testing',
        confidence: Math.max(probABetter, probBBetter),
      });
    }
  }
  
  // Encontrar winners
  const winners = variantList
    .map(([id, v]) => ({
      id,
      mean: v.mean,
      responseRate: v.responseRate,
      confidence: v.sent >= 20 ? 'high' : v.sent >= 10 ? 'medium' : 'low',
    }))
    .sort((a, b) => b.mean - a.mean);
  
  return {
    variants,
    comparisons,
    winners,
  };
}

function main() {
  const logs = parseLogs();
  if (!logs.length) {
    console.warn('⚠️  No logs found');
    return;
  }
  
  const responses = parseResponses();
  const analysis = analyzeBayesian(logs, responses);
  
  const report = {
    generatedAt: new Date().toISOString(),
    method: 'Bayesian A/B Testing',
    confidenceLevel: CONFIG.confidenceLevel,
    analysis,
    recommendations: analysis.comparisons
      .filter(c => c.confidence > CONFIG.confidenceLevel)
      .map(c => ({
        action: c.recommendation,
        confidence: (c.confidence * 100).toFixed(1) + '%',
      })),
  };
  
  fs.writeFileSync(CONFIG.outputFile, JSON.stringify(report, null, 2), 'utf8');
  
  console.log('🔬 Bayesian A/B Analysis Complete\n');
  console.log('🏆 Top Variants:');
  analysis.winners.slice(0, 5).forEach((w, i) => {
    console.log(`  ${i + 1}. ${w.id}: ${(w.mean * 100).toFixed(2)}% (${w.confidence} confidence)`);
  });
  
  console.log('\n💡 Recommendations:');
  report.recommendations.slice(0, 5).forEach((r, i) => {
    console.log(`  ${i + 1}. ${r.action} (${r.confidence} confidence)`);
  });
  
  console.log(`\n✅ Report saved: ${CONFIG.outputFile}`);
}

if (require.main === module) {
  main();
}





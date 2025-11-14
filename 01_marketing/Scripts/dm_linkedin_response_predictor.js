#!/usr/bin/env node
/**
 * Predictor de Respuesta
 * Usa ML simple (regresión logística) para predecir probabilidad de respuesta
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_predictions.csv'),
  minSamples: 50, // mínimo para entrenar modelo
};

function parseHistoricalData(logs, responses) {
  const features = [];
  const labels = [];
  
  logs.forEach(log => {
    if (log.status !== 'SENT') return;
    const recipient = log.recipient?.trim();
    if (!recipient || !responses[recipient]) return;
    
    // Features simples (puedes expandir)
    const featuresVec = [
      log.variant ? (log.variant.includes('Problem') ? 1 : 0) : 0, // hook type
      log.variant ? (log.variant.includes('Benefit') ? 1 : 0) : 0,
      log.variant ? (log.variant.includes('Urgency') ? 1 : 0) : 0,
      log.campaign ? (log.campaign.includes('curso') ? 1 : 0) : 0, // product type
      log.campaign ? (log.campaign.includes('webinar') ? 1 : 0) : 0,
      log.campaign ? (log.campaign.includes('saas') ? 1 : 0) : 0,
      // Day of week (simplified)
      new Date(log.timestamp || Date.now()).getDay() / 7,
      // Hour (simplified to 0-1)
      new Date(log.timestamp || Date.now()).getHours() / 24,
    ];
    
    features.push(featuresVec);
    labels.push(responses[recipient].responded ? 1 : 0);
  });
  
  return { features, labels };
}

function simpleLogisticRegression(features, labels) {
  // Regresión logística muy simple (gradient descent básico)
  const nFeatures = features[0]?.length || 0;
  const weights = new Array(nFeatures).fill(0);
  const bias = 0;
  const learningRate = 0.01;
  const iterations = 100;
  
  for (let iter = 0; iter < iterations; iter++) {
    features.forEach((feat, idx) => {
      const z = weights.reduce((sum, w, i) => sum + w * feat[i], 0) + bias;
      const prediction = 1 / (1 + Math.exp(-z)); // sigmoid
      const error = prediction - labels[idx];
      
      weights.forEach((_, i) => {
        weights[i] -= learningRate * error * feat[i];
      });
      bias -= learningRate * error;
    });
  }
  
  return { weights, bias };
}

function predict(weights, bias, features) {
  const z = weights.reduce((sum, w, i) => sum + w * features[i], 0) + bias;
  return 1 / (1 + Math.exp(-z));
}

function main() {
  // Parse logs
  if (!fs.existsSync(CONFIG.logsFile)) {
    console.warn('⚠️  Logs file not found');
    return;
  }
  
  const logLines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const logHeaders = logLines[0]?.split(',') || [];
  const logs = logLines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    logHeaders.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  });
  
  // Parse responses
  const responses = parseResponses();
  
  // Historical data
  const { features, labels } = parseHistoricalData(logs, responses);
  
  if (features.length < CONFIG.minSamples) {
    console.warn(`⚠️  Insufficient data (${features.length} samples, need ${CONFIG.minSamples})`);
    return;
  }
  
  // Train model
  console.log(`🔮 Training model on ${features.length} samples...`);
  const { weights, bias } = simpleLogisticRegression(features, labels);
  
  // Predict for all sent (including those without responses yet)
  const sent = logs.filter(l => l.status === 'SENT');
  const predictions = sent.map(log => {
    const featuresVec = [
      log.variant ? (log.variant.includes('Problem') ? 1 : 0) : 0,
      log.variant ? (log.variant.includes('Benefit') ? 1 : 0) : 0,
      log.variant ? (log.variant.includes('Urgency') ? 1 : 0) : 0,
      log.campaign ? (log.campaign.includes('curso') ? 1 : 0) : 0,
      log.campaign ? (log.campaign.includes('webinar') ? 1 : 0) : 0,
      log.campaign ? (log.campaign.includes('saas') ? 1 : 0) : 0,
      new Date(log.timestamp || Date.now()).getDay() / 7,
      new Date(log.timestamp || Date.now()).getHours() / 24,
    ];
    
    const probability = predict(weights, bias, featuresVec);
    return {
      recipient: log.recipient,
      variant: log.variant,
      campaign: log.campaign,
      probability: probability,
      score: Math.round(probability * 100),
      predicted: probability >= 0.5,
    };
  });
  
  // Sort by probability
  predictions.sort((a, b) => b.probability - a.probability);
  
  // Output
  const header = 'recipient,variant,campaign,probability,score,predicted_response';
  const rows = predictions.map(p => [
    p.recipient,
    p.variant,
    p.campaign,
    p.probability.toFixed(3),
    p.score,
    p.predicted ? 'yes' : 'no',
  ].join(','));
  
  fs.writeFileSync(CONFIG.outputFile, [header, ...rows].join('\n'), 'utf8');
  
  console.log(`✅ Predictions generated → ${CONFIG.outputFile}`);
  console.log(`📊 Top 5 high-probability recipients:`);
  predictions.slice(0, 5).forEach((p, i) => {
    console.log(`  ${i + 1}. ${p.recipient.split('/').pop()} - ${p.score}% (${p.variant})`);
  });
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

if (require.main === module) {
  main();
}





#!/usr/bin/env node
/**
 * Analizador de Sentimiento en Respuestas
 * Clasifica respuestas como positivo/neutral/negativo
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses_raw.csv'),
  outputFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses_with_sentiment.csv'),
};

const POSITIVE_WORDS = [
  'interesado', 'sí', 'yes', 'genial', 'excelente', 'perfecto', 'me encanta', 'me gusta',
  'quiero', 'cuéntame más', 'envíame', 'seguro', 'buena idea', 'sounds good',
  'interested', 'great', 'excellent', 'perfect', 'love it', 'like it', 'sure',
];
const NEGATIVE_WORDS = [
  'no', 'no gracias', 'no thanks', 'no me interesa', 'not interested', 'caro', 'expensive',
  'ahora no', 'not now', 'ocupado', 'busy', 'cancelar', 'cancel', 'no más', 'no more',
  'no necesito', "don't need", 'demasiado', 'too much',
];

function analyzeSentiment(text) {
  if (!text || !text.trim()) return { sentiment: 'neutral', score: 0, confidence: 0 };
  
  const lower = text.toLowerCase();
  let positiveScore = 0;
  let negativeScore = 0;
  
  POSITIVE_WORDS.forEach(word => {
    if (lower.includes(word)) positiveScore++;
  });
  
  NEGATIVE_WORDS.forEach(word => {
    if (lower.includes(word)) negativeScore++;
  });
  
  // Indicadores adicionales
  if (lower.includes('!') || lower.includes('😊') || lower.includes('👍')) positiveScore += 0.5;
  if (lower.includes('😞') || lower.includes('👎')) negativeScore += 0.5;
  
  const totalScore = positiveScore - negativeScore;
  
  let sentiment = 'neutral';
  let confidence = 0.5;
  
  if (totalScore > 1) {
    sentiment = 'positive';
    confidence = Math.min(0.7 + (totalScore * 0.1), 0.95);
  } else if (totalScore < -1) {
    sentiment = 'negative';
    confidence = Math.min(0.7 + (Math.abs(totalScore) * 0.1), 0.95);
  } else {
    sentiment = 'neutral';
    confidence = 0.5 + (Math.abs(totalScore) * 0.1);
  }
  
  return {
    sentiment,
    score: totalScore,
    confidence: Math.min(confidence, 1.0),
  };
}

function main() {
  if (!fs.existsSync(CONFIG.responsesFile)) {
    console.warn('⚠️  responses_raw.csv not found');
    return;
  }
  
  const lines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  const textIndex = headers.findIndex(h => h.toLowerCase().includes('text') || h.toLowerCase().includes('response'));
  
  if (textIndex === -1) {
    console.error('❌ No response text column found');
    return;
  }
  
  const results = [];
  lines.slice(1).forEach((line, idx) => {
    const parts = line.split(',');
    const text = parts[textIndex]?.replace(/"/g, '') || '';
    const sentiment = analyzeSentiment(text);
    
    const row = [...parts];
    row.push(sentiment.sentiment);
    row.push(sentiment.score.toFixed(2));
    row.push(sentiment.confidence.toFixed(2));
    results.push(row);
  });
  
  const newHeaders = [...headers, 'sentiment', 'sentiment_score', 'sentiment_confidence'];
  const output = [newHeaders.join(','), ...results.map(r => r.join(','))].join('\n');
  
  fs.writeFileSync(CONFIG.outputFile, output, 'utf8');
  
  // Stats
  const stats = { positive: 0, negative: 0, neutral: 0 };
  results.forEach(r => {
    const sent = r[r.length - 3];
    stats[sent]++;
  });
  
  console.log(`✅ Sentiment analysis complete → ${CONFIG.outputFile}`);
  console.log(`📊 Distribution:`);
  console.log(`  Positive: ${stats.positive} (${((stats.positive / results.length) * 100).toFixed(1)}%)`);
  console.log(`  Neutral: ${stats.neutral} (${((stats.neutral / results.length) * 100).toFixed(1)}%)`);
  console.log(`  Negative: ${stats.negative} (${((stats.negative / results.length) * 100).toFixed(1)}%)`);
}

if (require.main === module) {
  main();
}





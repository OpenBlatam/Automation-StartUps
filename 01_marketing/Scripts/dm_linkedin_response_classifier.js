#!/usr/bin/env node
/**
 * Clasificador Inteligente de Respuestas
 * Categoriza respuestas automáticamente para routing
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses_raw.csv'),
  outputFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses_classified.csv'),
  rulesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_classification_rules.json'),
};

const DEFAULT_RULES = {
  positive: ['interesado', 'sí', 'yes', 'me gustaría', 'quiero', 'cuéntame más', 'envíame', 'sígueme'],
  objection_budget: ['caro', 'precio', 'costoso', 'expensive', 'budget', 'presupuesto', 'no tengo dinero'],
  objection_timing: ['ahora no', 'más adelante', 'not now', 'later', 'más tarde', 'busy', 'ocupado'],
  objection_need: ['no necesito', "don't need", 'no me interesa', "not interested", 'no gracias', 'no thanks'],
  objection_competitor: ['ya uso', 'already use', 'tengo algo similar', 'tengo otra herramienta'],
  question: ['qué', 'cuánto', 'cómo', 'what', 'how', 'cuándo', 'when', 'dónde', 'where', '?'],
  opt_out: ['stop', 'unsubscribe', 'no más', 'no more', 'no envíes', "don't send"],
};

function loadRules() {
  if (fs.existsSync(CONFIG.rulesFile)) {
    return JSON.parse(fs.readFileSync(CONFIG.rulesFile, 'utf8'));
  }
  return DEFAULT_RULES;
}

function classifyResponse(text, rules) {
  const lower = text.toLowerCase().trim();
  const categories = [];
  let confidence = 0;
  
  // Opt-out (prioritario)
  if (rules.opt_out.some(word => lower.includes(word))) {
    return { category: 'opt_out', confidence: 1.0, action: 'add_to_suppression' };
  }
  
  // Positive
  const positiveMatches = rules.positive.filter(word => lower.includes(word)).length;
  if (positiveMatches >= 2) {
    categories.push({ name: 'positive', score: 0.9 });
  } else if (positiveMatches === 1) {
    categories.push({ name: 'positive', score: 0.6 });
  }
  
  // Objections
  rules.objection_budget.forEach(word => {
    if (lower.includes(word)) {
      categories.push({ name: 'objection_budget', score: 0.8 });
    }
  });
  
  rules.objection_timing.forEach(word => {
    if (lower.includes(word)) {
      categories.push({ name: 'objection_timing', score: 0.8 });
    }
  });
  
  rules.objection_need.forEach(word => {
    if (lower.includes(word)) {
      categories.push({ name: 'objection_need', score: 0.9 });
    }
  });
  
  rules.objection_competitor.forEach(word => {
    if (lower.includes(word)) {
      categories.push({ name: 'objection_competitor', score: 0.7 });
    }
  });
  
  // Questions
  const questionMatches = rules.question.filter(word => lower.includes(word)).length;
  if (questionMatches >= 2 || lower.includes('?')) {
    categories.push({ name: 'question', score: 0.7 });
  }
  
  if (categories.length === 0) {
    return { category: 'neutral', confidence: 0.5, action: 'manual_review' };
  }
  
  // Ordenar por score
  categories.sort((a, b) => b.score - a.score);
  const primary = categories[0];
  
  const actions = {
    positive: 'send_next_step',
    objection_budget: 'handle_budget_objection',
    objection_timing: 'schedule_followup',
    objection_need: 'provide_value_first',
    objection_competitor: 'highlight_differentiators',
    question: 'answer_question',
    neutral: 'manual_review',
  };
  
  return {
    category: primary.name,
    confidence: primary.score,
    action: actions[primary.name] || 'manual_review',
    secondaryCategories: categories.slice(1).map(c => c.name),
  };
}

function parseResponses() {
  if (!fs.existsSync(CONFIG.responsesFile)) {
    console.warn('⚠️  responses_raw.csv not found, creating template');
    const template = 'recipient,response_text,timestamp\n';
    fs.writeFileSync(CONFIG.responsesFile, template, 'utf8');
    return [];
  }
  
  const lines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
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

function main() {
  const rules = loadRules();
  const responses = parseResponses();
  
  if (!responses.length) {
    console.log('✅ Template created. Add responses to responses_raw.csv and run again.');
    return;
  }
  
  const classified = responses.map(r => {
    const classification = classifyResponse(r.response_text || '', rules);
    return {
      ...r,
      category: classification.category,
      confidence: classification.confidence,
      action: classification.action,
      secondary_categories: (classification.secondaryCategories || []).join(';'),
    };
  });
  
  const header = 'recipient,response_text,timestamp,category,confidence,action,secondary_categories';
  const rows = classified.map(c => [
    c.recipient,
    c.response_text,
    c.timestamp,
    c.category,
    c.confidence,
    c.action,
    c.secondary_categories,
  ].join(','));
  
  fs.writeFileSync(CONFIG.outputFile, [header, ...rows].join('\n'), 'utf8');
  
  // Stats
  const stats = {};
  classified.forEach(c => {
    stats[c.category] = (stats[c.category] || 0) + 1;
  });
  
  console.log(`✅ Classified ${classified.length} responses → ${CONFIG.outputFile}`);
  console.log('\n📊 Distribution:');
  Object.entries(stats).forEach(([cat, count]) => {
    console.log(`  ${cat}: ${count} (${((count / classified.length) * 100).toFixed(1)}%)`);
  });
  
  // Alerts
  const optOuts = classified.filter(c => c.category === 'opt_out').length;
  if (optOuts > 0) {
    console.log(`\n⚠️  ${optOuts} opt-out detected → add to suppression list`);
  }
}

if (require.main === module) {
  main();
}





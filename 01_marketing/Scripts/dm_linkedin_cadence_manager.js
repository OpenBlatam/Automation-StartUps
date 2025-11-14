#!/usr/bin/env node
/**
 * Gestor de Cadencias Automáticas
 * Calcula timing óptimo para follow-ups basado en reglas
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  cadenceFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_cadences.json'),
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  outputFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_next_followups.csv'),
};

const DEFAULT_CADENCE = {
  warm: { d0: 'initial', d2: 'followup1', d5: 'followup2', d10: 'final' },
  cold: { d0: 'initial', d3: 'followup1', d7: 'followup2', d14: 'followup3', d21: 'final' },
  objection: { d0: 'address', d5: 'value_add', d12: 'alternative' },
};

function parseLogs() {
  if (!fs.existsSync(CONFIG.logsFile)) return [];
  const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  lines.shift();
  return lines.map(l => {
    const parts = l.split(',');
    return {
      timestamp: parts[0],
      recipient: parts[1]?.replace(/"/g, ''),
      variant: parts[2]?.replace(/"/g, ''),
      campaign: parts[3]?.replace(/"/g, ''),
      status: parts[4]?.replace(/"/g, ''),
    };
  });
}

function loadCadences() {
  if (fs.existsSync(CONFIG.cadenceFile)) {
    return JSON.parse(fs.readFileSync(CONFIG.cadenceFile, 'utf8'));
  }
  return DEFAULT_CADENCE;
}

function calculateNextFollowup(logEntry, cadences, now = new Date()) {
  const sentDate = new Date(logEntry.timestamp);
  const daysSince = Math.floor((now - sentDate) / (1000 * 60 * 60 * 24));
  
  let cadenceType = 'cold';
  if (logEntry.variant?.includes('warm') || logEntry.variant?.includes('engagement')) {
    cadenceType = 'warm';
  }
  
  const cadence = cadences[cadenceType] || cadences.cold;
  const steps = Object.entries(cadence).sort(([a], [b]) => {
    const dayA = parseInt(a.replace('d', '')) || 0;
    const dayB = parseInt(b.replace('d', '')) || 0;
    return dayA - dayB;
  });
  
  for (const [dayKey, stepType] of steps) {
    const targetDay = parseInt(dayKey.replace('d', '')) || 0;
    if (daysSince >= targetDay) {
      // Ya pasó este step, busca el siguiente
      continue;
    }
    return {
      recipient: logEntry.recipient,
      campaign: logEntry.campaign,
      currentStep: stepType,
      nextStep: stepType,
      nextDay: targetDay,
      daysUntilNext: targetDay - daysSince,
      nextDate: new Date(sentDate.getTime() + targetDay * 24 * 60 * 60 * 1000),
      status: logEntry.status,
    };
  }
  
  // Ya completó todos los pasos
  return {
    recipient: logEntry.recipient,
    campaign: logEntry.campaign,
    currentStep: 'completed',
    nextStep: null,
    daysUntilNext: null,
    status: 'COMPLETED',
  };
}

function main() {
  const logs = parseLogs();
  const cadences = loadCadences();
  const sent = logs.filter(l => l.status === 'SENT');
  
  const followups = sent
    .map(l => calculateNextFollowup(l, cadences))
    .filter(f => f.nextStep && f.nextStep !== 'completed')
    .sort((a, b) => (a.daysUntilNext || 0) - (b.daysUntilNext || 0));
  
  const header = 'recipient,campaign,current_step,next_step,days_until_next,next_date,status';
  const rows = followups.map(f => [
    f.recipient,
    f.campaign,
    f.currentStep,
    f.nextStep,
    f.daysUntilNext,
    f.nextDate.toISOString().split('T')[0],
    f.status,
  ].join(','));
  
  fs.writeFileSync(CONFIG.outputFile, [header, ...rows].join('\n'), 'utf8');
  console.log(`✅ Generated ${followups.length} follow-ups → ${CONFIG.outputFile}`);
  console.log(`📅 Next follow-ups: ${followups.slice(0, 5).map(f => `${f.recipient.split('/').pop()} (${f.daysUntilNext}d)`).join(', ')}`);
}

if (require.main === module) {
  main();
}





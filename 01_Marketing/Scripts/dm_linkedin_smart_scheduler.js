#!/usr/bin/env node
/**
 * Scheduler Inteligente
 * Programa envíos basado en reglas de timing óptimo, timezone, y hábitos de respuesta
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  recipientsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_recipients.csv'),
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  outputFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_scheduled_sends.csv'),
  businessHours: {
    start: 9,  // 9 AM
    end: 17,   // 5 PM
  },
  optimalDays: [1, 2, 3, 4], // Mon-Thu
  optimalHours: [9, 10, 14, 15], // 9AM, 10AM, 2PM, 3PM
};

function parseRecipients() {
  if (!fs.existsSync(CONFIG.recipientsFile)) return [];
  const lines = fs.readFileSync(CONFIG.recipientsFile, 'utf8').split('\n').filter(Boolean);
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

function getBestTimeForRecipient(recipient, historicalLogs, historicalResponses) {
  // Si hay historial de respuestas rápidas, usar ese timing
  const recipientLogs = historicalLogs.filter(l => l.recipient === recipient.profileUrl);
  const recipientResponses = historicalResponses.filter(r => r.recipient === recipient.profileUrl);
  
  // Si respondió rápido (dentro de 2 horas), usar ese día/hora
  const quickResponses = recipientResponses.filter(r => {
    const log = recipientLogs.find(l => l.recipient === r.recipient && l.status === 'SENT');
    if (!log || !log.timestamp) return false;
    const sentTime = new Date(log.timestamp);
    const responseTime = new Date(r.timestamp || Date.now());
    const hoursDiff = (responseTime - sentTime) / (1000 * 60 * 60);
    return hoursDiff <= 2 && hoursDiff > 0;
  });
  
  if (quickResponses.length > 0) {
    const bestTime = new Date(quickResponses[0].timestamp);
    return {
      hour: bestTime.getHours(),
      dayOfWeek: bestTime.getDay(),
      reason: 'historical_quick_response',
    };
  }
  
  // Default: optimal timing basado en industria/seniority
  let hour = CONFIG.optimalHours[0];
  let dayOfWeek = CONFIG.optimalDays[0];
  
  // Ajustes por seniority
  if (recipient.seniority === 'executive' || recipient.seniority === 'c-level') {
    hour = 8; // Más temprano para executives
  } else if (recipient.seniority === 'junior') {
    hour = 10; // Más tarde para junior
  }
  
  // Ajustes por timezone (simplificado)
  const timezone = recipient.locale || 'es-MX';
  if (timezone.includes('US') || timezone.includes('en-US')) {
    hour = (hour + 2) % 24; // Ajuste aproximado
  }
  
  return {
    hour,
    dayOfWeek,
    reason: 'optimal_timing',
  };
}

function calculateNextSendTime(bestTime) {
  const now = new Date();
  const nextSend = new Date();
  
  // Establecer día
  const daysUntilOptimal = (bestTime.dayOfWeek - now.getDay() + 7) % 7;
  if (daysUntilOptimal === 0 && now.getHours() >= bestTime.hour) {
    // Si es hoy pero ya pasó la hora, programar para el próximo día óptimo
    nextSend.setDate(now.getDate() + CONFIG.optimalDays.find(d => d > now.getDay()) || CONFIG.optimalDays[0] + 7);
  } else {
    nextSend.setDate(now.getDate() + daysUntilOptimal);
  }
  
  // Establecer hora
  nextSend.setHours(bestTime.hour, 0, 0, 0);
  
  // Si ya pasó hoy, ajustar a mañana
  if (nextSend <= now) {
    nextSend.setDate(nextSend.getDate() + 1);
  }
  
  return nextSend;
}

function main() {
  const recipients = parseRecipients();
  
  // Load historical data
  const logs = [];
  const responses = [];
  if (fs.existsSync(CONFIG.logsFile)) {
    const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
    const headers = lines[0]?.split(',') || [];
    logs.push(...lines.slice(1).map(l => {
      const parts = l.split(',');
      const obj = {};
      headers.forEach((h, i) => {
        obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
      });
      return obj;
    }));
  }
  
  if (fs.existsSync(CONFIG.responsesFile)) {
    const lines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
    const headers = lines[0]?.split(',') || [];
    responses.push(...lines.slice(1).map(l => {
      const parts = l.split(',');
      const obj = {};
      headers.forEach((h, i) => {
        obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
      });
      return obj;
    }));
  }
  
  // Generate schedule
  const schedule = recipients.map(recipient => {
    const bestTime = getBestTimeForRecipient(recipient, logs, responses);
    const nextSend = calculateNextSendTime(bestTime);
    
    return {
      recipient: recipient.profileUrl || recipient.profileurl || '',
      name: recipient.name || '',
      company: recipient.company || '',
      nextSendTime: nextSend.toISOString(),
      nextSendDate: nextSend.toISOString().split('T')[0],
      nextSendHour: `${String(nextSend.getHours()).padStart(2, '0')}:00`,
      timezone: recipient.locale || 'es-MX',
      reason: bestTime.reason,
      priority: bestTime.reason === 'historical_quick_response' ? 'high' : 'normal',
    };
  }).filter(s => s.recipient); // Remove empty
  
  // Sort by priority and time
  schedule.sort((a, b) => {
    if (a.priority !== b.priority) {
      return a.priority === 'high' ? -1 : 1;
    }
    return new Date(a.nextSendTime) - new Date(b.nextSendTime);
  });
  
  // Export
  const header = 'recipient,name,company,next_send_time,next_send_date,next_send_hour,timezone,reason,priority';
  const rows = schedule.map(s => [
    s.recipient,
    s.name,
    s.company,
    s.nextSendTime,
    s.nextSendDate,
    s.nextSendHour,
    s.timezone,
    s.reason,
    s.priority,
  ].join(','));
  
  fs.writeFileSync(CONFIG.outputFile, [header, ...rows].join('\n'), 'utf8');
  
  console.log(`✅ Schedule generated: ${schedule.length} recipients`);
  console.log(`📅 Next sends:`);
  schedule.slice(0, 5).forEach((s, i) => {
    console.log(`  ${i + 1}. ${s.name || s.recipient.split('/').pop()} - ${s.nextSendDate} ${s.nextSendHour} (${s.priority})`);
  });
}

if (require.main === module) {
  main();
}





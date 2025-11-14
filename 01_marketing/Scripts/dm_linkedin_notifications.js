#!/usr/bin/env node
/**
 * Sistema de Notificaciones Avanzado
 * Envía alertas via Slack, Email, y SMS para eventos importantes
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  slackWebhook: process.env.SLACK_WEBHOOK || '',
  emailSMTP: process.env.EMAIL_SMTP || '',
  emailFrom: process.env.EMAIL_FROM || '',
  emailTo: process.env.EMAIL_TO || '',
  smsAPI: process.env.SMS_API || '',
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  checkInterval: 300000, // 5 minutos
};

const ALERT_RULES = {
  highErrorRate: { threshold: 0.15, message: '⚠️ High error rate detected (>15%)' },
  lowResponseRate: { threshold: 0.10, message: '📉 Response rate below 10%' },
  optOutSpike: { threshold: 5, message: '🛑 Multiple opt-outs detected (>5 in period)' },
  conversionDrop: { threshold: 0.03, message: '📊 Conversion rate dropped below 3%' },
  successMilestone: { threshold: 100, message: '🎉 Milestone: 100+ successful sends!' },
};

async function sendSlack(message, level = 'info') {
  if (!CONFIG.slackWebhook) return false;
  
  const colors = {
    success: '#28a745',
    warning: '#ffc107',
    error: '#dc3545',
    info: '#007bff',
  };
  
  const payload = {
    text: message,
    attachments: [{
      color: colors[level] || colors.info,
      text: message,
      footer: 'LinkedIn DMs System',
      ts: Math.floor(Date.now() / 1000),
    }],
  };
  
  return new Promise((resolve) => {
    const url = new URL(CONFIG.slackWebhook);
    const data = JSON.stringify(payload);
    
    const options = {
      hostname: url.hostname,
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length,
      },
    };
    
    const req = http.request(options, (res) => {
      resolve(res.statusCode === 200);
    });
    
    req.on('error', () => resolve(false));
    req.write(data);
    req.end();
  });
}

async function sendEmail(subject, body) {
  // Placeholder - integra con servicio de email (SendGrid, SES, etc.)
  console.log(`📧 Email would be sent to ${CONFIG.emailTo}: ${subject}`);
  return true;
}

function checkAlerts() {
  if (!fs.existsSync(CONFIG.logsFile)) {
    console.warn('⚠️  Logs file not found');
    return [];
  }
  
  const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  const logs = lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  });
  
  const alerts = [];
  const recent = logs.slice(-100); // Últimos 100 logs
  const sent = recent.filter(l => l.status === 'SENT');
  const errors = recent.filter(l => l.status === 'ERROR');
  
  // Error rate
  if (recent.length > 0) {
    const errorRate = errors.length / recent.length;
    if (errorRate > ALERT_RULES.highErrorRate.threshold) {
      alerts.push({
        level: 'error',
        message: ALERT_RULES.highErrorRate.message + ` (${(errorRate * 100).toFixed(1)}%)`,
        action: 'Check API connectivity and rate limits',
      });
    }
  }
  
  // Response rate (si hay responses file)
  if (fs.existsSync(CONFIG.responsesFile)) {
    const responseLines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
    responseLines.shift();
    const responses = responseLines.filter(l => {
      const parts = l.split(',');
      return parts[1] === 'true' || parts[1] === '1';
    }).length;
    
    if (sent.length > 10) {
      const responseRate = responses / sent.length;
      if (responseRate < ALERT_RULES.lowResponseRate.threshold) {
        alerts.push({
          level: 'warning',
          message: ALERT_RULES.lowResponseRate.message + ` (${(responseRate * 100).toFixed(1)}%)`,
          action: 'Review message quality and targeting',
        });
      }
    }
  }
  
  // Opt-outs
  if (fs.existsSync(CONFIG.responsesFile)) {
    const responseLines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
    const optOuts = responseLines.filter(l => {
      const text = l.toLowerCase();
      return text.includes('stop') || text.includes('opt-out') || text.includes('unsubscribe');
    }).length;
    
    if (optOuts > ALERT_RULES.optOutSpike.threshold) {
      alerts.push({
        level: 'warning',
        message: ALERT_RULES.optOutSpike.message + ` (${optOuts} detected)`,
        action: 'Review messaging frequency and compliance',
      });
    }
  }
  
  // Success milestone
  const totalSent = logs.filter(l => l.status === 'SENT').length;
  if (totalSent > 0 && totalSent % ALERT_RULES.successMilestone.threshold === 0) {
    alerts.push({
      level: 'success',
      message: ALERT_RULES.successMilestone.message.replace('100', totalSent.toString()),
      action: 'Celebrate and continue scaling',
    });
  }
  
  return alerts;
}

async function main() {
  const mode = process.argv[2] || 'check'; // check, monitor
  
  if (mode === 'check') {
    const alerts = checkAlerts();
    
    if (alerts.length === 0) {
      console.log('✅ No alerts detected');
      return;
    }
    
    console.log(`📢 Found ${alerts.length} alert(s):\n`);
    
    for (const alert of alerts) {
      console.log(`[${alert.level.toUpperCase()}] ${alert.message}`);
      console.log(`   → ${alert.action}\n`);
      
      // Send notifications
      if (CONFIG.slackWebhook) {
        await sendSlack(`${alert.message}\n${alert.action}`, alert.level);
      }
      if (CONFIG.emailTo) {
        await sendEmail(`LinkedIn DMs Alert: ${alert.message}`, alert.action);
      }
    }
  } else if (mode === 'monitor') {
    console.log('🔔 Starting monitoring mode (checking every 5 minutes)...');
    console.log('Press Ctrl+C to stop\n');
    
    setInterval(async () => {
      const alerts = checkAlerts();
      if (alerts.length > 0) {
        for (const alert of alerts) {
          console.log(`[${new Date().toLocaleTimeString()}] ${alert.message}`);
          if (CONFIG.slackWebhook) {
            await sendSlack(`${alert.message}\n${alert.action}`, alert.level);
          }
        }
      }
    }, CONFIG.checkInterval);
  }
}

if (require.main === module) {
  main().catch(console.error);
}





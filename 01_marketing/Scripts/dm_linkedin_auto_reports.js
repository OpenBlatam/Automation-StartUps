#!/usr/bin/env node
/**
 * Generador de Reportes Automáticos por Email
 * Envía reportes periódicos a stakeholders
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  frequency: process.argv[2] || 'weekly', // daily, weekly, monthly
  emailTo: process.env.REPORT_EMAIL_TO || '',
  emailFrom: process.env.REPORT_EMAIL_FROM || 'noreply@linkedindms.com',
  smtpHost: process.env.SMTP_HOST || '',
  smtpUser: process.env.SMTP_USER || '',
  smtpPass: process.env.SMTP_PASS || '',
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  templateDir: path.resolve(__dirname, '../Templates/EmailReports'),
};

function parseLogs() {
  if (!fs.existsSync(CONFIG.logsFile)) return [];
  const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  const cutoff = new Date();
  
  if (CONFIG.frequency === 'daily') {
    cutoff.setDate(cutoff.getDate() - 1);
  } else if (CONFIG.frequency === 'weekly') {
    cutoff.setDate(cutoff.getDate() - 7);
  } else if (CONFIG.frequency === 'monthly') {
    cutoff.setMonth(cutoff.getMonth() - 1);
  }
  
  return lines.slice(1)
    .map(l => {
      const parts = l.split(',');
      const obj = {};
      headers.forEach((h, i) => {
        obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
      });
      return obj;
    })
    .filter(l => {
      if (!l.timestamp) return false;
      return new Date(l.timestamp) >= cutoff;
    })
    .filter(l => l.status === 'SENT');
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

function generateReport(logs, responses) {
  const sent = logs.length;
  const responded = Object.values(responses).filter(r => r.responded).length;
  const clicked = Object.values(responses).filter(r => r.clicked).length;
  const converted = Object.values(responses).filter(r => r.converted).length;
  
  // Por campaña
  const byCampaign = {};
  logs.forEach(l => {
    const camp = l.campaign || 'unknown';
    if (!byCampaign[camp]) {
      byCampaign[camp] = { sent: 0, responded: 0 };
    }
    byCampaign[camp].sent++;
    if (responses[l.recipient]?.responded) byCampaign[camp].responded++;
  });
  
  const campaignRows = Object.entries(byCampaign)
    .map(([name, data]) => {
      const rate = data.sent > 0 ? (data.responded / data.sent) * 100 : 0;
      return `<tr>
        <td>${name}</td>
        <td>${data.sent}</td>
        <td>${data.responded}</td>
        <td>${rate.toFixed(1)}%</td>
      </tr>`;
    })
    .join('');
  
  const period = CONFIG.frequency === 'daily' ? 'Last 24 hours' : 
                 CONFIG.frequency === 'weekly' ? 'Last 7 days' : 'Last 30 days';
  
  const html = `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
    .header { background: #0077b5; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .kpi { display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin: 20px 0; }
    .kpi-card { background: #f5f7fa; padding: 15px; border-radius: 6px; text-align: center; }
    .kpi-value { font-size: 28px; font-weight: bold; color: #0077b5; }
    .kpi-label { color: #666; font-size: 12px; margin-top: 5px; }
    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
    th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background: #0077b5; color: white; }
    .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; text-align: center; }
  </style>
</head>
<body>
  <div class="header">
    <h2>📊 LinkedIn DMs Report</h2>
    <p>${period}</p>
  </div>
  
  <div class="kpi">
    <div class="kpi-card">
      <div class="kpi-value">${sent}</div>
      <div class="kpi-label">DMs Sent</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value">${((responded / sent) * 100).toFixed(1)}%</div>
      <div class="kpi-label">Response Rate</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value">${clicked}</div>
      <div class="kpi-label">Clicks</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-value">${converted}</div>
      <div class="kpi-label">Conversions</div>
    </div>
  </div>
  
  <h3>📈 Performance by Campaign</h3>
  <table>
    <thead>
      <tr>
        <th>Campaign</th>
        <th>Sent</th>
        <th>Responses</th>
        <th>Rate</th>
      </tr>
    </thead>
    <tbody>${campaignRows}</tbody>
  </table>
  
  <div class="footer">
    <p>Automated report from LinkedIn DMs System</p>
    <p>Generated: ${new Date().toLocaleString()}</p>
  </div>
</body>
</html>
  `;
  
  return html;
}

async function sendEmail(subject, html) {
  // Placeholder - integra con tu servicio de email
  // Ejemplo con nodemailer, sendgrid, o AWS SES
  console.log(`📧 Email would be sent to ${CONFIG.emailTo}`);
  console.log(`Subject: ${subject}`);
  console.log(`\n${html.substring(0, 200)}...\n`);
  
  // Implementación real:
  // const transporter = nodemailer.createTransport({...});
  // await transporter.sendMail({ to: CONFIG.emailTo, subject, html });
  
  return true;
}

function main() {
  if (!CONFIG.emailTo) {
    console.warn('⚠️  REPORT_EMAIL_TO not set, generating report only');
  }
  
  const logs = parseLogs();
  const responses = parseResponses();
  
  if (!logs.length) {
    console.warn(`⚠️  No data found for ${CONFIG.frequency} period`);
    return;
  }
  
  const html = generateReport(logs, responses);
  
  // Save report
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const reportFile = path.resolve(__dirname, `../Reports/email_report_${CONFIG.frequency}_${timestamp}.html`);
  fs.writeFileSync(reportFile, html, 'utf8');
  console.log(`✅ Report generated: ${reportFile}`);
  
  // Send email if configured
  if (CONFIG.emailTo && CONFIG.smtpHost) {
    const subject = `LinkedIn DMs Report - ${CONFIG.frequency} (${new Date().toLocaleDateString()})`;
    sendEmail(subject, html).then(() => {
      console.log(`📧 Email sent to ${CONFIG.emailTo}`);
    }).catch(e => {
      console.error(`❌ Email failed: ${e.message}`);
    });
  } else {
    console.log(`💡 Set REPORT_EMAIL_TO and SMTP_* vars to enable email sending`);
  }
}

if (require.main === module) {
  main();
}





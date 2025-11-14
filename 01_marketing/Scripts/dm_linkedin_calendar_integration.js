#!/usr/bin/env node
/**
 * Integración con Calendarios (Google Calendar, Outlook)
 * Programa eventos automáticos para follow-ups y reuniones
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG = {
  followupsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_next_followups.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  calendarType: process.env.CALENDAR_TYPE || 'google', // google, outlook, ical
  outputDir: path.resolve(__dirname, '../Calendars'),
};

function ensureOutputDir() {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
}

function parseFollowups() {
  if (!fs.existsSync(CONFIG.followupsFile)) {
    console.warn('⚠️  Run cadence_manager first to generate follow-ups');
    return [];
  }
  
  const lines = fs.readFileSync(CONFIG.followupsFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  }).filter(f => f.days_until_next && parseInt(f.days_until_next) <= 3); // Solo próximos 3 días
}

function generateGoogleCalendar(events) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(CONFIG.outputDir, `linkedin_followups_${timestamp}.csv`);
  
  // Google Calendar CSV format
  const header = 'Subject,Start Date,Start Time,End Date,End Time,Description';
  const rows = events.map(e => {
    const date = e.next_send_date || new Date().toISOString().split('T')[0];
    const time = e.next_send_hour || '09:00';
    const name = e.name || e.recipient.split('/').pop();
    
    return [
      `DM Follow-up: ${name}`,
      date,
      time,
      date,
      time.split(':')[0] + ':30', // 30 min duration
      `Follow-up DM for ${name}\nCampaign: ${e.campaign || 'N/A'}\nReason: ${e.reason || 'Scheduled follow-up'}`,
    ].join(',');
  });
  
  fs.writeFileSync(outputFile, [header, ...rows].join('\n'), 'utf8');
  console.log(`✅ Google Calendar CSV: ${outputFile}`);
  console.log(`📅 Import: Open Google Calendar → Import → Select file`);
  return outputFile;
}

function generateICal(events) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(CONFIG.outputDir, `linkedin_followups_${timestamp}.ics`);
  
  let ical = 'BEGIN:VCALENDAR\n';
  ical += 'VERSION:2.0\n';
  ical += 'PRODID:-//LinkedIn DMs//Follow-ups//EN\n';
  ical += 'CALSCALE:GREGORIAN\n';
  
  events.forEach(e => {
    const date = e.next_send_date || new Date().toISOString().split('T')[0];
    const [hour, minute = '00'] = (e.next_send_hour || '09:00').split(':');
    const dtStart = new Date(`${date}T${hour.padStart(2, '0')}:${minute}:00`);
    const dtEnd = new Date(dtStart.getTime() + 30 * 60 * 1000); // 30 min
    
    ical += 'BEGIN:VEVENT\n';
    ical += `UID:${Date.now()}-${Math.random().toString(36).substr(2, 9)}\n`;
    ical += `DTSTAMP:${new Date().toISOString().replace(/[-:]/g, '').split('.')[0]}Z\n`;
    ical += `DTSTART:${dtStart.toISOString().replace(/[-:]/g, '').split('.')[0]}Z\n`;
    ical += `DTEND:${dtEnd.toISOString().replace(/[-:]/g, '').split('.')[0]}Z\n`;
    ical += `SUMMARY:DM Follow-up: ${e.name || e.recipient.split('/').pop()}\n`;
    ical += `DESCRIPTION:Follow-up DM\\nCampaign: ${e.campaign || 'N/A'}\\nReason: ${e.reason || 'Scheduled'}\n`;
    ical += `STATUS:CONFIRMED\n`;
    ical += 'END:VEVENT\n';
  });
  
  ical += 'END:VCALENDAR\n';
  
  fs.writeFileSync(outputFile, ical, 'utf8');
  console.log(`✅ iCal file: ${outputFile}`);
  console.log(`📅 Import: Double-click to add to your calendar app`);
  return outputFile;
}

function generateOutlook(events) {
  // Outlook acepta CSV similar a Google
  return generateGoogleCalendar(events);
}

function main() {
  const followups = parseFollowups();
  
  if (followups.length === 0) {
    console.warn('⚠️  No upcoming follow-ups found');
    console.log('💡 Run: node Scripts/dm_linkedin_cadence_manager.js');
    return;
  }
  
  ensureOutputDir();
  
  console.log(`📅 Found ${followups.length} upcoming follow-ups\n`);
  
  switch (CONFIG.calendarType) {
    case 'google':
      generateGoogleCalendar(followups);
      break;
    case 'ical':
      generateICal(followups);
      break;
    case 'outlook':
      generateOutlook(followups);
      break;
    default:
      console.error(`❌ Unknown calendar type: ${CONFIG.calendarType}`);
      console.log('Available: google, ical, outlook');
      process.exit(1);
  }
  
  console.log(`\n✅ Calendar integration complete`);
}

if (require.main === module) {
  main();
}





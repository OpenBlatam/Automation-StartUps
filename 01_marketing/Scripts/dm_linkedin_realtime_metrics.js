#!/usr/bin/env node
/**
 * Métricas en Tiempo Real
 * Monitorea performance en vivo y actualiza métricas cada X segundos
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  updateInterval: parseInt(process.env.UPDATE_INTERVAL) || 5000, // 5 segundos
  watchMode: process.argv.includes('--watch'),
};

let lastProcessedLine = 0;

function getCurrentStats() {
  if (!fs.existsSync(CONFIG.logsFile)) {
    return { error: 'Logs file not found' };
  }
  
  const allLines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
  const headers = allLines[0]?.split(',') || [];
  const logs = allLines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  });
  
  // New logs since last check
  const newLogs = logs.slice(lastProcessedLine);
  lastProcessedLine = logs.length;
  
  const sent = logs.filter(l => l.status === 'SENT');
  const recentSent = sent.slice(-100); // Últimos 100
  
  // Parse responses
  const responses = {};
  if (fs.existsSync(CONFIG.responsesFile)) {
    const responseLines = fs.readFileSync(CONFIG.responsesFile, 'utf8').split('\n').filter(Boolean);
    responseLines.shift();
    responseLines.forEach(l => {
      const [recipient, responded] = l.split(',');
      if (recipient) {
        responses[recipient.trim()] = {
          responded: responded === 'true' || responded === '1',
        };
      }
    });
  }
  
  const responded = sent.filter(l => responses[l.recipient]?.responded).length;
  const recentResponded = recentSent.filter(l => responses[l.recipient]?.responded).length;
  
  // Rate calculations
  const responseRate = sent.length > 0 ? (responded / sent.length) * 100 : 0;
  const recentResponseRate = recentSent.length > 0 ? (recentResponded / recentSent.length) * 100 : 0;
  
  // Today's stats Stochastic
  const today = new Date().toISOString().split('T')[0];
  const todaySent = sent.filter(l => l.timestamp && l.timestamp.startsWith(today)).length;
  const todayResponded = sent.filter(l => 
    l.timestamp && l.timestamp.startsWith(today) && responses[l.recipient]?.responded
  ).length;
  
  return {
    totalSent: sent.length,
    totalResponded: responded,
    responseRate: responseRate.toFixed(2),
    recentResponseRate: recentResponseRate.toFixed(2),
    todaySent,
    todayResponded,
    todayResponseRate: todaySent > 0 ? ((todayResponded / todaySent) * 100).toFixed(2) : 0,
    newLogs: newLogs.length,
    timestamp: new Date().toISOString(),
  };
}

function displayStats(stats) {
  // Clear console (Unix/Linux/Mac)
  process.stdout.write('\x1Bc');
  
  console.log('📊 LinkedIn DMs - Real-Time Metrics');
  console.log('═'.repeat(50));
  console.log(`⏰ Last Update: ${new Date().toLocaleTimeString()}\n`);
  
  console.log('📈 Overall Performance:');
  console.log(`  Total Sent:     ${stats.totalSent}`);
  console.log(`  Total Responses: ${stats.totalResponded}`);
  console.log(`  Response Rate:   ${stats.responseRate}%\n`);
  
  console.log('🔥 Recent (Last 100):');
  console.log(`  Response Rate:   ${stats.recentResponseRate}%\n`);
  
  console.log('📅 Today:');
  console.log(`  Sent:            ${stats.todaySent}`);
  console.log(`  Responses:       ${stats.todayResponded}`);
  console.log(`  Response Rate:   ${stats.todayResponseRate}%\n`);
  
  if (stats.newLogs > 0) {
    console.log(`✨ New activity: ${stats.newLogs} new logs since last check\n`);
  }
  
  console.log('─'.repeat(50));
  console.log('Press Ctrl+C to stop');
}

function main() {
  if (CONFIG.watchMode) {
    console.log('👀 Real-time monitoring started...\n');
    
    const interval = setInterval(() => {
      const stats = getCurrentStats();
      if (!stats.error) {
        displayStats(stats);
      }
    }, CONFIG.updateInterval);
    
    process.on('SIGINT', () => {
      clearInterval(interval);
      console.log('\n👋 Monitoring stopped');
      process.exit(0);
    });
  } else {
    // Single check
    const stats = getCurrentStats();
    if (stats.error) {
      console.error('❌', stats.error);
      return;
    }
    
    displayStats(stats);
  }
}

if (require.main === module) {
  main();
}





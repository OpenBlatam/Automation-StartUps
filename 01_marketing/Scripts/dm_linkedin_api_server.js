#!/usr/bin/env node
/**
 * API REST para LinkedIn DMs System
 * Endpoints para integraciones externas
 */
const http = require('http');
const url = require('url');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG = {
  port: process.env.API_PORT || 8080,
  apiKey: process.env.API_KEY || '',
};

const DATA_DIR = path.resolve(__dirname, '../Data_Files');

function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

function readCSV(csvFile) {
  if (!fs.existsSync(csvFile)) return [];
  const content = fs.readFileSync(csvFile, 'utf8');
  const lines = content.split('\n').filter(Boolean);
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

function handleStats(req, res) {
  const logs = readCSV(path.join(DATA_DIR, 'dm_linkedin_logs.csv'));
  const sent = logs.filter(l => l.status === 'SENT').length;
  const errors = logs.filter(l => l.status === 'ERROR').length;
  
  sendJSON(res, 200, {
    total: logs.length,
    sent,
    errors,
    successRate: logs.length > 0 ? ((sent / logs.length) * 100).toFixed(1) : 0,
  });
}

function handleRecipients(req, res) {
  const recipients = readCSV(path.join(DATA_DIR, 'dm_linkedin_recipients.csv'));
  sendJSON(res, 200, { count: recipients.length, recipients });
}

function handleVariants(req, res) {
  try {
    const variantsPath = path.join(DATA_DIR, 'dm_linkedin_variants_localized_completo.json');
    if (!fs.existsSync(variantsPath)) {
      sendJSON(res, 404, { error: 'Variants file not found' });
      return;
    }
    const variants = JSON.parse(fs.readFileSync(variantsPath, 'utf8'));
    sendJSON(res, 200, { count: variants.length, variants });
  } catch (e) {
    sendJSON(res, 500, { error: e.message });
  }
}

function handlePredictions(req, res) {
  try {
    execSync(`node "${path.join(__dirname, 'dm_linkedin_response_predictor.js')}"`, {
      encoding: 'utf8',
      stdio: 'pipe',
    });
    
    const predictions = readCSV(path.join(DATA_DIR, 'dm_linkedin_predictions.csv'));
    sendJSON(res, 200, { count: predictions.length, predictions });
  } catch (e) {
    sendJSON(res, 500, { error: e.message });
  }
}

function handleDashboard(req, res) {
  try {
    execSync(`node "${path.join(__dirname, 'dm_linkedin_dashboard_generator.js')}"`, {
      encoding: 'utf8',
      stdio: 'pipe',
    });
    
    const dashboardPath = path.resolve(__dirname, '../Reports/dm_linkedin_dashboard.html');
    if (fs.existsSync(dashboardPath)) {
      const html = fs.readFileSync(dashboardPath, 'utf8');
      res.writeHead(200, { 'Content-Type': 'text/html' });
      res.end(html);
    } else {
      sendJSON(res, 404, { error: 'Dashboard not generated' });
    }
  } catch (e) {
    sendJSON(res, 500, { error: e.message });
  }
}

function handleHealth(req, res) {
  try {
    execSync(`node "${path.join(__dirname, 'dm_linkedin_health_check.js')}"`, {
      encoding: 'utf8',
      stdio: 'pipe',
    });
    sendJSON(res, 200, { status: 'ok', timestamp: new Date().toISOString() });
  } catch (e) {
    sendJSON(res, 500, { status: 'error', error: e.message });
  }
}

function handleRequest(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }
  
  // API Key validation
  if (CONFIG.apiKey) {
    const authHeader = req.headers.authorization;
    if (!authHeader || authHeader !== `Bearer ${CONFIG.apiKey}`) {
      sendJSON(res, 401, { error: 'Unauthorized' });
      return;
    }
  }
  
  const parsedUrl = url.parse(req.url, true);
  const pathname = parsedUrl.pathname;
  
  if (pathname === '/api/stats') {
    handleStats(req, res);
  } else if (pathname === '/api/recipients') {
    handleRecipients(req, res);
  } else if (pathname === '/api/variants') {
    handleVariants(req, res);
  } else if (pathname === '/api/predictions') {
    handlePredictions(req, res);
  } else if (pathname === '/api/dashboard') {
    handleDashboard(req, res);
  } else if (pathname === '/api/health') {
    handleHealth(req, res);
  } else {
    sendJSON(res, 404, { error: 'Not found', available: ['/api/stats', '/api/recipients', '/api/variants', '/api/predictions', '/api/dashboard', '/api/health'] });
  }
}

function main() {
  const server = http.createServer(handleRequest);
  
  server.listen(CONFIG.port, () => {
    console.log(`🚀 API Server running on port ${CONFIG.port}`);
    console.log(`📡 Endpoints:`);
    console.log(`  GET /api/stats - Statistics`);
    console.log(`  GET /api/recipients - List recipients`);
    console.log(`  GET /api/variants - List variants`);
    console.log(`  GET /api/predictions - Generate and get predictions`);
    console.log(`  GET /api/dashboard - Generate and get dashboard HTML`);
    console.log(`  GET /api/health - Health check`);
    
    if (CONFIG.apiKey) {
      console.log(`\n🔐 API Key required (set via Authorization: Bearer <key>)`);
    } else {
      console.log(`\n⚠️  No API key set (use API_KEY env var for production)`);
    }
  });
  
  process.on('SIGINT', () => {
    console.log('\n👋 Shutting down API server...');
    server.close(() => process.exit(0));
  });
}

if (require.main === module) {
  main();
}





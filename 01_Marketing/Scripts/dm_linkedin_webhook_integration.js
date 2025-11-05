#!/usr/bin/env node
/**
 * Integración Webhook para Respuestas
 * Escucha webhooks de LinkedIn/CRM y actualiza automáticamente
 */
const http = require('http');
const fs = require('fs');
const path = require('path');

const CONFIG = {
  port: process.env.WEBHOOK_PORT || 3000,
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  webhookSecret: process.env.WEBHOOK_SECRET || '',
};

function appendResponse(recipient, data) {
  const { responded, clicked, converted } = data;
  const line = `${recipient},${responded},${clicked},${converted},${new Date().toISOString()}\n`;
  
  // Check if file exists, create header if not
  if (!fs.existsSync(CONFIG.responsesFile)) {
    fs.writeFileSync(CONFIG.responsesFile, 'recipient,responded,clicked,converted,timestamp\n', 'utf8');
  }
  
  // Append or update
  const content = fs.readFileSync(CONFIG.responsesFile, 'utf8');
  const lines = content.split('\n');
  const existing = lines.findIndex(l => l.startsWith(recipient));
  
  if (existing > 0) {
    lines[existing] = line.trim();
    fs.writeFileSync(CONFIG.responsesFile, lines.join('\n') + '\n', 'utf8');
  } else {
    fs.appendFileSync(CONFIG.responsesFile, line, 'utf8');
  }
}

function handleWebhook(req, res) {
  if (req.method !== 'POST') {
    res.writeHead(405);
    res.end('Method not allowed');
    return;
  }
  
  let body = '';
  req.on('data', chunk => {
    body += chunk.toString();
  });
  
  req.on('end', () => {
    try {
      const payload = JSON.parse(body);
      
      // Validate secret
      if (CONFIG.webhookSecret && payload.secret !== CONFIG.webhookSecret) {
        res.writeHead(401);
        res.end('Unauthorized');
        return;
      }
      
      // Expected format: { recipient, responded?, clicked?, converted? }
      const recipient = payload.recipient || payload.profileUrl;
      if (!recipient) {
        res.writeHead(400);
        res.end('Missing recipient');
        return;
      }
      
      appendResponse(recipient, {
        responded: payload.responded || false,
        clicked: payload.clicked || false,
        converted: payload.converted || false,
      });
      
      console.log(`✅ Updated response for ${recipient}`);
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ success: true, recipient }));
    } catch (e) {
      console.error('Error processing webhook:', e);
      res.writeHead(400);
      res.end('Invalid payload');
    }
  });
}

function main() {
  const server = http.createServer(handleWebhook);
  
  server.listen(CONFIG.port, () => {
    console.log(`🌐 Webhook server running on port ${CONFIG.port}`);
    console.log(`📥 POST to http://localhost:${CONFIG.port}/webhook`);
    console.log(`📋 Expected format: { recipient, responded, clicked, converted, secret? }`);
    
    if (!CONFIG.webhookSecret) {
      console.warn('⚠️  No webhook secret set (use WEBHOOK_SECRET env var)');
    }
  });
  
  process.on('SIGINT', () => {
    console.log('\n👋 Shutting down webhook server...');
    server.close(() => {
      process.exit(0);
    });
  });
}

if (require.main === module) {
  main();
}





const https = require('https');
const url = require('url');

function postJson(webhookUrl, payload) {
  try {
    const u = new url.URL(webhookUrl);
    const data = Buffer.from(JSON.stringify(payload));
    const opts = {
      protocol: u.protocol,
      hostname: u.hostname,
      port: u.port || 443,
      path: u.pathname + (u.search || ''),
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': data.length
      }
    };
    const req = https.request(opts, res => {
      res.on('data', () => {});
    });
    req.on('error', () => {});
    req.write(data);
    req.end();
  } catch (e) {
    // swallow
  }
}

function notify(message, extras) {
  const hook = process.env.SLACK_WEBHOOK_URL;
  if (!hook) return;
  const payload = { text: message, ...extras };
  postJson(hook, payload);
}

module.exports = { notify };




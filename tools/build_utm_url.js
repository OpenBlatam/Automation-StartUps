#!/usr/bin/env node
// Build a URL with UTM params and optionally update tokens.json
// Usage:
//  node tools/build_utm_url.js --source=instagram --medium=social --campaign=35IA_48h --content=feed --term=promo --apply

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOKENS_PATH = path.join(ROOT, 'design', 'instagram', 'tokens.json');

function parseArgs() {
  const args = process.argv.slice(2);
  const out = { apply: false };
  for (const a of args) {
    const [k, v] = a.includes('=') ? a.split('=') : [a, 'true'];
    const key = k.replace(/^--/, '');
    out[key] = v;
  }
  return out;
}

function buildUrl(base, p) {
  const u = new URL(base.startsWith('http') ? base : `https://${base}`);
  if (p.source) u.searchParams.set('utm_source', p.source);
  if (p.medium) u.searchParams.set('utm_medium', p.medium);
  if (p.campaign) u.searchParams.set('utm_campaign', p.campaign);
  if (p.content) u.searchParams.set('utm_content', p.content);
  if (p.term) u.searchParams.set('utm_term', p.term);
  return u.toString();
}

function main() {
  const p = parseArgs();
  const tokens = JSON.parse(fs.readFileSync(TOKENS_PATH, 'utf8'));
  const base = tokens.url || 'example.com';
  const url = buildUrl(base, p);
  console.log('UTM URL:', url);
  if (p.apply === 'true' || p.apply === true) {
    tokens.url = url;
    fs.writeFileSync(TOKENS_PATH, JSON.stringify(tokens, null, 2), 'utf8');
    console.log('tokens.json updated.');
  }
}

if (require.main === module) main();






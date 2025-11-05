#!/usr/bin/env node
// Apply UTM preset by market (es/en/pt) to tokens.json using build_utm_url

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOKENS = path.join(ROOT, 'design', 'instagram', 'tokens.json');
const PRESETS = path.join(ROOT, 'design', 'instagram', 'utm_presets.json');

function main() {
  const market = (process.argv[2] || '').toLowerCase();
  if (!market || !['es', 'en', 'pt'].includes(market)) {
    console.error('Usage: node tools/apply_market_utm.js <es|en|pt>');
    process.exit(1);
  }
  const presets = JSON.parse(fs.readFileSync(PRESETS, 'utf8'));
  const p = presets[market];
  if (!p) {
    console.error('Preset not found for market:', market);
    process.exit(1);
  }
  const tokens = JSON.parse(fs.readFileSync(TOKENS, 'utf8'));
  const base = tokens.url || 'example.com';
  const u = new URL(base.startsWith('http') ? base : `https://${base}`);
  u.searchParams.set('utm_source', p.source);
  u.searchParams.set('utm_medium', p.medium);
  u.searchParams.set('utm_campaign', p.campaign);
  u.searchParams.set('utm_content', p.content);
  u.searchParams.set('utm_term', p.term);
  tokens.url = u.toString();
  fs.writeFileSync(TOKENS, JSON.stringify(tokens, null, 2), 'utf8');
  console.log('Applied market UTM:', market);
  console.log('New URL:', tokens.url);
}

if (require.main === module) main();






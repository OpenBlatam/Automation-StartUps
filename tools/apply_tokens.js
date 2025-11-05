#!/usr/bin/env node
// Simple token applier for SVG files in design/instagram
// Replaces url/handle/coupon strings without external deps

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TARGET_DIR = path.join(ROOT, 'design', 'instagram');
const TOKENS_PATH = path.join(ROOT, 'design', 'instagram', 'tokens.json');

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, 'utf8'));
}

function* walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) {
      yield* walk(full);
    } else if (e.isFile() && e.name.endsWith('.svg')) {
      yield full;
    }
  }
}

function applyTokensToSvg(content, tokens) {
  let out = content;
  if (tokens.url) out = out.replace(/tu-sitio\.com/g, tokens.url);
  if (tokens.handle) out = out.replace(/@tu_marca/g, tokens.handle);
  if (tokens.coupon) out = out.replace(/CUPÓN: 35IA/g, `CUPÓN: ${tokens.coupon}`);
  if (tokens.coupon) out = out.replace(/CUPON: 35IA/g, `CUPON: ${tokens.coupon}`); // fallback sin tilde
  if (tokens.cta) out = out.replace(/Aprovecha hoy/g, tokens.cta);
  return out;
}

function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry');
  const tokens = readJson(TOKENS_PATH);
  let changed = 0;
  for (const file of walk(TARGET_DIR)) {
    const prev = fs.readFileSync(file, 'utf8');
    const next = applyTokensToSvg(prev, tokens);
    if (next !== prev) {
      changed += 1;
      if (!dryRun) fs.writeFileSync(file, next, 'utf8');
      console.log(`${dryRun ? '[dry]' : '[write]'} ${path.relative(ROOT, file)}`);
    }
  }
  console.log(`Done. Files changed: ${changed}${dryRun ? ' (dry run)' : ''}`);
}

if (require.main === module) {
  main();
}






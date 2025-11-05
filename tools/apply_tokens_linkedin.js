#!/usr/bin/env node
// Aplica tokens a los SVG de LinkedIn

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const LINKEDIN_DIR = path.join(ROOT, 'ads', 'linkedin');
const TOKENS_PATH = path.join(ROOT, 'ads', 'linkedin', 'tokens.json');

function readJson(p) {
  if (!fs.existsSync(p)) {
    console.error(`Tokens no encontrados: ${p}`);
    console.error('Ejecuta primero: node tools/sync_tokens_all_platforms.js');
    process.exit(1);
  }
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

function applyTokens(svg, tokens) {
  let out = svg;
  if (tokens.url) {
    out = out.replace(/tu-sitio\.com|example\.com/g, tokens.url);
    out = out.replace(/https?:\/\/example\.com/g, tokens.url);
  }
  if (tokens.handle) {
    out = out.replace(/@tu_marca|@example/g, tokens.handle);
  }
  if (tokens.coupon) {
    out = out.replace(/CUPÓN:?\s*35IA|COUPON:?\s*35IA|35IA/gi, `CUPÓN: ${tokens.coupon}`);
  }
  if (tokens.cta) {
    out = out.replace(/Aprovecha hoy|Act now|Únete hoy/gi, tokens.cta);
  }
  if (tokens.companyName) {
    out = out.replace(/Tu Empresa|Your Company/gi, tokens.companyName);
  }
  return out;
}

function main() {
  const args = process.argv.slice(2);
  const dryRun = args.includes('--dry');
  const tokens = readJson(TOKENS_PATH);
  let changed = 0;
  
  for (const file of walk(LINKEDIN_DIR)) {
    if (file.includes('tokens.json')) continue;
    const prev = fs.readFileSync(file, 'utf8');
    const next = applyTokens(prev, tokens);
    if (next !== prev) {
      changed++;
      if (!dryRun) fs.writeFileSync(file, next, 'utf8');
      console.log(`${dryRun ? '[dry]' : '[write]'} ${path.relative(ROOT, file)}`);
    }
  }
  
  console.log(`Done. Files changed: ${changed}${dryRun ? ' (dry run)' : ''}`);
}

if (require.main === module) main();




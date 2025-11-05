#!/usr/bin/env node
// Apply brand theme colors (gradients, CTA, logo placeholders) across SVGs

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TARGET_DIR = path.join(ROOT, 'design', 'instagram');
const TOKENS_PATH = path.join(ROOT, 'design', 'instagram', 'tokens.json');

function readJson(p) { return JSON.parse(fs.readFileSync(p, 'utf8')); }

function* walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const e of entries) {
    const full = path.join(dir, e.name);
    if (e.isDirectory()) yield* walk(full);
    else if (e.isFile() && e.name.endsWith('.svg')) yield full;
  }
}

function applyTheme(svg, c) {
  let out = svg;
  // Gradients primary/secondary replacements (common defaults used in files)
  out = out.replace(/#7B2FF7/gi, c.primary);
  out = out.replace(/#1E90FF/gi, c.secondary);
  out = out.replace(/#EE0979/gi, c.accent);
  out = out.replace(/#111111/gi, c.neutralDark);
  out = out.replace(/#ffffff/gi, c.neutralLight);
  // CTA strokes/fills using primary/accent when present
  out = out.replace(/stroke="#7B2FF7"/gi, `stroke="${c.primary}"`);
  out = out.replace(/stroke="#EE0979"/gi, `stroke="${c.accent}"`);
  out = out.replace(/fill="#7B2FF7"/gi, `fill="${c.primary}"`);
  out = out.replace(/fill="#EE0979"/gi, `fill="${c.accent}"`);
  return out;
}

function main() {
  const tokens = readJson(TOKENS_PATH);
  const colors = tokens.brandColors || {};
  const required = ['primary','secondary','accent','neutralDark','neutralLight'];
  for (const k of required) {
    if (!colors[k]) {
      console.error(`Missing brandColors.${k} in tokens.json`);
      process.exit(1);
    }
  }
  let changed = 0;
  for (const file of walk(TARGET_DIR)) {
    const prev = fs.readFileSync(file, 'utf8');
    const next = applyTheme(prev, colors);
    if (next !== prev) {
      fs.writeFileSync(file, next, 'utf8');
      changed++;
      console.log(`[theme] ${path.relative(ROOT, file)}`);
    }
  }
  console.log(`Theme applied. Files changed: ${changed}`);
}

if (require.main === module) main();






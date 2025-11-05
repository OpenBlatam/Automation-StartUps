#!/usr/bin/env node
// Generate text variants for discount (-XX %) and urgency labels in SVGs
// Usage examples:
//  node tools/generate_variants.js --perc=25,40,50 --urg="Solo 48 horas,Últimas 24 horas,Termina hoy"
//  node tools/generate_variants.js --perc=30 --targets=ig_descuento_curso_ia.svg

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const FEED_DIR = path.join(ROOT, 'design', 'instagram', '1080x1080');

function parseArgs() {
  const args = process.argv.slice(2);
  const res = { perc: [], urg: [], targets: [] };
  for (const a of args) {
    if (a.startsWith('--perc=')) {
      res.perc = a.replace('--perc=', '').split(',').map(s => s.trim()).filter(Boolean);
    } else if (a.startsWith('--urg=')) {
      res.urg = a.replace('--urg=', '').split(',').map(s => s.trim()).filter(Boolean);
    } else if (a.startsWith('--targets=')) {
      res.targets = a.replace('--targets=', '').split(',').map(s => s.trim()).filter(Boolean);
    }
  }
  return res;
}

function listDefaultTargets() {
  return [
    'ig_descuento_curso_ia.svg',
    'ig_descuento_saas_marketing.svg',
    'ig_descuento_ia_bulk.svg',
  ];
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function generateVariantName(baseName, perc, urg) {
  const name = baseName.replace('.svg', `_${perc}pct_${slug(urg)}.svg`);
  return name;
}

function slug(s) {
  return s.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '');
}

function buildVariant(svg, perc, urg) {
  let out = svg;
  // Replace discount (supports white/black variants)
  out = out.replace(/-\d+\s?%/g, `-${perc} %`);
  // Replace urgency label common options
  out = out.replace(/Solo 48 horas|Últimas 24 horas|Ultimas 24 horas|Termina hoy/gi, match => {
    // Keep capitalization similar to target
    const target = urg;
    if (match === match.toUpperCase()) return target.toUpperCase();
    if (match[0] === match[0].toUpperCase()) return target[0].toUpperCase() + target.slice(1);
    return target;
  });
  return out;
}

function main() {
  const { perc, urg, targets } = parseArgs();
  const discounts = perc.length ? perc : ['35'];
  const urgencies = urg.length ? urg : ['Solo 48 horas', 'Últimas 24 horas', 'Termina hoy'];
  const files = (targets.length ? targets : listDefaultTargets()).map(f => path.join(FEED_DIR, f));

  for (const file of files) {
    if (!fs.existsSync(file)) {
      console.warn(`[skip] not found: ${path.relative(ROOT, file)}`);
      continue;
    }
    const svg = fs.readFileSync(file, 'utf8');
    for (const d of discounts) {
      for (const u of urgencies) {
        const variant = buildVariant(svg, d, u);
        const outName = generateVariantName(path.basename(file), d, u);
        const outPath = path.join(FEED_DIR, 'variants');
        ensureDir(outPath);
        const full = path.join(outPath, outName);
        fs.writeFileSync(full, variant, 'utf8');
        console.log(`[write] ${path.relative(ROOT, full)}`);
      }
    }
  }
  console.log('Done generating variants.');
}

if (require.main === module) {
  main();
}






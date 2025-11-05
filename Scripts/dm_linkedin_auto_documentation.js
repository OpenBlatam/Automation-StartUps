#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { notify } = require('./utils_notify');
const { parseCliFlags } = require('./utils_fs');

function safeReadJson(absPath, fallback) {
  try {
    if (!fs.existsSync(absPath)) return fallback;
    const raw = fs.readFileSync(absPath, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    return fallback;
  }
}

function safeReadCsv(absPath) {
  try {
    if (!fs.existsSync(absPath)) return [];
    const raw = fs.readFileSync(absPath, 'utf8');
    const [headerLine, ...lines] = raw.split(/\r?\n/).filter(Boolean);
    if (!headerLine) return [];
    const headers = headerLine.split(',');
    return lines.map(l => {
      const cols = l.split(',');
      const obj = {};
      headers.forEach((h, i) => (obj[h.trim()] = (cols[i] || '').trim()));
      return obj;
    });
  } catch (e) {
    return [];
  }
}

function listTopScripts(dir) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter(f => f.endsWith('.js'))
    .sort();
}

function generateDocs() {
  const root = path.resolve(__dirname, '..');
  const reportsDir = path.resolve(root, '01_Marketing', 'Reports');
  if (!fs.existsSync(reportsDir)) fs.mkdirSync(reportsDir, { recursive: true });

  const config = safeReadJson(path.resolve(root, 'config.json'), {});
  const variantsCsv = safeReadCsv(path.resolve(root, 'dm_variants_master.csv'));
  const variantsShortCsv = safeReadCsv(path.resolve(root, 'DM_Variants_Short.csv'));
  const scripts = listTopScripts(path.resolve(root, 'Scripts'));

  const scriptList = scripts.map(s => `- ${path.join('Scripts', s)}`).join('\n');

  const variantsPreview = (variantsCsv.length ? variantsCsv : variantsShortCsv)
    .slice(0, 10)
    .map((r, i) => `- [${i + 1}] ${JSON.stringify(r)}`)
    .join('\n');

  const docContent = `## 📚 Documentación Automática – Sistema DMs LinkedIn\n\n**Generado:** ${new Date().toISOString()}\n**Versión Sistema:** 12.0\n\n### 🛠️ Scripts disponibles\n${scriptList || '- (sin scripts .js en Scripts/)'}\n\n### 💬 Variantes (preview 10)\n${variantsPreview || '- (sin variantes CSV detectadas)'}\n\n### 🔗 Configuración (config.json)\n\n\`\`\`json\n${JSON.stringify(config, null, 2)}\n\`\`\`\n\n### Notas\n- Este documento es generado por \`node Scripts/dm_linkedin_auto_documentation.js\`.\n- Rutas esperadas: \`dm_variants_master.csv\`, \`DM_Variants_Short.csv\`, \`config.json\`.\n`;

  const outFile = path.resolve(reportsDir, 'dm_linkedin_auto_documentacion.md');
  fs.writeFileSync(outFile, docContent, 'utf8');
  const rel = path.relative(root, outFile);
  console.log(`Documentación generada: ${rel}`);
  const { noNotify } = parseCliFlags();
  if (!noNotify) notify(`DM Docs generadas: ${rel}`);
}

generateDocs();



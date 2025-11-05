#!/usr/bin/env node
// Verifica que todos los tokens estén aplicados correctamente

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOKENS_FILE = path.join(ROOT, 'design', 'instagram', 'tokens.json');
const SVG_DIR = path.join(ROOT, 'design', 'instagram');

function findSvgs(dir) {
  const svgs = [];
  const items = fs.readdirSync(dir, { withFileTypes: true });
  for (const item of items) {
    const fullPath = path.join(dir, item.name);
    if (item.isDirectory() && !item.name.startsWith('.') && item.name !== 'node_modules') {
      svgs.push(...findSvgs(fullPath));
    } else if (item.isFile() && item.name.endsWith('.svg')) {
      svgs.push(fullPath);
    }
  }
  return svgs;
}

function main() {
  if (!fs.existsSync(TOKENS_FILE)) {
    console.error('❌ tokens.json no encontrado');
    process.exit(1);
  }

  const tokens = JSON.parse(fs.readFileSync(TOKENS_FILE, 'utf8'));
  const tokenKeys = Object.keys(tokens).filter(k => k !== 'brandColors');
  
  console.log(`🔍 Verificando cobertura de tokens...\n`);
  console.log(`Tokens a verificar: ${tokenKeys.join(', ')}\n`);

  const svgs = findSvgs(SVG_DIR);
  let totalWithPlaceholders = 0;
  const byToken = {};

  for (const svgPath of svgs) {
    const content = fs.readFileSync(svgPath, 'utf8');
    const relPath = path.relative(ROOT, svgPath);
    
    for (const key of tokenKeys) {
      const placeholder = `{{${key}}}`;
      if (content.includes(placeholder)) {
        if (!byToken[key]) byToken[key] = [];
        byToken[key].push(relPath);
        totalWithPlaceholders++;
      }
    }
  }

  // Resultados
  console.log('📊 Resultados:');
  console.log('─'.repeat(50));
  
  let hasIssues = false;
  for (const key of tokenKeys) {
    const files = byToken[key] || [];
    if (files.length > 0) {
      console.log(`\n⚠️  ${key}: ${files.length} archivo(s) con placeholder`);
      files.slice(0, 5).forEach(f => console.log(`   - ${f}`));
      if (files.length > 5) {
        console.log(`   ... y ${files.length - 5} más`);
      }
      hasIssues = true;
    } else {
      console.log(`✅ ${key}: todos aplicados`);
    }
  }

  console.log('\n' + '─'.repeat(50));
  if (hasIssues) {
    console.log(`\n⚠️  Total: ${totalWithPlaceholders} placeholder(s) sin aplicar`);
    console.log('\n💡 Ejecuta: node tools/apply_tokens.js');
    process.exit(1);
  } else {
    console.log(`\n✅ Todos los tokens están aplicados correctamente`);
  }
}

if (require.main === module) main();



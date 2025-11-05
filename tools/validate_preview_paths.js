#!/usr/bin/env node
// Valida que todas las rutas del preview HTML existan

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PREVIEW = path.join(ROOT, 'exports', 'preview', 'index.html');

function extractSvgPaths(html) {
  const paths = [];
  // Buscar rutas en el objeto categories
  const matches = html.matchAll(/['"](\.\.\/.*?\.svg)['"]/g);
  for (const match of matches) {
    paths.push(match[1]);
  }
  return [...new Set(paths)]; // Eliminar duplicados
}

function main() {
  if (!fs.existsSync(PREVIEW)) {
    console.error('❌ Preview no encontrado:', PREVIEW);
    process.exit(1);
  }

  const html = fs.readFileSync(PREVIEW, 'utf8');
  const paths = extractSvgPaths(html);
  
  console.log(`🔍 Validando ${paths.length} rutas del preview...\n`);
  
  let missing = 0;
  let found = 0;
  
  for (const relPath of paths) {
    const absPath = path.join(ROOT, 'exports', 'preview', relPath);
    if (fs.existsSync(absPath)) {
      found++;
      // Opcional: verificar que no esté vacío
      const stats = fs.statSync(absPath);
      if (stats.size === 0) {
        console.log(`⚠️  VACÍO: ${relPath}`);
      }
    } else {
      console.log(`❌ NO ENCONTRADO: ${relPath}`);
      missing++;
    }
  }
  
  console.log(`\n📊 Resultados:`);
  console.log(`  ✅ Encontrados: ${found}`);
  console.log(`  ❌ No encontrados: ${missing}`);
  
  if (missing > 0) {
    console.log(`\n⚠️  Hay ${missing} ruta(s) rota(s) en el preview.`);
    process.exit(1);
  } else {
    console.log(`\n✅ Todas las rutas son válidas.`);
  }
}

if (require.main === module) main();




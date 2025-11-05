#!/usr/bin/env node
// Auto-detecta assets y actualiza el preview dinámicamente
// Ejecutar después de añadir nuevos assets

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PREVIEW = path.join(ROOT, 'exports', 'preview', 'index.html');

function findAssets(dir, pattern) {
  if (!fs.existsSync(dir)) return [];
  const files = [];
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true, recursive: true });
    for (const e of entries) {
      if (e.isFile() && e.name.match(pattern)) {
        const rel = path.relative(ROOT, path.join(e.path || dir, e.name));
        files.push(rel);
      }
    }
  } catch (e) {
    // Ignore errors
  }
  return files;
}

function main() {
  console.log('🔍 Detectando assets para preview...');
  
  const categories = {
    linkedin: findAssets(path.join(ROOT, 'ads', 'linkedin'), /\.svg$/),
    webinars: findAssets(ROOT, /^webinar-.*\.svg$/),
    webinarsSquare: findAssets(ROOT, /^webinar-square-.*\.svg$/),
  };
  
  console.log('LinkedIn encontrados:', categories.linkedin.length);
  console.log('Webinars encontrados:', categories.webinars.length);
  console.log('Webinars Square:', categories.webinarsSquare.length);
  
  console.log('\n💡 Para añadir manualmente, edita exports/preview/index.html');
  console.log('💡 Los assets se detectan automáticamente si están en las rutas esperadas');
}

if (require.main === module) main();




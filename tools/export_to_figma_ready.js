#!/usr/bin/env node
/**
 * Prepara assets para importación en Figma
 * Genera un CSV con información de assets para facilitar la importación
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const OUTPUT_CSV = path.join(ROOT_DIR, 'exports/figma_import.csv');
const OUTPUT_README = path.join(ROOT_DIR, 'exports/FIGMA_IMPORT_GUIDE.md');

console.log('🎨 Preparando assets para Figma...');
console.log('');

// Encontrar todos los SVGs
function findSVGs(dir, baseDir = dir) {
  const svgs = [];
  
  if (!fs.existsSync(dir)) return svgs;
  
  const items = fs.readdirSync(dir, { withFileTypes: true });
  
  items.forEach(item => {
    const fullPath = path.join(dir, item.name);
    const relativePath = path.relative(baseDir, fullPath);
    
    if (item.isDirectory()) {
      svgs.push(...findSVGs(fullPath, baseDir));
    } else if (item.name.endsWith('.svg')) {
      const content = fs.readFileSync(fullPath, 'utf8');
      const sizeMatch = content.match(/viewBox=["']0 0 (\d+) (\d+)["']/);
      const width = sizeMatch ? sizeMatch[1] : '1080';
      const height = sizeMatch ? sizeMatch[2] : '1080';
      
      svgs.push({
        name: item.name,
        path: relativePath,
        fullPath: fullPath,
        width: parseInt(width),
        height: parseInt(height),
        size: fs.statSync(fullPath).size,
        platform: fullPath.includes('linkedin') ? 'LinkedIn' : 
                 fullPath.includes('webinar') ? 'Webinar' : 'Instagram'
      });
    }
  });
  
  return svgs;
}

const designDir = path.join(ROOT_DIR, 'design');
const adsDir = path.join(ROOT_DIR, 'ads');

const allSVGs = [
  ...findSVGs(designDir, ROOT_DIR),
  ...findSVGs(adsDir, ROOT_DIR)
];

// Generar CSV
const csvLines = [
  'Asset Name,Path,Platform,Width,Height,Size (bytes),Figma Ready'
];

allSVGs.forEach(svg => {
  const figmaReady = svg.width && svg.height ? 'Yes' : 'Needs Review';
  csvLines.push(
    `"${svg.name}","${svg.path}","${svg.platform}",${svg.width},${svg.height},${svg.size},"${figmaReady}"`
  );
});

fs.mkdirSync(path.dirname(OUTPUT_CSV), { recursive: true });
fs.writeFileSync(OUTPUT_CSV, csvLines.join('\n'));

// Generar README
const readme = `# Guía de Importación a Figma

Este documento explica cómo importar los assets de este proyecto a Figma.

## 📋 Preparación

1. **CSV de Referencia**: Abre \`figma_import.csv\` para ver todos los assets disponibles.

2. **Método de Importación**:
   - **Opción A**: Arrastra y suelta los archivos SVG directamente en Figma
   - **Opción B**: Usa el plugin "SVG Import" de Figma
   - **Opción C**: Importa desde archivo (File → Import)

## 📦 Assets Disponibles

**Total**: ${allSVGs.length} archivos SVG

### Por Plataforma:
${['Instagram', 'LinkedIn', 'Webinar'].map(platform => {
  const count = allSVGs.filter(s => s.platform === platform).length;
  return `- **${platform}**: ${count} assets`;
}).join('\n')}

### Por Tamaño:
${['1080x1080', '1080x1920', '1200x627'].map(size => {
  const [w, h] = size.split('x').map(Number);
  const count = allSVGs.filter(s => s.width === w && s.height === h).length;
  return count > 0 ? `- **${size}**: ${count} assets` : null;
}).filter(Boolean).join('\n')}

## ⚙️ Configuración Recomendada en Figma

1. **Crear un Frame** por tamaño de asset:
   - Frame 1080x1080 para feed posts
   - Frame 1080x1920 para stories
   - Frame 1200x627 para LinkedIn

2. **Organizar en Pages**:
   - Página "Instagram Feed"
   - Página "Instagram Stories"
   - Página "LinkedIn"

3. **Usar Components**:
   - Convierte assets reutilizables en Components
   - Crea Variants para diferentes descuentos/CTAs

## 🔄 Sincronización

Para mantener sincronizados los assets:

1. Exporta cambios desde Figma como SVG
2. Reemplaza los archivos originales en \`design/\` o \`ads/\`
3. Ejecuta: \`node tools/apply_tokens.js\` para aplicar tokens
4. Ejecuta: \`bash tools/export_png.sh\` para generar PNGs

## 📝 Notas Importantes

- Los SVGs contienen tokens ({{TOKEN}}) que deben reemplazarse antes de usar
- Usa el sistema de tokens de este proyecto para mantener consistencia
- Los assets están optimizados con SVGO (ejecutar: \`bash tools/optimize_svg.sh\`)

## 🎨 Personalización

1. Edita los SVGs en Figma según necesites
2. Exporta como SVG (File → Export → SVG)
3. Guarda en la estructura original del proyecto
4. Ejecuta el build completo: \`bash tools/build_all.sh\`

## 🔗 Enlaces Útiles

- [Documentación de Figma SVG](https://www.figma.com/developers/api#svg)
- [Guía de tokens del proyecto](./readme.md#tokens)
- [Exportación de PNG](./readme.md#exportación)
`;

fs.writeFileSync(OUTPUT_README, readme);

console.log('✅ Archivos generados:');
console.log(`   📄 CSV: ${OUTPUT_CSV}`);
console.log(`   📖 Guía: ${OUTPUT_README}`);
console.log('');
console.log('📊 Resumen:');
console.log(`   Total assets: ${allSVGs.length}`);
console.log(`   Instagram: ${allSVGs.filter(s => s.platform === 'Instagram').length}`);
console.log(`   LinkedIn: ${allSVGs.filter(s => s.platform === 'LinkedIn').length}`);
console.log(`   Webinar: ${allSVGs.filter(s => s.platform === 'Webinar').length}`);
console.log('');
console.log('💡 Próximos pasos:');
console.log('   1. Abre figma_import.csv en Excel/Sheets');
console.log('   2. Importa los SVGs a Figma según la guía');
console.log('   3. Edita y exporta de vuelta cuando esté listo');


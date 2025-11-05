#!/usr/bin/env node
/**
 * Sistema de recomendaciones inteligentes basado en análisis de assets
 * Sugiere mejoras basadas en mejores prácticas de marketing y diseño
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const TOKENS_FILE = path.join(ROOT_DIR, 'design/instagram/tokens.json');
const RECOMMENDATIONS_FILE = path.join(ROOT_DIR, 'exports/smart_recommendations.json');

// Cargar tokens
let tokens = {};
if (fs.existsSync(TOKENS_FILE)) {
  tokens = JSON.parse(fs.readFileSync(TOKENS_FILE, 'utf8'));
}

const recommendations = {
  critical: [],
  important: [],
  suggestions: [],
  insights: []
};

// 1. Verificar tokens con valores por defecto
if (tokens.URL && (tokens.URL.includes('tu-sitio.com') || tokens.URL.includes('ejemplo.com'))) {
  recommendations.critical.push({
    type: 'tokens',
    title: 'Actualizar URLs',
    message: 'Los tokens contienen URLs de ejemplo. Actualiza con tus URLs reales.',
    action: 'Editar design/instagram/tokens.json',
    impact: 'high'
  });
}

// 2. Verificar contraste de colores
if (tokens.brandColors) {
  const primaryColor = tokens.brandColors.primary || '';
  const textColor = tokens.brandColors.text || '#000000';
  
  // Validación básica de contraste (simplificada)
  if (primaryColor === textColor || primaryColor === '#000000' && textColor === '#000000') {
    recommendations.important.push({
      type: 'accessibility',
      title: 'Contraste de colores',
      message: 'El color primario y el texto pueden no tener suficiente contraste.',
      action: 'Verificar contraste WCAG AA (mínimo 4.5:1)',
      impact: 'medium',
      tool: 'https://webaim.org/resources/contrastchecker/'
    });
  }
}

// 3. Verificar uso de QR codes
function checkQRUsage() {
  const designDir = path.join(ROOT_DIR, 'design/instagram');
  if (!fs.existsSync(designDir)) return;
  
  const svgFiles = [];
  function findSVGs(dir) {
    const files = fs.readdirSync(dir, { withFileTypes: true });
    files.forEach(file => {
      const fullPath = path.join(dir, file.name);
      if (file.isDirectory()) {
        findSVGs(fullPath);
      } else if (file.name.endsWith('.svg')) {
        svgFiles.push(fullPath);
      }
    });
  }
  
  findSVGs(designDir);
  
  let qrCount = 0;
  let totalAssets = 0;
  
  svgFiles.forEach(svgPath => {
    const content = fs.readFileSync(svgPath, 'utf8');
    if (content.includes('qr-placeholder') || content.includes('QR_PLACEHOLDER')) {
      qrCount++;
    }
    totalAssets++;
  });
  
  if (totalAssets > 0 && qrCount === 0) {
    recommendations.suggestions.push({
      type: 'engagement',
      title: 'Agregar QR codes',
      message: `Ninguno de tus ${totalAssets} assets tiene QR codes. Los QR codes pueden aumentar engagement hasta 40%.`,
      action: 'Ejecutar: node tools/generate_qr.js',
      impact: 'medium',
      benefit: 'Aumento de conversión'
    });
  }
}

// 4. Verificar variantes A/B
function checkABVariants() {
  const designDir = path.join(ROOT_DIR, 'design/instagram/1080x1080');
  if (!fs.existsSync(designDir)) return;
  
  const files = fs.readdirSync(designDir);
  const abVariants = files.filter(f => f.includes('_ab_'));
  
  if (abVariants.length === 0) {
    recommendations.suggestions.push({
      type: 'optimization',
      title: 'Crear variantes A/B',
      message: 'No se detectaron variantes A/B. El testing A/B puede mejorar CTR hasta 30%.',
      action: 'Usar: bash tools/generate_variants.js --type ab',
      impact: 'medium',
      benefit: 'Mejor CTR y conversión'
    });
  }
}

// 5. Verificar optimización de SVGs
function checkSVGOptimization() {
  const exportDir = path.join(ROOT_DIR, 'exports/svg_opt');
  if (!fs.existsSync(exportDir)) {
    recommendations.important.push({
      type: 'performance',
      title: 'Optimizar SVGs',
      message: 'No se encontró carpeta de SVGs optimizados. La optimización reduce tamaño 20-50%.',
      action: 'Ejecutar: bash tools/optimize_svg.sh',
      impact: 'medium',
      benefit: 'Mejor carga y performance'
    });
  }
}

// 6. Verificar exports PNG
function checkPNGExports() {
  const pngDir = path.join(ROOT_DIR, 'exports/png');
  if (!fs.existsSync(pngDir) || !fs.existsSync(path.join(pngDir, '1x')) || !fs.existsSync(path.join(pngDir, '2x'))) {
    recommendations.important.push({
      type: 'delivery',
      title: 'Exportar PNGs',
      message: 'Los PNGs 1x y 2x no están generados. Instagram requiere PNGs para publicación.',
      action: 'Ejecutar: bash tools/export_png.sh',
      impact: 'high',
      benefit: 'Assets listos para publicación'
    });
  }
}

// 7. Verificar dark mode
function checkDarkMode() {
  const designDir = path.join(ROOT_DIR, 'design/instagram');
  if (!fs.existsSync(designDir)) return;
  
  const svgFiles = [];
  function findSVGs(dir) {
    const files = fs.readdirSync(dir, { withFileTypes: true });
    files.forEach(file => {
      const fullPath = path.join(dir, file.name);
      if (file.isDirectory()) {
        findSVGs(fullPath);
      } else if (file.name.endsWith('.svg') && !file.name.includes('_dark')) {
        svgFiles.push(fullPath);
      }
    });
  }
  
  findSVGs(designDir);
  
  if (svgFiles.length > 3) {
    recommendations.suggestions.push({
      type: 'design',
      title: 'Crear variantes dark mode',
      message: `${svgFiles.length} assets sin variante dark. El dark mode puede mejorar engagement en móviles.`,
      action: 'Considerar crear variantes dark para assets principales',
      impact: 'low',
      benefit: 'Mejor UX en modo oscuro'
    });
  }
}

// 8. Insights basados en mejores prácticas
recommendations.insights.push({
  type: 'best_practice',
  title: 'Horarios de publicación',
  message: 'Las mejores horas para Instagram: 11am-1pm y 7pm-9pm (zona horaria del público objetivo)',
  source: 'Analytics de Instagram'
});

recommendations.insights.push({
  type: 'best_practice',
  title: 'Formato Stories',
  message: 'Stories con texto <20% tienen mejor rendimiento en Instagram Ads',
  source: 'Instagram Ads Policy'
});

// Ejecutar todas las verificaciones
checkQRUsage();
checkABVariants();
checkSVGOptimization();
checkPNGExports();
checkDarkMode();

// Generar reporte
const report = {
  generated: new Date().toISOString(),
  summary: {
    critical: recommendations.critical.length,
    important: recommendations.important.length,
    suggestions: recommendations.suggestions.length,
    insights: recommendations.insights.length
  },
  recommendations,
  nextSteps: [
    recommendations.critical.length > 0 ? 'Revisar y corregir recomendaciones críticas' : null,
    recommendations.important.length > 0 ? 'Implementar mejoras importantes' : null,
    'Revisar sugerencias y insights para optimización',
    'Ejecutar: bash tools/auto_fix_issues.sh para correcciones automáticas'
  ].filter(Boolean)
};

// Guardar reporte
fs.mkdirSync(path.dirname(RECOMMENDATIONS_FILE), { recursive: true });
fs.writeFileSync(RECOMMENDATIONS_FILE, JSON.stringify(report, null, 2));

// Mostrar resumen
console.log('💡 Recomendaciones Inteligentes');
console.log('================================');
console.log(`🔴 Críticas: ${recommendations.critical.length}`);
console.log(`🟠 Importantes: ${recommendations.important.length}`);
console.log(`🟡 Sugerencias: ${recommendations.suggestions.length}`);
console.log(`🔵 Insights: ${recommendations.insights.length}`);
console.log('');
console.log(`📄 Reporte completo: ${RECOMMENDATIONS_FILE}`);
console.log('');

if (recommendations.critical.length > 0) {
  console.log('🔴 CRÍTICAS:');
  recommendations.critical.forEach((rec, i) => {
    console.log(`   ${i + 1}. ${rec.title}: ${rec.message}`);
  });
  console.log('');
}

if (recommendations.important.length > 0) {
  console.log('🟠 IMPORTANTES:');
  recommendations.important.forEach((rec, i) => {
    console.log(`   ${i + 1}. ${rec.title}: ${rec.message}`);
  });
  console.log('');
}

console.log('💡 Para ver todas las recomendaciones:');
console.log(`   cat ${RECOMMENDATIONS_FILE} | jq`);


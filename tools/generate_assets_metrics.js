#!/usr/bin/env node
// Genera métricas avanzadas de assets para análisis de rendimiento

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const OUTPUT = path.join(ROOT, 'exports', 'assets_metrics.json');

function findSvgs(dir, base = ROOT) {
  const svgs = [];
  try {
    const items = fs.readdirSync(dir, { withFileTypes: true });
    for (const item of items) {
      const fullPath = path.join(dir, item.name);
      if (item.isDirectory() && !item.name.startsWith('.') && item.name !== 'node_modules') {
        svgs.push(...findSvgs(fullPath, base));
      } else if (item.isFile() && item.name.endsWith('.svg')) {
        svgs.push(path.relative(base, fullPath));
      }
    }
  } catch (e) {
    // Ignorar errores
  }
  return svgs;
}

function analyzeSvg(filePath) {
  const fullPath = path.join(ROOT, filePath);
  const stats = fs.statSync(fullPath);
  const content = fs.readFileSync(fullPath, 'utf8');
  
  // Análisis básico
  const size = stats.size;
  const lines = content.split('\n').length;
  
  // Elementos
  const hasGradient = /gradient/i.test(content);
  const hasFilter = /<filter/i.test(content);
  const hasText = /<text/i.test(content);
  const hasImage = /<image|<img/i.test(content);
  const hasAnimation = /<animate|<animateTransform/i.test(content);
  
  // Complejidad
  const elementCount = (content.match(/<\w+/g) || []).length;
  const pathCount = (content.match(/<path/g) || []).length;
  const textElementCount = (content.match(/<text/g) || []).length;
  
  // Accesibilidad
  const hasTitle = /<title/i.test(content);
  const hasDesc = /<desc/i.test(content);
  const hasAriaLabel = /aria-label/i.test(content);
  
  // Tokens y placeholders
  const hasPlaceholders = /{{|LOGO|PLACEHOLDER/i.test(content);
  const tokenCount = (content.match(/{{[^}]+}}/g) || []).length;
  
  // Dimensiones
  let width = null;
  let height = null;
  let viewBox = null;
  
  const viewBoxMatch = content.match(/viewBox="([^"]+)"/);
  if (viewBoxMatch) {
    viewBox = viewBoxMatch[1];
    const parts = viewBox.split(/\s+/);
    if (parts.length === 4) {
      width = parseFloat(parts[2]);
      height = parseFloat(parts[3]);
    }
  } else {
    const widthMatch = content.match(/width="(\d+)"/);
    const heightMatch = content.match(/height="(\d+)"/);
    if (widthMatch) width = parseFloat(widthMatch[1]);
    if (heightMatch) height = parseFloat(heightMatch[1]);
  }
  
  // Categorización
  let category = 'unknown';
  if (filePath.includes('1080x1080')) category = 'feed';
  else if (filePath.includes('1080x1350')) category = 'vertical_feed';
  else if (filePath.includes('1080x1920')) category = 'stories';
  else if (filePath.includes('1200x627')) category = 'linkedin_horizontal';
  else if (filePath.includes('reels')) category = 'reels';
  else if (filePath.includes('highlights')) category = 'highlights';
  else if (filePath.includes('carousel')) category = 'carousel';
  else if (filePath.includes('linkedin')) category = 'linkedin';
  else if (filePath.includes('webinar')) category = 'webinar';
  
  return {
    path: filePath,
    size,
    lines,
    dimensions: { width, height, viewBox },
    complexity: {
      elements: elementCount,
      paths: pathCount,
      textElements: textElementCount,
      score: elementCount + (pathCount * 2) + (textElementCount * 0.5)
    },
    features: {
      gradient: hasGradient,
      filter: hasFilter,
      text: hasText,
      image: hasImage,
      animation: hasAnimation
    },
    accessibility: {
      title: hasTitle,
      description: hasDesc,
      ariaLabel: hasAriaLabel,
      score: (hasTitle ? 1 : 0) + (hasDesc ? 1 : 0) + (hasAriaLabel ? 1 : 0)
    },
    tokens: {
      hasPlaceholders,
      tokenCount
    },
    category,
    timestamp: stats.mtime.toISOString()
  };
}

function main() {
  console.log('📊 Generando métricas avanzadas de assets...\n');
  
  const svgs = findSvgs(ROOT);
  console.log(`Encontrados ${svgs.length} archivos SVG\n`);
  
  const metrics = {
    generated: new Date().toISOString(),
    summary: {
      total: svgs.length,
      byCategory: {},
      totalSize: 0,
      avgSize: 0,
      avgComplexity: 0,
      avgAccessibility: 0
    },
    assets: [],
    insights: {
      largest: null,
      smallest: null,
      mostComplex: null,
      mostAccessible: [],
      needsOptimization: [],
      missingTokens: []
    }
  };
  
  let totalSize = 0;
  let totalComplexity = 0;
  let totalAccessibility = 0;
  
  for (const svg of svgs) {
    try {
      const analysis = analyzeSvg(svg);
      metrics.assets.push(analysis);
      
      // Agregar a categorías
      if (!metrics.summary.byCategory[analysis.category]) {
        metrics.summary.byCategory[analysis.category] = 0;
      }
      metrics.summary.byCategory[analysis.category]++;
      
      totalSize += analysis.size;
      totalComplexity += analysis.complexity.score;
      totalAccessibility += analysis.accessibility.score;
      
      // Insights
      if (!metrics.insights.largest || analysis.size > metrics.insights.largest.size) {
        metrics.insights.largest = { path: svg, size: analysis.size };
      }
      if (!metrics.insights.smallest || analysis.size < metrics.insights.smallest.size) {
        metrics.insights.smallest = { path: svg, size: analysis.size };
      }
      if (!metrics.insights.mostComplex || analysis.complexity.score > metrics.insights.mostComplex.score) {
        metrics.insights.mostComplex = { path: svg, score: analysis.complexity.score };
      }
      
      if (analysis.accessibility.score === 3) {
        metrics.insights.mostAccessible.push(svg);
      }
      
      if (analysis.size > 100000) {
        metrics.insights.needsOptimization.push({ path: svg, size: analysis.size });
      }
      
      if (analysis.tokens.hasPlaceholders) {
        metrics.insights.missingTokens.push(svg);
      }
    } catch (e) {
      console.warn(`⚠️  Error analizando ${svg}: ${e.message}`);
    }
  }
  
  metrics.summary.totalSize = totalSize;
  metrics.summary.avgSize = svgs.length > 0 ? Math.round(totalSize / svgs.length) : 0;
  metrics.summary.avgComplexity = svgs.length > 0 ? (totalComplexity / svgs.length).toFixed(2) : 0;
  metrics.summary.avgAccessibility = svgs.length > 0 ? (totalAccessibility / svgs.length).toFixed(2) : 0;
  
  // Ordenar assets por complejidad
  metrics.assets.sort((a, b) => b.complexity.score - a.complexity.score);
  
  fs.writeFileSync(OUTPUT, JSON.stringify(metrics, null, 2));
  
  console.log('✅ Métricas generadas:');
  console.log(`   Total assets: ${metrics.summary.total}`);
  console.log(`   Tamaño total: ${(totalSize / 1024).toFixed(2)} KB`);
  console.log(`   Complejidad promedio: ${metrics.summary.avgComplexity}`);
  console.log(`   Accesibilidad promedio: ${metrics.summary.avgAccessibility}/3`);
  console.log(`   Categorías: ${Object.keys(metrics.summary.byCategory).length}`);
  console.log(`   Necesitan optimización: ${metrics.insights.needsOptimization.length}`);
  console.log(`   Faltan tokens: ${metrics.insights.missingTokens.length}`);
  console.log(`\n📄 Reporte guardado en: ${OUTPUT}`);
}

if (require.main === module) main();



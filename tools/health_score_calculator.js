#!/usr/bin/env node
/**
 * Calcula health score del sistema basado en múltiples métricas
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT_DIR = path.join(__dirname, '..');
const OUTPUT_FILE = path.join(ROOT_DIR, 'exports/health_score.json');

console.log('🏥 Calculando Health Score...');
console.log('');

let score = 100;
const issues = [];
const warnings = [];

// 1. Verificar estructura básica (-10 si falta)
const requiredDirs = [
  'design/instagram',
  'exports',
  'tools'
];

requiredDirs.forEach(dir => {
  if (!fs.existsSync(path.join(ROOT_DIR, dir))) {
    score -= 10;
    issues.push(`Directorio faltante: ${dir}`);
  }
});

// 2. Verificar tokens.json (-20 si falta o tiene valores por defecto)
const tokensFile = path.join(ROOT_DIR, 'design/instagram/tokens.json');
if (!fs.existsSync(tokensFile)) {
  score -= 20;
  issues.push('tokens.json no encontrado');
} else {
  try {
    const tokens = JSON.parse(fs.readFileSync(tokensFile, 'utf8'));
    if (tokens.URL && (tokens.URL.includes('tu-sitio.com') || tokens.URL.includes('ejemplo.com'))) {
      score -= 15;
      warnings.push('Tokens con valores por defecto');
    }
  } catch (e) {
    score -= 10;
    issues.push('tokens.json inválido');
  }
}

// 3. Verificar SVGs vacíos (-15 por cada 5 vacíos)
try {
  const emptySVGs = execSync(
    `find "${ROOT_DIR}/design" "${ROOT_DIR}/ads" -name "*.svg" -size 0 2>/dev/null | wc -l`,
    { encoding: 'utf8' }
  ).trim();
  
  const emptyCount = parseInt(emptySVGs) || 0;
  if (emptyCount > 0) {
    const penalty = Math.min(15, Math.ceil(emptyCount / 5) * 5);
    score -= penalty;
    issues.push(`${emptyCount} SVG(s) vacío(s)`);
  }
} catch (e) {
  // Ignorar errores
}

// 4. Verificar tokens aplicados (-10 si hay tokens sin aplicar)
try {
  const tokenCheck = execSync('node tools/check_token_coverage.js', { 
    encoding: 'utf8',
    cwd: ROOT_DIR,
    stdio: 'pipe'
  });
  
  if (tokenCheck.includes('tokens no aplicados') || tokenCheck.includes('encontrados')) {
    score -= 10;
    warnings.push('Algunos tokens no están aplicados');
  }
} catch (e) {
  // Puede ser que el script falle, no penalizar mucho
  score -= 5;
  warnings.push('No se pudo verificar tokens (script puede no existir)');
}

// 5. Verificar PNGs exportados (+5 si existen)
const pngDir = path.join(ROOT_DIR, 'exports/png');
if (fs.existsSync(pngDir)) {
  try {
    const pngCount = execSync(
      `find "${pngDir}" -name "*.png" 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim();
    
    if (parseInt(pngCount) > 0) {
      score = Math.min(100, score + 5);
    }
  } catch (e) {
    // Ignorar
  }
} else {
  warnings.push('PNGs no exportados');
}

// 6. Verificar validación reciente (+5 si hay reportes recientes)
const reportsDir = path.join(ROOT_DIR, 'exports/reports');
if (fs.existsSync(reportsDir)) {
  try {
    const reports = fs.readdirSync(reportsDir);
    if (reports.length > 0) {
      score = Math.min(100, score + 5);
    }
  } catch (e) {
    // Ignorar
  }
}

// 7. Verificar optimización SVGs (+5 si existe carpeta)
const svgOptDir = path.join(ROOT_DIR, 'exports/svg_opt');
if (fs.existsSync(svgOptDir)) {
  try {
    const optCount = execSync(
      `find "${svgOptDir}" -name "*.svg" 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim();
    
    if (parseInt(optCount) > 0) {
      score = Math.min(100, score + 5);
    }
  } catch (e) {
    // Ignorar
  }
}

// Asegurar que el score esté entre 0 y 100
score = Math.max(0, Math.min(100, score));

// Determinar estado
let status;
let emoji;
if (score >= 90) {
  status = 'Excelente';
  emoji = '🟢';
} else if (score >= 70) {
  status = 'Bueno';
  emoji = '🟡';
} else if (score >= 50) {
  status = 'Regular';
  emoji = '🟠';
} else {
  status = 'Crítico';
  emoji = '🔴';
}

// Generar reporte
const report = {
  timestamp: new Date().toISOString(),
  score: score,
  status: status,
  issues: issues,
  warnings: warnings,
  recommendations: [
    issues.length > 0 ? 'Ejecutar: bash tools/auto_fix_issues.sh' : null,
    warnings.length > 0 ? 'Revisar: node tools/smart_recommendations.js' : null,
    score < 70 ? 'Ejecutar: bash tools/run_all_validations.sh' : null,
    'Mantener: bash tools/health_check.sh regularmente'
  ].filter(Boolean)
};

fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
fs.writeFileSync(OUTPUT_FILE, JSON.stringify(report, null, 2));

// Mostrar resultado
console.log(`${emoji} Health Score: ${score}/100 - ${status}`);
console.log('');

if (issues.length > 0) {
  console.log('❌ Problemas detectados:');
  issues.forEach(issue => console.log(`   - ${issue}`));
  console.log('');
}

if (warnings.length > 0) {
  console.log('⚠️  Advertencias:');
  warnings.forEach(warning => console.log(`   - ${warning}`));
  console.log('');
}

if (score >= 90) {
  console.log('✅ Sistema en excelente estado');
} else if (score >= 70) {
  console.log('💡 Sistema saludable, pero hay oportunidades de mejora');
} else {
  console.log('🔧 Se requiere atención inmediata');
  console.log('   Ejecutar: bash tools/auto_fix_issues.sh');
}

console.log('');
console.log(`📄 Reporte completo: ${OUTPUT_FILE}`);


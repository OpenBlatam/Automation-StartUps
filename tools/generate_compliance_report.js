#!/usr/bin/env node
/**
 * Genera reporte de compliance: verifica cumplimiento de estándares y políticas
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const REPORT_FILE = path.join(ROOT_DIR, 'exports/compliance_report.json');
const REPORT_HTML = path.join(ROOT_DIR, 'exports/compliance_report.html');

console.log('📋 Generando Reporte de Compliance');
console.log('==================================');
console.log('');

const compliance = {
  timestamp: new Date().toISOString(),
  standards: {
    instagram: {},
    linkedin: {},
    general: {}
  },
  checks: [],
  score: 0,
  passed: 0,
  failed: 0,
  warnings: 0
};

// Verificar dimensiones de Instagram
function checkInstagramCompliance() {
  const checks = [];
  
  const requiredSizes = [
    { name: 'Feed', width: 1080, height: 1080 },
    { name: 'Stories', width: 1080, height: 1920 },
    { name: 'Reels', width: 1080, height: 1920 }
  ];
  
  // Verificar SVGs con dimensiones correctas
  const instagramDir = path.join(ROOT_DIR, 'design/instagram');
  if (fs.existsSync(instagramDir)) {
    requiredSizes.forEach(size => {
      const dir = path.join(instagramDir, `${size.width}x${size.height}`);
      if (fs.existsSync(dir)) {
        const svgs = fs.readdirSync(dir).filter(f => f.endsWith('.svg'));
        checks.push({
          name: `Instagram ${size.name} (${size.width}x${size.height})`,
          status: svgs.length > 0 ? 'passed' : 'warning',
          message: svgs.length > 0 ? `${svgs.length} asset(s) encontrado(s)` : 'No assets encontrados',
          required: true
        });
      } else {
        checks.push({
          name: `Instagram ${size.name} (${size.width}x${size.height})`,
          status: 'warning',
          message: 'Directorio no encontrado',
          required: false
        });
      }
    });
  }
  
  compliance.standards.instagram = { checks };
}

// Verificar dimensiones de LinkedIn
function checkLinkedInCompliance() {
  const checks = [];
  
  const requiredSize = { name: 'LinkedIn Post', width: 1200, height: 627 };
  const linkedinDir = path.join(ROOT_DIR, 'ads/linkedin');
  
  if (fs.existsSync(linkedinDir)) {
    const svgs = fs.readdirSync(linkedinDir)
      .filter(f => f.endsWith('.svg'))
      .map(f => {
        const content = fs.readFileSync(path.join(linkedinDir, f), 'utf8');
        const viewBoxMatch = content.match(/viewBox=["']0 0 (\d+) (\d+)["']/);
        return {
          file: f,
          width: viewBoxMatch ? parseInt(viewBoxMatch[1]) : null,
          height: viewBoxMatch ? parseInt(viewBoxMatch[2]) : null
        };
      });
    
    checks.push({
      name: `${requiredSize.name} (${requiredSize.width}x${requiredSize.height})`,
      status: svgs.length > 0 ? 'passed' : 'warning',
      message: `${svgs.length} asset(s) encontrado(s)`,
      required: true
    });
  } else {
    checks.push({
      name: `${requiredSize.name} (${requiredSize.width}x${requiredSize.height})`,
      status: 'warning',
      message: 'Directorio no encontrado',
      required: false
    });
  }
  
  compliance.standards.linkedin = { checks };
}

// Verificar cumplimiento general
function checkGeneralCompliance() {
  const checks = [];
  
  // Alt text para accesibilidad
  const altTextFile = path.join(ROOT_DIR, 'design/instagram/accessibility/alt_text.csv');
  if (fs.existsSync(altTextFile)) {
    checks.push({
      name: 'Alt text para accesibilidad',
      status: 'passed',
      message: 'Archivo alt_text.csv encontrado',
      required: true
    });
  } else {
    checks.push({
      name: 'Alt text para accesibilidad',
      status: 'warning',
      message: 'alt_text.csv no encontrado',
      required: false
    });
  }
  
  // QA Checklist
  const qaFile = path.join(ROOT_DIR, 'design/instagram/qa/qa_checklist.md');
  if (fs.existsSync(qaFile)) {
    checks.push({
      name: 'QA Checklist',
      status: 'passed',
      message: 'Checklist de QA presente',
      required: true
    });
  } else {
    checks.push({
      name: 'QA Checklist',
      status: 'warning',
      message: 'QA checklist no encontrado',
      required: false
    });
  }
  
  // Tokens configurados
  const tokensFile = path.join(ROOT_DIR, 'design/instagram/tokens.json');
  if (fs.existsSync(tokensFile)) {
    try {
      const tokens = JSON.parse(fs.readFileSync(tokensFile, 'utf8'));
      if (!tokens.URL || tokens.URL.includes('ejemplo.com') || tokens.URL.includes('tu-sitio.com')) {
        checks.push({
          name: 'Tokens configurados',
          status: 'warning',
          message: 'Tokens con valores por defecto',
          required: true
        });
      } else {
        checks.push({
          name: 'Tokens configurados',
          status: 'passed',
          message: 'Tokens configurados correctamente',
          required: true
        });
      }
    } catch (e) {
      checks.push({
        name: 'Tokens configurados',
        status: 'failed',
        message: 'Error leyendo tokens.json',
        required: true
      });
    }
  } else {
    checks.push({
      name: 'Tokens configurados',
      status: 'failed',
      message: 'tokens.json no encontrado',
      required: true
    });
  }
  
  compliance.standards.general = { checks };
}

// Ejecutar todas las verificaciones
checkInstagramCompliance();
checkLinkedInCompliance();
checkGeneralCompliance();

// Consolidar todos los checks
compliance.checks = [
  ...(compliance.standards.instagram.checks || []),
  ...(compliance.standards.linkedin.checks || []),
  ...(compliance.standards.general.checks || [])
];

// Calcular score
compliance.checks.forEach(check => {
  if (check.status === 'passed') {
    compliance.passed++;
    compliance.score += check.required ? 10 : 5;
  } else if (check.status === 'warning') {
    compliance.warnings++;
    compliance.score += check.required ? 3 : 5;
  } else {
    compliance.failed++;
    if (check.required) {
      compliance.score -= 10;
    }
  }
});

compliance.score = Math.max(0, Math.min(100, compliance.score));

// Generar JSON
fs.mkdirSync(path.dirname(REPORT_FILE), { recursive: true });
fs.writeFileSync(REPORT_FILE, JSON.stringify(compliance, null, 2));

// Generar HTML
const html = `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reporte de Compliance</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #f5f5f5;
      padding: 20px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
      background: white;
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    h1 { color: #333; margin-bottom: 10px; }
    .subtitle { color: #666; margin-bottom: 30px; }
    .score-badge {
      display: inline-block;
      padding: 10px 20px;
      border-radius: 8px;
      font-size: 2em;
      font-weight: bold;
      margin-bottom: 20px;
    }
    .score-excellent { background: #4caf50; color: white; }
    .score-good { background: #8bc34a; color: white; }
    .score-warning { background: #ff9800; color: white; }
    .score-failed { background: #f44336; color: white; }
    .check-item {
      padding: 15px;
      margin-bottom: 10px;
      border-radius: 8px;
      border-left: 4px solid;
    }
    .check-passed { background: #e8f5e9; border-color: #4caf50; }
    .check-warning { background: #fff3e0; border-color: #ff9800; }
    .check-failed { background: #ffebee; border-color: #f44336; }
    .check-name { font-weight: bold; margin-bottom: 5px; }
    .check-message { color: #666; font-size: 0.9em; }
    .section { margin-top: 30px; }
    .section h2 { color: #333; margin-bottom: 15px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>📋 Reporte de Compliance</h1>
    <div class="subtitle">Generado: ${new Date().toLocaleString()}</div>
    
    <div class="score-badge ${
      compliance.score >= 90 ? 'score-excellent' :
      compliance.score >= 70 ? 'score-good' :
      compliance.score >= 50 ? 'score-warning' : 'score-failed'
    }">
      Score: ${compliance.score}/100
    </div>
    
    <div>
      <strong>✅ Pasados:</strong> ${compliance.passed}<br>
      <strong>⚠️ Advertencias:</strong> ${compliance.warnings}<br>
      <strong>❌ Fallidos:</strong> ${compliance.failed}
    </div>
    
    ${['Instagram', 'LinkedIn', 'General'].map(platform => {
      const checks = compliance.standards[platform.toLowerCase()]?.checks || [];
      if (checks.length === 0) return '';
      
      return `
        <div class="section">
          <h2>${platform}</h2>
          ${checks.map(check => `
            <div class="check-item check-${check.status}">
              <div class="check-name">
                ${check.status === 'passed' ? '✅' : check.status === 'warning' ? '⚠️' : '❌'} 
                ${check.name}
                ${check.required ? '<span style="color: #999; font-size: 0.8em;">(Requerido)</span>' : ''}
              </div>
              <div class="check-message">${check.message}</div>
            </div>
          `).join('')}
        </div>
      `;
    }).join('')}
  </div>
</body>
</html>
`;

fs.writeFileSync(REPORT_HTML, html);

console.log('✅ Reporte de compliance generado:');
console.log(`   JSON: ${REPORT_FILE}`);
console.log(`   HTML: ${REPORT_HTML}`);
console.log('');
console.log(`📊 Score: ${compliance.score}/100`);
console.log(`   ✅ Pasados: ${compliance.passed}`);
console.log(`   ⚠️  Advertencias: ${compliance.warnings}`);
console.log(`   ❌ Fallidos: ${compliance.failed}`);


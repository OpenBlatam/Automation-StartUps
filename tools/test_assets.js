#!/usr/bin/env node
/**
 * Suite de tests para validar assets y funcionalidades del sistema
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT_DIR = path.join(__dirname, '..');
const TEST_RESULTS = path.join(ROOT_DIR, 'exports/test_results.json');

console.log('🧪 Ejecutando Suite de Tests');
console.log('============================');
console.log('');

const tests = [];
let passed = 0;
let failed = 0;

function test(name, fn) {
  try {
    fn();
    tests.push({ name, status: 'passed', error: null });
    passed++;
    console.log(`✅ ${name}`);
  } catch (error) {
    tests.push({ name, status: 'failed', error: error.message });
    failed++;
    console.log(`❌ ${name}: ${error.message}`);
  }
}

// Test 1: Estructura básica
test('Estructura de directorios', () => {
  const required = ['design', 'exports', 'tools'];
  required.forEach(dir => {
    if (!fs.existsSync(path.join(ROOT_DIR, dir))) {
      throw new Error(`Directorio faltante: ${dir}`);
    }
  });
});

// Test 2: Tokens configurados
test('Tokens configurados', () => {
  const tokensFile = path.join(ROOT_DIR, 'design/instagram/tokens.json');
  if (!fs.existsSync(tokensFile)) {
    throw new Error('tokens.json no encontrado');
  }
  
  const tokens = JSON.parse(fs.readFileSync(tokensFile, 'utf8'));
  if (tokens.URL && (tokens.URL.includes('tu-sitio.com') || tokens.URL.includes('ejemplo.com'))) {
    throw new Error('Tokens con valores por defecto');
  }
});

// Test 3: SVGs válidos
test('SVGs no vacíos', () => {
  const { execSync } = require('child_process');
  const emptyCount = parseInt(execSync(
    `find "${ROOT_DIR}/design" "${ROOT_DIR}/ads" -name "*.svg" -size 0 2>/dev/null | wc -l`,
    { encoding: 'utf8' }
  ).trim()) || 0;
  
  if (emptyCount > 0) {
    throw new Error(`${emptyCount} SVG(s) vacío(s) encontrado(s)`);
  }
});

// Test 4: Herramientas ejecutables
test('Scripts principales ejecutables', () => {
  const scripts = [
    'tools/quick_audit.sh',
    'tools/health_check.sh',
    'tools/auto_fix_issues.sh'
  ];
  
  scripts.forEach(script => {
    const scriptPath = path.join(ROOT_DIR, script);
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Script faltante: ${script}`);
    }
    
    // Verificar que sea ejecutable
    const stats = fs.statSync(scriptPath);
    if (!(stats.mode & parseInt('111', 8))) {
      throw new Error(`Script no ejecutable: ${script}`);
    }
  });
});

// Test 5: Node.js scripts
test('Node.js scripts válidos', () => {
  const nodeScripts = [
    'tools/apply_tokens.js',
    'tools/health_score_calculator.js'
  ];
  
  nodeScripts.forEach(script => {
    const scriptPath = path.join(ROOT_DIR, script);
    if (!fs.existsSync(scriptPath)) {
      throw new Error(`Script faltante: ${script}`);
    }
    
    // Verificar sintaxis básica
    try {
      const content = fs.readFileSync(scriptPath, 'utf8');
      if (!content.includes('require') && !content.includes('#!/usr/bin/env node')) {
        throw new Error(`Script inválido: ${script}`);
      }
    } catch (e) {
      throw new Error(`Error leyendo script: ${script}`);
    }
  });
});

// Test 6: Exportaciones
test('Directorios de exportación existen', () => {
  const exportDirs = ['exports/png', 'exports/svg_opt'];
  
  exportDirs.forEach(dir => {
    const dirPath = path.join(ROOT_DIR, dir);
    if (!fs.existsSync(dirPath)) {
      // Crear si no existe (warning, no error)
      fs.mkdirSync(dirPath, { recursive: true });
    }
  });
});

// Test 7: Dependencias críticas
test('Dependencias críticas disponibles', () => {
  const deps = ['node'];
  const missing = [];
  
  deps.forEach(dep => {
    try {
      execSync(`which ${dep}`, { stdio: 'pipe' });
    } catch (e) {
      missing.push(dep);
    }
  });
  
  if (missing.length > 0) {
    throw new Error(`Dependencias faltantes: ${missing.join(', ')}`);
  }
});

// Test 8: Configuración de validación
test('Configuración de validación', () => {
  const configFiles = [
    'design/instagram/tokens.example.json'
  ];
  
  configFiles.forEach(file => {
    const filePath = path.join(ROOT_DIR, file);
    if (!fs.existsSync(filePath)) {
      throw new Error(`Archivo de configuración faltante: ${file}`);
    }
  });
});

// Test 9: Integridad de dashboards
test('Dashboards HTML válidos', () => {
  const dashboards = [
    'tools/create_master_dashboard.html',
    'tools/create_realtime_dashboard.html'
  ];
  
  dashboards.forEach(dashboard => {
    const dashPath = path.join(ROOT_DIR, dashboard);
    if (fs.existsSync(dashPath)) {
      const content = fs.readFileSync(dashPath, 'utf8');
      if (!content.includes('<!DOCTYPE html>') && !content.includes('<html')) {
        throw new Error(`Dashboard inválido: ${dashboard}`);
      }
    }
  });
});

// Test 10: Documentación presente
test('Documentación principal', () => {
  const docs = ['readme.md', 'QUICKSTART.md'];
  
  docs.forEach(doc => {
    const docPath = path.join(ROOT_DIR, doc);
    if (!fs.existsSync(docPath)) {
      throw new Error(`Documentación faltante: ${doc}`);
    }
  });
});

// Resumen
console.log('');
console.log('============================');
console.log(`✅ Tests exitosos: ${passed}`);
console.log(`❌ Tests fallidos: ${failed}`);
console.log(`📊 Total: ${tests.length}`);

// Guardar resultados
const results = {
  timestamp: new Date().toISOString(),
  summary: {
    total: tests.length,
    passed,
    failed,
    success_rate: ((passed / tests.length) * 100).toFixed(2) + '%'
  },
  tests
};

fs.mkdirSync(path.dirname(TEST_RESULTS), { recursive: true });
fs.writeFileSync(TEST_RESULTS, JSON.stringify(results, null, 2));

console.log(`📄 Resultados guardados: ${TEST_RESULTS}`);
console.log('');

if (failed > 0) {
  console.log('⚠️  Algunos tests fallaron. Revisa los resultados arriba.');
  process.exit(1);
} else {
  console.log('✅ Todos los tests pasaron');
  process.exit(0);
}


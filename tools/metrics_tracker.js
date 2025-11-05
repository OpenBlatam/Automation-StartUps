#!/usr/bin/env node
/**
 * Sistema de tracking y métricas en el tiempo
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const METRICS_DIR = path.join(ROOT_DIR, 'exports/metrics_history');
const LATEST_METRICS = path.join(ROOT_DIR, 'exports/latest_metrics.json');

console.log('📈 Sistema de Tracking de Métricas');
console.log('==================================');
console.log('');

// Crear directorio de historial
fs.mkdirSync(METRICS_DIR, { recursive: true });

// Recopilar métricas actuales
const metrics = {
  timestamp: new Date().toISOString(),
  date: new Date().toISOString().split('T')[0],
  assets: {},
  system: {},
  performance: {},
  quality: {}
};

// Métricas de assets
function collectAssetMetrics() {
  const { execSync } = require('child_process');
  
  try {
    // Contar SVGs por plataforma
    const instagramSvgs = parseInt(execSync(
      `find "${ROOT_DIR}/design/instagram" -name "*.svg" 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim()) || 0;
    
    const linkedinSvgs = parseInt(execSync(
      `find "${ROOT_DIR}/ads/linkedin" -name "*.svg" 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim()) || 0;
    
    const webinarSvgs = parseInt(execSync(
      `find "${ROOT_DIR}/ads/webinars" -name "*.svg" 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim()) || 0;
    
    metrics.assets = {
      total_svgs: instagramSvgs + linkedinSvgs + webinarSvgs,
      instagram: instagramSvgs,
      linkedin: linkedinSvgs,
      webinars: webinarSvgs,
      pngs_1x: 0,
      pngs_2x: 0
    };
    
    // Contar PNGs
    const png1xDir = path.join(ROOT_DIR, 'exports/png/1x');
    const png2xDir = path.join(ROOT_DIR, 'exports/png/2x');
    
    if (fs.existsSync(png1xDir)) {
      metrics.assets.pngs_1x = fs.readdirSync(png1xDir)
        .filter(f => f.endsWith('.png')).length;
    }
    
    if (fs.existsSync(png2xDir)) {
      metrics.assets.pngs_2x = fs.readdirSync(png2xDir)
        .filter(f => f.endsWith('.png')).length;
    }
  } catch (e) {
    console.warn('⚠️  Error recopilando métricas de assets');
  }
}

// Métricas del sistema
function collectSystemMetrics() {
  // Health score
  const healthFile = path.join(ROOT_DIR, 'exports/health_score.json');
  if (fs.existsSync(healthFile)) {
    try {
      const health = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
      metrics.system.health_score = health.score || 0;
      metrics.system.health_status = health.status || 'unknown';
    } catch (e) {
      metrics.system.health_score = null;
    }
  }
  
  // Tokens configurados
  const tokensFile = path.join(ROOT_DIR, 'design/instagram/tokens.json');
  metrics.system.tokens_configured = fs.existsSync(tokensFile);
  
  // Backups recientes
  const backupsDir = path.join(ROOT_DIR, 'backups/assets');
  if (fs.existsSync(backupsDir)) {
    const backups = fs.readdirSync(backupsDir)
      .filter(f => f.endsWith('.tar.gz'))
      .map(f => ({
        name: f,
        mtime: fs.statSync(path.join(backupsDir, f)).mtime
      }))
      .sort((a, b) => b.mtime - a.mtime);
    
    if (backups.length > 0) {
      const latestBackup = backups[0];
      const hoursSinceBackup = (Date.now() - latestBackup.mtime) / (1000 * 60 * 60);
      metrics.system.last_backup_hours_ago = Math.round(hoursSinceBackup);
      metrics.system.backup_count = backups.length;
    }
  }
}

// Métricas de calidad
function collectQualityMetrics() {
  const { execSync } = require('child_process');
  
  try {
    // SVGs vacíos
    const emptySvgs = parseInt(execSync(
      `find "${ROOT_DIR}/design" "${ROOT_DIR}/ads" -name "*.svg" -size 0 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim()) || 0;
    
    metrics.quality.empty_svgs = emptySvgs;
    
    // SVGs grandes (>100KB)
    const largeSvgs = parseInt(execSync(
      `find "${ROOT_DIR}/design" "${ROOT_DIR}/ads" -name "*.svg" -size +100k 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim()) || 0;
    
    metrics.quality.large_svgs = largeSvgs;
  } catch (e) {
    // Ignorar errores
  }
}

// Métricas de performance
function collectPerformanceMetrics() {
  // Buscar último benchmark
  const exportsDir = path.join(ROOT_DIR, 'exports');
  if (fs.existsSync(exportsDir)) {
    const benchmarkFiles = fs.readdirSync(exportsDir)
      .filter(f => f.startsWith('benchmark_') && f.endsWith('.json'))
      .map(f => path.join(exportsDir, f))
      .filter(f => fs.existsSync(f))
      .map(f => ({
        path: f,
        mtime: fs.statSync(f).mtime
      }))
      .sort((a, b) => b.mtime - a.mtime);
    
    if (benchmarkFiles.length > 0) {
      try {
        const latestBenchmark = JSON.parse(
          fs.readFileSync(benchmarkFiles[0].path, 'utf8')
        );
        metrics.performance.last_benchmark_total_time = latestBenchmark.summary?.total_duration || null;
        metrics.performance.last_benchmark_date = benchmarkFiles[0].mtime.toISOString();
      } catch (e) {
        // Ignorar errores
      }
    }
  }
}

// Recopilar todas las métricas
collectAssetMetrics();
collectSystemMetrics();
collectQualityMetrics();
collectPerformanceMetrics();

// Guardar métricas actuales
fs.writeFileSync(LATEST_METRICS, JSON.stringify(metrics, null, 2));

// Guardar en historial (un archivo por día)
const historyFile = path.join(METRICS_DIR, `metrics_${metrics.date}.json`);
let historyData = {};

if (fs.existsSync(historyFile)) {
  try {
    historyData = JSON.parse(fs.readFileSync(historyFile, 'utf8'));
  } catch (e) {
    historyData = { date: metrics.date, entries: [] };
  }
}

if (!historyData.entries) {
  historyData.entries = [];
}

historyData.entries.push(metrics);
historyData.last_updated = new Date().toISOString();

fs.writeFileSync(historyFile, JSON.stringify(historyData, null, 2));

// Mostrar resumen
console.log('✅ Métricas recopiladas:');
console.log(`   📊 Assets SVG: ${metrics.assets.total_svgs}`);
console.log(`   🏥 Health Score: ${metrics.system.health_score || 'N/A'}`);
console.log(`   💾 Backups: ${metrics.system.backup_count || 0}`);
console.log(`   ⚠️  SVGs vacíos: ${metrics.quality.empty_svgs}`);
console.log(`   📦 PNGs: ${metrics.assets.pngs_1x} (1x) + ${metrics.assets.pngs_2x} (2x)`);
console.log('');
console.log(`📄 Métricas guardadas:`);
console.log(`   Actual: ${LATEST_METRICS}`);
console.log(`   Historial: ${historyFile}`);
console.log('');

// Mostrar tendencias si hay datos históricos
const historyFiles = fs.readdirSync(METRICS_DIR)
  .filter(f => f.startsWith('metrics_') && f.endsWith('.json'))
  .sort()
  .reverse()
  .slice(0, 7); // Últimos 7 días

if (historyFiles.length > 1) {
  console.log('📈 Tendencia (últimos 7 días):');
  console.log('   Fecha       | SVGs | Health | Backups');
  console.log('   ------------+------+--------+--------');
  
  historyFiles.forEach(file => {
    try {
      const data = JSON.parse(
        fs.readFileSync(path.join(METRICS_DIR, file), 'utf8')
      );
      if (data.entries && data.entries.length > 0) {
        const latest = data.entries[data.entries.length - 1];
        const date = data.date || file.replace('metrics_', '').replace('.json', '');
        console.log(
          `   ${date} | ${String(latest.assets?.total_svgs || 0).padEnd(4)} | ` +
          `${String(latest.system?.health_score || 'N/A').padEnd(6)} | ${latest.system?.backup_count || 0}`
        );
      }
    } catch (e) {
      // Ignorar errores
    }
  });
}


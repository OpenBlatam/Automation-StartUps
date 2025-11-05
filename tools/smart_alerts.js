#!/usr/bin/env node
/**
 * Sistema de alertas inteligentes basado en umbrales y condiciones
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const ALERTS_FILE = path.join(ROOT_DIR, 'exports/smart_alerts.json');
const CONFIG_FILE = path.join(ROOT_DIR, 'exports/alert_config.json');

// Configuración de alertas por defecto
const defaultConfig = {
  thresholds: {
    healthScore: { min: 70, critical: 50 },
    svgCount: { min: 10 },
    emptySvgs: { max: 0, critical: 5 },
    tokensNotApplied: { max: 0, critical: 10 },
    largeSvgs: { max: 3, critical: 10 },
    backupAge: { maxHours: 24, critical: 48 }
  },
  enabled: true,
  notifications: {
    console: true,
    file: true,
    email: false
  }
};

// Cargar configuración
let config = defaultConfig;
if (fs.existsSync(CONFIG_FILE)) {
  try {
    config = { ...defaultConfig, ...JSON.parse(fs.readFileSync(CONFIG_FILE, 'utf8')) };
  } catch (e) {
    console.warn('⚠️  Error cargando configuración, usando defaults');
  }
}

const alerts = {
  critical: [],
  warning: [],
  info: [],
  timestamp: new Date().toISOString()
};

console.log('🔔 Sistema de Alertas Inteligentes');
console.log('==================================');
console.log('');

// 1. Verificar Health Score
function checkHealthScore() {
  const healthFile = path.join(ROOT_DIR, 'exports/health_score.json');
  if (fs.existsSync(healthFile)) {
    try {
      const health = JSON.parse(fs.readFileSync(healthFile, 'utf8'));
      const score = health.score || 0;
      
      if (score < config.thresholds.healthScore.critical) {
        alerts.critical.push({
          type: 'health_score',
          message: `Health score crítico: ${score}/100`,
          action: 'bash tools/auto_fix_issues.sh',
          value: score,
          threshold: config.thresholds.healthScore.critical
        });
      } else if (score < config.thresholds.healthScore.min) {
        alerts.warning.push({
          type: 'health_score',
          message: `Health score bajo: ${score}/100`,
          action: 'node tools/smart_recommendations.js',
          value: score,
          threshold: config.thresholds.healthScore.min
        });
      } else if (score >= 90) {
        alerts.info.push({
          type: 'health_score',
          message: `Health score excelente: ${score}/100`,
          value: score
        });
      }
    } catch (e) {
      alerts.warning.push({
        type: 'health_score',
        message: 'No se pudo leer health score',
        action: 'node tools/health_score_calculator.js'
      });
    }
  } else {
    alerts.warning.push({
      type: 'health_score',
      message: 'Health score no generado',
      action: 'node tools/health_score_calculator.js'
    });
  }
}

// 2. Verificar SVGs vacíos
function checkEmptySvgs() {
  const { execSync } = require('child_process');
  try {
    const emptyCount = parseInt(execSync(
      `find "${ROOT_DIR}/design" "${ROOT_DIR}/ads" -name "*.svg" -size 0 2>/dev/null | wc -l`,
      { encoding: 'utf8' }
    ).trim()) || 0;
    
    if (emptyCount > config.thresholds.emptySvgs.critical) {
      alerts.critical.push({
        type: 'empty_svgs',
        message: `${emptyCount} SVG(s) vacío(s) detectado(s)`,
        action: 'bash tools/fix_broken_svgs.sh',
        value: emptyCount,
        threshold: config.thresholds.emptySvgs.critical
      });
    } else if (emptyCount > config.thresholds.emptySvgs.max) {
      alerts.warning.push({
        type: 'empty_svgs',
        message: `${emptyCount} SVG(s) vacío(s)`,
        action: 'bash tools/fix_broken_svgs.sh',
        value: emptyCount
      });
    }
  } catch (e) {
    // Ignorar errores
  }
}

// 3. Verificar tokens
function checkTokens() {
  const tokensFile = path.join(ROOT_DIR, 'design/instagram/tokens.json');
  if (!fs.existsSync(tokensFile)) {
    alerts.critical.push({
      type: 'tokens',
      message: 'tokens.json no encontrado',
      action: 'cp design/instagram/tokens.example.json design/instagram/tokens.json'
    });
  } else {
    try {
      const tokens = JSON.parse(fs.readFileSync(tokensFile, 'utf8'));
      if (tokens.URL && (tokens.URL.includes('tu-sitio.com') || tokens.URL.includes('ejemplo.com'))) {
        alerts.warning.push({
          type: 'tokens',
          message: 'Tokens con valores por defecto',
          action: 'Editar design/instagram/tokens.json'
        });
      }
    } catch (e) {
      alerts.warning.push({
        type: 'tokens',
        message: 'tokens.json inválido',
        action: 'Verificar sintaxis JSON'
      });
    }
  }
}

// 4. Verificar backups recientes
function checkBackups() {
  const backupsDir = path.join(ROOT_DIR, 'backups/assets');
  if (!fs.existsSync(backupsDir)) {
    alerts.warning.push({
      type: 'backup',
      message: 'No hay backups recientes',
      action: 'bash tools/auto_backup.sh'
    });
    return;
  }
  
  try {
    const backups = fs.readdirSync(backupsDir)
      .filter(f => f.endsWith('.tar.gz'))
      .map(f => ({
        name: f,
        path: path.join(backupsDir, f),
        mtime: fs.statSync(path.join(backupsDir, f)).mtime
      }))
      .sort((a, b) => b.mtime - a.mtime);
    
    if (backups.length === 0) {
      alerts.warning.push({
        type: 'backup',
        message: 'No hay backups disponibles',
        action: 'bash tools/auto_backup.sh'
      });
    } else {
      const latestBackup = backups[0];
      const hoursSinceBackup = (Date.now() - latestBackup.mtime) / (1000 * 60 * 60);
      
      if (hoursSinceBackup > config.thresholds.backupAge.critical) {
        alerts.critical.push({
          type: 'backup',
          message: `Último backup hace ${Math.round(hoursSinceBackup)} horas`,
          action: 'bash tools/auto_backup.sh',
          value: hoursSinceBackup,
          threshold: config.thresholds.backupAge.critical
        });
      } else if (hoursSinceBackup > config.thresholds.backupAge.maxHours) {
        alerts.warning.push({
          type: 'backup',
          message: `Último backup hace ${Math.round(hoursSinceBackup)} horas`,
          action: 'bash tools/auto_backup.sh',
          value: hoursSinceBackup
        });
      } else {
        alerts.info.push({
          type: 'backup',
          message: `Backup reciente: ${Math.round(hoursSinceBackup)} horas atrás`,
          value: hoursSinceBackup
        });
      }
    }
  } catch (e) {
    // Ignorar errores
  }
}

// 5. Verificar PNGs exportados
function checkPngs() {
  const pngDir = path.join(ROOT_DIR, 'exports/png');
  if (!fs.existsSync(pngDir)) {
    alerts.warning.push({
      type: 'pngs',
      message: 'PNGs no exportados',
      action: 'bash tools/export_png.sh'
    });
  } else {
    const png1x = fs.existsSync(path.join(pngDir, '1x')) 
      ? fs.readdirSync(path.join(pngDir, '1x')).filter(f => f.endsWith('.png')).length 
      : 0;
    const png2x = fs.existsSync(path.join(pngDir, '2x'))
      ? fs.readdirSync(path.join(pngDir, '2x')).filter(f => f.endsWith('.png')).length
      : 0;
    
    if (png1x === 0 && png2x === 0) {
      alerts.warning.push({
        type: 'pngs',
        message: 'PNGs no exportados',
        action: 'bash tools/export_png.sh'
      });
    }
  }
}

// Ejecutar todas las verificaciones
checkHealthScore();
checkEmptySvgs();
checkTokens();
checkBackups();
checkPngs();

// Generar reporte
fs.mkdirSync(path.dirname(ALERTS_FILE), { recursive: true });
fs.writeFileSync(ALERTS_FILE, JSON.stringify(alerts, null, 2));

// Mostrar alertas
if (alerts.critical.length > 0) {
  console.log('🔴 ALERTAS CRÍTICAS:');
  alerts.critical.forEach((alert, i) => {
    console.log(`   ${i + 1}. ${alert.message}`);
    if (alert.action) console.log(`      Acción: ${alert.action}`);
  });
  console.log('');
}

if (alerts.warning.length > 0) {
  console.log('🟠 ADVERTENCIAS:');
  alerts.warning.forEach((alert, i) => {
    console.log(`   ${i + 1}. ${alert.message}`);
    if (alert.action) console.log(`      Acción: ${alert.action}`);
  });
  console.log('');
}

if (alerts.info.length > 0) {
  console.log('🔵 INFORMACIÓN:');
  alerts.info.forEach((alert, i) => {
    console.log(`   ${i + 1}. ${alert.message}`);
  });
  console.log('');
}

if (alerts.critical.length === 0 && alerts.warning.length === 0) {
  console.log('✅ Sin alertas - Sistema en buen estado');
}

console.log(`📄 Reporte completo: ${ALERTS_FILE}`);
console.log('');

if (alerts.critical.length > 0) {
  process.exit(1);
} else if (alerts.warning.length > 0) {
  process.exit(0);
} else {
  process.exit(0);
}


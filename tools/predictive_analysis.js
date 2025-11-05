#!/usr/bin/env node
/**
 * Análisis predictivo: predice tendencias y problemas potenciales
 */

const fs = require('fs');
const path = require('path');

const ROOT_DIR = path.join(__dirname, '..');
const OUTPUT_FILE = path.join(ROOT_DIR, 'exports/predictive_analysis.json');

console.log('🔮 Análisis Predictivo');
console.log('======================');
console.log('');

const predictions = {
  timestamp: new Date().toISOString(),
  trends: [],
  warnings: [],
  recommendations: [],
  metrics_forecast: {}
};

// Analizar histórico de métricas
function analyzeTrends() {
  const metricsDir = path.join(ROOT_DIR, 'exports/metrics_history');
  
  if (!fs.existsSync(metricsDir)) {
    predictions.warnings.push({
      type: 'no_history',
      message: 'No hay datos históricos suficientes para análisis predictivo',
      action: 'Ejecutar: node tools/metrics_tracker.js regularmente'
    });
    return;
  }
  
  const historyFiles = fs.readdirSync(metricsDir)
    .filter(f => f.startsWith('metrics_') && f.endsWith('.json'))
    .map(f => path.join(metricsDir, f))
    .filter(f => fs.existsSync(f))
    .sort()
    .reverse()
    .slice(0, 7); // Últimos 7 días
  
  if (historyFiles.length < 3) {
    predictions.warnings.push({
      type: 'insufficient_data',
      message: 'Se necesitan al menos 3 días de datos para análisis predictivo',
      action: 'Ejecutar: node tools/metrics_tracker.js'
    });
    return;
  }
  
  // Analizar tendencia de health score
  const healthScores = [];
  const assetCounts = [];
  
  historyFiles.forEach(file => {
    try {
      const data = JSON.parse(fs.readFileSync(file, 'utf8'));
      if (data.entries && data.entries.length > 0) {
        const latest = data.entries[data.entries.length - 1];
        if (latest.system?.health_score) {
          healthScores.push(latest.system.health_score);
        }
        if (latest.assets?.total_svgs) {
          assetCounts.push(latest.assets.total_svgs);
        }
      }
    } catch (e) {
      // Ignorar errores
    }
  });
  
  // Calcular tendencia
  if (healthScores.length >= 3) {
    const recent = healthScores.slice(0, 3);
    const older = healthScores.slice(3);
    
    if (older.length > 0) {
      const recentAvg = recent.reduce((a, b) => a + b, 0) / recent.length;
      const olderAvg = older.reduce((a, b) => a + b, 0) / older.length;
      const change = recentAvg - olderAvg;
      
      if (change < -5) {
        predictions.warnings.push({
          type: 'health_decline',
          message: `Health score está disminuyendo (${change.toFixed(1)} puntos)`,
          severity: 'high',
          action: 'bash tools/auto_fix_issues.sh'
        });
      } else if (change > 5) {
        predictions.trends.push({
          type: 'health_improvement',
          message: `Health score está mejorando (${change.toFixed(1)} puntos)`,
          confidence: 'high'
        });
      }
      
      // Predicción a 7 días
      const forecast = recentAvg + (change * 2);
      predictions.metrics_forecast.health_score_7days = Math.max(0, Math.min(100, forecast));
    }
  }
  
  // Analizar crecimiento de assets
  if (assetCounts.length >= 3) {
    const growth = assetCounts[0] - assetCounts[assetCounts.length - 1];
    if (growth > 0) {
      predictions.trends.push({
        type: 'asset_growth',
        message: `Crecimiento de assets: +${growth} en últimos ${historyFiles.length} días`,
        confidence: 'medium'
      });
    }
  }
}

// Predecir problemas potenciales
function predictIssues() {
  // Verificar uso de espacio
  try {
    const { execSync } = require('child_process');
    const backupDir = path.join(ROOT_DIR, 'backups/assets');
    
    if (fs.existsSync(backupDir)) {
      const backups = fs.readdirSync(backupDir)
        .filter(f => f.endsWith('.tar.gz'))
        .map(f => {
          const filePath = path.join(backupDir, f);
          return {
            name: f,
            size: fs.statSync(filePath).size
          };
        });
      
      const totalSize = backups.reduce((sum, b) => sum + b.size, 0);
      const sizeMB = totalSize / (1024 * 1024);
      
      if (sizeMB > 500) {
        predictions.warnings.push({
          type: 'storage_warning',
          message: `Backups ocupan ${sizeMB.toFixed(1)} MB. Considerar limpieza`,
          severity: 'low',
          action: 'bash tools/cleanup_reports.sh'
        });
      }
    }
  } catch (e) {
    // Ignorar errores
  }
  
  // Predecir necesidad de mantenimiento
  const maintenanceFile = path.join(ROOT_DIR, 'exports/performance_optimization.txt');
  if (fs.existsSync(maintenanceFile)) {
    const stats = fs.statSync(maintenanceFile);
    const ageHours = (Date.now() - stats.mtime) / (1000 * 60 * 60);
    
    if (ageHours > 72) {
      predictions.recommendations.push({
        type: 'maintenance',
        message: 'Último análisis de performance hace más de 72 horas',
        action: 'bash tools/performance_optimizer.sh',
        priority: 'medium'
      });
    }
  }
}

// Generar recomendaciones predictivas
function generatePredictions() {
  // Basado en patrones históricos
  predictions.recommendations.push({
    type: 'routine',
    message: 'Ejecutar validación completa semanalmente',
    action: 'bash tools/run_all_validations.sh',
    priority: 'low'
  });
  
  predictions.recommendations.push({
    type: 'routine',
    message: 'Regenerar reportes si tienen más de 1 día',
    action: 'bash tools/generate_full_report.sh',
    priority: 'low'
  });
}

// Ejecutar análisis
analyzeTrends();
predictIssues();
generatePredictions();

// Guardar resultados
fs.mkdirSync(path.dirname(OUTPUT_FILE), { recursive: true });
fs.writeFileSync(OUTPUT_FILE, JSON.stringify(predictions, null, 2));

// Mostrar resumen
console.log('✅ Análisis predictivo completado');
console.log('');

if (predictions.trends.length > 0) {
  console.log('📈 Tendencias detectadas:');
  predictions.trends.forEach(trend => {
    console.log(`   • ${trend.message}`);
  });
  console.log('');
}

if (predictions.warnings.length > 0) {
  console.log('⚠️  Advertencias:');
  predictions.warnings.forEach(warning => {
    const icon = warning.severity === 'high' ? '🔴' : '🟡';
    console.log(`   ${icon} ${warning.message}`);
    if (warning.action) {
      console.log(`      Acción: ${warning.action}`);
    }
  });
  console.log('');
}

if (predictions.recommendations.length > 0) {
  console.log('💡 Recomendaciones:');
  predictions.recommendations.forEach(rec => {
    console.log(`   • ${rec.message}`);
    if (rec.action) {
      console.log(`      Acción: ${rec.action}`);
    }
  });
  console.log('');
}

if (predictions.metrics_forecast.health_score_7days) {
  console.log('🔮 Predicción a 7 días:');
  console.log(`   Health Score estimado: ${predictions.metrics_forecast.health_score_7days.toFixed(1)}/100`);
  console.log('');
}

console.log(`📄 Reporte completo: ${OUTPUT_FILE}`);


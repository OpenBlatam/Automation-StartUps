# 🐍 Integración Completa con Script Python de Análisis

## 🎯 Integración Profunda con `analisis_engagement_contenido.py`

### Funcionalidad

**Integración completa bidireccional** con el script Python de análisis de engagement existente:
- Exportación automática de datos desde n8n
- Ejecución del script Python desde n8n
- Importación de resultados y insights
- Uso de análisis avanzado del script
- Generación de reportes HTML/PDF/Excel

## 📊 Flujo de Integración

### 1. Exportar Datos desde n8n

```javascript
// Export Engagement Data for Python Analysis
function exportForPythonAnalysis(engagementHistory) {
  const exportData = {
    publicaciones: engagementHistory.map(video => ({
      id: video.videoId,
      tipo_contenido: 'sora_video',
      titulo: video.title,
      plataforma: Object.keys(video.platformMetrics || {})[0] || 'unknown',
      fecha_publicacion: video.publishedAt,
      likes: video.platformMetrics?.instagram?.likes || 
             video.platformMetrics?.tiktok?.likes || 
             video.platformMetrics?.youtube?.likes || 0,
      comentarios: video.platformMetrics?.instagram?.comments || 
                  video.platformMetrics?.tiktok?.comments || 
                  video.platformMetrics?.youtube?.comments || 0,
      shares: video.platformMetrics?.instagram?.shares || 
             video.platformMetrics?.tiktok?.shares || 
             video.platformMetrics?.youtube?.shares || 0,
      impresiones: video.platformMetrics?.instagram?.impressions || 0,
      reach: video.platformMetrics?.instagram?.reach || 0,
      hashtags: typeof video.hashtags === 'string' ? 
        video.hashtags.split(/\\s+/) : 
        (Array.isArray(video.hashtags) ? video.hashtags : []),
      tiene_media: true,
      duracion_video: video.duration || 0,
      metadata: {
        engagement_rate: video.overallMetrics?.avgEngagementRate || 0,
        engagement_score: video.overallMetrics?.totalEngagementScore || 0,
        viral: video.overallMetrics?.viralOn?.length > 0,
        platforms: Object.keys(video.platformMetrics || {})
      }
    }))
  };
  
  return exportData;
}
```

### 2. Ejecutar Script Python

```javascript
// Execute Python Analysis Script
async function executePythonAnalysis(exportData, options = {}) {
  const fs = require('fs');
  const path = require('path');
  
  // Guardar datos en formato JSON
  const exportPath = '/tmp/engagement_export.json';
  fs.writeFileSync(exportPath, JSON.stringify(exportData, null, 2));
  
  // Preparar comando
  const scriptPath = '/Users/adan/IA/scripts/analisis_engagement_contenido.py';
  const outputPath = '/tmp/python_analysis_output.json';
  
  const command = `python3 "${scriptPath}" "${exportPath}" --format json --output "${outputPath}"`;
  
  // Ejecutar script
  const { exec } = require('child_process');
  
  return new Promise((resolve, reject) => {
    exec(command, { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error ejecutando script: ${error}`);
        reject(error);
        return;
      }
      
      // Leer resultados
      try {
        const results = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
        resolve(results);
      } catch (e) {
        // Si no hay JSON, intentar leer stdout
        try {
          const results = JSON.parse(stdout);
          resolve(results);
        } catch (e2) {
          reject(new Error('No se pudo parsear la salida del script'));
        }
      }
    });
  });
}
```

### 3. Importar Resultados y Aplicar Insights

```javascript
// Import Python Analysis Results
function importPythonResults(pythonResults, engagementHistory) {
  const insights = {
    // Resumen ejecutivo
    mejorHorario: pythonResults.resumen_ejecutivo?.mejor_horario,
    mejorDia: pythonResults.resumen_ejecutivo?.mejor_dia,
    mejorPlataforma: pythonResults.resumen_ejecutivo?.mejor_plataforma,
    engagementRatePromedio: pythonResults.resumen_ejecutivo?.engagement_rate_promedio,
    engagementScorePromedio: pythonResults.resumen_ejecutivo?.engagement_score_promedio,
    
    // Análisis por tipo de contenido
    mejorTipoContenido: pythonResults.analisis_por_tipo?.mejor_tipo,
    tiposContenido: pythonResults.analisis_por_tipo || {},
    
    // Análisis de hashtags
    hashtagsEfectivos: pythonResults.analisis_por_hashtag?.top_hashtags || [],
    hashtagsPerformance: pythonResults.analisis_por_hashtag?.hashtags_performance || {},
    
    // Análisis de horarios
    horariosOptimos: pythonResults.analisis_por_horario?.mejores_horarios || [],
    diasOptimos: pythonResults.analisis_por_dia?.mejores_dias || [],
    
    // Análisis de plataformas
    plataformasPerformance: pythonResults.analisis_por_plataforma || {},
    
    // Recomendaciones de IA
    recomendacionesIA: pythonResults.recomendaciones_ia || {},
    recomendacionesEstrategicas: pythonResults.recomendaciones_ia?.recomendaciones_estrategicas || [],
    ideasContenido: pythonResults.recomendaciones_ia?.ideas_contenido || [],
    mejorasPrioritarias: pythonResults.recomendaciones_ia?.mejoras_prioritarias || [],
    
    // Análisis avanzado (si está disponible)
    analisisML: pythonResults.analisis_ml || null,
    predicciones: pythonResults.predicciones || null,
    tendencias: pythonResults.tendencias || null,
    anomalias: pythonResults.anomalias || null,
    
    // ROI y monetización (si está disponible)
    roi: pythonResults.roi || null,
    monetizacion: pythonResults.monetizacion || null,
    
    // Calendario optimizado (si está disponible)
    calendarioOptimizado: pythonResults.calendario_contenido || null,
    
    // Benchmarking (si está disponible)
    benchmarking: pythonResults.benchmarking || null,
    
    // Alertas (si está disponible)
    alertas: pythonResults.alertas || [],
    
    // Análisis de competencia (si está disponible)
    competencia: pythonResults.analisis_competencia || null,
    
    // Palabras trending (si está disponible)
    palabrasTrending: pythonResults.palabras_trending || null
  };
  
  // Actualizar workflow con insights
  $workflow.staticData.pythonInsights = insights;
  
  // Aplicar insights a optimización
  applyPythonInsights(insights);
  
  return insights;
}

// Aplicar insights del Python al workflow
function applyPythonInsights(insights) {
  // Actualizar top hashtags
  if (insights.hashtagsEfectivos.length > 0) {
    const topHashtags = insights.hashtagsEfectivos.map(h => ({
      tag: typeof h === 'string' ? h : h.hashtag || h.tag,
      avgEngagementRate: typeof h === 'object' ? (h.engagement_rate || h.avgEngagementRate || 0) : 0,
      count: typeof h === 'object' ? (h.count || h.usage_count || 0) : 0
    }));
    $workflow.staticData.topHashtags = topHashtags;
  }
  
  // Actualizar mejores horarios
  if (insights.horariosOptimos.length > 0) {
    const bestHours = insights.horariosOptimos.map(h => ({
      hour: typeof h === 'number' ? h : (h.hora || h.hour),
      avgEngagementRate: typeof h === 'object' ? (h.engagement_rate || h.avgEngagementRate || 0) : 0,
      count: typeof h === 'object' ? (h.count || 0) : 0
    }));
    $workflow.staticData.bestHours = bestHours;
  }
  
  // Actualizar mejores días
  if (insights.diasOptimos.length > 0) {
    const bestDays = insights.diasOptimos.map(d => ({
      day: typeof d === 'string' ? d : (d.dia || d.day),
      avgEngagementRate: typeof d === 'object' ? (d.engagement_rate || d.avgEngagementRate || 0) : 0,
      count: typeof d === 'object' ? (d.count || 0) : 0
    }));
    $workflow.staticData.bestDays = bestDays;
  }
  
  // Guardar recomendaciones
  if (insights.recomendacionesEstrategicas.length > 0) {
    $workflow.staticData.strategicRecommendations = insights.recomendacionesEstrategicas;
  }
  
  if (insights.ideasContenido.length > 0) {
    $workflow.staticData.contentIdeas = insights.ideasContenido;
  }
  
  if (insights.mejorasPrioritarias.length > 0) {
    $workflow.staticData.priorityImprovements = insights.mejorasPrioritarias;
  }
}
```

## 🔄 Nodo Completo de Integración

```javascript
// Complete Python Integration Node
const engagementHistory = $workflow.staticData.engagementHistory || [];

if (engagementHistory.length < 5) {
  return {
    json: {
      ...$input.item.json,
      pythonIntegration: {
        available: false,
        reason: 'insufficient_data',
        minRequired: 5,
        current: engagementHistory.length
      }
    }
  };
}

// Exportar datos
const exportData = exportForPythonAnalysis(engagementHistory);

// Ejecutar análisis Python
try {
  const pythonResults = await executePythonAnalysis(exportData);
  
  // Importar resultados
  const insights = importPythonResults(pythonResults, engagementHistory);
  
  // Generar reporte HTML si está disponible
  let htmlReport = null;
  if (pythonResults.reporte_html) {
    htmlReport = pythonResults.reporte_html;
  } else {
    // Intentar generar reporte HTML
    try {
      const htmlCommand = `python3 "/Users/adan/IA/scripts/analisis_engagement_contenido.py" "/tmp/engagement_export.json" --format html --output "/tmp/reporte_engagement.html"`;
      exec(htmlCommand, () => {
        const fs = require('fs');
        if (fs.existsSync('/tmp/reporte_engagement.html')) {
          htmlReport = fs.readFileSync('/tmp/reporte_engagement.html', 'utf8');
        }
      });
    } catch (e) {
      // Ignorar error de HTML
    }
  }
  
  return {
    json: {
      ...$input.item.json,
      pythonIntegration: {
        available: true,
        executed: true,
        insights: insights,
        htmlReport: htmlReport,
        pythonResults: pythonResults,
        applied: true,
        timestamp: new Date().toISOString()
      }
    }
  };
  
} catch (error) {
  return {
    json: {
      ...$input.item.json,
      pythonIntegration: {
        available: true,
        executed: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }
    }
  };
}
```

## 📊 Funcionalidades del Script Python Disponibles

### Análisis Básico
- ✅ Análisis de engagement por tipo de contenido
- ✅ Análisis de hashtags más efectivos
- ✅ Análisis de horarios óptimos
- ✅ Análisis por día de la semana
- ✅ Análisis por plataforma

### Análisis Avanzado
- ✅ Análisis de tendencias temporales
- ✅ Detección de anomalías
- ✅ Comparación de períodos
- ✅ Análisis de patrones temporales
- ✅ Análisis predictivo con ML
- ✅ Análisis de sentimiento avanzado

### Recomendaciones
- ✅ Recomendaciones estratégicas
- ✅ Ideas de contenido
- ✅ Mejoras prioritarias
- ✅ Recomendaciones personalizadas
- ✅ Recomendaciones específicas de LinkedIn

### Reportes
- ✅ Exportación a HTML con visualizaciones
- ✅ Exportación a CSV
- ✅ Exportación a PDF
- ✅ Exportación a Excel con múltiples hojas
- ✅ Dashboard HTML interactivo

### Análisis Especializados
- ✅ Análisis de competencia por hashtags
- ✅ Análisis de crecimiento de audiencia
- ✅ Análisis de cohortes de contenido
- ✅ Cálculo de ROI de contenido
- ✅ Optimización de frecuencia de publicación
- ✅ Detección de contenido duplicado
- ✅ Análisis de palabras clave trending
- ✅ Optimización de calendario de contenido

## 🎯 Casos de Uso de Integración

### Caso 1: Análisis Semanal Automático

```javascript
// Schedule: Cada domingo a las 00:00
// 1. Exportar datos de la semana
// 2. Ejecutar análisis Python completo
// 3. Generar reporte HTML
// 4. Enviar reporte por email/Telegram
// 5. Aplicar insights al workflow
```

### Caso 2: Optimización Continua

```javascript
// Schedule: Cada vez que se acumulan 10 nuevos videos
// 1. Exportar datos actualizados
// 2. Ejecutar análisis Python
// 3. Actualizar top hashtags y mejores horarios
// 4. Aplicar automáticamente al workflow
```

### Caso 3: Reporte Mensual Completo

```javascript
// Schedule: Primer día de cada mes
// 1. Exportar todos los datos del mes anterior
// 2. Ejecutar análisis completo con todas las opciones
// 3. Generar reporte HTML completo
// 4. Generar reporte PDF para archivo
// 5. Enviar reporte completo
```

### Caso 4: Análisis de Competencia

```javascript
// Manual o programado
// 1. Exportar datos propios
// 2. Ejecutar análisis de competencia del script Python
// 3. Obtener insights de benchmarking
// 4. Aplicar mejoras identificadas
```

## 🔧 Configuración

### Variables de Entorno

```bash
# Integración Python
ENABLE_PYTHON_INTEGRATION=true
PYTHON_SCRIPT_PATH=/Users/adan/IA/scripts/analisis_engagement_contenido.py
PYTHON_OUTPUT_DIR=/tmp
PYTHON_MIN_VIDEOS=5

# Opciones de análisis
PYTHON_ANALYSIS_FORMAT=json  # json, html, csv, pdf, excel
PYTHON_GENERATE_REPORTS=true
PYTHON_APPLY_INSIGHTS=true

# Reportes automáticos
PYTHON_WEEKLY_REPORT=true
PYTHON_MONTHLY_REPORT=true
PYTHON_REPORT_EMAIL=tu@email.com
```

### Requisitos del Sistema

```bash
# Python 3.7+
python3 --version

# Dependencias del script
pip install pandas numpy matplotlib seaborn scikit-learn openai

# Permisos de ejecución
chmod +x /Users/adan/IA/scripts/analisis_engagement_contenido.py
```

## 📈 Beneficios de la Integración

### Ventajas

1. **Análisis Más Profundo**
   - Usa todas las capacidades del script Python
   - Análisis ML avanzado
   - Visualizaciones profesionales

2. **Reportes Profesionales**
   - HTML interactivo con gráficos
   - PDF para archivo
   - Excel con múltiples hojas

3. **Insights Avanzados**
   - Análisis predictivo
   - Detección de anomalías
   - Análisis de competencia
   - ROI y monetización

4. **Automatización Completa**
   - Exportación automática
   - Ejecución automática
   - Aplicación automática de insights

## 🚀 Flujo Completo Integrado

```
1. Workflow n8n procesa videos
   ↓
2. Tracking de engagement automático
   ↓
3. Acumulación de datos en historial
   ↓
4. [Trigger: Cada X videos o tiempo]
   ↓
5. Exportar datos para Python
   ↓
6. Ejecutar script Python de análisis
   ↓
7. Obtener resultados completos
   ↓
8. Importar insights al workflow
   ↓
9. Aplicar insights automáticamente
   ↓
10. Generar reportes HTML/PDF
   ↓
11. Enviar reportes automáticamente
   ↓
12. Workflow optimizado con nuevos insights
```

## 🎯 Ejemplos de Uso

### Ejemplo 1: Análisis Rápido

```javascript
// Ejecutar análisis básico
const exportData = exportForPythonAnalysis(engagementHistory);
const results = await executePythonAnalysis(exportData, {
  format: 'json',
  quick: true
});

// Aplicar insights inmediatamente
const insights = importPythonResults(results);
// Insights ya aplicados automáticamente
```

### Ejemplo 2: Reporte Completo

```javascript
// Ejecutar análisis completo con reporte
const exportData = exportForPythonAnalysis(engagementHistory);
const results = await executePythonAnalysis(exportData, {
  format: 'html',
  fullAnalysis: true,
  generateReport: true
});

// Obtener reporte HTML
const htmlReport = results.reporte_html || fs.readFileSync('/tmp/reporte_engagement.html');

// Enviar reporte
sendReport(htmlReport, 'weekly');
```

### Ejemplo 3: Análisis Predictivo

```javascript
// Usar análisis ML del script Python
const exportData = exportForPythonAnalysis(engagementHistory);
const results = await executePythonAnalysis(exportData, {
  format: 'json',
  mlAnalysis: true
});

// Obtener predicciones
const predictions = results.analisis_ml?.predicciones || [];
const tendencias = results.tendencias || [];

// Aplicar predicciones al workflow
applyPredictions(predictions, tendencias);
```

---

**Estado**: ✅ Integración completa diseñada  
**Complejidad**: Media  
**Tiempo de Setup**: 30 minutos  
**ROI**: Muy Alto (aprovecha análisis avanzado existente)



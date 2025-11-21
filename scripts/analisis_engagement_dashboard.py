#!/usr/bin/env python3
"""
Dashboard Web Interactivo de Engagement - Mejoras Premium
=========================================================
Dashboard web completo con visualizaciones avanzadas:
- Dashboard Flask con gráficos interactivos
- Visualizaciones en tiempo real
- Múltiples vistas y filtros
- Exportación de gráficos
- Comparaciones interactivas
- Análisis comparativo visual
- Filtros avanzados
- Métricas en tiempo real
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

try:
    from flask import Flask, render_template_string, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("Error: Flask no está instalado. Instálalo con: pip install flask flask-cors")
    sys.exit(1)

try:
    from analisis_engagement_contenido import AnalizadorEngagement, Publicacion
    from analisis_engagement_ai import AnalizadorEngagementAI
    from analisis_engagement_mejorado import AnalizadorEngagementMejorado
except ImportError:
    print("Error: Módulos de análisis no encontrados")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Instancias globales
analizador_base = None
analizador_ai = None
analizador_mejorado = None


def init_analizadores():
    """Inicializa los analizadores"""
    global analizador_base, analizador_ai, analizador_mejorado
    
    analizador_base = AnalizadorEngagement()
    analizador_base.generar_datos_ejemplo(num_publicaciones=50)
    analizador_ai = AnalizadorEngagementAI(analizador_base)
    analizador_mejorado = AnalizadorEngagementMejorado(analizador_base, analizador_ai)


# Template HTML del dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Engagement - Análisis Completo</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #333;
            margin-bottom: 10px;
        }
        .header .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        .filters {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .filters select, .filters input {
            padding: 8px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .card h2 {
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .metric {
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 20px;
        }
        .chart-container-large {
            height: 400px;
        }
        .insights {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .insights ul {
            list-style: none;
            padding-left: 0;
        }
        .insights li {
            padding: 10px;
            margin-bottom: 10px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }
        .alert {
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid;
        }
        .alert-critical {
            background: #fee;
            border-color: #f00;
        }
        .alert-high {
            background: #ffeaa7;
            border-color: #fdcb6e;
        }
        .alert-medium {
            background: #dfe6e9;
            border-color: #b2bec3;
        }
        .btn {
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background: #5568d3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>📊 Dashboard de Engagement</h1>
                <div class="timestamp" id="timestamp">Cargando...</div>
            </div>
            <div>
                <button class="btn" onclick="actualizarDashboard()">🔄 Actualizar</button>
                <button class="btn" onclick="exportarDatos()">📥 Exportar</button>
            </div>
        </div>
        
        <div class="filters">
            <label>Plataforma:</label>
            <select id="filter-platform" onchange="aplicarFiltros()">
                <option value="all">Todas</option>
            </select>
            <label>Tipo:</label>
            <select id="filter-type" onchange="aplicarFiltros()">
                <option value="all">Todos</option>
                <option value="X">Tutoriales/Educativos</option>
                <option value="Y">Entretenimiento/Viral</option>
                <option value="Z">Promocional/Producto</option>
            </select>
            <label>Período:</label>
            <select id="filter-period" onchange="aplicarFiltros()">
                <option value="7">Últimos 7 días</option>
                <option value="30" selected>Últimos 30 días</option>
                <option value="90">Últimos 90 días</option>
            </select>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Engagement Rate</h2>
                <div class="metric" id="metric-engagement-rate">-</div>
                <div class="metric-label">Promedio</div>
            </div>
            <div class="card">
                <h2>Engagement Score</h2>
                <div class="metric" id="metric-engagement-score">-</div>
                <div class="metric-label">Puntos</div>
            </div>
            <div class="card">
                <h2>Total Publicaciones</h2>
                <div class="metric" id="metric-total-posts">-</div>
                <div class="metric-label">Análisis</div>
            </div>
            <div class="card">
                <h2>Contenido Viral</h2>
                <div class="metric" id="metric-viral">-</div>
                <div class="metric-label">Porcentaje</div>
            </div>
        </div>
        
        <div class="card">
            <h2>Engagement por Plataforma</h2>
            <div class="chart-container">
                <canvas id="platformChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>Tendencia Temporal</h2>
            <div class="chart-container chart-container-large">
                <canvas id="trendChart"></canvas>
            </div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>Engagement por Tipo de Contenido</h2>
                <div class="chart-container">
                    <canvas id="typeChart"></canvas>
                </div>
            </div>
            <div class="card">
                <h2>Distribución de Hashtags</h2>
                <div class="chart-container">
                    <canvas id="hashtagChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="insights" id="insights-section">
            <h2>💡 Insights Clave</h2>
            <ul id="insights-list">
                <li>Cargando insights...</li>
            </ul>
        </div>
        
        <div id="alerts-section"></div>
    </div>
    
    <script>
        let charts = {};
        let datosActuales = {};
        
        async function cargarDashboard() {
            try {
                const response = await fetch('/api/dashboard-data');
                datosActuales = await response.json();
                actualizarVista();
            } catch (error) {
                console.error('Error cargando dashboard:', error);
            }
        }
        
        function actualizarVista() {
            // Actualizar métricas
            document.getElementById('metric-engagement-rate').textContent = 
                datosActuales.metricas?.engagement_rate?.toFixed(2) + '%' || '-';
            document.getElementById('metric-engagement-score').textContent = 
                datosActuales.metricas?.engagement_score?.toFixed(1) || '-';
            document.getElementById('metric-total-posts').textContent = 
                datosActuales.metricas?.total_publicaciones || '-';
            document.getElementById('metric-viral').textContent = 
                datosActuales.metricas?.contenido_viral?.toFixed(1) + '%' || '-';
            
            // Actualizar timestamp
            document.getElementById('timestamp').textContent = 
                'Actualizado: ' + new Date().toLocaleString('es-ES');
            
            // Actualizar gráficos
            actualizarGraficos();
            
            // Actualizar insights
            actualizarInsights();
            
            // Actualizar alertas
            actualizarAlertas();
        }
        
        function actualizarGraficos() {
            // Gráfico de plataformas
            if (datosActuales.graficos?.plataformas) {
                const ctx = document.getElementById('platformChart').getContext('2d');
                if (charts.platformChart) charts.platformChart.destroy();
                charts.platformChart = new Chart(ctx, {
                    type: 'bar',
                    data: datosActuales.graficos.plataformas,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            datalabels: { anchor: 'end', align: 'top' }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            }
            
            // Gráfico de tendencia
            if (datosActuales.graficos?.tendencia) {
                const ctx = document.getElementById('trendChart').getContext('2d');
                if (charts.trendChart) charts.trendChart.destroy();
                charts.trendChart = new Chart(ctx, {
                    type: 'line',
                    data: datosActuales.graficos.tendencia,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: true }
                        },
                        scales: {
                            y: { beginAtZero: true }
                        }
                    }
                });
            }
            
            // Gráfico de tipos
            if (datosActuales.graficos?.tipos) {
                const ctx = document.getElementById('typeChart').getContext('2d');
                if (charts.typeChart) charts.typeChart.destroy();
                charts.typeChart = new Chart(ctx, {
                    type: 'doughnut',
                    data: datosActuales.graficos.tipos,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
            
            // Gráfico de hashtags
            if (datosActuales.graficos?.hashtags) {
                const ctx = document.getElementById('hashtagChart').getContext('2d');
                if (charts.hashtagChart) charts.hashtagChart.destroy();
                charts.hashtagChart = new Chart(ctx, {
                    type: 'pie',
                    data: datosActuales.graficos.hashtags,
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            }
        }
        
        function actualizarInsights() {
            const insightsList = document.getElementById('insights-list');
            if (datosActuales.insights) {
                insightsList.innerHTML = datosActuales.insights.map(insight => 
                    `<li>${insight}</li>`
                ).join('');
            }
        }
        
        function actualizarAlertas() {
            const alertsSection = document.getElementById('alerts-section');
            if (datosActuales.alertas && datosActuales.alertas.length > 0) {
                alertsSection.innerHTML = '<h2>⚠️ Alertas</h2>' + 
                    datosActuales.alertas.map(alerta => `
                        <div class="alert alert-${alerta.nivel.toLowerCase()}">
                            <strong>${alerta.nivel}:</strong> ${alerta.mensaje}
                        </div>
                    `).join('');
            } else {
                alertsSection.innerHTML = '';
            }
        }
        
        function aplicarFiltros() {
            const platform = document.getElementById('filter-platform').value;
            const type = document.getElementById('filter-type').value;
            const period = document.getElementById('filter-period').value;
            
            fetch(`/api/dashboard-data?platform=${platform}&type=${type}&period=${period}`)
                .then(r => r.json())
                .then(data => {
                    datosActuales = data;
                    actualizarVista();
                });
        }
        
        function actualizarDashboard() {
            cargarDashboard();
        }
        
        function exportarDatos() {
            const dataStr = JSON.stringify(datosActuales, null, 2);
            const dataBlob = new Blob([dataStr], {type: 'application/json'});
            const url = URL.createObjectURL(dataBlob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'dashboard_data_' + new Date().toISOString() + '.json';
            link.click();
        }
        
        // Cargar dashboard al inicio
        cargarDashboard();
        
        // Actualizar cada 5 minutos
        setInterval(cargarDashboard, 300000);
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Ruta principal del dashboard"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/dashboard-data')
def dashboard_data():
    """API endpoint para datos del dashboard"""
    try:
        platform_filter = request.args.get('platform', 'all')
        type_filter = request.args.get('type', 'all')
        period_days = int(request.args.get('period', 30))
        
        # Filtrar publicaciones
        fecha_limite = datetime.now() - timedelta(days=period_days)
        publicaciones_filtradas = [
            p for p in analizador_base.publicaciones
            if p.fecha_publicacion >= fecha_limite and
            (platform_filter == 'all' or p.plataforma == platform_filter) and
            (type_filter == 'all' or p.tipo_contenido == type_filter)
        ]
        
        # Generar reporte con datos filtrados
        publicaciones_originales = analizador_base.publicaciones
        analizador_base.publicaciones = publicaciones_filtradas
        reporte = analizador_base.generar_reporte()
        analizador_base.publicaciones = publicaciones_originales
        
        resumen = reporte.get('resumen_ejecutivo', {})
        
        # Preparar datos para gráficos
        datos_graficos = preparar_datos_graficos(reporte, publicaciones_filtradas)
        
        # Preparar insights
        insights = preparar_insights(reporte, resumen)
        
        # Preparar alertas
        alertas = preparar_alertas(reporte, resumen)
        
        return jsonify({
            "metricas": {
                "engagement_rate": resumen.get('engagement_rate_promedio', 0),
                "engagement_score": resumen.get('engagement_score_promedio', 0),
                "total_publicaciones": len(publicaciones_filtradas),
                "contenido_viral": resumen.get('contenido_viral_porcentaje', 0)
            },
            "graficos": datos_graficos,
            "insights": insights,
            "alertas": alertas,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error generando datos del dashboard: {e}")
        return jsonify({"error": str(e)}), 500


def preparar_datos_graficos(reporte: Dict[str, Any], publicaciones: List[Publicacion]) -> Dict[str, Any]:
    """Prepara datos para los gráficos"""
    # Gráfico de plataformas
    analisis_plataformas = reporte.get('analisis_por_plataforma', {})
    plataformas_data = {
        "labels": list(analisis_plataformas.keys()),
        "datasets": [{
            "label": "Engagement Rate (%)",
            "data": [d.get('engagement_rate_promedio', 0) for d in analisis_plataformas.values()],
            "backgroundColor": "rgba(102, 126, 234, 0.6)",
            "borderColor": "rgba(102, 126, 234, 1)",
            "borderWidth": 2
        }]
    }
    
    # Gráfico de tendencia temporal
    engagement_scores = [p.engagement_score for p in publicaciones]
    fechas = [p.fecha_publicacion.strftime('%Y-%m-%d') for p in publicaciones]
    
    # Agrupar por fecha
    scores_por_fecha = defaultdict(list)
    for fecha, score in zip(fechas, engagement_scores):
        scores_por_fecha[fecha].append(score)
    
    fechas_ordenadas = sorted(scores_por_fecha.keys())
    promedios = [statistics.mean(scores_por_fecha[f]) for f in fechas_ordenadas]
    
    tendencia_data = {
        "labels": fechas_ordenadas[-30:],  # Últimas 30 fechas
        "datasets": [{
            "label": "Engagement Score",
            "data": promedios[-30:],
            "borderColor": "rgba(102, 126, 234, 1)",
            "backgroundColor": "rgba(102, 126, 234, 0.1)",
            "tension": 0.4
        }]
    }
    
    # Gráfico de tipos de contenido
    tipos_count = defaultdict(int)
    tipos_score = defaultdict(list)
    for pub in publicaciones:
        tipos_count[pub.tipo_contenido] += 1
        tipos_score[pub.tipo_contenido].append(pub.engagement_score)
    
    tipos_data = {
        "labels": list(tipos_count.keys()),
        "datasets": [{
            "data": [statistics.mean(tipos_score[t]) if tipos_score[t] else 0 for t in tipos_count.keys()],
            "backgroundColor": [
                "rgba(102, 126, 234, 0.6)",
                "rgba(118, 75, 162, 0.6)",
                "rgba(255, 99, 132, 0.6)"
            ]
        }]
    }
    
    # Gráfico de hashtags top
    hashtags_efectivos = reporte.get('hashtags_efectivos', [])[:10]
    hashtags_data = {
        "labels": [h.get('hashtag', '') for h in hashtags_efectivos],
        "datasets": [{
            "data": [h.get('engagement_score_promedio', 0) for h in hashtags_efectivos],
            "backgroundColor": [
                f"rgba({100 + i * 20}, {126 + i * 10}, {234 - i * 20}, 0.6)"
                for i in range(len(hashtags_efectivos))
            ]
        }]
    }
    
    return {
        "plataformas": plataformas_data,
        "tendencia": tendencia_data,
        "tipos": tipos_data,
        "hashtags": hashtags_data
    }


def preparar_insights(reporte: Dict[str, Any], resumen: Dict[str, Any]) -> List[str]:
    """Prepara insights para el dashboard"""
    insights = []
    
    mejor_tipo = resumen.get('nombre_tipo', 'N/A')
    insights.append(f"Tipo de contenido más exitoso: {mejor_tipo}")
    
    mejor_plataforma = resumen.get('mejor_plataforma')
    if mejor_plataforma:
        insights.append(f"Plataforma con mejor rendimiento: {mejor_plataforma}")
    
    mejor_horario = resumen.get('mejor_horario')
    if mejor_horario:
        insights.append(f"Mejor horario para publicar: {mejor_horario}")
    
    tendencia = resumen.get('tendencia')
    if tendencia:
        insights.append(f"Tendencia actual: {tendencia.capitalize()}")
    
    viral_pct = resumen.get('contenido_viral_porcentaje', 0)
    if viral_pct > 5:
        insights.append(f"Excelente contenido viral: {viral_pct:.1f}%")
    elif viral_pct < 2:
        insights.append(f"Oportunidad de mejora: Solo {viral_pct:.1f}% de contenido viral")
    
    return insights


def preparar_alertas(reporte: Dict[str, Any], resumen: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Prepara alertas para el dashboard"""
    alertas = []
    
    engagement_rate = resumen.get('engagement_rate_promedio', 0)
    if engagement_rate < 1.0:
        alertas.append({
            "nivel": "CRITICAL",
            "mensaje": f"Engagement rate crítico: {engagement_rate:.2f}%"
        })
    elif engagement_rate < 2.0:
        alertas.append({
            "nivel": "HIGH",
            "mensaje": f"Engagement rate bajo: {engagement_rate:.2f}%"
        })
    
    viral_pct = resumen.get('contenido_viral_porcentaje', 0)
    if viral_pct < 2.0:
        alertas.append({
            "nivel": "MEDIUM",
            "mensaje": f"Bajo contenido viral: {viral_pct:.1f}%"
        })
    
    return alertas


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Dashboard Web de Engagement')
    parser.add_argument('--host', default='0.0.0.0', help='Host (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5002, help='Puerto (default: 5002)')
    parser.add_argument('--publicaciones', type=int, default=50, help='Número de publicaciones')
    parser.add_argument('--debug', action='store_true', help='Modo debug')
    
    args = parser.parse_args()
    
    # Inicializar analizadores
    init_analizadores()
    analizador_base.generar_datos_ejemplo(num_publicaciones=args.publicaciones)
    
    logger.info(f"Dashboard iniciado en http://{args.host}:{args.port}")
    logger.info(f"Cargadas {len(analizador_base.publicaciones)} publicaciones")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()




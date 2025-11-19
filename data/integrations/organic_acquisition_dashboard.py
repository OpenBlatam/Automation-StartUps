"""
Dashboard Web Interactivo para Adquisición Orgánica

Dashboard en tiempo real con visualizaciones avanzadas,
métricas clave, análisis de cohortes y alertas inteligentes.
"""

from flask import Flask, render_template_string, jsonify, request
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuración de base de datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "tu_base_de_datos"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}


def get_db_connection():
    """Obtiene conexión a la base de datos."""
    try:
        import psycopg2
        return psycopg2.connect(**DB_CONFIG)
    except ImportError:
        logger.error("psycopg2 no está instalado")
        return None
    except Exception as e:
        logger.error(f"Error conectando a base de datos: {e}")
        return None


DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Adquisición Orgánica</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1600px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
        }
        .header .last-update {
            color: #666;
            font-size: 0.9em;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .kpi-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
            position: relative;
            overflow: hidden;
        }
        .kpi-card:hover {
            transform: translateY(-5px);
        }
        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        .kpi-value {
            font-size: 3em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }
        .kpi-label {
            color: #666;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .kpi-change {
            font-size: 0.9em;
            margin-top: 10px;
        }
        .kpi-change.positive { color: #4caf50; }
        .kpi-change.negative { color: #f44336; }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        .chart-title {
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
        .alerts-section {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .alert-item {
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
            border-left: 4px solid;
        }
        .alert-item.info { background: #e3f2fd; border-color: #2196f3; }
        .alert-item.warning { background: #fff3e0; border-color: #ff9800; }
        .alert-item.error { background: #ffebee; border-color: #f44336; }
        .alert-item.success { background: #e8f5e9; border-color: #4caf50; }
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            margin: 20px auto;
            display: block;
            transition: background 0.3s;
        }
        .refresh-btn:hover {
            background: #5568d3;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: #f5f5f5;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>🚀 Dashboard - Adquisición Orgánica</h1>
                <p class="last-update">Última actualización: <span id="lastUpdate"></span></p>
            </div>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Leads</div>
                <div class="kpi-value" id="total-leads">0</div>
                <div class="kpi-change" id="leads-change"></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Leads Enganchados</div>
                <div class="kpi-value" id="engaged-leads">0</div>
                <div class="kpi-change" id="engaged-change"></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Tasa de Conversión</div>
                <div class="kpi-value" id="conversion-rate">0%</div>
                <div class="kpi-change" id="conversion-change"></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Referidos Validados</div>
                <div class="kpi-value" id="validated-referrals">0</div>
                <div class="kpi-change" id="referrals-change"></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Recompensas Pagadas</div>
                <div class="kpi-value" id="rewards-paid">$0</div>
                <div class="kpi-change" id="rewards-change"></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Score Promedio</div>
                <div class="kpi-value" id="avg-score">0</div>
                <div class="kpi-change" id="score-change"></div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('overview')">📊 Overview</button>
            <button class="tab" onclick="switchTab('cohorts')">👥 Cohortes</button>
            <button class="tab" onclick="switchTab('content')">📝 Contenido</button>
            <button class="tab" onclick="switchTab('referrals')">🎁 Referidos</button>
        </div>

        <div id="overview" class="tab-content active">
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">Tendencia de Leads</div>
                    <canvas id="leadsTrendChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Distribución por Fuente</div>
                    <canvas id="sourceChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Engagement por Tipo de Contenido</div>
                    <canvas id="contentChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Funnel de Conversión</div>
                    <canvas id="funnelChart"></canvas>
                </div>
            </div>
        </div>

        <div id="cohorts" class="tab-content">
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">Análisis de Cohortes</div>
                    <canvas id="cohortChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Retención por Mes</div>
                    <canvas id="retentionChart"></canvas>
                </div>
            </div>
        </div>

        <div id="content" class="tab-content">
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">Performance de Contenido</div>
                    <canvas id="contentPerformanceChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">A/B Testing Results</div>
                    <canvas id="abTestChart"></canvas>
                </div>
            </div>
        </div>

        <div id="referrals" class="tab-content">
            <div class="charts-grid">
                <div class="chart-card">
                    <div class="chart-title">Referidos por Referidor</div>
                    <canvas id="referrerChart"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">Tasa de Validación</div>
                    <canvas id="validationChart"></canvas>
                </div>
            </div>
        </div>

        <div class="alerts-section">
            <h2 style="color: #667eea; margin-bottom: 20px;">🔔 Alertas Inteligentes</h2>
            <div id="alerts-container"></div>
        </div>

        <button class="refresh-btn" onclick="loadDashboard()">🔄 Actualizar Dashboard</button>
    </div>

    <script>
        let charts = {};

        function switchTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }

        function initCharts() {
            // Tendencia de leads
            const leadsCtx = document.getElementById('leadsTrendChart').getContext('2d');
            charts.leadsTrend = new Chart(leadsCtx, {
                type: 'line',
                data: { labels: [], datasets: [] },
                options: { responsive: true, maintainAspectRatio: true }
            });

            // Distribución por fuente
            const sourceCtx = document.getElementById('sourceChart').getContext('2d');
            charts.source = new Chart(sourceCtx, {
                type: 'doughnut',
                data: { labels: [], datasets: [] },
                options: { responsive: true, maintainAspectRatio: true }
            });

            // Engagement por contenido
            const contentCtx = document.getElementById('contentChart').getContext('2d');
            charts.content = new Chart(contentCtx, {
                type: 'bar',
                data: { labels: [], datasets: [] },
                options: { responsive: true, maintainAspectRatio: true }
            });

            // Funnel
            const funnelCtx = document.getElementById('funnelChart').getContext('2d');
            charts.funnel = new Chart(funnelCtx, {
                type: 'bar',
                data: { labels: [], datasets: [] },
                options: { responsive: true, maintainAspectRatio: true, indexAxis: 'y' }
            });
        }

        async function loadDashboard() {
            try {
                const response = await fetch('/api/dashboard');
                const data = await response.json();

                // Actualizar KPIs
                updateKPIs(data.kpis);
                
                // Actualizar gráficos
                updateCharts(data.charts);
                
                // Actualizar alertas
                updateAlerts(data.alerts);
                
                // Actualizar timestamp
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString('es-ES');
            } catch (error) {
                console.error('Error cargando dashboard:', error);
            }
        }

        function updateKPIs(kpis) {
            document.getElementById('total-leads').textContent = kpis.total_leads || 0;
            document.getElementById('engaged-leads').textContent = kpis.engaged_leads || 0;
            document.getElementById('conversion-rate').textContent = (kpis.conversion_rate || 0).toFixed(1) + '%';
            document.getElementById('validated-referrals').textContent = kpis.validated_referrals || 0;
            document.getElementById('rewards-paid').textContent = '$' + (kpis.rewards_paid || 0).toFixed(2);
            document.getElementById('avg-score').textContent = (kpis.avg_score || 0).toFixed(1);
        }

        function updateCharts(chartsData) {
            // Actualizar cada gráfico con los datos
            if (chartsData.leads_trend && charts.leadsTrend) {
                charts.leadsTrend.data = chartsData.leads_trend;
                charts.leadsTrend.update();
            }
            // ... más actualizaciones de gráficos
        }

        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            container.innerHTML = '';
            alerts.forEach(alert => {
                const div = document.createElement('div');
                div.className = `alert-item ${alert.type}`;
                div.innerHTML = `<strong>${alert.title}</strong><br>${alert.message}`;
                container.appendChild(div);
            });
        }

        // Inicializar
        initCharts();
        loadDashboard();
        setInterval(loadDashboard, 60000); // Actualizar cada minuto
    </script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Renderiza el dashboard principal."""
    return render_template_string(DASHBOARD_HTML)


@app.route("/api/dashboard")
def dashboard_data():
    """API que retorna datos del dashboard."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        cursor = conn.cursor()
        
        # KPIs principales
        kpis = get_main_kpis(cursor)
        
        # Datos para gráficos
        charts = get_charts_data(cursor)
        
        # Alertas inteligentes
        alerts = get_intelligent_alerts(cursor)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "kpis": kpis,
            "charts": charts,
            "alerts": alerts,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error obteniendo datos del dashboard: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()


def get_main_kpis(cursor) -> Dict[str, Any]:
    """Obtiene KPIs principales."""
    # Total leads (últimos 30 días)
    cursor.execute("""
        SELECT COUNT(*) FROM organic_leads
        WHERE created_at >= NOW() - INTERVAL '30 days'
    """)
    total_leads = cursor.fetchone()[0]
    
    # Leads enganchados
    cursor.execute("""
        SELECT COUNT(*) FROM organic_leads
        WHERE status = 'engaged' AND created_at >= NOW() - INTERVAL '30 days'
    """)
    engaged_leads = cursor.fetchone()[0]
    
    # Tasa de conversión
    conversion_rate = (engaged_leads / total_leads * 100) if total_leads > 0 else 0
    
    # Referidos validados
    cursor.execute("""
        SELECT COUNT(*) FROM referrals
        WHERE status = 'validated' AND created_at >= NOW() - INTERVAL '30 days'
    """)
    validated_referrals = cursor.fetchone()[0]
    
    # Recompensas pagadas
    cursor.execute("""
        SELECT COALESCE(SUM(reward_amount), 0) FROM referral_rewards
        WHERE status = 'paid' AND created_at >= NOW() - INTERVAL '30 days'
    """)
    rewards_paid = float(cursor.fetchone()[0] or 0)
    
    # Score promedio
    cursor.execute("""
        SELECT COALESCE(AVG(engagement_score), 0) FROM organic_leads
        WHERE created_at >= NOW() - INTERVAL '30 days'
    """)
    avg_score = float(cursor.fetchone()[0] or 0)
    
    return {
        "total_leads": total_leads,
        "engaged_leads": engaged_leads,
        "conversion_rate": conversion_rate,
        "validated_referrals": validated_referrals,
        "rewards_paid": rewards_paid,
        "avg_score": avg_score
    }


def get_charts_data(cursor) -> Dict[str, Any]:
    """Obtiene datos para gráficos."""
    # Tendencia de leads (últimos 7 días)
    cursor.execute("""
        SELECT DATE(created_at) as date, COUNT(*) as count
        FROM organic_leads
        WHERE created_at >= NOW() - INTERVAL '7 days'
        GROUP BY DATE(created_at)
        ORDER BY date
    """)
    leads_trend = cursor.fetchall()
    
    # Distribución por fuente
    cursor.execute("""
        SELECT source, COUNT(*) as count
        FROM organic_leads
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY source
    """)
    source_dist = cursor.fetchall()
    
    return {
        "leads_trend": {
            "labels": [row[0].strftime("%Y-%m-%d") for row in leads_trend],
            "datasets": [{
                "label": "Leads",
                "data": [row[1] for row in leads_trend],
                "borderColor": "#667eea",
                "tension": 0.4
            }]
        },
        "source_distribution": {
            "labels": [row[0] for row in source_dist],
            "datasets": [{
                "data": [row[1] for row in source_dist],
                "backgroundColor": ["#667eea", "#764ba2", "#f093fb", "#4facfe"]
            }]
        }
    }


def get_intelligent_alerts(cursor) -> List[Dict[str, Any]]:
    """Genera alertas inteligentes basadas en métricas."""
    alerts = []
    
    # Verificar tasa de conversión baja
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged
        FROM organic_leads
        WHERE created_at >= NOW() - INTERVAL '7 days'
    """)
    result = cursor.fetchone()
    if result and result[0] > 0:
        conversion = (result[1] / result[0]) * 100
        if conversion < 10:
            alerts.append({
                "type": "warning",
                "title": "Tasa de Conversión Baja",
                "message": f"La tasa de conversión es {conversion:.1f}%, considera revisar el contenido de nurturing."
            })
    
    # Verificar fraude alto
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'fraud' THEN 1 END) as fraud
        FROM referrals
        WHERE created_at >= NOW() - INTERVAL '7 days'
    """)
    result = cursor.fetchone()
    if result and result[0] > 0:
        fraud_rate = (result[1] / result[0]) * 100
        if fraud_rate > 20:
            alerts.append({
                "type": "error",
                "title": "Alta Tasa de Fraude",
                "message": f"Tasa de fraude del {fraud_rate:.1f}%, revisa las validaciones."
            })
    
    return alerts


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Iniciando dashboard en puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=debug)


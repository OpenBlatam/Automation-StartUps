"""
Dashboard de Métricas en Tiempo Real para Chatbot
Versión: 2.0.0
"""

from flask import Flask, render_template_string, jsonify
from datetime import datetime, timedelta
from typing import Dict, List
import json
from pathlib import Path

app = Flask(__name__)

# Template HTML para el dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Chatbot - Métricas en Tiempo Real</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
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
        }
        .kpi-card:hover {
            transform: translateY(-5px);
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
        .kpi-target {
            font-size: 0.9em;
            color: #999;
            margin-top: 10px;
        }
        .target-met {
            color: #4caf50;
        }
        .target-not-met {
            color: #f44336;
        }
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .chart-card {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .chart-title {
            font-size: 1.5em;
            color: #667eea;
            margin-bottom: 20px;
            text-align: center;
        }
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
        .auto-refresh {
            text-align: center;
            color: white;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Dashboard Chatbot - Métricas en Tiempo Real</h1>
            <p>Última actualización: <span id="lastUpdate"></span></p>
        </div>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Tasa de Resolución</div>
                <div class="kpi-value" id="resolution-rate">0%</div>
                <div class="kpi-target" id="resolution-target">Objetivo: 80%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Satisfacción</div>
                <div class="kpi-value" id="satisfaction">0.0</div>
                <div class="kpi-target" id="satisfaction-target">Objetivo: 4.5/5</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Tiempo Respuesta</div>
                <div class="kpi-value" id="response-time">0s</div>
                <div class="kpi-target" id="response-target">Objetivo: <60s</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Interacciones Totales</div>
                <div class="kpi-value" id="total-interactions">0</div>
                <div class="kpi-target">Total de conversaciones</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Escalamientos</div>
                <div class="kpi-value" id="escalations">0</div>
                <div class="kpi-target" id="escalation-rate">0%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Conversaciones Activas</div>
                <div class="kpi-value" id="active-conversations">0</div>
                <div class="kpi-target">Sesiones en curso</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <div class="chart-title">Distribución de Sentimientos</div>
                <canvas id="sentimentChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">Distribución de Intenciones</div>
                <canvas id="intentChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">Tendencia de Resolución</div>
                <canvas id="resolutionTrendChart"></canvas>
            </div>
            <div class="chart-card">
                <div class="chart-title">Resultados A/B Testing</div>
                <canvas id="abTestChart"></canvas>
            </div>
        </div>

        <button class="refresh-btn" onclick="loadMetrics()">🔄 Actualizar Métricas</button>
        <div class="auto-refresh">Auto-actualización cada 30 segundos</div>
    </div>
    
    <script>
        let sentimentChart, intentChart, resolutionTrendChart, abTestChart;

        function initCharts() {
            // Gráfico de sentimientos
            const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
            sentimentChart = new Chart(sentimentCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Positivo', 'Neutral', 'Negativo', 'Frustrado'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#4caf50', '#2196f3', '#ff9800', '#f44336']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true
                }
            });

            // Gráfico de intenciones
            const intentCtx = document.getElementById('intentChart').getContext('2d');
            intentChart = new Chart(intentCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Frecuencia',
                        data: [],
                        backgroundColor: '#667eea'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });

            // Gráfico de tendencia
            const trendCtx = document.getElementById('resolutionTrendChart').getContext('2d');
            resolutionTrendChart = new Chart(trendCtx, {
            type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Tasa de Resolución (%)',
                        data: [],
                        borderColor: '#667eea',
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(102, 126, 234, 0.1)'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true, max: 100 }
                    }
                }
            });

            // Gráfico A/B Testing
            const abCtx = document.getElementById('abTestChart').getContext('2d');
            abTestChart = new Chart(abCtx, {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Variante A',
                        data: [],
                        backgroundColor: '#667eea'
                    }, {
                        label: 'Variante B',
                        data: [],
                        backgroundColor: '#764ba2'
                    }]
                },
                options: {
                responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        }

        async function loadMetrics() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();

                // Actualizar KPIs
                document.getElementById('resolution-rate').textContent = data.resolution_rate + '%';
                document.getElementById('satisfaction').textContent = data.avg_satisfaction.toFixed(2);
                document.getElementById('response-time').textContent = data.avg_response_time.toFixed(1) + 's';
                document.getElementById('total-interactions').textContent = data.total_interactions;
                document.getElementById('escalations').textContent = data.escalated;
                document.getElementById('escalation-rate').textContent = data.escalation_rate + '%';
                document.getElementById('active-conversations').textContent = data.active_conversations;

                // Actualizar targets
                const resolutionTarget = data.targets.resolution_rate;
                const resolutionEl = document.getElementById('resolution-target');
                resolutionEl.textContent = `Objetivo: ${resolutionTarget.target}%`;
                resolutionEl.className = resolutionTarget.met ? 'kpi-target target-met' : 'kpi-target target-not-met';

                const satisfactionTarget = data.targets.satisfaction;
                const satisfactionEl = document.getElementById('satisfaction-target');
                satisfactionEl.textContent = `Objetivo: ${satisfactionTarget.target}/5`;
                satisfactionEl.className = satisfactionTarget.met ? 'kpi-target target-met' : 'kpi-target target-not-met';

                const responseTarget = data.targets.response_time;
                const responseEl = document.getElementById('response-target');
                responseEl.textContent = `Objetivo: <${responseTarget.target}s`;
                responseEl.className = responseTarget.met ? 'kpi-target target-met' : 'kpi-target target-not-met';

                // Actualizar gráficos
                const sentimentData = data.sentiment_percentages;
                sentimentChart.data.datasets[0].data = [
                    sentimentData.positive || 0,
                    sentimentData.neutral || 0,
                    sentimentData.negative || 0,
                    sentimentData.frustrated || 0
                ];
                sentimentChart.update();

                // Gráfico de intenciones
                const intentData = data.intent_distribution || {};
                intentChart.data.labels = Object.keys(intentData);
                intentChart.data.datasets[0].data = Object.values(intentData);
                intentChart.update();

                // Actualizar última actualización
                document.getElementById('lastUpdate').textContent = new Date().toLocaleString('es-ES');
            } catch (error) {
                console.error('Error cargando métricas:', error);
            }
        }

        // Inicializar
        initCharts();
        loadMetrics();
        setInterval(loadMetrics, 30000); // Actualizar cada 30 segundos
    </script>
</body>
</html>
"""


class MetricsDashboard:
    """Clase para gestionar el dashboard de métricas"""
    
    def __init__(self, chatbot_engine):
        self.chatbot = chatbot_engine
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _setup_routes(self):
        """Configura las rutas del dashboard"""
        
        @self.app.route('/')
        def dashboard():
            return render_template_string(DASHBOARD_TEMPLATE)
        
        @self.app.route('/api/metrics')
        def api_metrics():
            metrics = self.chatbot.get_metrics()
            return jsonify(metrics)
        
        @self.app.route('/api/conversations')
        def api_conversations():
            conversations = []
            for session_id, conv in self.chatbot.conversations.items():
                conversations.append({
                    "session_id": session_id,
                    "user_id": conv.user_id,
                    "message_count": len(conv.messages),
                    "language": conv.language.value,
                    "created_at": conv.created_at.isoformat(),
                    "last_activity": conv.last_activity.isoformat()
                })
            return jsonify(conversations)
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Inicia el servidor del dashboard"""
        print(f"🚀 Dashboard iniciado en http://{host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    from chatbot_engine import ChatbotEngine
    
    chatbot = ChatbotEngine()
    dashboard = MetricsDashboard(chatbot)
    dashboard.run(debug=True)

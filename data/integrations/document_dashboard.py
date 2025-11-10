"""
Dashboard Web en Tiempo Real
============================

Genera dashboard HTML interactivo con métricas en tiempo real.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Generador de dashboards web"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_dashboard(
        self,
        analytics_data: Dict[str, Any],
        monitoring_data: Dict[str, Any],
        output_path: str,
        title: str = "Document Processing Dashboard"
    ) -> str:
        """Genera dashboard HTML completo"""
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header .subtitle {{
            color: #666;
            font-size: 14px;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stat-change {{
            font-size: 12px;
            margin-top: 5px;
        }}
        
        .stat-change.positive {{
            color: #10b981;
        }}
        
        .stat-change.negative {{
            color: #ef4444;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .chart-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chart-card h3 {{
            margin-bottom: 20px;
            color: #333;
        }}
        
        .table-container {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .badge-success {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .badge-warning {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .badge-error {{
            background: #fee2e2;
            color: #991b1b;
        }}
        
        .refresh-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            margin-top: 20px;
        }}
        
        .refresh-btn:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <div class="subtitle">Última actualización: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{analytics_data.get('summary', {}).get('total_documents', 0)}</div>
                <div class="stat-label">Total Documentos</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">{analytics_data.get('summary', {}).get('success_rate', 0) * 100:.1f}%</div>
                <div class="stat-label">Tasa de Éxito</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">{analytics_data.get('summary', {}).get('avg_confidence', 0) * 100:.1f}%</div>
                <div class="stat-label">Confianza Promedio</div>
            </div>
            
            <div class="stat-card">
                <div class="stat-value">{monitoring_data.get('alerts', {}).get('critical', 0) + monitoring_data.get('alerts', {}).get('error', 0)}</div>
                <div class="stat-label">Alertas Activas</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>Documentos por Tipo</h3>
                <canvas id="typeChart"></canvas>
            </div>
            
            <div class="chart-card">
                <h3>Tendencias de Calidad</h3>
                <canvas id="qualityChart"></canvas>
            </div>
        </div>
        
        <div class="table-container">
            <h3 style="margin-bottom: 15px;">Documentos Recientes</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Tipo</th>
                        <th>Confianza</th>
                        <th>Fecha</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody id="recentDocuments">
                </tbody>
            </table>
        </div>
        
        <button class="refresh-btn" onclick="location.reload()">Actualizar</button>
    </div>
    
    <script>
        // Datos para gráficos
        const typeData = {json.dumps(analytics_data.get('distribution', {}).get('by_type', {}))};
        const qualityTrends = {json.dumps(analytics_data.get('trends', {}))};
        
        // Gráfico de tipos
        const typeCtx = document.getElementById('typeChart').getContext('2d');
        new Chart(typeCtx, {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(typeData),
                datasets: [{{
                    data: Object.values(typeData),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#4facfe',
                        '#00f2fe',
                        '#43e97b'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true
            }}
        }});
        
        // Gráfico de tendencias
        const qualityCtx = document.getElementById('qualityChart').getContext('2d');
        new Chart(qualityCtx, {{
            type: 'line',
            data: {{
                labels: qualityTrends.dates || [],
                datasets: [{{
                    label: 'Confianza OCR',
                    data: qualityTrends.ocr_confidence || [],
                    borderColor: '#667eea',
                    tension: 0.1
                }}, {{
                    label: 'Confianza Clasificación',
                    data: qualityTrends.classification_confidence || [],
                    borderColor: '#764ba2',
                    tension: 0.1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        max: 1
                    }}
                }}
            }}
        }});
        
        // Auto-refresh cada 30 segundos
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        self.logger.info(f"Dashboard generado: {output_path}")
        return output_path


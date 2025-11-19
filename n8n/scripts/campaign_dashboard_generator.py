#!/usr/bin/env python3
"""
Campaign Dashboard Generator
Genera dashboards HTML interactivos para visualizar métricas de campaña en tiempo real
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path


class CampaignDashboardGenerator:
    """
    Generador de dashboards HTML para campañas
    Crea visualizaciones interactivas con Chart.js
    """
    
    def __init__(self, output_dir: str = "dashboards"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_dashboard(
        self,
        campaign_id: str,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None
    ) -> str:
        """
        Genera dashboard completo para una campaña
        
        Args:
            campaign_id: ID de la campaña
            metrics: Métricas actuales
            historical_data: Datos históricos (opcional)
        
        Returns:
            Ruta al archivo HTML generado
        """
        html_content = self._build_dashboard_html(campaign_id, metrics, historical_data)
        
        filename = f"campaign_{campaign_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(filepath)
    
    def _build_dashboard_html(
        self,
        campaign_id: str,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]]
    ) -> str:
        """Construye HTML del dashboard"""
        
        # Preparar datos para gráficos
        chart_data = self._prepare_chart_data(metrics, historical_data)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Campaña {campaign_id}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-label {{
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            color: #333;
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .metric-change {{
            font-size: 12px;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
        }}
        
        .metric-change.positive {{
            background: #d4edda;
            color: #155724;
        }}
        
        .metric-change.negative {{
            background: #f8d7da;
            color: #721c24;
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
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .chart-card h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 18px;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        .footer {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            color: #666;
            font-size: 12px;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard de Campaña</h1>
            <div class="meta">
                <strong>ID:</strong> {campaign_id} | 
                <strong>Última actualización:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Alcance Total</div>
                <div class="metric-value">{metrics.get('totalReach', 0):,}</div>
                <span class="metric-change positive">+{metrics.get('reachChange', 0):.1f}%</span>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Engagement Rate</div>
                <div class="metric-value">{metrics.get('engagementRate', 0):.2%}</div>
                <span class="metric-change {'positive' if metrics.get('engagementRate', 0) > 0.05 else 'negative'}">
                    {'+' if metrics.get('engagementChange', 0) > 0 else ''}{metrics.get('engagementChange', 0):.1f}%
                </span>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Leads Capturados</div>
                <div class="metric-value">{metrics.get('totalLeads', 0):,}</div>
                <span class="metric-change positive">+{metrics.get('leadsChange', 0):.1f}%</span>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Tasa de Conversión</div>
                <div class="metric-value">{metrics.get('conversionRate', 0):.2%}</div>
                <span class="metric-change {'positive' if metrics.get('conversionRate', 0) > 0.10 else 'negative'}">
                    {'+' if metrics.get('conversionChange', 0) > 0 else ''}{metrics.get('conversionChange', 0):.1f}%
                </span>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Revenue</div>
                <div class="metric-value">${metrics.get('totalRevenue', 0):,.2f}</div>
                <span class="metric-change positive">+{metrics.get('revenueChange', 0):.1f}%</span>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">ROI</div>
                <div class="metric-value">{metrics.get('roi', 0):.1f}%</div>
                <span class="metric-change {'positive' if metrics.get('roi', 0) > 0 else 'negative'}">
                    {'+' if metrics.get('roiChange', 0) > 0 else ''}{metrics.get('roiChange', 0):.1f}%
                </span>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📈 Engagement por Día</h3>
                <div class="chart-container">
                    <canvas id="engagementChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>💰 Revenue por Día</h3>
                <div class="chart-container">
                    <canvas id="revenueChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>📊 Distribución por Plataforma</h3>
                <div class="chart-container">
                    <canvas id="platformChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>🎯 Funnel de Conversión</h3>
                <div class="chart-container">
                    <canvas id="funnelChart"></canvas>
                </div>
            </div>
        </div>
        
        <div class="footer">
            Generado automáticamente por Campaign Dashboard Generator | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
    
    <script>
        // Datos para gráficos
        const chartData = {json.dumps(chart_data, ensure_ascii=False)};
        
        // Engagement Chart
        const engagementCtx = document.getElementById('engagementChart').getContext('2d');
        new Chart(engagementCtx, {{
            type: 'line',
            data: {{
                labels: chartData.engagement.labels,
                datasets: [{{
                    label: 'Engagement Rate',
                    data: chartData.engagement.data,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return (value * 100).toFixed(1) + '%';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Revenue Chart
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        new Chart(revenueCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.revenue.labels,
                datasets: [{{
                    label: 'Revenue ($)',
                    data: chartData.revenue.data,
                    backgroundColor: 'rgba(54, 162, 235, 0.6)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString();
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Platform Chart
        const platformCtx = document.getElementById('platformChart').getContext('2d');
        new Chart(platformCtx, {{
            type: 'doughnut',
            data: {{
                labels: chartData.platforms.labels,
                datasets: [{{
                    data: chartData.platforms.data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.6)',
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        display: true,
                        position: 'right'
                    }}
                }}
            }}
        }});
        
        // Funnel Chart
        const funnelCtx = document.getElementById('funnelChart').getContext('2d');
        new Chart(funnelCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.funnel.labels,
                datasets: [{{
                    label: 'Usuarios',
                    data: chartData.funnel.data,
                    backgroundColor: 'rgba(153, 102, 255, 0.6)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
        
        return html
    
    def _prepare_chart_data(
        self,
        metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]]
    ) -> Dict[str, Any]:
        """Prepara datos para los gráficos"""
        
        # Datos de ejemplo si no hay históricos
        if not historical_data:
            historical_data = [
                {"day": 1, "engagement": 0.04, "revenue": 500},
                {"day": 2, "engagement": 0.06, "revenue": 1200},
                {"day": 3, "engagement": 0.05, "revenue": 800}
            ]
        
        engagement_labels = [f"Día {d['day']}" for d in historical_data]
        engagement_data = [d.get('engagement', 0) for d in historical_data]
        
        revenue_labels = [f"Día {d['day']}" for d in historical_data]
        revenue_data = [d.get('revenue', 0) for d in historical_data]
        
        # Datos de plataformas
        platforms_data = metrics.get('platforms', {
            'instagram': 5000,
            'facebook': 3000,
            'linkedin': 2000
        })
        
        platform_labels = list(platforms_data.keys())
        platform_values = list(platforms_data.values())
        
        # Funnel de conversión
        funnel_labels = ['Alcance', 'Engagement', 'Leads', 'Conversiones']
        funnel_data = [
            metrics.get('totalReach', 0),
            int(metrics.get('totalReach', 0) * metrics.get('engagementRate', 0)),
            metrics.get('totalLeads', 0),
            metrics.get('totalSales', 0)
        ]
        
        return {
            "engagement": {
                "labels": engagement_labels,
                "data": engagement_data
            },
            "revenue": {
                "labels": revenue_labels,
                "data": revenue_data
            },
            "platforms": {
                "labels": platform_labels,
                "data": platform_values
            },
            "funnel": {
                "labels": funnel_labels,
                "data": funnel_data
            }
        }


def main():
    """Ejemplo de uso"""
    generator = CampaignDashboardGenerator(output_dir="dashboards")
    
    # Métricas de ejemplo
    metrics = {
        "totalReach": 10000,
        "engagementRate": 0.05,
        "totalLeads": 50,
        "conversionRate": 0.10,
        "totalRevenue": 5000,
        "roi": 150.0,
        "reachChange": 15.5,
        "engagementChange": 2.3,
        "leadsChange": 25.0,
        "conversionChange": 5.0,
        "revenueChange": 30.0,
        "roiChange": 10.0,
        "platforms": {
            "instagram": 5000,
            "facebook": 3000,
            "linkedin": 2000
        },
        "totalSales": 5
    }
    
    # Generar dashboard
    filepath = generator.generate_dashboard(
        campaign_id="campaign_123",
        metrics=metrics
    )
    
    print(f"Dashboard generado: {filepath}")


if __name__ == "__main__":
    main()










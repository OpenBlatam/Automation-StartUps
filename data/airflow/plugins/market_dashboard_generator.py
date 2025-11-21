"""
Generador de Dashboards Visuales para Investigación de Mercado

Genera dashboards HTML interactivos con visualizaciones de tendencias,
insights, predicciones y análisis de mercado.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)


class MarketDashboardGenerator:
    """Generador de dashboards visuales."""
    
    def __init__(self):
        """Inicializa el generador."""
        self.logger = logging.getLogger(__name__)
    
    def generate_dashboard(
        self,
        market_analysis: Dict[str, Any],
        insights: List[Dict[str, Any]],
        predictions: Optional[List[Dict[str, Any]]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Genera dashboard HTML completo.
        
        Args:
            market_analysis: Análisis completo de mercado
            insights: Lista de insights
            predictions: Predicciones ML (opcional)
            output_path: Ruta para guardar (opcional)
            
        Returns:
            HTML del dashboard
        """
        industry = market_analysis.get("industry", "Unknown")
        trends = market_analysis.get("trends", [])
        opportunities = market_analysis.get("opportunities", [])
        risks = market_analysis.get("risk_factors", [])
        
        # Preparar datos para gráficos
        trends_data = self._prepare_trends_data(trends)
        insights_by_priority = self._group_insights_by_priority(insights)
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Market Research Dashboard - {industry}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
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
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #667eea;
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
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .metric-value {{
            font-size: 42px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        .metric-label {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .chart-container {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .chart-container h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 20px;
        }}
        .insights-section {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .insight-card {{
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid;
            background: #f8f9fa;
        }}
        .insight-card.high {{
            border-left-color: #d32f2f;
            background: #ffebee;
        }}
        .insight-card.medium {{
            border-left-color: #f57c00;
            background: #fff3e0;
        }}
        .insight-card.low {{
            border-left-color: #1976d2;
            background: #e3f2fd;
        }}
        .insight-title {{
            font-weight: bold;
            font-size: 18px;
            margin-bottom: 10px;
            color: #333;
        }}
        .insight-description {{
            color: #666;
            margin-bottom: 15px;
            line-height: 1.6;
        }}
        .insight-steps {{
            margin-top: 15px;
        }}
        .insight-steps ol {{
            margin-left: 20px;
            color: #555;
        }}
        .insight-steps li {{
            margin: 8px 0;
            line-height: 1.5;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: bold;
            text-transform: uppercase;
        }}
        .badge.high {{
            background: #d32f2f;
            color: white;
        }}
        .badge.medium {{
            background: #f57c00;
            color: white;
        }}
        .badge.low {{
            background: #1976d2;
            color: white;
        }}
        .badge.opportunity {{
            background: #388e3c;
            color: white;
        }}
        .badge.risk {{
            background: #d32f2f;
            color: white;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 16px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }}
        .tab.active {{
            color: #667eea;
            border-bottom-color: #667eea;
            font-weight: bold;
        }}
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Market Research Dashboard</h1>
            <div class="meta">
                <strong>Industry:</strong> {industry} | 
                <strong>Analysis Date:</strong> {market_analysis.get('analysis_date', datetime.utcnow().isoformat())} |
                <strong>Timeframe:</strong> {market_analysis.get('timeframe_months', 6)} months
            </div>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{len(trends)}</div>
                <div class="metric-label">Trends Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(insights)}</div>
                <div class="metric-label">Actionable Insights</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(opportunities)}</div>
                <div class="metric-label">Opportunities</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len(risks)}</div>
                <div class="metric-label">Risk Factors</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{len([i for i in insights if i.get('priority') == 'high'])}</div>
                <div class="metric-label">High Priority</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>📈 Trends Overview</h3>
            <canvas id="trendsChart" style="max-height: 400px;"></canvas>
        </div>
        
        {self._generate_predictions_section(predictions) if predictions else ''}
        
        <div class="insights-section">
            <div class="tabs">
                <button class="tab active" onclick="showTab('all')">All Insights</button>
                <button class="tab" onclick="showTab('high')">High Priority</button>
                <button class="tab" onclick="showTab('opportunities')">Opportunities</button>
                <button class="tab" onclick="showTab('risks')">Risks</button>
            </div>
            
            <div id="tab-all" class="tab-content active">
                {self._generate_insights_html(insights)}
            </div>
            <div id="tab-high" class="tab-content">
                {self._generate_insights_html([i for i in insights if i.get('priority') == 'high'])}
            </div>
            <div id="tab-opportunities" class="tab-content">
                {self._generate_insights_html([i for i in insights if i.get('category') == 'opportunity'])}
            </div>
            <div id="tab-risks" class="tab-content">
                {self._generate_insights_html([i for i in insights if i.get('category') == 'threat'])}
            </div>
        </div>
    </div>
    
    <script>
        // Datos para gráficos
        const trendsData = {json.dumps(trends_data)};
        
        // Gráfico de tendencias
        const ctx = document.getElementById('trendsChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: trendsData.labels,
                datasets: trendsData.datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: true,
                        text: 'Market Trends Over Time'
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: false
                    }}
                }}
            }}
        }});
        
        // Tabs functionality
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(`tab-${{tabName}}`).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            self.logger.info(f"Dashboard saved to {output_path}")
        
        return html
    
    def _prepare_trends_data(self, trends: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Prepara datos para gráficos de tendencias."""
        # Agrupar por categoría
        categories = {}
        for trend in trends:
            category = trend.get("category", "unknown")
            if category not in categories:
                categories[category] = []
            categories[category].append(trend)
        
        # Preparar datasets para Chart.js
        datasets = []
        colors = [
            {'border': 'rgb(102, 126, 234)', 'bg': 'rgba(102, 126, 234, 0.1)'},
            {'border': 'rgb(118, 75, 162)', 'bg': 'rgba(118, 75, 162, 0.1)'},
            {'border': 'rgb(56, 142, 60)', 'bg': 'rgba(56, 142, 60, 0.1)'},
            {'border': 'rgb(245, 124, 0)', 'bg': 'rgba(245, 124, 0, 0.1)'},
        ]
        
        for i, (category, category_trends) in enumerate(categories.items()):
            color = colors[i % len(colors)]
            values = [t.get("current_value", 0) for t in category_trends]
            labels = [t.get("trend_name", "Unknown")[:30] for t in category_trends]
            
            datasets.append({
                "label": category.replace("_", " ").title(),
                "data": values,
                "borderColor": color['border'],
                "backgroundColor": color['bg'],
                "tension": 0.4
            })
        
        return {
            "labels": labels if labels else ["Trend 1", "Trend 2", "Trend 3"],
            "datasets": datasets
        }
    
    def _group_insights_by_priority(self, insights: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa insights por prioridad."""
        grouped = {"high": [], "medium": [], "low": []}
        for insight in insights:
            priority = insight.get("priority", "low")
            if priority in grouped:
                grouped[priority].append(insight)
        return grouped
    
    def _generate_insights_html(self, insights: List[Dict[str, Any]]) -> str:
        """Genera HTML para lista de insights."""
        if not insights:
            return "<p>No insights available.</p>"
        
        html = ""
        for insight in insights:
            priority = insight.get("priority", "low")
            category = insight.get("category", "trend")
            title = insight.get("title", "Untitled Insight")
            description = insight.get("description", "")
            steps = insight.get("actionable_steps", [])
            impact = insight.get("expected_impact", "")
            
            html += f"""
            <div class="insight-card {priority}">
                <div class="insight-title">
                    {title}
                    <span class="badge {priority}">{priority}</span>
                    <span class="badge {category}">{category}</span>
                </div>
                <div class="insight-description">{description}</div>
                <div><strong>Expected Impact:</strong> {impact}</div>
                {f'<div class="insight-steps"><strong>Actionable Steps:</strong><ol>{"".join([f"<li>{step}</li>" for step in steps])}</ol></div>' if steps else ''}
            </div>
            """
        
        return html
    
    def _generate_predictions_section(self, predictions: Optional[List[Dict[str, Any]]]) -> str:
        """Genera sección de predicciones ML."""
        if not predictions:
            return ""
        
        predictions_html = '<div class="chart-container"><h3>🔮 ML Predictions</h3><canvas id="predictionsChart"></canvas></div>'
        # Agregar lógica para gráfico de predicciones
        return predictions_html







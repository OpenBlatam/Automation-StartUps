#!/usr/bin/env python3
"""
Generador de Dashboard HTML Interactivo para Testimonios
Crea dashboards visuales con gráficos y métricas
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class DashboardGenerator:
    """Genera dashboards HTML interactivos con visualizaciones"""
    
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Análisis de Testimonios</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
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
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        .subtitle {{
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}
        .chart-container {{
            background: #f8f9fa;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .chart-title {{
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        .recommendations {{
            background: #e3f2fd;
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid #2196f3;
            margin-top: 30px;
        }}
        .recommendations h3 {{
            color: #1976d2;
            margin-bottom: 15px;
        }}
        .recommendations ul {{
            list-style: none;
            padding-left: 0;
        }}
        .recommendations li {{
            padding: 10px;
            margin: 5px 0;
            background: white;
            border-radius: 8px;
            border-left: 3px solid #2196f3;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge-excellent {{
            background: #4caf50;
            color: white;
        }}
        .badge-good {{
            background: #8bc34a;
            color: white;
        }}
        .badge-average {{
            background: #ff9800;
            color: white;
        }}
        .badge-poor {{
            background: #f44336;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Dashboard de Análisis de Testimonios</h1>
        <p class="subtitle">Generado el {timestamp}</p>
        
        <div class="metrics-grid">
            {metrics_cards}
        </div>
        
        <div class="charts-grid">
            {charts}
        </div>
        
        {recommendations_section}
    </div>
    
    <script>
        {charts_js}
    </script>
</body>
</html>
"""
    
    def generate_dashboard(
        self,
        post_data: Dict[str, Any],
        platform: str,
        output_file: Optional[str] = None
    ) -> str:
        """
        Genera un dashboard HTML interactivo
        
        Args:
            post_data: Datos de la publicación generada
            platform: Plataforma objetivo
            output_file: Archivo de salida (opcional)
        
        Returns:
            Contenido HTML del dashboard
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Generar métricas principales
        metrics_cards = self._generate_metrics_cards(post_data)
        
        # Generar gráficos
        charts_html, charts_js = self._generate_charts(post_data, platform)
        
        # Generar recomendaciones
        recommendations_section = self._generate_recommendations_section(post_data)
        
        # Construir HTML
        html_content = self.HTML_TEMPLATE.format(
            timestamp=timestamp,
            metrics_cards=metrics_cards,
            charts=charts_html,
            recommendations_section=recommendations_section,
            charts_js=charts_js
        )
        
        # Guardar si se especifica archivo
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Dashboard guardado en: {output_file}")
        
        return html_content
    
    def _generate_metrics_cards(self, post_data: Dict[str, Any]) -> str:
        """Genera las tarjetas de métricas principales"""
        cards = []
        
        # Score de engagement
        if "engagement_prediction" in post_data:
            pred = post_data["engagement_prediction"]
            score = pred.get("predicted_score", 0)
            cards.append(f"""
                <div class="metric-card">
                    <div class="metric-label">Score de Engagement</div>
                    <div class="metric-value">{score:.1f}/100</div>
                </div>
            """)
            
            # Engagement rate
            rate = pred.get("predicted_engagement_rate", 0)
            cards.append(f"""
                <div class="metric-card">
                    <div class="metric-label">Engagement Rate Estimado</div>
                    <div class="metric-value">{rate:.2f}%</div>
                </div>
            """)
        
        # Score general
        if "analytics_report" in post_data and "overall_score" in post_data["analytics_report"]:
            score_data = post_data["analytics_report"]["overall_score"]
            grade = score_data.get("grade", "N/A")
            percentage = score_data.get("percentage", 0)
            
            badge_class = {
                "A+": "badge-excellent",
                "A": "badge-good",
                "B": "badge-average",
                "C": "badge-average",
                "D": "badge-poor"
            }.get(grade, "badge-average")
            
            cards.append(f"""
                <div class="metric-card">
                    <div class="metric-label">Score General</div>
                    <div class="metric-value">
                        {percentage:.1f}%
                        <span class="badge {badge_class}">{grade}</span>
                    </div>
                </div>
            """)
        
        # Longitud
        length = post_data.get("length", 0)
        cards.append(f"""
            <div class="metric-card">
                <div class="metric-label">Longitud del Contenido</div>
                <div class="metric-value">{length}</div>
            </div>
        """)
        
        # Hashtags
        hashtags_count = len(post_data.get("hashtags", []))
        cards.append(f"""
            <div class="metric-card">
                <div class="metric-label">Hashtags</div>
                <div class="metric-value">{hashtags_count}</div>
            </div>
        """)
        
        return "\n".join(cards)
    
    def _generate_charts(self, post_data: Dict[str, Any], platform: str) -> tuple:
        """Genera gráficos HTML y JavaScript"""
        charts_html = []
        charts_js_parts = []
        
        # Gráfico de factores de engagement
        if "engagement_prediction" in post_data:
            factors = post_data["engagement_prediction"].get("factors", {})
            chart_id = "factorsChart"
            
            charts_html.append(f"""
                <div class="chart-container">
                    <div class="chart-title">Factores de Engagement</div>
                    <canvas id="{chart_id}"></canvas>
                </div>
            """)
            
            factors_data = {
                "Longitud": factors.get("length_factor", 1.0) * 100,
                "Hashtags": factors.get("hashtag_factor", 1.0) * 100,
                "Números": 150 if factors.get("has_numbers", False) else 100,
                "Emojis": 120 if factors.get("has_emojis", False) else 100,
                "CTA": 140 if factors.get("has_cta", False) else 100,
                "Storytelling": 160 if factors.get("has_storytelling", False) else 100
            }
            
            charts_js_parts.append(f"""
                const ctx{chart_id} = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx{chart_id}, {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(list(factors_data.keys()))},
                        datasets: [{{
                            label: 'Impacto (%)',
                            data: {json.dumps(list(factors_data.values()))},
                            backgroundColor: [
                                'rgba(102, 126, 234, 0.8)',
                                'rgba(118, 75, 162, 0.8)',
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)',
                                'rgba(255, 206, 86, 0.8)',
                                'rgba(75, 192, 192, 0.8)'
                            ],
                            borderColor: [
                                'rgba(102, 126, 234, 1)',
                                'rgba(118, 75, 162, 1)',
                                'rgba(255, 99, 132, 1)',
                                'rgba(54, 162, 235, 1)',
                                'rgba(255, 206, 86, 1)',
                                'rgba(75, 192, 192, 1)'
                            ],
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            y: {{
                                beginAtZero: true,
                                max: 200
                            }}
                        }}
                    }}
                }});
            """)
        
        # Gráfico de comparación con benchmarks
        if "analytics_report" in post_data and "benchmark_comparison" in post_data["analytics_report"]:
            bench = post_data["analytics_report"]["benchmark_comparison"]
            chart_id = "benchmarkChart"
            
            charts_html.append(f"""
                <div class="chart-container">
                    <div class="chart-title">Comparación con Benchmarks</div>
                    <canvas id="{chart_id}"></canvas>
                </div>
            """)
            
            charts_js_parts.append(f"""
                const ctx{chart_id} = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx{chart_id}, {{
                    type: 'radar',
                    data: {{
                        labels: ['Tu Score', 'Promedio Industria', 'Top 10%'],
                        datasets: [{{
                            label: 'Engagement Rate (%)',
                            data: [
                                {bench.get('your_score', 0)},
                                {bench.get('industry_average', 0)},
                                {bench.get('top_percentile', 0)}
                            ],
                            backgroundColor: 'rgba(102, 126, 234, 0.2)',
                            borderColor: 'rgba(102, 126, 234, 1)',
                            pointBackgroundColor: 'rgba(102, 126, 234, 1)',
                            pointBorderColor: '#fff',
                            pointHoverBackgroundColor: '#fff',
                            pointHoverBorderColor: 'rgba(102, 126, 234, 1)'
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        scales: {{
                            r: {{
                                beginAtZero: true
                            }}
                        }}
                    }}
                }});
            """)
        
        # Gráfico de distribución de score
        if "analytics_report" in post_data and "overall_score" in post_data["analytics_report"]:
            score_data = post_data["analytics_report"]["overall_score"]
            chart_id = "scoreChart"
            
            charts_html.append(f"""
                <div class="chart-container">
                    <div class="chart-title">Distribución del Score</div>
                    <canvas id="{chart_id}"></canvas>
                </div>
            """)
            
            factors = score_data.get("factors", [])
            factor_names = [f.split(":")[0] if ":" in f else f for f in factors[:5]]
            factor_scores = []
            
            # Extraer scores aproximados de los factores
            for factor in factors:
                if "Predicción engagement" in factor:
                    factor_scores.append(40)
                elif "Optimización" in factor:
                    factor_scores.append(20)
                elif "Análisis completo" in factor:
                    factor_scores.append(20)
                elif "Calidad contenido" in factor:
                    factor_scores.append(20)
                else:
                    factor_scores.append(10)
            
            charts_js_parts.append(f"""
                const ctx{chart_id} = document.getElementById('{chart_id}').getContext('2d');
                new Chart(ctx{chart_id}, {{
                    type: 'doughnut',
                    data: {{
                        labels: {json.dumps(factor_names)},
                        datasets: [{{
                            data: {json.dumps(factor_scores)},
                            backgroundColor: [
                                'rgba(102, 126, 234, 0.8)',
                                'rgba(118, 75, 162, 0.8)',
                                'rgba(255, 99, 132, 0.8)',
                                'rgba(54, 162, 235, 0.8)',
                                'rgba(255, 206, 86, 0.8)'
                            ]
                        }}]
                    }},
                    options: {{
                        responsive: true
                    }}
                }});
            """)
        
        charts_js = "\n".join(charts_js_parts)
        charts_html_str = "\n".join(charts_html)
        
        return charts_html_str, charts_js
    
    def _generate_recommendations_section(self, post_data: Dict[str, Any]) -> str:
        """Genera la sección de recomendaciones"""
        recommendations = []
        
        # Recomendaciones de engagement
        if "engagement_prediction" in post_data:
            pred_recs = post_data["engagement_prediction"].get("recommendations", [])
            recommendations.extend(pred_recs[:5])
        
        # Recomendaciones de optimización
        if "engagement_optimization" in post_data:
            opt = post_data["engagement_optimization"]
            if opt.get("engagement_boosters"):
                recommendations.extend(opt["engagement_boosters"][:3])
        
        # Recomendaciones del reporte
        if "analytics_report" in post_data and "recommendations" in post_data["analytics_report"]:
            recommendations.extend(post_data["analytics_report"]["recommendations"])
        
        if not recommendations:
            return ""
        
        recommendations_html = "\n".join([
            f"<li>• {rec}</li>" for rec in recommendations[:10]
        ])
        
        return f"""
        <div class="recommendations">
            <h3>💡 Recomendaciones</h3>
            <ul>
                {recommendations_html}
            </ul>
        </div>
        """



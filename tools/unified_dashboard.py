#!/usr/bin/env python3
"""
Dashboard Unificado Interactivo
Genera dashboard HTML completo con todas las métricas y visualizaciones
"""
import csv
import sys
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_creatives():
    """Carga creativos desde CSV Master"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        return None
    
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creatives.append(row)
    
    return creatives

def calculate_summary_metrics(creatives):
    """Calcula métricas resumen"""
    total = len(creatives)
    
    by_format = defaultdict(int)
    by_angle = defaultdict(int)
    by_product = defaultdict(int)
    
    total_impressions = 0
    total_clicks = 0
    total_spend = 0
    total_conversions = 0
    creatives_with_metrics = 0
    
    for creative in creatives:
        by_format[creative.get('formato', 'unknown')] += 1
        by_angle[creative.get('angulo', 'unknown')] += 1
        by_product[creative.get('producto', 'unknown')] += 1
        
        impressions = float(creative.get('impressions', 0) or 0)
        if impressions > 0:
            creatives_with_metrics += 1
            total_impressions += impressions
            total_clicks += float(creative.get('clicks', 0) or 0)
            total_spend += float(creative.get('spend', 0) or 0)
            total_conversions += float(creative.get('conversions', 0) or 0)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
    avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
    
    assumed_ltv = 500
    total_revenue = total_conversions * assumed_ltv
    total_roi = ((total_revenue - total_spend) / total_spend * 100) if total_spend > 0 else 0
    
    return {
        'total': total,
        'with_metrics': creatives_with_metrics,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'total_spend': total_spend,
        'total_conversions': total_conversions,
        'avg_ctr': avg_ctr,
        'avg_cpc': avg_cpc,
        'avg_cpa': avg_cpa,
        'total_revenue': total_revenue,
        'total_roi': total_roi,
        'by_format': dict(by_format),
        'by_angle': dict(by_angle),
        'by_product': dict(by_product)
    }

def generate_html_dashboard(metrics):
    """Genera dashboard HTML interactivo"""
    
    # Preparar datos para JavaScript
    format_labels = json.dumps(list(metrics['by_format'].keys()))
    format_data = json.dumps(list(metrics['by_format'].values()))
    angle_labels = json.dumps(list(metrics['by_angle'].keys()))
    angle_data = json.dumps(list(metrics['by_angle'].values()))
    product_labels = json.dumps(list(metrics['by_product'].keys()))
    product_data = json.dumps(list(metrics['by_product'].values()))
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Unificado - Creativos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }}
        
        h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .subtitle {{
            color: #666;
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
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }}
        
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}
        
        .metric-value {{
            font-size: 2em;
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
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        
        .chart-title {{
            font-size: 1.3em;
            color: #333;
            margin-bottom: 20px;
            font-weight: 600;
        }}
        
        footer {{
            text-align: center;
            color: #666;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Dashboard Unificado</h1>
            <p class="subtitle">Análisis completo de performance de creativos</p>
            <p class="subtitle">Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Creativos</div>
                <div class="metric-value">{metrics['total']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Con Métricas</div>
                <div class="metric-value">{metrics['with_metrics']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Impresiones Totales</div>
                <div class="metric-value">{metrics['total_impressions']:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Clics Totales</div>
                <div class="metric-value">{metrics['total_clicks']:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">CTR Promedio</div>
                <div class="metric-value">{metrics['avg_ctr']:.2f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Gasto Total</div>
                <div class="metric-value">${metrics['total_spend']:,.2f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Conversiones</div>
                <div class="metric-value">{metrics['total_conversions']:,.0f}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">ROI Total</div>
                <div class="metric-value">{metrics['total_roi']:.1f}%</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-container">
                <div class="chart-title">📐 Distribución por Formato</div>
                <canvas id="formatChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🎯 Distribución por Ángulo</div>
                <canvas id="angleChart"></canvas>
            </div>
            
            <div class="chart-container">
                <div class="chart-title">🏢 Distribución por Producto</div>
                <canvas id="productChart"></canvas>
            </div>
        </div>
        
        <footer>
            <p>💡 Actualiza los datos ejecutando: python3 tools/analyze_real_time_performance.py</p>
            <p>📊 Para análisis detallado, consulta los reportes individuales en reports/</p>
        </footer>
    </div>
    
    <script>
        // Datos para gráficos
        const formatData = {{
            labels: {format_labels},
            data: {format_data}
        }};
        
        const angleData = {{
            labels: {angle_labels},
            data: {angle_data}
        }};
        
        const productData = {{
            labels: {product_labels},
            data: {product_data}
        }};
        
        // Gráfico de formatos
        new Chart(document.getElementById('formatChart'), {{
            type: 'doughnut',
            data: {{
                labels: formatData.labels,
                datasets: [{{
                    data: formatData.data,
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#4facfe',
                        '#43e97b'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
        
        // Gráfico de ángulos
        new Chart(document.getElementById('angleChart'), {{
            type: 'bar',
            data: {{
                labels: angleData.labels,
                datasets: [{{
                    label: 'Cantidad',
                    data: angleData.data,
                    backgroundColor: '#667eea'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Gráfico de productos
        new Chart(document.getElementById('productChart'), {{
            type: 'pie',
            data: {{
                labels: productData.labels,
                datasets: [{{
                    data: productData.data,
                    backgroundColor: [
                        '#4facfe',
                        '#43e97b',
                        '#f093fb',
                        '#fa709a'
                    ]
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>"""
    
    return html

def main():
    print("=" * 80)
    print("📊 Generador de Dashboard Unificado")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Calcular métricas
    metrics = calculate_summary_metrics(creatives)
    
    print("📊 Métricas calculadas:")
    print(f"   Total creativos: {metrics['total']}")
    print(f"   Con métricas: {metrics['with_metrics']}")
    print(f"   ROI total: {metrics['total_roi']:.1f}%")
    print()
    
    # Generar HTML
    print("🎨 Generando dashboard HTML...")
    html_content = generate_html_dashboard(metrics)
    
    # Guardar
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    exports_dir = root_dir / 'exports'
    exports_dir.mkdir(exist_ok=True)
    
    dashboard_path = exports_dir / 'unified_dashboard.html'
    
    with open(dashboard_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard generado: {dashboard_path}")
    print()
    print("🌐 Abre el archivo en tu navegador para ver el dashboard interactivo")
    print()

if __name__ == '__main__':
    main()


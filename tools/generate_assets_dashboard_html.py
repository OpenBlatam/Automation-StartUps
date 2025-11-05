#!/usr/bin/env python3
"""
Genera dashboard HTML interactivo con análisis completo de assets
Combina datos de analyze_assets.sh con CSV Master
"""
import csv
import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_csv_master():
    """Carga el CSV Master"""
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

def analyze_creatives(creatives):
    """Analiza creativos y genera estadísticas"""
    stats = {
        'total': len(creatives),
        'by_format': defaultdict(int),
        'by_product': defaultdict(int),
        'by_angle': defaultdict(int),
        'by_placement': defaultdict(int),
        'utms_complete': 0,
        'utms_incomplete': 0
    }
    
    for creative in creatives:
        # Por formato
        formato = creative.get('formato', 'unknown')
        stats['by_format'][formato] += 1
        
        # Por producto
        producto = creative.get('producto', 'unknown')
        stats['by_product'][producto] += 1
        
        # Por ángulo
        angulo = creative.get('angulo', 'unknown')
        stats['by_angle'][angulo] += 1
        
        # Por placement
        placement = creative.get('placement', 'unknown')
        stats['by_placement'][placement] += 1
        
        # UTMs completos
        required_utms = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'final_url']
        if all(creative.get(field) for field in required_utms):
            stats['utms_complete'] += 1
        else:
            stats['utms_incomplete'] += 1
    
    return stats

def generate_html_dashboard(creatives, stats):
    """Genera dashboard HTML interactivo"""
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dashboard de Assets - Análisis Completo</title>
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
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .header p {{
            color: #666;
            font-size: 1.1em;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            color: #333;
            font-size: 2.5em;
            font-weight: bold;
        }}
        .stat-card .label {{
            color: #999;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        .chart-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.5em;
        }}
        .table-container {{
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            overflow-x: auto;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th {{
            background: #f8f9fa;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
        }}
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #dee2e6;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
        .badge-danger {{
            background: #f8d7da;
            color: #721c24;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard de Assets</h1>
            <p>Análisis completo generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Creativos</h3>
                <div class="value">{stats['total']}</div>
                <div class="label">Registrados en CSV Master</div>
            </div>
            <div class="stat-card">
                <h3>UTMs Completos</h3>
                <div class="value">{stats['utms_complete']}</div>
                <div class="label">{int((stats['utms_complete'] / stats['total']) * 100) if stats['total'] > 0 else 0}% cobertura</div>
            </div>
            <div class="stat-card">
                <h3>Formatos Únicos</h3>
                <div class="value">{len(stats['by_format'])}</div>
                <div class="label">Tipos diferentes</div>
            </div>
            <div class="stat-card">
                <h3>Productos</h3>
                <div class="value">{len(stats['by_product'])}</div>
                <div class="label">Líneas de producto</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>Distribución por Formato</h2>
            <canvas id="formatChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>Distribución por Producto</h2>
            <canvas id="productChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>Distribución por Ángulo</h2>
            <canvas id="angleChart"></canvas>
        </div>
        
        <div class="table-container">
            <h2 style="margin-bottom: 20px;">Lista Completa de Creativos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Creative File</th>
                        <th>Producto</th>
                        <th>Formato</th>
                        <th>Ángulo</th>
                        <th>Placement</th>
                        <th>UTM Content</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Añadir filas de tabla
    for creative in creatives:
        required_utms = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'final_url']
        utm_complete = all(creative.get(field) for field in required_utms)
        
        status_badge = '<span class="badge badge-success">✅ Completo</span>' if utm_complete else '<span class="badge badge-warning">⚠️ Incompleto</span>'
        
        html += f"""
                    <tr>
                        <td><strong>{creative.get('creative_file', 'N/A')}</strong></td>
                        <td>{creative.get('producto', 'N/A')}</td>
                        <td>{creative.get('formato', 'N/A')}</td>
                        <td>{creative.get('angulo', 'N/A')}</td>
                        <td>{creative.get('placement', 'N/A')}</td>
                        <td><code style="background: #f8f9fa; padding: 3px 8px; border-radius: 4px;">{creative.get('utm_content', 'N/A')[:30]}...</code></td>
                        <td>{status_badge}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        // Chart.js config
        const chartOptions = {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom',
                }
            }
        };
        
        // Formato Chart
        const formatData = """ + json.dumps({
            'labels': list(stats['by_format'].keys()),
            'datasets': [{
                'label': 'Creativos',
                'data': list(stats['by_format'].values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                ]
            }]
        }) + """;
        
        new Chart(document.getElementById('formatChart'), {
            type: 'doughnut',
            data: formatData,
            options: chartOptions
        });
        
        // Product Chart
        const productData = """ + json.dumps({
            'labels': list(stats['by_product'].keys()),
            'datasets': [{
                'label': 'Creativos',
                'data': list(stats['by_product'].values()),
                'backgroundColor': [
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                ]
            }]
        }) + """;
        
        new Chart(document.getElementById('productChart'), {
            type: 'bar',
            data: productData,
            options: chartOptions
        });
        
        // Angle Chart
        const angleData = """ + json.dumps({
            'labels': list(stats['by_angle'].keys()),
            'datasets': [{
                'label': 'Creativos',
                'data': list(stats['by_angle'].values()),
                'backgroundColor': [
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 206, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                ]
            }]
        }) + """;
        
        new Chart(document.getElementById('angleChart'), {
            type: 'pie',
            data: angleData,
            options: chartOptions
        });
    </script>
    
    <div class="footer">
        <p>Generado automáticamente por generate_assets_dashboard_html.py</p>
    </div>
</body>
</html>
"""
    
    return html

def main():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    output_path = root_dir / 'exports' / 'assets_dashboard.html'
    
    print("📊 Generando dashboard HTML...")
    
    # Cargar creativos
    creatives = load_csv_master()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    
    # Analizar
    stats = analyze_creatives(creatives)
    
    # Generar HTML
    html = generate_html_dashboard(creatives, stats)
    
    # Guardar
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✅ Dashboard generado: {output_path}")
    print(f"💡 Abre en tu navegador para ver visualizaciones interactivas")

if __name__ == '__main__':
    main()



#!/usr/bin/env python3
"""
Generador de Dashboard de KPIs Centralizado

Genera un dashboard HTML interactivo consolidando todos los KPIs y métricas
del sistema de gestión de creativos.
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import statistics

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def calculate_kpis(creatives: List[Dict]) -> Dict:
    """Calcula todos los KPIs principales"""
    kpis = {
        'portfolio': {},
        'performance': {},
        'distribution': {},
        'health': {}
    }
    
    total = len(creatives)
    
    # KPIs de Portfolio
    kpis['portfolio'] = {
        'total_creatives': total,
        'with_metrics': sum(1 for c in creatives if c.get('ctr')),
        'active': sum(1 for c in creatives if c.get('status', '').lower() == 'active'),
        'unique_formats': len(set(c.get('format', '').lower() for c in creatives if c.get('format'))),
        'unique_angles': len(set(c.get('angle', '').lower() for c in creatives if c.get('angle'))),
        'unique_products': len(set(c.get('product', '') for c in creatives if c.get('product')))
    }
    
    # KPIs de Performance
    ctrs = []
    cvrs = []
    impressions_total = 0
    spend_total = 0
    
    for c in creatives:
        ctr_val = c.get('ctr', '')
        cvr_val = c.get('conversion_rate', '')
        imp_val = c.get('impressions', '')
        spend_val = c.get('spend', '')
        
        if ctr_val:
            try:
                ctrs.append(float(ctr_val.replace('%', '')))
            except:
                pass
        
        if cvr_val:
            try:
                cvrs.append(float(cvr_val.replace('%', '')))
            except:
                pass
        
        if imp_val:
            try:
                impressions_total += int(imp_val)
            except:
                pass
        
        if spend_val:
            try:
                spend_total += float(spend_val)
            except:
                pass
    
    avg_ctr = statistics.mean(ctrs) if ctrs else 0
    avg_cvr = statistics.mean(cvrs) if cvrs else 0
    high_performers = sum(1 for ctr in ctrs if ctr > 0.7)
    low_performers = sum(1 for ctr in ctrs if ctr < 0.3)
    
    kpis['performance'] = {
        'avg_ctr': avg_ctr,
        'avg_cvr': avg_cvr,
        'high_performers_count': high_performers,
        'high_performers_pct': (high_performers / len(ctrs) * 100) if ctrs else 0,
        'low_performers_count': low_performers,
        'low_performers_pct': (low_performers / len(ctrs) * 100) if ctrs else 0,
        'total_impressions': impressions_total,
        'total_spend': spend_total,
        'avg_cpc': (spend_total / impressions_total * 1000) if impressions_total > 0 else 0
    }
    
    # KPIs de Distribución
    format_dist = Counter(c.get('format', '').lower() for c in creatives if c.get('format'))
    angle_dist = Counter(c.get('angle', '').lower() for c in creatives if c.get('angle'))
    product_dist = Counter(c.get('product', '') for c in creatives if c.get('product'))
    
    kpis['distribution'] = {
        'formats': dict(format_dist.most_common(10)),
        'angles': dict(angle_dist.most_common(10)),
        'products': dict(product_dist.most_common(10)),
        'diversity_score': len(format_dist) * len(angle_dist)
    }
    
    # KPIs de Health
    gaps = 0  # Simplificado - debería venir de análisis de gaps
    issues = low_performers
    
    kpis['health'] = {
        'score': max(0, min(100, 100 - (issues / max(total, 1) * 50))),
        'gaps_count': gaps,
        'issues_count': issues,
        'coverage_pct': (kpis['portfolio']['with_metrics'] / max(total, 1)) * 100
    }
    
    return kpis

def generate_html_dashboard(kpis: Dict, output_file: Path):
    """Genera dashboard HTML interactivo"""
    
    # Preparar datos para JavaScript
    format_labels = json.dumps(list(kpis['distribution']['formats'].keys()))
    format_data = json.dumps(list(kpis['distribution']['formats'].values()))
    angle_labels = json.dumps(list(kpis['distribution']['angles'].keys()))
    angle_data = json.dumps(list(kpis['distribution']['angles'].values()))
    
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard KPIs - Creativos</title>
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
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .kpi-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        
        .kpi-card:hover {{
            transform: translateY(-5px);
        }}
        
        .kpi-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        
        .kpi-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .kpi-trend {{
            font-size: 0.8em;
            margin-top: 5px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .chart-card {{
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        
        .chart-card h3 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 1.3em;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 5px;
        }}
        
        .status-excellent {{ background: #10b981; }}
        .status-good {{ background: #3b82f6; }}
        .status-warning {{ background: #f59e0b; }}
        .status-poor {{ background: #ef4444; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard KPIs - Creativos</h1>
            <div class="timestamp">Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Total Creativos</div>
                <div class="kpi-value">{kpis['portfolio']['total_creatives']}</div>
                <div class="kpi-trend">Con métricas: {kpis['portfolio']['with_metrics']}</div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">CTR Promedio</div>
                <div class="kpi-value">{kpis['performance']['avg_ctr']:.2f}%</div>
                <div class="kpi-trend">
                    <span class="status-indicator status-{'excellent' if kpis['performance']['avg_ctr'] >= 0.8 else 'good' if kpis['performance']['avg_ctr'] >= 0.5 else 'warning' if kpis['performance']['avg_ctr'] >= 0.3 else 'poor'}"></span>
                    {'Excelente' if kpis['performance']['avg_ctr'] >= 0.8 else 'Bueno' if kpis['performance']['avg_ctr'] >= 0.5 else 'Atención' if kpis['performance']['avg_ctr'] >= 0.3 else 'Mejorar'}
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">High Performers</div>
                <div class="kpi-value">{kpis['performance']['high_performers_count']}</div>
                <div class="kpi-trend">{kpis['performance']['high_performers_pct']:.1f}% del total</div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">Health Score</div>
                <div class="kpi-value">{int(kpis['health']['score'])}</div>
                <div class="kpi-trend">
                    <span class="status-indicator status-{'excellent' if kpis['health']['score'] >= 80 else 'good' if kpis['health']['score'] >= 70 else 'warning' if kpis['health']['score'] >= 60 else 'poor'}"></span>
                    {'Excelente' if kpis['health']['score'] >= 80 else 'Bueno' if kpis['health']['score'] >= 70 else 'Atención' if kpis['health']['score'] >= 60 else 'Crítico'}
                </div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">Diversidad</div>
                <div class="kpi-value">{kpis['distribution']['diversity_score']}</div>
                <div class="kpi-trend">{kpis['portfolio']['unique_formats']} formatos × {kpis['portfolio']['unique_angles']} ángulos</div>
            </div>
            
            <div class="kpi-card">
                <div class="kpi-label">Cobertura Métricas</div>
                <div class="kpi-value">{kpis['health']['coverage_pct']:.0f}%</div>
                <div class="kpi-trend">{kpis['portfolio']['with_metrics']} de {kpis['portfolio']['total_creatives']}</div>
            </div>
        </div>
        
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📊 Distribución por Formato</h3>
                <canvas id="formatChart"></canvas>
            </div>
            
            <div class="chart-card">
                <h3>🎯 Distribución por Ángulo</h3>
                <canvas id="angleChart"></canvas>
            </div>
        </div>
        
        <div class="chart-card">
            <h3>📈 Resumen de Performance</h3>
            <div style="padding: 20px;">
                <p><strong>Total Impresiones:</strong> {kpis['performance']['total_impressions']:,}</p>
                <p><strong>Total Spend:</strong> ${kpis['performance']['total_spend']:,.2f}</p>
                <p><strong>CPC Promedio:</strong> ${kpis['performance']['avg_cpc']:.2f}</p>
                <p><strong>CVR Promedio:</strong> {kpis['performance']['avg_cvr']:.2f}%</p>
            </div>
        </div>
    </div>
    
    <script>
        // Configuración de colores
        const colors = [
            '#667eea', '#764ba2', '#f093fb', '#4facfe',
            '#43e97b', '#fa709a', '#fee140', '#30cfd0',
            '#a8edea', '#fed6e3'
        ];
        
        // Gráfico de Formatos
        const formatCtx = document.getElementById('formatChart').getContext('2d');
        new Chart(formatCtx, {{
            type: 'doughnut',
            data: {{
                labels: {format_labels},
                datasets: [{{
                    data: {format_data},
                    backgroundColor: colors.slice(0, {format_labels.count(',') + 1}),
                    borderWidth: 2,
                    borderColor: '#fff'
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
        
        // Gráfico de Ángulos
        const angleCtx = document.getElementById('angleChart').getContext('2d');
        new Chart(angleCtx, {{
            type: 'bar',
            data: {{
                labels: {angle_labels},
                datasets: [{{
                    label: 'Creativos',
                    data: {angle_data},
                    backgroundColor: colors[0],
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    output_file.write_text(html, encoding='utf-8')
    print(f"📊 Dashboard guardado: {output_file}")

def main():
    print("=" * 80)
    print("📊 Generador de Dashboard KPIs Centralizado")
    print("=" * 80)
    print()
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print("📊 Calculando KPIs...")
    kpis = calculate_kpis(creatives)
    
    print("🎨 Generando dashboard HTML...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = EXPORTS_DIR / f'kpi_dashboard_{timestamp}.html'
    
    generate_html_dashboard(kpis, output_file)
    
    print()
    print("=" * 80)
    print("✅ Dashboard generado exitosamente")
    print("=" * 80)
    print(f"📄 Archivo: {output_file}")
    print(f"🌐 Abre en navegador: file://{output_file.absolute()}")
    print()

if __name__ == '__main__':
    main()


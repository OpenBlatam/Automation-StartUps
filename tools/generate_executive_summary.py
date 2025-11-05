#!/usr/bin/env python3
"""
Genera resumen ejecutivo de performance
Crea reporte de alto nivel para stakeholders y toma de decisiones
"""
import csv
import sys
from pathlib import Path
from datetime import datetime, timedelta
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

def calculate_executive_metrics(creatives):
    """Calcula métricas ejecutivas clave"""
    metrics = {
        'total_creatives': len(creatives),
        'creatives_with_metrics': 0,
        'total_impressions': 0,
        'total_clicks': 0,
        'total_spend': 0,
        'total_conversions': 0,
        'avg_ctr': 0,
        'avg_cpc': 0,
        'avg_cpa': 0,
        'total_revenue': 0,
        'total_roi': 0
    }
    
    creatives_with_data = []
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        if impressions > 0 or spend > 0:
            metrics['creatives_with_metrics'] += 1
            metrics['total_impressions'] += impressions
            metrics['total_clicks'] += clicks
            metrics['total_spend'] += spend
            metrics['total_conversions'] += conversions
            
            # Asumir LTV
            assumed_ltv = 500
            revenue = conversions * assumed_ltv
            metrics['total_revenue'] += revenue
            
            creatives_with_data.append({
                'creative': creative,
                'revenue': revenue,
                'profit': revenue - spend,
                'roi': ((revenue - spend) / spend * 100) if spend > 0 else 0
            })
    
    if metrics['creatives_with_metrics'] > 0:
        metrics['avg_ctr'] = (metrics['total_clicks'] / metrics['total_impressions'] * 100) if metrics['total_impressions'] > 0 else 0
        metrics['avg_cpc'] = (metrics['total_spend'] / metrics['total_clicks']) if metrics['total_clicks'] > 0 else 0
        metrics['avg_cpa'] = (metrics['total_spend'] / metrics['total_conversions']) if metrics['total_conversions'] > 0 else 0
        metrics['total_roi'] = ((metrics['total_revenue'] - metrics['total_spend']) / metrics['total_spend'] * 100) if metrics['total_spend'] > 0 else 0
    
    # Top performers
    top_performers = sorted(creatives_with_data, key=lambda x: x['roi'], reverse=True)[:5]
    metrics['top_performers'] = top_performers
    
    return metrics

def generate_summary_markdown(metrics, date_range="Últimos 30 días"):
    """Genera resumen ejecutivo en Markdown"""
    markdown = []
    
    markdown.append("# 📊 Resumen Ejecutivo de Performance")
    markdown.append("")
    markdown.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    markdown.append(f"**Período:** {date_range}")
    markdown.append("")
    markdown.append("---")
    markdown.append("")
    markdown.append("## 🎯 Métricas Principales")
    markdown.append("")
    markdown.append("| Métrica | Valor |")
    markdown.append("|---------|-------|")
    markdown.append(f"| **Total Creativos** | {metrics['total_creatives']} |")
    markdown.append(f"| **Creativos Activos** | {metrics['creatives_with_metrics']} |")
    markdown.append(f"| **Impresiones Totales** | {metrics['total_impressions']:,.0f} |")
    markdown.append(f"| **Clics Totales** | {metrics['total_clicks']:,.0f} |")
    markdown.append(f"| **CTR Promedio** | {metrics['avg_ctr']:.2f}% |")
    markdown.append(f"| **Gasto Total** | ${metrics['total_spend']:,.2f} |")
    markdown.append(f"| **CPC Promedio** | ${metrics['avg_cpc']:.2f} |")
    markdown.append(f"| **Conversiones** | {metrics['total_conversions']:.0f} |")
    markdown.append(f"| **CPA Promedio** | ${metrics['avg_cpa']:.2f} |")
    markdown.append(f"| **Ingresos Estimados** | ${metrics['total_revenue']:,.2f} |")
    markdown.append(f"| **ROI Total** | {metrics['total_roi']:.2f}% |")
    markdown.append("")
    
    if metrics['top_performers']:
        markdown.append("## 🏆 Top 5 Performers")
        markdown.append("")
        markdown.append("| Creative | ROI | Conversiones | Ingresos |")
        markdown.append("|----------|-----|--------------|----------|")
        for perf in metrics['top_performers']:
            creative_file = perf['creative'].get('creative_file', 'N/A')
            roi = perf['roi']
            conversions = perf['creative'].get('conversions', 0)
            revenue = perf['revenue']
            markdown.append(f"| {creative_file} | {roi:.1f}% | {conversions} | ${revenue:,.2f} |")
        markdown.append("")
    
    # Insights clave
    markdown.append("## 💡 Insights Clave")
    markdown.append("")
    
    if metrics['total_roi'] > 100:
        markdown.append(f"- ✅ **ROI Excelente**: {metrics['total_roi']:.1f}% indica performance fuerte")
    elif metrics['total_roi'] > 50:
        markdown.append(f"- ✅ **ROI Positivo**: {metrics['total_roi']:.1f}% indica retorno positivo")
    elif metrics['total_roi'] > 0:
        markdown.append(f"- ⚠️ **ROI Bajo**: {metrics['total_roi']:.1f}% requiere optimización")
    else:
        markdown.append(f"- ❌ **ROI Negativo**: {metrics['total_roi']:.1f}% requiere acción inmediata")
    
    if metrics['avg_ctr'] > 2.0:
        markdown.append(f"- ✅ **CTR Fuerte**: {metrics['avg_ctr']:.2f}% está por encima del promedio de industria")
    elif metrics['avg_ctr'] > 1.0:
        markdown.append(f"- ✅ **CTR Promedio**: {metrics['avg_ctr']:.2f}% está en línea con benchmarks")
    else:
        markdown.append(f"- ⚠️ **CTR Bajo**: {metrics['avg_ctr']:.2f}% está por debajo del promedio")
    
    if metrics['total_conversions'] > 0:
        conversion_rate = (metrics['total_conversions'] / metrics['total_clicks'] * 100) if metrics['total_clicks'] > 0 else 0
        markdown.append(f"- 📊 **Tasa de Conversión**: {conversion_rate:.2f}% ({metrics['total_conversions']:.0f} conversiones)")
    
    markdown.append("")
    markdown.append("---")
    markdown.append("")
    markdown.append("*Este reporte fue generado automáticamente. Para análisis detallado, consulta los reportes completos.*")
    
    return '\n'.join(markdown)

def main():
    print("=" * 80)
    print("📊 Generador de Resumen Ejecutivo")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Calcular métricas
    metrics = calculate_executive_metrics(creatives)
    
    # Mostrar resumen
    print("=" * 80)
    print("📊 Métricas Ejecutivas")
    print("=" * 80)
    print()
    print(f"Total creativos: {metrics['total_creatives']}")
    print(f"Creativos con métricas: {metrics['creatives_with_metrics']}")
    print()
    print(f"📈 Performance:")
    print(f"  Impresiones: {metrics['total_impressions']:,.0f}")
    print(f"  Clics: {metrics['total_clicks']:,.0f}")
    print(f"  CTR promedio: {metrics['avg_ctr']:.2f}%")
    print()
    print(f"💰 Financiero:")
    print(f"  Gasto total: ${metrics['total_spend']:,.2f}")
    print(f"  Ingresos estimados: ${metrics['total_revenue']:,.2f}")
    print(f"  ROI total: {metrics['total_roi']:.2f}%")
    print(f"  CPA promedio: ${metrics['avg_cpa']:.2f}")
    print()
    
    if metrics['top_performers']:
        print("🏆 Top Performers:")
        for i, perf in enumerate(metrics['top_performers'], 1):
            creative_file = perf['creative'].get('creative_file', 'N/A')
            roi = perf['roi']
            conversions = perf['creative'].get('conversions', 0)
            print(f"  {i}. {creative_file}: ROI {roi:.1f}% ({conversions} conversiones)")
        print()
    
    # Generar markdown
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'executive_summary_{timestamp}.md'
    
    markdown_content = generate_summary_markdown(metrics)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    
    print(f"📄 Resumen ejecutivo guardado: {report_path}")
    print()

if __name__ == '__main__':
    main()


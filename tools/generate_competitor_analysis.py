#!/usr/bin/env python3
"""
Análisis Competitivo y Benchmarking

Analiza el portfolio propio vs. benchmarks de industria y genera
recomendaciones para mejorar posicionamiento competitivo.
"""
import sys
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import Counter
import statistics

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
REPORTS_DIR = Path(__file__).parent.parent / 'reports' / 'competitive'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Benchmarks de industria LinkedIn Ads 2024
INDUSTRY_BENCHMARKS = {
    'linkedin': {
        'ctr': {
            'excellent': 0.8,
            'good': 0.5,
            'average': 0.3,
            'poor': 0.1
        },
        'cvr': {
            'excellent': 15.0,
            'good': 10.0,
            'average': 5.0,
            'poor': 2.0
        },
        'cpc': {
            'excellent': 2.0,
            'good': 3.5,
            'average': 5.0,
            'poor': 8.0
        },
        'formats': {
            'carousel': {'ctr_avg': 0.65, 'usage_pct': 35},
            'single_image': {'ctr_avg': 0.45, 'usage_pct': 40},
            'video': {'ctr_avg': 0.75, 'usage_pct': 15},
            'document': {'ctr_avg': 0.55, 'usage_pct': 10}
        },
        'angles': {
            'benefit': {'ctr_avg': 0.55, 'usage_pct': 30},
            'problem': {'ctr_avg': 0.50, 'usage_pct': 25},
            'social_proof': {'ctr_avg': 0.65, 'usage_pct': 20},
            'education': {'ctr_avg': 0.45, 'usage_pct': 15},
            'urgency': {'ctr_avg': 0.70, 'usage_pct': 10}
        }
    }
}

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def calculate_portfolio_metrics(creatives: List[Dict]) -> Dict:
    """Calcula métricas del portfolio"""
    metrics = {
        'ctr': [],
        'cvr': [],
        'cpc': [],
        'format_distribution': Counter(),
        'angle_distribution': Counter(),
        'performance_by_format': defaultdict(list),
        'performance_by_angle': defaultdict(list)
    }
    
    for c in creatives:
        # CTR
        ctr_val = c.get('ctr', '')
        if ctr_val:
            try:
                metrics['ctr'].append(float(ctr_val.replace('%', '')))
            except:
                pass
        
        # CVR
        cvr_val = c.get('conversion_rate', '')
        if cvr_val:
            try:
                metrics['cvr'].append(float(cvr_val.replace('%', '')))
            except:
                pass
        
        # CPC (derivado de spend e impressions)
        spend = c.get('spend', '')
        impressions = c.get('impressions', '')
        if spend and impressions:
            try:
                cpc = (float(spend) / int(impressions)) * 1000
                metrics['cpc'].append(cpc)
            except:
                pass
        
        # Distribuciones
        format_val = c.get('format', '').lower()
        angle_val = c.get('angle', '').lower()
        
        if format_val:
            metrics['format_distribution'][format_val] += 1
            if ctr_val:
                try:
                    metrics['performance_by_format'][format_val].append(float(ctr_val.replace('%', '')))
                except:
                    pass
        
        if angle_val:
            metrics['angle_distribution'][angle_val] += 1
            if ctr_val:
                try:
                    metrics['performance_by_angle'][angle_val].append(float(ctr_val.replace('%', '')))
                except:
                    pass
    
    # Calcular promedios
    metrics['avg_ctr'] = statistics.mean(metrics['ctr']) if metrics['ctr'] else 0
    metrics['avg_cvr'] = statistics.mean(metrics['cvr']) if metrics['cvr'] else 0
    metrics['avg_cpc'] = statistics.mean(metrics['cpc']) if metrics['cpc'] else 0
    
    # Calcular promedios por formato y ángulo
    metrics['avg_by_format'] = {
        fmt: statistics.mean(ctrs) if ctrs else 0
        for fmt, ctrs in metrics['performance_by_format'].items()
    }
    
    metrics['avg_by_angle'] = {
        angle: statistics.mean(ctrs) if ctrs else 0
        for angle, ctrs in metrics['performance_by_angle'].items()
    }
    
    return metrics

def compare_with_benchmarks(metrics: Dict) -> Dict:
    """Compara métricas propias con benchmarks de industria"""
    comparison = {
        'overall': {},
        'by_format': {},
        'by_angle': {},
        'gaps': [],
        'strengths': [],
        'opportunities': []
    }
    
    benchmarks = INDUSTRY_BENCHMARKS['linkedin']
    
    # Comparación general
    ctr = metrics['avg_ctr']
    if ctr >= benchmarks['ctr']['excellent']:
        comparison['overall']['ctr'] = {'status': 'excellent', 'vs_benchmark': '+excellent'}
        comparison['strengths'].append('CTR excelente vs. industria')
    elif ctr >= benchmarks['ctr']['good']:
        comparison['overall']['ctr'] = {'status': 'good', 'vs_benchmark': '+good'}
        comparison['strengths'].append('CTR bueno vs. industria')
    elif ctr < benchmarks['ctr']['poor']:
        comparison['overall']['ctr'] = {'status': 'poor', 'vs_benchmark': '-poor'}
        comparison['gaps'].append({
            'metric': 'CTR',
            'current': f"{ctr:.2f}%",
            'benchmark_avg': f"{benchmarks['ctr']['average']:.2f}%",
            'gap': f"{(benchmarks['ctr']['average'] - ctr):.2f}%",
            'recommendation': 'Optimizar creativos y targeting'
        })
    else:
        comparison['overall']['ctr'] = {'status': 'average', 'vs_benchmark': '≈average'}
    
    # Comparación por formato
    for format_name, benchmark_data in benchmarks['formats'].items():
        if format_name in metrics['avg_by_format']:
            own_avg = metrics['avg_by_format'][format_name]
            benchmark_avg = benchmark_data['ctr_avg']
            
            diff = own_avg - benchmark_avg
            diff_pct = (diff / benchmark_avg) * 100 if benchmark_avg > 0 else 0
            
            comparison['by_format'][format_name] = {
                'own_avg': own_avg,
                'benchmark_avg': benchmark_avg,
                'difference': diff,
                'difference_pct': diff_pct,
                'status': 'above' if diff > 0.1 else 'below' if diff < -0.1 else 'on_par'
            }
            
            if diff < -0.15:
                comparison['opportunities'].append({
                    'type': 'format',
                    'format': format_name,
                    'issue': f"CTR {diff:.2f}% por debajo del benchmark",
                    'recommendation': f'Optimizar creativos de formato {format_name}'
                })
    
    # Comparación por ángulo
    for angle_name, benchmark_data in benchmarks['angles'].items():
        if angle_name in metrics['avg_by_angle']:
            own_avg = metrics['avg_by_angle'][angle_name]
            benchmark_avg = benchmark_data['ctr_avg']
            
            diff = own_avg - benchmark_avg
            
            comparison['by_angle'][angle_name] = {
                'own_avg': own_avg,
                'benchmark_avg': benchmark_avg,
                'difference': diff,
                'status': 'above' if diff > 0.1 else 'below' if diff < -0.1 else 'on_par'
            }
    
    # Análisis de diversidad
    total_creatives = sum(metrics['format_distribution'].values())
    if total_creatives > 0:
        format_diversity = {}
        for format_name, benchmark_pct in {k: v['usage_pct'] for k, v in benchmarks['formats'].items()}.items():
            own_count = metrics['format_distribution'].get(format_name, 0)
            own_pct = (own_count / total_creatives) * 100
            benchmark_pct = benchmark_pct
            
            format_diversity[format_name] = {
                'own_pct': own_pct,
                'benchmark_pct': benchmark_pct,
                'difference': own_pct - benchmark_pct
            }
            
            if own_pct < benchmark_pct - 10:
                comparison['opportunities'].append({
                    'type': 'diversification',
                    'format': format_name,
                    'issue': f"Subutilizado ({own_pct:.1f}% vs. {benchmark_pct}% benchmark)",
                    'recommendation': f'Aumentar uso de formato {format_name}'
                })
        
        comparison['format_diversity'] = format_diversity
    
    return comparison

def generate_competitive_report(metrics: Dict, comparison: Dict, output_file: Path):
    """Genera reporte competitivo"""
    report = f"""# 🏆 Análisis Competitivo y Benchmarking

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Métricas del Portfolio

### Performance General

- **CTR promedio:** {metrics['avg_ctr']:.2f}%
- **CVR promedio:** {metrics['avg_cvr']:.2f}% (si disponible)
- **CPC promedio:** ${metrics['avg_cpc']:.2f} (si disponible)

### Comparación con Benchmarks de Industria

#### CTR

"""
    
    ctr_status = comparison['overall'].get('ctr', {})
    status_emoji = '🔥' if ctr_status.get('status') == 'excellent' else '✅' if ctr_status.get('status') == 'good' else '⚠️' if ctr_status.get('status') == 'average' else '❌'
    
    report += f"{status_emoji} **{ctr_status.get('status', 'unknown').upper()}**: {metrics['avg_ctr']:.2f}%\n"
    report += f"   - Benchmark promedio industria: {INDUSTRY_BENCHMARKS['linkedin']['ctr']['average']:.2f}%\n"
    report += f"   - Benchmark excelente: {INDUSTRY_BENCHMARKS['linkedin']['ctr']['excellent']:.2f}%\n\n"
    
    report += "\n### Comparación por Formato\n\n"
    report += "| Formato | Tu Promedio | Benchmark | Diferencia | Status |\n"
    report += "|---------|-------------|-----------|------------|--------|\n"
    
    for format_name, data in comparison.get('by_format', {}).items():
        status_emoji = '✅' if data['status'] == 'above' else '⚠️' if data['status'] == 'on_par' else '❌'
        report += f"| {format_name} | {data['own_avg']:.2f}% | {data['benchmark_avg']:.2f}% | {data['difference']:+.2f}% | {status_emoji} |\n"
    
    report += "\n### Comparación por Ángulo\n\n"
    for angle_name, data in comparison.get('by_angle', {}).items():
        status_emoji = '✅' if data['status'] == 'above' else '⚠️' if data['status'] == 'on_par' else '❌'
        report += f"- **{angle_name}**: {data['own_avg']:.2f}% (benchmark: {data['benchmark_avg']:.2f}%) {status_emoji}\n"
    
    report += "\n## 🎯 Fortalezas Identificadas\n\n"
    if comparison['strengths']:
        for strength in comparison['strengths']:
            report += f"- ✅ {strength}\n"
    else:
        report += "*Revisar métricas para identificar fortalezas*\n"
    
    report += "\n## ⚠️ Gaps vs. Industria\n\n"
    if comparison['gaps']:
        for gap in comparison['gaps']:
            report += f"- **{gap['metric']}**:\n"
            report += f"  - Actual: {gap['current']}\n"
            report += f"  - Benchmark: {gap['benchmark_avg']}\n")
            report += f"  - Gap: {gap['gap']}\n"
            report += f"  - 💡 {gap['recommendation']}\n\n"
    else:
        report += "*No se identificaron gaps significativos*\n\n"
    
    report += "\n## 💡 Oportunidades de Mejora\n\n"
    if comparison['opportunities']:
        for opp in comparison['opportunities']:
            report += f"- **{opp['type'].title()}**: {opp.get('format', 'N/A')}\n")
            report += f"  - Problema: {opp['issue']}\n"
            report += f"  - Recomendación: {opp['recommendation']}\n\n"
    else:
        report += "*Portfolio está alineado con benchmarks de industria*\n\n"
    
    report += "\n## 🚀 Plan de Acción Competitivo\n\n"
    
    # Priorizar acciones
    high_priority = [g for g in comparison['gaps'] if abs(float(g['gap'].replace('%', ''))) > 0.2]
    if high_priority:
        report += "### Acciones Prioritarias (Alta)\n\n"
        for i, gap in enumerate(high_priority[:3], 1):
            report += f"{i}. **Mejorar {gap['metric']}**\n")
            report += f"   - {gap['recommendation']}\n\n"
    
    if comparison['opportunities']:
        report += "### Oportunidades de Diversificación\n\n"
        for opp in comparison['opportunities'][:3]:
            report += f"- {opp['recommendation']}\n")
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def main():
    print("=" * 80)
    print("🏆 Análisis Competitivo y Benchmarking")
    print("=" * 80)
    print()
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print("📊 Calculando métricas del portfolio...")
    metrics = calculate_portfolio_metrics(creatives)
    
    print("🏆 Comparando con benchmarks de industria...")
    comparison = compare_with_benchmarks(metrics)
    
    # Generar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = REPORTS_DIR / f'competitive_analysis_{timestamp}.md'
    
    generate_competitive_report(metrics, comparison, output_file)
    
    # Resumen en consola
    print()
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  📈 CTR promedio: {metrics['avg_ctr']:.2f}%")
    print(f"  🏆 Status vs. benchmark: {comparison['overall'].get('ctr', {}).get('status', 'unknown')}")
    print(f"  ✅ Fortalezas: {len(comparison['strengths'])}")
    print(f"  ⚠️  Gaps: {len(comparison['gaps'])}")
    print(f"  💡 Oportunidades: {len(comparison['opportunities'])}")
    print()

if __name__ == '__main__':
    main()


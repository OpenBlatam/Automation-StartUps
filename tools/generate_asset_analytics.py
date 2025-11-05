#!/usr/bin/env python3
"""
Generador de Analytics Avanzados de Assets

Analiza patrones de uso, tendencias y genera insights accionables basados en
datos históricos y actuales del portfolio de creativos.
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, Counter
import statistics

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
REPORTS_DIR = Path(__file__).parent.parent / 'reports' / 'analytics'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze_usage_patterns(creatives: List[Dict]) -> Dict:
    """Analiza patrones de uso y tendencias"""
    patterns = {
        'format_distribution': Counter(),
        'angle_distribution': Counter(),
        'cta_distribution': Counter(),
        'product_distribution': Counter(),
        'platform_distribution': Counter(),
        'performance_by_category': defaultdict(list),
        'trends': {
            'popular_formats': [],
            'emerging_formats': [],
            'declining_formats': []
        }
    }
    
    # Distribuciones
    for c in creatives:
        if c.get('format'):
            patterns['format_distribution'][c['format'].lower()] += 1
        if c.get('angle'):
            patterns['angle_distribution'][c['angle'].lower()] += 1
        if c.get('cta'):
            patterns['cta_distribution'][c['cta'].lower()] += 1
        if c.get('product'):
            patterns['product_distribution'][c['product'].lower()] += 1
        if c.get('utm_source'):
            patterns['platform_distribution'][c['utm_source'].lower()] += 1
        
        # Performance por categoría
        ctr_val = c.get('ctr', '')
        if ctr_val:
            try:
                ctr = float(ctr_val.replace('%', ''))
                format_val = c.get('format', '').lower()
                if format_val:
                    patterns['performance_by_category'][f'format_{format_val}'].append(ctr)
            except:
                pass
    
    # Identificar tendencias
    total = len(creatives)
    for format_name, count in patterns['format_distribution'].most_common():
        percentage = (count / total) * 100
        if percentage > 30:
            patterns['trends']['popular_formats'].append({
                'format': format_name,
                'count': count,
                'percentage': f"{percentage:.1f}%"
            })
        elif percentage < 5:
            patterns['trends']['emerging_formats'].append({
                'format': format_name,
                'count': count,
                'percentage': f"{percentage:.1f}%"
            })
    
    # Calcular promedios de performance
    performance_avg = {}
    for category, ctrs in patterns['performance_by_category'].items():
        if ctrs:
            performance_avg[category] = {
                'avg': statistics.mean(ctrs),
                'median': statistics.median(ctrs),
                'max': max(ctrs),
                'min': min(ctrs),
                'count': len(ctrs)
            }
    
    patterns['performance_averages'] = performance_avg
    
    return patterns

def analyze_content_strategy(creatives: List[Dict]) -> Dict:
    """Analiza estrategia de contenido y recomendaciones"""
    strategy = {
        'content_mix': {},
        'messaging_themes': [],
        'recommendations': [],
        'gaps': []
    }
    
    # Analizar mix de contenido
    format_counts = Counter(c.get('format', '').lower() for c in creatives if c.get('format'))
    angle_counts = Counter(c.get('angle', '').lower() for c in creatives if c.get('angle'))
    
    strategy['content_mix'] = {
        'formats': dict(format_counts),
        'angles': dict(angle_counts),
        'diversity_score': len(format_counts) * len(angle_counts)
    }
    
    # Identificar temas de mensajería
    angle_performance = defaultdict(list)
    for c in creatives:
        angle = c.get('angle', '').lower()
        ctr_val = c.get('ctr', '')
        if angle and ctr_val:
            try:
                ctr = float(ctr_val.replace('%', ''))
                angle_performance[angle].append(ctr)
            except:
                pass
    
    for angle, ctrs in angle_performance.items():
        if ctrs:
            avg_ctr = statistics.mean(ctrs)
            strategy['messaging_themes'].append({
                'angle': angle,
                'avg_ctr': f"{avg_ctr:.2f}%",
                'count': len(ctrs),
                'effectiveness': 'high' if avg_ctr > 0.8 else 'medium' if avg_ctr > 0.4 else 'low'
            })
    
    # Recomendaciones
    strategy['recommendations'] = []
    
    # Diversificar si hay demasiada concentración
    if len(format_counts) < 3:
        strategy['recommendations'].append({
            'priority': 'high',
            'action': 'Diversificar formatos',
            'reason': f'Solo {len(format_counts)} formato(s) en uso',
            'suggestion': 'Probar nuevos formatos para ampliar alcance'
        })
    
    # Identificar ángulos con bajo uso pero alto performance
    for theme in strategy['messaging_themes']:
        if theme['effectiveness'] == 'high' and theme['count'] < 5:
            strategy['recommendations'].append({
                'priority': 'medium',
                'action': f"Escalar ángulo '{theme['angle']}'",
                'reason': f"Alto CTR ({theme['avg_ctr']}) pero solo {theme['count']} variantes",
                'suggestion': 'Crear más variantes de este ángulo exitoso'
            })
    
    return strategy

def analyze_optimization_opportunities(creatives: List[Dict]) -> Dict:
    """Identifica oportunidades de optimización"""
    opportunities = {
        'underperforming': [],
        'scale_candidates': [],
        'optimization_tips': []
    }
    
    for c in creatives:
        utm_content = c.get('utm_content', '')
        ctr_val = c.get('ctr', '')
        impressions = c.get('impressions', '')
        spend = c.get('spend', '')
        
        try:
            ctr = float(ctr_val.replace('%', '')) if ctr_val else None
            imp = int(impressions) if impressions else None
            spent = float(spend) if spend else None
            
            if ctr is not None:
                # Creativos con bajo performance
                if ctr < 0.3:
                    opportunities['underperforming'].append({
                        'creative': utm_content,
                        'ctr': f"{ctr:.2f}%",
                        'format': c.get('format', ''),
                        'angle': c.get('angle', ''),
                        'recommendation': 'Revisar mensaje o CTA, considerar variantes'
                    })
                
                # Candidatos para escalar (alto CTR, bajo alcance)
                if ctr > 0.8 and imp is not None and imp < 10000:
                    opportunities['scale_candidates'].append({
                        'creative': utm_content,
                        'ctr': f"{ctr:.2f}%",
                        'impressions': imp,
                        'recommendation': 'Aumentar budget para mayor alcance',
                        'potential_reach': f"{imp * 5:,}"  # Estimación conservadora
                    })
                
                # Optimización de costos
                if ctr > 0.5 and spent is not None and imp is not None and imp > 0:
                    cpc = spent / imp * 1000  # Costo por mil impresiones
                    if cpc > 10:
                        opportunities['optimization_tips'].append({
                            'creative': utm_content,
                            'cpc': f"${cpc:.2f}",
                            'tip': 'Considerar optimizar targeting o creativo para reducir CPC'
                        })
        except:
            pass
    
    # Ordenar por prioridad
    opportunities['underperforming'] = sorted(
        opportunities['underperforming'],
        key=lambda x: float(x['ctr'].replace('%', ''))
    )[:10]
    
    opportunities['scale_candidates'] = sorted(
        opportunities['scale_candidates'],
        key=lambda x: float(x['ctr'].replace('%', '')),
        reverse=True
    )[:10]
    
    return opportunities

def generate_analytics_report(patterns: Dict, strategy: Dict, opportunities: Dict, output_file: Path):
    """Genera reporte de analytics"""
    report = f"""# 📊 Analytics Avanzados de Assets

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Patrones de Uso

### Distribución de Formatos

"""
    
    for format_name, count in patterns['format_distribution'].most_common(10):
        report += f"- **{format_name}**: {count} creativos\n"
    
    report += "\n### Distribución de Ángulos\n\n"
    for angle_name, count in patterns['angle_distribution'].most_common(10):
        report += f"- **{angle_name}**: {count} creativos\n"
    
    report += "\n### Performance por Formato\n\n"
    for category, perf in sorted(patterns['performance_averages'].items(), 
                                  key=lambda x: x[1]['avg'], reverse=True)[:5]:
        format_name = category.replace('format_', '')
        report += f"- **{format_name}**:\n"
        report += f"  - CTR promedio: {perf['avg']:.2f}%\n"
        report += f"  - CTR máximo: {perf['max']:.2f}%\n"
        report += f"  - Creativos analizados: {perf['count']}\n\n"
    
    report += "\n## 🎯 Estrategia de Contenido\n\n"
    
    report += "### Temas de Mensajería\n\n"
    for theme in sorted(strategy['messaging_themes'], 
                       key=lambda x: float(x['avg_ctr'].replace('%', '')), 
                       reverse=True)[:5]:
        effectiveness_emoji = '🔥' if theme['effectiveness'] == 'high' else '✅' if theme['effectiveness'] == 'medium' else '⚠️'
        report += f"- {effectiveness_emoji} **{theme['angle']}**: {theme['avg_ctr']} (avg) - {theme['count']} variantes\n"
    
    report += "\n### Recomendaciones Estratégicas\n\n"
    for rec in strategy['recommendations']:
        priority_emoji = '🔴' if rec['priority'] == 'high' else '🟡' if rec['priority'] == 'medium' else '🟢'
        report += f"{priority_emoji} **{rec['action']}**\n"
        report += f"   - Razón: {rec['reason']}\n"
        report += f"   - Sugerencia: {rec['suggestion']}\n\n"
    
    report += "\n## 💡 Oportunidades de Optimización\n\n"
    
    report += "### Creativos Bajo Performance (<0.3% CTR)\n\n"
    if opportunities['underperforming']:
        for item in opportunities['underperforming'][:5]:
            report += f"- **{item['creative']}**: {item['ctr']}\n"
            report += f"  - {item['format']} + {item['angle']}\n"
            report += f"  - 💡 {item['recommendation']}\n\n"
    else:
        report += "*No hay creativos con bajo performance*\n\n"
    
    report += "### Candidatos para Escalar\n\n"
    if opportunities['scale_candidates']:
        for item in opportunities['scale_candidates'][:5]:
            report += f"- **{item['creative']}**: {item['ctr']} CTR, {item['impressions']:,} impresiones\n"
            report += f"  - 💡 {item['recommendation']}\n"
            report += f"  - Potencial alcance: {item['potential_reach']} impresiones\n\n"
    else:
        report += "*No hay candidatos identificados*\n\n"
    
    report += "\n## 📊 Resumen Ejecutivo\n\n"
    
    total_creatives = sum(patterns['format_distribution'].values())
    diversity_score = strategy['content_mix']['diversity_score']
    
    report += f"- **Total creativos analizados:** {total_creatives}\n"
    report += f"- **Diversidad de contenido:** {diversity_score} (más alto = más diverso)\n"
    report += f"- **Formatos únicos:** {len(patterns['format_distribution'])}\n"
    report += f"- **Ángulos únicos:** {len(patterns['angle_distribution'])}\n"
    report += f"- **Creativos bajo performance:** {len(opportunities['underperforming'])}\n"
    report += f"- **Candidatos para escalar:** {len(opportunities['scale_candidates'])}\n"
    
    report += "\n## 🚀 Acciones Recomendadas\n\n"
    
    report += "1. **Priorizar escalamiento** de creativos con alto CTR y bajo alcance\n"
    report += "2. **Optimizar o pausar** creativos con bajo performance\n"
    report += "3. **Diversificar** mix de formatos si hay poca variación\n"
    report += "4. **Escalar ángulos exitosos** creando más variantes\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def main():
    print("=" * 80)
    print("📊 Generador de Analytics Avanzados de Assets")
    print("=" * 80)
    print()
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print("🔍 Analizando patrones de uso...")
    patterns = analyze_usage_patterns(creatives)
    
    print("🎯 Analizando estrategia de contenido...")
    strategy = analyze_content_strategy(creatives)
    
    print("💡 Identificando oportunidades de optimización...")
    opportunities = analyze_optimization_opportunities(creatives)
    
    # Generar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = REPORTS_DIR / f'asset_analytics_{timestamp}.md'
    
    generate_analytics_report(patterns, strategy, opportunities, output_file)
    
    # Resumen en consola
    print()
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  📈 Formatos únicos: {len(patterns['format_distribution'])}")
    print(f"  🎯 Ángulos únicos: {len(patterns['angle_distribution'])}")
    print(f"  🔥 Temas efectivos: {len([t for t in strategy['messaging_themes'] if t['effectiveness'] == 'high'])}")
    print(f"  ⚠️  Creativos bajo performance: {len(opportunities['underperforming'])}")
    print(f"  ⬆️  Candidatos para escalar: {len(opportunities['scale_candidates'])}")
    print()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Insights Predictivos y Recomendaciones Inteligentes

Combina análisis histórico, tendencias y machine learning para generar
insights predictivos y recomendaciones accionables para el futuro.
"""
import sys
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict
import statistics

CSV_MASTER = Path(__file__).parent.parent / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
REPORTS_DIR = Path(__file__).parent.parent / 'reports' / 'predictive'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_csv() -> List[Dict]:
    """Carga el CSV Master"""
    if not CSV_MASTER.exists():
        print(f"❌ CSV Master no encontrado: {CSV_MASTER}")
        return []
    
    with open(CSV_MASTER, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def predict_performance_trends(creatives: List[Dict]) -> Dict:
    """Predice tendencias de performance basado en datos históricos"""
    predictions = {
        'format_trends': {},
        'angle_trends': {},
        'seasonal_patterns': {},
        'growth_projections': {}
    }
    
    # Analizar performance por formato
    format_performance = defaultdict(list)
    for c in creatives:
        format_val = c.get('format', '').lower()
        ctr_val = c.get('ctr', '')
        
        if format_val and ctr_val:
            try:
                ctr = float(ctr_val.replace('%', ''))
                format_performance[format_val].append(ctr)
            except:
                pass
    
    for format_name, ctrs in format_performance.items():
        if len(ctrs) >= 3:
            avg_ctr = statistics.mean(ctrs)
            trend = 'increasing' if avg_ctr > statistics.median(ctrs) else 'stable' if avg_ctr > 0.5 else 'decreasing'
            
            predictions['format_trends'][format_name] = {
                'current_avg': avg_ctr,
                'trend': trend,
                'projected_next_month': avg_ctr * (1.05 if trend == 'increasing' else 0.95 if trend == 'decreasing' else 1.0),
                'confidence': 'high' if len(ctrs) > 10 else 'medium'
            }
    
    # Análisis similar para ángulos
    angle_performance = defaultdict(list)
    for c in creatives:
        angle_val = c.get('angle', '').lower()
        ctr_val = c.get('ctr', '')
        
        if angle_val and ctr_val:
            try:
                ctr = float(ctr_val.replace('%', ''))
                angle_performance[angle_val].append(ctr)
            except:
                pass
    
    for angle_name, ctrs in angle_performance.items():
        if len(ctrs) >= 3:
            avg_ctr = statistics.mean(ctrs)
            trend = 'increasing' if avg_ctr > statistics.median(ctrs) else 'stable'
            
            predictions['angle_trends'][angle_name] = {
                'current_avg': avg_ctr,
                'trend': trend,
                'projected_next_month': avg_ctr * (1.03 if trend == 'increasing' else 1.0)
            }
    
    # Proyecciones de crecimiento
    total_creatives = len(creatives)
    high_performers = sum(1 for c in creatives 
                         if c.get('ctr') and float(c.get('ctr', '0').replace('%', '')) > 0.7)
    
    predictions['growth_projections'] = {
        'current_portfolio_size': total_creatives,
        'high_performers_ratio': (high_performers / total_creatives * 100) if total_creatives > 0 else 0,
        'recommended_portfolio_size': int(total_creatives * 1.2),
        'optimal_high_performers_target': int(total_creatives * 0.4)
    }
    
    return predictions

def generate_strategic_recommendations(creatives: List[Dict], predictions: Dict) -> List[Dict]:
    """Genera recomendaciones estratégicas basadas en predicciones"""
    recommendations = []
    
    # Recomendaciones basadas en tendencias de formato
    for format_name, data in predictions['format_trends'].items():
        if data['trend'] == 'increasing':
            recommendations.append({
                'priority': 'high',
                'category': 'format',
                'action': f"Aumentar uso de formato '{format_name}'",
                'reason': f"Tendencia creciente (CTR promedio: {data['current_avg']:.2f}%)",
                'expected_impact': f"Proyección: {data['projected_next_month']:.2f}% CTR el próximo mes",
                'confidence': data['confidence']
            })
    
    # Recomendaciones de portfolio
    growth = predictions['growth_projections']
    if growth['high_performers_ratio'] < 30:
        recommendations.append({
            'priority': 'high',
            'category': 'portfolio',
            'action': 'Aumentar proporción de high performers',
            'reason': f"Actualmente solo {growth['high_performers_ratio']:.1f}% son high performers",
            'expected_impact': 'Objetivo: 40% de high performers para optimizar ROI',
            'confidence': 'high'
        })
    
    # Recomendaciones de diversificación
    unique_formats = len(set(c.get('format', '').lower() for c in creatives if c.get('format')))
    if unique_formats < 3:
        recommendations.append({
            'priority': 'medium',
            'category': 'diversification',
            'action': 'Diversificar mix de formatos',
            'reason': f"Solo {unique_formats} formato(s) en uso",
            'expected_impact': 'Mayor diversidad puede mejorar alcance y reducir riesgo',
            'confidence': 'medium'
        })
    
    return recommendations

def identify_opportunity_windows(creatives: List[Dict]) -> Dict:
    """Identifica ventanas de oportunidad y timing óptimo"""
    opportunities = {
        'underutilized_high_performers': [],
        'scale_opportunities': [],
        'testing_opportunities': []
    }
    
    # Creativos con alto CTR pero bajo uso
    for c in creatives:
        ctr_val = c.get('ctr', '')
        impressions = c.get('impressions', '')
        
        try:
            ctr = float(ctr_val.replace('%', '')) if ctr_val else None
            imp = int(impressions) if impressions else None
            
            if ctr and ctr > 0.8:
                if imp and imp < 5000:
                    opportunities['underutilized_high_performers'].append({
                        'creative': c.get('utm_content', ''),
                        'ctr': f"{ctr:.2f}%",
                        'impressions': imp,
                        'opportunity': 'Escalar inmediatamente',
                        'potential': 'Alto - CTR excelente con alcance limitado'
                    })
        except:
            pass
    
    # Oportunidades de testing
    format_counts = defaultdict(int)
    for c in creatives:
        format_val = c.get('format', '').lower()
        if format_val:
            format_counts[format_val] += 1
    
    for format_name, count in format_counts.items():
        if count < 3:
            opportunities['testing_opportunities'].append({
                'format': format_name,
                'current_count': count,
                'opportunity': 'Expandir testing de este formato',
                'reason': 'Pocas variantes limitan aprendizaje'
            })
    
    return opportunities

def generate_predictive_report(predictions: Dict, recommendations: List[Dict], 
                              opportunities: Dict, output_file: Path):
    """Genera reporte predictivo"""
    report = f"""# 🔮 Insights Predictivos y Recomendaciones

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📈 Predicciones y Tendencias

### Tendencias de Formatos

"""
    
    for format_name, data in sorted(predictions['format_trends'].items(), 
                                   key=lambda x: x[1]['current_avg'], reverse=True)[:5]:
        trend_emoji = '📈' if data['trend'] == 'increasing' else '➡️' if data['trend'] == 'stable' else '📉'
        report += f"{trend_emoji} **{format_name}**:\n"
        report += f"  - CTR actual: {data['current_avg']:.2f}%\n"
        report += f"  - Tendencia: {data['trend']}\n"
        report += f"  - Proyección próximo mes: {data['projected_next_month']:.2f}%\n"
        report += f"  - Confianza: {data['confidence']}\n\n"
    
    report += "\n### Tendencias de Ángulos\n\n"
    for angle_name, data in sorted(predictions['angle_trends'].items(), 
                                  key=lambda x: x[1]['current_avg'], reverse=True)[:5]:
        trend_emoji = '📈' if data['trend'] == 'increasing' else '➡️'
        report += f"{trend_emoji} **{angle_name}**: {data['current_avg']:.2f}% (proy: {data['projected_next_month']:.2f}%)\n"
    
    report += "\n### Proyecciones de Crecimiento\n\n"
    growth = predictions['growth_projections']
    report += f"- Portfolio actual: {growth['current_portfolio_size']} creativos\n"
    report += f"- High performers: {growth['high_performers_ratio']:.1f}%\n"
    report += f"- Portfolio recomendado: {growth['recommended_portfolio_size']} creativos\n"
    report += f"- Objetivo high performers: {growth['optimal_high_performers_target']} ({growth['optimal_high_performers_target']/growth['recommended_portfolio_size']*100:.0f}%)\n"
    
    report += "\n## 🎯 Recomendaciones Estratégicas\n\n"
    
    for rec in sorted(recommendations, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x['priority'], 0), reverse=True):
        priority_emoji = '🔴' if rec['priority'] == 'high' else '🟡' if rec['priority'] == 'medium' else '🟢'
        confidence_emoji = '✅' if rec['confidence'] == 'high' else '⚠️'
        
        report += f"{priority_emoji} **{rec['action']}** {confidence_emoji}\n"
        report += f"   - Categoría: {rec['category']}\n"
        report += f"   - Razón: {rec['reason']}\n"
        report += f"   - Impacto esperado: {rec['expected_impact']}\n\n"
    
    report += "\n## 💡 Ventanas de Oportunidad\n\n"
    
    report += "### Creativos Bajo Utilizados con Alto Performance\n\n"
    if opportunities['underutilized_high_performers']:
        for opp in opportunities['underutilized_high_performers'][:5]:
            report += f"- **{opp['creative']}**: {opp['ctr']} CTR, {opp['impressions']:,} impresiones\n"
            report += f"  - {opp['opportunity']}\n"
            report += f"  - Potencial: {opp['potential']}\n\n"
    else:
        report += "*Todos los high performers están siendo utilizados adecuadamente*\n\n"
    
    report += "### Oportunidades de Testing\n\n"
    if opportunities['testing_opportunities']:
        for opp in opportunities['testing_opportunities']:
            report += f"- **{opp['format']}**: Solo {opp['current_count']} variante(s)\n"
            report += f"  - {opp['opportunity']}\n"
            report += f"  - Razón: {opp['reason']}\n\n"
    else:
        report += "*Buena cobertura de testing en todos los formatos*\n\n"
    
    report += "\n## 🚀 Plan de Acción Recomendado (Próximos 30 días)\n\n"
    
    high_priority = [r for r in recommendations if r['priority'] == 'high']
    if high_priority:
        report += "### Acciones Prioritarias\n\n"
        for i, rec in enumerate(high_priority[:5], 1):
            report += f"{i}. {rec['action']}\n")
            report += f"   - Razón: {rec['reason']}\n\n"
    
    report += "\n### Métricas de Éxito\n\n"
    report += "- Portfolio size: Objetivo +20%\n"
    report += "- High performers ratio: Objetivo 40%\n"
    report += "- Formatos únicos: Objetivo mínimo 4\n"
    report += "- CTR promedio: Mantener o mejorar\n"
    
    output_file.write_text(report, encoding='utf-8')
    print(f"📄 Reporte guardado: {output_file}")

def main():
    print("=" * 80)
    print("🔮 Insights Predictivos y Recomendaciones Inteligentes")
    print("=" * 80)
    print()
    
    creatives = load_csv()
    
    if not creatives:
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    print("🔮 Analizando tendencias y generando predicciones...")
    predictions = predict_performance_trends(creatives)
    
    print("🎯 Generando recomendaciones estratégicas...")
    recommendations = generate_strategic_recommendations(creatives, predictions)
    
    print("💡 Identificando ventanas de oportunidad...")
    opportunities = identify_opportunity_windows(creatives)
    
    # Generar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = REPORTS_DIR / f'predictive_insights_{timestamp}.md'
    
    generate_predictive_report(predictions, recommendations, opportunities, output_file)
    
    # Resumen en consola
    print()
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  📈 Formatos con tendencia: {len(predictions['format_trends'])}")
    print(f"  🎯 Recomendaciones: {len(recommendations)}")
    print(f"  💡 Oportunidades de escalamiento: {len(opportunities['underutilized_high_performers'])}")
    print(f"  🧪 Oportunidades de testing: {len(opportunities['testing_opportunities'])}")
    print()

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Sistema de Recomendaciones Inteligentes
Genera recomendaciones contextuales basadas en múltiples factores
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

def analyze_context(creatives):
    """Analiza contexto actual para recomendaciones"""
    context = {
        'total_creatives': len(creatives),
        'creatives_with_metrics': 0,
        'total_spend': 0,
        'total_conversions': 0,
        'avg_ctr': 0,
        'roi_positive': 0,
        'roi_negative': 0,
        'by_format': defaultdict(int),
        'by_angle': defaultdict(int),
        'recent_activity': False
    }
    
    for creative in creatives:
        formato = creative.get('formato', 'unknown')
        angulo = creative.get('angulo', 'unknown')
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        impressions = float(creative.get('impressions', 0) or 0)
        
        context['by_format'][formato] += 1
        context['by_angle'][angulo] += 1
        
        if impressions > 0:
            context['creatives_with_metrics'] += 1
            context['total_spend'] += spend
            context['total_conversions'] += conversions
            
            clicks = float(creative.get('clicks', 0) or 0)
            if impressions > 0:
                ctr = (clicks / impressions * 100)
                context['avg_ctr'] += ctr
            
            if spend > 0:
                assumed_ltv = 500
                revenue = conversions * assumed_ltv
                roi = ((revenue - spend) / spend * 100)
                if roi > 0:
                    context['roi_positive'] += 1
                else:
                    context['roi_negative'] += 1
    
    if context['creatives_with_metrics'] > 0:
        context['avg_ctr'] /= context['creatives_with_metrics']
    
    return context

def generate_contextual_recommendations(context, creatives):
    """Genera recomendaciones basadas en contexto"""
    recommendations = []
    
    # Recomendación: Portfolio pequeño
    if context['total_creatives'] < 20:
        recommendations.append({
            'priority': 'high',
            'category': 'portfolio_size',
            'title': 'Portfolio pequeño',
            'message': f"Solo {context['total_creatives']} creativos. Portfolio ideal: 30-50+",
            'action': 'Crear más creativos para testing y rotación',
            'impact': 'Aumentar capacidad de testing y escalado',
            'timeline': '2-4 semanas'
        })
    
    # Recomendación: Falta de métricas
    if context['creatives_with_metrics'] < context['total_creatives'] * 0.7:
        missing_pct = ((context['total_creatives'] - context['creatives_with_metrics']) / context['total_creatives']) * 100
        recommendations.append({
            'priority': 'high',
            'category': 'data_quality',
            'title': 'Falta de datos de performance',
            'message': f"{missing_pct:.0f}% de creativos sin métricas",
            'action': 'Ejecutar: python3 tools/analyze_real_time_performance.py',
            'impact': 'Habilitar análisis de ROI y optimización',
            'timeline': 'Inmediato'
        })
    
    # Recomendación: ROI negativo
    if context['roi_negative'] > context['roi_positive']:
        recommendations.append({
            'priority': 'critical',
            'category': 'performance',
            'title': 'Mayoría de creativos con ROI negativo',
            'message': f"{context['roi_negative']} creativos con ROI negativo vs. {context['roi_positive']} positivos",
            'action': 'Revisar y pausar poor performers. Ejecutar: python3 tools/calculate_roi_and_optimize.py',
            'impact': 'Reducir desperdicio de budget',
            'timeline': 'Inmediato'
        })
    
    # Recomendación: CTR bajo
    if context['avg_ctr'] < 1.5:
        recommendations.append({
            'priority': 'high',
            'category': 'performance',
            'title': 'CTR por debajo del promedio',
            'message': f"CTR promedio: {context['avg_ctr']:.2f}% (benchmark: 1.8-2.5%)",
            'action': 'Optimizar creativos y testing. Ejecutar: python3 tools/benchmark_creatives.py',
            'impact': 'Mejorar CTR en 20-40%',
            'timeline': '2-3 semanas'
        })
    
    # Recomendación: Desbalance de formatos
    format_dist = context['by_format']
    total = context['total_creatives']
    ideal_1200 = total * 0.30
    ideal_1080 = total * 0.30
    
    if format_dist.get('1200x627', 0) < ideal_1200 * 0.7:
        recommendations.append({
            'priority': 'medium',
            'category': 'format_balance',
            'title': 'Pocos creativos en formato 1200×627',
            'message': f"Tienes {format_dist.get('1200x627', 0)} (ideal: {ideal_1200:.0f})",
            'action': f'Crear {int(ideal_1200 - format_dist.get("1200x627", 0))} creativos adicionales',
            'impact': 'Mejor coverage de desktop feed',
            'timeline': '1-2 semanas'
        })
    
    if format_dist.get('1080x1080', 0) < ideal_1080 * 0.7:
        recommendations.append({
            'priority': 'medium',
            'category': 'format_balance',
            'title': 'Pocos creativos en formato 1080×1080',
            'message': f"Tienes {format_dist.get('1080x1080', 0)} (ideal: {ideal_1080:.0f})",
            'action': f'Crear {int(ideal_1080 - format_dist.get("1080x1080", 0))} creativos adicionales',
            'impact': 'Mejor performance en mobile feed',
            'timeline': '1-2 semanas'
        })
    
    # Recomendación: Diversidad de ángulos
    unique_angles = len(context['by_angle'])
    if unique_angles < 3:
        recommendations.append({
            'priority': 'medium',
            'category': 'diversity',
            'title': 'Baja diversidad de ángulos',
            'message': f"Solo {unique_angles} ángulo(s) diferente(s)",
            'action': 'Crear más variantes con diferentes ángulos (metrics, social proof, urgency)',
            'impact': 'Más oportunidades de testing y personalización',
            'timeline': '2 semanas'
        })
    
    # Recomendación: Sin actividad reciente
    if not context['recent_activity'] and context['total_creatives'] > 0:
        recommendations.append({
            'priority': 'low',
            'category': 'activity',
            'title': 'Sin actividad reciente detectada',
            'message': 'No se detectó creación de creativos en últimos 30 días',
            'action': 'Crear nuevos creativos para mantener portfolio fresco',
            'impact': 'Evitar fatiga de audiencia',
            'timeline': '1 semana'
        })
    
    return recommendations

def prioritize_recommendations(recommendations):
    """Prioriza recomendaciones por impacto y urgencia"""
    priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    
    return sorted(
        recommendations,
        key=lambda x: (
            priority_order.get(x['priority'], 99),
            x.get('impact', ''),
            x.get('timeline', '')
        )
    )

def main():
    print("=" * 80)
    print("🤖 Sistema de Recomendaciones Inteligentes")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Analizar contexto
    print("🔍 Analizando contexto actual...")
    context = analyze_context(creatives)
    
    print("✅ Contexto analizado")
    print()
    
    # Generar recomendaciones
    print("💡 Generando recomendaciones inteligentes...")
    recommendations = generate_contextual_recommendations(context, creatives)
    recommendations = prioritize_recommendations(recommendations)
    
    if not recommendations:
        print("✅ No hay recomendaciones críticas. Sistema en buen estado.")
        return
    
    print(f"✅ {len(recommendations)} recomendación(es) generada(s)")
    print()
    
    # Mostrar recomendaciones
    print("=" * 80)
    print("💡 Recomendaciones Inteligentes")
    print("=" * 80)
    print()
    
    by_priority = defaultdict(list)
    for rec in recommendations:
        by_priority[rec['priority']].append(rec)
    
    for priority in ['critical', 'high', 'medium', 'low']:
        recs = by_priority.get(priority, [])
        if not recs:
            continue
        
        priority_icon = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🔵'
        }.get(priority, '⚪')
        
        print(f"{priority_icon} {priority.upper()} PRIORITY ({len(recs)})")
        print("-" * 80)
        print()
        
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['title']}")
            print(f"   📊 {rec['message']}")
            print(f"   💡 Acción: {rec['action']}")
            print(f"   📈 Impacto: {rec['impact']}")
            print(f"   📅 Timeline: {rec['timeline']}")
            print()
    
    # Resumen ejecutivo
    print("=" * 80)
    print("📊 Resumen Ejecutivo")
    print("=" * 80)
    print()
    print(f"Total recomendaciones: {len(recommendations)}")
    print(f"  🔴 Críticas: {len(by_priority.get('critical', []))}")
    print(f"  🟠 Altas: {len(by_priority.get('high', []))}")
    print(f"  🟡 Medias: {len(by_priority.get('medium', []))}")
    print(f"  🔵 Bajas: {len(by_priority.get('low', []))}")
    print()
    
    # Acciones inmediatas
    immediate = [r for r in recommendations if r['timeline'] == 'Inmediato' or r['priority'] == 'critical']
    if immediate:
        print("⚡ Acciones Inmediatas Requeridas:")
        print()
        for rec in immediate:
            print(f"  • {rec['action']}")
        print()
    
    # Guardar reporte
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'intelligent_recommendations_{timestamp}.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Recomendaciones Inteligentes\n\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total recomendaciones: {len(recommendations)}\n\n")
        
        for priority in ['critical', 'high', 'medium', 'low']:
            recs = by_priority.get(priority, [])
            if not recs:
                continue
            
            f.write(f"## {priority.upper()} Priority\n\n")
            for rec in recs:
                f.write(f"### {rec['title']}\n\n")
                f.write(f"- **Mensaje**: {rec['message']}\n")
                f.write(f"- **Acción**: {rec['action']}\n")
                f.write(f"- **Impacto**: {rec['impact']}\n")
                f.write(f"- **Timeline**: {rec['timeline']}\n\n")
    
    print(f"📄 Reporte guardado: {report_path}")
    print()

if __name__ == '__main__':
    main()


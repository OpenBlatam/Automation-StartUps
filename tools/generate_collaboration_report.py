#!/usr/bin/env python3
"""
Genera reportes de colaboración y uso de creativos
Identifica patrones de uso, ownership y recomendaciones de colaboración
"""
import csv
import sys
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

def analyze_usage_patterns(creatives):
    """Analiza patrones de uso"""
    by_product = defaultdict(list)
    by_format = defaultdict(list)
    by_angle = defaultdict(list)
    
    for creative in creatives:
        producto = creative.get('producto', 'unknown')
        formato = creative.get('formato', 'unknown')
        angulo = creative.get('angulo', 'unknown')
        
        by_product[producto].append(creative)
        by_format[formato].append(creative)
        by_angle[angulo].append(creative)
    
    return {
        'by_product': dict(by_product),
        'by_format': dict(by_format),
        'by_angle': dict(by_angle),
        'total': len(creatives)
    }

def identify_gaps(patterns):
    """Identifica gaps en portfolio"""
    gaps = []
    
    # Gap en formatos
    ideal_formats = {
        '1200x627': 0.30,
        '1080x1080': 0.30,
        '1080x1920': 0.20,
        'carousel': 0.20
    }
    
    total = patterns['total']
    for formato, ideal_pct in ideal_formats.items():
        actual_count = len(patterns['by_format'].get(formato, []))
        actual_pct = (actual_count / total) if total > 0 else 0
        gap = ideal_pct - actual_pct
        
        if gap > 0.10:
            gaps.append({
                'type': 'format',
                'item': formato,
                'gap': gap,
                'needed': int(gap * total),
                'priority': 'high' if gap > 0.20 else 'medium'
            })
    
    # Gap en diversidad de ángulos
    unique_angles = len(patterns['by_angle'])
    if unique_angles < 3:
        gaps.append({
            'type': 'angle_diversity',
            'item': f'Solo {unique_angles} ángulo(s)',
            'gap': 1.0,
            'needed': 3 - unique_angles,
            'priority': 'medium'
        })
    
    return gaps

def generate_collaboration_recommendations(patterns, gaps):
    """Genera recomendaciones de colaboración"""
    recommendations = []
    
    # Recomendaciones basadas en gaps
    for gap in gaps:
        if gap['type'] == 'format':
            recommendations.append({
                'action': f"Crear {gap['needed']} creativo(s) en formato {gap['item']}",
                'reason': f"Gap del {gap['gap']:.1%} vs. distribución ideal",
                'suggested_team': 'Design Team',
                'timeline': '1-2 semanas' if gap['needed'] <= 5 else '2-4 semanas'
            })
        
        elif gap['type'] == 'angle_diversity':
            recommendations.append({
                'action': f"Crear {gap['needed']} ángulo(s) adicional(es) para testing",
                'reason': 'Baja diversidad limita oportunidades de optimización',
                'suggested_team': 'Marketing + Design',
                'timeline': '2 semanas'
            })
    
    # Recomendaciones de optimización
    total = patterns['total']
    if total < 20:
        recommendations.append({
            'action': 'Aumentar portfolio a mínimo 20 creativos',
            'reason': 'Portfolio pequeño limita capacidad de testing y rotación',
            'suggested_team': 'Full Team',
            'timeline': '1 mes'
        })
    
    return recommendations

def generate_report(patterns, gaps, recommendations):
    """Genera reporte completo"""
    print("=" * 80)
    print("👥 Reporte de Colaboración y Portfolio")
    print("=" * 80)
    print()
    print(f"📊 Análisis de {patterns['total']} creativos")
    print()
    
    # Distribución actual
    print("=" * 80)
    print("📐 Distribución Actual")
    print("=" * 80)
    print()
    
    print("Por Producto:")
    for producto, creatives_list in sorted(patterns['by_product'].items(), key=lambda x: len(x[1]), reverse=True):
        pct = (len(creatives_list) / patterns['total']) * 100 if patterns['total'] > 0 else 0
        print(f"  • {producto:20}: {len(creatives_list):3} ({pct:5.1f}%)")
    
    print()
    print("Por Formato:")
    for formato, creatives_list in sorted(patterns['by_format'].items(), key=lambda x: len(x[1]), reverse=True):
        pct = (len(creatives_list) / patterns['total']) * 100 if patterns['total'] > 0 else 0
        print(f"  • {formato:20}: {len(creatives_list):3} ({pct:5.1f}%)")
    
    print()
    print("Por Ángulo:")
    for angle, creatives_list in sorted(patterns['by_angle'].items(), key=lambda x: len(x[1]), reverse=True):
        pct = (len(creatives_list) / patterns['total']) * 100 if patterns['total'] > 0 else 0
        print(f"  • {angle:20}: {len(creatives_list):3} ({pct:5.1f}%)")
    
    # Gaps identificados
    if gaps:
        print()
        print("=" * 80)
        print("⚠️  Gaps Identificados")
        print("=" * 80)
        print()
        
        for i, gap in enumerate(gaps, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🔵'
            }.get(gap['priority'], '⚪')
            
            print(f"{i}. {priority_icon} [{gap['priority'].upper()}] {gap['type']}")
            print(f"   {gap['item']}")
            print(f"   Gap: {gap['gap']:.1%} | Necesarios: {gap['needed']}")
            print()
    
    # Recomendaciones
    if recommendations:
        print("=" * 80)
        print("💡 Recomendaciones de Colaboración")
        print("=" * 80)
        print()
        
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec['action']}")
            print(f"   📊 Razón: {rec['reason']}")
            print(f"   👥 Equipo sugerido: {rec['suggested_team']}")
            print(f"   📅 Timeline: {rec['timeline']}")
            print()
    
    # Guardar reporte
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    report_path = reports_dir / f'collaboration_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Reporte de Colaboración y Portfolio\n\n")
        f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"## Resumen\n\n")
        f.write(f"- Total creativos: {patterns['total']}\n")
        f.write(f"- Gaps identificados: {len(gaps)}\n")
        f.write(f"- Recomendaciones: {len(recommendations)}\n\n")
        f.write(f"## Gaps\n\n")
        for gap in gaps:
            f.write(f"- **{gap['type']}**: {gap['item']} (Gap: {gap['gap']:.1%})\n")
        f.write(f"\n## Recomendaciones\n\n")
        for rec in recommendations:
            f.write(f"### {rec['action']}\n\n")
            f.write(f"- Razón: {rec['reason']}\n")
            f.write(f"- Equipo: {rec['suggested_team']}\n")
            f.write(f"- Timeline: {rec['timeline']}\n\n")
    
    print(f"📄 Reporte guardado: {report_path}")
    print()

def main():
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    # Analizar patrones
    patterns = analyze_usage_patterns(creatives)
    
    # Identificar gaps
    gaps = identify_gaps(patterns)
    
    # Generar recomendaciones
    recommendations = generate_collaboration_recommendations(patterns, gaps)
    
    # Generar reporte
    generate_report(patterns, gaps, recommendations)

if __name__ == '__main__':
    main()


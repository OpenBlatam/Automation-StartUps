#!/usr/bin/env python3
"""
Genera reporte completo de performance combinando análisis predictivo,
tendencias temporales y distribución de creativos
"""
import csv
import sys
from pathlib import Path
from datetime import datetime
import subprocess
import json

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

def analyze_distribution(creatives):
    """Analiza distribución de creativos"""
    from collections import defaultdict
    
    by_format = defaultdict(int)
    by_angle = defaultdict(int)
    by_product = defaultdict(int)
    
    for creative in creatives:
        by_format[creative.get('formato', 'unknown')] += 1
        by_angle[creative.get('angulo', 'unknown')] += 1
        by_product[creative.get('producto', 'unknown')] += 1
    
    total = len(creatives)
    
    return {
        'by_format': dict(by_format),
        'by_angle': dict(by_angle),
        'by_product': dict(by_product),
        'total': total,
        'format_distribution': {k: (v/total)*100 for k, v in by_format.items()} if total > 0 else {},
        'angle_distribution': {k: (v/total)*100 for k, v in by_angle.items()} if total > 0 else {},
        'product_distribution': {k: (v/total)*100 for k, v in by_product.items()} if total > 0 else {}
    }

def generate_recommendations(distribution):
    """Genera recomendaciones estratégicas"""
    recommendations = []
    
    # Balance de formatos
    format_dist = distribution['format_distribution']
    
    # Ideal: 30% 1200x627, 30% 1080x1080, 20% 1080x1920, 20% carousel
    ideal_dist = {
        '1200x627': 30,
        '1080x1080': 30,
        '1080x1920': 20,
        'carousel': 20
    }
    
    for formato, ideal_pct in ideal_dist.items():
        actual_pct = format_dist.get(formato, 0)
        gap = ideal_pct - actual_pct
        
        if gap > 5:  # Más de 5% de diferencia
            needed = int((gap / 100) * distribution['total'])
            recommendations.append({
                'priority': 'high' if gap > 15 else 'medium',
                'category': 'format_balance',
                'message': f"Faltan creativos en formato {formato}",
                'detail': f"{formato}: {actual_pct:.1f}% (ideal: {ideal_pct}%)",
                'action': f"Crear ~{needed} creativos adicionales en formato {formato}",
                'expected_impact': f"Mejorar balance de formatos (+{gap:.1f}%)"
            })
    
    # Diversidad de ángulos
    angle_dist = distribution['angle_distribution']
    
    if angle_dist.get('metrics', 0) < 20:
        recommendations.append({
            'priority': 'medium',
            'category': 'angle_diversity',
            'message': 'Pocos creativos con ángulo "metrics"',
            'detail': f"Metrics: {angle_dist.get('metrics', 0):.1f}% (recomendado: >20%)",
            'action': 'Aumentar creativos enfocados en métricas/resultados',
            'expected_impact': '+15-20% CVR esperado'
        })
    
    # Cobertura de productos
    product_dist = distribution['product_distribution']
    
    for product, pct in product_dist.items():
        if pct < 10 and product != 'unknown':
            recommendations.append({
                'priority': 'low',
                'category': 'product_coverage',
                'message': f'Cobertura baja para producto: {product}',
                'detail': f"{product}: {pct:.1f}%",
                'action': f'Considerar más creativos para {product}',
                'expected_impact': 'Mejor balance de portfolio'
            })
    
    return recommendations

def run_external_analysis(script_name):
    """Ejecuta script externo y captura output"""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name
    
    if not script_path.exists():
        return None
    
    try:
        if script_name.endswith('.sh'):
            result = subprocess.run(
                ['bash', str(script_path)],
                capture_output=True,
                text=True,
                cwd=script_dir.parent,
                timeout=60
            )
        else:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=script_dir.parent,
                timeout=60
            )
        
        if result.returncode == 0:
            return result.stdout
    except:
        pass
    
    return None

def generate_markdown_report(creatives, distribution, recommendations):
    """Genera reporte en Markdown"""
    report = []
    
    report.append("# 📊 Reporte de Performance de Creativos")
    report.append("")
    report.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"**Total de creativos:** {len(creatives)}")
    report.append("")
    
    # Distribución por formato
    report.append("## 📐 Distribución por Formato")
    report.append("")
    report.append("| Formato | Cantidad | Porcentaje |")
    report.append("|---------|----------|------------|")
    for formato, count in sorted(distribution['by_format'].items(), key=lambda x: x[1], reverse=True):
        pct = distribution['format_distribution'].get(formato, 0)
        report.append(f"| {formato} | {count} | {pct:.1f}% |")
    report.append("")
    
    # Distribución por ángulo
    report.append("## 🎯 Distribución por Ángulo")
    report.append("")
    report.append("| Ángulo | Cantidad | Porcentaje |")
    report.append("|--------|----------|------------|")
    for angulo, count in sorted(distribution['by_angle'].items(), key=lambda x: x[1], reverse=True):
        pct = distribution['angle_distribution'].get(angulo, 0)
        report.append(f"| {angulo} | {count} | {pct:.1f}% |")
    report.append("")
    
    # Distribución por producto
    report.append("## 🏢 Distribución por Producto")
    report.append("")
    report.append("| Producto | Cantidad | Porcentaje |")
    report.append("|----------|----------|------------|")
    for product, count in sorted(distribution['by_product'].items(), key=lambda x: x[1], reverse=True):
        pct = distribution['product_distribution'].get(product, 0)
        report.append(f"| {product} | {count} | {pct:.1f}% |")
    report.append("")
    
    # Recomendaciones
    if recommendations:
        report.append("## 💡 Recomendaciones Estratégicas")
        report.append("")
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🔵'
            }.get(rec['priority'], '⚪')
            
            report.append(f"### {i}. {priority_icon} {rec['message']}")
            report.append("")
            report.append(f"**Detalle:** {rec['detail']}")
            report.append("")
            report.append(f"**Acción:** {rec['action']}")
            report.append("")
            report.append(f"**Impacto esperado:** {rec['expected_impact']}")
            report.append("")
    
    return '\n'.join(report)

def main():
    print("=" * 80)
    print("📊 Generador de Reporte de Performance")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Analizar distribución
    print("📊 Calculando distribución...")
    distribution = analyze_distribution(creatives)
    
    # Generar recomendaciones
    print("💡 Generando recomendaciones...")
    recommendations = generate_recommendations(distribution)
    
    # Mostrar resumen
    print()
    print("=" * 80)
    print("📊 Resumen de Distribución")
    print("=" * 80)
    print()
    
    print("Por Formato:")
    for formato, count in sorted(distribution['by_format'].items(), key=lambda x: x[1], reverse=True):
        pct = distribution['format_distribution'].get(formato, 0)
        print(f"  {formato:15}: {count:3} ({pct:5.1f}%)")
    
    print()
    print("Por Ángulo:")
    for angulo, count in sorted(distribution['by_angle'].items(), key=lambda x: x[1], reverse=True):
        pct = distribution['angle_distribution'].get(angulo, 0)
        print(f"  {angulo:15}: {count:3} ({pct:5.1f}%)")
    
    print()
    print("Por Producto:")
    for product, count in sorted(distribution['by_product'].items(), key=lambda x: x[1], reverse=True):
        pct = distribution['product_distribution'].get(product, 0)
        print(f"  {product:15}: {count:3} ({pct:5.1f}%)")
    
    # Mostrar recomendaciones
    if recommendations:
        print()
        print("=" * 80)
        print("💡 Recomendaciones Prioritarias")
        print("=" * 80)
        print()
        
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        low_priority = [r for r in recommendations if r['priority'] == 'low']
        
        for priority_list, label in [(high_priority, '🔴 Alta Prioridad'), 
                                     (medium_priority, '🟡 Media Prioridad'),
                                     (low_priority, '🔵 Baja Prioridad')]:
            if priority_list:
                print(f"\n{label}:")
                for i, rec in enumerate(priority_list, 1):
                    print(f"\n  {i}. {rec['message']}")
                    print(f"     {rec['detail']}")
                    print(f"     💡 {rec['action']}")
                    print(f"     📈 {rec['expected_impact']}")
    
    # Generar reporte Markdown
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    report_path = root_dir / 'reports' / f'performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    report_path.parent.mkdir(exist_ok=True)
    
    markdown = generate_markdown_report(creatives, distribution, recommendations)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(markdown)
    
    print()
    print("=" * 80)
    print(f"✅ Reporte guardado: {report_path}")
    print("=" * 80)
    print()

if __name__ == '__main__':
    main()


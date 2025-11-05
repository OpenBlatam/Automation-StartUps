#!/usr/bin/env python3
"""
Benchmarking de creativos vs. estándares de industria
Compara métricas actuales con benchmarks y genera recomendaciones
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict

# Benchmarks de industria (LinkedIn Ads)
INDUSTRY_BENCHMARKS = {
    'ctr': {
        '1200x627': {'min': 0.015, 'avg': 0.018, 'max': 0.025},
        '1080x1080': {'min': 0.020, 'avg': 0.025, 'max': 0.035},
        '1080x1920': {'min': 0.025, 'avg': 0.030, 'max': 0.040},
        'carousel': {'min': 0.022, 'avg': 0.028, 'max': 0.038}
    },
    'cvr': {
        '1200x627': {'min': 0.045, 'avg': 0.055, 'max': 0.070},
        '1080x1080': {'min': 0.055, 'avg': 0.065, 'max': 0.080},
        '1080x1920': {'min': 0.065, 'avg': 0.075, 'max': 0.090},
        'carousel': {'min': 0.070, 'avg': 0.080, 'max': 0.095}
    },
    'cpa': {
        'b2b_saas': {'min': 40, 'avg': 60, 'max': 100},
        'b2b_education': {'min': 35, 'avg': 50, 'max': 80},
        'b2b_tools': {'min': 45, 'avg': 65, 'max': 110}
    }
}

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

def analyze_portfolio(creatives):
    """Analiza portfolio actual"""
    by_format = defaultdict(lambda: {'count': 0, 'total_size': 0})
    by_angle = defaultdict(int)
    by_product = defaultdict(int)
    
    for creative in creatives:
        formato = creative.get('formato', 'unknown')
        angulo = creative.get('angulo', 'unknown')
        producto = creative.get('producto', 'unknown')
        
        by_format[formato]['count'] += 1
        by_angle[angulo] += 1
        by_product[producto] += 1
    
    return {
        'by_format': dict(by_format),
        'by_angle': dict(by_angle),
        'by_product': dict(by_product),
        'total': len(creatives)
    }

def compare_with_benchmarks(portfolio):
    """Compara portfolio con benchmarks"""
    comparisons = []
    
    # Comparar distribución de formatos
    total = portfolio['total']
    ideal_distribution = {
        '1200x627': 0.30,
        '1080x1080': 0.30,
        '1080x1920': 0.20,
        'carousel': 0.20
    }
    
    for formato, ideal_pct in ideal_distribution.items():
        actual_count = portfolio['by_format'].get(formato, {}).get('count', 0)
        actual_pct = (actual_count / total) if total > 0 else 0
        gap = ideal_pct - actual_pct
        
        if abs(gap) > 0.10:  # Más de 10% de diferencia
            comparisons.append({
                'category': 'format_distribution',
                'item': formato,
                'actual': f"{actual_pct:.1%}",
                'ideal': f"{ideal_pct:.1%}",
                'gap': f"{gap:+.1%}",
                'status': 'below' if gap > 0 else 'above'
            })
    
    return comparisons

def calculate_portfolio_score(portfolio):
    """Calcula score del portfolio vs. benchmarks"""
    score = 100
    deductions = []
    
    # Penalizar desbalance de formatos
    total = portfolio['total']
    ideal_distribution = {
        '1200x627': 0.30,
        '1080x1080': 0.30,
        '1080x1920': 0.20,
        'carousel': 0.20
    }
    
    for formato, ideal_pct in ideal_distribution.items():
        actual_count = portfolio['by_format'].get(formato, {}).get('count', 0)
        actual_pct = (actual_count / total) if total > 0 else 0
        gap = abs(ideal_pct - actual_pct)
        
        if gap > 0.15:
            deduction = int(gap * 100)
            score -= deduction
            deductions.append(f"-{deduction} por desbalance en {formato}")
    
    # Penalizar falta de diversidad en ángulos
    unique_angles = len(portfolio['by_angle'])
    if unique_angles < 3:
        deduction = (3 - unique_angles) * 5
        score -= deduction
        deductions.append(f"-{deduction} por baja diversidad de ángulos")
    
    return max(0, score), deductions

def generate_recommendations(portfolio, comparisons, score):
    """Genera recomendaciones basadas en benchmarking"""
    recommendations = []
    
    # Recomendaciones de formato
    for comp in comparisons:
        if comp['status'] == 'below':
            needed = int(float(comp['gap'].replace('%', '').replace('+', '')) / 100 * portfolio['total'])
            recommendations.append({
                'priority': 'high' if needed > 5 else 'medium',
                'category': 'format',
                'message': f"Crear {needed} creativo(s) adicional(es) en formato {comp['item']}",
                'rationale': f"Actual: {comp['actual']}, Ideal: {comp['ideal']}, Gap: {comp['gap']}",
                'expected_impact': f"Mejorar balance de portfolio y coverage de formatos"
            })
    
    # Recomendaciones basadas en score
    if score < 70:
        recommendations.append({
            'priority': 'high',
            'category': 'portfolio_health',
            'message': 'Portfolio necesita optimización general',
            'rationale': f'Score actual: {score}/100',
            'expected_impact': 'Mejorar distribución y diversidad de creativos'
        })
    
    # Recomendaciones de diversidad
    unique_angles = len(portfolio['by_angle'])
    if unique_angles < 3:
        recommendations.append({
            'priority': 'medium',
            'category': 'diversity',
            'message': f'Aumentar diversidad de ángulos (actual: {unique_angles}, recomendado: 4+)',
            'rationale': 'Más ángulos = más oportunidades de testing y optimización',
            'expected_impact': 'Mejor capacidad de A/B testing y personalización'
        })
    
    return recommendations

def main():
    print("=" * 80)
    print("📊 Benchmarking de Creativos vs. Estándares de Industria")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Analizar portfolio
    portfolio = analyze_portfolio(creatives)
    
    # Comparar con benchmarks
    comparisons = compare_with_benchmarks(portfolio)
    
    # Calcular score
    score, deductions = calculate_portfolio_score(portfolio)
    
    # Mostrar resultados
    print("=" * 80)
    print("📊 Análisis de Portfolio")
    print("=" * 80)
    print()
    
    print("Distribución por Formato:")
    total = portfolio['total']
    ideal_distribution = {
        '1200x627': 0.30,
        '1080x1080': 0.30,
        '1080x1920': 0.20,
        'carousel': 0.20
    }
    
    for formato, ideal_pct in ideal_distribution.items():
        actual_count = portfolio['by_format'].get(formato, {}).get('count', 0)
        actual_pct = (actual_count / total) if total > 0 else 0
        gap = ideal_pct - actual_pct
        
        status = "✅" if abs(gap) <= 0.10 else "⚠️"
        print(f"  {status} {formato:15}: {actual_count:3} ({actual_pct:5.1f}%) | Ideal: {ideal_pct:.1%} | Gap: {gap:+.1%}")
    
    print()
    print("Distribución por Ángulo:")
    for angle, count in sorted(portfolio['by_angle'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total) if total > 0 else 0
        print(f"  • {angle:15}: {count:3} ({pct:5.1f}%)")
    
    print()
    print("=" * 80)
    print(f"📈 Score de Portfolio: {score}/100")
    print("=" * 80)
    
    if deductions:
        print("\nDeducciones:")
        for deduction in deductions:
            print(f"  {deduction}")
    
    # Status basado en score
    if score >= 90:
        status = "✅ Excelente"
    elif score >= 75:
        status = "✅ Bueno"
    elif score >= 60:
        status = "⚠️  Requiere atención"
    else:
        status = "❌ Crítico"
    
    print(f"\nEstado: {status}")
    print()
    
    # Mostrar benchmarks
    print("=" * 80)
    print("📊 Benchmarks de Industria (LinkedIn Ads)")
    print("=" * 80)
    print()
    
    print("CTR por Formato:")
    for formato, benchmarks in INDUSTRY_BENCHMARKS['ctr'].items():
        print(f"  {formato:15}: Min: {benchmarks['min']*100:.1f}% | Avg: {benchmarks['avg']*100:.1f}% | Max: {benchmarks['max']*100:.1f}%")
    
    print()
    print("CVR por Formato:")
    for formato, benchmarks in INDUSTRY_BENCHMARKS['cvr'].items():
        print(f"  {formato:15}: Min: {benchmarks['min']*100:.1f}% | Avg: {benchmarks['avg']*100:.1f}% | Max: {benchmarks['max']*100:.1f}%")
    
    # Generar recomendaciones
    recommendations = generate_recommendations(portfolio, comparisons, score)
    
    if recommendations:
        print()
        print("=" * 80)
        print("💡 Recomendaciones Estratégicas")
        print("=" * 80)
        print()
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🔵'
            }.get(rec['priority'], '⚪')
            
            print(f"{i}. {priority_icon} [{rec['priority'].upper()}] {rec['message']}")
            print(f"   📊 {rec['rationale']}")
            print(f"   📈 Impacto esperado: {rec['expected_impact']}")
            print()
    
    print("=" * 80)
    print()
    print("💡 Tip: Compara tus métricas reales (CTR, CVR) con estos benchmarks")
    print("   para identificar oportunidades de optimización")

if __name__ == '__main__':
    main()


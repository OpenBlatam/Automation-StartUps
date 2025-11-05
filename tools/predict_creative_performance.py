#!/usr/bin/env python3
"""
Análisis predictivo de performance de creativos basado en patrones históricos
y características del creative (formato, ángulo, producto)
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict
import json

# Benchmarks históricos (basados en industria)
BENCHMARKS = {
    'format': {
        '1200x627': {'ctr': 0.018, 'cvr': 0.055, 'cpa': 50},
        '1080x1080': {'ctr': 0.025, 'cvr': 0.065, 'cpa': 45},
        '1080x1920': {'ctr': 0.030, 'cvr': 0.075, 'cpa': 40},
        'carousel': {'ctr': 0.028, 'cvr': 0.080, 'cpa': 42}
    },
    'angle': {
        'metrics': {'ctr_multiplier': 1.15, 'cvr_multiplier': 1.20},
        'socialproof': {'ctr_multiplier': 1.10, 'cvr_multiplier': 1.15},
        'urgency': {'ctr_multiplier': 1.05, 'cvr_multiplier': 1.10},
        'base': {'ctr_multiplier': 1.0, 'cvr_multiplier': 1.0}
    },
    'product': {
        'iabulk': {'cpa_multiplier': 1.0},
        'cursoia': {'cpa_multiplier': 0.85},
        'saasia': {'cpa_multiplier': 1.15}
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

def predict_performance(creative):
    """Predice performance de un creative basado en sus características"""
    formato = creative.get('formato', '1200x627')
    angulo = creative.get('angulo', 'base')
    producto = creative.get('producto', 'iabulk')
    
    # Obtener benchmarks base por formato
    format_bench = BENCHMARKS['format'].get(formato, BENCHMARKS['format']['1200x627'])
    
    # Aplicar multiplicadores por ángulo
    angle_bench = BENCHMARKS['angle'].get(angulo, BENCHMARKS['angle']['base'])
    
    # Aplicar multiplicadores por producto
    product_bench = BENCHMARKS['product'].get(producto, BENCHMARKS['product']['iabulk'])
    
    # Calcular métricas predichas
    predicted_ctr = format_bench['ctr'] * angle_bench['ctr_multiplier']
    predicted_cvr = format_bench['cvr'] * angle_bench['cvr_multiplier']
    predicted_cpa = format_bench['cpa'] * product_bench['cpa_multiplier']
    
    # Calcular ROAS estimado (asumiendo LTV promedio)
    assumed_ltv = 500  # Valor promedio estimado
    predicted_roas = (predicted_cvr * assumed_ltv) / predicted_cpa
    
    return {
        'ctr': predicted_ctr,
        'cvr': predicted_cvr,
        'cpa': predicted_cpa,
        'roas': predicted_roas,
        'confidence': 'medium'  # Basado en benchmarks de industria
    }

def analyze_portfolio(creatives):
    """Analiza portfolio completo y genera insights"""
    predictions = []
    by_format = defaultdict(list)
    by_angle = defaultdict(list)
    
    for creative in creatives:
        pred = predict_performance(creative)
        pred['creative'] = creative
        predictions.append(pred)
        
        formato = creative.get('formato', 'unknown')
        angulo = creative.get('angulo', 'unknown')
        by_format[formato].append(pred)
        by_angle[angulo].append(pred)
    
    # Calcular promedios
    format_avg = {}
    for formato, preds in by_format.items():
        format_avg[formato] = {
            'avg_ctr': sum(p['ctr'] for p in preds) / len(preds),
            'avg_cvr': sum(p['cvr'] for p in preds) / len(preds),
            'avg_cpa': sum(p['cpa'] for p in preds) / len(preds),
            'count': len(preds)
        }
    
    angle_avg = {}
    for angulo, preds in by_angle.items():
        angle_avg[angulo] = {
            'avg_ctr': sum(p['ctr'] for p in preds) / len(preds),
            'avg_cvr': sum(p['cvr'] for p in preds) / len(preds),
            'count': len(preds)
        }
    
    return {
        'predictions': predictions,
        'format_avg': format_avg,
        'angle_avg': angle_avg,
        'total': len(predictions)
    }

def generate_recommendations(analysis):
    """Genera recomendaciones basadas en análisis"""
    recommendations = []
    
    # Recomendación: Balance de formatos
    format_counts = {fmt: stats['count'] for fmt, stats in analysis['format_avg'].items()}
    total_formats = sum(format_counts.values())
    
    if format_counts.get('1080x1080', 0) / total_formats < 0.25:
        recommendations.append({
            'priority': 'high',
            'category': 'format_balance',
            'message': '⚠️ Pocos creativos en formato square (1080×1080)',
            'insight': f"Solo {format_counts.get('1080x1080', 0)}/{total_formats} creativos ({(format_counts.get('1080x1080', 0)/total_formats)*100:.1f}%)",
            'action': 'Crear más formatos square para mobile feed (mejor CTR esperado: +39%)',
            'expected_impact': '+15-20% CTR en mobile'
        })
    
    # Recomendación: Ángulos de alto performance
    if analysis['angle_avg'].get('metrics', {}).get('count', 0) < 3:
        recommendations.append({
            'priority': 'medium',
            'category': 'angle_diversity',
            'message': '📊 Pocos creativos con ángulo "metrics"',
            'insight': f"Metrics ads tienen mejor CVR esperado (+20%)",
            'action': 'Crear más ads enfocados en métricas/resultados',
            'expected_impact': '+15-20% CVR'
        })
    
    # Identificar mejor combinación
    best_combo = None
    best_roas = 0
    
    for pred in analysis['predictions']:
        if pred['roas'] > best_roas:
            best_roas = pred['roas']
            best_combo = pred['creative']
    
    if best_combo:
        recommendations.append({
            'priority': 'info',
            'category': 'best_practice',
            'message': '⭐ Mejor combinación predicha',
            'insight': f"{best_combo.get('formato')} + {best_combo.get('angulo')} = ROAS estimado {best_roas:.2f}x",
            'action': 'Priorizar esta combinación en próximas campañas',
            'expected_impact': f"ROAS {best_roas:.2f}x"
        })
    
    return recommendations

def main():
    print("=" * 80)
    print("🔮 Análisis Predictivo de Performance")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Analizar portfolio
    analysis = analyze_portfolio(creatives)
    
    # Mostrar resumen por formato
    print("📊 Performance Predicha por Formato:")
    print("-" * 80)
    for formato, stats in sorted(analysis['format_avg'].items(), key=lambda x: x[1]['avg_roas'], reverse=True):
        roas = (stats['avg_cvr'] * 500) / stats['avg_cpa']  # LTV estimado 500
        print(f"\n{formato:15} ({stats['count']} creativos):")
        print(f"  CTR esperado:  {stats['avg_ctr']*100:.2f}%")
        print(f"  CVR esperado:  {stats['avg_cvr']*100:.2f}%")
        print(f"  CPA esperado:  ${stats['avg_cpa']:.2f}")
        print(f"  ROAS estimado: {roas:.2f}x")
    
    print()
    print("🎯 Performance Predicha por Ángulo:")
    print("-" * 80)
    for angulo, stats in sorted(analysis['angle_avg'].items(), key=lambda x: x[1]['avg_ctr'], reverse=True):
        print(f"\n{angulo:15} ({stats['count']} creativos):")
        print(f"  CTR esperado:  {stats['avg_ctr']*100:.2f}%")
        print(f"  CVR esperado:  {stats['avg_cvr']*100:.2f}%")
    
    # Generar recomendaciones
    recommendations = generate_recommendations(analysis)
    
    if recommendations:
        print()
        print("💡 Recomendaciones Estratégicas:")
        print("-" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'info': '🔵'
            }.get(rec['priority'], '⚪')
            
            print(f"\n{i}. {priority_icon} {rec['message']}")
            print(f"   {rec['insight']}")
            print(f"   💡 {rec['action']}")
            print(f"   📈 Impacto esperado: {rec['expected_impact']}")
    
    print()
    print("=" * 80)
    print()
    print("⚠️  Nota: Estas predicciones están basadas en benchmarks de industria.")
    print("   Ajusta según tu historial real de performance.")
    print()

if __name__ == '__main__':
    main()



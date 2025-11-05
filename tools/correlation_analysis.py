#!/usr/bin/env python3
"""
Análisis de Correlaciones Avanzado
Identifica relaciones entre variables (formato, ángulo, producto) y performance
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict
import statistics

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

def extract_metrics(creatives):
    """Extrae métricas para análisis de correlación"""
    metrics = []
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        if impressions == 0:
            continue
        
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0
        cpa = (spend / conversions) if conversions > 0 else 0
        
        assumed_ltv = 500
        revenue = conversions * assumed_ltv
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
        
        metrics.append({
            'formato': creative.get('formato', 'unknown'),
            'angulo': creative.get('angulo', 'unknown'),
            'producto': creative.get('producto', 'unknown'),
            'ctr': ctr,
            'cpc': cpc,
            'cpa': cpa,
            'roi': roi,
            'conversions': conversions,
            'impressions': impressions
        })
    
    return metrics

def calculate_correlation(factor_values, metric_values):
    """Calcula correlación simple entre factor y métrica"""
    if len(factor_values) != len(metric_values) or len(factor_values) < 2:
        return None
    
    # Agrupar por factor
    by_factor = defaultdict(list)
    for factor, metric in zip(factor_values, metric_values):
        by_factor[factor].append(metric)
    
    if len(by_factor) < 2:
        return None
    
    # Calcular diferencia promedio entre grupos
    group_averages = {}
    for factor, values in by_factor.items():
        if values:
            group_averages[factor] = statistics.mean(values)
    
    # Calcular varianza entre grupos vs. dentro de grupos
    overall_mean = statistics.mean(metric_values)
    
    between_group_variance = 0
    within_group_variance = 0
    
    for factor, avg in group_averages.items():
        count = len(by_factor[factor])
        between_group_variance += count * ((avg - overall_mean) ** 2)
        
        for value in by_factor[factor]:
            within_group_variance += ((value - avg) ** 2)
    
    if within_group_variance == 0:
        return 1.0  # Correlación perfecta
    
    correlation_strength = between_group_variance / (between_group_variance + within_group_variance)
    
    return correlation_strength

def analyze_correlations(metrics):
    """Analiza correlaciones entre factores y métricas"""
    correlations = []
    
    # Correlación: Formato → CTR
    format_values = [m['formato'] for m in metrics]
    ctr_values = [m['ctr'] for m in metrics]
    format_ctr_corr = calculate_correlation(format_values, ctr_values)
    
    if format_ctr_corr:
        correlations.append({
            'factor': 'formato',
            'metric': 'CTR',
            'strength': format_ctr_corr,
            'interpretation': 'strong' if format_ctr_corr > 0.5 else 'moderate' if format_ctr_corr > 0.3 else 'weak'
        })
    
    # Correlación: Ángulo → ROI
    angle_values = [m['angulo'] for m in metrics]
    roi_values = [m['roi'] for m in metrics]
    angle_roi_corr = calculate_correlation(angle_values, roi_values)
    
    if angle_roi_corr:
        correlations.append({
            'factor': 'angulo',
            'metric': 'ROI',
            'strength': angle_roi_corr,
            'interpretation': 'strong' if angle_roi_corr > 0.5 else 'moderate' if angle_roi_corr > 0.3 else 'weak'
        })
    
    # Correlación: Producto → Conversiones
    product_values = [m['producto'] for m in metrics]
    conv_values = [m['conversions'] for m in metrics]
    product_conv_corr = calculate_correlation(product_values, conv_values)
    
    if product_conv_corr:
        correlations.append({
            'factor': 'producto',
            'metric': 'Conversions',
            'strength': product_conv_corr,
            'interpretation': 'strong' if product_conv_corr > 0.5 else 'moderate' if product_conv_corr > 0.3 else 'weak'
        })
    
    # Análisis de combinaciones
    combo_performance = defaultdict(list)
    for m in metrics:
        combo = f"{m['formato']}_{m['angulo']}"
        combo_performance[combo].append(m['roi'])
    
    best_combo = None
    best_avg_roi = -999
    
    for combo, roi_list in combo_performance.items():
        if len(roi_list) >= 2:  # Mínimo 2 muestras
            avg_roi = statistics.mean(roi_list)
            if avg_roi > best_avg_roi:
                best_avg_roi = avg_roi
                best_combo = combo
    
    return correlations, best_combo, best_avg_roi

def main():
    print("=" * 80)
    print("📊 Análisis de Correlaciones Avanzado")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Extraer métricas
    metrics = extract_metrics(creatives)
    
    if not metrics:
        print("⚠️  No se encontraron creativos con métricas")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    print(f"✅ {len(metrics)} creativos con métricas extraídas")
    print()
    
    # Analizar correlaciones
    print("🔍 Analizando correlaciones...")
    correlations, best_combo, best_avg_roi = analyze_correlations(metrics)
    
    print("✅ Análisis completado")
    print()
    
    # Mostrar resultados
    print("=" * 80)
    print("📊 Correlaciones Identificadas")
    print("=" * 80)
    print()
    
    if correlations:
        for corr in correlations:
            strength_icon = {
                'strong': '🟢',
                'moderate': '🟡',
                'weak': '🔵'
            }.get(corr['interpretation'], '⚪')
            
            print(f"{strength_icon} {corr['factor'].upper()} → {corr['metric']}")
            print(f"   Fuerza: {corr['strength']:.3f} ({corr['interpretation']})")
            
            if corr['strength'] > 0.5:
                print(f"   💡 {corr['factor']} tiene influencia fuerte en {corr['metric']}")
            elif corr['strength'] > 0.3:
                print(f"   💡 {corr['factor']} tiene influencia moderada en {corr['metric']}")
            
            print()
    else:
        print("⚠️  No se pudieron calcular correlaciones significativas")
        print("   Se requieren más datos para análisis de correlación")
        print()
    
    # Mejor combinación
    if best_combo:
        formato, angulo = best_combo.split('_', 1)
        print("=" * 80)
        print("🏆 Mejor Combinación Identificada")
        print("=" * 80)
        print()
        print(f"Combinación: {formato} + {angulo}")
        print(f"ROI promedio: {best_avg_roi:.1f}%")
        print(f"💡 Recomendación: Priorizar esta combinación en nuevos creativos")
        print()
    
    print("=" * 80)
    print()
    print("💡 Tip: Correlaciones fuertes (>0.5) indican factores clave para optimización")
    print("   Usa estos insights para enfocar esfuerzos de creación")

if __name__ == '__main__':
    main()


#!/usr/bin/env python3
"""
Optimización basada en Machine Learning
Analiza patrones en performance y genera recomendaciones inteligentes
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

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

def extract_features(creatives):
    """Extrae features para ML"""
    features = []
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        if impressions == 0:
            continue
        
        # Features categóricas
        formato = creative.get('formato', 'unknown')
        angulo = creative.get('angulo', 'unknown')
        producto = creative.get('producto', 'unknown')
        
        # Features numéricas
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0
        cpa = (spend / conversions) if conversions > 0 else 0
        
        # Feature engineering
        assumed_ltv = 500
        revenue = conversions * assumed_ltv
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
        
        features.append({
            'creative_file': creative.get('creative_file', ''),
            'formato': formato,
            'angulo': angulo,
            'producto': producto,
            'ctr': ctr,
            'cpc': cpc,
            'cpa': cpa,
            'roi': roi,
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'conversions': conversions,
            'revenue': revenue
        })
    
    return features

def find_patterns(features):
    """Encuentra patrones en los datos usando reglas simples"""
    patterns = []
    
    # Agrupar por formato
    by_format = defaultdict(list)
    for f in features:
        by_format[f['formato']].append(f)
    
    # Patrón: Mejor formato para CTR
    format_ctr = {}
    for formato, format_features in by_format.items():
        if format_features:
            avg_ctr = sum(x['ctr'] for x in format_features) / len(format_features)
            format_ctr[formato] = avg_ctr
    
    if format_ctr:
        best_format = max(format_ctr.items(), key=lambda x: x[1])
        patterns.append({
            'type': 'best_format_ctr',
            'insight': f"Formato {best_format[0]} tiene mejor CTR promedio ({best_format[1]:.2f}%)",
            'recommendation': f"Priorizar formato {best_format[0]} para nuevos creativos",
            'confidence': 'high'
        })
    
    # Agrupar por ángulo
    by_angle = defaultdict(list)
    for f in features:
        by_angle[f['angulo']].append(f)
    
    # Patrón: Mejor ángulo para ROI
    angle_roi = {}
    for angle, angle_features in by_angle.items():
        if angle_features:
            avg_roi = sum(x['roi'] for x in angle_features) / len(angle_features)
            angle_roi[angle] = avg_roi
    
    if angle_roi:
        best_angle = max(angle_roi.items(), key=lambda x: x[1])
        patterns.append({
            'type': 'best_angle_roi',
            'insight': f"Ángulo '{best_angle[0]}' tiene mejor ROI promedio ({best_angle[1]:.1f}%)",
            'recommendation': f"Usar ángulo '{best_angle[0]}' más frecuentemente",
            'confidence': 'high'
        })
    
    # Patrón: Combinación óptima formato + ángulo
    combo_performance = defaultdict(list)
    for f in features:
        combo = f"{f['formato']}_{f['angulo']}"
        combo_performance[combo].append(f)
    
    combo_avg_roi = {}
    for combo, combo_features in combo_performance.items():
        if len(combo_features) >= 2:  # Mínimo 2 muestras
            avg_roi = sum(x['roi'] for x in combo_features) / len(combo_features)
            combo_avg_roi[combo] = avg_roi
    
    if combo_avg_roi:
        best_combo = max(combo_avg_roi.items(), key=lambda x: x[1])
        formato, angulo = best_combo[0].split('_', 1)
        patterns.append({
            'type': 'best_combo',
            'insight': f"Combinación {formato} + {angulo} tiene mejor ROI ({best_combo[1]:.1f}%)",
            'recommendation': f"Crear más creativos con formato {formato} y ángulo {angulo}",
            'confidence': 'high'
        })
    
    # Patrón: Volumen óptimo para mejor performance
    high_performers = [f for f in features if f['roi'] > 50]
    if high_performers:
        avg_impressions_top = sum(x['impressions'] for x in high_performers) / len(high_performers)
        patterns.append({
            'type': 'volume_threshold',
            'insight': f"Top performers tienen promedio {avg_impressions_top:,.0f} impresiones",
            'recommendation': f"Dar más impresiones a creativos prometedores",
            'confidence': 'medium'
        })
    
    return patterns

def predict_performance(new_creative_features, historical_features):
    """Predice performance de un nuevo creative basado en patrones históricos"""
    if not historical_features:
        return None
    
    formato = new_creative_features.get('formato')
    angulo = new_creative_features.get('angulo')
    
    # Buscar creativos similares
    similar = [
        f for f in historical_features
        if f['formato'] == formato and f['angulo'] == angulo
    ]
    
    if not similar:
        # Fallback a solo formato
        similar = [f for f in historical_features if f['formato'] == formato]
    
    if not similar:
        return None
    
    # Calcular promedio de performance similar
    avg_ctr = sum(x['ctr'] for x in similar) / len(similar)
    avg_roi = sum(x['roi'] for x in similar) / len(similar)
    avg_cpa = sum(x['cpa'] for x in similar) / len(similar) if any(x['cpa'] > 0 for x in similar) else 0
    
    return {
        'predicted_ctr': avg_ctr,
        'predicted_roi': avg_roi,
        'predicted_cpa': avg_cpa,
        'confidence': 'high' if len(similar) >= 5 else 'medium' if len(similar) >= 2 else 'low',
        'sample_size': len(similar)
    }

def generate_ml_recommendations(features, patterns):
    """Genera recomendaciones basadas en ML"""
    recommendations = []
    
    # Recomendación basada en mejor formato
    best_format_pattern = next((p for p in patterns if p['type'] == 'best_format_ctr'), None)
    if best_format_pattern:
        recommendations.append({
            'priority': 'high',
            'action': best_format_pattern['recommendation'],
            'reason': best_format_pattern['insight'],
            'expected_impact': '+15-25% CTR promedio',
            'confidence': best_format_pattern['confidence']
        })
    
    # Recomendación basada en mejor ángulo
    best_angle_pattern = next((p for p in patterns if p['type'] == 'best_angle_roi'), None)
    if best_angle_pattern:
        recommendations.append({
            'priority': 'high',
            'action': best_angle_pattern['recommendation'],
            'reason': best_angle_pattern['insight'],
            'expected_impact': '+20-30% ROI promedio',
            'confidence': best_angle_pattern['confidence']
        })
    
    # Recomendación basada en mejor combinación
    best_combo_pattern = next((p for p in patterns if p['type'] == 'best_combo'), None)
    if best_combo_pattern:
        recommendations.append({
            'priority': 'high',
            'action': best_combo_pattern['recommendation'],
            'reason': best_combo_pattern['insight'],
            'expected_impact': '+25-35% ROI en nuevos creativos',
            'confidence': best_combo_pattern['confidence']
        })
    
    return recommendations

def main():
    print("=" * 80)
    print("🤖 Optimización Basada en Machine Learning")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    # Extraer features
    print("🔬 Extrayendo features para ML...")
    features = extract_features(creatives)
    
    if not features:
        print("⚠️  No se encontraron creativos con métricas")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    print(f"✅ {len(features)} creativos con features extraídos")
    print()
    
    # Encontrar patrones
    print("🔍 Analizando patrones...")
    patterns = find_patterns(features)
    
    if patterns:
        print(f"✅ {len(patterns)} patrón(es) identificado(s)")
        print()
        
        print("=" * 80)
        print("📊 Patrones Identificados")
        print("=" * 80)
        print()
        
        for i, pattern in enumerate(patterns, 1):
            confidence_icon = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🔴'
            }.get(pattern.get('confidence', 'low'), '⚪')
            
            print(f"{i}. {confidence_icon} {pattern['insight']}")
            print(f"   💡 {pattern['recommendation']}")
            print()
    
    # Generar recomendaciones ML
    recommendations = generate_ml_recommendations(features, patterns)
    
    if recommendations:
        print("=" * 80)
        print("💡 Recomendaciones Basadas en ML")
        print("=" * 80)
        print()
        
        for i, rec in enumerate(recommendations, 1):
            confidence_icon = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🔴'
            }.get(rec.get('confidence', 'low'), '⚪')
            
            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🔵'
            }.get(rec['priority'], '⚪')
            
            print(f"{i}. {priority_icon} {confidence_icon} {rec['action']}")
            print(f"   📊 Razón: {rec['reason']}")
            print(f"   📈 Impacto esperado: {rec['expected_impact']}")
            print(f"   🎯 Confianza: {rec['confidence']}")
            print()
    
    # Ejemplo de predicción
    print("=" * 80)
    print("🔮 Ejemplo de Predicción")
    print("=" * 80)
    print()
    
    if features:
        # Tomar primer formato/ángulo como ejemplo
        example_format = features[0]['formato']
        example_angle = features[0]['angulo']
        
        prediction = predict_performance(
            {'formato': example_format, 'angulo': example_angle},
            features
        )
        
        if prediction:
            print(f"Predicción para formato {example_format} + ángulo {example_angle}:")
            print(f"  CTR esperado: {prediction['predicted_ctr']:.2f}%")
            print(f"  ROI esperado: {prediction['predicted_roi']:.1f}%")
            if prediction['predicted_cpa'] > 0:
                print(f"  CPA esperado: ${prediction['predicted_cpa']:.2f}")
            print(f"  Confianza: {prediction['confidence']} (basado en {prediction['sample_size']} muestras)")
            print()
    
    print("=" * 80)
    print()
    print("💡 Tip: Cuantos más datos históricos tengas, mejores serán las predicciones")
    print("   y recomendaciones del sistema de ML")

if __name__ == '__main__':
    main()


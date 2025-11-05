#!/usr/bin/env python3
"""
Sistema automatizado de A/B Testing
Identifica variantes, calcula significancia estadística y genera recomendaciones
"""
import csv
import sys
import math
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

def group_variants(creatives):
    """Agrupa creativos en variantes de A/B test"""
    # Agrupar por base name (sin v1, v2, etc.)
    variants = defaultdict(list)
    
    for creative in creatives:
        creative_file = creative.get('creative_file', '')
        utm_content = creative.get('utm_content', '')
        
        # Identificar base name
        base_name = creative_file
        
        # Detectar variantes (v1, v2, v3, etc.)
        if '_v' in creative_file.lower():
            parts = creative_file.rsplit('_v', 1)
            base_name = parts[0]
        
        # Agrupar por base name + formato
        formato = creative.get('formato', '')
        key = f"{base_name}_{formato}"
        
        variants[key].append({
            'creative': creative,
            'variant_id': creative_file,
            'base_name': base_name
        })
    
    # Filtrar solo grupos con múltiples variantes
    test_groups = {k: v for k, v in variants.items() if len(v) >= 2}
    
    return test_groups

def calculate_conversion_rate(clicks, conversions):
    """Calcula tasa de conversión"""
    if clicks == 0:
        return 0
    return (conversions / clicks) * 100

def calculate_statistical_significance(variant_a, variant_b):
    """Calcula significancia estadística entre dos variantes"""
    # Extraer métricas
    clicks_a = float(variant_a.get('clicks', 0) or 0)
    conversions_a = float(variant_a.get('conversions', 0) or 0)
    clicks_b = float(variant_b.get('clicks', 0) or 0)
    conversions_b = float(variant_b.get('conversions', 0) or 0)
    
    if clicks_a == 0 or clicks_b == 0:
        return None
    
    # Tasas de conversión
    rate_a = conversions_a / clicks_a
    rate_b = conversions_b / clicks_b
    
    # Pooled proportion
    pooled_p = (conversions_a + conversions_b) / (clicks_a + clicks_b)
    pooled_q = 1 - pooled_p
    
    # Standard error
    se_a = math.sqrt((pooled_p * pooled_q) / clicks_a)
    se_b = math.sqrt((pooled_p * pooled_q) / clicks_b)
    se_diff = math.sqrt(se_a**2 + se_b**2)
    
    # Z-score
    if se_diff == 0:
        return None
    
    z_score = (rate_b - rate_a) / se_diff
    
    # P-value aproximado (two-tailed)
    # Usando aproximación simple para p-value
    if abs(z_score) >= 2.576:  # 99% confidence
        p_value = 0.01
        significance = 'high'
    elif abs(z_score) >= 1.96:  # 95% confidence
        p_value = 0.05
        significance = 'medium'
    elif abs(z_score) >= 1.645:  # 90% confidence
        p_value = 0.10
        significance = 'low'
    else:
        p_value = 1.0
        significance = 'none'
    
    return {
        'z_score': z_score,
        'p_value': p_value,
        'significance': significance,
        'rate_a': rate_a * 100,
        'rate_b': rate_b * 100,
        'improvement': ((rate_b - rate_a) / rate_a * 100) if rate_a > 0 else 0
    }

def analyze_ab_tests(test_groups):
    """Analiza todos los A/B tests identificados"""
    results = []
    
    for group_name, variants in test_groups.items():
        if len(variants) < 2:
            continue
        
        # Comparar todas las combinaciones
        for i in range(len(variants)):
            for j in range(i + 1, len(variants)):
                variant_a = variants[i]['creative']
                variant_b = variants[j]['creative']
                
                variant_a_id = variants[i]['variant_id']
                variant_b_id = variants[j]['variant_id']
                
                stats = calculate_statistical_significance(variant_a, variant_b)
                
                if stats:
                    # Determinar ganador
                    if stats['improvement'] > 0 and stats['significance'] != 'none':
                        winner = variant_b_id
                        loser = variant_a_id
                    elif stats['improvement'] < 0 and stats['significance'] != 'none':
                        winner = variant_a_id
                        loser = variant_b_id
                    else:
                        winner = None
                        loser = None
                    
                    results.append({
                        'test_name': group_name,
                        'variant_a': variant_a_id,
                        'variant_b': variant_b_id,
                        'winner': winner,
                        'stats': stats,
                        'recommendation': generate_recommendation(stats, winner, variant_a_id, variant_b_id)
                    })
    
    return results

def generate_recommendation(stats, winner, variant_a, variant_b):
    """Genera recomendación basada en resultados"""
    if stats['significance'] == 'none':
        return f"Sin diferencia significativa. Continuar testing con más datos."
    
    if winner:
        improvement = abs(stats['improvement'])
        if stats['significance'] == 'high':
            return f"Ganador claro: {winner} ({improvement:.1f}% mejora, p<0.01). Escalar ganador y pausar {loser if winner == variant_b else variant_b}."
        elif stats['significance'] == 'medium':
            return f"Ganador probable: {winner} ({improvement:.1f}% mejora, p<0.05). Considerar escalar ganador."
        else:
            return f"Tendencia favorable: {winner} ({improvement:.1f}% mejora, p<0.10). Continuar testing."
    else:
        return "Sin ganador claro. Continuar testing."

def main():
    print("=" * 80)
    print("🧪 Sistema Automatizado de A/B Testing")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Agrupar variantes
    print("🔍 Identificando variantes de A/B tests...")
    test_groups = group_variants(creatives)
    
    if not test_groups:
        print("⚠️  No se encontraron grupos de A/B testing")
        print("   Tip: Usa naming convention como creative_v1.svg, creative_v2.svg")
        return
    
    print(f"✅ {len(test_groups)} grupo(s) de A/B testing identificado(s)")
    print()
    
    # Analizar tests
    print("📊 Analizando significancia estadística...")
    results = analyze_ab_tests(test_groups)
    
    if not results:
        print("⚠️  No se pudieron analizar tests (faltan métricas)")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    print(f"✅ {len(results)} comparación(es) analizada(s)")
    print()
    
    # Mostrar resultados
    print("=" * 80)
    print("📊 Resultados de A/B Testing")
    print("=" * 80)
    print()
    
    significant_results = [r for r in results if r['stats']['significance'] != 'none']
    
    if significant_results:
        print(f"🎯 {len(significant_results)} test(s) con resultados significativos:")
        print()
        
        for i, result in enumerate(significant_results[:10], 1):  # Top 10
            stats = result['stats']
            sig_icon = {
                'high': '🟢',
                'medium': '🟡',
                'low': '🔵'
            }.get(stats['significance'], '⚪')
            
            print(f"{i}. {sig_icon} Test: {result['test_name']}")
            print(f"   Variante A: {result['variant_a']} ({stats['rate_a']:.2f}% CVR)")
            print(f"   Variante B: {result['variant_b']} ({stats['rate_b']:.2f}% CVR)")
            print(f"   Mejora: {stats['improvement']:+.1f}%")
            
            if result['winner']:
                print(f"   🏆 Ganador: {result['winner']}")
            
            print(f"   📊 Significancia: {stats['significance']} (p={stats['p_value']:.3f}, z={stats['z_score']:.2f})")
            print(f"   💡 {result['recommendation']}")
            print()
    else:
        print("⚠️  No se encontraron resultados estadísticamente significativos")
        print("   Posibles razones:")
        print("   - Tamaño de muestra insuficiente")
        print("   - Diferencia real muy pequeña")
        print("   - Continuar testing con más datos")
        print()
    
    # Tests no significativos
    non_significant = [r for r in results if r['stats']['significance'] == 'none']
    if non_significant and len(significant_results) < len(results):
        print(f"ℹ️  {len(non_significant)} test(s) sin significancia estadística (continuar testing)")
        print()
    
    # Guardar reporte
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'ab_testing_results_{timestamp}.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Reporte de A/B Testing - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total tests: {len(results)}\n")
        f.write(f"Significativos: {len(significant_results)}\n\n")
        
        for result in significant_results:
            stats = result['stats']
            f.write(f"Test: {result['test_name']}\n")
            f.write(f"  Variante A: {result['variant_a']} ({stats['rate_a']:.2f}% CVR)\n")
            f.write(f"  Variante B: {result['variant_b']} ({stats['rate_b']:.2f}% CVR)\n")
            if result['winner']:
                f.write(f"  Ganador: {result['winner']}\n")
            f.write(f"  Significancia: {stats['significance']} (p={stats['p_value']:.3f})\n")
            f.write(f"  Recomendación: {result['recommendation']}\n\n")
    
    print(f"📄 Reporte guardado: {report_path}")
    print()

if __name__ == '__main__':
    main()


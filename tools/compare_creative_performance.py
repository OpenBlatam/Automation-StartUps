#!/usr/bin/env python3
"""
Compara performance de creativos basado en métricas de LinkedIn Ads
Requiere exportar datos desde LinkedIn Campaign Manager
"""
import csv
import sys
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def load_csv_master():
    """Carga el CSV Master de creativos"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        print(f"❌ CSV Master no encontrado: {csv_path}")
        return None
    
    creatives = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creative_file = row.get('creative_file', '')
            if creative_file:
                creatives[creative_file] = row
    
    return creatives

def load_performance_data(performance_csv_path):
    """Carga datos de performance desde CSV exportado de LinkedIn"""
    if not os.path.exists(performance_csv_path):
        print(f"❌ Archivo de performance no encontrado: {performance_csv_path}")
        print("💡 Exporta datos desde LinkedIn Campaign Manager como CSV")
        return None
    
    performance = {}
    with open(performance_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Buscar utm_content en la URL o nombre del ad
            utm_content = None
            creative_url = row.get('Final URL', row.get('Landing Page URL', ''))
            
            # Extraer utm_content de la URL
            if 'utm_content=' in creative_url:
                utm_content = creative_url.split('utm_content=')[1].split('&')[0]
            elif 'Creative Name' in row:
                # Intentar extraer del nombre del creative
                creative_name = row['Creative Name']
                performance[creative_name] = row
    
    return performance

def analyze_performance_by_format(creatives, performance):
    """Analiza performance por formato"""
    format_stats = defaultdict(lambda: {
        'count': 0,
        'total_clicks': 0,
        'total_impressions': 0,
        'total_spend': 0,
        'total_leads': 0
    })
    
    for creative_file, creative_data in creatives.items():
        formato = creative_data.get('formato', 'unknown')
        utm_content = creative_data.get('utm_content', '')
        
        # Buscar performance data por utm_content
        # (Esto requiere mapeo manual o integración con API)
        format_stats[formato]['count'] += 1
    
    return format_stats

def analyze_performance_by_angle(creatives, performance):
    """Analiza performance por ángulo (metrics, social, urgency)"""
    angle_stats = defaultdict(lambda: {
        'count': 0,
        'ctr_sum': 0,
        'cvr_sum': 0,
        'cpa_sum': 0
    })
    
    for creative_file, creative_data in creatives.items():
        angulo = creative_data.get('angulo', 'unknown')
        utm_content = creative_data.get('utm_content', '')
        
        # Determinar ángulo desde utm_content si no está en CSV
        if angulo == 'unknown' and utm_content:
            if 'metrics' in utm_content:
                angulo = 'metrics'
            elif 'socialproof' in utm_content or 'social' in utm_content:
                angulo = 'socialproof'
            elif 'urgency' in utm_content:
                angulo = 'urgency'
            else:
                angulo = 'base'
        
        angle_stats[angulo]['count'] += 1
    
    return angle_stats

def generate_recommendations(creatives, format_stats, angle_stats):
    """Genera recomendaciones basadas en análisis"""
    recommendations = []
    
    # Analizar distribución de formatos
    total_creatives = len(creatives)
    format_distribution = {fmt: stats['count'] for fmt, stats in format_stats.items()}
    
    # Recomendación: Balancear formatos
    if format_distribution.get('1200x627', 0) > format_distribution.get('1080x1080', 0) * 2:
        recommendations.append({
            'type': 'balance',
            'message': '⚠️ Desbalance en formatos: Tienes más creativos 1200×627 que 1080×1080',
            'action': 'Considera crear más formatos square (1080×1080) para mobile feed'
        })
    
    # Analizar ángulos
    angle_distribution = {angle: stats['count'] for angle, stats in angle_stats.items()}
    
    if angle_distribution.get('metrics', 0) < 3:
        recommendations.append({
            'type': 'missing',
            'message': '📊 Pocos creativos con ángulo "metrics"',
            'action': 'A/B test con más ads enfocados en métricas/resultados'
        })
    
    if angle_distribution.get('socialproof', 0) < 3:
        recommendations.append({
            'type': 'missing',
            'message': '👥 Pocos creativos con ángulo "social proof"',
            'action': 'Añade más testimonios y casos de estudio'
        })
    
    return recommendations

def main():
    print("=" * 80)
    print("📊 Análisis Comparativo de Performance de Creativos")
    print("=" * 80)
    print()
    
    # Cargar CSV Master
    creatives = load_csv_master()
    if not creatives:
        sys.exit(1)
    
    print(f"✅ CSV Master cargado: {len(creatives)} creativos")
    print()
    
    # Análisis por formato
    format_stats = analyze_performance_by_format(creatives, None)
    angle_stats = analyze_performance_by_angle(creatives, None)
    
    print("📊 Distribución por Formato:")
    print("-" * 80)
    for formato, stats in sorted(format_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        percentage = (stats['count'] / len(creatives)) * 100 if creatives else 0
        print(f"  {formato:20} {stats['count']:3} archivos ({percentage:5.1f}%)")
    print()
    
    print("🎯 Distribución por Ángulo:")
    print("-" * 80)
    for angulo, stats in sorted(angle_stats.items(), key=lambda x: x[1]['count'], reverse=True):
        percentage = (stats['count'] / len(creatives)) * 100 if creatives else 0
        print(f"  {angulo:20} {stats['count']:3} archivos ({percentage:5.1f}%)")
    print()
    
    # Generar recomendaciones
    recommendations = generate_recommendations(creatives, format_stats, angle_stats)
    
    if recommendations:
        print("💡 Recomendaciones:")
        print("-" * 80)
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['message']}")
            print(f"   Acción: {rec['action']}")
    else:
        print("✅ Distribución balanceada. No se requieren acciones inmediatas.")
    print()
    
    print("=" * 80)
    print("💡 Para análisis de performance completo:")
    print("   1. Exporta datos desde LinkedIn Campaign Manager")
    print("   2. Guarda como 'linkedin_performance.csv'")
    print("   3. Ejecuta: python3 tools/compare_creative_performance.py linkedin_performance.csv")
    print("=" * 80)

if __name__ == '__main__':
    performance_csv = sys.argv[1] if len(sys.argv) > 1 else None
    
    if performance_csv:
        performance = load_performance_data(performance_csv)
        if performance:
            print(f"✅ Datos de performance cargados: {len(performance)} registros")
    else:
        main()



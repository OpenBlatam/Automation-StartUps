#!/usr/bin/env python3
"""
Cálculo de ROI y optimización automática de presupuesto
Analiza performance y sugiere reasignación de budget para maximizar ROI
"""
import csv
import sys
from pathlib import Path
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

def calculate_roi_metrics(creatives):
    """Calcula métricas de ROI para cada creative"""
    roi_data = []
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        if impressions == 0 or spend == 0:
            continue
        
        # Métricas básicas
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cpc = (spend / clicks) if clicks > 0 else 0
        cpa = (spend / conversions) if conversions > 0 else 0
        
        # Asumir LTV promedio (puede configurarse)
        assumed_ltv = 500  # Valor promedio por conversión
        revenue = conversions * assumed_ltv
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
        roas = (revenue / spend) if spend > 0 else 0
        
        roi_data.append({
            'creative_file': creative.get('creative_file', ''),
            'utm_content': creative.get('utm_content', ''),
            'formato': creative.get('formato', ''),
            'producto': creative.get('producto', ''),
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'conversions': conversions,
            'ctr': ctr,
            'cpc': cpc,
            'cpa': cpa,
            'roi': roi,
            'roas': roas,
            'revenue': revenue,
            'profit': revenue - spend
        })
    
    return roi_data

def optimize_budget_allocation(roi_data, total_budget):
    """Optimiza asignación de presupuesto basado en ROI"""
    if not roi_data:
        return []
    
    # Ordenar por ROI descendente
    sorted_data = sorted(roi_data, key=lambda x: x['roi'], reverse=True)
    
    # Calcular scores de performance
    for item in sorted_data:
        # Score basado en ROI, ROAS y volumen
        roi_score = min(item['roi'] / 100, 3.0)  # Normalizar ROI (máx 300%)
        roas_score = min(item['roas'] / 5, 2.0)  # Normalizar ROAS (máx 5x)
        volume_score = min(item['conversions'] / 50, 1.0)  # Normalizar volumen
        
        # Score combinado (ponderado)
        item['performance_score'] = (
            roi_score * 0.4 +  # ROI es más importante
            roas_score * 0.3 +
            volume_score * 0.3
        )
    
    # Categorizar creativos
    top_performers = [x for x in sorted_data if x['roi'] > 50 and x['conversions'] > 0]
    medium_performers = [x for x in sorted_data if 0 < x['roi'] <= 50]
    poor_performers = [x for x in sorted_data if x['roi'] <= 0 or x['conversions'] == 0]
    
    # Optimizar budget
    optimized_allocation = []
    
    # Top performers: 60% del budget
    top_budget = total_budget * 0.60
    if top_performers:
        budget_per_top = top_budget / len(top_performers)
        for item in top_performers:
            optimized_allocation.append({
                'creative_file': item['creative_file'],
                'current_spend': item['spend'],
                'recommended_spend': budget_per_top,
                'change': budget_per_top - item['spend'],
                'change_pct': ((budget_per_top - item['spend']) / item['spend'] * 100) if item['spend'] > 0 else 100,
                'category': 'top_performer',
                'roi': item['roi'],
                'reason': f"ROI alto ({item['roi']:.1f}%) con {item['conversions']:.0f} conversiones"
            })
    
    # Medium performers: 30% del budget
    medium_budget = total_budget * 0.30
    if medium_performers:
        budget_per_medium = medium_budget / len(medium_performers)
        for item in medium_performers:
            optimized_allocation.append({
                'creative_file': item['creative_file'],
                'current_spend': item['spend'],
                'recommended_spend': budget_per_medium,
                'change': budget_per_medium - item['spend'],
                'change_pct': ((budget_per_medium - item['spend']) / item['spend'] * 100) if item['spend'] > 0 else 100,
                'category': 'medium_performer',
                'roi': item['roi'],
                'reason': f"ROI positivo ({item['roi']:.1f}%) pero necesita optimización"
            })
    
    # Poor performers: 10% del budget (testing mínimo)
    poor_budget = total_budget * 0.10
    if poor_performers:
        budget_per_poor = poor_budget / len(poor_performers)
        for item in poor_performers:
            optimized_allocation.append({
                'creative_file': item['creative_file'],
                'current_spend': item['spend'],
                'recommended_spend': budget_per_poor,
                'change': budget_per_poor - item['spend'],
                'change_pct': ((budget_per_poor - item['spend']) / item['spend'] * 100) if item['spend'] > 0 else -50,
                'category': 'poor_performer',
                'roi': item['roi'],
                'reason': f"ROI bajo ({item['roi']:.1f}%) - reducir budget o pausar"
            })
    
    return optimized_allocation

def generate_recommendations(roi_data, optimized_allocation):
    """Genera recomendaciones estratégicas"""
    recommendations = []
    
    if not roi_data:
        recommendations.append({
            'priority': 'high',
            'action': 'Añadir métricas de performance al CSV Master',
            'reason': 'Sin métricas no se puede calcular ROI',
            'impact': 'Habilitar análisis de ROI y optimización'
        })
        return recommendations
    
    # Análisis de top performers
    top_performers = [x for x in roi_data if x['roi'] > 50]
    if top_performers:
        avg_roi_top = sum(x['roi'] for x in top_performers) / len(top_performers)
        recommendations.append({
            'priority': 'high',
            'action': f'Escalar top {len(top_performers)} creativos con ROI > 50%',
            'reason': f'ROI promedio de {avg_roi_top:.1f}% en top performers',
            'impact': f'Potencial de incrementar ROI total en {avg_roi_top * 0.2:.1f}%'
        })
    
    # Análisis de poor performers
    poor_performers = [x for x in roi_data if x['roi'] <= 0 or x['conversions'] == 0]
    if poor_performers:
        recommendations.append({
            'priority': 'medium',
            'action': f'Revisar o pausar {len(poor_performers)} creativos con ROI negativo',
            'reason': 'Están consumiendo budget sin generar retorno',
            'impact': f'Ahorro potencial de ${sum(x["spend"] for x in poor_performers):,.2f}/período'
        })
    
    # Análisis de budget
    total_current_spend = sum(x['current_spend'] for x in optimized_allocation)
    total_recommended_spend = sum(x['recommended_spend'] for x in optimized_allocation)
    
    if total_current_spend > 0:
        budget_change = total_recommended_spend - total_current_spend
        recommendations.append({
            'priority': 'medium',
            'action': 'Implementar reasignación de budget sugerida',
            'reason': f'Cambio neto de ${budget_change:,.2f} para optimizar ROI',
            'impact': 'Potencial de mejorar ROI promedio en 15-25%'
        })
    
    return recommendations

def main():
    print("=" * 80)
    print("💰 Análisis de ROI y Optimización de Presupuesto")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Calcular ROI
    roi_data = calculate_roi_metrics(creatives)
    
    if not roi_data:
        print("⚠️  No se encontraron creativos con métricas de performance")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    print(f"📊 {len(roi_data)} creativos con métricas de ROI")
    print()
    
    # Calcular totales
    total_spend = sum(x['spend'] for x in roi_data)
    total_revenue = sum(x['revenue'] for x in roi_data)
    total_profit = sum(x['profit'] for x in roi_data)
    total_conversions = sum(x['conversions'] for x in roi_data)
    avg_roi = sum(x['roi'] for x in roi_data) / len(roi_data) if roi_data else 0
    avg_cpa = sum(x['cpa'] for x in roi_data) / len(roi_data) if roi_data else 0
    
    print("=" * 80)
    print("📊 Métricas de ROI Totales")
    print("=" * 80)
    print(f"  Gasto total: ${total_spend:,.2f}")
    print(f"  Ingresos estimados: ${total_revenue:,.2f}")
    print(f"  Ganancia neta: ${total_profit:,.2f}")
    print(f"  ROI promedio: {avg_roi:.2f}%")
    print(f"  Conversiones totales: {total_conversions:.0f}")
    print(f"  CPA promedio: ${avg_cpa:.2f}")
    print()
    
    # Optimizar budget
    total_budget = total_spend * 1.1  # Asumir 10% más de budget disponible
    print(f"💡 Optimizando asignación de budget (${total_budget:,.2f})...")
    print()
    
    optimized_allocation = optimize_budget_allocation(roi_data, total_budget)
    
    # Mostrar optimización
    print("=" * 80)
    print("🎯 Optimización de Presupuesto Sugerida")
    print("=" * 80)
    print()
    
    by_category = defaultdict(list)
    for item in optimized_allocation:
        by_category[item['category']].append(item)
    
    for category in ['top_performer', 'medium_performer', 'poor_performer']:
        items = by_category.get(category, [])
        if not items:
            continue
        
        category_name = {
            'top_performer': '🏆 Top Performers (60% budget)',
            'medium_performer': '🟡 Medium Performers (30% budget)',
            'poor_performer': '🔴 Poor Performers (10% budget - testing)'
        }.get(category, category)
        
        print(category_name)
        print("-" * 80)
        
        for item in items[:5]:  # Mostrar top 5
            change_icon = "📈" if item['change'] > 0 else "📉"
            print(f"  {change_icon} {item['creative_file']}")
            print(f"     Actual: ${item['current_spend']:,.2f} → Recomendado: ${item['recommended_spend']:,.2f}")
            print(f"     Cambio: {item['change_pct']:+.1f}% (${item['change']:,.2f})")
            print(f"     ROI: {item['roi']:.1f}% | {item['reason']}")
            print()
        
        if len(items) > 5:
            print(f"     ... y {len(items) - 5} más")
            print()
    
    # Generar recomendaciones
    recommendations = generate_recommendations(roi_data, optimized_allocation)
    
    if recommendations:
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
            
            print(f"{i}. {priority_icon} [{rec['priority'].upper()}] {rec['action']}")
            print(f"   📊 Razón: {rec['reason']}")
            print(f"   📈 Impacto: {rec['impact']}")
            print()
    
    # Guardar reporte
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'roi_optimization_{timestamp}.csv'
    
    with open(report_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['creative_file', 'current_spend', 'recommended_spend', 'change', 'change_pct', 'category', 'roi', 'reason'])
        writer.writeheader()
        writer.writerows(optimized_allocation)
    
    print(f"📄 Reporte de optimización guardado: {report_path}")
    print()

if __name__ == '__main__':
    main()


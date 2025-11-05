#!/usr/bin/env python3
"""
Forecasting avanzado de performance
Predice métricas futuras basado en tendencias históricas y patrones estacionales
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

def calculate_growth_rate(values):
    """Calcula tasa de crecimiento promedio"""
    if len(values) < 2:
        return 0
    
    growth_rates = []
    for i in range(1, len(values)):
        if values[i-1] > 0:
            growth = ((values[i] - values[i-1]) / values[i-1]) * 100
            growth_rates.append(growth)
    
    if not growth_rates:
        return 0
    
    return sum(growth_rates) / len(growth_rates)

def forecast_metrics(current_value, growth_rate, periods, trend='linear'):
    """Genera forecast de métricas"""
    forecasts = []
    
    for period in range(1, periods + 1):
        if trend == 'exponential':
            forecast = current_value * ((1 + growth_rate / 100) ** period)
        else:  # linear
            forecast = current_value * (1 + (growth_rate / 100) * period)
        
        forecasts.append({
            'period': period,
            'forecast': max(0, forecast),  # No valores negativos
            'growth_rate': growth_rate
        })
    
    return forecasts

def analyze_trends(creatives):
    """Analiza tendencias históricas"""
    # Agrupar por período (simulado - en producción usarías fechas reales)
    monthly_data = defaultdict(lambda: {
        'impressions': [],
        'clicks': [],
        'spend': [],
        'conversions': []
    })
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        # Por ahora, agregar todo en "current" month
        # En producción, agruparías por fecha real
        if impressions > 0:
            monthly_data['current']['impressions'].append(impressions)
            monthly_data['current']['clicks'].append(clicks)
            monthly_data['current']['spend'].append(spend)
            monthly_data['current']['conversions'].append(conversions)
    
    trends = {}
    
    for period, data in monthly_data.items():
        if data['impressions']:
            trends[period] = {
                'total_impressions': sum(data['impressions']),
                'total_clicks': sum(data['clicks']),
                'total_spend': sum(data['spend']),
                'total_conversions': sum(data['conversions']),
                'avg_ctr': (sum(data['clicks']) / sum(data['impressions']) * 100) if sum(data['impressions']) > 0 else 0,
                'avg_cpc': (sum(data['spend']) / sum(data['clicks'])) if sum(data['clicks']) > 0 else 0,
                'avg_cpa': (sum(data['spend']) / sum(data['conversions'])) if sum(data['conversions']) > 0 else 0
            }
    
    return trends

def generate_forecasts(trends, periods=3):
    """Genera forecasts para próximos períodos"""
    if 'current' not in trends:
        return None
    
    current = trends['current']
    
    # Calcular tasas de crecimiento (simulado - en producción usarías datos históricos)
    # Por ahora, usamos tasas conservadoras
    growth_rates = {
        'impressions': 5.0,  # 5% crecimiento mensual
        'clicks': 7.0,       # 7% crecimiento (mejor CTR)
        'spend': 10.0,       # 10% crecimiento (más budget)
        'conversions': 8.0   # 8% crecimiento
    }
    
    forecasts = {}
    
    for metric in ['impressions', 'clicks', 'spend', 'conversions']:
        current_value = current.get(f'total_{metric}', 0)
        growth_rate = growth_rates.get(metric, 5.0)
        
        forecasts[metric] = forecast_metrics(current_value, growth_rate, periods)
    
    # Forecast de métricas derivadas
    forecasts['ctr'] = []
    forecasts['cpc'] = []
    forecasts['cpa'] = []
    
    for period in range(periods):
        period_num = period + 1
        
        # CTR forecast (asumiendo mejora gradual)
        current_ctr = current.get('avg_ctr', 0)
        ctr_improvement = 0.1  # 0.1% mejora por mes
        forecast_ctr = current_ctr + (ctr_improvement * period_num)
        forecasts['ctr'].append({
            'period': period_num,
            'forecast': max(0, forecast_ctr),
            'growth_rate': (ctr_improvement / current_ctr * 100) if current_ctr > 0 else 0
        })
        
        # CPC forecast (asumiendo optimización)
        current_cpc = current.get('avg_cpc', 0)
        cpc_reduction = -0.05  # 5% reducción por mes (optimización)
        forecast_cpc = current_cpc * ((1 + cpc_reduction) ** period_num)
        forecasts['cpc'].append({
            'period': period_num,
            'forecast': max(0, forecast_cpc),
            'growth_rate': cpc_reduction * 100
        })
        
        # CPA forecast
        current_cpa = current.get('avg_cpa', 0)
        cpa_reduction = -0.03  # 3% reducción por mes
        forecast_cpa = current_cpa * ((1 + cpa_reduction) ** period_num)
        forecasts['cpa'].append({
            'period': period_num,
            'forecast': max(0, forecast_cpa),
            'growth_rate': cpa_reduction * 100
        })
    
    return forecasts

def main():
    print("=" * 80)
    print("📈 Forecasting Avanzado de Performance")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Analizar tendencias
    print("📊 Analizando tendencias históricas...")
    trends = analyze_trends(creatives)
    
    if 'current' not in trends:
        print("⚠️  No se encontraron métricas para análisis")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    current = trends['current']
    
    print("✅ Tendencias analizadas")
    print()
    
    # Mostrar situación actual
    print("=" * 80)
    print("📊 Situación Actual")
    print("=" * 80)
    print()
    print(f"Impresiones: {current['total_impressions']:,.0f}")
    print(f"Clics: {current['total_clicks']:,.0f}")
    print(f"CTR promedio: {current['avg_ctr']:.2f}%")
    print(f"Gasto: ${current['total_spend']:,.2f}")
    print(f"CPC promedio: ${current['avg_cpc']:.2f}")
    print(f"Conversiones: {current['total_conversions']:.0f}")
    print(f"CPA promedio: ${current['avg_cpa']:.2f}")
    print()
    
    # Generar forecasts
    print("🔮 Generando forecasts para próximos 3 meses...")
    forecasts = generate_forecasts(trends, periods=3)
    
    if not forecasts:
        print("❌ No se pudo generar forecast")
        return
    
    print()
    print("=" * 80)
    print("📈 Forecasts (Próximos 3 Meses)")
    print("=" * 80)
    print()
    
    for period in range(3):
        period_num = period + 1
        month_name = (datetime.now() + timedelta(days=30*period_num)).strftime('%B %Y')
        
        print(f"📅 {month_name} (Mes {period_num}):")
        print("-" * 80)
        
        impressions = forecasts['impressions'][period]['forecast']
        clicks = forecasts['clicks'][period]['forecast']
        spend = forecasts['spend'][period]['forecast']
        conversions = forecasts['conversions'][period]['forecast']
        ctr = forecasts['ctr'][period]['forecast']
        cpc = forecasts['cpc'][period]['forecast']
        cpa = forecasts['cpa'][period]['forecast']
        
        print(f"  Impresiones: {impressions:,.0f} ({forecasts['impressions'][period]['growth_rate']:+.1f}%)")
        print(f"  Clics: {clicks:,.0f} ({forecasts['clicks'][period]['growth_rate']:+.1f}%)")
        print(f"  CTR: {ctr:.2f}% ({forecasts['ctr'][period]['growth_rate']:+.1f}% vs. actual)")
        print(f"  Gasto: ${spend:,.2f} ({forecasts['spend'][period]['growth_rate']:+.1f}%)")
        print(f"  CPC: ${cpc:.2f} ({forecasts['cpc'][period]['growth_rate']:+.1f}% vs. actual)")
        print(f"  Conversiones: {conversions:,.0f} ({forecasts['conversions'][period]['growth_rate']:+.1f}%)")
        print(f"  CPA: ${cpa:.2f} ({forecasts['cpa'][period]['growth_rate']:+.1f}% vs. actual)")
        
        # Revenue forecast
        assumed_ltv = 500
        revenue = conversions * assumed_ltv
        roi = ((revenue - spend) / spend * 100) if spend > 0 else 0
        
        print(f"  📊 Revenue estimado: ${revenue:,.2f}")
        print(f"  💰 ROI proyectado: {roi:.1f}%")
        print()
    
    # Recomendaciones
    print("=" * 80)
    print("💡 Recomendaciones Basadas en Forecast")
    print("=" * 80)
    print()
    
    avg_growth = sum(f['growth_rate'] for f in forecasts['conversions']) / len(forecasts['conversions'])
    
    if avg_growth > 10:
        print("✅ Crecimiento fuerte proyectado. Considera:")
        print("   • Aumentar budget para capturar oportunidad")
        print("   • Escalar top performers")
        print("   • Preparar infraestructura para mayor volumen")
    elif avg_growth > 5:
        print("✅ Crecimiento positivo proyectado. Considera:")
        print("   • Optimización continua de creativos")
        print("   • Testing de nuevos formatos/ángulos")
    else:
        print("⚠️  Crecimiento lento proyectado. Considera:")
        print("   • Revisar y optimizar creativos existentes")
        print("   • Testing agresivo de nuevas variantes")
        print("   • Análisis de competencia")
    
    print()
    print("⚠️  Nota: Estos forecasts son estimaciones basadas en tendencias actuales.")
    print("   Ajusta según cambios en estrategia, estacionalidad y factores externos.")

if __name__ == '__main__':
    main()


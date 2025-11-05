#!/usr/bin/env python3
"""
Análisis de tendencias temporales y estacionalidad en creativos
Identifica patrones de creación, uso y performance por periodo
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta
import re

def parse_date(filename):
    """Extrae fecha del filename si está presente"""
    # Patrones comunes: YYYYMMDD, YYYY-MM-DD, etc.
    patterns = [
        r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
        r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        r'(\d{2})(\d{2})(\d{4})',  # MMDDYYYY
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            try:
                groups = match.groups()
                if len(groups) == 3:
                    # Intentar diferentes formatos
                    for fmt in ['%Y%m%d', '%Y-%m-%d', '%m%d%Y']:
                        try:
                            date_str = ''.join(groups)
                            if fmt == '%Y-%m-%d':
                                date_str = '-'.join(groups)
                            return datetime.strptime(date_str, fmt)
                        except:
                            continue
            except:
                continue
    
    return None

def get_file_modification_date(file_path):
    """Obtiene fecha de modificación del archivo"""
    try:
        return datetime.fromtimestamp(file_path.stat().st_mtime)
    except:
        return None

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
        for creatives_row in reader:
            creatives.append(creatives_row)
    
    return creatives

def analyze_temporal_patterns(creatives):
    """Analiza patrones temporales"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    assets_dir = root_dir / 'assets'
    
    by_month = defaultdict(list)
    by_weekday = defaultdict(int)
    by_hour = defaultdict(int)
    recent_activity = []
    
    now = datetime.now()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)
    
    # Analizar creativos del CSV
    for creative in creatives:
        creative_file = creative.get('creative_file', '')
        if not creative_file:
            continue
        
        # Intentar obtener fecha del filename
        file_date = parse_date(creative_file)
        
        # Si no hay fecha en filename, intentar obtener fecha de modificación
        if not file_date:
            file_path = None
            for ext in ['.svg', '.png', '.jpg', '.jpeg']:
                test_path = assets_dir / 'linkedin' / creative_file.replace('.svg', ext)
                if test_path.exists():
                    file_path = test_path
                    break
            
            if file_path:
                file_date = get_file_modification_date(file_path)
        
        if file_date:
            by_month[file_date.strftime('%Y-%m')].append(creative)
            by_weekday[file_date.strftime('%A')] += 1
            by_hour[file_date.hour] += 1
            
            if file_date >= last_month:
                recent_activity.append({
                    'date': file_date,
                    'creative': creative
                })
    
    # Calcular estadísticas
    total_months = len(by_month)
    avg_per_month = len(creatives) / total_months if total_months > 0 else 0
    
    # Meses más productivos
    top_months = sorted(by_month.items(), key=lambda x: len(x[1]), reverse=True)[:5]
    
    # Días más productivos
    top_weekdays = sorted(by_weekday.items(), key=lambda x: x[1], reverse=True)
    
    # Horas más productivas
    top_hours = sorted(by_hour.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Actividad reciente
    current_month_count = len([a for a in recent_activity if a['date'] >= (now - timedelta(days=30))])
    last_month_count = len([a for a in recent_activity if a['date'] >= last_month - timedelta(days=30) and a['date'] < last_month])
    
    return {
        'by_month': dict(by_month),
        'by_weekday': dict(by_weekday),
        'by_hour': dict(by_hour),
        'top_months': top_months,
        'top_weekdays': top_weekdays,
        'top_hours': top_hours,
        'avg_per_month': avg_per_month,
        'current_month_count': current_month_count,
        'last_month_count': last_month_count,
        'total_months': total_months,
        'recent_activity': recent_activity
    }

def detect_seasonal_patterns(patterns):
    """Detecta patrones estacionales"""
    insights = []
    
    # Comparar actividad actual vs. mes anterior
    if patterns['current_month_count'] > 0 and patterns['last_month_count'] > 0:
        change = ((patterns['current_month_count'] - patterns['last_month_count']) / patterns['last_month_count']) * 100
        
        if change > 20:
            insights.append({
                'type': 'trend',
                'message': '📈 Crecimiento acelerado',
                'detail': f"+{change:.1f}% vs. mes anterior ({patterns['current_month_count']} vs. {patterns['last_month_count']})",
                'recommendation': 'Mantén el ritmo actual de producción'
            })
        elif change < -20:
            insights.append({
                'type': 'warning',
                'message': '📉 Disminución de actividad',
                'detail': f"{change:.1f}% vs. mes anterior ({patterns['current_month_count']} vs. {patterns['last_month_count']})",
                'recommendation': 'Considera aumentar producción de creativos'
            })
    
    # Días más productivos
    if patterns['top_weekdays']:
        best_day = patterns['top_weekdays'][0]
        insights.append({
            'type': 'info',
            'message': '📅 Día más productivo',
            'detail': f"{best_day[0]}: {best_day[1]} creativos creados",
            'recommendation': f'Planifica sesiones de creación los {best_day[0]}s'
        })
    
    # Horas más productivas
    if patterns['top_hours']:
        best_hour = patterns['top_hours'][0]
        hour_str = f"{best_hour[0]:02d}:00"
        insights.append({
            'type': 'info',
            'message': '⏰ Hora más productiva',
            'detail': f"{hour_str}: {best_hour[1]} creativos creados",
            'recommendation': f'Programa bloques de creación alrededor de {hour_str}'
        })
    
    return insights

def generate_forecast(patterns):
    """Genera forecast de producción necesaria"""
    if patterns['avg_per_month'] == 0:
        return None
    
    # Basado en promedio histórico
    forecast_next_month = int(patterns['avg_per_month'] * 1.1)  # +10% buffer
    
    # Basado en tendencia reciente
    if patterns['current_month_count'] > 0:
        growth_rate = patterns['current_month_count'] / patterns['avg_per_month'] if patterns['avg_per_month'] > 0 else 1
        forecast_trend = int(patterns['current_month_count'] * growth_rate)
    else:
        forecast_trend = forecast_next_month
    
    # Usar el mayor de los dos
    forecast = max(forecast_next_month, forecast_trend)
    
    return {
        'next_month': forecast,
        'based_on': 'historical_average' if forecast == forecast_next_month else 'recent_trend',
        'current_pace': patterns['current_month_count'],
        'on_track': patterns['current_month_count'] >= (forecast * 0.8)  # 80% del forecast
    }

def main():
    print("=" * 80)
    print("📊 Análisis de Tendencias Temporales")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Analizar patrones
    patterns = analyze_temporal_patterns(creatives)
    
    # Mostrar estadísticas por mes
    print("📅 Actividad por Mes:")
    print("-" * 80)
    
    if patterns['top_months']:
        for month, creatives_list in patterns['top_months']:
            print(f"  {month}: {len(creatives_list)} creativos")
    else:
        print("  ℹ️  No se detectaron fechas en los creativos")
    
    print()
    print(f"📈 Promedio mensual: {patterns['avg_per_month']:.1f} creativos/mes")
    print()
    
    # Actividad reciente
    print("🕐 Actividad Reciente:")
    print("-" * 80)
    print(f"  Mes actual: {patterns['current_month_count']} creativos")
    print(f"  Mes anterior: {patterns['last_month_count']} creativos")
    
    if patterns['current_month_count'] > patterns['last_month_count']:
        change = ((patterns['current_month_count'] - patterns['last_month_count']) / patterns['last_month_count']) * 100 if patterns['last_month_count'] > 0 else 0
        print(f"  📈 Cambio: +{change:.1f}%")
    elif patterns['last_month_count'] > 0:
        change = ((patterns['current_month_count'] - patterns['last_month_count']) / patterns['last_month_count']) * 100
        print(f"  📉 Cambio: {change:.1f}%")
    
    print()
    
    # Días y horas más productivos
    if patterns['top_weekdays']:
        print("📅 Días Más Productivos:")
        print("-" * 80)
        for day, count in patterns['top_weekdays'][:5]:
            print(f"  {day:12}: {count:3} creativos")
        print()
    
    if patterns['top_hours']:
        print("⏰ Horas Más Productivas:")
        print("-" * 80)
        for hour, count in patterns['top_hours']:
            hour_str = f"{hour:02d}:00"
            print(f"  {hour_str}: {count:3} creativos")
        print()
    
    # Detectar patrones
    insights = detect_seasonal_patterns(patterns)
    
    if insights:
        print("💡 Insights & Recomendaciones:")
        print("-" * 80)
        for insight in insights:
            icon = {
                'trend': '📈',
                'warning': '⚠️',
                'info': 'ℹ️'
            }.get(insight['type'], '•')
            
            print(f"\n{icon} {insight['message']}")
            print(f"   {insight['detail']}")
            print(f"   💡 {insight['recommendation']}")
        print()
    
    # Forecast
    forecast = generate_forecast(patterns)
    if forecast:
        print("🔮 Forecast Próximo Mes:")
        print("-" * 80)
        print(f"  Meta sugerida: {forecast['next_month']} creativos")
        print(f"  Basado en: {forecast['based_on']}")
        print(f"  Ritmo actual: {forecast['current_pace']} creativos este mes")
        
        if forecast['on_track']:
            print("  ✅ En camino de cumplir meta")
        else:
            needed = max(0, forecast['next_month'] - forecast['current_pace'])
            print(f"  ⚠️  Necesitas crear {needed} creativos más este mes para cumplir meta")
        print()
    
    print("=" * 80)
    print()
    print("💡 Tip: Añade fechas a los nombres de archivos (YYYYMMDD) para análisis más preciso")

if __name__ == '__main__':
    main()


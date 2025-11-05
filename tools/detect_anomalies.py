#!/usr/bin/env python3
"""
Detección de anomalías en performance
Identifica cambios inusuales en métricas que requieren atención
"""
import csv
import sys
import statistics
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

def calculate_statistics(creatives):
    """Calcula estadísticas base para detección de anomalías"""
    metrics = {
        'ctr': [],
        'cpc': [],
        'cpa': [],
        'spend': [],
        'conversions': []
    }
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        if impressions > 0:
            ctr = (clicks / impressions * 100)
            metrics['ctr'].append(ctr)
        
        if clicks > 0:
            cpc = (spend / clicks)
            metrics['cpc'].append(cpc)
        
        if conversions > 0:
            cpa = (spend / conversions)
            metrics['cpa'].append(cpa)
        
        if spend > 0:
            metrics['spend'].append(spend)
            metrics['conversions'].append(conversions)
    
    # Calcular medianas y desviaciones
    stats = {}
    for metric_name, values in metrics.items():
        if len(values) >= 3:  # Necesitamos al menos 3 valores
            stats[metric_name] = {
                'median': statistics.median(values),
                'mean': statistics.mean(values),
                'stdev': statistics.stdev(values) if len(values) > 1 else 0,
                'values': values
            }
        else:
            stats[metric_name] = None
    
    return stats

def detect_anomalies(creatives, stats):
    """Detecta anomalías en creativos individuales"""
    anomalies = []
    
    for creative in creatives:
        impressions = float(creative.get('impressions', 0) or 0)
        clicks = float(creative.get('clicks', 0) or 0)
        spend = float(creative.get('spend', 0) or 0)
        conversions = float(creative.get('conversions', 0) or 0)
        
        if impressions == 0:
            continue
        
        creative_anomalies = []
        
        # Anomalía en CTR
        if stats.get('ctr'):
            ctr = (clicks / impressions * 100)
            ctr_median = stats['ctr']['median']
            ctr_stdev = stats['ctr']['stdev']
            
            # CTR muy bajo (2 desviaciones estándar por debajo)
            if ctr < (ctr_median - 2 * ctr_stdev) and impressions > 1000:
                creative_anomalies.append({
                    'type': 'low_ctr',
                    'metric': 'CTR',
                    'value': ctr,
                    'expected': ctr_median,
                    'severity': 'high',
                    'message': f"CTR muy bajo ({ctr:.2f}% vs. promedio {ctr_median:.2f}%)"
                })
            
            # CTR muy alto (posible error o éxito excepcional)
            elif ctr > (ctr_median + 3 * ctr_stdev):
                creative_anomalies.append({
                    'type': 'high_ctr',
                    'metric': 'CTR',
                    'value': ctr,
                    'expected': ctr_median,
                    'severity': 'medium',
                    'message': f"CTR excepcionalmente alto ({ctr:.2f}% vs. promedio {ctr_median:.2f}%) - verificar"
                })
        
        # Anomalía en CPC
        if stats.get('cpc') and clicks > 0:
            cpc = (spend / clicks)
            cpc_median = stats['cpc']['median']
            cpc_stdev = stats['cpc']['stdev']
            
            # CPC muy alto
            if cpc > (cpc_median + 2 * cpc_stdev):
                creative_anomalies.append({
                    'type': 'high_cpc',
                    'metric': 'CPC',
                    'value': cpc,
                    'expected': cpc_median,
                    'severity': 'high',
                    'message': f"CPC muy alto (${cpc:.2f} vs. promedio ${cpc_median:.2f})"
                })
        
        # Anomalía en CPA
        if stats.get('cpa') and conversions > 0:
            cpa = (spend / conversions)
            cpa_median = stats['cpa']['median']
            cpa_stdev = stats['cpa']['stdev']
            
            # CPA muy alto
            if cpa > (cpa_median + 2 * cpa_stdev):
                creative_anomalies.append({
                    'type': 'high_cpa',
                    'metric': 'CPA',
                    'value': cpa,
                    'expected': cpa_median,
                    'severity': 'high',
                    'message': f"CPA muy alto (${cpa:.2f} vs. promedio ${cpa_median:.2f})"
                })
        
        # Anomalía en conversiones (drops súbitos)
        if stats.get('conversions'):
            conversions_median = stats['conversions']['median']
            if conversions > 0 and conversions < (conversions_median * 0.3) and impressions > 5000:
                creative_anomalies.append({
                    'type': 'low_conversions',
                    'metric': 'Conversions',
                    'value': conversions,
                    'expected': conversions_median,
                    'severity': 'high',
                    'message': f"Conversiones muy bajas ({conversions:.0f} vs. esperado {conversions_median:.0f})"
                })
        
        if creative_anomalies:
            anomalies.append({
                'creative_file': creative.get('creative_file', ''),
                'utm_content': creative.get('utm_content', ''),
                'anomalies': creative_anomalies
            })
    
    return anomalies

def main():
    print("=" * 80)
    print("🔍 Detección de Anomalías en Performance")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Analizando {len(creatives)} creativos...")
    print()
    
    # Calcular estadísticas
    print("📊 Calculando estadísticas base...")
    stats = calculate_statistics(creatives)
    
    if not any(stats.values()):
        print("⚠️  No hay suficientes métricas para análisis de anomalías")
        print("   Ejecuta primero: python3 tools/analyze_real_time_performance.py")
        return
    
    print("✅ Estadísticas calculadas")
    print()
    
    # Detectar anomalías
    print("🔍 Detectando anomalías...")
    anomalies = detect_anomalies(creatives, stats)
    
    if not anomalies:
        print("✅ No se detectaron anomalías")
        print("   Todos los creativos están dentro de rangos normales")
        return
    
    print(f"⚠️  {len(anomalies)} creativo(s) con anomalías detectadas")
    print()
    
    # Agrupar por severidad
    high_severity = []
    medium_severity = []
    
    for item in anomalies:
        for anomaly in item['anomalies']:
            if anomaly['severity'] == 'high':
                high_severity.append((item, anomaly))
            else:
                medium_severity.append((item, anomaly))
    
    # Mostrar anomalías
    print("=" * 80)
    print("🚨 Anomalías Detectadas")
    print("=" * 80)
    print()
    
    if high_severity:
        print("🔴 Alta Severidad:")
        print("-" * 80)
        for item, anomaly in high_severity[:10]:
            print(f"  • {item['creative_file']}")
            print(f"    {anomaly['message']}")
            print(f"    Valor: {anomaly['value']:.2f} | Esperado: ~{anomaly['expected']:.2f}")
            print()
    
    if medium_severity:
        print("🟡 Media Severidad:")
        print("-" * 80)
        for item, anomaly in medium_severity[:10]:
            print(f"  • {item['creative_file']}")
            print(f"    {anomaly['message']}")
            print()
    
    # Guardar reporte
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'anomalies_{timestamp}.txt'
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"Reporte de Anomalías - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total anomalías: {len(anomalies)}\n")
        f.write(f"Alta severidad: {len(high_severity)}\n")
        f.write(f"Media severidad: {len(medium_severity)}\n\n")
        
        if high_severity:
            f.write("Alta Severidad:\n")
            for item, anomaly in high_severity:
                f.write(f"- {item['creative_file']}: {anomaly['message']}\n")
        
        if medium_severity:
            f.write("\nMedia Severidad:\n")
            for item, anomaly in medium_severity:
                f.write(f"- {item['creative_file']}: {anomaly['message']}\n")
    
    print(f"📄 Reporte guardado: {report_path}")
    print()
    
    # Recomendaciones
    print("💡 Recomendaciones:")
    if high_severity:
        print("  1. Revisar creativos con anomalías de alta severidad")
        print("  2. Considerar pausar o optimizar creativos con métricas fuera de rango")
        print("  3. Investigar causas de drops en performance")
    print()

if __name__ == '__main__':
    main()


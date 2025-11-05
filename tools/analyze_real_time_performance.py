#!/usr/bin/env python3
"""
Análisis de performance en tiempo real
Conecta con APIs de LinkedIn/Google Analytics para obtener métricas actuales
"""
import sys
import csv
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

def load_config():
    """Carga configuración de APIs"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    config_path = root_dir / '.api_config.json'
    
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def create_config_template():
    """Crea template de configuración"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    config_path = root_dir / '.api_config.json'
    
    template = {
        "linkedin": {
            "access_token": "",
            "account_id": "",
            "enabled": False
        },
        "ga4": {
            "property_id": "",
            "credentials_path": "",
            "enabled": False
        },
        "update_csv": True,
        "date_range_days": 30
    }
    
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Template de configuración creado: {config_path}")
        print("   Edita el archivo con tus credenciales")
    else:
        print(f"⚠️  Configuración ya existe: {config_path}")
    
    return template

def fetch_linkedin_metrics(config, utm_contents, days=30):
    """Obtiene métricas de LinkedIn Campaign Manager"""
    if not config.get('linkedin', {}).get('enabled'):
        return None
    
    if not REQUESTS_AVAILABLE:
        print("⚠️  requests no instalado. Instala con: pip install requests")
        return None
    
    access_token = config['linkedin']['access_token']
    account_id = config['linkedin']['account_id']
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    url = "https://api.linkedin.com/v2/adAnalyticsV2"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Restli-Protocol-Version': '2.0.0'
    }
    
    params = {
        'q': 'analytics',
        'pivot': 'CREATIVE',
        'timeGranularity': 'DAILY',
        'dateRange.start.day': start_date.day,
        'dateRange.start.month': start_date.month,
        'dateRange.start.year': start_date.year,
        'dateRange.end.day': end_date.day,
        'dateRange.end.month': end_date.month,
        'dateRange.end.year': end_date.year,
        'accounts[0]': f'urn:li:sponsoredAccount:{account_id}',
        'fields': 'impressions,clicks,ctr,spend,conversions,creativeId'
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            # Procesar y mapear a utm_content
            metrics = {}
            for element in data.get('elements', []):
                creative_id = element.get('creativeId', '')
                # Aquí necesitarías mapear creative_id a utm_content
                # Por ahora, usamos creative_id como key
                metrics[creative_id] = {
                    'impressions': element.get('impressions', 0),
                    'clicks': element.get('clicks', 0),
                    'ctr': element.get('ctr', 0),
                    'spend': element.get('spend', 0),
                    'conversions': element.get('conversions', 0)
                }
            return metrics
        else:
            print(f"❌ Error LinkedIn API: {response.status_code} - {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo métricas de LinkedIn: {e}")
        return None

def update_csv_with_metrics(csv_path, metrics_dict):
    """Actualiza CSV Master con métricas de performance"""
    creatives = []
    fieldnames = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        creatives = list(reader)
    
    # Añadir campos de métricas si no existen
    metric_fields = ['impressions', 'clicks', 'ctr', 'spend', 'conversions', 'last_updated']
    for field in metric_fields:
        if field not in fieldnames:
            fieldnames.append(field)
    
    updated_count = 0
    
    for creative in creatives:
        utm_content = creative.get('utm_content', '')
        creative_file = creative.get('creative_file', '')
        
        # Buscar métricas por utm_content o creative_file
        metrics = None
        
        # Intentar encontrar por utm_content
        if utm_content in metrics_dict:
            metrics = metrics_dict[utm_content]
        else:
            # Intentar buscar por creative_id si está disponible
            # Por ahora, simulamos actualización
            pass
        
        # Actualizar si encontramos métricas
        if metrics:
            creative['impressions'] = str(metrics.get('impressions', ''))
            creative['clicks'] = str(metrics.get('clicks', ''))
            creative['ctr'] = f"{metrics.get('ctr', 0):.4f}"
            creative['spend'] = str(metrics.get('spend', ''))
            creative['conversions'] = str(metrics.get('conversions', ''))
            creative['last_updated'] = datetime.now().isoformat()
            updated_count += 1
        else:
            # Asegurar que campos existan
            for field in metric_fields:
                if field not in creative:
                    creative[field] = ''
    
    # Guardar CSV actualizado
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(creatives)
    
    return updated_count

def analyze_performance_trends(csv_path):
    """Analiza tendencias de performance"""
    creatives = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        creatives = list(reader)
    
    # Filtrar creativos con métricas
    creatives_with_metrics = [
        c for c in creatives 
        if c.get('impressions') and c.get('impressions').strip()
    ]
    
    if not creatives_with_metrics:
        print("ℹ️  No hay métricas de performance disponibles")
        return
    
    # Calcular estadísticas
    total_impressions = sum(int(float(c.get('impressions', 0))) for c in creatives_with_metrics)
    total_clicks = sum(int(float(c.get('clicks', 0))) for c in creatives_with_metrics)
    total_spend = sum(float(c.get('spend', 0)) for c in creatives_with_metrics)
    total_conversions = sum(int(float(c.get('conversions', 0))) for c in creatives_with_metrics)
    
    avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
    
    # Top performers
    top_by_ctr = sorted(
        creatives_with_metrics,
        key=lambda x: float(x.get('ctr', 0)),
        reverse=True
    )[:5]
    
    top_by_conversions = sorted(
        creatives_with_metrics,
        key=lambda x: int(float(x.get('conversions', 0))),
        reverse=True
    )[:5]
    
    print("=" * 80)
    print("📊 Análisis de Performance en Tiempo Real")
    print("=" * 80)
    print()
    
    print(f"📈 Métricas Totales ({len(creatives_with_metrics)} creativos con datos):")
    print(f"  Impresiones: {total_impressions:,}")
    print(f"  Clics: {total_clicks:,}")
    print(f"  CTR promedio: {avg_ctr:.2f}%")
    print(f"  Gasto total: ${total_spend:,.2f}")
    print(f"  Conversiones: {total_conversions:,}")
    print(f"  CPA promedio: ${avg_cpa:.2f}")
    print()
    
    print("🏆 Top 5 por CTR:")
    for i, creative in enumerate(top_by_ctr, 1):
        ctr = float(creative.get('ctr', 0))
        impressions = int(float(creative.get('impressions', 0)))
        clicks = int(float(creative.get('clicks', 0)))
        print(f"  {i}. {creative.get('creative_file', 'N/A')}: {ctr:.2f}% ({clicks}/{impressions:,})")
    print()
    
    print("🏆 Top 5 por Conversiones:")
    for i, creative in enumerate(top_by_conversions, 1):
        conversions = int(float(creative.get('conversions', 0)))
        spend = float(creative.get('spend', 0))
        cpa = (spend / conversions) if conversions > 0 else 0
        print(f"  {i}. {creative.get('creative_file', 'N/A')}: {conversions} conversiones (CPA: ${cpa:.2f})")
    print()

def main():
    print("=" * 80)
    print("📊 Análisis de Performance en Tiempo Real")
    print("=" * 80)
    print()
    
    if not REQUESTS_AVAILABLE:
        print("⚠️  requests no instalado. Instala con: pip install requests")
        print("   Funcionalidad limitada sin conexión a APIs")
        print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        print("❌ CSV Master no encontrado")
        return
    
    # Cargar configuración
    config = load_config()
    
    if not config:
        print("⚠️  No se encontró configuración de APIs")
        response = input("¿Crear template de configuración? (s/n): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            create_config_template()
        print()
        print("ℹ️  Continuando con análisis de datos locales...")
        analyze_performance_trends(csv_path)
        return
    
    # Obtener métricas de APIs si están configuradas
    metrics_dict = {}
    
    if config.get('linkedin', {}).get('enabled'):
        print("📡 Obteniendo métricas de LinkedIn...")
        days = config.get('date_range_days', 30)
        linkedin_metrics = fetch_linkedin_metrics(config, [], days)
        if linkedin_metrics:
            metrics_dict.update(linkedin_metrics)
            print(f"✅ {len(linkedin_metrics)} creativos con métricas obtenidas")
    
    # Actualizar CSV si se solicita
    if config.get('update_csv', False) and metrics_dict:
        print()
        print("💾 Actualizando CSV Master con métricas...")
        updated = update_csv_with_metrics(csv_path, metrics_dict)
        print(f"✅ {updated} creativos actualizados")
    
    # Analizar tendencias
    print()
    analyze_performance_trends(csv_path)

if __name__ == '__main__':
    main()


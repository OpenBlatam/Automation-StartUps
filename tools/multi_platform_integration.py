#!/usr/bin/env python3
"""
Integración Multi-Platforma
Sincroniza creativos y métricas entre LinkedIn, Facebook Ads, Google Ads, etc.
"""
import csv
import sys
import json
from pathlib import Path
from datetime import datetime

def load_config():
    """Carga configuración de plataformas"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    config_path = root_dir / '.platforms_config.json'
    
    if not config_path.exists():
        return {}
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def create_config_template():
    """Crea template de configuración multi-plataforma"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    config_path = root_dir / '.platforms_config.json'
    
    template = {
        "linkedin": {
            "enabled": True,
            "access_token": "",
            "account_id": "",
            "sync_creatives": True,
            "sync_metrics": True
        },
        "facebook": {
            "enabled": False,
            "access_token": "",
            "ad_account_id": "",
            "sync_creatives": True,
            "sync_metrics": True
        },
        "google_ads": {
            "enabled": False,
            "developer_token": "",
            "client_id": "",
            "client_secret": "",
            "refresh_token": "",
            "customer_id": "",
            "sync_creatives": True,
            "sync_metrics": True
        },
        "twitter": {
            "enabled": False,
            "bearer_token": "",
            "account_id": "",
            "sync_creatives": True,
            "sync_metrics": True
        }
    }
    
    if not config_path.exists():
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        print(f"✅ Template de configuración creado: {config_path}")
        print("   Edita el archivo con tus credenciales de plataformas")
    else:
        print(f"⚠️  Configuración ya existe: {config_path}")
    
    return template

def sync_to_facebook(creatives, config):
    """Sincroniza creativos a Facebook Ads"""
    if not config.get('facebook', {}).get('enabled'):
        return False
    
    print("📘 Sincronizando con Facebook Ads...")
    print("   (Implementación requerida: Facebook Marketing API)")
    print("   Requiere: pip install facebook-business")
    return True

def sync_to_google_ads(creatives, config):
    """Sincroniza creativos a Google Ads"""
    if not config.get('google_ads', {}).get('enabled'):
        return False
    
    print("🔵 Sincronizando con Google Ads...")
    print("   (Implementación requerida: Google Ads API)")
    print("   Requiere: pip install google-ads")
    return True

def sync_to_twitter(creatives, config):
    """Sincroniza creativos a Twitter Ads"""
    if not config.get('twitter', {}).get('enabled'):
        return False
    
    print("🐦 Sincronizando con Twitter Ads...")
    print("   (Implementación requerida: Twitter Ads API)")
    print("   Requiere: pip install twitter-ads")
    return True

def aggregate_metrics_from_platforms(config):
    """Agrega métricas de múltiples plataformas"""
    print("=" * 80)
    print("📊 Agregación de Métricas Multi-Platforma")
    print("=" * 80)
    print()
    
    platforms_enabled = []
    
    if config.get('linkedin', {}).get('enabled'):
        platforms_enabled.append('LinkedIn')
    if config.get('facebook', {}).get('enabled'):
        platforms_enabled.append('Facebook')
    if config.get('google_ads', {}).get('enabled'):
        platforms_enabled.append('Google Ads')
    if config.get('twitter', {}).get('enabled'):
        platforms_enabled.append('Twitter')
    
    if not platforms_enabled:
        print("⚠️  No hay plataformas habilitadas")
        print("   Configura plataformas en .platforms_config.json")
        return
    
    print(f"✅ Plataformas habilitadas: {', '.join(platforms_enabled)}")
    print()
    print("💡 Para implementación completa:")
    print("   1. Instala SDKs requeridos de cada plataforma")
    print("   2. Configura credenciales en .platforms_config.json")
    print("   3. Adapta funciones de sincronización según APIs específicas")
    print()

def main():
    print("=" * 80)
    print("🌐 Integración Multi-Platforma")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        print("❌ CSV Master no encontrado")
        return
    
    # Cargar creativos
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        creatives = list(reader)
    
    print(f"✅ Cargados {len(creatives)} creativos del CSV Master")
    print()
    
    # Cargar configuración
    config = load_config()
    
    if not config:
        print("⚠️  No se encontró configuración")
        response = input("¿Crear template de configuración? (s/n): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            create_config_template()
        return
    
    # Sincronizar con plataformas
    if len(sys.argv) > 1:
        platform = sys.argv[1]
        
        if platform == 'facebook':
            sync_to_facebook(creatives, config)
        elif platform == 'google':
            sync_to_google_ads(creatives, config)
        elif platform == 'twitter':
            sync_to_twitter(creatives, config)
        elif platform == 'all':
            sync_to_facebook(creatives, config)
            sync_to_google_ads(creatives, config)
            sync_to_twitter(creatives, config)
        elif platform == 'aggregate':
            aggregate_metrics_from_platforms(config)
        else:
            print(f"❌ Plataforma desconocida: {platform}")
            print("   Disponibles: facebook, google, twitter, all, aggregate")
    else:
        # Mostrar opciones
        print("Uso:")
        print("  python3 multi_platform_integration.py facebook")
        print("  python3 multi_platform_integration.py google")
        print("  python3 multi_platform_integration.py twitter")
        print("  python3 multi_platform_integration.py all")
        print("  python3 multi_platform_integration.py aggregate")
        print()
        aggregate_metrics_from_platforms(config)

if __name__ == '__main__':
    main()


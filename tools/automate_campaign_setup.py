#!/usr/bin/env python3
"""
Automatización de setup de campañas
Genera configuraciones de campaña listas para importar en LinkedIn Campaign Manager
"""
import csv
import sys
import json
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

def group_creatives_by_campaign(creatives):
    """Agrupa creativos por campaña sugerida"""
    campaigns = defaultdict(list)
    
    for creative in creatives:
        # Agrupar por producto y formato
        producto = creative.get('producto', 'unknown')
        formato = creative.get('formato', 'unknown')
        angulo = creative.get('angulo', 'base')
        
        # Nombre de campaña sugerido
        campaign_name = f"{producto}_{formato}_{angulo}"
        
        campaigns[campaign_name].append(creative)
    
    return dict(campaigns)

def generate_campaign_config(campaign_name, creatives, settings=None):
    """Genera configuración de campaña para LinkedIn"""
    if settings is None:
        settings = {
            'daily_budget': 50,
            'objective': 'WEBSITE_CONVERSIONS',
            'audience_type': 'MATCHED_AUDIENCES',
            'bid_strategy': 'COST_PER_CLICK',
            'start_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'end_date': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        }
    
    # Extraer información común
    first_creative = creatives[0]
    producto = first_creative.get('producto', 'unknown')
    
    config = {
        'campaign_name': campaign_name,
        'campaign_status': 'ACTIVE',
        'account_id': settings.get('account_id', 'YOUR_ACCOUNT_ID'),
        'objective': settings['objective'],
        'budget': {
            'daily_budget': settings['daily_budget'],
            'currency': 'USD'
        },
        'dates': {
            'start': settings['start_date'],
            'end': settings['end_date']
        },
        'targeting': {
            'audience_type': settings['audience_type'],
            'locations': settings.get('locations', ['United States']),
            'job_titles': settings.get('job_titles', []),
            'company_sizes': settings.get('company_sizes', [])
        },
        'bid_strategy': settings['bid_strategy'],
        'ad_groups': []
    }
    
    # Crear ad groups por formato/ángulo
    by_format = defaultdict(list)
    for creative in creatives:
        formato = creative.get('formato', 'unknown')
        by_format[formato].append(creative)
    
    for formato, format_creatives in by_format.items():
        ad_group = {
            'ad_group_name': f"{campaign_name}_{formato}",
            'creatives': []
        }
        
        for creative in format_creatives:
            ad_creative = {
                'creative_name': creative.get('creative_file', ''),
                'headline': creative.get('headline', 'Default Headline'),
                'description': creative.get('description', 'Default Description'),
                'final_url': creative.get('final_url', ''),
                'image_url': creative.get('image_url', ''),
                'utm_parameters': {
                    'utm_source': creative.get('utm_source', 'linkedin'),
                    'utm_medium': creative.get('utm_medium', 'cpc'),
                    'utm_campaign': creative.get('utm_campaign', campaign_name),
                    'utm_content': creative.get('utm_content', ''),
                    'utm_term': creative.get('utm_term', '')
                }
            }
            ad_group['creatives'].append(ad_creative)
        
        config['ad_groups'].append(ad_group)
    
    return config

def generate_linkedin_import_json(campaigns_config):
    """Genera JSON para importar en LinkedIn"""
    import_data = {
        'version': '2.0',
        'campaigns': []
    }
    
    for campaign_config in campaigns_config:
        import_data['campaigns'].append(campaign_config)
    
    return json.dumps(import_data, indent=2)

def generate_instructions(campaigns_config):
    """Genera instrucciones de importación"""
    instructions = []
    instructions.append("# Instrucciones de Importación de Campañas")
    instructions.append("")
    instructions.append(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    instructions.append("")
    instructions.append(f"Total campañas: {len(campaigns_config)}")
    instructions.append("")
    instructions.append("## Pasos para Importar")
    instructions.append("")
    instructions.append("1. Abre LinkedIn Campaign Manager")
    instructions.append("2. Ve a 'Create' > 'Import from file'")
    instructions.append("3. Selecciona el archivo JSON generado")
    instructions.append("4. Revisa y ajusta configuraciones según sea necesario")
    instructions.append("5. Confirma la importación")
    instructions.append("")
    instructions.append("## Notas Importantes")
    instructions.append("")
    instructions.append("- Revisa los budgets antes de activar")
    instructions.append("- Verifica las URLs finales y UTMs")
    instructions.append("- Ajusta targeting según tu audiencia")
    instructions.append("- Activa campañas gradualmente para testing")
    instructions.append("")
    
    return '\n'.join(instructions)

def main():
    print("=" * 80)
    print("🚀 Automatización de Setup de Campañas")
    print("=" * 80)
    print()
    
    creatives = load_creatives()
    if not creatives:
        print("❌ No se encontró CSV Master")
        return
    
    print(f"✅ Cargados {len(creatives)} creativos")
    print()
    
    # Agrupar por campaña
    campaigns = group_creatives_by_campaign(creatives)
    
    print(f"📊 Generando configuraciones para {len(campaigns)} campañas...")
    print()
    
    # Generar configuraciones
    campaigns_config = []
    
    for campaign_name, campaign_creatives in campaigns.items():
        config = generate_campaign_config(campaign_name, campaign_creatives)
        campaigns_config.append(config)
        print(f"  ✅ {campaign_name}: {len(campaign_creatives)} creativos")
    
    print()
    
    # Generar archivos de exportación
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    exports_dir = root_dir / 'exports'
    exports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # JSON para importación
    json_path = exports_dir / f'linkedin_campaigns_{timestamp}.json'
    json_content = generate_linkedin_import_json(campaigns_config)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        f.write(json_content)
    
    print(f"✅ JSON de importación: {json_path}")
    
    # Instrucciones
    instructions_path = exports_dir / f'campaign_import_instructions_{timestamp}.md'
    instructions_content = generate_instructions(campaigns_config)
    
    with open(instructions_path, 'w', encoding='utf-8') as f:
        f.write(instructions_content)
    
    print(f"✅ Instrucciones: {instructions_path}")
    print()
    
    print("=" * 80)
    print("📋 Resumen")
    print("=" * 80)
    print(f"  Campañas generadas: {len(campaigns_config)}")
    
    total_creatives = sum(len(c['ad_groups']) * sum(len(ag['creatives']) for ag in c['ad_groups']) 
                         for c in campaigns_config)
    print(f"  Total creativos agrupados: {total_creatives}")
    print()
    
    print("💡 Próximos pasos:")
    print("   1. Revisa el JSON generado")
    print("   2. Ajusta budgets y targeting según necesites")
    print("   3. Importa en LinkedIn Campaign Manager")
    print("   4. Activa campañas gradualmente")
    print()

if __name__ == '__main__':
    main()


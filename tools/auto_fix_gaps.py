#!/usr/bin/env python3
"""
Auto-fix de gaps: Añade automáticamente SVGs faltantes al CSV Master
Genera UTMs sugeridos basados en naming conventions
"""
import csv
import os
import sys
from pathlib import Path
from datetime import datetime
import re

def extract_info_from_filename(filename):
    """Extrae información del filename para generar UTM"""
    # ad_ia_bulk_1200x627_metrics.svg
    info = {
        'producto': 'unknown',
        'formato': 'unknown',
        'angulo': 'base',
        'cta': 'demo',
        'placement': 'feed'
    }
    
    # Producto
    if 'ia_bulk' in filename or 'bulk' in filename:
        info['producto'] = 'iabulk'
    elif 'curso' in filename:
        info['producto'] = 'cursoia'
    elif 'saas' in filename:
        info['producto'] = 'saasia'
    
    # Formato
    if '1200x627' in filename:
        info['formato'] = '1200x627'
        info['placement'] = 'feed'
    elif '1080x1080' in filename:
        info['formato'] = '1080x1080'
        info['placement'] = 'feed'
    elif '1080x1920' in filename:
        info['formato'] = '1080x1920'
        info['placement'] = 'stories'
    elif 'carousel' in filename:
        info['formato'] = 'carousel'
        info['placement'] = 'feed'
    
    # Ángulo
    if 'metrics' in filename:
        info['angulo'] = 'metrics'
    elif 'social' in filename or 'socialproof' in filename:
        info['angulo'] = 'socialproof'
    elif 'urgency' in filename or 'urgent' in filename:
        info['angulo'] = 'urgency'
    elif 'v2' in filename:
        info['angulo'] = 'base'
    
    # CTA
    if 'demo' in filename:
        info['cta'] = 'demo'
    elif 'registro' in filename or 'registrar' in filename:
        info['cta'] = 'registro'
    elif 'trial' in filename:
        info['cta'] = 'trial'
    
    # Webinar preroll
    if 'webinar-preroll' in filename:
        info['producto'] = 'cursoia'
        info['formato'] = 'preroll'
        info['placement'] = 'video'
        if 'social' in filename:
            info['angulo'] = 'socialproof'
        elif 'benefits' in filename:
            info['angulo'] = 'benefits'
        elif 'speaker' in filename:
            info['angulo'] = 'speaker'
        elif 'urgent' in filename:
            info['angulo'] = 'urgent'
    
    return info

def generate_utm_content(info):
    """Genera utm_content basado en información extraída"""
    parts = []
    
    # Formato prefix
    if info['formato'] == '1080x1080':
        parts.append('sq')
    elif info['formato'] == '1080x1920':
        parts.append('vt')
    elif info['formato'] == 'carousel':
        parts.append('carousel')
        # Extraer slide number si existe
        if 'slide' in info.get('filename', ''):
            slide_match = re.search(r'slide(\d+)', info['filename'])
            if slide_match:
                parts.append(f"slide{slide_match.group(1)}")
    elif info['formato'] == 'preroll':
        parts.append('preroll')
    
    # Ángulo
    if info['angulo'] != 'base':
        parts.append(info['angulo'])
    
    # CTA
    parts.append(f"cta_{info['cta']}")
    parts.append('v1')
    
    return '_'.join(parts)

def generate_final_url(base_url, utm_params):
    """Genera final_url con parámetros UTM"""
    from urllib.parse import urlencode
    
    params = {k: v for k, v in utm_params.items() if v}
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url

def find_svgs_without_csv():
    """Encuentra SVGs que no están en CSV"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    linkedin_dir = root_dir / 'ads' / 'linkedin'
    
    if not csv_path.exists():
        print("❌ CSV Master no encontrado")
        return []
    
    # Cargar creativos existentes en CSV
    existing_files = set()
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            existing_files.add(row.get('creative_file', ''))
    
    # Buscar SVGs sin entrada
    missing_svgs = []
    
    # LinkedIn SVGs
    if linkedin_dir.exists():
        for svg_file in linkedin_dir.glob('*.svg'):
            if svg_file.name not in existing_files and svg_file.name != 'tokens.json':
                missing_svgs.append(('linkedin', svg_file.name))
    
    # Webinar prerolls en raíz
    for svg_file in root_dir.glob('webinar-preroll-*.svg'):
        if svg_file.name not in existing_files:
            missing_svgs.append(('root', svg_file.name))
    
    return missing_svgs

def add_to_csv(creative_data, csv_path):
    """Añade entrada al CSV Master"""
    fieldnames = [
        'fecha', 'creative_file', 'producto', 'formato', 'angulo', 'cta',
        'placement', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content',
        'utm_term', 'landing_url', 'final_url'
    ]
    
    # Leer CSV existente
    rows = []
    if csv_path.exists():
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            if fieldnames != reader.fieldnames:
                fieldnames = reader.fieldnames
    
    # Añadir nueva fila
    rows.append(creative_data)
    
    # Escribir CSV
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def main():
    print("=" * 80)
    print("🔧 Auto-fix de Gaps: SVGs → CSV Master")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    # Encontrar SVGs faltantes
    missing_svgs = find_svgs_without_csv()
    
    if not missing_svgs:
        print("✅ No se encontraron SVGs sin entrada en CSV")
        return
    
    print(f"📁 Encontrados {len(missing_svgs)} SVGs sin entrada en CSV:")
    for location, filename in missing_svgs:
        print(f"   • {filename} ({location})")
    print()
    
    # Confirmar acción
    if '--auto' not in sys.argv:
        response = input("¿Añadir automáticamente al CSV Master? (s/n): ")
        if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return
    
    # Generar entradas para cada SVG faltante
    added = 0
    today = datetime.now().strftime('%Y-%m-%d')
    
    for location, filename in missing_svgs:
        info = extract_info_from_filename(filename)
        info['filename'] = filename
        
        # Generar UTMs
        utm_content = generate_utm_content(info)
        utm_campaign = f"{info['producto']}_{info['cta']}_linkedin_{datetime.now().strftime('%Y-%m')}"
        
        # Landing URL por defecto (debe actualizarse manualmente)
        landing_url = f"https://tusitio.com/{info['cta']}"
        
        # Generar final_url
        utm_params = {
            'utm_source': 'linkedin',
            'utm_medium': 'cpc' if location == 'linkedin' else 'email',
            'utm_campaign': utm_campaign,
            'utm_content': utm_content,
            'utm_term': 'cmo_mx'  # Default, debe actualizarse
        }
        
        final_url = generate_final_url(landing_url, utm_params)
        
        # Crear entrada
        creative_data = {
            'fecha': today,
            'creative_file': filename,
            'producto': info['producto'],
            'formato': info['formato'],
            'angulo': info['angulo'],
            'cta': info['cta'],
            'placement': info['placement'],
            'utm_source': 'linkedin',
            'utm_medium': 'cpc' if location == 'linkedin' else 'email',
            'utm_campaign': utm_campaign,
            'utm_content': utm_content,
            'utm_term': 'cmo_mx',
            'landing_url': landing_url,
            'final_url': final_url
        }
        
        # Añadir al CSV
        add_to_csv(creative_data, csv_path)
        added += 1
        
        print(f"✅ Añadido: {filename}")
        print(f"   UTM Content: {utm_content}")
        print(f"   ⚠️  Revisa landing_url y utm_term (valores por defecto)")
    
    print()
    print(f"✅ {added} entradas añadidas al CSV Master")
    print()
    print("💡 Próximos pasos:")
    print("   1. Revisar y actualizar landing_url según corresponda")
    print("   2. Ajustar utm_term según audiencia objetivo")
    print("   3. Validar con: python3 tools/validate_utms.py")
    print()

if __name__ == '__main__':
    main()



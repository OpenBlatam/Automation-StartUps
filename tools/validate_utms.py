#!/usr/bin/env python3
"""
Valida que todos los creativos tengan UTMs configurados correctamente
"""
import csv
import os
import sys

def validate_row(row, index):
    """Valida una fila del CSV"""
    errors = []
    
    # Campos requeridos
    required_fields = ['creative_file', 'utm_source', 'utm_medium', 
                       'utm_campaign', 'utm_content', 'final_url']
    
    for field in required_fields:
        if not row.get(field):
            errors.append(f"Fila {index}: Falta '{field}'")
    
    # Validar formato de utm_content
    utm_content = row.get('utm_content', '')
    if utm_content:
        # Debe tener al menos: tipo_producto_angulo_cta_version
        parts = utm_content.split('_')
        if len(parts) < 4:
            errors.append(f"Fila {index}: utm_content debe tener formato: tipo_angulo_cta_version (tiene {len(parts)} partes)")
    
    # Validar que final_url tenga parámetros UTM
    final_url = row.get('final_url', '')
    if final_url:
        if 'utm_source=' not in final_url:
            errors.append(f"Fila {index}: final_url no contiene utm_source")
    
    # Validar que el SVG existe (si está en ads/linkedin)
    creative_file = row.get('creative_file', '')
    if creative_file and creative_file.startswith('ad_'):
        svg_path = f"ads/linkedin/{creative_file}"
        if not os.path.exists(svg_path):
            # También verificar si es preroll en raíz
            if 'webinar-preroll' in creative_file:
                preroll_path = creative_file
                if not os.path.exists(preroll_path):
                    errors.append(f"Fila {index}: SVG no encontrado: {svg_path} o {preroll_path}")
            else:
                errors.append(f"Fila {index}: SVG no encontrado: {svg_path}")
    
    return errors

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(root_dir, 'docs', 'LINKEDIN_ADS_CREATIVES_MASTER.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV no encontrado: {csv_path}")
        sys.exit(1)
    
    all_errors = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            errors = validate_row(row, i)
            all_errors.extend(errors)
    
    if all_errors:
        print("❌ Errores encontrados:\n")
        for error in all_errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("✅ Todos los UTMs están configurados correctamente")

if __name__ == '__main__':
    main()



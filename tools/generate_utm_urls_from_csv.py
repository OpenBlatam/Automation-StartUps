#!/usr/bin/env python3
"""
Genera URLs finales con UTMs desde LINKEDIN_ADS_CREATIVES_MASTER.csv
y exporta para LinkedIn Campaign Manager
"""
import csv
import os
import sys
from urllib.parse import urlencode

def generate_final_url(row):
    """Genera final_url con parámetros UTM"""
    base_url = row.get('landing_url', '')
    if not base_url:
        return ''
    
    params = {}
    if row.get('utm_source'): params['utm_source'] = row['utm_source']
    if row.get('utm_medium'): params['utm_medium'] = row['utm_medium']
    if row.get('utm_campaign'): params['utm_campaign'] = row['utm_campaign']
    if row.get('utm_content'): params['utm_content'] = row['utm_content']
    if row.get('utm_term'): params['utm_term'] = row['utm_term']
    
    if params:
        return f"{base_url}?{urlencode(params)}"
    return base_url

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(script_dir)
    csv_path = os.path.join(root_dir, 'docs', 'LINKEDIN_ADS_CREATIVES_MASTER.csv')
    
    if not os.path.exists(csv_path):
        print(f"❌ CSV no encontrado: {csv_path}")
        sys.exit(1)
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    # Generar final_url para cada row
    updated_rows = []
    for row in rows:
        if not row.get('final_url'):
            row['final_url'] = generate_final_url(row)
        updated_rows.append(row)
    
    # Exportar para LinkedIn Campaign Manager
    print("URLs listas para LinkedIn Campaign Manager:\n")
    print("-" * 80)
    for row in updated_rows:
        print(f"\n📄 {row['creative_file']}")
        print(f"   Producto: {row.get('producto', 'N/A')}")
        print(f"   Formato: {row.get('formato', 'N/A')}")
        print(f"   URL: {row['final_url']}")
        print(f"   UTM Content: {row.get('utm_content', 'N/A')}")
    
    print("\n" + "-" * 80)
    print(f"\n✅ Total: {len(updated_rows)} URLs generadas")
    
    # Opción para exportar a CSV actualizado
    export_path = os.path.join(root_dir, 'docs', 'LINKEDIN_ADS_CREATIVES_MASTER_UPDATED.csv')
    fieldnames = updated_rows[0].keys() if updated_rows else []
    
    with open(export_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)
    
    print(f"📁 CSV actualizado guardado en: {export_path}")

if __name__ == '__main__':
    main()



#!/usr/bin/env python3
"""
Optimiza el CSV Master: elimina duplicados, normaliza valores, valida consistencia
"""
import csv
import sys
from pathlib import Path
from collections import defaultdict
import re

def normalize_value(value, field_type):
    """Normaliza valores según tipo de campo"""
    if not value:
        return value
    
    value = value.strip()
    
    if field_type == 'utm_content':
        # Normalizar: minúsculas, sin espacios extras
        value = value.lower().replace(' ', '_')
    elif field_type == 'utm_campaign':
        # Normalizar: minúsculas
        value = value.lower()
    elif field_type == 'formato':
        # Normalizar formatos
        value = value.replace('×', 'x').replace(' ', '')
    elif field_type == 'producto':
        # Normalizar productos
        value = value.lower().replace(' ', '_')
    
    return value

def find_duplicates(creatives):
    """Encuentra duplicados en CSV"""
    seen = {}
    duplicates = []
    
    for i, creative in enumerate(creatives):
        creative_file = creative.get('creative_file', '')
        if not creative_file:
            continue
        
        if creative_file in seen:
            duplicates.append({
                'file': creative_file,
                'rows': [seen[creative_file], i + 2]  # +2 porque header es row 1
            })
        else:
            seen[creative_file] = i + 2
    
    return duplicates

def validate_consistency(creatives):
    """Valida consistencia de datos"""
    issues = []
    
    for i, creative in enumerate(creatives, start=2):  # Start at 2 (header is row 1)
        creative_file = creative.get('creative_file', '')
        
        # Validar que formato coincide con filename
        formato = creative.get('formato', '')
        if formato and creative_file:
            if '1200x627' in creative_file and formato != '1200x627':
                issues.append({
                    'row': i,
                    'file': creative_file,
                    'issue': f"Formato '{formato}' no coincide con filename (contiene 1200x627)"
                })
        
        # Validar que utm_content sigue convención
        utm_content = creative.get('utm_content', '')
        if utm_content and not re.match(r'^[a-z0-9_]+$', utm_content):
            issues.append({
                'row': i,
                'file': creative_file,
                'issue': f"utm_content '{utm_content}' contiene caracteres inválidos"
            })
        
        # Validar final_url contiene UTMs
        final_url = creative.get('final_url', '')
        if final_url and 'utm_source=' not in final_url:
            issues.append({
                'row': i,
                'file': creative_file,
                'issue': 'final_url no contiene parámetros UTM'
            })
    
    return issues

def optimize_csv(csv_path):
    """Optimiza el CSV Master"""
    print("=" * 80)
    print("🔧 Optimización de CSV Master")
    print("=" * 80)
    print()
    
    # Leer CSV
    creatives = []
    fieldnames = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        creatives = list(reader)
    
    print(f"✅ CSV cargado: {len(creatives)} registros")
    print()
    
    # Normalizar valores
    print("📝 Normalizando valores...")
    for creative in creatives:
        creative['formato'] = normalize_value(creative.get('formato', ''), 'formato')
        creative['producto'] = normalize_value(creative.get('producto', ''), 'producto')
        creative['utm_content'] = normalize_value(creative.get('utm_content', ''), 'utm_content')
        creative['utm_campaign'] = normalize_value(creative.get('utm_campaign', ''), 'utm_campaign')
    
    print("   ✅ Valores normalizados")
    print()
    
    # Encontrar duplicados
    print("🔍 Buscando duplicados...")
    duplicates = find_duplicates(creatives)
    
    if duplicates:
        print(f"   ⚠️  {len(duplicates)} duplicado(s) encontrado(s):")
        for dup in duplicates[:5]:
            print(f"      • {dup['file']} (filas {dup['rows']})")
        if len(duplicates) > 5:
            print(f"      ... y {len(duplicates) - 5} más")
        
        # Eliminar duplicados (mantener primera ocurrencia)
        seen_files = set()
        unique_creatives = []
        removed = 0
        
        for creative in creatives:
            creative_file = creative.get('creative_file', '')
            if creative_file and creative_file not in seen_files:
                seen_files.add(creative_file)
                unique_creatives.append(creative)
            elif creative_file:
                removed += 1
        
        creatives = unique_creatives
        print(f"   ✅ {removed} duplicado(s) eliminado(s)")
    else:
        print("   ✅ No se encontraron duplicados")
    print()
    
    # Validar consistencia
    print("✅ Validando consistencia...")
    issues = validate_consistency(creatives)
    
    if issues:
        print(f"   ⚠️  {len(issues)} inconsistencia(s) encontrada(s):")
        for issue in issues[:5]:
            print(f"      • Fila {issue['row']} ({issue['file']}): {issue['issue']}")
        if len(issues) > 5:
            print(f"      ... y {len(issues) - 5} más")
    else:
        print("   ✅ Sin inconsistencias detectadas")
    print()
    
    # Guardar CSV optimizado
    backup_path = csv_path.with_suffix('.csv.backup')
    
    # Crear backup
    import shutil
    shutil.copy2(csv_path, backup_path)
    print(f"📦 Backup creado: {backup_path}")
    
    # Guardar optimizado
    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(creatives)
    
    print(f"✅ CSV optimizado guardado: {csv_path}")
    print()
    print(f"📊 Resumen:")
    print(f"   • Registros procesados: {len(creatives)}")
    print(f"   • Duplicados eliminados: {len(duplicates)}")
    print(f"   • Inconsistencias detectadas: {len(issues)}")
    print()
    
    if issues:
        print("💡 Próximos pasos:")
        print("   1. Revisar inconsistencias manualmente")
        print("   2. Corregir según sea necesario")
        print("   3. Validar con: python3 tools/validate_utms.py")
    print()

def main():
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    if not csv_path.exists():
        print(f"❌ CSV Master no encontrado: {csv_path}")
        sys.exit(1)
    
    if '--no-backup' not in sys.argv:
        response = input("¿Crear backup antes de optimizar? (s/n): ")
        if response.lower() not in ['s', 'si', 'sí', 'y', 'yes']:
            print("❌ Operación cancelada")
            return
    
    optimize_csv(csv_path)

if __name__ == '__main__':
    main()



#!/usr/bin/env python3
"""
Genera reporte de gaps entre SVGs y CSV Master
Identifica: SVGs sin UTMs, CSV sin SVGs, UTMs incompletos
"""
import csv
import os
import sys
from pathlib import Path

def find_svg_files(directory):
    """Encuentra todos los SVGs en un directorio"""
    svgs = set()
    for path in Path(directory).rglob('*.svg'):
        if 'node_modules' not in str(path) and '.git' not in str(path):
            svgs.add(path.name)
    return svgs

def analyze_gaps():
    """Analiza gaps entre CSV y SVGs"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    linkedin_dir = root_dir / 'ads' / 'linkedin'
    
    if not csv_path.exists():
        print(f"❌ CSV no encontrado: {csv_path}")
        sys.exit(1)
    
    # Leer CSV
    csv_creatives = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            creative_file = row.get('creative_file', '')
            if creative_file:
                csv_creatives[creative_file] = row
    
    # Encontrar SVGs
    svgs_in_dir = find_svg_files(linkedin_dir) if linkedin_dir.exists() else set()
    
    # Webinars en raíz
    webinar_dir = root_dir
    webinars_in_dir = {f.name for f in webinar_dir.glob('webinar-preroll-*.svg')}
    all_svgs = svgs_in_dir | webinars_in_dir
    
    # Análisis de gaps
    svgs_without_csv = all_svgs - set(csv_creatives.keys())
    csv_without_svg = set()
    
    for creative_file, row in csv_creatives.items():
        if creative_file.startswith('webinar-preroll'):
            svg_path = root_dir / creative_file
        else:
            svg_path = linkedin_dir / creative_file
        
        if not svg_path.exists():
            csv_without_svg.add(creative_file)
    
    # SVGs con UTMs incompletos
    incomplete_utms = []
    for creative_file, row in csv_creatives.items():
        required_fields = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'final_url']
        missing = [f for f in required_fields if not row.get(f)]
        if missing:
            incomplete_utms.append({
                'file': creative_file,
                'missing': missing
            })
    
    # Generar reporte
    print("=" * 80)
    print("📋 REPORTE DE GAPS: SVGs ↔ CSV Master")
    print("=" * 80)
    print()
    
    # SVGs sin CSV
    print(f"📁 SVGs sin entrada en CSV: {len(svgs_without_csv)}")
    if svgs_without_csv:
        print("   Archivos:")
        for svg in sorted(list(svgs_without_csv)[:10]):
            print(f"   • {svg}")
        if len(svgs_without_csv) > 10:
            print(f"   ... y {len(svgs_without_csv) - 10} más")
        print()
        print("   💡 Acción: Añadir estos SVGs al CSV Master con sus UTMs")
    else:
        print("   ✅ Todos los SVGs tienen entrada en CSV")
    print()
    
    # CSV sin SVG
    print(f"📝 Registros CSV sin SVG: {len(csv_without_svg)}")
    if csv_without_svg:
        print("   Archivos:")
        for csv_file in sorted(list(csv_without_svg)[:10]):
            print(f"   • {csv_file}")
        if len(csv_without_svg) > 10:
            print(f"   ... y {len(csv_without_svg) - 10} más")
        print()
        print("   💡 Acción: Eliminar registros obsoletos o crear los SVGs faltantes")
    else:
        print("   ✅ Todos los registros CSV tienen SVG correspondiente")
    print()
    
    # UTMs incompletos
    print(f"⚠️  UTMs incompletos: {len(incomplete_utms)}")
    if incomplete_utms:
        print("   Archivos con campos faltantes:")
        for item in incomplete_utms[:10]:
            missing_str = ', '.join(item['missing'])
            print(f"   • {item['file']}: falta {missing_str}")
        if len(incomplete_utms) > 10:
            print(f"   ... y {len(incomplete_utms) - 10} más")
        print()
        print("   💡 Acción: Completar campos UTM faltantes en CSV")
    else:
        print("   ✅ Todos los UTMs están completos")
    print()
    
    # Resumen
    print("=" * 80)
    print("📊 RESUMEN")
    print("=" * 80)
    print(f"Total SVGs encontrados: {len(all_svgs)}")
    print(f"Total registros en CSV: {len(csv_creatives)}")
    print(f"SVGs con CSV: {len(all_svgs) - len(svgs_without_csv)}")
    print(f"CSV con SVG: {len(csv_creatives) - len(csv_without_svg)}")
    print()
    
    # Recomendaciones
    if svgs_without_csv or csv_without_svg or incomplete_utms:
        print("💡 RECOMENDACIONES:")
        if svgs_without_csv:
            print("   1. Ejecutar: python3 tools/validate_utms.py para validar formato")
            print("   2. Añadir SVGs faltantes al CSV Master")
        if csv_without_svg:
            print("   3. Revisar y limpiar registros CSV obsoletos")
        if incomplete_utms:
            print("   4. Completar campos UTM faltantes")
    else:
        print("✅ ¡Todo está sincronizado! No se requieren acciones.")
    print()

if __name__ == '__main__':
    analyze_gaps()



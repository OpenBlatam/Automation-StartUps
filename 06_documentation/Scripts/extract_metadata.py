#!/usr/bin/env python3
"""
Script para extraer y analizar metadatos de archivos Markdown
"""
import os
import re
import yaml
from pathlib import Path
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).parent.parent.parent

def extract_frontmatter(file_path):
    """Extrae el frontmatter YAML de un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None, None
    
    if not content.startswith('---'):
        return None, content
    
    # Encontrar el final del frontmatter
    end_pos = content.find('---', 3)
    if end_pos == -1:
        return None, content
    
    frontmatter_text = content[3:end_pos]
    body = content[end_pos + 3:].lstrip('\n')
    
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        return frontmatter, body
    except yaml.YAMLError:
        return None, content

def analyze_metadata(folder_path=None, max_files=None):
    """Analiza metadatos de todos los archivos"""
    if folder_path is None:
        folder_path = BASE_DIR
    
    metadata_stats = {
        'total_files': 0,
        'files_with_frontmatter': 0,
        'files_without_frontmatter': 0,
        'fields': Counter(),
        'categories': Counter(),
        'tags': Counter(),
        'created_dates': Counter(),
        'paths': Counter(),
        'missing_fields': defaultdict(int)
    }
    
    all_metadata = []
    
    count = 0
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            if max_files and count >= max_files:
                break
            
            file_path = Path(root) / file
            metadata_stats['total_files'] += 1
            count += 1
            
            frontmatter, body = extract_frontmatter(file_path)
            
            if frontmatter:
                metadata_stats['files_with_frontmatter'] += 1
                all_metadata.append({
                    'file': str(file_path.relative_to(BASE_DIR)),
                    'metadata': frontmatter
                })
                
                # Analizar campos
                for key, value in frontmatter.items():
                    metadata_stats['fields'][key] += 1
                    
                    if key == 'category':
                        if isinstance(value, str):
                            metadata_stats['categories'][value] += 1
                    elif key == 'tags':
                        if isinstance(value, list):
                            for tag in value:
                                if isinstance(tag, str):
                                    metadata_stats['tags'][tag] += 1
                    elif key == 'created':
                        if isinstance(value, str):
                            # Extraer año
                            year_match = re.search(r'(\d{4})', value)
                            if year_match:
                                metadata_stats['created_dates'][year_match.group(1)] += 1
                    elif key == 'path':
                        if isinstance(value, str):
                            metadata_stats['paths'][value] += 1
            else:
                metadata_stats['files_without_frontmatter'] += 1
    
    # Campos comunes que deberían estar
    common_fields = ['title', 'category', 'tags', 'created', 'path']
    for metadata_item in all_metadata:
        for field in common_fields:
            if field not in metadata_item['metadata']:
                metadata_stats['missing_fields'][field] += 1
    
    return metadata_stats, all_metadata

def generate_metadata_report(folder_path=None, max_files=500):
    """Genera reporte de metadatos"""
    print("📊 Analizando metadatos de archivos...")
    
    stats, all_metadata = analyze_metadata(folder_path, max_files)
    
    print("\n" + "="*80)
    print("📋 REPORTE DE METADATOS")
    print("="*80)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES")
    print(f"  Total de archivos: {stats['total_files']:,}")
    print(f"  Con frontmatter: {stats['files_with_frontmatter']:,} ({stats['files_with_frontmatter']/max(stats['total_files'],1)*100:.1f}%)")
    print(f"  Sin frontmatter: {stats['files_without_frontmatter']:,} ({stats['files_without_frontmatter']/max(stats['total_files'],1)*100:.1f}%)")
    
    if stats['fields']:
        print(f"\n📝 CAMPOS MÁS COMUNES (Top 15)")
        for field, count in stats['fields'].most_common(15):
            percentage = (count / stats['files_with_frontmatter']) * 100 if stats['files_with_frontmatter'] > 0 else 0
            print(f"  {field:20s}: {count:6,} archivos ({percentage:5.1f}%)")
    
    if stats['categories']:
        print(f"\n📂 CATEGORÍAS MÁS COMUNES (Top 20)")
        for category, count in stats['categories'].most_common(20):
            print(f"  {category:30s}: {count:6,}")
    
    if stats['tags']:
        print(f"\n🏷️  TAGS MÁS COMUNES (Top 30)")
        for tag, count in stats['tags'].most_common(30):
            print(f"  {tag:30s}: {count:6,}")
    
    if stats['created_dates']:
        print(f"\n📅 ARCHIVOS POR AÑO DE CREACIÓN")
        for year, count in sorted(stats['created_dates'].items()):
            print(f"  {year}: {count:,} archivos")
    
    if stats['missing_fields']:
        print(f"\n⚠️  CAMPOS FALTANTES")
        for field, count in sorted(stats['missing_fields'].items(), key=lambda x: -x[1]):
            percentage = (count / stats['files_with_frontmatter']) * 100 if stats['files_with_frontmatter'] > 0 else 0
            print(f"  {field:20s}: {count:6,} archivos sin este campo ({percentage:5.1f}%)")
    
    # Archivos sin frontmatter (muestra algunos)
    if stats['files_without_frontmatter'] > 0:
        print(f"\n⚠️  ARCHIVOS SIN FRONTMATTER: {stats['files_without_frontmatter']}")
        print("  (Considera agregar frontmatter para mejor organización)")

if __name__ == '__main__':
    import sys
    
    try:
        import yaml
    except ImportError:
        print("❌ Error: Se requiere PyYAML. Instala con: pip install pyyaml")
        sys.exit(1)
    
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    max_files = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    generate_metadata_report(folder, max_files)








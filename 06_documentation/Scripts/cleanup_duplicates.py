#!/usr/bin/env python3
"""
Script para identificar y manejar archivos duplicados
"""
import os
import hashlib
from pathlib import Path
from collections import defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent

def calculate_file_hash(file_path):
    """Calcula el hash MD5 de un archivo"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (OSError, PermissionError):
        return None

def find_duplicates():
    """Encuentra archivos duplicados por hash"""
    hash_to_files = defaultdict(list)
    
    print("🔍 Buscando archivos duplicados...")
    
    for root, dirs, files in os.walk(BASE_DIR):
        # Saltar carpetas de backups y temporales
        dirs[:] = [d for d in dirs if not d.startswith('.') and 'backup' not in d.lower() and 'temp' not in d.lower()]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            file_path = Path(root) / file
            try:
                if file_path.stat().st_size == 0:
                    continue
                
                file_hash = calculate_file_hash(file_path)
                if file_hash:
                    rel_path = file_path.relative_to(BASE_DIR)
                    hash_to_files[file_hash].append(str(rel_path))
            except (OSError, PermissionError):
                continue
    
    # Filtrar solo los que tienen duplicados
    duplicates = {h: files for h, files in hash_to_files.items() if len(files) > 1}
    
    return duplicates

def find_similar_names():
    """Encuentra archivos con nombres similares"""
    name_groups = defaultdict(list)
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            file_path = Path(root) / file
            # Normalizar nombre (sin extensión, lowercase, sin espacios)
            base_name = file_path.stem.lower().replace(' ', '_').replace('-', '_')
            name_groups[base_name].append(str(file_path.relative_to(BASE_DIR)))
    
    # Filtrar solo los que tienen múltiples archivos
    similar = {name: files for name, files in name_groups.items() if len(files) > 1}
    
    return similar

def generate_duplicates_report():
    """Genera reporte de duplicados"""
    print("📊 Generando reporte de duplicados...\n")
    
    duplicates = find_duplicates()
    similar_names = find_similar_names()
    
    print("="*80)
    print("📋 REPORTE DE ARCHIVOS DUPLICADOS")
    print("="*80)
    
    if duplicates:
        print(f"\n🔴 ARCHIVOS DUPLICADOS (mismo contenido): {len(duplicates)} grupos")
        total_duplicates = sum(len(files) - 1 for files in duplicates.values())
        print(f"   Total de archivos duplicados: {total_duplicates}")
        
        # Mostrar los primeros 20 grupos
        for i, (file_hash, files) in enumerate(list(duplicates.items())[:20], 1):
            print(f"\n   Grupo {i} ({len(files)} archivos):")
            for file in files:
                file_path = BASE_DIR / file
                try:
                    size = file_path.stat().st_size
                    print(f"     - {file} ({size:,} bytes)")
                except:
                    print(f"     - {file}")
        
        if len(duplicates) > 20:
            print(f"\n   ... y {len(duplicates) - 20} grupos más")
    else:
        print("\n✅ No se encontraron archivos duplicados por contenido")
    
    if similar_names:
        print(f"\n⚠️  ARCHIVOS CON NOMBRES SIMILARES: {len(similar_names)} grupos")
        
        # Mostrar los primeros 15 grupos
        for i, (name, files) in enumerate(list(similar_names.items())[:15], 1):
            if len(files) > 1:
                print(f"\n   Grupo '{name}' ({len(files)} archivos):")
                for file in files[:5]:
                    print(f"     - {file}")
                if len(files) > 5:
                    print(f"     ... y {len(files) - 5} más")
        
        if len(similar_names) > 15:
            print(f"\n   ... y {len(similar_names) - 15} grupos más")
    
    # Guardar reporte
    report = {
        'timestamp': datetime.now().isoformat(),
        'duplicates_by_hash': {h: files for h, files in list(duplicates.items())[:100]},
        'similar_names': {name: files for name, files in list(similar_names.items())[:100]},
        'total_duplicate_groups': len(duplicates),
        'total_similar_name_groups': len(similar_names)
    }
    
    report_path = BASE_DIR / '06_documentation' / 'duplicados_report.json'
    with open(report_path, 'w', encoding='utf-8') as f:
        import json
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte guardado en: {report_path}")

if __name__ == '__main__':
    generate_duplicates_report()









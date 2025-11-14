#!/usr/bin/env python3
"""
Script de búsqueda avanzada de archivos en el proyecto
"""
import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent

def search_by_name(pattern, case_sensitive=False):
    """Busca archivos por nombre"""
    results = []
    pattern_re = re.compile(pattern, re.IGNORECASE if not case_sensitive else 0)
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            if pattern_re.search(file):
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BASE_DIR)
                results.append(str(rel_path))
    
    return sorted(results)

def search_by_content(pattern, file_extensions=None, case_sensitive=False):
    """Busca archivos por contenido"""
    results = []
    pattern_re = re.compile(pattern, re.IGNORECASE if not case_sensitive else 0)
    
    if file_extensions is None:
        file_extensions = ['.md', '.txt', '.py', '.js', '.json']
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            
            file_path = Path(root) / file
            if file_path.suffix not in file_extensions:
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if pattern_re.search(content):
                        rel_path = file_path.relative_to(BASE_DIR)
                        # Contar coincidencias
                        matches = len(pattern_re.findall(content))
                        results.append((str(rel_path), matches))
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
    
    return sorted(results, key=lambda x: -x[1])  # Ordenar por número de coincidencias

def search_by_category(category):
    """Busca archivos en una categoría específica"""
    category_map = {
        'marketing': '01_marketing',
        'sales': '09_sales',
        'analytics': '16_data_analytics',
        'ai': '08_ai_artificial_intelligence',
        'documentation': '06_documentation',
        'operations': '04_operations',
        'strategy': '06_strategy',
        'legal': '13_legal_compliance',
        'finance': '02_finance',
        'technology': '05_technology',
    }
    
    category_lower = category.lower()
    if category_lower not in category_map:
        return []
    
    folder = BASE_DIR / category_map[category_lower]
    if not folder.exists():
        return []
    
    results = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            file_path = Path(root) / file
            rel_path = file_path.relative_to(BASE_DIR)
            results.append(str(rel_path))
    
    return sorted(results)

def search_by_extension(extension):
    """Busca archivos por extensión"""
    if not extension.startswith('.'):
        extension = '.' + extension
    
    results = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if file.startswith('.'):
                continue
            if Path(file).suffix.lower() == extension.lower():
                file_path = Path(root) / file
                rel_path = file_path.relative_to(BASE_DIR)
                results.append(str(rel_path))
    
    return sorted(results)

def interactive_search():
    """Búsqueda interactiva"""
    print("🔍 Búsqueda Avanzada de Archivos")
    print("=" * 60)
    print("\nOpciones:")
    print("1. Buscar por nombre")
    print("2. Buscar por contenido")
    print("3. Buscar por categoría")
    print("4. Buscar por extensión")
    print("5. Búsqueda combinada")
    print("0. Salir")
    
    choice = input("\nSelecciona una opción: ").strip()
    
    if choice == '1':
        pattern = input("Patrón de búsqueda (regex): ").strip()
        case_sensitive = input("Sensible a mayúsculas? (s/n): ").strip().lower() == 's'
        results = search_by_name(pattern, case_sensitive)
        print(f"\n✓ Encontrados {len(results)} archivos:")
        for r in results[:50]:
            print(f"  - {r}")
        if len(results) > 50:
            print(f"  ... y {len(results) - 50} más")
    
    elif choice == '2':
        pattern = input("Patrón de búsqueda (regex): ").strip()
        case_sensitive = input("Sensible a mayúsculas? (s/n): ").strip().lower() == 's'
        results = search_by_content(pattern, case_sensitive=case_sensitive)
        print(f"\n✓ Encontrados {len(results)} archivos:")
        for r, count in results[:50]:
            print(f"  - {r} ({count} coincidencias)")
        if len(results) > 50:
            print(f"  ... y {len(results) - 50} más")
    
    elif choice == '3':
        print("\nCategorías disponibles:")
        categories = ['marketing', 'sales', 'analytics', 'ai', 'documentation', 
                     'operations', 'strategy', 'legal', 'finance', 'technology']
        for i, cat in enumerate(categories, 1):
            print(f"  {i}. {cat}")
        category = input("\nCategoría: ").strip().lower()
        results = search_by_category(category)
        print(f"\n✓ Encontrados {len(results)} archivos:")
        for r in results[:50]:
            print(f"  - {r}")
        if len(results) > 50:
            print(f"  ... y {len(results) - 50} más")
    
    elif choice == '4':
        extension = input("Extensión (ej: md, py, csv): ").strip()
        results = search_by_extension(extension)
        print(f"\n✓ Encontrados {len(results)} archivos:")
        for r in results[:50]:
            print(f"  - {r}")
        if len(results) > 50:
            print(f"  ... y {len(results) - 50} más")
    
    elif choice == '5':
        name_pattern = input("Patrón en nombre (opcional, Enter para omitir): ").strip()
        content_pattern = input("Patrón en contenido (opcional, Enter para omitir): ").strip()
        category = input("Categoría (opcional, Enter para omitir): ").strip().lower()
        extension = input("Extensión (opcional, Enter para omitir): ").strip()
        
        # Combinar búsquedas
        all_results = set()
        
        if name_pattern:
            results = search_by_name(name_pattern)
            all_results.update(results)
        
        if content_pattern:
            results = [r[0] for r in search_by_content(content_pattern)]
            if all_results:
                all_results = all_results.intersection(set(results))
            else:
                all_results.update(results)
        
        if category:
            results = search_by_category(category)
            if all_results:
                all_results = all_results.intersection(set(results))
            else:
                all_results.update(results)
        
        if extension:
            results = search_by_extension(extension)
            if all_results:
                all_results = all_results.intersection(set(results))
            else:
                all_results.update(results)
        
        results = sorted(list(all_results))
        print(f"\n✓ Encontrados {len(results)} archivos:")
        for r in results[:50]:
            print(f"  - {r}")
        if len(results) > 50:
            print(f"  ... y {len(results) - 50} más")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # Modo línea de comandos
        if sys.argv[1] == 'name' and len(sys.argv) > 2:
            results = search_by_name(sys.argv[2])
            for r in results:
                print(r)
        elif sys.argv[1] == 'content' and len(sys.argv) > 2:
            results = search_by_content(sys.argv[2])
            for r, count in results:
                print(f"{r} ({count} coincidencias)")
        elif sys.argv[1] == 'category' and len(sys.argv) > 2:
            results = search_by_category(sys.argv[2])
            for r in results:
                print(r)
        elif sys.argv[1] == 'ext' and len(sys.argv) > 2:
            results = search_by_extension(sys.argv[2])
            for r in results:
                print(r)
        else:
            print("Uso: python3 search_files.py [name|content|category|ext] <patrón>")
    else:
        # Modo interactivo
        interactive_search()









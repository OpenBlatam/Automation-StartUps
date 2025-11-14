#!/usr/bin/env python3
"""
Script para encontrar enlaces rotos en documentos Markdown
"""
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent.parent

def find_links_in_file(file_path):
    """Encuentra todos los enlaces en un archivo"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return []
    
    links = []
    
    # Enlaces Markdown [text](url)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    for match in link_pattern.finditer(content):
        link_text, link_url = match.groups()
        line_num = content[:match.start()].count('\n') + 1
        links.append({
            'text': link_text,
            'url': link_url,
            'line': line_num,
            'type': 'markdown'
        })
    
    # Enlaces HTML <a href="...">
    html_link_pattern = re.compile(r'<a\s+href=["\']([^"\']+)["\']')
    for match in html_link_pattern.finditer(content):
        link_url = match.group(1)
        line_num = content[:match.start()].count('\n') + 1
        links.append({
            'text': '',
            'url': link_url,
            'line': line_num,
            'type': 'html'
        })
    
    return links

def check_link(file_path, link_url):
    """Verifica si un enlace es válido"""
    # Enlaces externos
    if link_url.startswith(('http://', 'https://', 'mailto:', 'tel:')):
        return {'valid': True, 'type': 'external', 'reason': 'Enlace externo'}
    
    # Anclas (fragmentos)
    if link_url.startswith('#'):
        return {'valid': True, 'type': 'anchor', 'reason': 'Ancla interna'}
    
    # Enlaces relativos
    if link_url.startswith('/'):
        target_path = BASE_DIR / link_url.lstrip('/')
    else:
        # Relativo al archivo actual
        target_path = file_path.parent / link_url
    
    # Resolver .. y .
    target_path = target_path.resolve()
    
    # Verificar si existe
    if target_path.exists():
        return {'valid': True, 'type': 'internal', 'reason': 'Archivo existe'}
    else:
        # Verificar si es un directorio sin index
        if target_path.is_dir():
            # Buscar index.md o README.md
            for index_file in ['index.md', 'INDEX.md', 'README.md', 'readme.md']:
                if (target_path / index_file).exists():
                    return {'valid': True, 'type': 'internal', 'reason': 'Directorio con índice'}
            return {'valid': False, 'type': 'internal', 'reason': 'Directorio sin índice'}
        else:
            return {'valid': False, 'type': 'internal', 'reason': 'Archivo no encontrado'}

def scan_for_broken_links(folder_path=None, max_files=None):
    """Escanea archivos buscando enlaces rotos"""
    if folder_path is None:
        folder_path = BASE_DIR
    
    broken_links = []
    valid_links = []
    external_links = []
    
    count = 0
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            if max_files and count >= max_files:
                break
            
            file_path = Path(root) / file
            count += 1
            
            links = find_links_in_file(file_path)
            
            for link in links:
                result = check_link(file_path, link['url'])
                link_info = {
                    'file': str(file_path.relative_to(BASE_DIR)),
                    'line': link['line'],
                    'text': link['text'],
                    'url': link['url'],
                    'result': result
                }
                
                if result['valid']:
                    if result['type'] == 'external':
                        external_links.append(link_info)
                    else:
                        valid_links.append(link_info)
                else:
                    broken_links.append(link_info)
    
    return broken_links, valid_links, external_links

def generate_links_report(folder_path=None, max_files=500):
    """Genera reporte de enlaces"""
    print("🔍 Escaneando enlaces en documentos...")
    
    broken, valid, external = scan_for_broken_links(folder_path, max_files)
    
    print("\n" + "="*80)
    print("📋 REPORTE DE ENLACES")
    print("="*80)
    
    total = len(broken) + len(valid) + len(external)
    
    print(f"\n📊 ESTADÍSTICAS")
    print(f"  Total de enlaces encontrados: {total:,}")
    print(f"  ✅ Enlaces válidos (internos): {len(valid):,}")
    print(f"  🌐 Enlaces externos: {len(external):,}")
    print(f"  ❌ Enlaces rotos: {len(broken):,}")
    
    if broken:
        print(f"\n❌ ENLACES ROTOS ({len(broken)}):")
        
        # Agrupar por archivo
        by_file = defaultdict(list)
        for link in broken:
            by_file[link['file']].append(link)
        
        print(f"\n  Archivos con enlaces rotos: {len(by_file)}")
        print(f"\n  Detalles (primeros 20 archivos):")
        
        for i, (file_path, links) in enumerate(list(by_file.items())[:20], 1):
            print(f"\n  {i}. {file_path}")
            for link in links[:5]:  # Máximo 5 por archivo
                print(f"     Línea {link['line']}: {link['url']}")
                print(f"       Texto: {link['text'][:50] if link['text'] else '(sin texto)'}")
                print(f"       Razón: {link['result']['reason']}")
            if len(links) > 5:
                print(f"     ... y {len(links) - 5} enlaces rotos más en este archivo")
        
        if len(by_file) > 20:
            print(f"\n  ... y {len(by_file) - 20} archivos más con enlaces rotos")
    else:
        print("\n✅ ¡No se encontraron enlaces rotos!")
    
    if external:
        print(f"\n🌐 ENLACES EXTERNOS ({len(external)}):")
        print(f"  (Estos no se verifican, solo se cuentan)")
        
        # Agrupar por dominio
        domains = defaultdict(int)
        for link in external:
            if link['url'].startswith('http'):
                try:
                    from urllib.parse import urlparse
                    domain = urlparse(link['url']).netloc
                    domains[domain] += 1
                except:
                    domains['(desconocido)'] += 1
        
        print(f"\n  Dominios más comunes (Top 10):")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1])[:10]:
            print(f"    {domain}: {count} enlaces")

if __name__ == '__main__':
    import sys
    
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    max_files = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    generate_links_report(folder, max_files)








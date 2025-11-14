#!/usr/bin/env python3
"""
Script para analizar la estructura de documentos y generar insights
"""
import os
import re
from pathlib import Path
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).parent.parent.parent

def analyze_document_structure(file_path):
    """Analiza la estructura de un documento"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return None
    
    analysis = {
        'file': str(file_path.relative_to(BASE_DIR)),
        'lines': len(content.split('\n')),
        'words': len(re.findall(r'\b\w+\b', content)),
        'headers': [],
        'sections': [],
        'code_blocks': 0,
        'links': 0,
        'images': 0,
        'lists': 0,
        'tables': 0,
        'has_frontmatter': content.startswith('---'),
        'complexity_score': 0
    }
    
    lines = content.split('\n')
    
    # Analizar headers
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            header_text = line.lstrip('#').strip()
            analysis['headers'].append({
                'level': level,
                'line': i,
                'text': header_text[:50]
            })
            analysis['complexity_score'] += level
    
    # Contar secciones (headers de nivel 1 y 2)
    analysis['sections'] = [h for h in analysis['headers'] if h['level'] <= 2]
    
    # Contar bloques de código
    code_blocks = re.findall(r'```[\s\S]*?```', content)
    analysis['code_blocks'] = len(code_blocks)
    analysis['complexity_score'] += len(code_blocks) * 2
    
    # Contar enlaces
    links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
    analysis['links'] = len(links)
    
    # Contar imágenes
    images = re.findall(r'!\[([^\]]*)\]\(([^\)]+)\)', content)
    analysis['images'] = len(images)
    
    # Contar listas
    list_items = re.findall(r'^[\s]*[-*+]\s+', content, re.MULTILINE)
    analysis['lists'] = len(list_items)
    
    # Contar tablas
    tables = re.findall(r'\|.*\|', content)
    if tables:
        # Agrupar líneas de tabla consecutivas
        table_count = 0
        in_table = False
        for line in lines:
            if '|' in line and '---' not in line:
                if not in_table:
                    table_count += 1
                    in_table = True
            else:
                in_table = False
        analysis['tables'] = table_count
    
    # Calcular score de complejidad
    analysis['complexity_score'] += analysis['links']
    analysis['complexity_score'] += analysis['images']
    analysis['complexity_score'] += analysis['tables'] * 3
    analysis['complexity_score'] += len(analysis['sections']) * 2
    
    return analysis

def analyze_folder(folder_path, max_files=None):
    """Analiza todos los documentos en una carpeta"""
    analyses = []
    
    count = 0
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            if max_files and count >= max_files:
                break
            
            file_path = Path(root) / file
            analysis = analyze_document_structure(file_path)
            if analysis:
                analyses.append(analysis)
                count += 1
    
    return analyses

def generate_structure_report(folder_path=None, max_files=100):
    """Genera reporte de estructura"""
    if folder_path is None:
        folder_path = BASE_DIR
    
    print(f"📊 Analizando estructura de documentos en {folder_path}...")
    
    analyses = analyze_folder(folder_path, max_files)
    
    if not analyses:
        print("No se encontraron archivos para analizar")
        return
    
    print("\n" + "="*80)
    print("📋 REPORTE DE ESTRUCTURA DE DOCUMENTOS")
    print("="*80)
    
    # Estadísticas generales
    total_lines = sum(a['lines'] for a in analyses)
    total_words = sum(a['words'] for a in analyses)
    total_headers = sum(len(a['headers']) for a in analyses)
    total_sections = sum(len(a['sections']) for a in analyses)
    total_code = sum(a['code_blocks'] for a in analyses)
    total_links = sum(a['links'] for a in analyses)
    total_images = sum(a['images'] for a in analyses)
    
    print(f"\n📊 ESTADÍSTICAS GENERALES")
    print(f"  Archivos analizados: {len(analyses)}")
    print(f"  Total de líneas: {total_lines:,}")
    print(f"  Total de palabras: {total_words:,}")
    print(f"  Promedio líneas/archivo: {total_lines // len(analyses):,}")
    print(f"  Promedio palabras/archivo: {total_words // len(analyses):,}")
    
    print(f"\n📑 ESTRUCTURA")
    print(f"  Total de headers: {total_headers:,}")
    print(f"  Total de secciones (H1/H2): {total_sections:,}")
    print(f"  Promedio headers/archivo: {total_headers // len(analyses):.1f}")
    print(f"  Promedio secciones/archivo: {total_sections // len(analyses):.1f}")
    
    print(f"\n🔗 CONTENIDO")
    print(f"  Bloques de código: {total_code:,}")
    print(f"  Enlaces: {total_links:,}")
    print(f"  Imágenes: {total_images:,}")
    print(f"  Promedio enlaces/archivo: {total_links / len(analyses):.1f}")
    
    # Distribución de complejidad
    complexity_scores = [a['complexity_score'] for a in analyses]
    avg_complexity = sum(complexity_scores) / len(complexity_scores)
    
    print(f"\n📈 COMPLEJIDAD")
    print(f"  Score promedio de complejidad: {avg_complexity:.1f}")
    print(f"  Score mínimo: {min(complexity_scores)}")
    print(f"  Score máximo: {max(complexity_scores)}")
    
    # Archivos más complejos
    sorted_by_complexity = sorted(analyses, key=lambda x: x['complexity_score'], reverse=True)
    print(f"\n🔝 ARCHIVOS MÁS COMPLEJOS (Top 10)")
    for i, analysis in enumerate(sorted_by_complexity[:10], 1):
        print(f"  {i}. {analysis['file']}")
        print(f"     Score: {analysis['complexity_score']}, "
              f"Headers: {len(analysis['headers'])}, "
              f"Líneas: {analysis['lines']}")
    
    # Distribución de headers por nivel
    header_levels = Counter()
    for analysis in analyses:
        for header in analysis['headers']:
            header_levels[f"H{header['level']}"] += 1
    
    if header_levels:
        print(f"\n📊 DISTRIBUCIÓN DE HEADERS POR NIVEL")
        for level, count in sorted(header_levels.items()):
            print(f"  {level}: {count:,}")

if __name__ == '__main__':
    import sys
    
    folder = sys.argv[1] if len(sys.argv) > 1 else None
    max_files = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    
    generate_structure_report(folder, max_files)








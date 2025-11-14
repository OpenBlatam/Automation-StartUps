#!/usr/bin/env python3
"""
Script para analizar contenido de archivos y generar insights
"""
import os
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent.parent

def analyze_markdown_files():
    """Analiza archivos Markdown para extraer información"""
    stats = {
        'total_files': 0,
        'total_words': 0,
        'total_lines': 0,
        'headers': Counter(),
        'code_blocks': 0,
        'links': 0,
        'images': 0,
        'tags': Counter(),
        'categories': Counter(),
        'languages': Counter(),
        'file_sizes': [],
        'most_common_words': Counter(),
    }
    
    # Patrones
    header_pattern = re.compile(r'^#{1,6}\s+(.+)$', re.MULTILINE)
    code_block_pattern = re.compile(r'```[\s\S]*?```')
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
    tag_pattern = re.compile(r'tags?:\s*\[(.*?)\]', re.IGNORECASE)
    category_pattern = re.compile(r'category:\s*["\']?([^"\']+)["\']?', re.IGNORECASE)
    language_pattern = re.compile(r'```(\w+)')
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    
                    stats['total_files'] += 1
                    stats['total_lines'] += len(content.split('\n'))
                    
                    # Palabras (excluyendo código)
                    words = re.findall(r'\b\w+\b', content)
                    stats['total_words'] += len(words)
                    stats['most_common_words'].update([w.lower() for w in words if len(w) > 3])
                    
                    # Headers
                    headers = header_pattern.findall(content)
                    for header in headers:
                        level = len(re.match(r'^#+', content[content.find(header)-10:content.find(header)]).group()) if re.match(r'^#+', content[content.find(header)-10:content.find(header)]) else 1
                        stats['headers'][f'H{level}'] += 1
                    
                    # Code blocks
                    code_blocks = code_block_pattern.findall(content)
                    stats['code_blocks'] += len(code_blocks)
                    
                    # Links
                    links = link_pattern.findall(content)
                    stats['links'] += len(links)
                    
                    # Images
                    images = image_pattern.findall(content)
                    stats['images'] += len(images)
                    
                    # Tags
                    tags = tag_pattern.findall(content)
                    for tag_list in tags:
                        for tag in tag_list.split(','):
                            tag = tag.strip().strip('"\'')
                            if tag:
                                stats['tags'][tag] += 1
                    
                    # Categories
                    categories = category_pattern.findall(content)
                    for cat in categories:
                        stats['categories'][cat] += 1
                    
                    # Languages
                    languages = language_pattern.findall(content)
                    stats['languages'].update(languages)
                    
                    # File size
                    size = file_path.stat().st_size
                    stats['file_sizes'].append(size)
                    
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
    
    return stats

def analyze_keywords():
    """Analiza palabras clave más comunes"""
    keywords = Counter()
    
    # Palabras clave de negocio
    business_keywords = [
        'marketing', 'sales', 'customer', 'client', 'revenue', 'roi',
        'strategy', 'analytics', 'data', 'automation', 'ai', 'ia',
        'email', 'campaign', 'lead', 'conversion', 'engagement',
        'template', 'checklist', 'guide', 'playbook', 'workflow'
    ]
    
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            file_path = Path(root) / file
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                    for keyword in business_keywords:
                        count = content.count(keyword)
                        if count > 0:
                            keywords[keyword] += count
                            
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
    
    return keywords

def generate_content_report():
    """Genera reporte de análisis de contenido"""
    print("📊 Analizando contenido de archivos...")
    
    md_stats = analyze_markdown_files()
    keywords = analyze_keywords()
    
    print("\n" + "="*80)
    print("📄 REPORTE DE ANÁLISIS DE CONTENIDO")
    print("="*80)
    
    print(f"\n📁 ESTADÍSTICAS DE MARKDOWN")
    print(f"  Total de archivos .md: {md_stats['total_files']:,}")
    print(f"  Total de palabras: {md_stats['total_words']:,}")
    print(f"  Total de líneas: {md_stats['total_lines']:,}")
    print(f"  Promedio de palabras por archivo: {md_stats['total_words'] // max(md_stats['total_files'], 1):,}")
    print(f"  Promedio de líneas por archivo: {md_stats['total_lines'] // max(md_stats['total_files'], 1):,}")
    
    print(f"\n📝 ESTRUCTURA DE CONTENIDO")
    print(f"  Bloques de código: {md_stats['code_blocks']:,}")
    print(f"  Enlaces: {md_stats['links']:,}")
    print(f"  Imágenes: {md_stats['images']:,}")
    
    if md_stats['headers']:
        print(f"\n📑 HEADERS POR NIVEL")
        for level, count in sorted(md_stats['headers'].items()):
            print(f"  {level}: {count:,}")
    
    if md_stats['tags']:
        print(f"\n🏷️  TAGS MÁS COMUNES (Top 20)")
        for tag, count in md_stats['tags'].most_common(20):
            print(f"  {tag:30s}: {count:,}")
    
    if md_stats['categories']:
        print(f"\n📂 CATEGORÍAS MÁS COMUNES (Top 20)")
        for cat, count in md_stats['categories'].most_common(20):
            print(f"  {cat:30s}: {count:,}")
    
    if md_stats['languages']:
        print(f"\n💻 LENGUAJES DE CÓDIGO (Top 15)")
        for lang, count in md_stats['languages'].most_common(15):
            print(f"  {lang:20s}: {count:,} bloques")
    
    if keywords:
        print(f"\n🔑 PALABRAS CLAVE DE NEGOCIO (Top 20)")
        for keyword, count in keywords.most_common(20):
            print(f"  {keyword:20s}: {count:,} menciones")
    
    if md_stats['most_common_words']:
        print(f"\n📚 PALABRAS MÁS COMUNES (Top 30, excluyendo comunes)")
        common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        filtered_words = {w: c for w, c in md_stats['most_common_words'].items() if w not in common_words}
        for word, count in Counter(filtered_words).most_common(30):
            print(f"  {word:20s}: {count:,}")

if __name__ == '__main__':
    generate_content_report()









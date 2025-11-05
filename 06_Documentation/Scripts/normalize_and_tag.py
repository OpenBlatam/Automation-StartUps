#!/usr/bin/env python3
import re, os, json
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', 'backups'}

def to_snake_case(s):
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '_', s)
    return s.lower()

def to_pascal_case(s):
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', ' ', s)
    return ''.join(word.capitalize() for word in s.split())

def normalize_file_name(name):
    if name.startswith('.'):
        return name
    stem, suffix = name.rsplit('.', 1) if '.' in name else (name, '')
    normalized = to_snake_case(stem)
    return f"{normalized}.{suffix}" if suffix else normalized

def normalize_dir_name(name):
    if name.startswith('.') or name in EXCLUDE_DIRS:
        return name
    return to_pascal_case(name)

def add_frontmatter_to_md(file_path):
    try:
        content = file_path.read_text(encoding='utf-8')
        if content.startswith('---'):
            return  # already has frontmatter
        
        # Extract category from path
        rel_path = file_path.relative_to(ROOT)
        parts = list(rel_path.parts)
        category = parts[0] if parts else 'General'
        
        # Generate tags based on filename and content
        tags = []
        name_lower = file_path.stem.lower()
        
        # Category-based tags
        if 'marketing' in category.lower():
            tags.extend(['marketing', 'business'])
        elif 'technology' in category.lower():
            tags.extend(['technology', 'technical'])
        elif 'finance' in category.lower():
            tags.extend(['finance', 'business'])
        elif 'ai' in category.lower():
            tags.extend(['ai', 'artificial-intelligence'])
        
        # Content-based tags
        if 'guide' in name_lower or 'guia' in name_lower:
            tags.append('guide')
        if 'template' in name_lower or 'plantilla' in name_lower:
            tags.append('template')
        if 'checklist' in name_lower:
            tags.append('checklist')
        if 'strategy' in name_lower or 'estrategia' in name_lower:
            tags.append('strategy')
        if 'script' in name_lower:
            tags.append('script')
        
        # Remove duplicates and sort
        tags = sorted(list(set(tags)))
        
        frontmatter = f"""---
title: "{file_path.stem.replace('_', ' ').title()}"
category: "{category}"
tags: {json.dumps(tags)}
created: "{datetime.now().strftime('%Y-%m-%d')}"
path: "{str(rel_path)}"
---

"""
        
        new_content = frontmatter + content
        file_path.write_text(new_content, encoding='utf-8')
        return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def normalize_structure():
    renamed_files = []
    renamed_dirs = []
    tagged_files = []
    
    print("Normalizando estructura de archivos y carpetas...")
    
    # First pass: rename directories
    for root, dirs, files in os.walk(ROOT, topdown=False):
        if any(ex in root for ex in EXCLUDE_DIRS):
            continue
        
        for dir_name in dirs:
            if dir_name.startswith('.') or dir_name in EXCLUDE_DIRS:
                continue
            
            old_path = Path(root) / dir_name
            new_name = normalize_dir_name(dir_name)
            if new_name != dir_name:
                new_path = Path(root) / new_name
                try:
                    old_path.rename(new_path)
                    renamed_dirs.append((str(old_path.relative_to(ROOT)), str(new_path.relative_to(ROOT))))
                    print(f"  ✓ Carpeta: {old_path.name} → {new_name}")
                except Exception as e:
                    print(f"  ✗ Error renombrando carpeta {old_path}: {e}")
    
    # Second pass: rename files
    for root, dirs, files in os.walk(ROOT):
        if any(ex in root for ex in EXCLUDE_DIRS):
            continue
        
        for file_name in files:
            if file_name.startswith('.'):
                continue
            
            old_path = Path(root) / file_name
            new_name = normalize_file_name(file_name)
            if new_name != file_name:
                new_path = Path(root) / new_name
                try:
                    old_path.rename(new_path)
                    renamed_files.append((str(old_path.relative_to(ROOT)), str(new_path.relative_to(ROOT))))
                    print(f"  ✓ Archivo: {old_path.name} → {new_name}")
                except Exception as e:
                    print(f"  ✗ Error renombrando archivo {old_path}: {e}")
    
    # Third pass: add frontmatter to .md files
    print("\nAñadiendo frontmatter YAML a archivos .md...")
    for root, dirs, files in os.walk(ROOT):
        if any(ex in root for ex in EXCLUDE_DIRS):
            continue
        
        for file_name in files:
            if file_name.endswith('.md'):
                file_path = Path(root) / file_name
                if add_frontmatter_to_md(file_path):
                    tagged_files.append(str(file_path.relative_to(ROOT)))
    
    # Generate search index
    print("\nGenerando índice de búsqueda...")
    search_index = []
    for root, dirs, files in os.walk(ROOT):
        if any(ex in root for ex in EXCLUDE_DIRS):
            continue
        
        for file_name in files:
            if file_name.endswith('.md'):
                file_path = Path(root) / file_name
                try:
                    content = file_path.read_text(encoding='utf-8')
                    # Extract title from frontmatter or filename
                    title = file_path.stem.replace('_', ' ').title()
                    if content.startswith('---'):
                        lines = content.split('\n')
                        for line in lines[1:]:
                            if line.startswith('title:'):
                                title = line.split(':', 1)[1].strip().strip('"')
                                break
                    
                    search_index.append({
                        'path': str(file_path.relative_to(ROOT)),
                        'title': title,
                        'category': str(file_path.relative_to(ROOT).parts[0]) if file_path.relative_to(ROOT).parts else 'General'
                    })
                except Exception:
                    continue
    
    # Write search index
    search_file = ROOT / '06_Documentation' / 'search_index.json'
    with search_file.open('w', encoding='utf-8') as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)
    
    # Write log
    log_file = ROOT / '06_Documentation' / 'NORMALIZATION_LOG.md'
    log_content = f"""# Log de Normalización

Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Carpetas renombradas: {len(renamed_dirs)}
{chr(10).join([f"- {old} → {new}" for old, new in renamed_dirs[:50]])}
{f"... y {len(renamed_dirs) - 50} más" if len(renamed_dirs) > 50 else ""}

## Archivos renombrados: {len(renamed_files)}
{chr(10).join([f"- {old} → {new}" for old, new in renamed_files[:50]])}
{f"... y {len(renamed_files) - 50} más" if len(renamed_files) > 50 else ""}

## Archivos .md etiquetados: {len(tagged_files)}
{chr(10).join([f"- {path}" for path in tagged_files[:50]])}
{f"... y {len(tagged_files) - 50} más" if len(tagged_files) > 50 else ""}

## Índice de búsqueda
Generado: search_index.json ({len(search_index)} entradas)
"""
    
    log_file.write_text(log_content, encoding='utf-8')
    
    print(f"\nResumen:")
    print(f"  Carpetas renombradas: {len(renamed_dirs)}")
    print(f"  Archivos renombrados: {len(renamed_files)}")
    print(f"  Archivos .md etiquetados: {len(tagged_files)}")
    print(f"  Índice de búsqueda: {len(search_index)} entradas")
    print(f"  Log: {log_file}")

if __name__ == '__main__':
    normalize_structure()

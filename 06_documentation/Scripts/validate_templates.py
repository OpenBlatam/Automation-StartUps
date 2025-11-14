#!/usr/bin/env python3
"""
Script para validar estructura y formato de plantillas y documentos
"""
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent.parent

def validate_markdown_structure(file_path):
    """Valida la estructura de un archivo Markdown"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [f"Error leyendo archivo: {e}"]
    
    # Verificar frontmatter
    if not content.startswith('---'):
        issues.append("❌ No tiene frontmatter YAML")
    else:
        # Verificar que el frontmatter esté cerrado
        frontmatter_end = content.find('---', 3)
        if frontmatter_end == -1:
            issues.append("❌ Frontmatter YAML no cerrado correctamente")
        else:
            frontmatter = content[3:frontmatter_end]
            # Verificar campos comunes
            if 'title:' not in frontmatter:
                issues.append("⚠️  Falta campo 'title' en frontmatter")
            if 'category:' not in frontmatter and 'tags:' not in frontmatter:
                issues.append("⚠️  Falta 'category' o 'tags' en frontmatter")
    
    # Verificar headers
    header_levels = []
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            level = len(line) - len(line.lstrip('#'))
            header_levels.append((i, level, line.strip()))
    
    # Verificar jerarquía de headers
    if header_levels:
        prev_level = 0
        for line_num, level, header in header_levels:
            if level > prev_level + 1:
                issues.append(f"⚠️  Línea {line_num}: Salto de nivel de header (H{prev_level} → H{level})")
            prev_level = level
    
    # Verificar enlaces rotos
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    for match in link_pattern.finditer(content):
        link_text, link_url = match.groups()
        # Verificar si es enlace interno
        if not link_url.startswith(('http://', 'https://', 'mailto:', '#')):
            # Es un enlace relativo
            if link_url.startswith('/'):
                target_path = BASE_DIR / link_url.lstrip('/')
            else:
                target_path = file_path.parent / link_url
            if not target_path.exists():
                issues.append(f"⚠️  Enlace roto: {link_url}")
    
    # Verificar imágenes
    image_pattern = re.compile(r'!\[([^\]]*)\]\(([^\)]+)\)')
    for match in image_pattern.finditer(content):
        alt_text, image_url = match.groups()
        if not image_url.startswith(('http://', 'https://')):
            image_path = file_path.parent / image_url
            if not image_path.exists():
                issues.append(f"⚠️  Imagen no encontrada: {image_url}")
    
    # Verificar código
    code_block_pattern = re.compile(r'```(\w+)?\n([\s\S]*?)```')
    for match in code_block_pattern.finditer(content):
        lang, code = match.groups()
        if not lang:
            issues.append("⚠️  Bloque de código sin especificar lenguaje")
    
    return issues

def validate_template_structure(file_path):
    """Valida estructura específica de plantillas"""
    issues = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"Error leyendo archivo: {e}"]
    
    # Verificar que sea una plantilla
    if 'template' not in file_path.name.lower() and 'plantilla' not in file_path.name.lower():
        return issues  # No es una plantilla
    
    # Verificar campos comunes en plantillas
    template_fields = [
        r'\{.*?nombre.*?\}',
        r'\{.*?email.*?\}',
        r'\{.*?fecha.*?\}',
        r'\{.*?date.*?\}',
    ]
    
    has_fields = False
    for field_pattern in template_fields:
        if re.search(field_pattern, content, re.IGNORECASE):
            has_fields = True
            break
    
    if not has_fields:
        issues.append("⚠️  Plantilla sin campos variables detectados")
    
    # Verificar secciones comunes
    common_sections = ['objetivo', 'instrucciones', 'ejemplo', 'notas']
    content_lower = content.lower()
    found_sections = [sec for sec in common_sections if sec in content_lower]
    
    if len(found_sections) < 2:
        issues.append(f"⚠️  Plantilla con pocas secciones estándar (encontradas: {', '.join(found_sections)})")
    
    return issues

def validate_all_files(folder_path=None, file_pattern=None):
    """Valida todos los archivos en una carpeta"""
    if folder_path is None:
        folder_path = BASE_DIR
    
    results = {
        'valid': [],
        'issues': defaultdict(list),
        'total': 0
    }
    
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        
        for file in files:
            if not file.endswith('.md'):
                continue
            
            if file_pattern and file_pattern not in file:
                continue
            
            file_path = Path(root) / file
            results['total'] += 1
            
            # Validar estructura Markdown
            md_issues = validate_markdown_structure(file_path)
            
            # Validar si es plantilla
            template_issues = []
            if 'template' in file.lower() or 'plantilla' in file.lower():
                template_issues = validate_template_structure(file_path)
            
            all_issues = md_issues + template_issues
            
            if all_issues:
                rel_path = file_path.relative_to(BASE_DIR)
                results['issues'][str(rel_path)] = all_issues
            else:
                rel_path = file_path.relative_to(BASE_DIR)
                results['valid'].append(str(rel_path))
    
    return results

def generate_validation_report(folder_path=None, file_pattern=None):
    """Genera reporte de validación"""
    print("🔍 Validando archivos...")
    
    results = validate_all_files(folder_path, file_pattern)
    
    print("\n" + "="*80)
    print("📋 REPORTE DE VALIDACIÓN")
    print("="*80)
    
    print(f"\n📊 ESTADÍSTICAS")
    print(f"  Total de archivos validados: {results['total']}")
    print(f"  Archivos válidos: {len(results['valid'])}")
    print(f"  Archivos con problemas: {len(results['issues'])}")
    
    if results['issues']:
        print(f"\n⚠️  ARCHIVOS CON PROBLEMAS ({len(results['issues'])}):")
        
        # Agrupar por tipo de problema
        problem_types = defaultdict(int)
        for file_path, issues in results['issues'].items():
            for issue in issues:
                if '❌' in issue:
                    problem_types['Errores críticos'] += 1
                elif '⚠️' in issue:
                    problem_types['Advertencias'] += 1
        
        print("\n  Tipos de problemas:")
        for ptype, count in problem_types.items():
            print(f"    {ptype}: {count}")
        
        print("\n  Detalles (primeros 20 archivos):")
        for i, (file_path, issues) in enumerate(list(results['issues'].items())[:20], 1):
            print(f"\n  {i}. {file_path}")
            for issue in issues:
                print(f"     {issue}")
        
        if len(results['issues']) > 20:
            print(f"\n  ... y {len(results['issues']) - 20} archivos más con problemas")
    else:
        print("\n✅ Todos los archivos son válidos!")
    
    if results['valid']:
        print(f"\n✅ ARCHIVOS VÁLIDOS ({len(results['valid'])}):")
        print(f"  (Mostrando primeros 10)")
        for file_path in results['valid'][:10]:
            print(f"    ✓ {file_path}")
        if len(results['valid']) > 10:
            print(f"    ... y {len(results['valid']) - 10} más")

if __name__ == '__main__':
    import sys
    
    folder = None
    pattern = None
    
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    if len(sys.argv) > 2:
        pattern = sys.argv[2]
    
    generate_validation_report(folder, pattern)








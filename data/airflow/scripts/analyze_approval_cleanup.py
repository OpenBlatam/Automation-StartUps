#!/usr/bin/env python3
"""
Análisis avanzado del DAG approval_cleanup.py

Analiza:
- Funciones duplicadas
- Código muerto
- Complejidad ciclomática
- Dependencias entre funciones
- Oportunidades de refactorización
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import re


def analyze_file_complexity(file_path: Path) -> Dict:
    """Analiza complejidad del archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {'error': f'Syntax error: {e}'}
    
    analysis = {
        'total_lines': len(lines),
        'total_functions': 0,
        'total_classes': 0,
        'functions': [],
        'complex_functions': [],
        'duplicate_functions': [],
        'nested_functions': [],
        'long_functions': [],
    }
    
    # Analizar funciones
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            analysis['total_functions'] += 1
            
            func_info = {
                'name': node.name,
                'lines': node.end_lineno - node.lineno if node.end_lineno else 0,
                'complexity': calculate_complexity(node),
                'has_nested': has_nested_functions(node),
                'line_start': node.lineno,
                'line_end': node.end_lineno,
            }
            
            analysis['functions'].append(func_info)
            
            # Identificar funciones complejas (> 10 complejidad)
            if func_info['complexity'] > 10:
                analysis['complex_functions'].append(func_info)
            
            # Identificar funciones largas (> 100 líneas)
            if func_info['lines'] > 100:
                analysis['long_functions'].append(func_info)
            
            # Identificar funciones con funciones anidadas
            if func_info['has_nested']:
                analysis['nested_functions'].append(func_info)
    
    # Buscar funciones duplicadas (simplificado)
    analysis['duplicate_functions'] = find_similar_functions(analysis['functions'])
    
    return analysis


def calculate_complexity(node: ast.FunctionDef) -> int:
    """Calcula complejidad ciclomática aproximada."""
    complexity = 1  # Base
    
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.ExceptHandler)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    
    return complexity


def has_nested_functions(node: ast.FunctionDef) -> bool:
    """Verifica si una función tiene funciones anidadas."""
    for child in node.body:
        if isinstance(child, ast.FunctionDef):
            return True
    return False


def find_similar_functions(functions: List[Dict]) -> List[Dict]:
    """Encuentra funciones con nombres similares (posible duplicación)."""
    name_parts = defaultdict(list)
    
    for func in functions:
        # Extraer partes del nombre (ej: _archive_requests -> archive, requests)
        parts = re.split(r'[_\s]+', func['name'])
        key = tuple(sorted([p for p in parts if len(p) > 2]))
        if key:
            name_parts[key].append(func)
    
    duplicates = []
    for key, funcs in name_parts.items():
        if len(funcs) > 1:
            duplicates.append({
                'pattern': '_'.join(key),
                'functions': funcs,
                'count': len(funcs)
            })
    
    return duplicates


def find_sql_queries(file_path: Path) -> Dict:
    """Encuentra todas las queries SQL en el archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patrones para encontrar SQL
    sql_patterns = [
        (r'CREATE\s+TABLE[^;]+;', 'CREATE TABLE'),
        (r'SELECT[^;]+;', 'SELECT'),
        (r'INSERT\s+INTO[^;]+;', 'INSERT'),
        (r'UPDATE[^;]+;', 'UPDATE'),
        (r'DELETE\s+FROM[^;]+;', 'DELETE'),
    ]
    
    queries = defaultdict(list)
    for pattern, query_type in sql_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE | re.DOTALL)
        for match in matches:
            query_text = match.group(0).strip()
            if len(query_text) < 200:  # Limitar tamaño
                queries[query_type].append({
                    'text': query_text[:150] + '...' if len(query_text) > 150 else query_text,
                    'line': content[:match.start()].count('\n') + 1
                })
    
    return dict(queries)


def find_imports_usage(file_path: Path) -> Dict:
    """Analiza qué imports se usan realmente."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return {'error': 'Cannot parse file'}
    
    imported_modules = set()
    used_modules = set()
    
    # Encontrar imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_modules.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported_modules.add(node.module.split('.')[0])
    
    # Encontrar uso (simplificado - busca en texto)
    for module in imported_modules:
        if module in content and f'import {module}' not in content:
            used_modules.add(module)
    
    unused = imported_modules - used_modules
    
    return {
        'imported': sorted(imported_modules),
        'used': sorted(used_modules),
        'unused': sorted(unused),
        'total_imported': len(imported_modules),
        'total_unused': len(unused)
    }


def generate_refactoring_suggestions(analysis: Dict) -> List[str]:
    """Genera sugerencias de refactorización."""
    suggestions = []
    
    # Funciones complejas
    if analysis['complex_functions']:
        count = len(analysis['complex_functions'])
        suggestions.append(
            f"🔴 {count} funciones con complejidad > 10. "
            f"Considerar dividir en funciones más pequeñas."
        )
        suggestions.append(
            f"   Top 3: {', '.join([f['name'] for f in sorted(analysis['complex_functions'], key=lambda x: x['complexity'], reverse=True)[:3]])}"
        )
    
    # Funciones largas
    if analysis['long_functions']:
        count = len(analysis['long_functions'])
        suggestions.append(
            f"⚠️  {count} funciones con > 100 líneas. "
            f"Considerar extraer a plugins."
        )
        suggestions.append(
            f"   Top 3: {', '.join([f['name'] for f in sorted(analysis['long_functions'], key=lambda x: x['lines'], reverse=True)[:3]])}"
        )
    
    # Funciones anidadas
    if analysis['nested_functions']:
        count = len(analysis['nested_functions'])
        suggestions.append(
            f"📦 {count} funciones con funciones anidadas. "
            f"Extraer funciones anidadas a plugins."
        )
    
    # Funciones duplicadas
    if analysis['duplicate_functions']:
        count = len(analysis['duplicate_functions'])
        suggestions.append(
            f"🔄 {count} grupos de funciones con nombres similares. "
            f"Posible duplicación de código."
        )
    
    return suggestions


def main():
    """Función principal."""
    # Obtener ruta del archivo
    if len(sys.argv) > 1:
        dag_file = Path(sys.argv[1])
    else:
        script_dir = Path(__file__).parent
        dag_file = script_dir.parent.parent / 'dags' / 'approval_cleanup.py'
    
    if not dag_file.exists():
        print(f"❌ Error: Archivo no encontrado: {dag_file}")
        sys.exit(1)
    
    print("=" * 80)
    print("ANÁLISIS AVANZADO - approval_cleanup.py")
    print("=" * 80)
    print(f"\n📄 Analizando: {dag_file}")
    print()
    
    # Análisis de complejidad
    print("🔍 Analizando complejidad...")
    complexity_analysis = analyze_file_complexity(dag_file)
    
    if 'error' in complexity_analysis:
        print(f"❌ Error: {complexity_analysis['error']}")
        sys.exit(1)
    
    # Análisis de SQL
    print("🔍 Analizando queries SQL...")
    sql_analysis = find_sql_queries(dag_file)
    
    # Análisis de imports
    print("🔍 Analizando imports...")
    imports_analysis = find_imports_usage(dag_file)
    
    # Generar reporte
    print("\n" + "=" * 80)
    print("RESULTADOS DEL ANÁLISIS")
    print("=" * 80)
    print()
    
    # Estadísticas generales
    print("📊 ESTADÍSTICAS GENERALES")
    print("-" * 80)
    print(f"Líneas totales: {complexity_analysis['total_lines']:,}")
    print(f"Funciones totales: {complexity_analysis['total_functions']}")
    print(f"Promedio líneas por función: {complexity_analysis['total_lines'] / max(complexity_analysis['total_functions'], 1):.1f}")
    print()
    
    # Funciones complejas
    if complexity_analysis['complex_functions']:
        print("🔴 FUNCIONES COMPLEJAS (complejidad > 10)")
        print("-" * 80)
        for func in sorted(complexity_analysis['complex_functions'], key=lambda x: x['complexity'], reverse=True)[:10]:
            print(f"  • {func['name']:40s} Complejidad: {func['complexity']:3d}  Líneas: {func['lines']:4d}")
        print()
    
    # Funciones largas
    if complexity_analysis['long_functions']:
        print("⚠️  FUNCIONES LARGAS (> 100 líneas)")
        print("-" * 80)
        for func in sorted(complexity_analysis['long_functions'], key=lambda x: x['lines'], reverse=True)[:10]:
            print(f"  • {func['name']:40s} Líneas: {func['lines']:4d}  Complejidad: {func['complexity']:3d}")
        print()
    
    # Funciones anidadas
    if complexity_analysis['nested_functions']:
        print("📦 FUNCIONES CON FUNCIONES ANIDADAS")
        print("-" * 80)
        for func in complexity_analysis['nested_functions'][:10]:
            print(f"  • {func['name']:40s} Líneas: {func['lines']:4d}")
        print()
    
    # Queries SQL
    if sql_analysis:
        print("🗄️  QUERIES SQL ENCONTRADAS")
        print("-" * 80)
        total_queries = sum(len(queries) for queries in sql_analysis.values())
        print(f"Total queries: {total_queries}")
        for query_type, queries in sql_analysis.items():
            print(f"  {query_type}: {len(queries)}")
        print()
    
    # Imports no usados
    if 'unused' in imports_analysis and imports_analysis['unused']:
        print("📦 IMPORTS POSIBLEMENTE NO USADOS")
        print("-" * 80)
        print(f"Total imports: {imports_analysis['total_imported']}")
        print(f"Posiblemente no usados: {imports_analysis['total_unused']}")
        if imports_analysis['unused']:
            print(f"  {', '.join(imports_analysis['unused'][:10])}")
        print()
    
    # Sugerencias
    suggestions = generate_refactoring_suggestions(complexity_analysis)
    if suggestions:
        print("💡 SUGERENCIAS DE REFACTORIZACIÓN")
        print("-" * 80)
        for suggestion in suggestions:
            print(f"  {suggestion}")
        print()
    
    print("=" * 80)
    
    # Guardar reporte
    report_file = dag_file.parent / 'approval_cleanup_ANALYSIS_REPORT.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("ANÁLISIS AVANZADO - approval_cleanup.py\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Líneas totales: {complexity_analysis['total_lines']:,}\n")
        f.write(f"Funciones totales: {complexity_analysis['total_functions']}\n")
        f.write(f"\nFunciones complejas: {len(complexity_analysis['complex_functions'])}\n")
        f.write(f"Funciones largas: {len(complexity_analysis['long_functions'])}\n")
        f.write(f"Funciones anidadas: {len(complexity_analysis['nested_functions'])}\n")
        f.write(f"\nSugerencias:\n")
        for suggestion in suggestions:
            f.write(f"  {suggestion}\n")
    
    print(f"💾 Reporte guardado en: {report_file}")


if __name__ == '__main__':
    main()



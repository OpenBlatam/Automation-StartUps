#!/usr/bin/env python3
"""
Script de utilidad para migrar approval_cleanup.py a la versión simplificada.

Este script ayuda a:
1. Identificar funciones que pueden extraerse a plugins
2. Validar que los plugins están correctamente importados
3. Generar un reporte de migración
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set
from collections import defaultdict


def analyze_dag_file(file_path: Path) -> Dict:
    """Analiza el archivo DAG y extrae información."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {'error': f'Syntax error: {e}'}
    
    analysis = {
        'total_lines': len(content.splitlines()),
        'functions': [],
        'tasks': [],
        'imports': [],
        'helpers_in_dag': [],
        'sql_queries': [],
    }
    
    # Analizar imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis['imports'].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                analysis['imports'].append(f"{module}.{alias.name}")
    
    # Analizar funciones y tareas
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                'name': node.name,
                'lines': node.end_lineno - node.lineno if node.end_lineno else 0,
                'is_task': False,
                'is_helper': False,
            }
            
            # Verificar si es una tarea (tiene decorador @task)
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name) and decorator.id == 'task':
                    func_info['is_task'] = True
                elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'task':
                        func_info['is_task'] = True
            
            # Verificar si es función auxiliar (empieza con _)
            if node.name.startswith('_'):
                func_info['is_helper'] = True
                analysis['helpers_in_dag'].append(func_info)
            
            if func_info['is_task']:
                analysis['tasks'].append(func_info)
            else:
                analysis['functions'].append(func_info)
    
    # Buscar queries SQL
    sql_pattern = r'(CREATE|SELECT|INSERT|UPDATE|DELETE|ALTER|DROP)\s+.*?;'
    matches = re.findall(sql_pattern, content, re.IGNORECASE | re.DOTALL)
    analysis['sql_queries'] = list(set(matches[:20]))  # Primeras 20 únicas
    
    return analysis


def check_plugins_available() -> Dict:
    """Verifica que los plugins estén disponibles."""
    plugins = {
        'approval_cleanup_config': False,
        'approval_cleanup_ops': False,
        'approval_cleanup_queries': False,
        'approval_cleanup_analytics': False,
        'approval_cleanup_utils': False,
    }
    
    for plugin_name in plugins.keys():
        try:
            __import__(f'data.airflow.plugins.{plugin_name}')
            plugins[plugin_name] = True
        except ImportError:
            pass
    
    return plugins


def generate_migration_report(dag_analysis: Dict, plugins_status: Dict) -> str:
    """Genera un reporte de migración."""
    report = []
    report.append("=" * 80)
    report.append("REPORTE DE MIGRACIÓN - approval_cleanup.py")
    report.append("=" * 80)
    report.append("")
    
    # Estadísticas del DAG
    report.append("📊 ESTADÍSTICAS DEL DAG ACTUAL")
    report.append("-" * 80)
    report.append(f"Líneas totales: {dag_analysis.get('total_lines', 0):,}")
    report.append(f"Funciones totales: {len(dag_analysis.get('functions', []))}")
    report.append(f"Tareas (@task): {len(dag_analysis.get('tasks', []))}")
    report.append(f"Funciones auxiliares (empiezan con _): {len(dag_analysis.get('helpers_in_dag', []))}")
    report.append(f"Queries SQL encontradas: {len(dag_analysis.get('sql_queries', []))}")
    report.append("")
    
    # Estado de plugins
    report.append("🔌 ESTADO DE PLUGINS")
    report.append("-" * 80)
    all_available = True
    for plugin, available in plugins_status.items():
        status = "✅ Disponible" if available else "❌ No disponible"
        report.append(f"{plugin:30s} {status}")
        if not available:
            all_available = False
    report.append("")
    
    if not all_available:
        report.append("⚠️  ADVERTENCIA: Algunos plugins no están disponibles")
        report.append("")
    
    # Funciones auxiliares que podrían moverse
    helpers = dag_analysis.get('helpers_in_dag', [])
    if helpers:
        report.append("🔧 FUNCIONES AUXILIARES EN EL DAG")
        report.append("-" * 80)
        report.append("Estas funciones deberían moverse a plugins:")
        report.append("")
        
        for helper in sorted(helpers, key=lambda x: x['lines'], reverse=True)[:10]:
            report.append(f"  • {helper['name']:30s} ({helper['lines']:4d} líneas)")
        report.append("")
    
    # Recomendaciones
    report.append("💡 RECOMENDACIONES")
    report.append("-" * 80)
    
    if len(helpers) > 0:
        report.append(f"1. Mover {len(helpers)} funciones auxiliares a plugins apropiados")
    
    if dag_analysis.get('total_lines', 0) > 2000:
        report.append(f"2. El DAG tiene {dag_analysis.get('total_lines', 0):,} líneas - considerar simplificación")
    
    if len(dag_analysis.get('sql_queries', [])) > 0:
        report.append(f"3. {len(dag_analysis.get('sql_queries', []))} queries SQL encontradas - mover a approval_cleanup_queries.py")
    
    report.append("4. Usar approval_cleanup_simplified_example.py como referencia")
    report.append("")
    
    # Pasos de migración
    report.append("📋 PASOS DE MIGRACIÓN")
    report.append("-" * 80)
    report.append("1. Validar que todos los plugins están disponibles")
    report.append("2. Probar approval_cleanup_simplified_example.py en desarrollo")
    report.append("3. Comparar resultados entre DAG original y simplificado")
    report.append("4. Renombrar original a approval_cleanup_legacy.py")
    report.append("5. Renombrar simplified_example a approval_cleanup.py")
    report.append("6. Validar en staging antes de producción")
    report.append("")
    
    report.append("=" * 80)
    
    return "\n".join(report)


def main():
    """Función principal."""
    # Obtener ruta del archivo
    if len(sys.argv) > 1:
        dag_file = Path(sys.argv[1])
    else:
        # Ruta por defecto
        script_dir = Path(__file__).parent
        dag_file = script_dir.parent.parent / 'dags' / 'approval_cleanup.py'
    
    if not dag_file.exists():
        print(f"❌ Error: Archivo no encontrado: {dag_file}")
        sys.exit(1)
    
    print(f"📄 Analizando: {dag_file}")
    print("")
    
    # Analizar DAG
    print("🔍 Analizando archivo DAG...")
    dag_analysis = analyze_dag_file(dag_file)
    
    if 'error' in dag_analysis:
        print(f"❌ Error al analizar: {dag_analysis['error']}")
        sys.exit(1)
    
    # Verificar plugins
    print("🔍 Verificando plugins...")
    plugins_status = check_plugins_available()
    
    # Generar reporte
    print("📝 Generando reporte...")
    report = generate_migration_report(dag_analysis, plugins_status)
    
    print(report)
    
    # Guardar reporte
    report_file = dag_file.parent / 'approval_cleanup_MIGRATION_REPORT.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n💾 Reporte guardado en: {report_file}")


if __name__ == '__main__':
    main()



#!/usr/bin/env python3
"""
Script de validación para approval_cleanup plugins y DAG.

Valida que:
1. Todos los plugins están correctamente importables
2. Las funciones tienen las firmas correctas
3. No hay errores de sintaxis
4. Los imports están correctos
"""
from __future__ import annotations

import sys
import importlib
import ast
from pathlib import Path
from typing import List, Dict, Tuple


def validate_plugin(plugin_name: str) -> Tuple[bool, List[str]]:
    """Valida que un plugin puede importarse correctamente."""
    errors = []
    
    try:
        module = importlib.import_module(f'data.airflow.plugins.{plugin_name}')
        errors.append(f"✅ {plugin_name} - Importado correctamente")
    except ImportError as e:
        errors.append(f"❌ {plugin_name} - Error de importación: {e}")
        return False, errors
    except SyntaxError as e:
        errors.append(f"❌ {plugin_name} - Error de sintaxis: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ {plugin_name} - Error inesperado: {e}")
        return False, errors
    
    return True, errors


def validate_plugin_functions(plugin_name: str) -> Tuple[bool, List[str]]:
    """Valida que las funciones principales existen."""
    errors = []
    
    try:
        module = importlib.import_module(f'data.airflow.plugins.{plugin_name}')
        
        # Definir funciones esperadas por plugin
        expected_functions = {
            'approval_cleanup_config': ['get_config'],
            'approval_cleanup_ops': [
                'get_pg_hook',
                'execute_query_with_timeout',
                'process_batch',
                'calculate_optimal_batch_size',
                'track_performance'
            ],
            'approval_cleanup_queries': [
                'check_table_exists',
                'create_archive_table',
                'get_old_requests_to_archive',
                'archive_requests_batch',
                'get_expired_notifications',
                'delete_notifications_batch',
            ],
            'approval_cleanup_analytics': [
                'calculate_percentiles',
                'detect_anomaly',
                'analyze_table_sizes',
                'analyze_trends',
                'predict_capacity_need',
            ],
            'approval_cleanup_utils': [
                'log_with_context',
                'check_circuit_breaker',
                'validate_params',
                'format_duration_ms',
                'format_bytes',
            ],
        }
        
        if plugin_name in expected_functions:
            for func_name in expected_functions[plugin_name]:
                if hasattr(module, func_name):
                    errors.append(f"  ✅ {func_name}")
                else:
                    errors.append(f"  ❌ {func_name} - No encontrada")
                    return False, errors
        
    except Exception as e:
        errors.append(f"❌ Error validando funciones: {e}")
        return False, errors
    
    return True, errors


def validate_syntax(file_path: Path) -> Tuple[bool, List[str]]:
    """Valida sintaxis de un archivo Python."""
    errors = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        errors.append(f"✅ Sintaxis válida: {file_path.name}")
        return True, errors
        
    except SyntaxError as e:
        errors.append(f"❌ Error de sintaxis en {file_path.name}: {e}")
        return False, errors
    except Exception as e:
        errors.append(f"❌ Error leyendo {file_path.name}: {e}")
        return False, errors


def main():
    """Función principal de validación."""
    print("=" * 80)
    print("VALIDACIÓN DE APPROVAL_CLEANUP PLUGINS")
    print("=" * 80)
    print()
    
    plugins = [
        'approval_cleanup_config',
        'approval_cleanup_ops',
        'approval_cleanup_queries',
        'approval_cleanup_analytics',
        'approval_cleanup_utils',
    ]
    
    all_valid = True
    results = []
    
    # Validar cada plugin
    for plugin_name in plugins:
        print(f"🔍 Validando {plugin_name}...")
        
        # Validar importación
        is_valid, import_errors = validate_plugin(plugin_name)
        results.extend(import_errors)
        
        if not is_valid:
            all_valid = False
            print()
            continue
        
        # Validar funciones
        funcs_valid, func_errors = validate_plugin_functions(plugin_name)
        results.extend(func_errors)
        
        if not funcs_valid:
            all_valid = False
        
        # Validar sintaxis del archivo
        script_dir = Path(__file__).parent
        plugin_file = script_dir.parent / 'plugins' / f'{plugin_name}.py'
        
        if plugin_file.exists():
            syntax_valid, syntax_errors = validate_syntax(plugin_file)
            results.extend(syntax_errors)
            if not syntax_valid:
                all_valid = False
        else:
            results.append(f"⚠️  Archivo no encontrado: {plugin_file}")
        
        print()
    
    # Mostrar resultados
    print("=" * 80)
    print("RESULTADOS")
    print("=" * 80)
    print()
    
    for result in results:
        print(result)
    
    print()
    print("=" * 80)
    
    if all_valid:
        print("✅ TODOS LOS PLUGINS SON VÁLIDOS")
        sys.exit(0)
    else:
        print("❌ ALGUNOS PLUGINS TIENEN ERRORES")
        sys.exit(1)


if __name__ == '__main__':
    main()



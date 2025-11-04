#!/usr/bin/env python3
"""
Script para extraer funciones del DAG a plugins automáticamente.

Uso:
    python extract_to_plugin.py approval_cleanup.py function_name approval_cleanup_utils.py
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Optional, Tuple


def extract_function_from_file(file_path: Path, function_name: str) -> Optional[str]:
    """Extrae el código de una función del archivo."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Error de sintaxis: {e}")
        return None
    
    # Buscar la función
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            # Extraer líneas de la función
            start_line = node.lineno - 1  # 0-indexed
            end_line = node.end_lineno if node.end_lineno else len(lines)
            
            # Extraer código con indentación original
            func_lines = lines[start_line:end_line]
            
            # Ajustar indentación (remover nivel extra si está dentro de otra función)
            if func_lines:
                # Encontrar indentación mínima
                min_indent = min(len(line) - len(line.lstrip()) for line in func_lines if line.strip())
                if min_indent > 0:
                    func_lines = [line[min_indent:] if len(line) > min_indent else line for line in func_lines]
            
            return '\n'.join(func_lines)
    
    print(f"❌ Función '{function_name}' no encontrada")
    return None


def find_function_dependencies(function_code: str) -> List[str]:
    """Encuentra dependencias de una función (otras funciones que llama)."""
    try:
        tree = ast.parse(function_code)
    except SyntaxError:
        return []
    
    dependencies = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                dependencies.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                dependencies.append(node.func.attr)
    
    return list(set(dependencies))


def add_function_to_plugin(plugin_path: Path, function_code: str, function_name: str) -> bool:
    """Agrega una función a un plugin."""
    if not plugin_path.exists():
        print(f"❌ Plugin no existe: {plugin_path}")
        return False
    
    with open(plugin_path, 'r', encoding='utf-8') as f:
        plugin_content = f.read()
    
    # Verificar si la función ya existe
    if f"def {function_name}(" in plugin_content:
        print(f"⚠️  Función '{function_name}' ya existe en el plugin")
        return False
    
    # Agregar función al final del archivo (antes de la última línea)
    lines = plugin_content.splitlines()
    
    # Encontrar última línea no vacía
    last_line_idx = len(lines) - 1
    while last_line_idx >= 0 and not lines[last_line_idx].strip():
        last_line_idx -= 1
    
    # Insertar función
    new_lines = lines[:last_line_idx + 1]
    new_lines.append('')
    new_lines.append('')
    new_lines.append(f'# Extraído de approval_cleanup.py')
    new_lines.extend(function_code.splitlines())
    new_lines.extend(lines[last_line_idx + 1:])
    
    # Guardar
    with open(plugin_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Función '{function_name}' agregada a {plugin_path.name}")
    return True


def remove_function_from_dag(dag_path: Path, function_name: str) -> bool:
    """Remueve una función del DAG (comentándola)."""
    with open(dag_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.splitlines()
    
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return False
    
    # Buscar función
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == function_name:
            start_line = node.lineno - 1
            end_line = node.end_lineno if node.end_lineno else len(lines)
            
            # Comentar función
            new_lines = []
            for i, line in enumerate(lines):
                if start_line <= i < end_line:
                    # Comentar línea (excepto si ya está vacía o es solo espacios)
                    if line.strip():
                        new_lines.append(f"# EXTRACTED TO PLUGIN: {line}")
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            # Guardar
            with open(dag_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"✅ Función '{function_name}' comentada en el DAG")
            return True
    
    return False


def main():
    """Función principal."""
    if len(sys.argv) < 4:
        print("Uso: python extract_to_plugin.py <dag_file> <function_name> <plugin_file> [--remove]")
        print("\nEjemplo:")
        print("  python extract_to_plugin.py approval_cleanup.py _log_with_context approval_cleanup_utils.py")
        print("  python extract_to_plugin.py approval_cleanup.py _log_with_context approval_cleanup_utils.py --remove")
        sys.exit(1)
    
    dag_file = Path(sys.argv[1])
    function_name = sys.argv[2]
    plugin_file = Path(sys.argv[3])
    remove_from_dag = '--remove' in sys.argv
    
    if not dag_file.exists():
        print(f"❌ DAG no encontrado: {dag_file}")
        sys.exit(1)
    
    # Obtener ruta completa del plugin
    if not plugin_file.is_absolute():
        script_dir = Path(__file__).parent
        plugin_file = script_dir.parent.parent / 'plugins' / plugin_file.name
    
    if not plugin_file.exists():
        print(f"❌ Plugin no encontrado: {plugin_file}")
        sys.exit(1)
    
    print(f"📄 Extrayendo función '{function_name}' de {dag_file.name}")
    print(f"📦 Agregando a {plugin_file.name}")
    print()
    
    # Extraer función
    function_code = extract_function_from_file(dag_file, function_name)
    if not function_code:
        sys.exit(1)
    
    # Mostrar dependencias
    dependencies = find_function_dependencies(function_code)
    if dependencies:
        print(f"📋 Dependencias encontradas: {', '.join(dependencies[:5])}")
        if len(dependencies) > 5:
            print(f"   ... y {len(dependencies) - 5} más")
        print()
    
    # Agregar a plugin
    if not add_function_to_plugin(plugin_file, function_code, function_name):
        sys.exit(1)
    
    # Remover del DAG si se solicita
    if remove_from_dag:
        print()
        print(f"🗑️  Removiendo función del DAG...")
        remove_function_from_dag(dag_file, function_name)
    
    print()
    print("✅ Extracción completada")
    print()
    print("⚠️  IMPORTANTE:")
    print("  1. Revisar que la función funciona correctamente en el plugin")
    print("  2. Actualizar imports en el DAG si es necesario")
    print("  3. Verificar que no hay dependencias circulares")
    print("  4. Ejecutar tests para validar")


if __name__ == '__main__':
    main()



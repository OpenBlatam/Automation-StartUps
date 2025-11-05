#!/usr/bin/env python3
"""
System Health Check Completo
Verifica estado de todas las herramientas, dependencias y configuraciones
"""
import sys
import subprocess
from pathlib import Path
from collections import defaultdict

def check_python_script(script_path):
    """Verifica si un script Python está disponible y puede ejecutarse"""
    if not script_path.exists():
        return {'available': False, 'error': 'Not found'}
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path), '--help'],
            capture_output=True,
            text=True,
            timeout=5
        )
        return {'available': True, 'executable': True}
    except subprocess.TimeoutExpired:
        return {'available': True, 'executable': False, 'error': 'Timeout'}
    except Exception as e:
        return {'available': True, 'executable': False, 'error': str(e)}

def check_bash_script(script_path):
    """Verifica si un script bash está disponible"""
    if not script_path.exists():
        return {'available': False, 'error': 'Not found'}
    
    # Verificar que sea ejecutable
    import os
    if not os.access(script_path, os.X_OK):
        return {'available': True, 'executable': False, 'error': 'Not executable'}
    
    return {'available': True, 'executable': True}

def check_dependencies():
    """Verifica dependencias del sistema"""
    dependencies = {
        'python3': {'command': 'python3 --version', 'required': True},
        'bash': {'command': 'bash --version', 'required': True},
        'jq': {'command': 'jq --version', 'required': False},
        'openpyxl': {'command': 'python3 -c "import openpyxl"', 'required': False},
        'requests': {'command': 'python3 -c "import requests"', 'required': False}
    }
    
    results = {}
    
    for dep_name, dep_info in dependencies.items():
        try:
            result = subprocess.run(
                dep_info['command'].split(),
                capture_output=True,
                text=True,
                timeout=3
            )
            results[dep_name] = {
                'installed': result.returncode == 0,
                'required': dep_info['required'],
                'version': result.stdout.strip() if result.returncode == 0 else None
            }
        except:
            results[dep_name] = {
                'installed': False,
                'required': dep_info['required']
            }
    
    return results

def check_configurations():
    """Verifica archivos de configuración"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    configs = {
        'CSV Master': root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv',
        '.api_config.json': root_dir / '.api_config.json',
        '.notifications_config.json': root_dir / '.notifications_config.json',
        '.platforms_config.json': root_dir / '.platforms_config.json',
        'custom_metrics.json': root_dir / 'custom_metrics.json',
        '.custom_workflows.json': root_dir / '.custom_workflows.json'
    }
    
    results = {}
    for config_name, config_path in configs.items():
        results[config_name] = {
            'exists': config_path.exists(),
            'path': str(config_path)
        }
    
    return results

def check_directory_structure():
    """Verifica estructura de directorios"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    directories = {
        'tools': script_dir,
        'docs': root_dir / 'docs',
        'assets': root_dir / 'assets',
        'assets/linkedin': root_dir / 'assets' / 'linkedin',
        'exports': root_dir / 'exports',
        'reports': root_dir / 'reports',
        'backups': root_dir / 'backups',
        'versions': root_dir / 'versions'
    }
    
    results = {}
    for dir_name, dir_path in directories.items():
        results[dir_name] = {
            'exists': dir_path.exists() and dir_path.is_dir(),
            'path': str(dir_path)
        }
    
    return results

def calculate_health_score(deps, configs, dirs, tools_status):
    """Calcula health score del sistema"""
    score = 100
    
    # Penalizar dependencias faltantes requeridas
    missing_required = sum(1 for d, r in deps.items() if r['required'] and not r['installed'])
    score -= missing_required * 20
    
    # Penalizar configuraciones críticas faltantes
    critical_configs = ['CSV Master']
    missing_critical = sum(1 for c in critical_configs if not configs.get(c, {}).get('exists'))
    score -= missing_critical * 30
    
    # Penalizar directorios críticos faltantes
    critical_dirs = ['tools', 'docs', 'assets']
    missing_critical_dirs = sum(1 for d in critical_dirs if not dirs.get(d, {}).get('exists'))
    score -= missing_critical_dirs * 10
    
    # Penalizar herramientas no disponibles
    unavailable_tools = sum(1 for status in tools_status.values() if not status.get('available'))
    if tools_status:
        unavailable_pct = unavailable_tools / len(tools_status)
        score -= unavailable_pct * 20
    
    return max(0, min(100, score))

def main():
    print("=" * 80)
    print("🏥 System Health Check Completo")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    
    # Verificar herramientas
    print("🔍 Verificando herramientas...")
    tools_status = {}
    
    for tool_file in sorted(script_dir.glob('*.py')):
        if tool_file.name == 'tools_index.py' or tool_file.name == 'system_health_check.py':
            continue
        tools_status[tool_file.name] = check_python_script(tool_file)
    
    for tool_file in sorted(script_dir.glob('*.sh')):
        tools_status[tool_file.name] = check_bash_script(tool_file)
    
    available_count = sum(1 for s in tools_status.values() if s.get('available'))
    print(f"✅ {available_count}/{len(tools_status)} herramientas disponibles")
    print()
    
    # Verificar dependencias
    print("📦 Verificando dependencias...")
    deps = check_dependencies()
    
    required_installed = sum(1 for d, r in deps.items() if r['required'] and r['installed'])
    required_total = sum(1 for r in deps.values() if r['required'])
    
    print(f"✅ Dependencias requeridas: {required_installed}/{required_total}")
    
    optional_installed = sum(1 for r in deps.values() if not r['required'] and r['installed'])
    optional_total = len([r for r in deps.values() if not r['required']])
    
    if optional_total > 0:
        print(f"ℹ️  Dependencias opcionales: {optional_installed}/{optional_total}")
    print()
    
    # Verificar configuraciones
    print("⚙️  Verificando configuraciones...")
    configs = check_configurations()
    
    configs_exists = sum(1 for c in configs.values() if c['exists'])
    print(f"✅ Configuraciones: {configs_exists}/{len(configs)} presentes")
    print()
    
    # Verificar directorios
    print("📁 Verificando estructura de directorios...")
    dirs = check_directory_structure()
    
    dirs_exists = sum(1 for d in dirs.values() if d['exists'])
    print(f"✅ Directorios: {dirs_exists}/{len(dirs)} presentes")
    print()
    
    # Calcular health score
    health_score = calculate_health_score(deps, configs, dirs, tools_status)
    
    print("=" * 80)
    print(f"🏥 Health Score del Sistema: {health_score}/100")
    print("=" * 80)
    
    if health_score >= 90:
        status = "✅ Excelente"
    elif health_score >= 75:
        status = "✅ Bueno"
    elif health_score >= 60:
        status = "⚠️  Requiere atención"
    else:
        status = "❌ Crítico"
    
    print(f"Estado: {status}")
    print()
    
    # Mostrar problemas
    issues = []
    
    # Dependencias faltantes requeridas
    missing_req = [d for d, r in deps.items() if r['required'] and not r['installed']]
    if missing_req:
        issues.append({
            'type': 'dependency',
            'message': f"Dependencias requeridas faltantes: {', '.join(missing_req)}",
            'action': 'Instalar dependencias requeridas'
        })
    
    # Configuraciones críticas faltantes
    missing_critical_configs = [c for c in ['CSV Master'] if not configs.get(c, {}).get('exists')]
    if missing_critical_configs:
        issues.append({
            'type': 'config',
            'message': f"Configuraciones críticas faltantes: {', '.join(missing_critical_configs)}",
            'action': 'Crear archivos de configuración faltantes'
        })
    
    # Directorios críticos faltantes
    missing_critical_dirs = [d for d in ['tools', 'docs', 'assets'] if not dirs.get(d, {}).get('exists')]
    if missing_critical_dirs:
        issues.append({
            'type': 'structure',
            'message': f"Directorios críticos faltantes: {', '.join(missing_critical_dirs)}",
            'action': 'Crear estructura de directorios'
        })
    
    if issues:
        print("⚠️  Problemas Detectados:")
        print("-" * 80)
        for issue in issues:
            print(f"  • {issue['message']}")
            print(f"    💡 {issue['action']}")
            print()
    else:
        print("✅ No se detectaron problemas críticos")
        print()
    
    # Recomendaciones
    if optional_installed < optional_total:
        print("💡 Recomendaciones:")
        missing_optional = [d for d, r in deps.items() if not r['required'] and not r['installed']]
        if missing_optional:
            print(f"  • Instalar dependencias opcionales para funcionalidad extendida:")
            for dep in missing_optional:
                if dep == 'openpyxl':
                    print(f"    - pip install openpyxl (para export_to_excel.py)")
                elif dep == 'requests':
                    print(f"    - pip install requests (para APIs y notificaciones)")
                elif dep == 'jq':
                    print(f"    - brew install jq (para análisis JSON avanzado)")
        print()

if __name__ == '__main__':
    main()


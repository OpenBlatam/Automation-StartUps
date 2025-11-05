#!/usr/bin/env python3
"""
Sistema de Automatización de Workflows
Ejecuta secuencias de análisis automatizados según configuraciones predefinidas
"""
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

def load_workflows():
    """Carga workflows predefinidos"""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    workflows = {
        'daily': {
            'name': 'Daily Health Check',
            'description': 'Verificación diaria rápida',
            'scripts': ['check_alerts.py', 'validate_utms.py'],
            'schedule': 'daily',
            'time': '09:00'
        },
        'weekly': {
            'name': 'Weekly Analysis',
            'description': 'Análisis semanal completo',
            'scripts': [
                'analyze_assets.sh',
                'validate_utms.py',
                'check_alerts.py',
                'benchmark_creatives.py',
                'generate_performance_report.py'
            ],
            'schedule': 'weekly',
            'day': 'monday',
            'time': '08:00'
        },
        'monthly': {
            'name': 'Monthly Comprehensive',
            'description': 'Análisis mensual comprehensivo',
            'scripts': [
                'analyze_assets.sh',
                'optimize_csv_master.py',
                'analyze_trends.py',
                'predict_creative_performance.py',
                'calculate_roi_and_optimize.py',
                'generate_executive_summary.py',
                'generate_comprehensive_report.py',
                'unified_dashboard.py'
            ],
            'schedule': 'monthly',
            'day': 1,
            'time': '09:00'
        },
        'pre_campaign': {
            'name': 'Pre-Campaign Validation',
            'description': 'Validación antes de lanzar campaña',
            'scripts': [
                'check_alerts.py',
                'validate_utms.py',
                'generate_utm_gaps_report.py',
                'auto_fix_gaps.py',
                'predict_creative_performance.py',
                'benchmark_creatives.py'
            ],
            'schedule': 'on_demand'
        },
        'post_campaign': {
            'name': 'Post-Campaign Analysis',
            'description': 'Análisis después de campaña',
            'scripts': [
                'analyze_real_time_performance.py',
                'calculate_roi_and_optimize.py',
                'detect_anomalies.py',
                'automated_ab_testing.py',
                'machine_learning_optimizer.py',
                'generate_executive_summary.py'
            ],
            'schedule': 'on_demand'
        },
        'optimization': {
            'name': 'Optimization Run',
            'description': 'Workflow de optimización completa',
            'scripts': [
                'analyze_real_time_performance.py',
                'calculate_roi_and_optimize.py',
                'machine_learning_optimizer.py',
                'benchmark_creatives.py',
                'detect_anomalies.py'
            ],
            'schedule': 'on_demand'
        }
    }
    
    # Cargar workflows personalizados si existen
    custom_workflows_path = root_dir / '.custom_workflows.json'
    if custom_workflows_path.exists():
        with open(custom_workflows_path, 'r', encoding='utf-8') as f:
            custom_workflows = json.load(f)
            workflows.update(custom_workflows)
    
    return workflows

def execute_workflow(workflow_name, workflows):
    """Ejecuta un workflow completo"""
    if workflow_name not in workflows:
        print(f"❌ Workflow '{workflow_name}' no encontrado")
        return False
    
    workflow = workflows[workflow_name]
    
    print("=" * 80)
    print(f"🚀 Ejecutando Workflow: {workflow['name']}")
    print("=" * 80)
    print(f"📝 {workflow['description']}")
    print(f"📋 Scripts: {len(workflow['scripts'])}")
    print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    results = []
    
    for script_name in workflow['scripts']:
        script_path = script_dir / script_name
        
        if not script_path.exists():
            print(f"⚠️  Script no encontrado: {script_name}")
            results.append({'script': script_name, 'success': False, 'error': 'Not found'})
            continue
        
        print(f"▶️  Ejecutando: {script_name}")
        
        try:
            # Determinar si es bash o python
            if script_name.endswith('.sh'):
                result = subprocess.run(
                    ['bash', str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=root_dir,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=root_dir,
                    timeout=300
                )
            
            if result.returncode == 0:
                print(f"✅ Completado: {script_name}")
                results.append({'script': script_name, 'success': True})
            else:
                print(f"❌ Error en: {script_name}")
                if result.stderr:
                    print(f"   {result.stderr[:200]}")
                results.append({'script': script_name, 'success': False, 'error': result.stderr[:200]})
        
        except subprocess.TimeoutExpired:
            print(f"⏱️  Timeout en: {script_name}")
            results.append({'script': script_name, 'success': False, 'error': 'Timeout'})
        except Exception as e:
            print(f"❌ Error ejecutando {script_name}: {e}")
            results.append({'script': script_name, 'success': False, 'error': str(e)})
        
        print()
    
    # Resumen
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print("=" * 80)
    print(f"📊 Resumen del Workflow")
    print("=" * 80)
    print(f"✅ Exitosos: {successful}/{total}")
    print(f"❌ Fallidos: {total - successful}/{total}")
    print()
    
    if successful == total:
        print("🎉 Workflow completado exitosamente")
    else:
        failed = [r['script'] for r in results if not r['success']]
        print(f"⚠️  Scripts fallidos: {', '.join(failed)}")
    
    print()
    
    return successful == total

def list_workflows(workflows):
    """Lista todos los workflows disponibles"""
    print("=" * 80)
    print("📋 Workflows Disponibles")
    print("=" * 80)
    print()
    
    for workflow_name, workflow in workflows.items():
        schedule_info = workflow.get('schedule', 'on_demand')
        if schedule_info == 'daily':
            schedule = f"Diario a las {workflow.get('time', 'N/A')}"
        elif schedule_info == 'weekly':
            schedule = f"Semanal ({workflow.get('day', 'N/A')}) a las {workflow.get('time', 'N/A')}"
        elif schedule_info == 'monthly':
            schedule = f"Mensual (día {workflow.get('day', 'N/A')}) a las {workflow.get('time', 'N/A')}"
        else:
            schedule = "Bajo demanda"
        
        print(f"📌 {workflow_name}")
        print(f"   Nombre: {workflow['name']}")
        print(f"   Descripción: {workflow['description']}")
        print(f"   Schedule: {schedule}")
        print(f"   Scripts: {len(workflow['scripts'])}")
        print()

def generate_cron_entries(workflows):
    """Genera entradas de cron para workflows programados"""
    cron_entries = []
    
    for workflow_name, workflow in workflows.items():
        schedule = workflow.get('schedule')
        
        if schedule == 'daily':
            time = workflow.get('time', '09:00')
            hour, minute = time.split(':')
            cron_entries.append(f"{minute} {hour} * * * cd {Path(__file__).parent.parent} && python3 tools/workflow_automation.py {workflow_name}")
        
        elif schedule == 'weekly':
            day = workflow.get('day', 'monday')
            time = workflow.get('time', '08:00')
            hour, minute = time.split(':')
            day_map = {'monday': 1, 'tuesday': 2, 'wednesday': 3, 'thursday': 4, 'friday': 5, 'saturday': 6, 'sunday': 0}
            day_num = day_map.get(day.lower(), 1)
            cron_entries.append(f"{minute} {hour} * * {day_num} cd {Path(__file__).parent.parent} && python3 tools/workflow_automation.py {workflow_name}")
        
        elif schedule == 'monthly':
            day = workflow.get('day', 1)
            time = workflow.get('time', '09:00')
            hour, minute = time.split(':')
            cron_entries.append(f"{minute} {hour} {day} * * cd {Path(__file__).parent.parent} && python3 tools/workflow_automation.py {workflow_name}")
    
    return cron_entries

def main():
    workflows = load_workflows()
    
    if len(sys.argv) < 2:
        list_workflows(workflows)
        print()
        print("Uso:")
        print("  python3 workflow_automation.py <workflow_name>")
        print("  python3 workflow_automation.py list")
        print("  python3 workflow_automation.py cron")
        print()
        return
    
    command = sys.argv[1]
    
    if command == 'list':
        list_workflows(workflows)
    
    elif command == 'cron':
        cron_entries = generate_cron_entries(workflows)
        if cron_entries:
            print("=" * 80)
            print("⏰ Entradas de Cron")
            print("=" * 80)
            print()
            print("# Agregar a crontab: crontab -e")
            print()
            for entry in cron_entries:
                print(entry)
            print()
        else:
            print("ℹ️  No hay workflows programados")
    
    else:
        execute_workflow(command, workflows)

if __name__ == '__main__':
    main()


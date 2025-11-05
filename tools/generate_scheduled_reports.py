#!/usr/bin/env python3
"""
Generador de Reportes Programados

Genera reportes automáticos en horarios específicos y los envía por email/Slack.
Ideal para reportes diarios, semanales y mensuales automáticos.
"""
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Configuración
REPORTS_DIR = Path(__file__).parent.parent / 'reports' / 'scheduled'
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de reportes programados
SCHEDULED_REPORTS = {
    'daily': {
        'scripts': ['quick_status', 'check_alerts', 'analyze'],
        'time': '09:00',
        'frequency': 'daily',
        'output': 'daily_status.md',
        'channels': ['email'],
        'subject': '📊 Daily Creative Status Report'
    },
    'weekly': {
        'scripts': ['comprehensive', 'benchmark', 'intelligent_recommendations'],
        'time': '09:00',
        'frequency': 'monday',
        'output': 'weekly_report.md',
        'channels': ['email', 'slack'],
        'subject': '📈 Weekly Creative Performance Report'
    },
    'monthly': {
        'scripts': ['comprehensive', 'executive', 'roi', 'forecasting'],
        'time': '09:00',
        'frequency': '1st',
        'output': 'monthly_executive.md',
        'channels': ['email', 'slack'],
        'subject': '🎯 Monthly Executive Summary'
    },
    'performance': {
        'scripts': ['performance-report', 'real-time', 'anomalies'],
        'time': '17:00',
        'frequency': 'daily',
        'output': 'daily_performance.md',
        'channels': ['slack'],
        'subject': '⚡ Daily Performance Update'
    }
}

def generate_report(report_type: str) -> bool:
    """Genera un reporte programado"""
    if report_type not in SCHEDULED_REPORTS:
        print(f"❌ Tipo de reporte desconocido: {report_type}")
        return False
    
    config = SCHEDULED_REPORTS[report_type]
    print(f"📊 Generando reporte {report_type}...")
    
    # Ejecutar scripts
    scripts_dir = Path(__file__).parent
    results = []
    
    for script_key in config['scripts']:
        # Mapear a script real
        script_mapping = {
            'quick_status': 'quick_status.py',
            'check_alerts': 'check_alerts.py',
            'analyze': 'analyze_assets.sh',
            'comprehensive': 'generate_comprehensive_report.py',
            'benchmark': 'benchmark_creatives.py',
            'intelligent_recommendations': 'intelligent_recommendations.py',
            'executive': 'generate_executive_summary.py',
            'roi': 'calculate_roi_and_optimize.py',
            'forecasting': 'advanced_forecasting.py',
            'performance-report': 'generate_performance_report.py',
            'real-time': 'analyze_real_time_performance.py',
            'anomalies': 'detect_anomalies.py'
        }
        
        script_name = script_mapping.get(script_key, f'{script_key}.py')
        script_path = scripts_dir / script_name
        
        if not script_path.exists():
            print(f"  ⚠️  Script no encontrado: {script_name}")
            continue
        
        try:
            if script_name.endswith('.sh'):
                result = subprocess.run(
                    ['bash', str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=scripts_dir.parent,
                    timeout=300
                )
            else:
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    capture_output=True,
                    text=True,
                    cwd=scripts_dir.parent,
                    timeout=300
                )
            
            if result.returncode == 0:
                results.append({
                    'script': script_key,
                    'status': 'success',
                    'output': result.stdout[:1000] if result.stdout else 'No output'
                })
                print(f"  ✅ {script_key}")
            else:
                results.append({
                    'script': script_key,
                    'status': 'error',
                    'error': result.stderr[:500] if result.stderr else 'Unknown error'
                })
                print(f"  ❌ {script_key}")
        except Exception as e:
            results.append({
                'script': script_key,
                'status': 'exception',
                'error': str(e)
            })
            print(f"  ❌ {script_key}: {e}")
    
    # Generar reporte consolidado
    report_content = f"""# {config['subject']}

**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Tipo:** {report_type}  
**Frecuencia:** {config['frequency']}

## 📊 Resultados

"""
    
    for result in results:
        status_emoji = '✅' if result['status'] == 'success' else '❌'
        report_content += f"### {status_emoji} {result['script']}\n\n"
        
        if result['status'] == 'success':
            report_content += f"```\n{result['output']}\n```\n\n"
        else:
            report_content += f"**Error:** {result.get('error', 'Unknown')}\n\n"
    
    # Guardar reporte
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = REPORTS_DIR / f"{report_type}_{timestamp}.md"
    report_file.write_text(report_content, encoding='utf-8')
    
    print(f"  📄 Reporte guardado: {report_file}")
    
    # Enviar notificaciones si está configurado
    if config.get('channels'):
        # Intentar enviar notificaciones
        notify_script = scripts_dir / 'send_notifications.py'
        if notify_script.exists():
            try:
                subprocess.run(
                    [sys.executable, str(notify_script), '--report', str(report_file)],
                    cwd=scripts_dir.parent,
                    timeout=30
                )
                print(f"  📧 Notificaciones enviadas a: {', '.join(config['channels'])}")
            except:
                print(f"  ⚠️  No se pudieron enviar notificaciones")
    
    return True

def generate_cron_config() -> str:
    """Genera configuración de cron para reportes automáticos"""
    cron_lines = []
    
    for report_type, config in SCHEDULED_REPORTS.items():
        time_parts = config['time'].split(':')
        hour = time_parts[0]
        minute = time_parts[1] if len(time_parts) > 1 else '0'
        
        script_path = Path(__file__).absolute()
        
        if config['frequency'] == 'daily':
            cron_schedule = f"{minute} {hour} * * *"
        elif config['frequency'] == 'monday':
            cron_schedule = f"{minute} {hour} * * 1"
        elif config['frequency'] == '1st':
            cron_schedule = f"{minute} {hour} 1 * *"
        else:
            continue
        
        cron_lines.append(
            f"# {config['subject']}\n"
            f"{cron_schedule} cd {script_path.parent.parent} && python3 {script_path} {report_type} >> logs/cron.log 2>&1\n"
        )
    
    return "\n".join(cron_lines)

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--cron':
            # Generar configuración de cron
            cron_config = generate_cron_config()
            cron_file = Path(__file__).parent.parent / 'crontab.txt'
            cron_file.write_text(cron_config, encoding='utf-8')
            print("📅 Configuración de cron generada en crontab.txt")
            print("\nPara instalar, ejecuta:")
            print(f"  crontab {cron_file}")
            return
        else:
            # Generar reporte específico
            report_type = sys.argv[1]
            generate_report(report_type)
            return
    
    # Modo interactivo
    print("=" * 80)
    print("📅 Generador de Reportes Programados")
    print("=" * 80)
    print()
    print("Tipos de reportes disponibles:")
    for report_type, config in SCHEDULED_REPORTS.items():
        print(f"  • {report_type:12} - {config['subject']} ({config['frequency']})")
    print()
    
    choice = input("Selecciona tipo de reporte (o 'all' para todos): ").strip().lower()
    
    if choice == 'all':
        for report_type in SCHEDULED_REPORTS.keys():
            print(f"\n{'='*80}")
            generate_report(report_type)
    elif choice in SCHEDULED_REPORTS:
        generate_report(choice)
    else:
        print(f"❌ Tipo desconocido: {choice}")

if __name__ == '__main__':
    main()


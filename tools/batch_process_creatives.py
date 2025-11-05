#!/usr/bin/env python3
"""
Procesamiento batch de múltiples operaciones sobre creativos
Permite ejecutar múltiples validaciones y optimizaciones en una sola corrida
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Lista de scripts disponibles
AVAILABLE_SCRIPTS = {
    'analyze': {
        'script': 'analyze_assets.sh',
        'description': 'Análisis completo de assets',
        'type': 'bash'
    },
    'predict': {
        'script': 'predict_creative_performance.py',
        'description': 'Predicción de performance',
        'type': 'python'
    },
    'optimize': {
        'script': 'optimize_csv_master.py',
        'description': 'Optimización del CSV Master',
        'type': 'python'
    },
    'validate': {
        'script': 'validate_utms.py',
        'description': 'Validación de UTMs',
        'type': 'python'
    },
    'trends': {
        'script': 'analyze_trends.py',
        'description': 'Análisis de tendencias temporales',
        'type': 'python'
    },
    'compare': {
        'script': 'compare_creative_performance.py',
        'description': 'Comparación de performance',
        'type': 'python'
    },
    'gaps': {
        'script': 'generate_utm_gaps_report.py',
        'description': 'Reporte de gaps SVG-CSV',
        'type': 'python'
    },
    'auto-fix': {
        'script': 'auto_fix_gaps.py',
        'description': 'Auto-fix de gaps',
        'type': 'python'
    },
    'dashboard': {
        'script': 'generate_assets_dashboard_html.py',
        'description': 'Generar dashboard HTML',
        'type': 'python'
    },
    'alerts': {
        'script': 'check_alerts.py',
        'description': 'Sistema de alertas',
        'type': 'python'
    },
    'export-excel': {
        'script': 'export_to_excel.py',
        'description': 'Exportar a Excel',
        'type': 'python'
    },
    'performance-report': {
        'script': 'generate_performance_report.py',
        'description': 'Reporte completo de performance',
        'type': 'python'
    },
    'api-docs': {
        'script': 'generate_api_docs.py',
        'description': 'Generar documentación de APIs',
        'type': 'python'
    },
    'benchmark': {
        'script': 'benchmark_creatives.py',
        'description': 'Benchmarking vs. estándares de industria',
        'type': 'python'
    },
    'version': {
        'script': 'create_version_control.py',
        'description': 'Sistema de versionado',
        'type': 'python'
    },
    'notify': {
        'script': 'send_notifications.py',
        'description': 'Enviar notificaciones',
        'type': 'python'
    },
    'real-time': {
        'script': 'analyze_real_time_performance.py',
        'description': 'Análisis de performance en tiempo real',
        'type': 'python'
    },
    'collaboration': {
        'script': 'generate_collaboration_report.py',
        'description': 'Reporte de colaboración',
        'type': 'python'
    },
    'campaign-setup': {
        'script': 'automate_campaign_setup.py',
        'description': 'Automación de setup de campañas',
        'type': 'python'
    },
    'roi': {
        'script': 'calculate_roi_and_optimize.py',
        'description': 'Cálculo de ROI y optimización de budget',
        'type': 'python'
    },
    'executive': {
        'script': 'generate_executive_summary.py',
        'description': 'Resumen ejecutivo de performance',
        'type': 'python'
    },
    'anomalies': {
        'script': 'detect_anomalies.py',
        'description': 'Detección de anomalías',
        'type': 'python'
    },
    'ml-optimize': {
        'script': 'machine_learning_optimizer.py',
        'description': 'Optimización basada en ML',
        'type': 'python'
    },
    'ab-testing': {
        'script': 'automated_ab_testing.py',
        'description': 'A/B testing automatizado',
        'type': 'python'
    },
    'forecasting': {
        'script': 'advanced_forecasting.py',
        'description': 'Forecasting avanzado',
        'type': 'python'
    },
    'custom-metrics': {
        'script': 'generate_custom_metrics.py',
        'description': 'Métricas personalizadas',
        'type': 'python'
    },
    'backup': {
        'script': 'backup_restore_system.py',
        'description': 'Backup y restore',
        'type': 'python'
    },
    'comprehensive': {
        'script': 'generate_comprehensive_report.py',
        'description': 'Reporte comprehensivo',
        'type': 'python'
    },
    'dashboard': {
        'script': 'unified_dashboard.py',
        'description': 'Dashboard unificado',
        'type': 'python'
    },
    'workflow': {
        'script': 'workflow_automation.py',
        'description': 'Automatización de workflows',
        'type': 'python'
    },
    'status': {
        'script': 'quick_status.py',
        'description': 'Status rápido',
        'type': 'python'
    },
    'multi-platform': {
        'script': 'multi_platform_integration.py',
        'description': 'Integración multi-plataforma',
        'type': 'python'
    },
    'recommendations': {
        'script': 'intelligent_recommendations.py',
        'description': 'Recomendaciones inteligentes',
        'type': 'python'
    },
    'auto-optimize': {
        'script': 'auto_optimization_engine.py',
        'description': 'Motor de optimización automática',
        'type': 'python'
    },
    'monitor': {
        'script': 'continuous_health_monitor.py',
        'description': 'Monitor continuo de salud',
        'type': 'python'
    },
    'correlation': {
        'script': 'correlation_analysis.py',
        'description': 'Análisis de correlaciones',
        'type': 'python'
    },
    'custom-script': {
        'script': 'generate_custom_script.py',
        'description': 'Generador de scripts personalizados',
        'type': 'python'
    }
}

def run_script(script_name, script_info):
    """Ejecuta un script"""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_info['script']
    
    if not script_path.exists():
        print(f"  ⚠️  Script no encontrado: {script_info['script']}")
        return False
    
    print(f"  ▶️  Ejecutando: {script_info['description']}...")
    
    try:
        if script_info['type'] == 'bash':
            result = subprocess.run(
                ['bash', str(script_path)],
                capture_output=True,
                text=True,
                cwd=script_dir.parent
            )
        else:  # python
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=script_dir.parent
            )
        
        if result.returncode == 0:
            print(f"  ✅ Completado: {script_info['description']}")
            if result.stdout:
                # Mostrar últimas 3 líneas si hay output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 3:
                    print(f"     ... ({len(lines)} líneas de output)")
                else:
                    for line in lines[-3:]:
                        if line.strip():
                            print(f"     {line}")
            return True
        else:
            print(f"  ❌ Error en {script_info['description']}")
            if result.stderr:
                print(f"     {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error ejecutando {script_info['description']}: {e}")
        return False

def main():
    print("=" * 80)
    print("⚙️  Batch Processing de Creativos")
    print("=" * 80)
    print()
    
    # Presets comunes
    PRESETS = {
        'full': ['analyze', 'validate', 'predict', 'trends', 'gaps', 'dashboard', 'alerts', 'performance-report', 'benchmark'],
        'quick': ['analyze', 'validate', 'alerts'],
        'optimize': ['optimize', 'validate', 'analyze', 'alerts'],
        'report': ['analyze', 'trends', 'compare', 'dashboard', 'performance-report', 'export-excel', 'benchmark'],
        'fix': ['gaps', 'auto-fix', 'validate', 'alerts'],
        'monitoring': ['alerts', 'analyze', 'validate'],
        'export': ['export-excel', 'performance-report', 'dashboard'],
        'benchmark': ['benchmark', 'analyze', 'compare'],
        'version': ['version'],
        'performance': ['real-time', 'benchmark', 'compare'],
        'collaboration': ['collaboration', 'analyze', 'gaps'],
        'roi-analysis': ['roi', 'real-time', 'executive'],
        'executive-report': ['executive', 'roi', 'anomalies'],
        'ml-analysis': ['ml-optimize', 'ab-testing', 'forecasting'],
        'optimization': ['ml-optimize', 'roi', 'benchmark'],
        'comprehensive': ['comprehensive'],
        'backup': ['backup'],
        'intelligent': ['recommendations', 'auto-optimize', 'ml-optimize'],
        'auto-optimize': ['auto-optimize', 'roi', 'recommendations']
    }
    
    # Mostrar opciones
    print("📋 Presets disponibles:")
    for preset_name, scripts in PRESETS.items():
        print(f"  • {preset_name:10} → {', '.join(scripts)}")
    print()
    
    # Determinar qué ejecutar
    if len(sys.argv) > 1:
        if sys.argv[1] in PRESETS:
            scripts_to_run = PRESETS[sys.argv[1]]
            print(f"🎯 Usando preset: {sys.argv[1]}")
        elif sys.argv[1] in AVAILABLE_SCRIPTS:
            scripts_to_run = [sys.argv[1]]
            print(f"🎯 Ejecutando: {sys.argv[1]}")
        else:
            print(f"❌ Preset/script desconocido: {sys.argv[1]}")
            print(f"   Disponibles: {', '.join(PRESETS.keys())} o {', '.join(AVAILABLE_SCRIPTS.keys())}")
            return
    else:
        # Modo interactivo
        print("Selecciona preset o script individual:")
        print("  1. full        - Análisis completo")
        print("  2. quick       - Validación rápida")
        print("  3. optimize    - Optimización y validación")
        print("  4. report      - Reportes y dashboards")
        print("  5. fix         - Detectar y arreglar gaps")
        print("  6. monitoring  - Monitoreo (alertas)")
        print("  7. export      - Exportación completa")
        print("  8. benchmark   - Benchmarking vs. industria")
        print("  9. version     - Versionado de creativos")
        print()
        
        choice = input("Opción (1-9 o nombre del preset/script): ").strip().lower()
        
        preset_map = {
            '1': 'full',
            '2': 'quick',
            '3': 'optimize',
            '4': 'report',
            '5': 'fix',
            '6': 'monitoring',
            '7': 'export',
            '8': 'benchmark',
            '9': 'version'
        }
        
        if choice in preset_map:
            scripts_to_run = PRESETS[preset_map[choice]]
        elif choice in PRESETS:
            scripts_to_run = PRESETS[choice]
        elif choice in AVAILABLE_SCRIPTS:
            scripts_to_run = [choice]
        else:
            print("❌ Opción inválida")
            return
    
    print()
    print(f"🚀 Ejecutando {len(scripts_to_run)} script(s)...")
    print("=" * 80)
    print()
    
    start_time = datetime.now()
    results = {}
    
    for script_name in scripts_to_run:
        if script_name not in AVAILABLE_SCRIPTS:
            print(f"  ⚠️  Script desconocido: {script_name}")
            results[script_name] = False
            continue
        
        script_info = AVAILABLE_SCRIPTS[script_name]
        success = run_script(script_name, script_info)
        results[script_name] = success
        print()
    
    # Resumen
    elapsed = (datetime.now() - start_time).total_seconds()
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("=" * 80)
    print(f"📊 Resumen:")
    print(f"  ✅ Exitosos: {successful}/{total}")
    print(f"  ⏱️  Tiempo total: {elapsed:.1f}s")
    print()
    
    if successful < total:
        failed = [k for k, v in results.items() if not v]
        print(f"  ⚠️  Fallidos: {', '.join(failed)}")
    else:
        print("  🎉 Todos los scripts completados exitosamente")
    print()

if __name__ == '__main__':
    main()


Procesamiento batch de múltiples operaciones sobre creativos
Permite ejecutar múltiples validaciones y optimizaciones en una sola corrida
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Lista de scripts disponibles
AVAILABLE_SCRIPTS = {
    'analyze': {
        'script': 'analyze_assets.sh',
        'description': 'Análisis completo de assets',
        'type': 'bash'
    },
    'predict': {
        'script': 'predict_creative_performance.py',
        'description': 'Predicción de performance',
        'type': 'python'
    },
    'optimize': {
        'script': 'optimize_csv_master.py',
        'description': 'Optimización del CSV Master',
        'type': 'python'
    },
    'validate': {
        'script': 'validate_utms.py',
        'description': 'Validación de UTMs',
        'type': 'python'
    },
    'trends': {
        'script': 'analyze_trends.py',
        'description': 'Análisis de tendencias temporales',
        'type': 'python'
    },
    'compare': {
        'script': 'compare_creative_performance.py',
        'description': 'Comparación de performance',
        'type': 'python'
    },
    'gaps': {
        'script': 'generate_utm_gaps_report.py',
        'description': 'Reporte de gaps SVG-CSV',
        'type': 'python'
    },
    'auto-fix': {
        'script': 'auto_fix_gaps.py',
        'description': 'Auto-fix de gaps',
        'type': 'python'
    },
    'dashboard': {
        'script': 'generate_assets_dashboard_html.py',
        'description': 'Generar dashboard HTML',
        'type': 'python'
    },
    'alerts': {
        'script': 'check_alerts.py',
        'description': 'Sistema de alertas',
        'type': 'python'
    },
    'export-excel': {
        'script': 'export_to_excel.py',
        'description': 'Exportar a Excel',
        'type': 'python'
    },
    'performance-report': {
        'script': 'generate_performance_report.py',
        'description': 'Reporte completo de performance',
        'type': 'python'
    },
    'api-docs': {
        'script': 'generate_api_docs.py',
        'description': 'Generar documentación de APIs',
        'type': 'python'
    },
    'benchmark': {
        'script': 'benchmark_creatives.py',
        'description': 'Benchmarking vs. estándares de industria',
        'type': 'python'
    },
    'version': {
        'script': 'create_version_control.py',
        'description': 'Sistema de versionado',
        'type': 'python'
    },
    'notify': {
        'script': 'send_notifications.py',
        'description': 'Enviar notificaciones',
        'type': 'python'
    },
    'real-time': {
        'script': 'analyze_real_time_performance.py',
        'description': 'Análisis de performance en tiempo real',
        'type': 'python'
    },
    'collaboration': {
        'script': 'generate_collaboration_report.py',
        'description': 'Reporte de colaboración',
        'type': 'python'
    },
    'campaign-setup': {
        'script': 'automate_campaign_setup.py',
        'description': 'Automación de setup de campañas',
        'type': 'python'
    },
    'roi': {
        'script': 'calculate_roi_and_optimize.py',
        'description': 'Cálculo de ROI y optimización de budget',
        'type': 'python'
    },
    'executive': {
        'script': 'generate_executive_summary.py',
        'description': 'Resumen ejecutivo de performance',
        'type': 'python'
    },
    'anomalies': {
        'script': 'detect_anomalies.py',
        'description': 'Detección de anomalías',
        'type': 'python'
    },
    'ml-optimize': {
        'script': 'machine_learning_optimizer.py',
        'description': 'Optimización basada en ML',
        'type': 'python'
    },
    'ab-testing': {
        'script': 'automated_ab_testing.py',
        'description': 'A/B testing automatizado',
        'type': 'python'
    },
    'forecasting': {
        'script': 'advanced_forecasting.py',
        'description': 'Forecasting avanzado',
        'type': 'python'
    },
    'custom-metrics': {
        'script': 'generate_custom_metrics.py',
        'description': 'Métricas personalizadas',
        'type': 'python'
    },
    'backup': {
        'script': 'backup_restore_system.py',
        'description': 'Backup y restore',
        'type': 'python'
    },
    'comprehensive': {
        'script': 'generate_comprehensive_report.py',
        'description': 'Reporte comprehensivo',
        'type': 'python'
    },
    'dashboard': {
        'script': 'unified_dashboard.py',
        'description': 'Dashboard unificado',
        'type': 'python'
    },
    'workflow': {
        'script': 'workflow_automation.py',
        'description': 'Automatización de workflows',
        'type': 'python'
    },
    'status': {
        'script': 'quick_status.py',
        'description': 'Status rápido',
        'type': 'python'
    },
    'multi-platform': {
        'script': 'multi_platform_integration.py',
        'description': 'Integración multi-plataforma',
        'type': 'python'
    },
    'recommendations': {
        'script': 'intelligent_recommendations.py',
        'description': 'Recomendaciones inteligentes',
        'type': 'python'
    },
    'auto-optimize': {
        'script': 'auto_optimization_engine.py',
        'description': 'Motor de optimización automática',
        'type': 'python'
    },
    'tools-index': {
        'script': 'tools_index.py',
        'description': 'Índice maestro de herramientas',
        'type': 'python'
    },
    'health-check': {
        'script': 'system_health_check.py',
        'description': 'Health check completo del sistema',
        'type': 'python'
    },
    'system-summary': {
        'script': 'generate_system_summary.py',
        'description': 'Resumen ejecutivo del sistema',
        'type': 'python'
    },
    'scheduled-reports': {
        'script': 'generate_scheduled_reports.py',
        'description': 'Generador de reportes programados',
        'type': 'python'
    },
    'compare-versions': {
        'script': 'compare_versions.py',
        'description': 'Comparador de versiones',
        'type': 'python'
    },
    'cleanup': {
        'script': 'cleanup_system.py',
        'description': 'Limpieza y mantenimiento',
        'type': 'python'
    },
    'market-intelligence': {
        'script': 'market_intelligence.py',
        'description': 'Market intelligence y análisis competitivo',
        'type': 'python'
    },
    'analytics': {
        'script': 'generate_asset_analytics.py',
        'description': 'Analytics avanzados de assets',
        'type': 'python'
    },
    'generate-variants': {
        'script': 'auto_generate_variants.py',
        'description': 'Generador automático de variantes',
        'type': 'python'
    },
    'predictive': {
        'script': 'predictive_insights.py',
        'description': 'Insights predictivos y recomendaciones',
        'type': 'python'
    },
    'competitive': {
        'script': 'generate_competitor_analysis.py',
        'description': 'Análisis competitivo y benchmarking',
        'type': 'python'
    },
    'kpi-dashboard': {
        'script': 'generate_kpi_dashboard.py',
        'description': 'Dashboard KPIs centralizado',
        'type': 'python'
    },
    'performance-optimizer': {
        'script': 'performance_optimizer.py',
        'description': 'Optimizador automático de performance',
        'type': 'python'
    }
}

def run_script(script_name, script_info):
    """Ejecuta un script"""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_info['script']
    
    if not script_path.exists():
        print(f"  ⚠️  Script no encontrado: {script_info['script']}")
        return False
    
    print(f"  ▶️  Ejecutando: {script_info['description']}...")
    
    try:
        if script_info['type'] == 'bash':
            result = subprocess.run(
                ['bash', str(script_path)],
                capture_output=True,
                text=True,
                cwd=script_dir.parent
            )
        else:  # python
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                cwd=script_dir.parent
            )
        
        if result.returncode == 0:
            print(f"  ✅ Completado: {script_info['description']}")
            if result.stdout:
                # Mostrar últimas 3 líneas si hay output
                lines = result.stdout.strip().split('\n')
                if len(lines) > 3:
                    print(f"     ... ({len(lines)} líneas de output)")
                else:
                    for line in lines[-3:]:
                        if line.strip():
                            print(f"     {line}")
            return True
        else:
            print(f"  ❌ Error en {script_info['description']}")
            if result.stderr:
                print(f"     {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error ejecutando {script_info['description']}: {e}")
        return False

def main():
    print("=" * 80)
    print("⚙️  Batch Processing de Creativos")
    print("=" * 80)
    print()
    
    # Presets comunes
    PRESETS = {
        'full': ['analyze', 'validate', 'predict', 'trends', 'gaps', 'dashboard', 'alerts', 'performance-report', 'benchmark'],
        'quick': ['analyze', 'validate', 'alerts'],
        'optimize': ['optimize', 'validate', 'analyze', 'alerts'],
        'report': ['analyze', 'trends', 'compare', 'dashboard', 'performance-report', 'export-excel', 'benchmark'],
        'fix': ['gaps', 'auto-fix', 'validate', 'alerts'],
        'monitoring': ['alerts', 'analyze', 'validate'],
        'export': ['export-excel', 'performance-report', 'dashboard'],
        'benchmark': ['benchmark', 'analyze', 'compare'],
        'version': ['version'],
        'performance': ['real-time', 'benchmark', 'compare'],
        'collaboration': ['collaboration', 'analyze', 'gaps'],
        'roi-analysis': ['roi', 'real-time', 'executive'],
        'executive-report': ['executive', 'roi', 'anomalies'],
        'ml-analysis': ['ml-optimize', 'ab-testing', 'forecasting'],
        'optimization': ['ml-optimize', 'roi', 'benchmark'],
        'comprehensive': ['comprehensive'],
        'backup': ['backup'],
        'intelligent': ['recommendations', 'auto-optimize', 'ml-optimize'],
        'auto-optimize': ['auto-optimize', 'roi', 'recommendations']
    }
    
    # Mostrar opciones
    print("📋 Presets disponibles:")
    for preset_name, scripts in PRESETS.items():
        print(f"  • {preset_name:10} → {', '.join(scripts)}")
    print()
    
    # Determinar qué ejecutar
    if len(sys.argv) > 1:
        if sys.argv[1] in PRESETS:
            scripts_to_run = PRESETS[sys.argv[1]]
            print(f"🎯 Usando preset: {sys.argv[1]}")
        elif sys.argv[1] in AVAILABLE_SCRIPTS:
            scripts_to_run = [sys.argv[1]]
            print(f"🎯 Ejecutando: {sys.argv[1]}")
        else:
            print(f"❌ Preset/script desconocido: {sys.argv[1]}")
            print(f"   Disponibles: {', '.join(PRESETS.keys())} o {', '.join(AVAILABLE_SCRIPTS.keys())}")
            return
    else:
        # Modo interactivo
        print("Selecciona preset o script individual:")
        print("  1. full        - Análisis completo")
        print("  2. quick       - Validación rápida")
        print("  3. optimize    - Optimización y validación")
        print("  4. report      - Reportes y dashboards")
        print("  5. fix         - Detectar y arreglar gaps")
        print("  6. monitoring  - Monitoreo (alertas)")
        print("  7. export      - Exportación completa")
        print("  8. benchmark   - Benchmarking vs. industria")
        print("  9. version     - Versionado de creativos")
        print()
        
        choice = input("Opción (1-9 o nombre del preset/script): ").strip().lower()
        
        preset_map = {
            '1': 'full',
            '2': 'quick',
            '3': 'optimize',
            '4': 'report',
            '5': 'fix',
            '6': 'monitoring',
            '7': 'export',
            '8': 'benchmark',
            '9': 'version'
        }
        
        if choice in preset_map:
            scripts_to_run = PRESETS[preset_map[choice]]
        elif choice in PRESETS:
            scripts_to_run = PRESETS[choice]
        elif choice in AVAILABLE_SCRIPTS:
            scripts_to_run = [choice]
        else:
            print("❌ Opción inválida")
            return
    
    print()
    print(f"🚀 Ejecutando {len(scripts_to_run)} script(s)...")
    print("=" * 80)
    print()
    
    start_time = datetime.now()
    results = {}
    
    for script_name in scripts_to_run:
        if script_name not in AVAILABLE_SCRIPTS:
            print(f"  ⚠️  Script desconocido: {script_name}")
            results[script_name] = False
            continue
        
        script_info = AVAILABLE_SCRIPTS[script_name]
        success = run_script(script_name, script_info)
        results[script_name] = success
        print()
    
    # Resumen
    elapsed = (datetime.now() - start_time).total_seconds()
    successful = sum(1 for v in results.values() if v)
    total = len(results)
    
    print("=" * 80)
    print(f"📊 Resumen:")
    print(f"  ✅ Exitosos: {successful}/{total}")
    print(f"  ⏱️  Tiempo total: {elapsed:.1f}s")
    print()
    
    if successful < total:
        failed = [k for k, v in results.items() if not v]
        print(f"  ⚠️  Fallidos: {', '.join(failed)}")
    else:
        print("  🎉 Todos los scripts completados exitosamente")
    print()

if __name__ == '__main__':
    main()


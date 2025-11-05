#!/usr/bin/env python3
"""
Índice Maestro de Herramientas
Genera índice completo de todas las herramientas disponibles con descripciones y categorías
"""
import sys
from pathlib import Path
from datetime import datetime

TOOLS_CATALOG = {
    'Análisis y Validación': {
        'analyze_assets.sh': {
            'description': 'Análisis completo de assets con estadísticas avanzadas',
            'category': 'Análisis',
            'dependencies': 'bash, jq (opcional)',
            'output': 'Reporte markdown, JSON, CSV',
            'usage': 'bash tools/analyze_assets.sh'
        },
        'validate_utms.py': {
            'description': 'Validación de UTMs y consistencia',
            'category': 'Validación',
            'dependencies': 'python3',
            'output': 'Reporte de validación',
            'usage': 'python3 tools/validate_utms.py'
        },
        'health_check.sh': {
            'description': 'Health check rápido del sistema',
            'category': 'Validación',
            'dependencies': 'bash',
            'output': 'Status del sistema',
            'usage': 'bash tools/health_check.sh'
        },
        'check_alerts.py': {
            'description': 'Sistema de alertas para monitoreo proactivo',
            'category': 'Monitoreo',
            'dependencies': 'python3',
            'output': 'Alertas priorizadas',
            'usage': 'python3 tools/check_alerts.py'
        },
        'detect_anomalies.py': {
            'description': 'Detección de anomalías en performance',
            'category': 'Monitoreo',
            'dependencies': 'python3, statistics',
            'output': 'Reporte de anomalías',
            'usage': 'python3 tools/detect_anomalies.py'
        }
    },
    'Optimización y Performance': {
        'calculate_roi_and_optimize.py': {
            'description': 'Cálculo de ROI y optimización automática de budget',
            'category': 'Optimización',
            'dependencies': 'python3',
            'output': 'CSV de optimización',
            'usage': 'python3 tools/calculate_roi_and_optimize.py'
        },
        'benchmark_creatives.py': {
            'description': 'Benchmarking vs. estándares de industria',
            'category': 'Análisis',
            'dependencies': 'python3',
            'output': 'Comparación con benchmarks',
            'usage': 'python3 tools/benchmark_creatives.py'
        },
        'auto_optimization_engine.py': {
            'description': 'Motor de optimización automática con scoring',
            'category': 'Optimización',
            'dependencies': 'python3',
            'output': 'JSON de acciones sugeridas',
            'usage': 'python3 tools/auto_optimization_engine.py'
        },
        'machine_learning_optimizer.py': {
            'description': 'Optimización basada en Machine Learning',
            'category': 'ML',
            'dependencies': 'python3',
            'output': 'Patrones y recomendaciones ML',
            'usage': 'python3 tools/machine_learning_optimizer.py'
        },
        'predict_creative_performance.py': {
            'description': 'Predicción de performance basada en benchmarks',
            'category': 'Análisis',
            'dependencies': 'python3',
            'output': 'Predicciones de CTR/CVR/CPA',
            'usage': 'python3 tools/predict_creative_performance.py'
        }
    },
    'Testing y Experimentación': {
        'automated_ab_testing.py': {
            'description': 'A/B Testing automatizado con significancia estadística',
            'category': 'Testing',
            'dependencies': 'python3, math',
            'output': 'Resultados de tests con p-values',
            'usage': 'python3 tools/automated_ab_testing.py'
        },
        'compare_creative_performance.py': {
            'description': 'Comparación de performance de creativos',
            'category': 'Análisis',
            'dependencies': 'python3',
            'output': 'Comparación detallada',
            'usage': 'python3 tools/compare_creative_performance.py'
        }
    },
    'Tendencias y Forecasting': {
        'analyze_trends.py': {
            'description': 'Análisis de tendencias temporales y estacionalidad',
            'category': 'Análisis',
            'dependencies': 'python3',
            'output': 'Patrones temporales y forecast',
            'usage': 'python3 tools/analyze_trends.py'
        },
        'advanced_forecasting.py': {
            'description': 'Forecasting avanzado de métricas futuras',
            'category': 'Forecasting',
            'dependencies': 'python3',
            'output': 'Forecasts 3 meses adelante',
            'usage': 'python3 tools/advanced_forecasting.py'
        }
    },
    'Gestión de Datos': {
        'optimize_csv_master.py': {
            'description': 'Optimización del CSV Master (duplicados, normalización)',
            'category': 'Gestión',
            'dependencies': 'python3',
            'output': 'CSV optimizado con backup',
            'usage': 'python3 tools/optimize_csv_master.py'
        },
        'auto_fix_gaps.py': {
            'description': 'Auto-fix de gaps entre SVGs y CSV',
            'category': 'Gestión',
            'dependencies': 'python3',
            'output': 'CSV actualizado',
            'usage': 'python3 tools/auto_fix_gaps.py'
        },
        'generate_utm_gaps_report.py': {
            'description': 'Reporte detallado de gaps SVG ↔ CSV',
            'category': 'Gestión',
            'dependencies': 'python3',
            'output': 'Reporte de gaps',
            'usage': 'python3 tools/generate_utm_gaps_report.py'
        },
        'backup_restore_system.py': {
            'description': 'Sistema de backup y restore del CSV Master',
            'category': 'Gestión',
            'dependencies': 'python3',
            'output': 'Backups con metadata',
            'usage': 'python3 tools/backup_restore_system.py create'
        },
        'create_version_control.py': {
            'description': 'Sistema de versionado de creativos',
            'category': 'Gestión',
            'dependencies': 'python3',
            'output': 'Versiones con hash MD5',
            'usage': 'python3 tools/create_version_control.py create'
        }
    },
    'Exportación y Reportes': {
        'export_to_excel.py': {
            'description': 'Exporta datos a Excel con formato avanzado',
            'category': 'Exportación',
            'dependencies': 'python3, openpyxl',
            'output': 'Excel con múltiples hojas',
            'usage': 'python3 tools/export_to_excel.py'
        },
        'generate_performance_report.py': {
            'description': 'Reporte completo de performance',
            'category': 'Reportes',
            'dependencies': 'python3',
            'output': 'Markdown con recomendaciones',
            'usage': 'python3 tools/generate_performance_report.py'
        },
        'generate_executive_summary.py': {
            'description': 'Resumen ejecutivo para stakeholders',
            'category': 'Reportes',
            'dependencies': 'python3',
            'output': 'Markdown ejecutivo',
            'usage': 'python3 tools/generate_executive_summary.py'
        },
        'generate_comprehensive_report.py': {
            'description': 'Reporte comprehensivo combinando múltiples análisis',
            'category': 'Reportes',
            'dependencies': 'python3',
            'output': 'Markdown completo',
            'usage': 'python3 tools/generate_comprehensive_report.py'
        },
        'generate_collaboration_report.py': {
            'description': 'Reporte de colaboración y gaps',
            'category': 'Reportes',
            'dependencies': 'python3',
            'output': 'Markdown con recomendaciones de equipo',
            'usage': 'python3 tools/generate_collaboration_report.py'
        }
    },
    'Visualización': {
        'generate_assets_dashboard_html.py': {
            'description': 'Dashboard visual interactivo con Chart.js',
            'category': 'Visualización',
            'dependencies': 'python3',
            'output': 'HTML interactivo',
            'usage': 'python3 tools/generate_assets_dashboard_html.py'
        },
        'unified_dashboard.py': {
            'description': 'Dashboard unificado con todas las métricas',
            'category': 'Visualización',
            'dependencies': 'python3',
            'output': 'HTML con Chart.js',
            'usage': 'python3 tools/unified_dashboard.py'
        }
    },
    'Automatización': {
        'batch_process_creatives.py': {
            'description': 'Procesamiento batch de múltiples operaciones',
            'category': 'Automatización',
            'dependencies': 'python3',
            'output': 'Ejecución de múltiples scripts',
            'usage': 'python3 tools/batch_process_creatives.py full'
        },
        'workflow_automation.py': {
            'description': 'Automatización de workflows predefinidos',
            'category': 'Automatización',
            'dependencies': 'python3',
            'output': 'Workflows ejecutados',
            'usage': 'python3 tools/workflow_automation.py daily'
        },
        'automate_campaign_setup.py': {
            'description': 'Automatización de setup de campañas LinkedIn',
            'category': 'Automatización',
            'dependencies': 'python3',
            'output': 'JSON para importar en LinkedIn',
            'usage': 'python3 tools/automate_campaign_setup.py'
        }
    },
    'Integraciones': {
        'analyze_real_time_performance.py': {
            'description': 'Análisis de performance en tiempo real (APIs)',
            'category': 'Integración',
            'dependencies': 'python3, requests',
            'output': 'Métricas actualizadas en CSV',
            'usage': 'python3 tools/analyze_real_time_performance.py'
        },
        'multi_platform_integration.py': {
            'description': 'Integración multi-plataforma (LinkedIn, Facebook, Google, Twitter)',
            'category': 'Integración',
            'dependencies': 'python3, SDKs de plataformas',
            'output': 'Sincronización cross-platform',
            'usage': 'python3 tools/multi_platform_integration.py all'
        },
        'generate_api_docs.py': {
            'description': 'Genera documentación de APIs con ejemplos',
            'category': 'Documentación',
            'dependencies': 'python3',
            'output': 'Markdown con ejemplos de código',
            'usage': 'python3 tools/generate_api_docs.py'
        }
    },
    'Utilidades': {
        'generate_utm_urls_from_csv.py': {
            'description': 'Genera URLs finales con UTMs desde CSV',
            'category': 'Utilidades',
            'dependencies': 'python3',
            'output': 'URLs completas',
            'usage': 'python3 tools/generate_utm_urls_from_csv.py'
        },
        'generate_utm_suggestions.py': {
            'description': 'Genera sugerencias de UTMs para escenarios',
            'category': 'Utilidades',
            'dependencies': 'python3',
            'output': 'Sugerencias de UTMs',
            'usage': 'python3 tools/generate_utm_suggestions.py'
        },
        'generate_custom_metrics.py': {
            'description': 'Generador de métricas personalizadas',
            'category': 'Utilidades',
            'dependencies': 'python3',
            'output': 'CSV con métricas custom',
            'usage': 'python3 tools/generate_custom_metrics.py'
        },
        'quick_status.py': {
            'description': 'Status rápido del sistema en una línea',
            'category': 'Utilidades',
            'dependencies': 'python3',
            'output': 'Vista compacta',
            'usage': 'python3 tools/quick_status.py'
        },
        'send_notifications.py': {
            'description': 'Sistema de notificaciones (Slack, Email, Teams)',
            'category': 'Notificaciones',
            'dependencies': 'python3, requests',
            'output': 'Notificaciones enviadas',
            'usage': 'python3 tools/send_notifications.py alerts'
        },
        'intelligent_recommendations.py': {
            'description': 'Sistema de recomendaciones inteligentes contextuales',
            'category': 'Inteligencia',
            'dependencies': 'python3',
            'output': 'Recomendaciones priorizadas',
            'usage': 'python3 tools/intelligent_recommendations.py'
        }
    }
}

def check_tool_availability(tool_name):
    """Verifica si una herramienta está disponible"""
    script_dir = Path(__file__).parent
    tool_path = script_dir / tool_name
    
    return tool_path.exists()

def generate_index_markdown():
    """Genera índice completo en Markdown"""
    script_dir = Path(__file__).parent
    
    index = []
    index.append("# 📚 Índice Maestro de Herramientas")
    index.append("")
    index.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    index.append("")
    index.append("---")
    index.append("")
    
    total_tools = 0
    
    for category, tools in TOOLS_CATALOG.items():
        index.append(f"## {category}")
        index.append("")
        index.append("| Herramienta | Descripción | Dependencias | Output | Uso |")
        index.append("|-------------|-------------|--------------|--------|-----|")
        
        for tool_name, tool_info in tools.items():
            available = "✅" if check_tool_availability(tool_name) else "❌"
            index.append(
                f"| {available} `{tool_name}` | {tool_info['description']} | "
                f"{tool_info['dependencies']} | {tool_info['output']} | "
                f"`{tool_info['usage']}` |"
            )
            total_tools += 1
        
        index.append("")
        index.append("---")
        index.append("")
    
    index.append(f"**Total de herramientas:** {total_tools}")
    index.append("")
    
    return '\n'.join(index)

def generate_interactive_index():
    """Genera índice interactivo en consola"""
    print("=" * 80)
    print("📚 Índice Maestro de Herramientas")
    print("=" * 80)
    print()
    
    total_available = 0
    total_tools = 0
    
    for category, tools in TOOLS_CATALOG.items():
        print(f"📁 {category}")
        print("-" * 80)
        
        for tool_name, tool_info in tools.items():
            available = check_tool_availability(tool_name)
            status = "✅" if available else "❌"
            
            if available:
                total_available += 1
            
            total_tools += 1
            
            print(f"  {status} {tool_name}")
            print(f"     📝 {tool_info['description']}")
            print(f"     📦 {tool_info['dependencies']}")
            print(f"     💻 {tool_info['usage']}")
            print()
    
    print("=" * 80)
    print(f"📊 Resumen: {total_available}/{total_tools} herramientas disponibles")
    print("=" * 80)
    print()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--markdown':
        # Generar Markdown
        script_dir = Path(__file__).parent
        root_dir = script_dir.parent
        docs_dir = root_dir / 'docs'
        docs_dir.mkdir(exist_ok=True)
        
        index_md = generate_index_markdown()
        index_path = docs_dir / 'TOOLS_INDEX.md'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_md)
        
        print(f"✅ Índice Markdown generado: {index_path}")
    else:
        # Mostrar índice interactivo
        generate_interactive_index()
        
        print("💡 Para generar índice Markdown:")
        print("   python3 tools/tools_index.py --markdown")

if __name__ == '__main__':
    main()


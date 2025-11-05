#!/usr/bin/env python3
"""
Generador de Reporte Comprehensivo
Combina múltiples análisis en un solo reporte ejecutivo completo
"""
import sys
import subprocess
from pathlib import Path
from datetime import datetime

def run_analysis(script_name):
    """Ejecuta un script de análisis"""
    script_dir = Path(__file__).parent
    script_path = script_dir / script_name
    
    if not script_path.exists():
        return None
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return result.stdout
    except:
        pass
    
    return None

def generate_comprehensive_report():
    """Genera reporte comprehensivo combinando múltiples análisis"""
    print("=" * 80)
    print("📊 Generador de Reporte Comprehensivo")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    reports_dir = root_dir / 'reports'
    reports_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = reports_dir / f'comprehensive_report_{timestamp}.md'
    
    report_sections = []
    
    # Header
    report_sections.append("# 📊 Reporte Comprehensivo de Creativos")
    report_sections.append("")
    report_sections.append(f"**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_sections.append("")
    report_sections.append("---")
    report_sections.append("")
    
    # Sección 1: Resumen Ejecutivo
    print("📝 Generando Resumen Ejecutivo...")
    executive_output = run_analysis('generate_executive_summary.py')
    if executive_output:
        report_sections.append("## 📊 Resumen Ejecutivo")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(executive_output[:1000])  # Primeros 1000 caracteres
        report_sections.append("```")
        report_sections.append("")
        report_sections.append("*Para análisis completo, ver: reports/executive_summary_*.md*")
        report_sections.append("")
    
    # Sección 2: Análisis de ROI
    print("💰 Analizando ROI...")
    roi_output = run_analysis('calculate_roi_and_optimize.py')
    if roi_output:
        report_sections.append("## 💰 Análisis de ROI y Optimización")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(roi_output[:800])
        report_sections.append("```")
        report_sections.append("")
    
    # Sección 3: Benchmarking
    print("📊 Ejecutando Benchmarking...")
    benchmark_output = run_analysis('benchmark_creatives.py')
    if benchmark_output:
        report_sections.append("## 📊 Benchmarking vs. Industria")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(benchmark_output[:800])
        report_sections.append("```")
        report_sections.append("")
    
    # Sección 4: Detección de Anomalías
    print("🔍 Detectando anomalías...")
    anomalies_output = run_analysis('detect_anomalies.py')
    if anomalies_output:
        report_sections.append("## 🔍 Anomalías Detectadas")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(anomalies_output[:800])
        report_sections.append("```")
        report_sections.append("")
    
    # Sección 5: Machine Learning Insights
    print("🤖 Analizando con ML...")
    ml_output = run_analysis('machine_learning_optimizer.py')
    if ml_output:
        report_sections.append("## 🤖 Insights de Machine Learning")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(ml_output[:800])
        report_sections.append("```")
        report_sections.append("")
    
    # Sección 6: A/B Testing
    print("🧪 Analizando A/B Tests...")
    ab_output = run_analysis('automated_ab_testing.py')
    if ab_output:
        report_sections.append("## 🧪 Resultados de A/B Testing")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(ab_output[:800])
        report_sections.append("```")
        report_sections.append("")
    
    # Sección 7: Forecasting
    print("📈 Generando forecasts...")
    forecast_output = run_analysis('advanced_forecasting.py')
    if forecast_output:
        report_sections.append("## 📈 Forecasting (Próximos 3 Meses)")
        report_sections.append("")
        report_sections.append("```")
        report_sections.append(forecast_output[:800])
        report_sections.append("```")
        report_sections.append("")
    
    # Sección 8: Recomendaciones Prioritarias
    report_sections.append("## 💡 Recomendaciones Prioritarias")
    report_sections.append("")
    report_sections.append("Basado en el análisis comprehensivo, las siguientes acciones son recomendadas:")
    report_sections.append("")
    report_sections.append("1. **Revisar anomalías detectadas** - Acción inmediata requerida")
    report_sections.append("2. **Implementar optimización de ROI** - Reasignar budget según recomendaciones")
    report_sections.append("3. **Escalar top performers** - Basado en análisis ML y benchmarking")
    report_sections.append("4. **Continuar A/B testing** - Para validar hipótesis y encontrar ganadores")
    report_sections.append("5. **Monitorear forecasts** - Ajustar estrategia según proyecciones")
    report_sections.append("")
    
    # Footer
    report_sections.append("---")
    report_sections.append("")
    report_sections.append("*Este reporte fue generado automáticamente combinando múltiples análisis.*")
    report_sections.append("*Para análisis detallados de cada sección, consulta los reportes individuales en reports/*")
    report_sections.append("")
    
    # Escribir reporte
    report_content = '\n'.join(report_sections)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print()
    print("=" * 80)
    print(f"✅ Reporte comprehensivo generado: {report_path}")
    print("=" * 80)
    print()
    print("📋 Secciones incluidas:")
    print("   • Resumen Ejecutivo")
    print("   • Análisis de ROI")
    print("   • Benchmarking")
    print("   • Anomalías")
    print("   • Insights de ML")
    print("   • A/B Testing")
    print("   • Forecasting")
    print("   • Recomendaciones Prioritarias")
    print()

def main():
    generate_comprehensive_report()

if __name__ == '__main__':
    main()


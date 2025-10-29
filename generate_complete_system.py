#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
from datetime import datetime

def run_script(script_name):
    """Ejecuta un script Python y maneja errores"""
    try:
        print(f"🔄 Ejecutando {script_name}...")
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"✅ {script_name} completado exitosamente")
            return True
        else:
            print(f"❌ Error en {script_name}: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error ejecutando {script_name}: {str(e)}")
        return False

def generate_complete_system():
    """Genera el sistema completo de Bioclones con todas las características"""
    
    print("🚀 INICIANDO GENERACIÓN DEL SISTEMA COMPLETO")
    print("=" * 70)
    print(f"📅 Fecha: {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}")
    print("=" * 70)
    
    # Lista completa de scripts a ejecutar
    scripts = [
        # Generación de versiones del libro
        "generate_pdf.py",
        "generate_improved_pdf.py", 
        "generate_final_pdf.py",
        "generate_premium_pdf.py",
        "generate_enhanced_pdf.py",
        "generate_luxury_pdf.py",
        "generate_professional_pdf.py",
        "generate_master_pdf.py",
        
        # Análisis y documentación
        "create_analysis_document.py",
        "text_analyzer.py",
        "generate_research_document.py",
        "generate_comparison_document.py"
    ]
    
    # Contadores
    successful = 0
    failed = 0
    
    print("📚 FASE 1: GENERACIÓN DE VERSIONES DEL LIBRO")
    print("-" * 50)
    
    # Ejecutar scripts de generación de versiones
    version_scripts = scripts[:8]
    for script in version_scripts:
        if os.path.exists(script):
            if run_script(script):
                successful += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Script no encontrado: {script}")
            failed += 1
        print("-" * 30)
    
    print("\n📊 FASE 2: ANÁLISIS Y DOCUMENTACIÓN")
    print("-" * 50)
    
    # Ejecutar scripts de análisis
    analysis_scripts = scripts[8:]
    for script in analysis_scripts:
        if os.path.exists(script):
            if run_script(script):
                successful += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Script no encontrado: {script}")
            failed += 1
        print("-" * 30)
    
    # Resumen final
    print("=" * 70)
    print("📊 RESUMEN COMPLETO DEL SISTEMA")
    print("=" * 70)
    print(f"✅ Scripts exitosos: {successful}")
    print(f"❌ Scripts fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(successful/(successful+failed)*100):.1f}%")
    
    if successful > 0:
        print("\n🎉 ¡SISTEMA COMPLETO GENERADO!")
        print("\n📚 ARCHIVOS GENERADOS:")
        
        # Listar archivos PDF generados
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        for pdf_file in sorted(pdf_files):
            size = os.path.getsize(pdf_file)
            print(f"   📄 {pdf_file} ({size:,} bytes)")
        
        # Listar archivos de análisis
        analysis_files = [f for f in os.listdir('.') if f.endswith('.json') or f.endswith('.md')]
        for analysis_file in sorted(analysis_files):
            size = os.path.getsize(analysis_file)
            print(f"   📊 {analysis_file} ({size:,} bytes)")
        
        print(f"\n📊 Total de archivos PDF: {len(pdf_files)}")
        print(f"📊 Total de archivos de análisis: {len(analysis_files)}")
        print(f"💾 Tamaño total: {sum(os.path.getsize(f) for f in pdf_files + analysis_files):,} bytes")
        
        # Categorización de archivos
        print("\n📋 CATEGORIZACIÓN DE ARCHIVOS:")
        
        # Versiones del libro
        book_versions = [f for f in pdf_files if 'bioclones_novela' in f and not 'analisis' in f and not 'investigacion' in f and not 'comparacion' in f]
        print(f"   📖 Versiones del libro: {len(book_versions)}")
        
        # Análisis y documentación
        analysis_docs = [f for f in pdf_files if 'analisis' in f or 'investigacion' in f or 'comparacion' in f]
        print(f"   📊 Documentos de análisis: {len(analysis_docs)}")
        
        # Archivos de datos
        data_files = [f for f in os.listdir('.') if f.endswith('.json') or (f.endswith('.md') and not f.startswith('resumen'))]
        print(f"   📋 Archivos de datos: {len(data_files)}")
        
        # Recomendaciones por categoría
        print("\n🎯 RECOMENDACIONES POR CATEGORÍA:")
        print("   📖 Lectura general: bioclones_novela_final.pdf")
        print("   🏆 Presentaciones: bioclones_novela_luxury.pdf")
        print("   ⚡ Nivel editorial: bioclones_novela_professional.pdf")
        print("   💎 Edición maestra: bioclones_novela_master.pdf")
        print("   📚 Análisis académico: analisis_bioclones.pdf")
        print("   🔬 Investigación: investigacion_literaria_bioclones.pdf")
        print("   📊 Comparación: comparacion_literaria_bioclones.pdf")
        
        # Estadísticas del sistema
        print("\n📈 ESTADÍSTICAS DEL SISTEMA:")
        print(f"   🐍 Scripts Python: {len([f for f in os.listdir('.') if f.endswith('.py')])}")
        print(f"   📄 Documentos PDF: {len(pdf_files)}")
        print(f"   📊 Archivos de datos: {len(analysis_files)}")
        print(f"   📝 Documentación: {len([f for f in os.listdir('.') if f.endswith('.md')])}")
        
        # Características únicas
        print("\n🌟 CARACTERÍSTICAS ÚNICAS DEL SISTEMA:")
        print("   ✅ 8 versiones diferentes del libro")
        print("   ✅ Análisis de texto automático")
        print("   ✅ Documento de investigación académica")
        print("   ✅ Comparación literaria")
        print("   ✅ Generación automática completa")
        print("   ✅ Documentación técnica exhaustiva")
        print("   ✅ Sistema de recomendaciones")
        
    else:
        print("\n❌ No se generaron archivos exitosamente")
    
    print("\n" + "=" * 70)
    print("🏁 SISTEMA COMPLETO FINALIZADO")
    print("=" * 70)
    print("🎉 ¡El proyecto Bioclones ahora es un sistema completo de publicación digital!")
    print("📚 ¡Listo para cualquier uso académico, profesional o personal!")

if __name__ == "__main__":
    generate_complete_system()





















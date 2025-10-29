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

def generate_all_versions():
    """Genera todas las versiones del libro Bioclones"""
    
    print("🚀 INICIANDO GENERACIÓN DE TODAS LAS VERSIONES")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}")
    print("=" * 60)
    
    # Lista de scripts a ejecutar en orden
    scripts = [
        "generate_pdf.py",
        "generate_improved_pdf.py", 
        "generate_final_pdf.py",
        "generate_premium_pdf.py",
        "generate_enhanced_pdf.py",
        "generate_luxury_pdf.py",
        "generate_professional_pdf.py",
        "generate_master_pdf.py",
        "create_analysis_document.py"
    ]
    
    # Contadores
    successful = 0
    failed = 0
    
    # Ejecutar cada script
    for script in scripts:
        if os.path.exists(script):
            if run_script(script):
                successful += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Script no encontrado: {script}")
            failed += 1
        print("-" * 40)
    
    # Resumen final
    print("=" * 60)
    print("📊 RESUMEN DE GENERACIÓN")
    print("=" * 60)
    print(f"✅ Scripts exitosos: {successful}")
    print(f"❌ Scripts fallidos: {failed}")
    print(f"📈 Tasa de éxito: {(successful/(successful+failed)*100):.1f}%")
    
    if successful > 0:
        print("\n🎉 ¡GENERACIÓN COMPLETADA!")
        print("\n📚 ARCHIVOS GENERADOS:")
        
        # Listar archivos PDF generados
        pdf_files = [f for f in os.listdir('.') if f.endswith('.pdf')]
        for pdf_file in sorted(pdf_files):
            size = os.path.getsize(pdf_file)
            print(f"   📄 {pdf_file} ({size:,} bytes)")
        
        print(f"\n📊 Total de archivos PDF: {len(pdf_files)}")
        print(f"💾 Tamaño total: {sum(os.path.getsize(f) for f in pdf_files):,} bytes")
        
        # Recomendaciones
        print("\n🎯 RECOMENDACIONES DE USO:")
        print("   📖 Lectura general: bioclones_novela_final.pdf")
        print("   🏆 Presentaciones: bioclones_novela_luxury.pdf")
        print("   ⚡ Nivel editorial: bioclones_novela_professional.pdf")
        print("   💎 Edición maestra: bioclones_novela_master.pdf")
        print("   📚 Análisis académico: analisis_bioclones.pdf")
        
    else:
        print("\n❌ No se generaron archivos exitosamente")
    
    print("\n" + "=" * 60)
    print("🏁 PROCESO COMPLETADO")
    print("=" * 60)

if __name__ == "__main__":
    generate_all_versions()




















#!/usr/bin/env python3
"""
Script para convertir el testimonial a diferentes formatos
"""

import os
import subprocess
import sys

def print_instructions():
    print("=" * 60)
    print("📄 TESTIMONIAL: CURSO DE IA Y SAAS DE IA APLICADO AL MARKETING")
    print("=" * 60)
    print()
    print("✅ Archivos creados exitosamente:")
    print()
    print("1. 📝 testimonial-ia-marketing.md")
    print("   - Formato: Markdown")
    print("   - Uso: GitHub, GitLab, documentación técnica")
    print()
    print("2. 🌐 testimonial-ia-marketing.html")
    print("   - Formato: HTML con estilos CSS")
    print("   - Uso: Web, presentaciones, conversión a PDF/Word")
    print()
    print("3. 📄 testimonial-ia-marketing-rtf.rtf")
    print("   - Formato: Rich Text Format")
    print("   - Uso: Word, procesadores de texto")
    print()
    print("=" * 60)
    print("🔄 CONVERSIONES DISPONIBLES:")
    print("=" * 60)
    print()
    print("📄 Para crear PDF:")
    print("   1. Abre testimonial-ia-marketing.html en tu navegador")
    print("   2. Presiona Ctrl+P (o Cmd+P en Mac)")
    print("   3. Selecciona 'Guardar como PDF'")
    print("   4. Haz clic en Guardar")
    print()
    print("📝 Para crear Word (.docx):")
    print("   1. Abre testimonial-ia-marketing-rtf.rtf en Word")
    print("   2. Guarda como .docx")
    print("   O")
    print("   1. Abre testimonial-ia-marketing.html en Word")
    print("   2. Guarda como .docx")
    print()
    print("🌐 Para usar en web:")
    print("   1. Sube testimonial-ia-marketing.html a tu servidor")
    print("   2. O copia el contenido a tu CMS")
    print()
    print("=" * 60)
    print("📊 CARACTERÍSTICAS DEL TESTIMONIAL:")
    print("=" * 60)
    print()
    print("✅ Basado en neurociencia del comportamiento")
    print("✅ Incluye métricas específicas y cuantificadas")
    print("✅ Estructura psicológica persuasiva")
    print("✅ Casos de éxito documentados")
    print("✅ ROI detallado ($3,997 → $3,714,000)")
    print("✅ Testimoniales del equipo")
    print("✅ Llamada a la acción clara")
    print("✅ Información de contacto")
    print()
    print("=" * 60)
    print("🎯 PRÓXIMOS PASOS RECOMENDADOS:")
    print("=" * 60)
    print()
    print("1. 📖 Revisa el contenido y personaliza según tu marca")
    print("2. 🎨 Ajusta los colores y estilos en el HTML")
    print("3. 📊 Agrega tus propias métricas y casos de éxito")
    print("4. 📧 Incluye tu información de contacto real")
    print("5. 🚀 Publica en tu sitio web y redes sociales")
    print()
    print("¡Tu testimonial está listo para usar! 🚀💎")

def open_files():
    """Abre los archivos en las aplicaciones predeterminadas"""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["open", "testimonial-ia-marketing.html"])
            print("✅ Abriendo HTML en el navegador...")
        elif sys.platform == "win32":  # Windows
            subprocess.run(["start", "testimonial-ia-marketing.html"], shell=True)
            print("✅ Abriendo HTML en el navegador...")
        else:  # Linux
            subprocess.run(["xdg-open", "testimonial-ia-marketing.html"])
            print("✅ Abriendo HTML en el navegador...")
    except Exception as e:
        print(f"⚠️  No se pudo abrir automáticamente: {e}")
        print("   Abre manualmente testimonial-ia-marketing.html en tu navegador")

if __name__ == "__main__":
    print_instructions()
    print()
    
    response = input("¿Quieres abrir el archivo HTML en tu navegador? (s/n): ").lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        open_files()
    
    print()
    print("¡Gracias por usar el generador de testimonials! 🎉")


#!/usr/bin/env python3
"""
Script para convertir archivos HTML a PDF con mucho estilo
Usando weasyprint para generar PDFs de alta calidad
"""

import os
import sys
from pathlib import Path

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
except ImportError:
    print("❌ Error: weasyprint no está instalado")
    print("Instálalo con: pip install weasyprint")
    sys.exit(1)

def convert_html_to_pdf(html_file, output_file):
    """Convierte un archivo HTML a PDF con estilos optimizados"""
    try:
        print(f"🔄 Convirtiendo {html_file} a PDF...")
        
        # Configuración de fuentes
        font_config = FontConfiguration()
        
        # CSS adicional para optimizar la impresión
        css_content = """
        @page {
            size: A4;
            margin: 0.5in;
        }
        
        body {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        
        .container {
            page-break-inside: avoid;
        }
        
        .bonus-card {
            page-break-inside: avoid;
        }
        """
        
        # Leer el archivo HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Crear el PDF
        html_doc = HTML(string=html_content)
        css_doc = CSS(string=css_content, font_config=font_config)
        
        # Generar el PDF
        html_doc.write_pdf(output_file, stylesheets=[css_doc], font_config=font_config)
        
        print(f"✅ PDF generado exitosamente: {output_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error al convertir {html_file}: {str(e)}")
        return False

def main():
    """Función principal"""
    print("🚀 Iniciando conversión de HTML a PDF...")
    
    # Archivos a convertir
    files_to_convert = [
        ("curso_ia_bonos_exclusivos.html", "Curso_IA_Bonos_Exclusivos.pdf"),
        ("webinar_ia_bonos_exclusivos.html", "Webinar_IA_Bonos_Exclusivos.pdf"),
        ("saas_ia_marketing_bonos_exclusivos.html", "SaaS_IA_Marketing_Bonos_Exclusivos.pdf")
    ]
    
    success_count = 0
    total_files = len(files_to_convert)
    
    for html_file, pdf_file in files_to_convert:
        if os.path.exists(html_file):
            if convert_html_to_pdf(html_file, pdf_file):
                success_count += 1
        else:
            print(f"❌ Archivo no encontrado: {html_file}")
    
    print(f"\n📊 Resumen:")
    print(f"✅ Archivos convertidos exitosamente: {success_count}/{total_files}")
    
    if success_count == total_files:
        print("🎉 ¡Todos los archivos se convirtieron correctamente!")
    else:
        print("⚠️  Algunos archivos no se pudieron convertir")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Script para crear PDF del Curso Premium de IA en Marketing
Usa weasyprint para generar PDF desde HTML
"""

import os
import sys
from pathlib import Path
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def read_md_file(file_path):
    """Lee un archivo Markdown y retorna su contenido"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return ""

def create_html_from_md(md_content):
    """Convierte contenido Markdown a HTML con estilos CSS"""
    
    # Estilos CSS personalizados
    css_styles = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Curso Premium: IA en Marketing";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Página " counter(page);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 100%;
            font-size: 11pt;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            margin-bottom: 20px;
            font-size: 2.2em;
            page-break-before: always;
        }
        
        h1:first-child {
            page-break-before: avoid;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 8px;
            margin-top: 25px;
            margin-bottom: 15px;
            font-size: 1.8em;
        }
        
        h3 {
            color: #2980b9;
            margin-top: 20px;
            margin-bottom: 10px;
            font-size: 1.4em;
        }
        
        h4 {
            color: #8e44ad;
            margin-top: 15px;
            margin-bottom: 8px;
            font-size: 1.2em;
        }
        
        h5, h6 {
            color: #27ae60;
            margin-top: 12px;
            margin-bottom: 6px;
        }
        
        p {
            margin-bottom: 12px;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 15px;
            padding-left: 25px;
        }
        
        li {
            margin-bottom: 5px;
        }
        
        strong {
            color: #e74c3c;
            font-weight: bold;
        }
        
        em {
            color: #8e44ad;
            font-style: italic;
        }
        
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }
        
        pre {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            margin: 15px 0;
            page-break-inside: avoid;
        }
        
        pre code {
            background: none;
            border: none;
            padding: 0;
        }
        
        blockquote {
            border-left: 4px solid #3498db;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #f8f9fa;
            font-style: italic;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            page-break-inside: avoid;
        }
        
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        
        tr:nth-child(even) {
            background-color: #f2f2f2;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .highlight {
            background-color: #fff3cd;
            padding: 10px;
            border-left: 4px solid #ffc107;
            margin: 15px 0;
        }
        
        .success {
            background-color: #d4edda;
            padding: 10px;
            border-left: 4px solid #28a745;
            margin: 15px 0;
        }
        
        .warning {
            background-color: #f8d7da;
            padding: 10px;
            border-left: 4px solid #dc3545;
            margin: 15px 0;
        }
        
        .info {
            background-color: #d1ecf1;
            padding: 10px;
            border-left: 4px solid #17a2b8;
            margin: 15px 0;
        }
        
        hr {
            border: none;
            height: 2px;
            background-color: #3498db;
            margin: 30px 0;
        }
        
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            margin: 20px 0;
        }
        
        .toc h2 {
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            margin-top: 0;
        }
        
        .toc ul {
            list-style-type: none;
            padding-left: 0;
        }
        
        .toc li {
            margin: 8px 0;
        }
        
        .toc a {
            text-decoration: none;
            color: #2980b9;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        .module-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin: 30px 0;
            text-align: center;
        }
        
        .module-header h2 {
            color: white;
            border: none;
            margin: 0;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            background-color: #e74c3c;
            color: white;
            border-radius: 3px;
            font-size: 0.8em;
            font-weight: bold;
            margin: 2px;
        }
        
        .badge.green {
            background-color: #27ae60;
        }
        
        .badge.blue {
            background-color: #3498db;
        }
        
        .badge.purple {
            background-color: #8e44ad;
        }
        
        .badge.orange {
            background-color: #f39c12;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #e74c3c;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
        }
        
        /* Evitar que los títulos queden solos al final de página */
        h1, h2, h3, h4, h5, h6 {
            page-break-after: avoid;
        }
        
        /* Evitar que las listas se rompan */
        ul, ol {
            page-break-inside: avoid;
        }
        
        /* Espaciado entre secciones */
        .section-break {
            page-break-before: always;
            margin-top: 0;
        }
    </style>
    """
    
    # Convertir Markdown a HTML
    html_content = markdown.markdown(
        md_content, 
        extensions=[
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.toc',
            'markdown.extensions.attr_list',
            'markdown.extensions.def_list',
            'markdown.extensions.footnotes',
            'markdown.extensions.md_in_html'
        ]
    )
    
    # Crear HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Curso Premium: Inteligencia Artificial Aplicada al Marketing</title>
        {css_styles}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html

def create_pdf_from_html(html_content, output_path):
    """Convierte HTML a PDF usando WeasyPrint"""
    
    try:
        # Configurar fuentes
        font_config = FontConfiguration()
        
        # Crear CSS adicional para el PDF
        css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
            }
        ''', font_config=font_config)
        
        # Generar PDF
        HTML(string=html_content).write_pdf(
            output_path,
            stylesheets=[css],
            font_config=font_config
        )
        
        return True
    except Exception as e:
        print(f"Error generando PDF: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Generando PDF del Curso Premium de IA en Marketing...")
    
    # Rutas de archivos
    base_dir = Path(".")
    file1 = base_dir / "AI_Marketing_Course_Complete_Structure.md"
    file2 = base_dir / "AI_Marketing_Course_Resources_Delivery_Marketing_Feedback.md"
    output_file = base_dir / "Curso_Premium_IA_Marketing_Completo.pdf"
    
    # Verificar que los archivos existen
    if not file1.exists():
        print(f"❌ Error: No se encontró {file1}")
        return False
    
    if not file2.exists():
        print(f"❌ Error: No se encontró {file2}")
        return False
    
    print("📖 Leyendo archivos Markdown...")
    
    # Leer contenido de ambos archivos
    content1 = read_md_file(file1)
    content2 = read_md_file(file2)
    
    if not content1 or not content2:
        print("❌ Error: No se pudo leer el contenido de los archivos")
        return False
    
    # Combinar contenido
    print("🔗 Combinando contenido...")
    combined_content = content1 + "\n\n" + content2
    
    # Convertir a HTML
    print("🎨 Convirtiendo a HTML...")
    html_content = create_html_from_md(combined_content)
    
    # Generar PDF
    print("📄 Generando PDF...")
    if create_pdf_from_html(html_content, output_file):
        print(f"✅ PDF generado exitosamente: {output_file}")
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024 / 1024
            print(f"📊 Tamaño del archivo: {file_size:.2f} MB")
        return True
    else:
        print("❌ Error generando PDF")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ¡PDF del curso generado exitosamente!")
            print("📧 El archivo está listo para compartir y distribuir.")
        else:
            print("\n💥 Error en la generación del PDF")
            sys.exit(1)
    except ImportError as e:
        print(f"❌ Error: Falta instalar una dependencia: {e}")
        print("💡 Instala las dependencias con: pip install weasyprint markdown")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

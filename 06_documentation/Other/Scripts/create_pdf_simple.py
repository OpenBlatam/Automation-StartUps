#!/usr/bin/env python3
"""
Script simple para crear PDF del Curso Premium de IA en Marketing
Usa solo librerías estándar de Python y genera un PDF básico
"""

import os
import sys
from pathlib import Path
import re

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

def markdown_to_html(md_content):
    """Convierte Markdown básico a HTML"""
    
    # Convertir títulos
    md_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^##### (.*?)$', r'<h5>\1</h5>', md_content, flags=re.MULTILINE)
    md_content = re.sub(r'^###### (.*?)$', r'<h6>\1</h6>', md_content, flags=re.MULTILINE)
    
    # Convertir negritas
    md_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_content)
    md_content = re.sub(r'__(.*?)__', r'<strong>\1</strong>', md_content)
    
    # Convertir cursivas
    md_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', md_content)
    md_content = re.sub(r'_(.*?)_', r'<em>\1</em>', md_content)
    
    # Convertir código
    md_content = re.sub(r'`(.*?)`', r'<code>\1</code>', md_content)
    
    # Convertir listas
    lines = md_content.split('\n')
    in_list = False
    result_lines = []
    
    for line in lines:
        if line.strip().startswith('- ') or line.strip().startswith('* '):
            if not in_list:
                result_lines.append('<ul>')
                in_list = True
            content = line.strip()[2:].strip()
            result_lines.append(f'<li>{content}</li>')
        elif line.strip().startswith(('1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ')):
            if not in_list:
                result_lines.append('<ol>')
                in_list = True
            content = line.strip()[3:].strip()
            result_lines.append(f'<li>{content}</li>')
        else:
            if in_list:
                result_lines.append('</ul>' if result_lines[-1].startswith('<li>') else '</ol>')
                in_list = False
            
            if line.strip():
                if not line.startswith('<'):
                    result_lines.append(f'<p>{line}</p>')
                else:
                    result_lines.append(line)
            else:
                result_lines.append('')
    
    if in_list:
        result_lines.append('</ul>')
    
    return '\n'.join(result_lines)

def create_html_document(html_content):
    """Crea un documento HTML completo"""
    
    css_styles = """
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        
        h2 {
            color: #34495e;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 8px;
        }
        
        h3 {
            color: #2980b9;
        }
        
        h4 {
            color: #8e44ad;
        }
        
        h5, h6 {
            color: #27ae60;
        }
        
        p {
            margin-bottom: 12px;
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
        }
        
        em {
            color: #8e44ad;
        }
        
        code {
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 3px;
            padding: 2px 4px;
            font-family: 'Courier New', monospace;
        }
        
        hr {
            border: none;
            height: 2px;
            background-color: #3498db;
            margin: 30px 0;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        @media print {
            body {
                font-size: 12pt;
            }
            
            h1 {
                page-break-before: always;
            }
            
            h1:first-child {
                page-break-before: avoid;
            }
        }
    </style>
    """
    
    html_doc = f"""
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
    
    return html_doc

def save_html_file(html_content, output_path):
    """Guarda el contenido HTML en un archivo"""
    try:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(html_content)
        return True
    except Exception as e:
        print(f"Error guardando HTML: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Generando HTML del Curso Premium de IA en Marketing...")
    
    # Rutas de archivos
    base_dir = Path(".")
    file1 = base_dir / "AI_Marketing_Course_Complete_Structure.md"
    file2 = base_dir / "AI_Marketing_Course_Resources_Delivery_Marketing_Feedback.md"
    output_file = base_dir / "Curso_Premium_IA_Marketing_Completo.html"
    
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
    html_content = markdown_to_html(combined_content)
    
    # Crear documento HTML completo
    print("📄 Creando documento HTML...")
    full_html = create_html_document(html_content)
    
    # Guardar archivo HTML
    print("💾 Guardando archivo HTML...")
    if save_html_file(full_html, output_file):
        print(f"✅ HTML generado exitosamente: {output_file}")
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024 / 1024
            print(f"📊 Tamaño del archivo: {file_size:.2f} MB")
        
        print("\n📋 Para convertir a PDF:")
        print("1. Abre el archivo HTML en tu navegador")
        print("2. Presiona Ctrl+P (Cmd+P en Mac)")
        print("3. Selecciona 'Guardar como PDF'")
        print("4. Ajusta la configuración de impresión si es necesario")
        
        return True
    else:
        print("❌ Error generando HTML")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ¡HTML del curso generado exitosamente!")
            print("📧 El archivo está listo para convertir a PDF desde el navegador.")
        else:
            print("\n💥 Error en la generación del HTML")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)

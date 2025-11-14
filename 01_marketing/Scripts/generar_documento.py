#!/usr/bin/env python3
"""
Script para generar documentos Word y PDF a partir del markdown
"""

import markdown
import os
from datetime import datetime

def markdown_to_html(md_file):
    """Convierte markdown a HTML"""
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Configuración de markdown con extensiones
    md = markdown.Markdown(extensions=[
        'markdown.extensions.tables',
        'markdown.extensions.fenced_code',
        'markdown.extensions.toc',
        'markdown.extensions.attr_list'
    ])
    
    html_content = md.convert(md_content)
    
    # HTML completo con estilos
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Estrategia Completa de Anchor Text para Cursos de IA Marketing</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1000px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #764ba2;
                margin-top: 30px;
            }}
            h3 {{
                color: #555;
                margin-top: 25px;
            }}
            .tier {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
            }}
            .gold {{ border-left: 5px solid #ffd700; }}
            .silver {{ border-left: 5px solid #c0c0c0; }}
            .bronze {{ border-left: 5px solid #cd7f32; }}
            ul, ol {{
                padding-left: 20px;
            }}
            li {{
                margin: 8px 0;
            }}
            .highlight {{
                background: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                border-left: 4px solid #2196f3;
            }}
            @media print {{
                body {{ font-size: 12px; }}
                h1 {{ page-break-before: always; }}
                h1:first-child {{ page-break-before: avoid; }}
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return full_html

def main():
    """Función principal"""
    md_file = 'estrategia-anchor-text-ia-marketing.md'
    
    if not os.path.exists(md_file):
        print(f"Error: No se encontró el archivo {md_file}")
        return
    
    print("🔄 Generando documentos...")
    
    # Generar HTML
    html_content = markdown_to_html(md_file)
    html_file = 'estrategia-anchor-text-ia-marketing.html'
    
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML generado: {html_file}")
    
    # Generar archivo de texto plano para Word
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir markdown básico a texto plano
    text_content = md_content
    text_content = text_content.replace('# ', '')
    text_content = text_content.replace('## ', '')
    text_content = text_content.replace('### ', '')
    text_content = text_content.replace('#### ', '')
    text_content = text_content.replace('**', '')
    text_content = text_content.replace('*', '')
    text_content = text_content.replace('`', '')
    text_content = text_content.replace('- ', '• ')
    
    txt_file = 'estrategia-anchor-text-ia-marketing.txt'
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(text_content)
    
    print(f"✅ Texto plano generado: {txt_file}")
    
    print("\n🎉 Documentos generados exitosamente!")
    print(f"📄 HTML: {html_file}")
    print(f"📄 TXT: {txt_file}")
    print("\n💡 Para convertir a Word:")
    print("   1. Abre el archivo HTML en tu navegador")
    print("   2. Usa Ctrl+P (Cmd+P en Mac)")
    print("   3. Selecciona 'Guardar como PDF' o 'Imprimir a Word'")
    print("\n💡 Para convertir a PDF:")
    print("   1. Abre el archivo HTML en tu navegador")
    print("   2. Usa Ctrl+P (Cmd+P en Mac)")
    print("   3. Selecciona 'Guardar como PDF'")

if __name__ == "__main__":
    main()









#!/usr/bin/env python3
"""
Script para convertir las narrativas de marketing a PDF
"""

import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
import os

def create_pdf_from_markdown():
    """Convierte el archivo markdown a PDF con formato profesional"""
    
    # Leer el archivo markdown
    with open('AI_Webinar_Narrativas_Completas.md', 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Convertir markdown a HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables', 'toc', 'fenced_code'])
    
    # CSS para el PDF
    css_content = """
    @page {
        size: A4;
        margin: 2cm;
        @top-center {
            content: "Narrativas de Marketing IA";
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
    }
    
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 10px;
        margin-top: 30px;
        page-break-before: always;
    }
    
    h1:first-child {
        page-break-before: auto;
        text-align: center;
        font-size: 28pt;
        margin-bottom: 30px;
    }
    
    h2 {
        color: #34495e;
        border-left: 4px solid #3498db;
        padding-left: 15px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    h3 {
        color: #2c3e50;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    h4 {
        color: #7f8c8d;
        margin-top: 15px;
        margin-bottom: 8px;
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
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        font-size: 12pt;
    }
    
    th, td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
    }
    
    th {
        background-color: #f8f9fa;
        font-weight: bold;
        color: #2c3e50;
    }
    
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    
    .highlight {
        background-color: #fff3cd;
        padding: 15px;
        border-left: 4px solid #ffc107;
        margin: 15px 0;
    }
    
    strong {
        color: #2c3e50;
        font-weight: 600;
    }
    
    em {
        color: #7f8c8d;
        font-style: italic;
    }
    
    code {
        background-color: #f8f9fa;
        padding: 2px 4px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 11pt;
    }
    
    blockquote {
        border-left: 4px solid #3498db;
        margin: 20px 0;
        padding: 10px 20px;
        background-color: #f8f9fa;
        font-style: italic;
    }
    
    .page-break {
        page-break-before: always;
    }
    
    .no-break {
        page-break-inside: avoid;
    }
    """
    
    # HTML completo
    full_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Narrativas de Marketing IA</title>
        <style>{css_content}</style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Crear PDF
    try:
        font_config = FontConfiguration()
        html_doc = HTML(string=full_html)
        css_doc = CSS(string=css_content, font_config=font_config)
        
        html_doc.write_pdf(
            'AI_Webinar_Narrativas_Completas.pdf',
            stylesheets=[css_doc],
            font_config=font_config
        )
        
        print("✅ PDF creado exitosamente: AI_Webinar_Narrativas_Completas.pdf")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear PDF: {e}")
        return False

if __name__ == "__main__":
    create_pdf_from_markdown()

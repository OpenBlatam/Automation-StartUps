#!/usr/bin/env python3
"""
Script para convertir documentos legales Markdown a PDF profesional
Genera PDFs con formato corporativo estándar para documentos legales
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import markdown
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

class LegalDocumentConverter:
    def __init__(self, input_dir="13_Legal_Compliance", output_dir="13_Legal_Compliance/PDFs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuración de fuentes
        self.font_config = FontConfiguration()
        
        # CSS personalizado para documentos legales
        self.legal_css = """
        @page {
            size: A4;
            margin: 2.5cm 2cm 2.5cm 2cm;
            @top-center {
                content: "CONFIDENCIAL - NO DISTRIBUIR";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Página " counter(page) " de " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Times New Roman', serif;
            font-size: 12pt;
            line-height: 1.6;
            color: #333;
            max-width: none;
        }
        
        h1 {
            font-size: 18pt;
            font-weight: bold;
            color: #1a365d;
            margin-top: 2em;
            margin-bottom: 1em;
            border-bottom: 2px solid #1a365d;
            padding-bottom: 0.5em;
        }
        
        h2 {
            font-size: 16pt;
            font-weight: bold;
            color: #2d3748;
            margin-top: 1.5em;
            margin-bottom: 0.8em;
        }
        
        h3 {
            font-size: 14pt;
            font-weight: bold;
            color: #4a5568;
            margin-top: 1.2em;
            margin-bottom: 0.6em;
        }
        
        h4 {
            font-size: 13pt;
            font-weight: bold;
            color: #718096;
            margin-top: 1em;
            margin-bottom: 0.5em;
        }
        
        p {
            margin-bottom: 1em;
            text-align: justify;
        }
        
        ul, ol {
            margin-bottom: 1em;
            padding-left: 2em;
        }
        
        li {
            margin-bottom: 0.5em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            font-size: 11pt;
        }
        
        th, td {
            border: 1px solid #e2e8f0;
            padding: 0.5em;
            text-align: left;
        }
        
        th {
            background-color: #f7fafc;
            font-weight: bold;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2em;
            padding: 1em;
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
        }
        
        .footer {
            text-align: center;
            margin-top: 2em;
            padding: 1em;
            background-color: #f7fafc;
            border: 1px solid #e2e8f0;
            font-size: 10pt;
        }
        
        .confidential {
            background-color: #fed7d7;
            border: 2px solid #f56565;
            padding: 1em;
            margin: 1em 0;
            text-align: center;
            font-weight: bold;
            color: #c53030;
        }
        
        .signature-section {
            margin-top: 3em;
            page-break-inside: avoid;
        }
        
        .signature-line {
            border-bottom: 1px solid #333;
            width: 300px;
            margin: 2em 0 0.5em 0;
        }
        
        .signature-label {
            font-size: 10pt;
            color: #666;
        }
        
        blockquote {
            border-left: 4px solid #1a365d;
            padding-left: 1em;
            margin: 1em 0;
            font-style: italic;
            background-color: #f7fafc;
            padding: 1em;
        }
        
        code {
            background-color: #f7fafc;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 11pt;
        }
        
        pre {
            background-color: #f7fafc;
            padding: 1em;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 11pt;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
        """
    
    def convert_markdown_to_html(self, markdown_file):
        """Convierte archivo Markdown a HTML con formato legal"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convertir Markdown a HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['tables', 'fenced_code', 'toc']
        )
        
        # Crear HTML completo con CSS
        full_html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{markdown_file.stem}</title>
            <style>{self.legal_css}</style>
        </head>
        <body>
            <div class="header">
                <h1>{markdown_file.stem.replace('_', ' ').title()}</h1>
                <p>Documento Legal Profesional</p>
                <p>Fecha: {datetime.now().strftime('%d de %B de %Y')}</p>
            </div>
            
            <div class="confidential">
                ⚠️ INFORMACIÓN CONFIDENCIAL - NO DISTRIBUIR ⚠️
            </div>
            
            {html_content}
            
            <div class="footer">
                <p>Documento generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}</p>
                <p>Este documento contiene información confidencial y propietaria.</p>
            </div>
        </body>
        </html>
        """
        
        return full_html
    
    def convert_to_pdf(self, markdown_file):
        """Convierte archivo Markdown a PDF profesional"""
        try:
            print(f"Convirtiendo {markdown_file.name} a PDF...")
            
            # Convertir a HTML
            html_content = self.convert_markdown_to_html(markdown_file)
            
            # Generar nombre del archivo PDF
            pdf_filename = markdown_file.stem + ".pdf"
            pdf_path = self.output_dir / pdf_filename
            
            # Convertir HTML a PDF
            HTML(string=html_content).write_pdf(
                pdf_path,
                font_config=self.font_config
            )
            
            print(f"✅ PDF generado: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error convirtiendo {markdown_file.name}: {str(e)}")
            return None
    
    def convert_all_documents(self):
        """Convierte todos los documentos Markdown a PDF"""
        markdown_files = list(self.input_dir.glob("*.md"))
        
        if not markdown_files:
            print("❌ No se encontraron archivos Markdown en el directorio")
            return
        
        print(f"📋 Encontrados {len(markdown_files)} documentos para convertir")
        print(f"📁 Directorio de salida: {self.output_dir}")
        print("-" * 50)
        
        converted_files = []
        failed_files = []
        
        for md_file in markdown_files:
            if md_file.name.startswith("00_"):  # Saltar archivos de índice
                continue
                
            pdf_path = self.convert_to_pdf(md_file)
            if pdf_path:
                converted_files.append(pdf_path)
            else:
                failed_files.append(md_file)
        
        # Resumen
        print("-" * 50)
        print(f"✅ Documentos convertidos exitosamente: {len(converted_files)}")
        print(f"❌ Documentos con errores: {len(failed_files)}")
        
        if converted_files:
            print("\n📄 Archivos PDF generados:")
            for pdf_file in converted_files:
                print(f"   - {pdf_file.name}")
        
        if failed_files:
            print("\n❌ Archivos con errores:")
            for md_file in failed_files:
                print(f"   - {md_file.name}")
        
        return converted_files, failed_files
    
    def create_package_zip(self):
        """Crea un archivo ZIP con todos los PDFs"""
        import zipfile
        
        zip_filename = f"Legal_Documents_Package_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.input_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pdf_file in self.output_dir.glob("*.pdf"):
                zipf.write(pdf_file, pdf_file.name)
        
        print(f"📦 Paquete ZIP creado: {zip_path}")
        return zip_path

def main():
    """Función principal"""
    print("🚀 CONVERTIDOR DE DOCUMENTOS LEGALES A PDF")
    print("=" * 50)
    
    # Verificar dependencias
    try:
        import weasyprint
        import markdown
    except ImportError as e:
        print("❌ Error: Faltan dependencias requeridas")
        print("Instale las dependencias con:")
        print("pip install weasyprint markdown")
        sys.exit(1)
    
    # Crear convertidor
    converter = LegalDocumentConverter()
    
    # Convertir documentos
    converted_files, failed_files = converter.convert_all_documents()
    
    if converted_files:
        # Crear paquete ZIP
        zip_path = converter.create_package_zip()
        
        print("\n🎉 CONVERSIÓN COMPLETADA")
        print(f"📁 PDFs guardados en: {converter.output_dir}")
        print(f"📦 Paquete ZIP: {zip_path}")
        
        # Mostrar instrucciones
        print("\n📋 INSTRUCCIONES:")
        print("1. Revise todos los PDFs generados")
        print("2. Personalice la información específica de su empresa")
        print("3. Consulte con abogados especializados")
        print("4. Ejecute los documentos según sea necesario")
        
    else:
        print("\n❌ No se pudieron convertir documentos")
        sys.exit(1)

if __name__ == "__main__":
    main()








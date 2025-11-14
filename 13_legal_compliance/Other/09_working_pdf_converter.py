#!/usr/bin/env python3
"""
Convertidor funcional de documentos legales Markdown a PDF
Versión simplificada que funciona correctamente
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import HexColor, black, darkblue, darkgray
from reportlab.pdfgen import canvas

class WorkingPDFConverter:
    def __init__(self, input_dir=".", output_dir="PDFs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar estilos
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados para documentos legales"""
        
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='LegalTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=HexColor('#1a365d')
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='LegalHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=HexColor('#2d3748')
        ))
        
        # Estilo para encabezados de sección
        self.styles.add(ParagraphStyle(
            name='LegalHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=HexColor('#4a5568')
        ))
        
        # Estilo para párrafos legales
        self.styles.add(ParagraphStyle(
            name='LegalParagraph',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))
        
        # Estilo para información confidencial
        self.styles.add(ParagraphStyle(
            name='Confidential',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#c53030')
        ))
    
    def convert_markdown_to_elements(self, markdown_file):
        """Convierte archivo Markdown a elementos de ReportLab"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convertir Markdown a elementos de ReportLab
        elements = []
        
        # Agregar encabezado
        elements.append(Paragraph("INFORMACIÓN CONFIDENCIAL - NO DISTRIBUIR", self.styles['Confidential']))
        elements.append(Spacer(1, 20))
        
        # Procesar contenido línea por línea
        lines = markdown_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                elements.append(Spacer(1, 6))
                i += 1
                continue
            
            # Títulos principales (#)
            if line.startswith('# '):
                title = line[2:].strip()
                elements.append(Paragraph(title, self.styles['LegalTitle']))
                elements.append(Spacer(1, 20))
            
            # Subtítulos (##)
            elif line.startswith('## '):
                subtitle = line[3:].strip()
                elements.append(Paragraph(subtitle, self.styles['LegalHeading2']))
                elements.append(Spacer(1, 15))
            
            # Encabezados de sección (###)
            elif line.startswith('### '):
                heading = line[4:].strip()
                elements.append(Paragraph(heading, self.styles['LegalHeading3']))
                elements.append(Spacer(1, 10))
            
            # Listas
            elif line.startswith('- ') or line.startswith('* '):
                # Procesar lista
                list_items = []
                while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                    item = lines[i].strip()[2:].strip()
                    list_items.append(f"• {item}")
                    i += 1
                i -= 1  # Retroceder una línea
                
                for item in list_items:
                    elements.append(Paragraph(item, self.styles['LegalParagraph']))
                elements.append(Spacer(1, 10))
            
            # Párrafos normales
            else:
                if line and not line.startswith('---'):
                    elements.append(Paragraph(line, self.styles['LegalParagraph']))
            
            i += 1
        
        return elements
    
    def add_header_footer(self, canvas, doc):
        """Agregar encabezado y pie de página"""
        canvas.saveState()
        
        # Encabezado
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(HexColor('#666666'))
        canvas.drawString(50, A4[1] - 50, "CONFIDENCIAL - NO DISTRIBUIR")
        
        # Pie de página
        canvas.setFont('Helvetica', 10)
        page_text = f"Página {doc.page} - {datetime.now().strftime('%d/%m/%Y')}"
        canvas.drawString(A4[0]/2 - len(page_text)*2, 50, page_text)
        
        canvas.restoreState()
    
    def convert_to_pdf(self, markdown_file):
        """Convierte archivo Markdown a PDF profesional"""
        try:
            print(f"Convirtiendo {markdown_file.name} a PDF...")
            
            # Generar nombre del archivo PDF
            pdf_filename = markdown_file.stem + ".pdf"
            pdf_path = self.output_dir / pdf_filename
            
            # Crear documento PDF
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Convertir contenido
            elements = self.convert_markdown_to_elements(markdown_file)
            
            # Construir PDF
            doc.build(elements, onFirstPage=self.add_header_footer, onLaterPages=self.add_header_footer)
            
            print(f"✅ PDF generado: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error convirtiendo {markdown_file.name}: {str(e)}")
            return None
    
    def convert_specific_documents(self):
        """Convierte solo los documentos legales específicos"""
        target_files = [
            "01_TERM_SHEET_INVESTMENT.md",
            "02_INVESTMENT_AGREEMENT.md", 
            "03_SHAREHOLDERS_AGREEMENT.md",
            "04_ARTICLES_OF_INCORPORATION.md",
            "05_DUE_DILIGENCE_PACKAGE.md",
            "06_LEGAL_OPINION.md"
        ]
        
        print(f"📋 Convirtiendo {len(target_files)} documentos legales específicos")
        print(f"📁 Directorio de salida: {self.output_dir}")
        print("-" * 50)
        
        converted_files = []
        failed_files = []
        
        for filename in target_files:
            md_file = self.input_dir / filename
            if md_file.exists():
                pdf_path = self.convert_to_pdf(md_file)
                if pdf_path:
                    converted_files.append(pdf_path)
                else:
                    failed_files.append(md_file)
            else:
                print(f"⚠️ Archivo no encontrado: {filename}")
        
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
    print("=" * 60)
    
    # Verificar dependencias
    try:
        import markdown2
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
    except ImportError as e:
        print("❌ Error: Faltan dependencias requeridas")
        print("Instale las dependencias con:")
        print("pip install markdown2 reportlab")
        sys.exit(1)
    
    # Crear convertidor
    converter = WorkingPDFConverter()
    
    # Convertir documentos específicos
    converted_files, failed_files = converter.convert_specific_documents()
    
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








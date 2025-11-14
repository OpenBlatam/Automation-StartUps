#!/usr/bin/env python3
"""
Generador de PDFs Legales Mejorado
Crea PDFs profesionales con características avanzadas
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import markdown2
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor, black, darkblue, darkgray, red, blue
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, Image, KeepTogether
)
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import qrcode
from io import BytesIO

class EnhancedLegalPDFGenerator:
    """Generador de PDFs legales mejorado con características avanzadas"""
    
    def __init__(self, input_dir=".", output_dir="Enhanced_PDFs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar estilos avanzados
        self.styles = getSampleStyleSheet()
        self.setup_advanced_styles()
        
        # Configurar fuentes
        self.setup_fonts()
    
    def setup_fonts(self):
        """Configurar fuentes personalizadas"""
        try:
            # Intentar registrar fuentes del sistema
            font_paths = [
                "/System/Library/Fonts/Times.ttc",
                "/System/Library/Fonts/Helvetica.ttc",
                "/System/Library/Fonts/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
            ]
            
            for font_path in font_paths:
                if Path(font_path).exists():
                    try:
                        pdfmetrics.registerFont(TTFont('CustomFont', font_path))
                        break
                    except:
                        continue
        except:
            pass  # Usar fuentes por defecto si no se pueden cargar
    
    def setup_advanced_styles(self):
        """Configurar estilos avanzados para documentos legales"""
        
        # Estilo para títulos principales con borde
        self.styles.add(ParagraphStyle(
            name='LegalTitle',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=30,
            spaceBefore=20,
            alignment=TA_CENTER,
            textColor=HexColor('#1a365d'),
            borderWidth=2,
            borderColor=HexColor('#1a365d'),
            borderPadding=15,
            backColor=HexColor('#f7fafc'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para subtítulos con fondo
        self.styles.add(ParagraphStyle(
            name='LegalHeading2',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            spaceBefore=15,
            textColor=HexColor('#2d3748'),
            backColor=HexColor('#edf2f7'),
            borderWidth=1,
            borderColor=HexColor('#e2e8f0'),
            borderPadding=8,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para encabezados de sección
        self.styles.add(ParagraphStyle(
            name='LegalHeading3',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=10,
            textColor=HexColor('#4a5568'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para párrafos legales con justificación
        self.styles.add(ParagraphStyle(
            name='LegalParagraph',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            alignment=TA_JUSTIFY,
            leftIndent=0,
            rightIndent=0,
            fontName='Times-Roman'
        ))
        
        # Estilo para información confidencial
        self.styles.add(ParagraphStyle(
            name='Confidential',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=HexColor('#c53030'),
            backColor=HexColor('#fed7d7'),
            borderWidth=2,
            borderColor=HexColor('#f56565'),
            borderPadding=12,
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para firmas
        self.styles.add(ParagraphStyle(
            name='Signature',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=20,
            alignment=TA_LEFT,
            textColor=HexColor('#4a5568'),
            fontName='Helvetica'
        ))
        
        # Estilo para tablas
        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=HexColor('#ffffff'),
            backColor=HexColor('#2d3748'),
            fontName='Helvetica-Bold'
        ))
        
        # Estilo para código
        self.styles.add(ParagraphStyle(
            name='LegalCode',
            parent=self.styles['Normal'],
            fontSize=9,
            spaceAfter=6,
            alignment=TA_LEFT,
            textColor=HexColor('#2d3748'),
            backColor=HexColor('#f7fafc'),
            borderWidth=1,
            borderColor=HexColor('#e2e8f0'),
            borderPadding=6,
            fontName='Courier'
        ))
    
    def create_qr_code(self, text: str, size: int = 100) -> BytesIO:
        """Crear código QR para el documento"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a BytesIO
        img_buffer = BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return img_buffer
    
    def add_advanced_header_footer(self, canvas, doc):
        """Agregar encabezado y pie de página avanzados"""
        canvas.saveState()
        
        # Encabezado con línea
        canvas.setStrokeColor(HexColor('#1a365d'))
        canvas.setLineWidth(2)
        canvas.line(50, A4[1] - 50, A4[0] - 50, A4[1] - 50)
        
        # Texto confidencial
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(HexColor('#c53030'))
        canvas.drawString(50, A4[1] - 35, "CONFIDENCIAL - NO DISTRIBUIR")
        
        # Código QR (opcional)
        try:
            qr_text = f"Documento Legal - {datetime.now().strftime('%Y%m%d')}"
            qr_buffer = self.create_qr_code(qr_text, 60)
            canvas.drawInlineImage(qr_buffer, A4[0] - 80, A4[1] - 80, width=60, height=60)
        except:
            pass
        
        # Pie de página con línea
        canvas.setStrokeColor(HexColor('#1a365d'))
        canvas.setLineWidth(1)
        canvas.line(50, 50, A4[0] - 50, 50)
        
        # Información de página
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(HexColor('#4a5568'))
        page_text = f"Página {doc.page} - {datetime.now().strftime('%d/%m/%Y')}"
        canvas.drawString(50, 30, page_text)
        
        # Número de documento
        doc_text = f"Doc: {doc.page}"
        canvas.drawRightString(A4[0] - 50, 30, doc_text)
        
        canvas.restoreState()
    
    def create_watermark(self, canvas, doc):
        """Crear marca de agua"""
        canvas.saveState()
        
        # Texto de marca de agua
        canvas.setFont('Helvetica', 60)
        canvas.setFillColor(HexColor('#f0f0f0'))
        canvas.rotate(45)
        canvas.drawString(200, -200, "CONFIDENCIAL")
        
        canvas.restoreState()
    
    def convert_markdown_to_advanced_elements(self, markdown_file):
        """Convierte archivo Markdown a elementos avanzados de ReportLab"""
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        elements = []
        
        # Agregar encabezado confidencial
        elements.append(Paragraph("⚠️ INFORMACIÓN CONFIDENCIAL - NO DISTRIBUIR ⚠️", self.styles['Confidential']))
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
            
            # Tablas (líneas que contienen |)
            elif '|' in line and not line.startswith('|---'):
                table_data = []
                # Recopilar datos de la tabla
                while i < len(lines) and '|' in lines[i]:
                    row = [cell.strip() for cell in lines[i].split('|') if cell.strip()]
                    if row:  # Ignorar filas vacías
                        table_data.append(row)
                    i += 1
                i -= 1  # Retroceder una línea
                
                if table_data:
                    # Crear tabla
                    table = Table(table_data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2d3748')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ]))
                    elements.append(table)
                    elements.append(Spacer(1, 15))
            
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
                elements.append(Spacer(1, 8))
            
            # Código (líneas que empiezan con espacios o tabulaciones)
            elif line.startswith('    ') or line.startswith('\t'):
                code_lines = []
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].startswith('\t')):
                    code_lines.append(lines[i].strip())
                    i += 1
                i -= 1  # Retroceder una línea
                
                code_text = '\n'.join(code_lines)
                elements.append(Paragraph(code_text, self.styles['LegalCode']))
                elements.append(Spacer(1, 10))
            
            # Párrafos normales
            else:
                if line and not line.startswith('---'):
                    elements.append(Paragraph(line, self.styles['LegalParagraph']))
            
            i += 1
        
        # Agregar sección de firmas
        elements.append(PageBreak())
        elements.append(Paragraph("FIRMAS Y APROBACIONES", self.styles['LegalHeading2']))
        elements.append(Spacer(1, 20))
        
        # Tabla de firmas
        signature_data = [
            ['PARTE', 'NOMBRE', 'FIRMA', 'FECHA'],
            ['Empresa', '_________________', '_________________', '_________________'],
            ['Lead Investor', '_________________', '_________________', '_________________'],
            ['Co-Investor 1', '_________________', '_________________', '_________________'],
            ['Co-Investor 2', '_________________', '_________________', '_________________'],
            ['Co-Investor 3', '_________________', '_________________', '_________________']
        ]
        
        signature_table = Table(signature_data)
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f7fafc')]),
        ]))
        
        elements.append(signature_table)
        elements.append(Spacer(1, 30))
        
        # Información de contacto
        contact_info = """
        <b>INFORMACIÓN DE CONTACTO:</b><br/>
        • Empresa: [NOMBRE] - [EMAIL] - [TELÉFONO]<br/>
        • Lead Investor: [NOMBRE] - [EMAIL] - [TELÉFONO]<br/>
        • Abogado Corporativo: [NOMBRE] - [EMAIL] - [TELÉFONO]<br/>
        • Fecha de Generación: """ + datetime.now().strftime('%d/%m/%Y %H:%M') + """
        """
        
        elements.append(Paragraph(contact_info, self.styles['LegalParagraph']))
        
        return elements
    
    def convert_to_enhanced_pdf(self, markdown_file):
        """Convierte archivo Markdown a PDF mejorado"""
        try:
            print(f"Generando PDF mejorado para {markdown_file.name}...")
            
            # Generar nombre del archivo PDF
            pdf_filename = f"Enhanced_{markdown_file.stem}.pdf"
            pdf_path = self.output_dir / pdf_filename
            
            # Crear documento PDF con características avanzadas
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=3*cm,
                bottomMargin=3*cm,
                title=f"Documento Legal - {markdown_file.stem}",
                author="Sistema de Documentos Legales",
                subject="Documento Legal Profesional",
                creator="Legal Document Generator v2.0"
            )
            
            # Convertir contenido
            elements = self.convert_markdown_to_advanced_elements(markdown_file)
            
            # Construir PDF con marca de agua
            def add_watermark(canvas, doc):
                self.create_watermark(canvas, doc)
                self.add_advanced_header_footer(canvas, doc)
            
            doc.build(elements, onFirstPage=add_watermark, onLaterPages=add_watermark)
            
            print(f"✅ PDF mejorado generado: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error generando PDF mejorado para {markdown_file.name}: {str(e)}")
            return None
    
    def convert_specific_documents(self):
        """Convierte solo los documentos legales específicos con mejoras"""
        target_files = [
            "01_TERM_SHEET_INVESTMENT.md",
            "02_INVESTMENT_AGREEMENT.md", 
            "03_SHAREHOLDERS_AGREEMENT.md",
            "04_ARTICLES_OF_INCORPORATION.md",
            "05_DUE_DILIGENCE_PACKAGE.md",
            "06_LEGAL_OPINION.md"
        ]
        
        print(f"📋 Generando PDFs mejorados para {len(target_files)} documentos legales")
        print(f"📁 Directorio de salida: {self.output_dir}")
        print("-" * 60)
        
        converted_files = []
        failed_files = []
        
        for filename in target_files:
            md_file = self.input_dir / filename
            if md_file.exists():
                pdf_path = self.convert_to_enhanced_pdf(md_file)
                if pdf_path:
                    converted_files.append(pdf_path)
                else:
                    failed_files.append(md_file)
            else:
                print(f"⚠️ Archivo no encontrado: {filename}")
        
        # Resumen
        print("-" * 60)
        print(f"✅ PDFs mejorados generados: {len(converted_files)}")
        print(f"❌ Documentos con errores: {len(failed_files)}")
        
        if converted_files:
            print("\n📄 Archivos PDF mejorados generados:")
            for pdf_file in converted_files:
                print(f"   - {pdf_file.name}")
        
        if failed_files:
            print("\n❌ Archivos con errores:")
            for md_file in failed_files:
                print(f"   - {md_file.name}")
        
        return converted_files, failed_files
    
    def create_enhanced_package_zip(self):
        """Crea un archivo ZIP con todos los PDFs mejorados"""
        import zipfile
        
        zip_filename = f"Enhanced_Legal_Documents_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = self.input_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for pdf_file in self.output_dir.glob("*.pdf"):
                zipf.write(pdf_file, pdf_file.name)
        
        print(f"📦 Paquete ZIP mejorado creado: {zip_path}")
        return zip_path

def main():
    """Función principal"""
    print("🚀 GENERADOR DE PDFs LEGALES MEJORADO")
    print("=" * 60)
    
    # Verificar dependencias
    try:
        import markdown2
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate
        import qrcode
    except ImportError as e:
        print("❌ Error: Faltan dependencias requeridas")
        print("Instale las dependencias con:")
        print("pip install markdown2 reportlab qrcode[pil]")
        sys.exit(1)
    
    # Crear generador mejorado
    generator = EnhancedLegalPDFGenerator()
    
    # Convertir documentos específicos
    converted_files, failed_files = generator.convert_specific_documents()
    
    if converted_files:
        # Crear paquete ZIP mejorado
        zip_path = generator.create_enhanced_package_zip()
        
        print("\n🎉 GENERACIÓN MEJORADA COMPLETADA")
        print(f"📁 PDFs mejorados guardados en: {generator.output_dir}")
        print(f"📦 Paquete ZIP mejorado: {zip_path}")
        
        # Mostrar características mejoradas
        print("\n✨ CARACTERÍSTICAS MEJORADAS INCLUIDAS:")
        print("   - Diseño profesional avanzado")
        print("   - Marca de agua de confidencialidad")
        print("   - Códigos QR para verificación")
        print("   - Tablas de firmas integradas")
        print("   - Estilos tipográficos mejorados")
        print("   - Encabezados y pies de página profesionales")
        print("   - Metadatos del documento")
        print("   - Colores corporativos")
        
        # Mostrar instrucciones
        print("\n📋 INSTRUCCIONES:")
        print("1. Revise todos los PDFs mejorados generados")
        print("2. Personalice la información específica de su empresa")
        print("3. Consulte con abogados especializados")
        print("4. Ejecute los documentos según sea necesario")
        print("5. Los PDFs incluyen características de seguridad avanzadas")
        
    else:
        print("\n❌ No se pudieron generar PDFs mejorados")
        sys.exit(1)

if __name__ == "__main__":
    main()

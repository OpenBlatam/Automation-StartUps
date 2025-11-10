"""
Generador de PDFs para Contratos
Convierte templates HTML/Markdown a PDF
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional
import base64

logger = logging.getLogger("airflow.task")

# Verificar si hay librerías de PDF disponibles
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.warning("reportlab no disponible, generación de PDF limitada")

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    logger.debug("weasyprint no disponible")

try:
    import markdown
    from markdown.extensions import codehilite, tables
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False
    logger.debug("markdown no disponible")


class PDFGenerator:
    """Generador de PDFs para contratos"""
    
    def __init__(self):
        self.available = REPORTLAB_AVAILABLE or WEASYPRINT_AVAILABLE
    
    def generate_pdf_from_text(
        self,
        content: str,
        title: str = "Contract",
        output_format: str = "bytes"
    ) -> bytes:
        """
        Genera PDF desde texto plano.
        
        Args:
            content: Contenido del contrato
            title: Título del documento
            output_format: 'bytes' o 'base64'
            
        Returns:
            Contenido del PDF como bytes o base64
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab no disponible para generar PDF")
        
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor='black',
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        normal_style = styles['Normal']
        normal_style.fontSize = 11
        normal_style.leading = 14
        
        # Construir contenido
        story = []
        
        # Título
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # Contenido (dividir por líneas)
        for line in content.split('\n'):
            if line.strip():
                # Escapar HTML especial
                line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(line, normal_style))
            else:
                story.append(Spacer(1, 0.1 * inch))
        
        # Generar PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        if output_format == "base64":
            return base64.b64encode(pdf_bytes).decode('utf-8')
        
        return pdf_bytes
    
    def generate_pdf_from_html(
        self,
        html_content: str,
        output_format: str = "bytes"
    ) -> bytes:
        """
        Genera PDF desde HTML usando WeasyPrint.
        
        Args:
            html_content: Contenido HTML
            output_format: 'bytes' o 'base64'
            
        Returns:
            Contenido del PDF como bytes o base64
        """
        if not WEASYPRINT_AVAILABLE:
            # Fallback a reportlab si está disponible
            if REPORTLAB_AVAILABLE:
                # Convertir HTML básico a texto
                from html import unescape
                import re
                text_content = re.sub(r'<[^>]+>', '', html_content)
                text_content = unescape(text_content)
                return self.generate_pdf_from_text(text_content, output_format=output_format)
            else:
                raise ImportError("weasyprint no disponible para generar PDF desde HTML")
        
        pdf_bytes = HTML(string=html_content).write_pdf()
        
        if output_format == "base64":
            return base64.b64encode(pdf_bytes).decode('utf-8')
        
        return pdf_bytes
    
    def generate_pdf_from_markdown(
        self,
        markdown_content: str,
        title: str = "Contract",
        output_format: str = "bytes"
    ) -> bytes:
        """
        Genera PDF desde Markdown.
        
        Args:
            markdown_content: Contenido en Markdown
            title: Título del documento
            output_format: 'bytes' o 'base64'
            
        Returns:
            Contenido del PDF como bytes o base64
        """
        if not MARKDOWN_AVAILABLE:
            # Si no hay markdown, tratar como texto plano
            return self.generate_pdf_from_text(markdown_content, title, output_format)
        
        # Convertir Markdown a HTML
        html_content = markdown.markdown(
            markdown_content,
            extensions=['codehilite', 'tables', 'fenced_code']
        )
        
        # Agregar título
        html_with_title = f"<h1>{title}</h1>\n{html_content}"
        
        # Generar PDF desde HTML
        return self.generate_pdf_from_html(html_with_title, output_format)


def generate_contract_pdf(
    contract_content: str,
    contract_type: str = "text",
    title: str = "Contract",
    output_format: str = "bytes"
) -> bytes:
    """
    Función helper para generar PDF de contrato.
    
    Args:
        contract_content: Contenido del contrato (text, HTML o Markdown)
        contract_type: 'text', 'html' o 'markdown'
        title: Título del documento
        output_format: 'bytes' o 'base64'
        
    Returns:
        Contenido del PDF
    """
    generator = PDFGenerator()
    
    if not generator.available:
        raise ImportError("No hay librerías de PDF disponibles. Instalar reportlab o weasyprint")
    
    if contract_type == "html":
        return generator.generate_pdf_from_html(contract_content, output_format)
    elif contract_type == "markdown":
        return generator.generate_pdf_from_markdown(contract_content, title, output_format)
    else:
        return generator.generate_pdf_from_text(contract_content, title, output_format)


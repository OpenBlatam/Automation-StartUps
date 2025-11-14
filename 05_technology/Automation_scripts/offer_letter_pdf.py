#!/usr/bin/env python3
"""
Generación de PDF para Cartas de Oferta
Convierte cartas de oferta a PDF profesional
"""

import sys
import os
from typing import Optional


def generate_pdf_from_html(html_file: str, pdf_file: Optional[str] = None) -> bool:
    """Genera PDF desde archivo HTML usando weasyprint."""
    try:
        from weasyprint import HTML, CSS
        from weasyprint.text.fonts import FontConfiguration
        
        if not pdf_file:
            pdf_file = html_file.replace('.html', '.pdf')
        
        print(f"🔄 Generando PDF desde {html_file}...")
        
        font_config = FontConfiguration()
        
        # CSS adicional para PDF
        css_content = """
        @page {
            size: A4;
            margin: 0.75in;
        }
        
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
        }
        
        .letter-container {
            max-width: 100%;
        }
        
        .section {
            page-break-inside: avoid;
        }
        
        .acceptance-section {
            page-break-inside: avoid;
        }
        """
        
        html_doc = HTML(filename=html_file)
        css_doc = CSS(string=css_content, font_config=font_config)
        
        html_doc.write_pdf(pdf_file, stylesheets=[css_doc], font_config=font_config)
        
        print(f"✅ PDF generado exitosamente: {pdf_file}")
        return True
        
    except ImportError:
        print("❌ Error: weasyprint no está instalado", file=sys.stderr)
        print("   Instálalo con: pip install weasyprint", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error generando PDF: {e}", file=sys.stderr)
        return False


def generate_pdf_from_text(text_file: str, pdf_file: Optional[str] = None) -> bool:
    """Genera PDF desde archivo de texto usando reportlab."""
    try:
        from reportlab.lib.pagesizes import letter, A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib.enums import TA_LEFT, TA_CENTER
        
        if not pdf_file:
            pdf_file = text_file.replace('.txt', '.pdf')
        
        print(f"🔄 Generando PDF desde {text_file}...")
        
        # Leer archivo de texto
        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Crear documento PDF
        doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Estilos
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor='#2c3e50'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12,
            textColor='#2c3e50'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            alignment=TA_LEFT,
            leading=14
        )
        
        # Procesar contenido
        story = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            
            # Detectar títulos
            if line.startswith('=') or line.startswith('OFFER OF EMPLOYMENT'):
                if 'OFFER OF EMPLOYMENT' in line:
                    story.append(Paragraph('OFFER OF EMPLOYMENT', title_style))
                    story.append(Spacer(1, 12))
            elif line.isupper() and len(line) < 50 and not line.startswith('•'):
                # Probablemente un encabezado de sección
                story.append(Paragraph(line, heading_style))
            else:
                # Texto normal
                # Escapar HTML especial
                line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(line, body_style))
        
        # Construir PDF
        doc.build(story)
        
        print(f"✅ PDF generado exitosamente: {pdf_file}")
        return True
        
    except ImportError:
        print("❌ Error: reportlab no está instalado", file=sys.stderr)
        print("   Instálalo con: pip install reportlab", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ Error generando PDF: {e}", file=sys.stderr)
        return False


def generate_pdf_from_offer_data(output_file: str = "offer_letter.pdf", **kwargs) -> bool:
    """Genera PDF directamente desde datos de oferta."""
    from offer_letter_extras import generate_html_offer_letter
    import tempfile
    
    # Generar HTML temporal
    html_content = generate_html_offer_letter(**kwargs)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        temp_html = f.name
        f.write(html_content)
    
    try:
        result = generate_pdf_from_html(temp_html, output_file)
        return result
    finally:
        # Limpiar archivo temporal
        if os.path.exists(temp_html):
            os.unlink(temp_html)


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Genera PDFs de cartas de oferta')
    parser.add_argument('input_file', nargs='?',
                       help='Archivo de entrada (HTML o TXT)')
    parser.add_argument('--output', '-o',
                       help='Archivo PDF de salida')
    parser.add_argument('--from-html', action='store_true',
                       help='Forzar entrada como HTML')
    parser.add_argument('--from-text', action='store_true',
                       help='Forzar entrada como texto')
    
    args = parser.parse_args()
    
    if not args.input_file:
        parser.print_help()
        return
    
    # Determinar tipo de archivo
    if args.from_html or args.input_file.endswith('.html'):
        success = generate_pdf_from_html(args.input_file, args.output)
    elif args.from_text or args.input_file.endswith('.txt'):
        success = generate_pdf_from_text(args.input_file, args.output)
    else:
        # Intentar detectar
        if args.input_file.endswith('.html'):
            success = generate_pdf_from_html(args.input_file, args.output)
        else:
            success = generate_pdf_from_text(args.input_file, args.output)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()






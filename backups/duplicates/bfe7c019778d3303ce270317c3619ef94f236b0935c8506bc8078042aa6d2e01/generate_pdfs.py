#!/usr/bin/env python3
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import os

def convert_md_to_pdf(md_file, pdf_file):
    """Convert Markdown file to PDF using ReportLab"""
    try:
        # Read markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML first
        html = markdown2.markdown(md_content, extras=['tables', 'fenced-code-blocks'])
        
        # Create PDF
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=colors.darkblue
        )
        
        heading1_style = ParagraphStyle(
            'CustomHeading1',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.darkblue
        )
        
        heading2_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.blue
        )
        
        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=10,
            textColor=colors.darkgreen
        )
        
        # Process content line by line
        lines = md_content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
                
            if line.startswith('# '):
                # Main title
                text = line[2:].strip()
                story.append(Paragraph(text, title_style))
                story.append(Spacer(1, 12))
            elif line.startswith('## '):
                # Heading 1
                text = line[3:].strip()
                story.append(Paragraph(text, heading1_style))
                story.append(Spacer(1, 8))
            elif line.startswith('### '):
                # Heading 2
                text = line[4:].strip()
                story.append(Paragraph(text, heading2_style))
                story.append(Spacer(1, 6))
            elif line.startswith('#### '):
                # Heading 3
                text = line[5:].strip()
                story.append(Paragraph(text, heading3_style))
                story.append(Spacer(1, 4))
            elif line.startswith('- '):
                # Bullet point
                text = line[2:].strip()
                story.append(Paragraph(f"• {text}", styles['Normal']))
            elif line.startswith('**') and line.endswith('**'):
                # Bold text
                text = line[2:-2].strip()
                story.append(Paragraph(f"<b>{text}</b>", styles['Normal']))
            elif line.startswith('|'):
                # Table row - simple handling
                text = line.replace('|', ' | ')
                story.append(Paragraph(text, styles['Normal']))
            else:
                # Regular paragraph
                if line:
                    story.append(Paragraph(line, styles['Normal']))
        
        # Build PDF
        doc.build(story)
        print(f"✅ Successfully converted {md_file} to {pdf_file}")
        
    except Exception as e:
        print(f"❌ Error converting {md_file}: {str(e)}")

def main():
    """Convert all markdown files to PDF"""
    files_to_convert = [
        ('remote-company-culture-strategy.md', 'remote-company-culture-strategy.pdf'),
        ('curso-inteligencia-artificial-empresas.md', 'curso-inteligencia-artificial-empresas.pdf'),
        ('guia-marketing-saas.md', 'guia-marketing-saas.pdf'),
        ('guia-implementacion-ia-fintech.md', 'guia-implementacion-ia-fintech.pdf'),
        ('estrategia-gtm-saas-fintech.md', 'estrategia-gtm-saas-fintech.pdf')
    ]
    
    for md_file, pdf_file in files_to_convert:
        if os.path.exists(md_file):
            convert_md_to_pdf(md_file, pdf_file)
        else:
            print(f"⚠️  File {md_file} not found, skipping...")

if __name__ == "__main__":
    main()

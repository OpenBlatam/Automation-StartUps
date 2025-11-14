import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from markdown2 import markdown

def clean_html_content(html_content):
    """Clean and fix HTML content for better parsing"""
    # Remove problematic HTML tags and fix common issues
    html_content = re.sub(r'<em>([^<]*)</em>', r'<i>\1</i>', html_content)
    html_content = re.sub(r'<strong>([^<]*)</strong>', r'<b>\1</b>', html_content)
    html_content = re.sub(r'<code>([^<]*)</code>', r'<font name="Courier">\1</font>', html_content)
    html_content = re.sub(r'<pre>([^<]*)</pre>', r'<font name="Courier">\1</font>', html_content)
    
    # Fix paragraph issues
    html_content = re.sub(r'<para>([^<]*)</para>', r'<p>\1</p>', html_content)
    
    return html_content

def convert_md_to_pdf(md_file, pdf_file):
    """Convert a markdown file to PDF using ReportLab with improved HTML handling"""
    try:
        doc = SimpleDocTemplate(pdf_file, pagesize=letter, 
                              rightMargin=72, leftMargin=72, 
                              topMargin=72, bottomMargin=18)
        styles = getSampleStyleSheet()
        story = []

        # Create custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=12,
            textColor='#2E86AB'
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            textColor='#A23B72'
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=12,
            spaceAfter=8,
            textColor='#F18F01'
        )

        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert markdown to HTML
        html_content = markdown(md_content, extras=['fenced-code-blocks', 'tables'])
        
        # Clean HTML content
        html_content = clean_html_content(html_content)

        # Split content into lines and process
        lines = html_content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
                
            try:
                # Handle different HTML elements
                if line.startswith('<h1>'):
                    text = re.sub(r'<[^>]+>', '', line)
                    story.append(Paragraph(text, title_style))
                    story.append(Spacer(1, 12))
                    
                elif line.startswith('<h2>'):
                    text = re.sub(r'<[^>]+>', '', line)
                    story.append(Paragraph(text, heading_style))
                    story.append(Spacer(1, 10))
                    
                elif line.startswith('<h3>'):
                    text = re.sub(r'<[^>]+>', '', line)
                    story.append(Paragraph(text, subheading_style))
                    story.append(Spacer(1, 8))
                    
                elif line.startswith('<p>'):
                    text = re.sub(r'<[^>]+>', '', line)
                    if text.strip():
                        story.append(Paragraph(text, styles['Normal']))
                        story.append(Spacer(1, 6))
                        
                elif line.startswith('<li>'):
                    text = re.sub(r'<[^>]+>', '', line)
                    if text.strip():
                        story.append(Paragraph(f"• {text}", styles['Normal']))
                        story.append(Spacer(1, 4))
                        
                elif line.startswith('<ul>') or line.startswith('</ul>'):
                    # Skip list tags
                    pass
                    
                elif line.startswith('<code>') or line.startswith('</code>'):
                    # Handle code blocks
                    if line.startswith('<code>') and not line.startswith('</code>'):
                        text = re.sub(r'<[^>]+>', '', line)
                        if text.strip():
                            story.append(Paragraph(f"<font name='Courier'>{text}</font>", styles['Normal']))
                            story.append(Spacer(1, 4))
                            
                elif '```' in line:
                    # Handle fenced code blocks
                    if line.startswith('```'):
                        i += 1
                        code_lines = []
                        while i < len(lines) and not lines[i].strip().startswith('```'):
                            code_lines.append(lines[i])
                            i += 1
                        if code_lines:
                            code_text = '\n'.join(code_lines)
                            story.append(Paragraph(f"<font name='Courier'>{code_text}</font>", styles['Normal']))
                            story.append(Spacer(1, 8))
                            
                elif line.startswith('---'):
                    # Add page break for horizontal rules
                    story.append(PageBreak())
                    
                else:
                    # Handle regular text
                    if line and not line.startswith('<'):
                        # Clean any remaining HTML tags
                        clean_line = re.sub(r'<[^>]+>', '', line)
                        if clean_line.strip():
                            story.append(Paragraph(clean_line, styles['Normal']))
                            story.append(Spacer(1, 4))
                            
            except Exception as e:
                # Skip problematic lines
                print(f"Warning: Skipping problematic line: {line[:50]}...")
                
            i += 1

        doc.build(story)
        print(f"✅ Successfully converted {md_file} to {pdf_file}")
        
    except Exception as e:
        print(f"❌ Error converting {md_file}: {str(e)}")

def main():
    """Convert the improved formulas document"""
    files_to_convert = [
        ('formulas-avanzadas-anchor-texts.md', 'formulas-avanzadas-anchor-texts-mejorado.pdf')
    ]

    for md_file, pdf_file in files_to_convert:
        if os.path.exists(md_file):
            convert_md_to_pdf(md_file, pdf_file)
        else:
            print(f"⚠️ Warning: {md_file} not found. Skipping conversion.")

if __name__ == "__main__":
    main()





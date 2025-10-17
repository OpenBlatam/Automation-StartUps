#!/usr/bin/env python3
import markdown
import pdfkit
import os

def convert_md_to_pdf(md_file, pdf_file):
    """Convert Markdown file to PDF"""
    try:
        # Read markdown file
        with open(md_file, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        # Convert markdown to HTML
        html = markdown.markdown(md_content, extensions=['tables', 'toc', 'codehilite'])
        
        # Add CSS styling
        html_with_css = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 30px;
                    margin-bottom: 15px;
                }}
                h1 {{
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                }}
                h2 {{
                    border-bottom: 2px solid #ecf0f1;
                    padding-bottom: 5px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Monaco', 'Menlo', monospace;
                }}
                pre {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                blockquote {{
                    border-left: 4px solid #3498db;
                    margin: 20px 0;
                    padding: 10px 20px;
                    background-color: #f8f9fa;
                }}
                ul, ol {{
                    margin: 15px 0;
                    padding-left: 30px;
                }}
                li {{
                    margin: 5px 0;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        # Convert HTML to PDF
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'no-outline': None
        }
        
        pdfkit.from_string(html_with_css, pdf_file, options=options)
        print(f"✅ Successfully converted {md_file} to {pdf_file}")
        
    except Exception as e:
        print(f"❌ Error converting {md_file}: {str(e)}")

def main():
    """Convert all markdown files to PDF"""
    files_to_convert = [
        ('remote-company-culture-strategy.md', 'remote-company-culture-strategy.pdf'),
        ('curso-inteligencia-artificial-empresas.md', 'curso-inteligencia-artificial-empresas.pdf'),
        ('guia-marketing-saas.md', 'guia-marketing-saas.pdf')
    ]
    
    for md_file, pdf_file in files_to_convert:
        if os.path.exists(md_file):
            convert_md_to_pdf(md_file, pdf_file)
        else:
            print(f"⚠️  File {md_file} not found, skipping...")

if __name__ == "__main__":
    main()









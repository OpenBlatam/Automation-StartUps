#!/usr/bin/env python3
import os
import subprocess
import sys

def create_pdf():
    print("Creating PDF from HTML file...")
    
    # Try to install weasyprint if not available
    try:
        import weasyprint
        print("WeasyPrint found, creating PDF...")
        
        # Create PDF from HTML
        html_file = "Entregable2_Semana4_AdanPablo.html"
        pdf_file = "Entregable2_Semana4_AdanPablo.pdf"
        
        weasyprint.HTML(filename=html_file).write_pdf(pdf_file)
        print(f"PDF created successfully: {pdf_file}")
        return True
        
    except ImportError:
        print("WeasyPrint not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "weasyprint"])
            import weasyprint
            
            html_file = "Entregable2_Semana4_AdanPablo.html"
            pdf_file = "Entregable2_Semana4_AdanPablo.pdf"
            
            weasyprint.HTML(filename=html_file).write_pdf(pdf_file)
            print(f"PDF created successfully: {pdf_file}")
            return True
            
        except Exception as e:
            print(f"Could not install WeasyPrint: {e}")
            return False
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def manual_pdf_instructions():
    print("\n" + "="*80)
    print("MANUAL PDF CREATION INSTRUCTIONS")
    print("="*80)
    print("Since automatic PDF creation failed, please follow these steps:")
    print()
    print("METHOD 1 - Using Browser (Recommended):")
    print("1. Open the file 'Entregable2_Semana4_AdanPablo.html' in your web browser")
    print("2. Press Cmd+P (Mac) or Ctrl+P (Windows/Linux)")
    print("3. In the print dialog:")
    print("   - Select 'Save as PDF' as destination")
    print("   - Set margins to 'Minimum'")
    print("   - Check 'Background graphics'")
    print("   - Click 'Save'")
    print("4. Save as 'Entregable2_Semana4_AdanPablo.pdf'")
    print()
    print("METHOD 2 - Using Word/Pages:")
    print("1. Open 'Entregable2_Semana4_AdanPablo.docx' in Microsoft Word or Pages")
    print("2. Go to File > Export > PDF")
    print("3. Save as 'Entregable2_Semana4_AdanPablo.pdf'")
    print()
    print("METHOD 3 - Using Online Converter:")
    print("1. Go to an online HTML to PDF converter")
    print("2. Upload 'Entregable2_Semana4_AdanPablo.html'")
    print("3. Download the resulting PDF")
    print("="*80)

if __name__ == "__main__":
    if not create_pdf():
        manual_pdf_instructions()

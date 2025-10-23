#!/usr/bin/env python3
import webbrowser
import time
import os
import subprocess

def convert_html_to_pdf():
    # Get the current directory
    current_dir = os.getcwd()
    html_file = os.path.join(current_dir, "Entregable2_Semana4_AdanPablo.html")
    
    # Check if HTML file exists
    if not os.path.exists(html_file):
        print("HTML file not found!")
        return False
    
    # Open the HTML file in the default browser
    print("Opening HTML file in browser for PDF conversion...")
    webbrowser.open(f"file://{html_file}")
    
    print("\n" + "="*60)
    print("INSTRUCTIONS TO CREATE PDF:")
    print("="*60)
    print("1. The HTML file should now be open in your browser")
    print("2. Press Ctrl+P (or Cmd+P on Mac) to open print dialog")
    print("3. In the print dialog:")
    print("   - Select 'Save as PDF' as destination")
    print("   - Choose 'More settings' and set margins to 'Minimum'")
    print("   - Make sure 'Background graphics' is checked")
    print("   - Click 'Save'")
    print("4. Save the file as: Entregable2_Semana4_AdanPablo.pdf")
    print("="*60)
    
    return True

if __name__ == "__main__":
    convert_html_to_pdf()

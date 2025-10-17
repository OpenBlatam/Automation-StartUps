#!/usr/bin/env python3
"""
Script simple para crear PDF del Curso Premium de IA en Marketing
Usa reportlab para generar PDF directamente
"""

import os
import sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import re

def read_md_file(file_path):
    """Lee un archivo Markdown y retorna su contenido"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""
    except Exception as e:
        print(f"Error leyendo {file_path}: {e}")
        return ""

def parse_markdown_to_elements(md_content):
    """Convierte contenido Markdown a elementos de ReportLab"""
    elements = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=HexColor('#2c3e50'),
        alignment=TA_CENTER
    )
    
    h1_style = ParagraphStyle(
        'CustomH1',
        parent=styles['Heading1'],
        fontSize=20,
        spaceAfter=20,
        textColor=HexColor('#2c3e50'),
        spaceBefore=20
    )
    
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=15,
        textColor=HexColor('#34495e'),
        spaceBefore=15
    )
    
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=10,
        textColor=HexColor('#2980b9'),
        spaceBefore=10
    )
    
    h4_style = ParagraphStyle(
        'CustomH4',
        parent=styles['Heading4'],
        fontSize=12,
        spaceAfter=8,
        textColor=HexColor('#8e44ad'),
        spaceBefore=8
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=12,
        alignment=TA_JUSTIFY
    )
    
    # Dividir contenido en líneas
    lines = md_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            elements.append(Spacer(1, 6))
            continue
            
        # Títulos
        if line.startswith('# '):
            text = line[2:].strip()
            elements.append(Paragraph(text, title_style))
            elements.append(Spacer(1, 12))
            
        elif line.startswith('## '):
            text = line[3:].strip()
            elements.append(Paragraph(text, h1_style))
            elements.append(Spacer(1, 10))
            
        elif line.startswith('### '):
            text = line[4:].strip()
            elements.append(Paragraph(text, h2_style))
            elements.append(Spacer(1, 8))
            
        elif line.startswith('#### '):
            text = line[5:].strip()
            elements.append(Paragraph(text, h3_style))
            elements.append(Spacer(1, 6))
            
        elif line.startswith('##### '):
            text = line[6:].strip()
            elements.append(Paragraph(text, h4_style))
            elements.append(Spacer(1, 4))
            
        # Listas
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            # Convertir negritas
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
            # Convertir cursivas
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
            elements.append(Paragraph(f"• {text}", normal_style))
            
        elif line.startswith('1. ') or line.startswith('2. ') or line.startswith('3. ') or line.startswith('4. ') or line.startswith('5. '):
            text = line[3:].strip()
            # Convertir negritas
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
            text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
            # Convertir cursivas
            text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
            text = re.sub(r'_(.*?)_', r'<i>\1</i>', text)
            elements.append(Paragraph(f"{line[:2]} {text}", normal_style))
            
        # Separadores
        elif line.startswith('---'):
            elements.append(Spacer(1, 20))
            
        # Párrafos normales
        else:
            if line:
                # Convertir negritas
                line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                line = re.sub(r'__(.*?)__', r'<b>\1</b>', line)
                # Convertir cursivas
                line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
                line = re.sub(r'_(.*?)_', r'<i>\1</i>', line)
                # Convertir código
                line = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', line)
                
                elements.append(Paragraph(line, normal_style))
    
    return elements

def create_pdf(elements, output_path):
    """Crea el PDF con los elementos dados"""
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18
    )
    
    try:
        doc.build(elements)
        return True
    except Exception as e:
        print(f"Error creando PDF: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 Generando PDF del Curso Premium de IA en Marketing...")
    
    # Rutas de archivos
    base_dir = Path(".")
    file1 = base_dir / "AI_Marketing_Course_Complete_Structure.md"
    file2 = base_dir / "AI_Marketing_Course_Resources_Delivery_Marketing_Feedback.md"
    output_file = base_dir / "Curso_Premium_IA_Marketing_Completo.pdf"
    
    # Verificar que los archivos existen
    if not file1.exists():
        print(f"❌ Error: No se encontró {file1}")
        return False
    
    if not file2.exists():
        print(f"❌ Error: No se encontró {file2}")
        return False
    
    print("📖 Leyendo archivos Markdown...")
    
    # Leer contenido de ambos archivos
    content1 = read_md_file(file1)
    content2 = read_md_file(file2)
    
    if not content1 or not content2:
        print("❌ Error: No se pudo leer el contenido de los archivos")
        return False
    
    # Combinar contenido
    print("🔗 Combinando contenido...")
    combined_content = content1 + "\n\n" + content2
    
    # Convertir a elementos de ReportLab
    print("🎨 Procesando contenido...")
    elements = parse_markdown_to_elements(combined_content)
    
    # Generar PDF
    print("📄 Generando PDF...")
    if create_pdf(elements, output_file):
        print(f"✅ PDF generado exitosamente: {output_file}")
        if output_file.exists():
            file_size = output_file.stat().st_size / 1024 / 1024
            print(f"📊 Tamaño del archivo: {file_size:.2f} MB")
        return True
    else:
        print("❌ Error generando PDF")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 ¡PDF del curso generado exitosamente!")
            print("📧 El archivo está listo para compartir y distribuir.")
        else:
            print("\n💥 Error en la generación del PDF")
            sys.exit(1)
    except ImportError as e:
        print(f"❌ Error: Falta instalar una dependencia: {e}")
        print("💡 Instala las dependencias con: pip install reportlab")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)
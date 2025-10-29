#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_cover_designer():
    """Genera portadas personalizadas para diferentes versiones del libro"""
    
    # Configuración del documento de portadas
    doc = SimpleDocTemplate(
        "portadas_bioclones.pdf", 
        pagesize=A4,
        rightMargin=1*cm, 
        leftMargin=1*cm,
        topMargin=1*cm, 
        bottomMargin=1*cm,
        title="Portadas Bioclones - Diseño Editorial",
        author="Sistema de Diseño de Portadas Automático",
        subject="Ciencia Ficción - Diseño Editorial - Portadas Personalizadas",
        creator="Sistema de Diseño de Portadas Digital",
        keywords="portadas, diseño editorial, ciencia ficción, bioclones, clonación"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores para portadas
    primary_color = HexColor('#0f172a')      # Negro azulado profundo
    secondary_color = HexColor('#1e40af')    # Azul real
    accent_color = HexColor('#dc2626')      # Rojo vibrante
    gold_color = HexColor('#f59e0b')        # Dorado
    silver_color = HexColor('#6b7280')      # Plata
    light_gray = HexColor('#f8fafc')        # Gris muy claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos para portadas
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Heading1'],
        fontSize=48,
        spaceAfter=60,
        spaceBefore=40,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=56,
        borderWidth=8,
        borderColor=gold_color,
        borderPadding=40,
        backColor=light_gray
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Heading2'],
        fontSize=28,
        spaceAfter=50,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Oblique',
        leading=36,
        borderWidth=4,
        borderColor=accent_color,
        borderPadding=25,
        backColor=light_gray
    )
    
    author_style = ParagraphStyle(
        'CoverAuthor',
        parent=styles['Heading3'],
        fontSize=24,
        spaceAfter=40,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=text_gray,
        fontName='Helvetica',
        leading=30
    )
    
    description_style = ParagraphStyle(
        'CoverDescription',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=30,
        spaceBefore=20,
        alignment=TA_CENTER,
        leftIndent=60,
        rightIndent=60,
        fontName='Times-Italic',
        leading=24,
        textColor=text_gray
    )
    
    version_style = ParagraphStyle(
        'CoverVersion',
        parent=styles['Heading3'],
        fontSize=20,
        spaceAfter=30,
        spaceBefore=20,
        alignment=TA_CENTER,
        textColor=gold_color,
        fontName='Helvetica-Bold',
        leading=26
    )
    
    # Contenido del documento
    story = []
    
    # Portada 1: Edición Básica
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("BIOCLONES", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Edición Básica", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una historia sobre la naturaleza humana en la era de la clonación", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 50, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Manuscrito Original", author_style))
    story.append(PageBreak())
    
    # Portada 2: Edición Premium
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph("◆ BIOCLONES ◆", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Premium", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Explorando los límites entre lo humano y lo artificial", description_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("En un futuro donde la clonación es realidad", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 60, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Manuscrito Original • Edición Premium", author_style))
    story.append(PageBreak())
    
    # Portada 3: Edición Luxury
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("💎 BIOCLONES 💎", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Luxury", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Una obra maestra de la ciencia ficción contemporánea", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Donde la tecnología y la humanidad se entrelazan", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("En una danza eterna entre creación y destrucción", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 70, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Manuscrito Original • Edición Luxury", author_style))
    story.append(PageBreak())
    
    # Portada 4: Edición Professional
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph("BIOCLONES", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Professional", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Análisis de la identidad humana en la era tecnológica", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Una reflexión profunda sobre lo que nos hace humanos", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 60, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Manuscrito Original • Edición Professional", author_style))
    story.append(PageBreak())
    
    # Portada 5: Edición Master
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("👑 BIOCLONES 👑", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Master", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("La obra definitiva sobre clonación e identidad", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Una exploración filosófica de la naturaleza humana", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("En el contexto de la revolución biotecnológica", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 80, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Manuscrito Original • Edición Master", author_style))
    story.append(PageBreak())
    
    # Portada 6: Edición Académica
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("BIOCLONES", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Académica", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Análisis literario y contextualización histórica", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Incluye investigación académica y comparación literaria", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 60, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Manuscrito Original • Edición Académica", author_style))
    story.append(PageBreak())
    
    # Portada 7: Edición de Análisis
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("📊 BIOCLONES 📊", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Análisis Literario", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Investigación Académica", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Análisis computacional y estadístico del texto", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Metodología de investigación literaria", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Contextualización en la tradición de ciencia ficción", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 70, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Análisis Literario • Investigación Académica", author_style))
    story.append(PageBreak())
    
    # Portada 8: Edición de Comparación
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("📚 BIOCLONES 📚", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Comparación Literaria", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Análisis Comparativo", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Comparación con obras clásicas de ciencia ficción", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Análisis de técnicas narrativas y temas recurrentes", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Posicionamiento en la tradición literaria", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 70, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Análisis Comparativo • Tradición Literaria", author_style))
    story.append(PageBreak())
    
    # Portada 9: Edición Completa
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("🚀 BIOCLONES 🚀", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Sistema Completo", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Publicación Digital Integral", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("8 versiones diferentes del libro", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Análisis computacional y investigación académica", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Sistema de generación automática completo", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 80, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Sistema Completo • Publicación Digital", author_style))
    story.append(PageBreak())
    
    # Portada 10: Edición Final
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("🎉 BIOCLONES 🎉", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Final", version_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Sistema de Publicación Digital", subtitle_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("La transformación completa de un manuscrito", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("En un sistema profesional de publicación digital", description_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Con análisis académico y generación automática", description_style))
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("─" * 80, author_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Edición Final • Sistema Completo", author_style))
    
    # Función para numerar páginas
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 12)
        page_num = canvas.getPageNumber()
        text = f"Portada {page_num}"
        canvas.drawRightString(200*cm, 20*cm, text)
        canvas.restoreState()
    
    # Construir el PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print("Portadas personalizadas creadas exitosamente: portadas_bioclones.pdf")

if __name__ == "__main__":
    create_cover_designer()





















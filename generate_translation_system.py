#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_translation_system():
    """Genera un sistema de traducción automática para Bioclones"""
    
    # Configuración del documento de traducción
    doc = SimpleDocTemplate(
        "sistema_traduccion_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Traducción - Bioclones",
        author="Sistema de Traducción Automática",
        subject="Ciencia Ficción - Traducción - Internacionalización",
        creator="Sistema de Traducción Digital",
        keywords="traducción, internacionalización, ciencia ficción, bioclones, multilingüe"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores internacional
    primary_color = HexColor('#1e40af')      # Azul internacional
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de traducción
    title_style = ParagraphStyle(
        'TranslationTitle',
        parent=styles['Heading1'],
        fontSize=28,
        spaceAfter=50,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=34,
        borderWidth=3,
        borderColor=accent_color,
        borderPadding=20,
        backColor=light_gray
    )
    
    subtitle_style = ParagraphStyle(
        'TranslationSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        spaceAfter=40,
        spaceBefore=25,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Bold',
        leading=26
    )
    
    section_style = ParagraphStyle(
        'TranslationSection',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=30,
        spaceBefore=35,
        alignment=TA_LEFT,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=24,
        borderWidth=2,
        borderColor=accent_color,
        borderPadding=15,
        backColor=light_gray,
        leftIndent=15
    )
    
    body_style = ParagraphStyle(
        'TranslationBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        spaceBefore=8,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Times-Roman',
        leading=17,
        textColor=text_gray
    )
    
    language_style = ParagraphStyle(
        'LanguageStyle',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        spaceBefore=15,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        textColor=secondary_color,
        leftIndent=20,
        leading=20
    )
    
    # Contenido del documento
    story = []
    
    # Portada de traducción
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("🌍 SISTEMA DE TRADUCCIÓN", title_style))
    story.append(Paragraph("Bioclones - Internacionalización Digital", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Traducción Automática</b><br/>
    <br/>
    <i>Internacionalización de Bioclones para mercados globales</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción para el mundo</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Idiomas: Múltiples | Mercados: Globales | Tecnología: IA
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Estrategia de internacionalización
    story.append(Paragraph("ESTRATEGIA DE INTERNACIONALIZACIÓN", section_style))
    
    estrategia_text = """
    La internacionalización de Bioclones representa una oportunidad única para llevar esta obra de ciencia ficción a mercados globales. El enfoque en temas universales como la identidad, la tecnología y la humanidad hace que la obra sea especialmente adecuada para la traducción y adaptación cultural.
    """
    story.append(Paragraph(estrategia_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Objetivos de Internacionalización", subtitle_style))
    objetivos = [
        "Expandir el alcance de Bioclones a mercados internacionales",
        "Adaptar el contenido a diferentes culturas y contextos",
        "Mantener la esencia literaria en todas las traducciones",
        "Crear versiones localizadas para diferentes regiones",
        "Establecer presencia global en el mercado de ciencia ficción"
    ]
    
    for objetivo in objetivos:
        story.append(Paragraph(f"• {objetivo}", language_style))
    
    story.append(PageBreak())
    
    # Idiomas objetivo
    story.append(Paragraph("IDIOMAS OBJETIVO", section_style))
    
    idiomas_text = """
    La selección de idiomas objetivo se basa en el tamaño del mercado, la demanda de ciencia ficción y la viabilidad técnica de la traducción.
    """
    story.append(Paragraph(idiomas_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de idiomas objetivo
    idiomas_data = [
        ['Idioma', 'Mercado', 'Prioridad', 'Complejidad', 'Estrategia'],
        ['Inglés', 'Global', 'Alta', 'Media', 'Traducción directa'],
        ['Francés', 'Europa', 'Alta', 'Media', 'Adaptación cultural'],
        ['Alemán', 'Europa', 'Alta', 'Alta', 'Traducción literaria'],
        ['Italiano', 'Europa', 'Media', 'Media', 'Adaptación regional'],
        ['Portugués', 'Brasil', 'Media', 'Media', 'Localización'],
        ['Japonés', 'Asia', 'Alta', 'Alta', 'Adaptación cultural'],
        ['Chino', 'Asia', 'Alta', 'Alta', 'Traducción especializada'],
        ['Ruso', 'Europa del Este', 'Media', 'Alta', 'Traducción literaria'],
        ['Árabe', 'Medio Oriente', 'Media', 'Alta', 'Adaptación cultural'],
        ['Español', 'Latinoamérica', 'Alta', 'Media', 'Localización regional']
    ]
    
    idiomas_table = Table(idiomas_data, colWidths=[2*cm, 2.5*cm, 1.5*cm, 1.5*cm, 3*cm])
    idiomas_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
        ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, HexColor('#ffffff')]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
    ]))
    
    story.append(idiomas_table)
    story.append(PageBreak())
    
    # Metodología de traducción
    story.append(Paragraph("METODOLOGÍA DE TRADUCCIÓN", section_style))
    
    metodologia_text = """
    La traducción de Bioclones requiere un enfoque especializado que combine tecnología de traducción automática con revisión humana experta para mantener la calidad literaria y la fidelidad al texto original.
    """
    story.append(Paragraph(metodologia_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Fases del Proceso de Traducción", subtitle_style))
    fases = [
        "Análisis del texto original y identificación de elementos culturales",
        "Traducción automática inicial usando IA especializada en literatura",
        "Revisión humana por traductores nativos especializados en ciencia ficción",
        "Adaptación cultural y localización para el mercado objetivo",
        "Revisión final y control de calidad por editores literarios",
        "Pruebas de lectura con lectores nativos del idioma objetivo"
    ]
    
    for fase in fases:
        story.append(Paragraph(f"• {fase}", language_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tecnologías Utilizadas", subtitle_style))
    tecnologias = [
        "Traducción automática neuronal (NMT) especializada en literatura",
        "Análisis de sentimientos para mantener el tono emocional",
        "Identificación automática de elementos culturales",
        "Herramientas de localización y adaptación cultural",
        "Sistemas de control de calidad automatizado",
        "Plataformas de colaboración para traductores humanos"
    ]
    
    for tecnologia in tecnologias:
        story.append(Paragraph(f"• {tecnologia}", language_style))
    
    story.append(PageBreak())
    
    # Adaptación cultural
    story.append(Paragraph("ADAPTACIÓN CULTURAL", section_style))
    
    adaptacion_text = """
    La adaptación cultural es crucial para el éxito de Bioclones en mercados internacionales. Cada traducción debe considerar las diferencias culturales, las referencias locales y las expectativas del público objetivo.
    """
    story.append(Paragraph(adaptacion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Elementos de Adaptación Cultural", subtitle_style))
    elementos = [
        "Referencias culturales y históricas específicas de cada región",
        "Adaptación de nombres y lugares a la fonética local",
        "Modificación de expresiones idiomáticas y metáforas",
        "Ajuste del tono y estilo narrativo a las preferencias locales",
        "Consideración de sensibilidades culturales y tabúes",
        "Adaptación de elementos tecnológicos a la realidad local"
    ]
    
    for elemento in elementos:
        story.append(Paragraph(f"• {elemento}", language_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Ejemplos de Adaptación", subtitle_style))
    ejemplos = [
        "G.R.E.E. → Adaptación del acrónimo según la cultura local",
        "Capital Biológica → Traducción que mantenga el concepto pero suene natural",
        "Diálogos filosóficos → Adaptación del lenguaje filosófico a la tradición local",
        "Referencias tecnológicas → Actualización a la tecnología local",
        "Elementos poéticos → Adaptación a la tradición poética local"
    ]
    
    for ejemplo in ejemplos:
        story.append(Paragraph(f"• {ejemplo}", language_style))
    
    story.append(PageBreak())
    
    # Control de calidad
    story.append(Paragraph("CONTROL DE CALIDAD", section_style))
    
    calidad_text = """
    El control de calidad en la traducción de Bioclones es esencial para mantener la integridad literaria y la experiencia del lector en todos los idiomas.
    """
    story.append(Paragraph(calidad_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Estándares de Calidad", subtitle_style))
    estandares = [
        "Fidelidad al texto original manteniendo la esencia literaria",
        "Fluidez natural en el idioma objetivo",
        "Consistencia terminológica a lo largo de toda la obra",
        "Precisión en la traducción de conceptos científicos y tecnológicos",
        "Mantenimiento del tono emocional y atmosférico",
        "Adaptación cultural apropiada sin perder el mensaje original"
    ]
    
    for estandar in estandares:
        story.append(Paragraph(f"• {estandar}", language_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Proceso de Revisión", subtitle_style))
    revision = [
        "Revisión automática de consistencia terminológica",
        "Análisis de sentimientos para verificar el tono emocional",
        "Revisión humana por traductores nativos especializados",
        "Pruebas de lectura con lectores objetivo",
        "Comparación con el texto original para verificar fidelidad",
        "Ajustes finales basados en feedback de lectores"
    ]
    
    for proceso in revision:
        story.append(Paragraph(f"• {proceso}", language_style))
    
    story.append(PageBreak())
    
    # Distribución internacional
    story.append(Paragraph("DISTRIBUCIÓN INTERNACIONAL", section_style))
    
    distribucion_text = """
    La distribución internacional de Bioclones requiere una estrategia coordinada que considere las particularidades de cada mercado y las preferencias de los lectores locales.
    """
    story.append(Paragraph(distribucion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Canales de Distribución", subtitle_style))
    canales = [
        "Plataformas digitales globales (Amazon, Apple Books, Google Play)",
        "Librerías locales y cadenas internacionales",
        "Bibliotecas públicas y universitarias",
        "Ferias del libro internacionales",
        "Medios de comunicación especializados en ciencia ficción",
        "Comunidades online y redes sociales locales"
    ]
    
    for canal in canales:
        story.append(Paragraph(f"• {canal}", language_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Estrategias de Marketing Local", subtitle_style))
    estrategias = [
        "Adaptación de materiales promocionales a cada mercado",
        "Colaboración con influencers y críticos literarios locales",
        "Participación en eventos y festivales de ciencia ficción",
        "Estrategias de precios adaptadas a cada mercado",
        "Promoción a través de medios locales especializados",
        "Creación de comunidades de lectores en cada idioma"
    ]
    
    for estrategia in estrategias:
        story.append(Paragraph(f"• {estrategia}", language_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de traducción generado automáticamente —<br/>
    <br/>
    <b>Internacionalización digital</b><br/>
    <i>Bioclones para el mundo</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Traducción Automática Digital
    </font>
    </para>
    """
    story.append(Paragraph(cierre_text, body_style))
    
    # Función para numerar páginas
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 10)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.drawRightString(200*cm, 20*cm, text)
        canvas.restoreState()
    
    # Construir el PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print("Sistema de traducción creado exitosamente: sistema_traduccion_bioclones.pdf")

if __name__ == "__main__":
    create_translation_system()













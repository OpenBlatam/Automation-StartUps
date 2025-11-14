#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime
import json

def create_marketing_materials():
    """Genera materiales de marketing para promocionar Bioclones"""
    
    # Configuración del documento de marketing
    doc = SimpleDocTemplate(
        "materiales_marketing_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Materiales de Marketing - Bioclones",
        author="Sistema de Marketing Digital Automático",
        subject="Ciencia Ficción - Marketing Digital - Promoción Editorial",
        creator="Sistema de Marketing Digital",
        keywords="marketing, promoción, ciencia ficción, bioclones, editorial"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores de marketing
    primary_color = HexColor('#1e40af')      # Azul corporativo
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')       # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de marketing
    title_style = ParagraphStyle(
        'MarketingTitle',
        parent=styles['Heading1'],
        fontSize=32,
        spaceAfter=50,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=40,
        borderWidth=4,
        borderColor=accent_color,
        borderPadding=25,
        backColor=light_gray
    )
    
    subtitle_style = ParagraphStyle(
        'MarketingSubtitle',
        parent=styles['Heading2'],
        fontSize=24,
        spaceAfter=40,
        spaceBefore=25,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Bold',
        leading=30
    )
    
    section_style = ParagraphStyle(
        'MarketingSection',
        parent=styles['Heading2'],
        fontSize=20,
        spaceAfter=30,
        spaceBefore=35,
        alignment=TA_LEFT,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=26,
        borderWidth=2,
        borderColor=accent_color,
        borderPadding=15,
        backColor=light_gray,
        leftIndent=15
    )
    
    body_style = ParagraphStyle(
        'MarketingBody',
        parent=styles['Normal'],
        fontSize=13,
        spaceAfter=15,
        spaceBefore=8,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Times-Roman',
        leading=18,
        textColor=text_gray
    )
    
    highlight_style = ParagraphStyle(
        'MarketingHighlight',
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
    
    # Portada de marketing
    story.append(Spacer(1, 4*inch))
    story.append(Paragraph("🚀 MATERIALES DE MARKETING", title_style))
    story.append(Paragraph("Bioclones - Estrategia de Promoción Digital", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="16" fontName="Helvetica" textColor="#374151">
    <b>Estrategia de Marketing Digital</b><br/>
    <br/>
    <i>Materiales de promoción para Bioclones</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción que explora la clonación e identidad</b><br/>
    <br/>
    <font size="14" color="#6b7280">
    Género: Ciencia Ficción | Tema: Clonación e Identidad<br/>
    Público: Adultos | Estilo: Narrativa Experimental
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Estrategia de marketing
    story.append(Paragraph("ESTRATEGIA DE MARKETING DIGITAL", section_style))
    
    estrategia_text = """
    Bioclones representa una oportunidad única en el mercado de la ciencia ficción contemporánea. Su enfoque en temas de clonación e identidad, combinado con técnicas narrativas experimentales, lo posiciona como una obra innovadora que puede atraer tanto a lectores de ciencia ficción tradicional como a nuevos públicos interesados en temas de tecnología y humanidad.
    """
    story.append(Paragraph(estrategia_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Objetivos de Marketing", subtitle_style))
    objetivos = [
        "Posicionar Bioclones como una obra innovadora de ciencia ficción",
        "Atraer lectores interesados en temas de tecnología y humanidad",
        "Generar interés en la comunidad académica y literaria",
        "Establecer presencia en redes sociales y plataformas digitales",
        "Crear una base de lectores fieles para futuras publicaciones"
    ]
    
    for objetivo in objetivos:
        story.append(Paragraph(f"• {objetivo}", highlight_style))
    
    story.append(PageBreak())
    
    # Público objetivo
    story.append(Paragraph("PÚBLICO OBJETIVO", section_style))
    
    publico_text = """
    El análisis del contenido y temas de Bioclones permite identificar varios segmentos de público objetivo que pueden ser especialmente receptivos a la obra:
    """
    story.append(Paragraph(publico_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de público objetivo
    publico_data = [
        ['Segmento', 'Características', 'Estrategia'],
        ['Lectores de Ciencia Ficción', 'Interesados en temas futuristas y tecnológicos', 'Marketing en comunidades de sci-fi'],
        ['Académicos y Estudiantes', 'Interesados en análisis literario y cultural', 'Presentaciones académicas'],
        ['Profesionales de Tecnología', 'Interesados en ética tecnológica', 'Conferencias y eventos tech'],
        ['Lectores de Literatura Experimental', 'Interesados en técnicas narrativas innovadoras', 'Festivales literarios'],
        ['Público General', 'Interesado en temas de identidad y humanidad', 'Marketing digital amplio']
    ]
    
    publico_table = Table(publico_data, colWidths=[4*cm, 5*cm, 4*cm])
    publico_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
        ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, HexColor('#ffffff')]),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
    ]))
    
    story.append(publico_table)
    story.append(PageBreak())
    
    # Canales de marketing
    story.append(Paragraph("CANALES DE MARKETING", section_style))
    
    canales_text = """
    La promoción de Bioclones debe utilizar una estrategia multicanal que combine canales digitales y tradicionales para maximizar el alcance y la visibilidad de la obra.
    """
    story.append(Paragraph(canales_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Canales Digitales", subtitle_style))
    canales_digitales = [
        "Redes sociales (Twitter, Instagram, LinkedIn, Facebook)",
        "Blogs y sitios web especializados en ciencia ficción",
        "Plataformas de lectura digital (Kindle, Kobo, etc.)",
        "YouTube para contenido audiovisual y reseñas",
        "Podcasts especializados en literatura y ciencia ficción",
        "Comunidades online (Reddit, Goodreads, etc.)"
    ]
    
    for canal in canales_digitales:
        story.append(Paragraph(f"• {canal}", highlight_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Canales Tradicionales", subtitle_style))
    canales_tradicionales = [
        "Ferias del libro y eventos literarios",
        "Librerías independientes y cadenas",
        "Bibliotecas públicas y universitarias",
        "Medios de comunicación especializados",
        "Conferencias académicas y literarias",
        "Clubes de lectura y grupos literarios"
    ]
    
    for canal in canales_tradicionales:
        story.append(Paragraph(f"• {canal}", highlight_style))
    
    story.append(PageBreak())
    
    # Contenido de marketing
    story.append(Paragraph("CONTENIDO DE MARKETING", section_style))
    
    contenido_text = """
    El contenido de marketing para Bioclones debe destacar los aspectos únicos de la obra, incluyendo su enfoque en temas contemporáneos, técnicas narrativas experimentales y relevancia cultural.
    """
    story.append(Paragraph(contenido_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Mensajes Clave", subtitle_style))
    mensajes = [
        "Una exploración profunda de la identidad humana en la era de la clonación",
        "Técnicas narrativas innovadoras que desafían las convenciones literarias",
        "Relevancia contemporánea en debates sobre tecnología y ética",
        "Una obra que anticipa debates futuros sobre biotecnología",
        "Literatura de ciencia ficción que trasciende el género"
    ]
    
    for mensaje in mensajes:
        story.append(Paragraph(f"• {mensaje}", highlight_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Materiales Promocionales", subtitle_style))
    materiales = [
        "Reseñas y análisis literario",
        "Entrevistas con el autor (ficticias)",
        "Contenido audiovisual (book trailers, podcasts)",
        "Materiales gráficos (infografías, citas destacadas)",
        "Contenido educativo (guías de lectura, análisis temático)",
        "Testimonios y recomendaciones"
    ]
    
    for material in materiales:
        story.append(Paragraph(f"• {material}", highlight_style))
    
    story.append(PageBreak())
    
    # Estrategia de precios
    story.append(Paragraph("ESTRATEGIA DE PRECIOS", section_style))
    
    precios_text = """
    La estrategia de precios para Bioclones debe considerar su posicionamiento como obra literaria de calidad, su audiencia objetivo y el valor único que ofrece en términos de contenido y formato.
    """
    story.append(Paragraph(precios_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de estrategia de precios
    precios_data = [
        ['Versión', 'Precio Sugerido', 'Público Objetivo', 'Justificación'],
        ['Edición Básica', 'Gratuita', 'Lectores generales', 'Generar interés y base de lectores'],
        ['Edición Premium', '$9.99', 'Lectores comprometidos', 'Valor agregado con diseño mejorado'],
        ['Edición Luxury', '$19.99', 'Coleccionistas', 'Diseño de lujo y elementos exclusivos'],
        ['Edición Master', '$29.99', 'Académicos', 'Análisis completo y documentación'],
        ['Paquete Completo', '$39.99', 'Super fans', 'Todas las versiones + análisis']
    ]
    
    precios_table = Table(precios_data, colWidths=[3*cm, 2*cm, 4*cm, 4*cm])
    precios_table.setStyle(TableStyle([
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
    
    story.append(precios_table)
    story.append(PageBreak())
    
    # Métricas y KPIs
    story.append(Paragraph("MÉTRICAS Y KPIs", section_style))
    
    metricas_text = """
    Para medir el éxito de la estrategia de marketing de Bioclones, es importante establecer métricas claras que permitan evaluar el rendimiento y ajustar la estrategia según sea necesario.
    """
    story.append(Paragraph(metricas_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Métricas de Alcance", subtitle_style))
    metricas_alcance = [
        "Número de descargas por versión",
        "Alcance en redes sociales",
        "Menciones en medios y blogs",
        "Tráfico web generado",
        "Participación en eventos y ferias"
    ]
    
    for metrica in metricas_alcance:
        story.append(Paragraph(f"• {metrica}", highlight_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Métricas de Engagement", subtitle_style))
    metricas_engagement = [
        "Tiempo de lectura promedio",
        "Comentarios y reseñas",
        "Compartidos en redes sociales",
        "Participación en discusiones",
        "Solicitudes de información adicional"
    ]
    
    for metrica in metricas_engagement:
        story.append(Paragraph(f"• {metrica}", highlight_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Métricas de Conversión", subtitle_style))
    metricas_conversion = [
        "Conversión de descarga gratuita a pago",
        "Ventas por canal de marketing",
        "Retención de lectores",
        "Recomendaciones y referencias",
        "Participación en comunidades"
    ]
    
    for metrica in metricas_conversion:
        story.append(Paragraph(f"• {metrica}", highlight_style))
    
    story.append(PageBreak())
    
    # Cronograma de lanzamiento
    story.append(Paragraph("CRONOGRAMA DE LANZAMIENTO", section_style))
    
    cronograma_text = """
    El lanzamiento de Bioclones debe seguir un cronograma estructurado que permita generar expectativa, maximizar el impacto inicial y mantener el interés a largo plazo.
    """
    story.append(Paragraph(cronograma_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de cronograma
    cronograma_data = [
        ['Fase', 'Duración', 'Actividades', 'Objetivos'],
        ['Pre-lanzamiento', '4 semanas', 'Teaser, contenido previo', 'Generar expectativa'],
        ['Lanzamiento', '2 semanas', 'Lanzamiento oficial, PR', 'Máximo impacto inicial'],
        ['Post-lanzamiento', '8 semanas', 'Marketing continuo', 'Mantener interés'],
        ['Sostenimiento', 'Ongoing', 'Contenido regular', 'Comunidad activa']
    ]
    
    cronograma_table = Table(cronograma_data, colWidths=[3*cm, 2*cm, 4*cm, 4*cm])
    cronograma_table.setStyle(TableStyle([
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
    
    story.append(cronograma_table)
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Estrategia de marketing generada automáticamente —<br/>
    <br/>
    <b>Materiales de promoción digital</b><br/>
    <i>Estrategia integral para Bioclones</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Marketing Digital Automático
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
    print("Materiales de marketing creados exitosamente: materiales_marketing_bioclones.pdf")

if __name__ == "__main__":
    create_marketing_materials()













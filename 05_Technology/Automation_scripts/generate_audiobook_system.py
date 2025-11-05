#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_audiobook_system():
    """Genera un sistema de audiolibros para Bioclones"""
    
    # Configuración del documento de audiolibros
    doc = SimpleDocTemplate(
        "sistema_audiolibros_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Audiolibros - Bioclones",
        author="Sistema de Audiolibros Automático",
        subject="Ciencia Ficción - Audiolibros - Audio Digital",
        creator="Sistema de Audiolibros Digital",
        keywords="audiolibros, audio, ciencia ficción, bioclones, narración"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores de audio
    primary_color = HexColor('#1e40af')      # Azul audio
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de audiolibros
    title_style = ParagraphStyle(
        'AudiobookTitle',
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
        'AudiobookSubtitle',
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
        'AudiobookSection',
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
        'AudiobookBody',
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
    
    audio_style = ParagraphStyle(
        'AudioStyle',
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
    
    # Portada de audiolibros
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("🎧 SISTEMA DE AUDIOLIBROS", title_style))
    story.append(Paragraph("Bioclones - Experiencia de Audio Inmersiva", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Audiolibros Automático</b><br/>
    <br/>
    <i>Transformación de Bioclones en experiencia de audio</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción para escuchar</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Formato: Audio Digital | Calidad: Alta | Duración: ~3 horas
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Estrategia de audiolibros
    story.append(Paragraph("ESTRATEGIA DE AUDIOLIBROS", section_style))
    
    estrategia_text = """
    La transformación de Bioclones en audiolibro representa una oportunidad única para crear una experiencia inmersiva que aproveche las características especiales de la obra, incluyendo sus elementos poéticos, filosóficos y de ciencia ficción.
    """
    story.append(Paragraph(estrategia_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Objetivos del Audiolibro", subtitle_style))
    objetivos = [
        "Crear una experiencia de audio inmersiva y envolvente",
        "Mantener la esencia literaria y poética de la obra",
        "Aprovechar las características narrativas experimentales",
        "Llegar a audiencias que prefieren el formato audio",
        "Crear una experiencia accesible para personas con discapacidad visual",
        "Establecer presencia en el mercado de audiolibros de ciencia ficción"
    ]
    
    for objetivo in objetivos:
        story.append(Paragraph(f"• {objetivo}", audio_style))
    
    story.append(PageBreak())
    
    # Especificaciones técnicas
    story.append(Paragraph("ESPECIFICACIONES TÉCNICAS", section_style))
    
    especificaciones_text = """
    Las especificaciones técnicas del audiolibro de Bioclones deben garantizar la máxima calidad de audio y una experiencia de escucha óptima.
    """
    story.append(Paragraph(especificaciones_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de especificaciones
    especificaciones_data = [
        ['Parámetro', 'Especificación', 'Justificación'],
        ['Formato de Audio', 'MP3 320 kbps / FLAC', 'Calidad alta, compatibilidad universal'],
        ['Frecuencia de Muestreo', '44.1 kHz', 'Calidad CD estándar'],
        ['Canales', 'Estéreo', 'Experiencia inmersiva'],
        ['Duración Total', '~3 horas', 'Longitud óptima para audiolibro'],
        ['Capítulos', '6 capítulos', 'Estructura del libro original'],
        ['Pausas', '30 segundos entre capítulos', 'Transición natural'],
        ['Volumen', 'Normalizado a -23 LUFS', 'Consistencia de volumen'],
        ['Ruido de Fondo', '< -60 dB', 'Audio limpio y profesional']
    ]
    
    especificaciones_table = Table(especificaciones_data, colWidths=[3*cm, 4*cm, 5*cm])
    especificaciones_table.setStyle(TableStyle([
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
    
    story.append(especificaciones_table)
    story.append(PageBreak())
    
    # Narración y voces
    story.append(Paragraph("NARRACIÓN Y VOCES", section_style))
    
    narracion_text = """
    La selección de narradores y el diseño de voces para el audiolibro de Bioclones es crucial para mantener la atmósfera y el tono de la obra original.
    """
    story.append(Paragraph(narracion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Características del Narrador", subtitle_style))
    caracteristicas = [
        "Voz masculina adulta, cálida y expresiva",
        "Capacidad para transmitir emociones y matices",
        "Experiencia en narrativa de ciencia ficción",
        "Pronunciación clara y dicción perfecta",
        "Capacidad para diferenciar voces de personajes",
        "Tono que refleje la naturaleza filosófica de la obra"
    ]
    
    for caracteristica in caracteristicas:
        story.append(Paragraph(f"• {caracteristica}", audio_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Voces de Personajes", subtitle_style))
    voces = [
        "Sophie: Voz femenina joven, inteligente y cálida",
        "Anthony: Voz masculina joven, con matices de miedo y vulnerabilidad",
        "Francisco: Voz masculina adulta, autoritaria y profesional",
        "Roger: Voz masculina adulta, amigable y confiable",
        "Narrador: Voz neutra que guía la historia",
        "Diálogos: Diferenciación clara entre personajes"
    ]
    
    for voz in voces:
        story.append(Paragraph(f"• {voz}", audio_style))
    
    story.append(PageBreak())
    
    # Elementos sonoros
    story.append(Paragraph("ELEMENTOS SONOROS", section_style))
    
    elementos_text = """
    Los elementos sonoros del audiolibro de Bioclones deben crear una atmósfera inmersiva que complemente la narrativa sin distraer del contenido.
    """
    story.append(Paragraph(elementos_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Música de Fondo", subtitle_style))
    musica = [
        "Tema principal: Música electrónica suave y futurista",
        "Transiciones: Efectos sonoros sutiles entre capítulos",
        "Atmósfera: Sonidos ambientales de laboratorio y tecnología",
        "Intensidad: Música que refleje el tono emocional de cada escena",
        "Duración: Máximo 30% del tiempo total de audio",
        "Volumen: Siempre por debajo de la voz del narrador"
    ]
    
    for elemento in musica:
        story.append(Paragraph(f"• {elemento}", audio_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Efectos Sonoros", subtitle_style))
    efectos = [
        "Sonidos de laboratorio: Beeps, zumbidos, ventiladores",
        "Ambiente espacial: Sonidos de nave espacial, gravedad cero",
        "Tecnología: Sonidos de computadoras, pantallas, interfaces",
        "Naturaleza: Sonidos de la Tierra para contrastar con el espacio",
        "Emociones: Sonidos que refuercen estados emocionales",
        "Transiciones: Efectos sutiles para cambios de escena"
    ]
    
    for efecto in efectos:
        story.append(Paragraph(f"• {efecto}", audio_style))
    
    story.append(PageBreak())
    
    # Estructura del audiolibro
    story.append(Paragraph("ESTRUCTURA DEL AUDIOLIBRO", section_style))
    
    estructura_text = """
    La estructura del audiolibro de Bioclones debe optimizar la experiencia de escucha manteniendo la integridad narrativa de la obra original.
    """
    story.append(Paragraph(estructura_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de estructura
    estructura_data = [
        ['Capítulo', 'Duración', 'Contenido', 'Elementos Sonoros'],
        ['Introducción', '5 min', 'Presentación y contexto', 'Música futurista'],
        ['Capítulo 1', '25 min', 'Nuestro objetivo', 'Sonidos de laboratorio'],
        ['Capítulo 2', '20 min', 'Elisa y Canon', 'Transición suave'],
        ['Capítulo 3', '30 min', 'Error y Acierto', 'Música emocional'],
        ['Capítulo 4', '35 min', 'Dios Clones', 'Sonidos tecnológicos'],
        ['Capítulo 5', '25 min', 'Sophie y yo', 'Música romántica'],
        ['Capítulo 6', '30 min', 'Borradores', 'Poesía con música'],
        ['Epílogo', '10 min', 'Reflexión final', 'Música de cierre']
    ]
    
    estructura_table = Table(estructura_data, colWidths=[2*cm, 2*cm, 4*cm, 4*cm])
    estructura_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
        ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, HexColor('#ffffff')]),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
    ]))
    
    story.append(estructura_table)
    story.append(PageBreak())
    
    # Distribución y marketing
    story.append(Paragraph("DISTRIBUCIÓN Y MARKETING", section_style))
    
    distribucion_text = """
    La distribución del audiolibro de Bioclones debe aprovechar las plataformas especializadas en audiolibros y crear estrategias de marketing específicas para este formato.
    """
    story.append(Paragraph(distribucion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Plataformas de Distribución", subtitle_style))
    plataformas = [
        "Audible (Amazon) - Plataforma líder en audiolibros",
        "Apple Books - Integración con ecosistema Apple",
        "Google Play Books - Acceso a usuarios Android",
        "Spotify - Plataforma de audio en streaming",
        "Librivox - Plataforma de audiolibros gratuitos",
        "Plataformas especializadas en ciencia ficción"
    ]
    
    for plataforma in plataformas:
        story.append(Paragraph(f"• {plataforma}", audio_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Estrategias de Marketing", subtitle_style))
    estrategias = [
        "Muestras de audio gratuitas en plataformas",
        "Podcasts promocionales con fragmentos del audiolibro",
        "Colaboraciones con influencers de ciencia ficción",
        "Marketing en comunidades de audiolibros",
        "Estrategias de precios competitivos",
        "Promoción en eventos de ciencia ficción"
    ]
    
    for estrategia in estrategias:
        story.append(Paragraph(f"• {estrategia}", audio_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de audiolibros generado automáticamente —<br/>
    <br/>
    <b>Experiencia de audio inmersiva</b><br/>
    <i>Bioclones para escuchar</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Audiolibros Digitales Automáticos
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
    print("Sistema de audiolibros creado exitosamente: sistema_audiolibros_bioclones.pdf")

if __name__ == "__main__":
    create_audiobook_system()













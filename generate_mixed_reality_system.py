#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_mixed_reality_system():
    """Genera un sistema de realidad mixta para Bioclones"""
    
    # Configuración del documento de realidad mixta
    doc = SimpleDocTemplate(
        "sistema_realidad_mixta_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Realidad Mixta - Bioclones",
        author="Sistema de Realidad Mixta Automático",
        subject="Ciencia Ficción - Realidad Mixta - MR/XR - Hologramas",
        creator="Sistema de Realidad Mixta Digital",
        keywords="realidad mixta, mr, xr, hologramas, ciencia ficción, bioclones, realidad híbrida"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores realidad mixta
    primary_color = HexColor('#1e40af')      # Azul MR
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de realidad mixta
    title_style = ParagraphStyle(
        'MixedRealityTitle',
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
        'MixedRealitySubtitle',
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
        'MixedRealitySection',
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
        'MixedRealityBody',
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
    
    mr_style = ParagraphStyle(
        'MixedRealityStyle',
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
    
    # Portada de realidad mixta
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("🔮 SISTEMA DE REALIDAD MIXTA", title_style))
    story.append(Paragraph("Bioclones - Experiencia MR Híbrida", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Realidad Mixta Automático</b><br/>
    <br/>
    <i>Bioclones en realidad mixta</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción en MR</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: MR/XR | Hologramas: Avanzados | Experiencia: Híbrida
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Arquitectura de realidad mixta
    story.append(Paragraph("ARQUITECTURA DE REALIDAD MIXTA", section_style))
    
    arquitectura_text = """
    El sistema de realidad mixta para Bioclones debe combinar elementos del mundo real y virtual de manera fluida, creando experiencias híbridas inmersivas.
    """
    story.append(Paragraph(arquitectura_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Componentes del Sistema MR", subtitle_style))
    componentes = [
        "Fusión de mundos reales y virtuales",
        "Hologramas interactivos en 3D",
        "Tracking preciso de objetos reales",
        "Oclusión y sombras realistas",
        "Interacción natural con elementos híbridos",
        "Persistencia de objetos virtuales"
    ]
    
    for componente in componentes:
        story.append(Paragraph(f"• {componente}", mr_style))
    
    story.append(PageBreak())
    
    # Experiencias MR
    story.append(Paragraph("EXPERIENCIAS MR", section_style))
    
    experiencias_text = """
    Las experiencias de realidad mixta de Bioclones deben ser diversas y adaptables, permitiendo diferentes tipos de interacción entre lo real y lo virtual.
    """
    story.append(Paragraph(experiencias_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de experiencias MR
    experiencias_data = [
        ['Experiencia', 'Descripción', 'Elementos Reales', 'Elementos Virtuales'],
        ['Laboratorio Híbrido', 'Experimentos en MR', 'Mesa, objetos físicos', 'Instrumentos virtuales, datos'],
        ['Personajes Holográficos', 'Interacción con avatares', 'Espacio físico', 'Personajes 3D, diálogos'],
        ['Entornos Superpuestos', 'Mundos virtuales en espacios reales', 'Habitación, muebles', 'Paisajes, objetos virtuales'],
        ['Educación Inmersiva', 'Aprendizaje con MR', 'Libros, materiales', 'Simulaciones, visualizaciones'],
        ['Colaboración Remota', 'Trabajo en equipo híbrido', 'Espacio de trabajo', 'Avatares, herramientas virtuales'],
        ['Entretenimiento MR', 'Juegos y diversión híbrida', 'Espacio físico', 'Juegos, efectos, personajes']
    ]
    
    experiencias_table = Table(experiencias_data, colWidths=[2.5*cm, 3*cm, 2.5*cm, 3*cm])
    experiencias_table.setStyle(TableStyle([
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
    
    story.append(experiencias_table)
    story.append(PageBreak())
    
    # Tecnologías MR
    story.append(Paragraph("TECNOLOGÍAS MR", section_style))
    
    tecnologias_text = """
    Las tecnologías de realidad mixta para Bioclones deben ser de última generación, proporcionando fusión perfecta entre lo real y lo virtual.
    """
    story.append(Paragraph(tecnologias_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tecnologías Core", subtitle_style))
    tecnologias_core = [
        "SLAM avanzado para mapeo 3D",
        "Computer vision para reconocimiento",
        "Holografía volumétrica",
        "Tracking de 6DOF preciso",
        "Oclusión y sombras realistas",
        "Audio espacial 3D"
    ]
    
    for tecnologia in tecnologias_core:
        story.append(Paragraph(f"• {tecnologia}", mr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Dispositivos MR", subtitle_style))
    dispositivos = [
        "Microsoft HoloLens 2 para enterprise",
        "Magic Leap 2 para desarrollo",
        "Apple Vision Pro para consumo",
        "Meta Quest Pro para VR/MR híbrida",
        "Varjo Aero para alta fidelidad",
        "Nreal Air para MR ligera"
    ]
    
    for dispositivo in dispositivos:
        story.append(Paragraph(f"• {dispositivo}", mr_style))
    
    story.append(PageBreak())
    
    # Interacciones MR
    story.append(Paragraph("INTERACCIONES MR", section_style))
    
    interacciones_text = """
    Las interacciones en realidad mixta de Bioclones deben ser naturales e intuitivas, aprovechando las capacidades únicas de la fusión real-virtual.
    """
    story.append(Paragraph(interacciones_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tipos de Interacciones", subtitle_style))
    tipos_interacciones = [
        "Manipulación de objetos híbridos",
        "Interacción con hologramas",
        "Colaboración en tiempo real",
        "Navegación espacial híbrida",
        "Creación de contenido MR",
        "Comunicación con avatares"
    ]
    
    for tipo in tipos_interacciones:
        story.append(Paragraph(f"• {tipo}", mr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Controles y Navegación", subtitle_style))
    controles = [
        "Gestos naturales para control",
        "Comandos de voz para acciones",
        "Mirada para selección",
        "Movimiento corporal para navegación",
        "Toque virtual en objetos",
        "Interfaz holográfica flotante"
    ]
    
    for control in controles:
        story.append(Paragraph(f"• {control}", mr_style))
    
    story.append(PageBreak())
    
    # Aplicaciones específicas
    story.append(Paragraph("APLICACIONES ESPECÍFICAS", section_style))
    
    aplicaciones_text = """
    Las aplicaciones específicas de realidad mixta en Bioclones deben ser prácticas y útiles para diferentes tipos de usuarios y casos de uso.
    """
    story.append(Paragraph(aplicaciones_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Para Lectores", subtitle_style))
    para_lectores = [
        "Lectura inmersiva con elementos 3D",
        "Visualización de conceptos científicos",
        "Interacción con personajes virtuales",
        "Exploración de entornos de la historia",
        "Análisis visual de temas complejos",
        "Experiencias educativas inmersivas"
    ]
    
    for aplicacion in para_lectores:
        story.append(Paragraph(f"• {aplicacion}", mr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Para Educadores", subtitle_style))
    para_educadores = [
        "Enseñanza con visualizaciones 3D",
        "Simulaciones de experimentos",
        "Colaboración en tiempo real",
        "Análisis visual de literatura",
        "Creación de contenido educativo",
        "Evaluación inmersiva"
    ]
    
    for aplicacion in para_educadores:
        story.append(Paragraph(f"• {aplicacion}", mr_style))
    
    story.append(PageBreak())
    
    # Desarrollo y distribución
    story.append(Paragraph("DESARROLLO Y DISTRIBUCIÓN", section_style))
    
    desarrollo_text = """
    El desarrollo y distribución de la experiencia MR de Bioclones debe seguir las mejores prácticas de la industria y aprovechar las plataformas especializadas.
    """
    story.append(Paragraph(desarrollo_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Proceso de Desarrollo", subtitle_style))
    proceso = [
        "Diseño de experiencia híbrida",
        "Prototipado con herramientas MR",
        "Testing en dispositivos reales",
        "Optimización de rendimiento",
        "Integración con sistemas existentes",
        "Lanzamiento gradual y feedback"
    ]
    
    for paso in proceso:
        story.append(Paragraph(f"• {paso}", mr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Canales de Distribución", subtitle_style))
    canales = [
        "Microsoft Store para HoloLens",
        "Magic Leap World para ML2",
        "App Store para Vision Pro",
        "Meta Store para Quest Pro",
        "Steam VR para PC MR",
        "Distribución directa para enterprise"
    ]
    
    for canal in canales:
        story.append(Paragraph(f"• {canal}", mr_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de realidad mixta generado automáticamente —<br/>
    <br/>
    <b>Experiencia MR híbrida</b><br/>
    <i>Bioclones en realidad mixta</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Realidad Mixta Digital Automática
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
    print("Sistema de realidad mixta creado exitosamente: sistema_realidad_mixta_bioclones.pdf")

if __name__ == "__main__":
    create_mixed_reality_system()



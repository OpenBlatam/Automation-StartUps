#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_metaverse_system():
    """Genera un sistema de metaverso para Bioclones"""
    
    # Configuración del documento de metaverso
    doc = SimpleDocTemplate(
        "sistema_metaverso_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Metaverso - Bioclones",
        author="Sistema de Metaverso Automático",
        subject="Ciencia Ficción - Metaverso - Realidad Virtual Avanzada",
        creator="Sistema de Metaverso Digital",
        keywords="metaverso, realidad virtual, ciencia ficción, bioclones, mundo virtual"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores metaverso
    primary_color = HexColor('#1e40af')      # Azul metaverso
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de metaverso
    title_style = ParagraphStyle(
        'MetaverseTitle',
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
        'MetaverseSubtitle',
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
        'MetaverseSection',
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
        'MetaverseBody',
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
    
    metaverse_style = ParagraphStyle(
        'MetaverseStyle',
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
    
    # Portada de metaverso
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("🌐 SISTEMA DE METAVERSO", title_style))
    story.append(Paragraph("Bioclones - Mundo Virtual Completo", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Metaverso Automático</b><br/>
    <br/>
    <i>Bioclones en un mundo virtual completo</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción en el metaverso</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: Metaverso | Plataforma: Multiplataforma | Experiencia: Inmersiva Total
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Arquitectura del metaverso
    story.append(Paragraph("ARQUITECTURA DEL METAVERSO", section_style))
    
    arquitectura_text = """
    El metaverso de Bioclones debe ser un mundo virtual completo donde los usuarios pueden vivir, trabajar, socializar y experimentar la historia de manera inmersiva y persistente.
    """
    story.append(Paragraph(arquitectura_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Componentes del Metaverso", subtitle_style))
    componentes = [
        "Mundo virtual persistente 24/7",
        "Avatares personalizables y únicos",
        "Economía virtual con tokens y NFT",
        "Sistema de propiedad digital",
        "Comunidad social integrada",
        "Eventos y actividades en tiempo real"
    ]
    
    for componente in componentes:
        story.append(Paragraph(f"• {componente}", metaverse_style))
    
    story.append(PageBreak())
    
    # Mundos virtuales
    story.append(Paragraph("MUNDOS VIRTUALES", section_style))
    
    mundos_text = """
    El metaverso de Bioclones debe incluir múltiples mundos virtuales interconectados, cada uno representando diferentes aspectos de la historia y la ciencia ficción.
    """
    story.append(Paragraph(mundos_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de mundos virtuales
    mundos_data = [
        ['Mundo', 'Descripción', 'Actividades', 'Tecnología'],
        ['Complejo Biológico', 'Laboratorio principal', 'Experimentos, investigación', 'VR/AR avanzada'],
        ['Ciudad Espacial', 'Estación orbital', 'Exploración, comercio', 'Simulación física'],
        ['Mundo Paralelo', 'Realidad alternativa', 'Aventuras, descubrimientos', 'IA generativa'],
        ['Universo Cuántico', 'Dimensión subatómica', 'Física cuántica, viajes', 'Computación cuántica'],
        ['Metaverso Social', 'Espacio comunitario', 'Eventos, networking', 'Blockchain social'],
        ['Mundo Educativo', 'Centro de aprendizaje', 'Cursos, talleres', 'Realidad mixta']
    ]
    
    mundos_table = Table(mundos_data, colWidths=[2.5*cm, 3*cm, 3*cm, 3.5*cm])
    mundos_table.setStyle(TableStyle([
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
    
    story.append(mundos_table)
    story.append(PageBreak())
    
    # Economía virtual
    story.append(Paragraph("ECONOMÍA VIRTUAL", section_style))
    
    economia_text = """
    La economía virtual del metaverso de Bioclones debe ser robusta y sostenible, permitiendo a los usuarios crear, intercambiar y monetizar activos digitales.
    """
    story.append(Paragraph(economia_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Sistema Económico", subtitle_style))
    sistema_economico = [
        "Token nativo BIO para transacciones",
        "NFTs únicos de personajes y objetos",
        "Sistema de tierras virtuales",
        "Mercado descentralizado de activos",
        "Sistema de recompensas por participación",
        "Economía de creadores y desarrolladores"
    ]
    
    for elemento in sistema_economico:
        story.append(Paragraph(f"• {elemento}", metaverse_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Monetización", subtitle_style))
    monetizacion = [
        "Venta de tierras virtuales",
        "Comisiones por transacciones",
        "Suscripciones premium",
        "Eventos y experiencias pagadas",
        "Publicidad inmersiva",
        "Licencias de contenido"
    ]
    
    for metodo in monetizacion:
        story.append(Paragraph(f"• {metodo}", metaverse_style))
    
    story.append(PageBreak())
    
    # Tecnologías del metaverso
    story.append(Paragraph("TECNOLOGÍAS DEL METAVERSO", section_style))
    
    tecnologias_text = """
    Las tecnologías del metaverso de Bioclones deben ser de vanguardia, proporcionando una experiencia inmersiva, fluida y escalable.
    """
    story.append(Paragraph(tecnologias_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tecnologías Core", subtitle_style))
    tecnologias_core = [
        "Realidad Virtual (VR) de alta fidelidad",
        "Realidad Aumentada (AR) integrada",
        "Inteligencia Artificial generativa",
        "Blockchain para propiedad digital",
        "Computación en la nube distribuida",
        "Redes 5G/6G para baja latencia"
    ]
    
    for tecnologia in tecnologias_core:
        story.append(Paragraph(f"• {tecnologia}", metaverse_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Plataformas Soportadas", subtitle_style))
    plataformas = [
        "Meta Quest Pro para VR premium",
        "Apple Vision Pro para AR avanzada",
        "PlayStation VR2 para gaming",
        "WebXR para acceso universal",
        "Mobile AR para smartphones",
        "Desktop para experiencias inmersivas"
    ]
    
    for plataforma in plataformas:
        story.append(Paragraph(f"• {plataforma}", metaverse_style))
    
    story.append(PageBreak())
    
    # Experiencias sociales
    story.append(Paragraph("EXPERIENCIAS SOCIALES", section_style))
    
    sociales_text = """
    Las experiencias sociales del metaverso de Bioclones deben fomentar la comunidad, la colaboración y la creatividad entre los usuarios.
    """
    story.append(Paragraph(sociales_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Actividades Sociales", subtitle_style))
    actividades = [
        "Eventos en vivo y presentaciones",
        "Clubes de lectura virtuales",
        "Talleres de escritura creativa",
        "Conferencias de ciencia ficción",
        "Competiciones y juegos",
        "Networking profesional"
    ]
    
    for actividad in actividades:
        story.append(Paragraph(f"• {actividad}", metaverse_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Herramientas de Comunicación", subtitle_style))
    herramientas = [
        "Chat de voz espacial 3D",
        "Gestos y expresiones de avatar",
        "Sistema de mensajería persistente",
        "Streaming de contenido en vivo",
        "Colaboración en tiempo real",
        "Traducción automática de idiomas"
    ]
    
    for herramienta in herramientas:
        story.append(Paragraph(f"• {herramienta}", metaverse_style))
    
    story.append(PageBreak())
    
    # Desarrollo y creación
    story.append(Paragraph("DESARROLLO Y CREACIÓN", section_style))
    
    desarrollo_text = """
    El metaverso de Bioclones debe incluir herramientas de creación que permitan a los usuarios desarrollar contenido, experiencias y mundos virtuales.
    """
    story.append(Paragraph(desarrollo_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Herramientas de Creación", subtitle_style))
    herramientas_creacion = [
        "Editor de mundos virtuales",
        "Constructor de avatares avanzado",
        "Sistema de scripting visual",
        "Biblioteca de assets 3D",
        "Herramientas de animación",
        "Sistema de física realista"
    ]
    
    for herramienta in herramientas_creacion:
        story.append(Paragraph(f"• {herramienta}", metaverse_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Programa de Desarrolladores", subtitle_style))
    programa_dev = [
        "SDK completo para desarrolladores",
        "Documentación técnica exhaustiva",
        "Sistema de monetización para creadores",
        "Herramientas de analytics y métricas",
        "Comunidad de desarrolladores",
        "Programa de incentivos y recompensas"
    ]
    
    for elemento in programa_dev:
        story.append(Paragraph(f"• {elemento}", metaverse_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de metaverso generado automáticamente —<br/>
    <br/>
    <b>Mundo virtual completo</b><br/>
    <i>Bioclones en el metaverso</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Metaverso Digital Automático
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
    print("Sistema de metaverso creado exitosamente: sistema_metaverso_bioclones.pdf")

if __name__ == "__main__":
    create_metaverse_system()




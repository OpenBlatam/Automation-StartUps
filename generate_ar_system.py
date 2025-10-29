#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_ar_system():
    """Genera un sistema de realidad aumentada para Bioclones"""
    
    # Configuración del documento de AR
    doc = SimpleDocTemplate(
        "sistema_ar_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Realidad Aumentada - Bioclones",
        author="Sistema de AR Automático",
        subject="Ciencia Ficción - Realidad Aumentada - AR/XR",
        creator="Sistema de AR Digital",
        keywords="realidad aumentada, AR, XR, ciencia ficción, bioclones, realidad mixta"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores AR
    primary_color = HexColor('#1e40af')      # Azul AR
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de AR
    title_style = ParagraphStyle(
        'ARTitle',
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
        'ARSubtitle',
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
        'ARSection',
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
        'ARBody',
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
    
    ar_style = ParagraphStyle(
        'ARStyle',
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
    
    # Portada de AR
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("📱 SISTEMA DE REALIDAD AUMENTADA", title_style))
    story.append(Paragraph("Bioclones - Experiencia AR Inmersiva", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Realidad Aumentada Automático</b><br/>
    <br/>
    <i>Bioclones en realidad aumentada</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción en AR</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: AR/XR | Plataforma: Multiplataforma | Experiencia: Realidad Mixta
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Estrategia de AR
    story.append(Paragraph("ESTRATEGIA DE REALIDAD AUMENTADA", section_style))
    
    estrategia_text = """
    La implementación de realidad aumentada para Bioclones debe crear una experiencia inmersiva que superponga elementos digitales sobre el mundo real, permitiendo a los usuarios interactuar con la historia de manera natural.
    """
    story.append(Paragraph(estrategia_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Objetivos de AR", subtitle_style))
    objetivos = [
        "Superponer elementos de Bioclones en el mundo real",
        "Crear interacciones naturales con personajes virtuales",
        "Visualizar conceptos científicos de forma inmersiva",
        "Permitir exploración de entornos virtuales",
        "Facilitar aprendizaje interactivo",
        "Crear experiencias sociales compartidas"
    ]
    
    for objetivo in objetivos:
        story.append(Paragraph(f"• {objetivo}", ar_style))
    
    story.append(PageBreak())
    
    # Tecnologías AR
    story.append(Paragraph("TECNOLOGÍAS AR", section_style))
    
    tecnologias_text = """
    Las tecnologías de realidad aumentada para Bioclones deben ser de última generación, proporcionando tracking preciso, renderizado de alta calidad y interacciones naturales.
    """
    story.append(Paragraph(tecnologias_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de tecnologías AR
    tecnologias_data = [
        ['Tecnología', 'Función', 'Precisión', 'Aplicación'],
        ['SLAM', 'Mapeo y localización', 'Milimétrica', 'Tracking espacial'],
        ['Computer Vision', 'Reconocimiento visual', 'Subpixel', 'Detección de objetos'],
        ['Machine Learning', 'Análisis inteligente', '99%+', 'Clasificación automática'],
        ['Spatial Audio', 'Sonido 3D', 'Direccional', 'Audio inmersivo'],
        ['Haptic Feedback', 'Retroalimentación táctil', 'Precisa', 'Interacción física'],
        ['Cloud Computing', 'Procesamiento remoto', 'Alta', 'Renderizado complejo']
    ]
    
    tecnologias_table = Table(tecnologias_data, colWidths=[2.5*cm, 3*cm, 2*cm, 3.5*cm])
    tecnologias_table.setStyle(TableStyle([
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
    
    story.append(tecnologias_table)
    story.append(PageBreak())
    
    # Experiencias AR
    story.append(Paragraph("EXPERIENCIAS AR", section_style))
    
    experiencias_text = """
    Las experiencias de realidad aumentada de Bioclones deben ser diversas y adaptables, permitiendo diferentes tipos de interacción según el contexto y las preferencias del usuario.
    """
    story.append(Paragraph(experiencias_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tipos de Experiencias", subtitle_style))
    tipos_experiencias = [
        "Lectura AR: Superposición de anotaciones y comentarios",
        "Personajes AR: Avatares virtuales en el espacio real",
        "Entornos AR: Recreación de espacios de la historia",
        "Educación AR: Visualización de conceptos científicos",
        "Social AR: Experiencias compartidas con otros usuarios",
        "Gaming AR: Juegos basados en la historia"
    ]
    
    for tipo in tipos_experiencias:
        story.append(Paragraph(f"• {tipo}", ar_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Interacciones AR", subtitle_style))
    interacciones = [
        "Gestos naturales para control",
        "Comandos de voz para navegación",
        "Toque virtual en objetos 3D",
        "Movimiento corporal para exploración",
        "Mirada para selección de elementos",
        "Proximidad para activación automática"
    ]
    
    for interaccion in interacciones:
        story.append(Paragraph(f"• {interaccion}", ar_style))
    
    story.append(PageBreak())
    
    # Plataformas AR
    story.append(Paragraph("PLATAFORMAS AR", section_style))
    
    plataformas_text = """
    Las plataformas de realidad aumentada para Bioclones deben ser compatibles con múltiples dispositivos y sistemas operativos para maximizar el alcance.
    """
    story.append(Paragraph(plataformas_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Dispositivos Soportados", subtitle_style))
    dispositivos = [
        "Apple Vision Pro para experiencias premium",
        "Meta Quest 3 para VR/AR híbrida",
        "Microsoft HoloLens 2 para enterprise",
        "Magic Leap 2 para desarrollo profesional",
        "Smartphones con ARCore/ARKit",
        "Tablets para experiencias educativas"
    ]
    
    for dispositivo in dispositivos:
        story.append(Paragraph(f"• {dispositivo}", ar_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Sistemas Operativos", subtitle_style))
    sistemas = [
        "iOS con ARKit para dispositivos Apple",
        "Android con ARCore para dispositivos Google",
        "Windows Mixed Reality para PC",
        "WebXR para acceso universal",
        "Unity AR Foundation para multiplataforma",
        "Unreal Engine para experiencias premium"
    ]
    
    for sistema in sistemas:
        story.append(Paragraph(f"• {sistema}", ar_style))
    
    story.append(PageBreak())
    
    # Contenido AR
    story.append(Paragraph("CONTENIDO AR", section_style))
    
    contenido_text = """
    El contenido de realidad aumentada para Bioclones debe ser rico, interactivo y educativo, aprovechando las capacidades únicas de la tecnología AR.
    """
    story.append(Paragraph(contenido_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Elementos Visuales", subtitle_style))
    elementos_visuales = [
        "Modelos 3D de personajes y objetos",
        "Animaciones de procesos científicos",
        "Hologramas de información contextual",
        "Efectos visuales de ciencia ficción",
        "Interfaces de usuario inmersivas",
        "Visualizaciones de datos complejos"
    ]
    
    for elemento in elementos_visuales:
        story.append(Paragraph(f"• {elemento}", ar_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Contenido Interactivo", subtitle_style))
    contenido_interactivo = [
        "Simulaciones de experimentos científicos",
        "Juegos de rol basados en la historia",
        "Quizzes interactivos sobre el contenido",
        "Tours virtuales de entornos",
        "Colaboración en tiempo real",
        "Creación de contenido personalizado"
    ]
    
    for contenido in contenido_interactivo:
        story.append(Paragraph(f"• {contenido}", ar_style))
    
    story.append(PageBreak())
    
    # Desarrollo y distribución
    story.append(Paragraph("DESARROLLO Y DISTRIBUCIÓN", section_style))
    
    desarrollo_text = """
    El desarrollo y distribución de la experiencia AR de Bioclones debe seguir las mejores prácticas de la industria y aprovechar las plataformas especializadas.
    """
    story.append(Paragraph(desarrollo_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Proceso de Desarrollo", subtitle_style))
    proceso = [
        "Diseño de experiencia centrado en el usuario",
        "Prototipado rápido con herramientas AR",
        "Testing en dispositivos reales",
        "Optimización de rendimiento",
        "Integración con sistemas existentes",
        "Lanzamiento gradual y feedback"
    ]
    
    for paso in proceso:
        story.append(Paragraph(f"• {paso}", ar_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Canales de Distribución", subtitle_style))
    canales = [
        "App Store para iOS",
        "Google Play para Android",
        "Microsoft Store para Windows",
        "Oculus Store para Meta",
        "WebXR para navegadores",
        "Distribución directa para enterprise"
    ]
    
    for canal in canales:
        story.append(Paragraph(f"• {canal}", ar_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de realidad aumentada generado automáticamente —<br/>
    <br/>
    <b>Experiencia AR inmersiva</b><br/>
    <i>Bioclones en realidad aumentada</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Realidad Aumentada Digital Automática
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
    print("Sistema de realidad aumentada creado exitosamente: sistema_ar_bioclones.pdf")

if __name__ == "__main__":
    create_ar_system()



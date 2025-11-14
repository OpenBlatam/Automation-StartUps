#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_vr_system():
    """Genera un sistema de realidad virtual para Bioclones"""
    
    # Configuración del documento de VR
    doc = SimpleDocTemplate(
        "sistema_vr_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Realidad Virtual - Bioclones",
        author="Sistema de VR Automático",
        subject="Ciencia Ficción - Realidad Virtual - VR/XR",
        creator="Sistema de VR Digital",
        keywords="realidad virtual, vr, xr, ciencia ficción, bioclones, inmersión"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores VR
    primary_color = HexColor('#1e40af')      # Azul VR
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de VR
    title_style = ParagraphStyle(
        'VRTitle',
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
        'VRSubtitle',
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
        'VRSection',
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
        'VRBody',
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
    
    vr_style = ParagraphStyle(
        'VRStyle',
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
    
    # Portada de VR
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("🥽 SISTEMA DE REALIDAD VIRTUAL", title_style))
    story.append(Paragraph("Bioclones - Experiencia VR Inmersiva", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Realidad Virtual Automático</b><br/>
    <br/>
    <i>Bioclones en realidad virtual</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción en VR</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: VR/XR | Plataforma: Multiplataforma | Experiencia: Inmersiva Total
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Arquitectura VR
    story.append(Paragraph("ARQUITECTURA VR", section_style))
    
    arquitectura_text = """
    El sistema de realidad virtual para Bioclones debe proporcionar una experiencia inmersiva completa, permitiendo a los usuarios explorar, interactuar y vivir la historia en un entorno virtual.
    """
    story.append(Paragraph(arquitectura_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Componentes del Sistema VR", subtitle_style))
    componentes = [
        "Motor de renderizado 3D de alta fidelidad",
        "Sistema de tracking de movimiento",
        "Audio espacial 3D",
        "Física realista del mundo virtual",
        "Sistema de interacción natural",
        "Redes de baja latencia para multijugador"
    ]
    
    for componente in componentes:
        story.append(Paragraph(f"• {componente}", vr_style))
    
    story.append(PageBreak())
    
    # Entornos virtuales
    story.append(Paragraph("ENTORNOS VIRTUALES", section_style))
    
    entornos_text = """
    Los entornos virtuales de Bioclones deben recrear fielmente los espacios de la historia, desde el Complejo Biológico hasta los mundos paralelos.
    """
    story.append(Paragraph(entornos_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de entornos virtuales
    entornos_data = [
        ['Entorno', 'Descripción', 'Características', 'Interacciones'],
        ['Complejo Biológico', 'Laboratorio principal', 'Equipos científicos, experimentos', 'Manipulación de objetos, experimentos'],
        ['Ciudad Espacial', 'Estación orbital', 'Gravitación cero, vistas espaciales', 'Flotación, exploración espacial'],
        ['Mundo Paralelo', 'Realidad alternativa', 'Física alterada, dimensiones extrañas', 'Viajes dimensionales, física cuántica'],
        ['Universo Cuántico', 'Dimensión subatómica', 'Partículas, ondas, probabilidades', 'Manipulación cuántica, observación'],
        ['Metaverso Social', 'Espacio comunitario', 'Avatares, eventos, networking', 'Socialización, colaboración'],
        ['Mundo Educativo', 'Centro de aprendizaje', 'Simulaciones, laboratorios virtuales', 'Experimentos, aprendizaje interactivo']
    ]
    
    entornos_table = Table(entornos_data, colWidths=[2.5*cm, 3*cm, 3*cm, 3.5*cm])
    entornos_table.setStyle(TableStyle([
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
    
    story.append(entornos_table)
    story.append(PageBreak())
    
    # Interacciones VR
    story.append(Paragraph("INTERACCIONES VR", section_style))
    
    interacciones_text = """
    Las interacciones en VR de Bioclones deben ser naturales e intuitivas, aprovechando las capacidades únicas de la realidad virtual.
    """
    story.append(Paragraph(interacciones_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tipos de Interacciones", subtitle_style))
    tipos_interacciones = [
        "Manipulación directa de objetos 3D",
        "Navegación por teleportación y movimiento",
        "Interacción con personajes virtuales",
        "Manipulación de interfaces holográficas",
        "Colaboración en tiempo real con otros usuarios",
        "Creación y modificación de contenido"
    ]
    
    for tipo in tipos_interacciones:
        story.append(Paragraph(f"• {tipo}", vr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Controles y Navegación", subtitle_style))
    controles = [
        "Controladores VR para manipulación precisa",
        "Tracking de manos para gestos naturales",
        "Navegación por teleportación",
        "Sistema de locomoción natural",
        "Comandos de voz para acciones",
        "Interfaz de usuario inmersiva"
    ]
    
    for control in controles:
        story.append(Paragraph(f"• {control}", vr_style))
    
    story.append(PageBreak())
    
    # Hardware VR
    story.append(Paragraph("HARDWARE VR", section_style))
    
    hardware_text = """
    El hardware de realidad virtual para Bioclones debe ser de última generación, proporcionando la mejor experiencia inmersiva posible.
    """
    story.append(Paragraph(hardware_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Dispositivos VR Soportados", subtitle_style))
    dispositivos = [
        "Meta Quest 3 para VR standalone",
        "PlayStation VR2 para gaming",
        "HTC Vive Pro 2 para VR premium",
        "Valve Index para alta fidelidad",
        "Pico 4 para VR empresarial",
        "Apple Vision Pro para AR/VR híbrida"
    ]
    
    for dispositivo in dispositivos:
        story.append(Paragraph(f"• {dispositivo}", vr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Especificaciones Técnicas", subtitle_style))
    especificaciones = [
        "Resolución: 4K por ojo (2160x2160)",
        "Frecuencia de actualización: 120Hz",
        "Campo de visión: 110° horizontal",
        "Tracking: 6DOF con precisión milimétrica",
        "Audio: Espacial 3D con cancelación de ruido",
        "Conectividad: Wi-Fi 6E, USB-C, DisplayPort"
    ]
    
    for especificacion in especificaciones:
        story.append(Paragraph(f"• {especificacion}", vr_style))
    
    story.append(PageBreak())
    
    # Contenido VR
    story.append(Paragraph("CONTENIDO VR", section_style))
    
    contenido_text = """
    El contenido de realidad virtual para Bioclones debe ser rico, interactivo y educativo, aprovechando las capacidades únicas de la tecnología VR.
    """
    story.append(Paragraph(contenido_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Experiencias VR", subtitle_style))
    experiencias = [
        "Recorridos inmersivos por la historia",
        "Simulaciones de experimentos científicos",
        "Interacciones con personajes virtuales",
        "Exploración de entornos imposibles",
        "Colaboración en tiempo real",
        "Creación de contenido personalizado"
    ]
    
    for experiencia in experiencias:
        story.append(Paragraph(f"• {experiencia}", vr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Elementos Multimedia", subtitle_style))
    elementos = [
        "Modelos 3D de alta fidelidad",
        "Animaciones fluidas y realistas",
        "Audio espacial 3D",
        "Efectos visuales avanzados",
        "Física realista del mundo virtual",
        "Iluminación dinámica y global"
    ]
    
    for elemento in elementos:
        story.append(Paragraph(f"• {elemento}", vr_style))
    
    story.append(PageBreak())
    
    # Desarrollo y distribución
    story.append(Paragraph("DESARROLLO Y DISTRIBUCIÓN", section_style))
    
    desarrollo_text = """
    El desarrollo y distribución de la experiencia VR de Bioclones debe seguir las mejores prácticas de la industria y aprovechar las plataformas especializadas.
    """
    story.append(Paragraph(desarrollo_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Proceso de Desarrollo", subtitle_style))
    proceso = [
        "Diseño de experiencia centrado en el usuario",
        "Prototipado rápido con herramientas VR",
        "Testing en dispositivos reales",
        "Optimización de rendimiento",
        "Integración con sistemas existentes",
        "Lanzamiento gradual y feedback"
    ]
    
    for paso in proceso:
        story.append(Paragraph(f"• {paso}", vr_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Canales de Distribución", subtitle_style))
    canales = [
        "Meta Quest Store para Quest",
        "PlayStation Store para PSVR2",
        "Steam VR para PC VR",
        "App Lab para desarrolladores",
        "SideQuest para contenido experimental",
        "Distribución directa para enterprise"
    ]
    
    for canal in canales:
        story.append(Paragraph(f"• {canal}", vr_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de realidad virtual generado automáticamente —<br/>
    <br/>
    <b>Experiencia VR inmersiva</b><br/>
    <i>Bioclones en realidad virtual</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Realidad Virtual Digital Automática
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
    print("Sistema de realidad virtual creado exitosamente: sistema_vr_bioclones.pdf")

if __name__ == "__main__":
    create_vr_system()
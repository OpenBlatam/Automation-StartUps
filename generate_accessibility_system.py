#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_accessibility_system():
    """Genera un sistema de accesibilidad para Bioclones"""
    
    # Configuración del documento de accesibilidad
    doc = SimpleDocTemplate(
        "sistema_accesibilidad_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de Accesibilidad - Bioclones",
        author="Sistema de Accesibilidad Automático",
        subject="Ciencia Ficción - Accesibilidad - Inclusión Digital",
        creator="Sistema de Accesibilidad Digital",
        keywords="accesibilidad, inclusión, discapacidad, ciencia ficción, bioclones"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores accesible
    primary_color = HexColor('#1e40af')      # Azul accesible
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de accesibilidad
    title_style = ParagraphStyle(
        'AccessibilityTitle',
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
        'AccessibilitySubtitle',
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
        'AccessibilitySection',
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
        'AccessibilityBody',
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
    
    accessibility_style = ParagraphStyle(
        'AccessibilityStyle',
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
    
    # Portada de accesibilidad
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("♿ SISTEMA DE ACCESIBILIDAD", title_style))
    story.append(Paragraph("Bioclones - Inclusión Digital Universal", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de Accesibilidad Automático</b><br/>
    <br/>
    <i>Bioclones accesible para todos</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción inclusiva</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Estándares: WCAG 2.1 AAA | Inclusión: Universal | Tecnología: Adaptativa
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Principios de accesibilidad
    story.append(Paragraph("PRINCIPIOS DE ACCESIBILIDAD", section_style))
    
    principios_text = """
    El sistema de accesibilidad de Bioclones se basa en los principios universales de diseño inclusivo, asegurando que la obra sea accesible para personas con diferentes tipos de discapacidades y necesidades especiales.
    """
    story.append(Paragraph(principios_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Principios Fundamentales", subtitle_style))
    principios = [
        "Perceptibilidad: La información debe ser presentada de manera que todos puedan percibirla",
        "Operabilidad: La interfaz debe ser operable por todos los usuarios",
        "Comprensibilidad: La información y el funcionamiento deben ser comprensibles",
        "Robustez: El contenido debe ser suficientemente robusto para ser interpretado por diferentes tecnologías",
        "Equidad: Todas las personas deben tener acceso igualitario al contenido",
        "Flexibilidad: El sistema debe adaptarse a diferentes necesidades y preferencias"
    ]
    
    for principio in principios:
        story.append(Paragraph(f"• {principio}", accessibility_style))
    
    story.append(PageBreak())
    
    # Tipos de discapacidad
    story.append(Paragraph("TIPOS DE DISCAPACIDAD", section_style))
    
    discapacidad_text = """
    El sistema de accesibilidad de Bioclones debe considerar las diferentes tipos de discapacidad y proporcionar soluciones específicas para cada una.
    """
    story.append(Paragraph(discapacidad_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de tipos de discapacidad
    discapacidad_data = [
        ['Tipo de Discapacidad', 'Necesidades', 'Soluciones', 'Tecnologías'],
        ['Visual', 'Lectores de pantalla, audio', 'Texto alternativo, audio', 'NVDA, JAWS, VoiceOver'],
        ['Auditiva', 'Subtítulos, texto', 'Transcripciones, texto', 'Subtítulos, transcripciones'],
        ['Motora', 'Navegación por teclado', 'Controles accesibles', 'Teclado, switches'],
        ['Cognitiva', 'Contenido claro', 'Simplificación', 'Lenguaje simple'],
        ['Neurológica', 'Diseño neurodiverso', 'Adaptación sensorial', 'Personalización'],
        ['Múltiple', 'Soluciones integradas', 'Acceso universal', 'Tecnologías combinadas']
    ]
    
    discapacidad_table = Table(discapacidad_data, colWidths=[2.5*cm, 3*cm, 3*cm, 3.5*cm])
    discapacidad_table.setStyle(TableStyle([
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
    
    story.append(discapacidad_table)
    story.append(PageBreak())
    
    # Soluciones técnicas
    story.append(Paragraph("SOLUCIONES TÉCNICAS", section_style))
    
    soluciones_text = """
    Las soluciones técnicas de accesibilidad para Bioclones incluyen múltiples formatos y tecnologías adaptativas que garantizan el acceso universal al contenido.
    """
    story.append(Paragraph(soluciones_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Formatos Accesibles", subtitle_style))
    formatos = [
        "PDF accesible con etiquetas semánticas y texto alternativo",
        "EPUB3 con características de accesibilidad avanzadas",
        "HTML semántico con estructura clara y navegable",
        "Audio con transcripciones y descripciones detalladas",
        "Braille digital para lectores de braille",
        "Formato DAISY para lectores de pantalla especializados"
    ]
    
    for formato in formatos:
        story.append(Paragraph(f"• {formato}", accessibility_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tecnologías de Asistencia", subtitle_style))
    tecnologias = [
        "Lectores de pantalla (NVDA, JAWS, VoiceOver)",
        "Software de reconocimiento de voz",
        "Dispositivos de entrada alternativos",
        "Software de amplificación de pantalla",
        "Herramientas de navegación por voz",
        "Tecnologías de síntesis de voz"
    ]
    
    for tecnologia in tecnologias:
        story.append(Paragraph(f"• {tecnologia}", accessibility_style))
    
    story.append(PageBreak())
    
    # Características de accesibilidad
    story.append(Paragraph("CARACTERÍSTICAS DE ACCESIBILIDAD", section_style))
    
    caracteristicas_text = """
    Las características de accesibilidad implementadas en Bioclones deben cumplir con los estándares internacionales y proporcionar una experiencia de usuario óptima para todas las personas.
    """
    story.append(Paragraph(caracteristicas_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Accesibilidad Visual", subtitle_style))
    visual = [
        "Contraste de color mínimo 4.5:1 para texto normal",
        "Contraste de color mínimo 3:1 para texto grande",
        "Texto alternativo para todas las imágenes",
        "Estructura semántica clara con encabezados",
        "Navegación por teclado completa",
        "Indicadores de foco visibles"
    ]
    
    for caracteristica in visual:
        story.append(Paragraph(f"• {caracteristica}", accessibility_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Accesibilidad Auditiva", subtitle_style))
    auditiva = [
        "Transcripciones completas de todo el contenido",
        "Subtítulos para contenido multimedia",
        "Indicadores visuales para sonidos importantes",
        "Texto descriptivo de elementos sonoros",
        "Opciones de audio alternativo",
        "Sincronización perfecta entre audio y texto"
    ]
    
    for caracteristica in auditiva:
        story.append(Paragraph(f"• {caracteristica}", accessibility_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Accesibilidad Motora", subtitle_style))
    motora = [
        "Navegación completa por teclado",
        "Atajos de teclado para todas las funciones",
        "Áreas de clic suficientemente grandes",
        "Tiempo suficiente para completar acciones",
        "Opciones de entrada alternativas",
        "Prevención de acciones accidentales"
    ]
    
    for caracteristica in motora:
        story.append(Paragraph(f"• {caracteristica}", accessibility_style))
    
    story.append(PageBreak())
    
    # Personalización
    story.append(Paragraph("PERSONALIZACIÓN", section_style))
    
    personalizacion_text = """
    El sistema de personalización permite a los usuarios adaptar la experiencia de lectura según sus necesidades específicas y preferencias individuales.
    """
    story.append(Paragraph(personalizacion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Opciones de Personalización", subtitle_style))
    opciones = [
        "Tamaño de fuente ajustable (12px a 24px)",
        "Tipografías accesibles (OpenDyslexic, Arial, Verdana)",
        "Colores de fondo y texto personalizables",
        "Espaciado de líneas ajustable",
        "Velocidad de lectura personalizable",
        "Opciones de audio (velocidad, tono, volumen)"
    ]
    
    for opcion in opciones:
        story.append(Paragraph(f"• {opcion}", accessibility_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Perfiles de Usuario", subtitle_style))
    perfiles = [
        "Perfil de baja visión: Contraste alto, texto grande",
        "Perfil de dislexia: Tipografía especial, espaciado amplio",
        "Perfil de TDAH: Navegación simplificada, distracciones mínimas",
        "Perfil de autismo: Colores suaves, estructura clara",
        "Perfil de discapacidad motora: Navegación por teclado",
        "Perfil personalizado: Combinación de opciones"
    ]
    
    for perfil in perfiles:
        story.append(Paragraph(f"• {perfil}", accessibility_style))
    
    story.append(PageBreak())
    
    # Testing y validación
    story.append(Paragraph("TESTING Y VALIDACIÓN", section_style))
    
    testing_text = """
    El proceso de testing y validación de accesibilidad debe incluir pruebas con usuarios reales y herramientas automatizadas para garantizar el cumplimiento de estándares.
    """
    story.append(Paragraph(testing_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Herramientas de Testing", subtitle_style))
    herramientas = [
        "WAVE (Web Accessibility Evaluation Tool)",
        "axe-core para testing automatizado",
        "Lighthouse para auditorías de accesibilidad",
        "Color Contrast Analyzer para verificar contraste",
        "Screen reader testing con NVDA, JAWS, VoiceOver",
        "Testing manual con usuarios con discapacidades"
    ]
    
    for herramienta in herramientas:
        story.append(Paragraph(f"• {herramienta}", accessibility_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Proceso de Validación", subtitle_style))
    validacion = [
        "Testing automatizado en cada versión",
        "Testing manual con usuarios reales",
        "Validación de estándares WCAG 2.1 AAA",
        "Testing de compatibilidad con tecnologías de asistencia",
        "Validación de navegación por teclado",
        "Testing de rendimiento con diferentes dispositivos"
    ]
    
    for proceso in validacion:
        story.append(Paragraph(f"• {proceso}", accessibility_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de accesibilidad generado automáticamente —<br/>
    <br/>
    <b>Inclusión digital universal</b><br/>
    <i>Bioclones accesible para todos</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Accesibilidad Digital Automática
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
    print("Sistema de accesibilidad creado exitosamente: sistema_accesibilidad_bioclones.pdf")

if __name__ == "__main__":
    create_accessibility_system()












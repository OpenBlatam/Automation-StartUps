#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_emotional_ai_system():
    """Genera un sistema de IA emocional para Bioclones"""
    
    # Configuración del documento de IA emocional
    doc = SimpleDocTemplate(
        "sistema_ia_emocional_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de IA Emocional - Bioclones",
        author="Sistema de IA Emocional Automático",
        subject="Ciencia Ficción - IA Emocional - Emociones - Empatía",
        creator="Sistema de IA Emocional Digital",
        keywords="ia emocional, emociones, empatía, ciencia ficción, bioclones, inteligencia emocional"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores IA emocional
    primary_color = HexColor('#1e40af')      # Azul emocional
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de IA emocional
    title_style = ParagraphStyle(
        'EmotionalAITitle',
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
        'EmotionalAISubtitle',
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
        'EmotionalAISection',
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
        'EmotionalAIBody',
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
    
    emotional_style = ParagraphStyle(
        'EmotionalAIStyle',
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
    
    # Portada de IA emocional
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("💝 SISTEMA DE IA EMOCIONAL", title_style))
    story.append(Paragraph("Bioclones - Inteligencia Emocional Artificial", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de IA Emocional Automático</b><br/>
    <br/>
    <i>Bioclones con inteligencia emocional</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción con IA emocional</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: IA Emocional | Empatía: Avanzada | Emociones: Reales
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Fundamentos de IA emocional
    story.append(Paragraph("FUNDAMENTOS DE IA EMOCIONAL", section_style))
    
    fundamentos_text = """
    La inteligencia artificial emocional para Bioclones debe ser capaz de reconocer, procesar, generar y responder a emociones humanas de manera natural y empática.
    """
    story.append(Paragraph(fundamentos_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Componentes de la IA Emocional", subtitle_style))
    componentes = [
        "Reconocimiento de emociones en texto y voz",
        "Generación de respuestas emocionalmente apropiadas",
        "Empatía y comprensión emocional",
        "Adaptación al estado emocional del usuario",
        "Memoria emocional y aprendizaje",
        "Expresión emocional natural"
    ]
    
    for componente in componentes:
        story.append(Paragraph(f"• {componente}", emotional_style))
    
    story.append(PageBreak())
    
    # Reconocimiento de emociones
    story.append(Paragraph("RECONOCIMIENTO DE EMOCIONES", section_style))
    
    reconocimiento_text = """
    El sistema de reconocimiento de emociones debe ser capaz de identificar y clasificar emociones complejas en múltiples modalidades y contextos.
    """
    story.append(Paragraph(reconocimiento_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de emociones
    emociones_data = [
        ['Emoción', 'Intensidad', 'Contexto', 'Expresión'],
        ['Alegría', 'Alta/Media/Baja', 'Éxito, logros', 'Sonrisa, risa, energía'],
        ['Tristeza', 'Alta/Media/Baja', 'Pérdida, fracaso', 'Llanto, melancolía, retraimiento'],
        ['Miedo', 'Alta/Media/Baja', 'Peligro, incertidumbre', 'Tensión, evitación, ansiedad'],
        ['Ira', 'Alta/Media/Baja', 'Injusticia, frustración', 'Agresividad, tensión, confrontación'],
        ['Sorpresa', 'Alta/Media/Baja', 'Eventos inesperados', 'Asombro, curiosidad, alerta'],
        ['Asco', 'Alta/Media/Baja', 'Repulsión, rechazo', 'Evitación, repulsión, náusea']
    ]
    
    emociones_table = Table(emociones_data, colWidths=[2*cm, 2*cm, 3*cm, 3*cm])
    emociones_table.setStyle(TableStyle([
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
    
    story.append(emociones_table)
    story.append(PageBreak())
    
    # Generación de respuestas emocionales
    story.append(Paragraph("GENERACIÓN DE RESPUESTAS EMOCIONALES", section_style))
    
    generacion_text = """
    El sistema debe generar respuestas emocionalmente apropiadas y empáticas, adaptándose al contexto emocional y las necesidades del usuario.
    """
    story.append(Paragraph(generacion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tipos de Respuestas Emocionales", subtitle_style))
    tipos_respuestas = [
        "Respuestas empáticas y comprensivas",
        "Consuelo y apoyo emocional",
        "Motivación y ánimo positivo",
        "Validación de sentimientos",
        "Orientación emocional",
        "Celebración de logros y éxitos"
    ]
    
    for tipo in tipos_respuestas:
        story.append(Paragraph(f"• {tipo}", emotional_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Estrategias de Respuesta", subtitle_style))
    estrategias = [
        "Escucha activa y reflexiva",
        "Preguntas abiertas y exploratorias",
        "Reflejo de emociones",
        "Normalización de sentimientos",
        "Orientación hacia soluciones",
        "Apoyo incondicional"
    ]
    
    for estrategia in estrategias:
        story.append(Paragraph(f"• {estrategia}", emotional_style))
    
    story.append(PageBreak())
    
    # Aplicaciones específicas
    story.append(Paragraph("APLICACIONES ESPECÍFICAS", section_style))
    
    aplicaciones_text = """
    Las aplicaciones de IA emocional en Bioclones deben ser específicas para diferentes tipos de usuarios y situaciones emocionales.
    """
    story.append(Paragraph(aplicaciones_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Para Lectores", subtitle_style))
    para_lectores = [
        "Comprensión emocional de la historia",
        "Apoyo emocional durante la lectura",
        "Identificación con personajes",
        "Procesamiento de emociones complejas",
        "Reflexión emocional profunda",
        "Crecimiento emocional personal"
    ]
    
    for aplicacion in para_lectores:
        story.append(Paragraph(f"• {aplicacion}", emotional_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Para Educadores", subtitle_style))
    para_educadores = [
        "Detección de necesidades emocionales",
        "Apoyo emocional a estudiantes",
        "Creación de ambientes emocionales seguros",
        "Desarrollo de inteligencia emocional",
        "Manejo de conflictos emocionales",
        "Promoción del bienestar emocional"
    ]
    
    for aplicacion in para_educadores:
        story.append(Paragraph(f"• {aplicacion}", emotional_style))
    
    story.append(PageBreak())
    
    # Tecnologías emocionales
    story.append(Paragraph("TECNOLOGÍAS EMOCIONALES", section_style))
    
    tecnologias_text = """
    Las tecnologías emocionales para Bioclones deben incluir herramientas avanzadas de procesamiento de emociones y generación de respuestas empáticas.
    """
    story.append(Paragraph(tecnologias_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Herramientas de Análisis Emocional", subtitle_style))
    herramientas = [
        "Análisis de sentimientos en tiempo real",
        "Detección de emociones en voz",
        "Análisis de expresiones faciales",
        "Procesamiento de lenguaje emocional",
        "Análisis de patrones emocionales",
        "Predicción de estados emocionales"
    ]
    
    for herramienta in herramientas:
        story.append(Paragraph(f"• {herramienta}", emotional_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Sistemas de Respuesta Emocional", subtitle_style))
    sistemas = [
        "Generación de respuestas empáticas",
        "Adaptación emocional automática",
        "Memoria emocional persistente",
        "Aprendizaje emocional continuo",
        "Personalización emocional",
        "Escalación emocional inteligente"
    ]
    
    for sistema in sistemas:
        story.append(Paragraph(f"• {sistema}", emotional_style))
    
    story.append(PageBreak())
    
    # Ética emocional
    story.append(Paragraph("ÉTICA EMOCIONAL", section_style))
    
    etica_text = """
    El uso de IA emocional en Bioclones debe seguir principios éticos sólidos, respetando la privacidad emocional y promoviendo el bienestar del usuario.
    """
    story.append(Paragraph(etica_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Principios Éticos", subtitle_style))
    principios = [
        "Respeto por la privacidad emocional",
        "Consentimiento informado para análisis emocional",
        "No manipulación emocional",
        "Promoción del bienestar emocional",
        "Transparencia en el uso de datos emocionales",
        "Accesibilidad emocional para todos"
    ]
    
    for principio in principios:
        story.append(Paragraph(f"• {principio}", emotional_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Medidas de Protección", subtitle_style))
    medidas = [
        "Encriptación de datos emocionales",
        "Anonimización de información sensible",
        "Control del usuario sobre datos emocionales",
        "Auditorías regulares de ética emocional",
        "Capacitación en uso responsable",
        "Monitoreo de impacto emocional"
    ]
    
    for medida in medidas:
        story.append(Paragraph(f"• {medida}", emotional_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de IA emocional generado automáticamente —<br/>
    <br/>
    <b>Inteligencia emocional artificial</b><br/>
    <i>Bioclones con IA emocional</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: IA Emocional Digital Automática
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
    print("Sistema de IA emocional creado exitosamente: sistema_ia_emocional_bioclones.pdf")

if __name__ == "__main__":
    create_emotional_ai_system()



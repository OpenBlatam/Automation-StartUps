#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_generative_ai_system():
    """Genera un sistema de IA generativa para Bioclones"""
    
    # Configuración del documento de IA generativa
    doc = SimpleDocTemplate(
        "sistema_ia_generativa_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Sistema de IA Generativa - Bioclones",
        author="Sistema de IA Generativa Automático",
        subject="Ciencia Ficción - IA Generativa - GPT - LLM",
        creator="Sistema de IA Generativa Digital",
        keywords="ia generativa, gpt, llm, ciencia ficción, bioclones, generación de contenido"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores IA generativa
    primary_color = HexColor('#1e40af')      # Azul IA
    secondary_color = HexColor('#dc2626')    # Rojo vibrante
    accent_color = HexColor('#f59e0b')      # Dorado
    light_gray = HexColor('#f8fafc')        # Gris claro
    text_gray = HexColor('#374151')         # Gris texto
    
    # Estilos de IA generativa
    title_style = ParagraphStyle(
        'GenerativeAITitle',
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
        'GenerativeAISubtitle',
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
        'GenerativeAISection',
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
        'GenerativeAIBody',
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
    
    ai_style = ParagraphStyle(
        'GenerativeAIStyle',
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
    
    # Portada de IA generativa
    story.append(Spacer(1, 3*inch))
    story.append(Paragraph("🤖 SISTEMA DE IA GENERATIVA", title_style))
    story.append(Paragraph("Bioclones - Inteligencia Artificial Generativa", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#374151">
    <b>Sistema de IA Generativa Automático</b><br/>
    <br/>
    <i>Bioclones potenciado por IA generativa</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una novela de ciencia ficción con IA generativa</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Tecnología: IA Generativa | Modelos: GPT/LLM | Generación: Automática
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Modelos de IA generativa
    story.append(Paragraph("MODELOS DE IA GENERATIVA", section_style))
    
    modelos_text = """
    Los modelos de IA generativa para Bioclones deben ser de última generación, capaces de generar texto, imágenes, audio y video de alta calidad.
    """
    story.append(Paragraph(modelos_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de modelos de IA
    modelos_data = [
        ['Modelo', 'Tipo', 'Capacidad', 'Aplicación'],
        ['GPT-4', 'Texto', '175B parámetros', 'Generación de contenido'],
        ['DALL-E 3', 'Imagen', '12B parámetros', 'Arte y visuales'],
        ['Whisper', 'Audio', '1.5B parámetros', 'Transcripción y síntesis'],
        ['Sora', 'Video', '3B parámetros', 'Generación de video'],
        ['Claude', 'Texto', '100B parámetros', 'Análisis y resumen'],
        ['Midjourney', 'Imagen', '5B parámetros', 'Arte generativo']
    ]
    
    modelos_table = Table(modelos_data, colWidths=[2*cm, 2*cm, 3*cm, 4*cm])
    modelos_table.setStyle(TableStyle([
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
    
    story.append(modelos_table)
    story.append(PageBreak())
    
    # Generación de contenido
    story.append(Paragraph("GENERACIÓN DE CONTENIDO", section_style))
    
    generacion_text = """
    La generación de contenido con IA para Bioclones debe ser diversa, creativa y de alta calidad, abarcando múltiples formatos y medios.
    """
    story.append(Paragraph(generacion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Tipos de Contenido Generado", subtitle_style))
    tipos_contenido = [
        "Continuaciones y secuelas de la historia",
        "Prequelas y historias de fondo",
        "Diálogos y conversaciones entre personajes",
        "Descripciones detalladas de entornos",
        "Análisis y comentarios literarios",
        "Adaptaciones a diferentes géneros"
    ]
    
    for tipo in tipos_contenido:
        story.append(Paragraph(f"• {tipo}", ai_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Formatos de Salida", subtitle_style))
    formatos = [
        "Texto narrativo en prosa",
        "Diálogos y conversaciones",
        "Poesía y versos",
        "Guiones y scripts",
        "Resúmenes y análisis",
        "Contenido multimedia"
    ]
    
    for formato in formatos:
        story.append(Paragraph(f"• {formato}", ai_style))
    
    story.append(PageBreak())
    
    # Personalización y fine-tuning
    story.append(Paragraph("PERSONALIZACIÓN Y FINE-TUNING", section_style))
    
    personalizacion_text = """
    Los modelos de IA para Bioclones deben ser personalizados y fine-tuned para mantener la coherencia, el estilo y la calidad del contenido original.
    """
    story.append(Paragraph(personalizacion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Técnicas de Fine-tuning", subtitle_style))
    tecnicas = [
        "Fine-tuning con datos de Bioclones",
        "Prompt engineering especializado",
        "Few-shot learning para ejemplos",
        "Reinforcement learning con feedback",
        "Transfer learning de modelos base",
        "Multi-task learning para versatilidad"
    ]
    
    for tecnica in tecnicas:
        story.append(Paragraph(f"• {tecnica}", ai_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Métricas de Calidad", subtitle_style))
    metricas = [
        "Coherencia con el contenido original",
        "Calidad literaria y estilística",
        "Precisión en detalles y hechos",
        "Creatividad y originalidad",
        "Fluidez y legibilidad",
        "Relevancia temática"
    ]
    
    for metrica in metricas:
        story.append(Paragraph(f"• {metrica}", ai_style))
    
    story.append(PageBreak())
    
    # Aplicaciones específicas
    story.append(Paragraph("APLICACIONES ESPECÍFICAS", section_style))
    
    aplicaciones_text = """
    Las aplicaciones específicas de IA generativa en Bioclones deben ser prácticas y útiles para diferentes tipos de usuarios y casos de uso.
    """
    story.append(Paragraph(aplicaciones_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Para Lectores", subtitle_style))
    para_lectores = [
        "Generación de resúmenes personalizados",
        "Explicaciones de conceptos complejos",
        "Preguntas y respuestas sobre la historia",
        "Análisis de personajes y temas",
        "Recomendaciones de contenido relacionado",
        "Traducción automática a otros idiomas"
    ]
    
    for aplicacion in para_lectores:
        story.append(Paragraph(f"• {aplicacion}", ai_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Para Educadores", subtitle_style))
    para_educadores = [
        "Generación de material educativo",
        "Creación de ejercicios y actividades",
        "Análisis literario automatizado",
        "Generación de preguntas de examen",
        "Recursos multimedia educativos",
        "Adaptación a diferentes niveles"
    ]
    
    for aplicacion in para_educadores:
        story.append(Paragraph(f"• {aplicacion}", ai_style))
    
    story.append(PageBreak())
    
    # Integración con otros sistemas
    story.append(Paragraph("INTEGRACIÓN CON OTROS SISTEMAS", section_style))
    
    integracion_text = """
    La IA generativa de Bioclones debe integrarse perfectamente con otros sistemas del ecosistema, incluyendo metaverso, blockchain y realidad aumentada.
    """
    story.append(Paragraph(integracion_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Integraciones Principales", subtitle_style))
    integraciones = [
        "Generación de contenido para metaverso",
        "Creación de NFTs con IA",
        "Contenido AR generado automáticamente",
        "Sistemas de recomendación inteligentes",
        "Análisis de sentimientos en tiempo real",
        "Personalización de experiencias"
    ]
    
    for integracion in integraciones:
        story.append(Paragraph(f"• {integracion}", ai_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("APIs y Servicios", subtitle_style))
    apis = [
        "API REST para generación de texto",
        "API de generación de imágenes",
        "API de síntesis de voz",
        "API de análisis de contenido",
        "API de recomendaciones",
        "API de traducción automática"
    ]
    
    for api in apis:
        story.append(Paragraph(f"• {api}", ai_style))
    
    story.append(PageBreak())
    
    # Ética y responsabilidad
    story.append(Paragraph("ÉTICA Y RESPONSABILIDAD", section_style))
    
    etica_text = """
    El uso de IA generativa en Bioclones debe seguir principios éticos sólidos, incluyendo transparencia, responsabilidad y respeto por los derechos de autor.
    """
    story.append(Paragraph(etica_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Principios Éticos", subtitle_style))
    principios = [
        "Transparencia en el uso de IA",
        "Respeto por los derechos de autor",
        "Prevención de sesgos y discriminación",
        "Protección de la privacidad",
        "Responsabilidad en el contenido generado",
        "Accesibilidad y inclusión"
    ]
    
    for principio in principios:
        story.append(Paragraph(f"• {principio}", ai_style))
    
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Medidas de Control", subtitle_style))
    medidas = [
        "Filtros de contenido inapropiado",
        "Verificación de hechos y precisión",
        "Sistema de reportes y feedback",
        "Auditorías regulares de calidad",
        "Capacitación en uso responsable",
        "Monitoreo continuo de resultados"
    ]
    
    for medida in medidas:
        story.append(Paragraph(f"• {medida}", ai_style))
    
    story.append(Spacer(1, 30))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Sistema de IA generativa generado automáticamente —<br/>
    <br/>
    <b>Inteligencia artificial generativa avanzada</b><br/>
    <i>Bioclones potenciado por IA generativa</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: IA Generativa Digital Automática
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
    print("Sistema de IA generativa creado exitosamente: sistema_ia_generativa_bioclones.pdf")

if __name__ == "__main__":
    create_generative_ai_system()













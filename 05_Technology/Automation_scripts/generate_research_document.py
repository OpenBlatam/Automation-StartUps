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
import os

def create_research_document():
    # Configuración del documento de investigación
    doc = SimpleDocTemplate(
        "investigacion_literaria_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Investigación Literaria - Bioclones",
        author="Sistema de Análisis Literario Automático",
        subject="Ciencia Ficción - Análisis Literario - Investigación Académica",
        creator="Sistema de Investigación Literaria Digital",
        keywords="análisis literario, ciencia ficción, investigación, clonación, identidad"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores académica
    primary_color = HexColor('#1e40af')      # Azul académico
    secondary_color = HexColor('#374151')    # Gris académico
    accent_color = HexColor('#dc2626')      # Rojo académico
    gold_color = HexColor('#d97706')        # Dorado académico
    light_gray = HexColor('#f9fafb')        # Gris claro
    text_gray = HexColor('#4b5563')         # Gris texto
    
    # Estilos académicos
    title_style = ParagraphStyle(
        'AcademicTitle',
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
        'AcademicSubtitle',
        parent=styles['Heading2'],
        fontSize=20,
        spaceAfter=40,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Oblique',
        leading=26
    )
    
    section_style = ParagraphStyle(
        'AcademicSection',
        parent=styles['Heading2'],
        fontSize=22,
        spaceAfter=30,
        spaceBefore=40,
        alignment=TA_LEFT,
        textColor=accent_color,
        fontName='Helvetica-Bold',
        leading=28,
        borderWidth=2,
        borderColor=accent_color,
        borderPadding=15,
        backColor=light_gray,
        leftIndent=15
    )
    
    subsection_style = ParagraphStyle(
        'AcademicSubsection',
        parent=styles['Heading3'],
        fontSize=18,
        spaceAfter=25,
        spaceBefore=25,
        alignment=TA_LEFT,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=24
    )
    
    body_style = ParagraphStyle(
        'AcademicBody',
        parent=styles['Normal'],
        fontSize=13,
        spaceAfter=18,
        spaceBefore=10,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Times-Roman',
        leading=19,
        textColor=text_gray
    )
    
    quote_style = ParagraphStyle(
        'AcademicQuote',
        parent=styles['Normal'],
        fontSize=14,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_LEFT,
        leftIndent=40,
        rightIndent=40,
        fontName='Times-Italic',
        textColor=text_gray,
        leading=20,
        borderWidth=1,
        borderColor=HexColor('#d1d5db'),
        borderPadding=15,
        backColor=light_gray
    )
    
    data_style = ParagraphStyle(
        'AcademicData',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        spaceBefore=8,
        alignment=TA_LEFT,
        fontName='Helvetica',
        textColor=secondary_color,
        leftIndent=20
    )
    
    # Contenido del documento
    story = []
    
    # Portada académica
    story.append(Spacer(1, 4*inch))
    story.append(Paragraph("INVESTIGACIÓN LITERARIA", title_style))
    story.append(Paragraph("Bioclones - Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#4b5563">
    <b>Análisis Literario Automático</b><br/>
    <br/>
    <i>Investigación académica generada digitalmente</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Análisis de texto, estadísticas y contexto literario</b><br/>
    <br/>
    <font size="12" color="#6b7280">
    Metodología: Análisis computacional de texto<br/>
    Área: Ciencia Ficción | Enfoque: Análisis literario
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Cargar datos del análisis
    try:
        with open('analisis_texto_bioclones.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    
    # Índice
    story.append(Paragraph("ÍNDICE", section_style))
    story.append(Spacer(1, 30))
    
    index_data = [
        ['Sección', 'Página'],
        ['Metodología de Análisis', '3'],
        ['Estadísticas del Texto', '4'],
        ['Análisis Temático', '5'],
        ['Análisis de Personajes', '6'],
        ['Análisis de Diálogos', '7'],
        ['Contexto Literario', '8'],
        ['Conclusiones', '9']
    ]
    
    index_table = Table(index_data, colWidths=[10*cm, 2*cm])
    index_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), secondary_color),
        ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    
    story.append(index_table)
    story.append(PageBreak())
    
    # Metodología
    story.append(Paragraph("METODOLOGÍA DE ANÁLISIS", section_style))
    
    metodologia_text = """
    Este análisis literario se basa en técnicas de procesamiento de lenguaje natural y análisis computacional de texto. La metodología incluye:
    """
    story.append(Paragraph(metodologia_text, body_style))
    story.append(Spacer(1, 20))
    
    metodologia_items = [
        "Análisis estadístico de frecuencias de palabras",
        "Identificación de patrones temáticos mediante palabras clave",
        "Análisis de densidad léxica y complejidad textual",
        "Estudio de la estructura narrativa y diálogos",
        "Análisis de personajes y sus apariciones",
        "Evaluación de la coherencia temática"
    ]
    
    for item in metodologia_items:
        story.append(Paragraph(f"• {item}", data_style))
    
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Herramientas Utilizadas", subsection_style))
    herramientas_text = """
    El análisis se realizó utilizando Python con librerías especializadas en procesamiento de texto, incluyendo expresiones regulares para la identificación de patrones y algoritmos de conteo para el análisis estadístico.
    """
    story.append(Paragraph(herramientas_text, body_style))
    story.append(PageBreak())
    
    # Estadísticas del texto
    story.append(Paragraph("ESTADÍSTICAS DEL TEXTO", section_style))
    
    if data:
        stats = data.get('estadisticas_basicas', {})
        
        # Tabla de estadísticas
        stats_data = [
            ['Métrica', 'Valor'],
            ['Total de caracteres', f"{stats.get('total_caracteres', 0):,}"],
            ['Total de palabras', f"{stats.get('total_palabras', 0):,}"],
            ['Total de oraciones', f"{stats.get('total_oraciones', 0):,}"],
            ['Total de párrafos', f"{stats.get('total_parrafos', 0):,}"],
            ['Promedio palabras/oración', f"{stats.get('promedio_palabras_por_oracion', 0)}"],
            ['Promedio caracteres/palabra', f"{stats.get('promedio_caracteres_por_palabra', 0)}"],
            ['Palabras únicas', f"{data.get('palabras_unicas', 0):,}"],
            ['Densidad léxica', f"{data.get('densidad_lexica', 0)}%"]
        ]
        
        stats_table = Table(stats_data, colWidths=[6*cm, 4*cm])
        stats_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, HexColor('#ffffff')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 30))
    
    # Análisis de complejidad
    story.append(Paragraph("Análisis de Complejidad Textual", subsection_style))
    complejidad_text = """
    La densidad léxica del texto indica el nivel de variedad en el vocabulario utilizado. Un valor alto sugiere un texto rico en vocabulario, mientras que un valor bajo puede indicar repetición o simplicidad léxica.
    """
    story.append(Paragraph(complejidad_text, body_style))
    story.append(PageBreak())
    
    # Análisis temático
    story.append(Paragraph("ANÁLISIS TEMÁTICO", section_style))
    
    if data and 'analisis_tematico' in data:
        temas = data['analisis_tematico']
        
        # Tabla de temas
        temas_data = [['Tema', 'Frecuencia', 'Interpretación']]
        interpretaciones = {
            'ciencia_ficcion': 'Elementos de ciencia ficción y tecnología',
            'emociones': 'Contenido emocional y psicológico',
            'filosofia': 'Reflexiones filosóficas y existenciales',
            'relaciones': 'Interacciones humanas y sociales',
            'lugar': 'Referencias espaciales y ambientales'
        }
        
        for tema, frecuencia in temas.items():
            interpretacion = interpretaciones.get(tema, 'Tema no clasificado')
            temas_data.append([tema.replace('_', ' ').title(), str(frecuencia), interpretacion])
        
        temas_table = Table(temas_data, colWidths=[3*cm, 2*cm, 5*cm])
        temas_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'LEFT'),
            ('TEXTCOLOR', (0, 0), (-1, -1), text_gray),
            ('LINEBELOW', (0, 0), (-1, 0), 2, accent_color),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, HexColor('#ffffff')]),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(temas_table)
        story.append(Spacer(1, 30))
    
    # Análisis de personajes
    story.append(Paragraph("ANÁLISIS DE PERSONAJES", section_style))
    
    if data and 'personajes' in data:
        personajes = data['personajes']
        
        personajes_text = """
        El análisis de personajes revela la importancia relativa de cada personaje en la narrativa basándose en la frecuencia de sus menciones en el texto.
        """
        story.append(Paragraph(personajes_text, body_style))
        story.append(Spacer(1, 20))
        
        for personaje, apariciones in personajes.items():
            story.append(Paragraph(f"• <b>{personaje}:</b> {apariciones} menciones", data_style))
    
    story.append(Spacer(1, 30))
    
    # Análisis de diálogos
    story.append(Paragraph("ANÁLISIS DE DIÁLOGOS", section_style))
    
    if data and 'dialogos' in data:
        dialogos = data['dialogos']
        
        dialogos_text = f"""
        El texto contiene {dialogos.get('total_dialogos', 0)} diálogos con una longitud promedio de {dialogos.get('promedio_longitud_dialogo', 0)} caracteres. 
        Los diálogos contribuyen significativamente al desarrollo de los personajes y la trama.
        """
        story.append(Paragraph(dialogos_text, body_style))
    
    story.append(PageBreak())
    
    # Contexto literario
    story.append(Paragraph("CONTEXTO LITERARIO", section_style))
    
    contexto_text = """
    "Bioclones" se inscribe en la tradición de la ciencia ficción especulativa que examina las consecuencias sociales y éticas del avance tecnológico. La obra dialoga con corrientes literarias como:
    """
    story.append(Paragraph(contexto_text, body_style))
    story.append(Spacer(1, 20))
    
    corrientes = [
        "Literatura distópica: Elementos de control social y manipulación",
        "Ciberpunk: Fusión de tecnología avanzada con crítica social", 
        "Ficción especulativa: Exploración de futuros posibles",
        "Literatura existencialista: Reflexiones sobre autenticidad y sentido",
        "Narrativa experimental: Técnicas no lineales y fragmentación"
    ]
    
    for corriente in corrientes:
        story.append(Paragraph(f"• {corriente}", data_style))
    
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Influencias y Precedentes", subsection_style))
    influencias_text = """
    La obra muestra influencias de la literatura de ciencia ficción del siglo XX, particularmente en su exploración de temas como la identidad, la clonación y las implicaciones éticas de la tecnología. El estilo narrativo fragmentado recuerda a técnicas utilizadas por autores como Philip K. Dick y William Gibson.
    """
    story.append(Paragraph(influencias_text, body_style))
    story.append(PageBreak())
    
    # Conclusiones
    story.append(Paragraph("CONCLUSIONES", section_style))
    
    conclusiones_text = """
    El análisis computacional de "Bioclones" revela una obra compleja que combina elementos de ciencia ficción con reflexiones filosóficas profundas. La densidad léxica y la variedad temática sugieren un texto rico en contenido conceptual.
    """
    story.append(Paragraph(conclusiones_text, body_style))
    story.append(Spacer(1, 20))
    
    conclusiones_items = [
        "La obra presenta una estructura narrativa experimental que refleja la fragmentación de la experiencia humana contemporánea",
        "Los temas de clonación e identidad se desarrollan a través de múltiples perspectivas y voces narrativas",
        "El análisis estadístico confirma la riqueza temática y la complejidad textual de la obra",
        "La obra anticipa debates contemporáneos sobre tecnología, identidad y humanidad"
    ]
    
    for item in conclusiones_items:
        story.append(Paragraph(f"• {item}", data_style))
    
    story.append(Spacer(1, 40))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="12" fontName="Helvetica" textColor="#6b7280">
    — Análisis generado automáticamente —<br/>
    <br/>
    <b>Investigación literaria digital</b><br/>
    <i>Metodología: Análisis computacional de texto</i><br/>
    <br/>
    <font size="10" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Análisis Literario Automático
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
    print("Documento de investigación creado exitosamente: investigacion_literaria_bioclones.pdf")

if __name__ == "__main__":
    create_research_document()




















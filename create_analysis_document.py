#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor, black, white
import os
from datetime import datetime

def create_analysis_document():
    # Crear documento de análisis
    doc = SimpleDocTemplate(
        "analisis_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=2.5*cm, 
        bottomMargin=2*cm
    )
    
    styles = getSampleStyleSheet()
    
    # Estilos para análisis
    title_style = ParagraphStyle(
        'AnalysisTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=HexColor('#1a365d'),
        fontName='Helvetica-Bold'
    )
    
    section_style = ParagraphStyle(
        'AnalysisSection',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        spaceBefore=25,
        alignment=TA_LEFT,
        textColor=HexColor('#c53030'),
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'AnalysisBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15,
        alignment=TA_JUSTIFY,
        fontName='Times-Roman',
        leading=16
    )
    
    list_style = ParagraphStyle(
        'AnalysisList',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leftIndent=20
    )
    
    story = []
    
    # Título
    story.append(Paragraph("ANÁLISIS LITERARIO", title_style))
    story.append(Paragraph("Bioclones - Una Novela", title_style))
    story.append(Spacer(1, 30))
    
    # Resumen ejecutivo
    story.append(Paragraph("RESUMEN EJECUTIVO", section_style))
    
    resumen_text = """
    "Bioclones" es una novela de ciencia ficción que explora temas de clonación, identidad humana y las implicaciones éticas de la manipulación genética. La obra presenta una narrativa fragmentada que combina elementos de thriller científico con reflexiones filosóficas sobre la naturaleza de la humanidad.
    """
    story.append(Paragraph(resumen_text, body_style))
    story.append(Spacer(1, 20))
    
    # Análisis de estructura
    story.append(Paragraph("ANÁLISIS DE ESTRUCTURA", section_style))
    
    estructura_text = """
    La novela presenta una estructura no lineal con múltiples voces narrativas. Los capítulos alternan entre diferentes perspectivas temporales y espaciales, creando un efecto de collage que refleja la fragmentación de la identidad en un mundo post-humano.
    """
    story.append(Paragraph(estructura_text, body_style))
    story.append(Spacer(1, 20))
    
    # Temas principales
    story.append(Paragraph("TEMAS PRINCIPALES", section_style))
    
    temas_data = [
        ['Tema', 'Descripción'],
        ['Clonación e Identidad', 'Exploración de qué significa ser humano en un mundo donde la identidad puede ser replicada'],
        ['Capitalismo Tecnológico', 'Crítica a la mercantilización de la vida y la tecnología'],
        ['Relaciones Humanas', 'Análisis de las conexiones emocionales en un contexto deshumanizado'],
        ['Filosofía Existencial', 'Reflexiones sobre el sentido de la existencia y la mortalidad'],
        ['Ciencia y Ética', 'Cuestionamiento de los límites éticos de la investigación científica']
    ]
    
    temas_table = Table(temas_data, colWidths=[4*cm, 10*cm])
    temas_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TEXTCOLOR', (0, 0), (-1, -1), black),
        ('LINEBELOW', (0, 0), (-1, 0), 1, HexColor('#c53030')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [HexColor('#f8f9fa'), white]),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    
    story.append(temas_table)
    story.append(Spacer(1, 25))
    
    # Personajes principales
    story.append(Paragraph("PERSONAJES PRINCIPALES", section_style))
    
    personajes_text = """
    <b>Narrador Protagonista:</b> Un profesional que visita el complejo de clonación. Su perspectiva evoluciona desde la curiosidad científica hasta la comprensión emocional de la humanidad de los clones.<br/><br/>
    <b>Sophie:</b> Amiga de Roger y guía en el complejo. Representa la conexión humana en un entorno tecnológico. Su relación con el narrador explora temas de intimidad y autenticidad.<br/><br/>
    <b>Anthony:</b> Un clon que desarrolla emociones y miedos genuinos. Su personaje cuestiona la diferencia entre humanos "originales" y clones.<br/><br/>
    <b>Francisco:</b> Figura de autoridad científica que facilita el acceso a áreas restringidas. Representa el establishment tecnológico.
    """
    story.append(Paragraph(personajes_text, body_style))
    story.append(Spacer(1, 25))
    
    # Análisis literario
    story.append(Paragraph("ANÁLISIS LITERARIO", section_style))
    
    analisis_text = """
    La obra utiliza técnicas narrativas experimentales que incluyen:<br/><br/>
    • <b>Stream of consciousness:</b> Los pensamientos del narrador fluyen de manera no lineal<br/>
    • <b>Fragmentación temporal:</b> Los eventos no siguen una secuencia cronológica tradicional<br/>
    • <b>Diálogo filosófico:</b> Las conversaciones exploran temas existenciales profundos<br/>
    • <b>Imaginería científica:</b> Descripciones detalladas de tecnología y procedimientos<br/>
    • <b>Simbolismo:</b> Elementos como los "trajes blancos radiactivos" y el "sistema paladiánico"<br/><br/>
    
    El estilo narrativo combina prosa científica con reflexión poética, creando un tono único que oscila entre lo técnico y lo emocional.
    """
    story.append(Paragraph(analisis_text, body_style))
    story.append(Spacer(1, 25))
    
    # Contexto histórico-literario
    story.append(Paragraph("CONTEXTO HISTÓRICO-LITERARIO", section_style))
    
    contexto_text = """
    "Bioclones" se inscribe en la tradición de la ciencia ficción especulativa que examina las consecuencias sociales y éticas del avance tecnológico. La obra dialoga con:<br/><br/>
    • <b>Literatura distópica:</b> Elementos de control social y manipulación<br/>
    • <b>Ciberpunk:</b> Fusión de tecnología avanzada con crítica social<br/>
    • <b>Ficción especulativa:</b> Exploración de futuros posibles basados en tendencias actuales<br/>
    • <b>Literatura existencialista:</b> Reflexiones sobre la autenticidad y el sentido de la vida<br/><br/>
    
    La novela anticipa debates contemporáneos sobre clonación, inteligencia artificial y la naturaleza de la conciencia.
    """
    story.append(Paragraph(contexto_text, body_style))
    story.append(Spacer(1, 25))
    
    # Significado simbólico
    story.append(Paragraph("SIGNIFICADO SIMBÓLICO", section_style))
    
    simbolico_text = """
    <b>El Complejo Biológico:</b> Representa la institucionalización de la vida y la muerte, donde la creación de vida se convierte en un proceso industrial.<br/><br/>
    <b>Los Trajes Blancos:</b> Símbolo de la deshumanización de la ciencia cuando se separa de la ética.<br/><br/>
    <b>G.R.E.E.:</b> Acrónimo que sugiere codicia y explotación económica de la vida.<br/><br/>
    <b>La Capital Biológica:</b> Metáfora de la mercantilización de la existencia humana.<br/><br/>
    <b>Anthony y su miedo:</b> Representa la humanización de lo artificial y la artificialidad de lo humano.
    """
    story.append(Paragraph(simbolico_text, body_style))
    story.append(Spacer(1, 25))
    
    # Conclusiones
    story.append(Paragraph("CONCLUSIONES", section_style))
    
    conclusiones_text = """
    "Bioclones" es una obra que trasciende el género de ciencia ficción para convertirse en una reflexión profunda sobre la condición humana en la era tecnológica. La novela plantea preguntas fundamentales sobre la identidad, la autenticidad y los límites éticos del progreso científico.<br/><br/>
    
    La estructura fragmentada y el estilo experimental de la obra reflejan la naturaleza fragmentada de la experiencia humana contemporánea, donde la tecnología y la biología se entrelazan de maneras que desafían nuestras concepciones tradicionales de lo que significa ser humano.<br/><br/>
    
    La obra invita al lector a reflexionar sobre las implicaciones de un futuro donde la línea entre lo natural y lo artificial, entre lo humano y lo post-humano, se vuelve cada vez más borrosa.
    """
    story.append(Paragraph(conclusiones_text, body_style))
    story.append(Spacer(1, 30))
    
    # Información del análisis
    info_text = """
    <para align="center" fontSize="10" fontName="Helvetica" textColor="#718096">
    Análisis literario generado digitalmente<br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <i>Documento de apoyo para el estudio de "Bioclones"</i>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    
    # Construir el PDF
    doc.build(story)
    print("Análisis literario creado exitosamente: analisis_bioclones.pdf")

if __name__ == "__main__":
    create_analysis_document()

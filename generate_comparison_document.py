#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor
from datetime import datetime

def create_comparison_document():
    # Configuración del documento de comparación
    doc = SimpleDocTemplate(
        "comparacion_literaria_bioclones.pdf", 
        pagesize=A4,
        rightMargin=2*cm, 
        leftMargin=2*cm,
        topMargin=3*cm, 
        bottomMargin=2.5*cm,
        title="Comparación Literaria - Bioclones",
        author="Sistema de Análisis Comparativo Literario",
        subject="Ciencia Ficción - Análisis Comparativo - Literatura Contemporánea",
        creator="Sistema de Comparación Literaria Digital",
        keywords="comparación literaria, ciencia ficción, análisis comparativo, literatura contemporánea"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores comparativa
    primary_color = HexColor('#1e40af')      # Azul académico
    secondary_color = HexColor('#374151')    # Gris académico
    accent_color = HexColor('#dc2626')      # Rojo académico
    gold_color = HexColor('#d97706')        # Dorado académico
    light_gray = HexColor('#f9fafb')        # Gris claro
    text_gray = HexColor('#4b5563')         # Gris texto
    
    # Estilos comparativos
    title_style = ParagraphStyle(
        'ComparisonTitle',
        parent=styles['Heading1'],
        fontSize=26,
        spaceAfter=50,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=32,
        borderWidth=3,
        borderColor=accent_color,
        borderPadding=20,
        backColor=light_gray
    )
    
    subtitle_style = ParagraphStyle(
        'ComparisonSubtitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=40,
        spaceBefore=30,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Oblique',
        leading=24
    )
    
    section_style = ParagraphStyle(
        'ComparisonSection',
        parent=styles['Heading2'],
        fontSize=20,
        spaceAfter=30,
        spaceBefore=35,
        alignment=TA_LEFT,
        textColor=accent_color,
        fontName='Helvetica-Bold',
        leading=26,
        borderWidth=2,
        borderColor=accent_color,
        borderPadding=15,
        backColor=light_gray,
        leftIndent=15
    )
    
    subsection_style = ParagraphStyle(
        'ComparisonSubsection',
        parent=styles['Heading3'],
        fontSize=16,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_LEFT,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=22
    )
    
    body_style = ParagraphStyle(
        'ComparisonBody',
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
    
    quote_style = ParagraphStyle(
        'ComparisonQuote',
        parent=styles['Normal'],
        fontSize=13,
        spaceAfter=15,
        spaceBefore=15,
        alignment=TA_LEFT,
        leftIndent=30,
        rightIndent=30,
        fontName='Times-Italic',
        textColor=text_gray,
        leading=18,
        borderWidth=1,
        borderColor=HexColor('#d1d5db'),
        borderPadding=10,
        backColor=light_gray
    )
    
    data_style = ParagraphStyle(
        'ComparisonData',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=10,
        spaceBefore=5,
        alignment=TA_LEFT,
        fontName='Helvetica',
        textColor=secondary_color,
        leftIndent=15
    )
    
    # Contenido del documento
    story = []
    
    # Portada comparativa
    story.append(Spacer(1, 4*inch))
    story.append(Paragraph("COMPARACIÓN LITERARIA", title_style))
    story.append(Paragraph("Bioclones en el Contexto de la Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 1*inch))
    
    # Información del documento
    info_text = """
    <para align="center" fontSize="13" fontName="Helvetica" textColor="#4b5563">
    <b>Análisis Comparativo Literario</b><br/>
    <br/>
    <i>Estudio comparativo con obras de ciencia ficción</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Posicionamiento en la tradición literaria</b><br/>
    <br/>
    <font size="11" color="#6b7280">
    Metodología: Análisis comparativo literario<br/>
    Área: Ciencia Ficción | Enfoque: Comparación textual
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Índice
    story.append(Paragraph("ÍNDICE", section_style))
    story.append(Spacer(1, 30))
    
    index_data = [
        ['Sección', 'Página'],
        ['Contexto Histórico-Literario', '3'],
        ['Comparación con Obras Clásicas', '4'],
        ['Análisis de Técnicas Narrativas', '5'],
        ['Temas y Motivos Recurrentes', '6'],
        ['Influencias y Precedentes', '7'],
        ['Posicionamiento Crítico', '8'],
        ['Conclusiones Comparativas', '9']
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
    
    # Contexto histórico-literario
    story.append(Paragraph("CONTEXTO HISTÓRICO-LITERARIO", section_style))
    
    contexto_text = """
    "Bioclones" se inscribe en la tradición de la ciencia ficción especulativa que surge en la segunda mitad del siglo XX, caracterizada por la exploración de las consecuencias sociales y éticas del avance tecnológico. La obra dialoga con movimientos literarios como el ciberpunk, la ficción especulativa y la literatura distópica.
    """
    story.append(Paragraph(contexto_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Evolución del Género", subsection_style))
    evolucion_text = """
    La ciencia ficción ha evolucionado desde sus orígenes en la literatura pulp hasta convertirse en un género que aborda cuestiones fundamentales sobre la humanidad, la tecnología y el futuro. "Bioclones" representa una continuidad de esta tradición, incorporando elementos contemporáneos como la clonación y la biotecnología.
    """
    story.append(Paragraph(evolucion_text, body_style))
    story.append(PageBreak())
    
    # Comparación con obras clásicas
    story.append(Paragraph("COMPARACIÓN CON OBRAS CLÁSICAS", section_style))
    
    # Tabla de comparación
    comparacion_data = [
        ['Obra', 'Autor', 'Año', 'Temas Comunes', 'Diferencias'],
        ['Bioclones', 'Anónimo', '2024', 'Clonación, Identidad', 'Narrativa experimental'],
        ['¿Sueñan los androides...?', 'Philip K. Dick', '1968', 'Identidad, Humanidad', 'Estructura más tradicional'],
        ['Neuromante', 'William Gibson', '1984', 'Tecnología, Ciberespacio', 'Enfoque en informática'],
        ['Un mundo feliz', 'Aldous Huxley', '1932', 'Control social, Clonación', 'Distopía clásica'],
        ['Frankenstein', 'Mary Shelley', '1818', 'Creación artificial', 'Gótico romántico']
    ]
    
    comparacion_table = Table(comparacion_data, colWidths=[2.5*cm, 2.5*cm, 1.5*cm, 3*cm, 3*cm])
    comparacion_table.setStyle(TableStyle([
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
    
    story.append(comparacion_table)
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Análisis Comparativo", subsection_style))
    analisis_text = """
    La comparación con obras clásicas revela que "Bioclones" comparte preocupaciones temáticas fundamentales con la tradición de la ciencia ficción, pero se distingue por su estructura narrativa experimental y su enfoque contemporáneo en la biotecnología.
    """
    story.append(Paragraph(analisis_text, body_style))
    story.append(PageBreak())
    
    # Análisis de técnicas narrativas
    story.append(Paragraph("ANÁLISIS DE TÉCNICAS NARRATIVAS", section_style))
    
    tecnicas_text = """
    "Bioclones" emplea técnicas narrativas que la distinguen de la ciencia ficción tradicional, incluyendo la fragmentación temporal, el stream of consciousness y la multiplicidad de voces narrativas.
    """
    story.append(Paragraph(tecnicas_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Técnicas Identificadas", subsection_style))
    tecnicas_items = [
        "Fragmentación temporal: Los eventos no siguen una secuencia cronológica tradicional",
        "Stream of consciousness: Los pensamientos fluyen de manera no lineal",
        "Multiplicidad de voces: Diferentes perspectivas narrativas",
        "Diálogo filosófico: Conversaciones que exploran temas existenciales",
        "Imaginería científica: Descripciones detalladas de tecnología"
    ]
    
    for item in tecnicas_items:
        story.append(Paragraph(f"• {item}", data_style))
    
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Comparación con Técnicas Clásicas", subsection_style))
    comparacion_tecnicas_text = """
    A diferencia de la ciencia ficción clásica que privilegia la narrativa lineal, "Bioclones" adopta técnicas más experimentales que reflejan la fragmentación de la experiencia contemporánea.
    """
    story.append(Paragraph(comparacion_tecnicas_text, body_style))
    story.append(PageBreak())
    
    # Temas y motivos recurrentes
    story.append(Paragraph("TEMAS Y MOTIVOS RECURRENTES", section_style))
    
    temas_text = """
    El análisis comparativo revela que "Bioclones" comparte temas fundamentales con la tradición de la ciencia ficción, pero los desarrolla de manera única y contemporánea.
    """
    story.append(Paragraph(temas_text, body_style))
    story.append(Spacer(1, 20))
    
    # Tabla de temas
    temas_data = [
        ['Tema', 'Tradición Clásica', 'Bioclones', 'Innovación'],
        ['Identidad', '¿Qué es humano?', 'Clonación e identidad', 'Biotecnología'],
        ['Tecnología', 'Máquinas y robots', 'Clonación y DNA', 'Biotecnología'],
        ['Control social', 'Gobiernos totalitarios', 'Corporaciones biológicas', 'Capitalismo biológico'],
        ['Ética científica', 'Responsabilidad del creador', 'Límites de la clonación', 'Ética genética']
    ]
    
    temas_table = Table(temas_data, colWidths=[2.5*cm, 3*cm, 3*cm, 3*cm])
    temas_table.setStyle(TableStyle([
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
    
    story.append(temas_table)
    story.append(Spacer(1, 30))
    
    # Influencias y precedentes
    story.append(Paragraph("INFLUENCIAS Y PRECEDENTES", section_style))
    
    influencias_text = """
    "Bioclones" muestra claras influencias de la literatura de ciencia ficción del siglo XX, particularmente en su exploración de temas como la identidad, la clonación y las implicaciones éticas de la tecnología.
    """
    story.append(Paragraph(influencias_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Influencias Identificadas", subsection_style))
    influencias_items = [
        "Philip K. Dick: Exploración de la realidad y la identidad",
        "William Gibson: Estilo narrativo fragmentado y tecnológico",
        "Aldous Huxley: Crítica del control social y la manipulación",
        "Mary Shelley: Cuestionamiento de los límites de la creación",
        "Jorge Luis Borges: Experimentación narrativa y filosófica"
    ]
    
    for item in influencias_items:
        story.append(Paragraph(f"• {item}", data_style))
    
    story.append(PageBreak())
    
    # Posicionamiento crítico
    story.append(Paragraph("POSICIONAMIENTO CRÍTICO", section_style))
    
    posicionamiento_text = """
    "Bioclones" se posiciona en la tradición de la ciencia ficción especulativa contemporánea, caracterizada por su enfoque en la biotecnología y su experimentación narrativa. La obra anticipa debates contemporáneos sobre clonación, identidad y ética genética.
    """
    story.append(Paragraph(posicionamiento_text, body_style))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Contribuciones al Género", subsection_style))
    contribuciones_items = [
        "Exploración contemporánea de la clonación y biotecnología",
        "Experimentación con técnicas narrativas no lineales",
        "Integración de reflexiones filosóficas con ciencia ficción",
        "Anticipación de debates éticos sobre tecnología genética",
        "Fusión de elementos poéticos con narrativa especulativa"
    ]
    
    for item in contribuciones_items:
        story.append(Paragraph(f"• {item}", data_style))
    
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("Relevancia Contemporánea", subsection_style))
    relevancia_text = """
    La obra adquiere relevancia especial en el contexto contemporáneo, donde los avances en biotecnología y clonación han hecho que sus temas sean más urgentes y actuales que nunca.
    """
    story.append(Paragraph(relevancia_text, body_style))
    story.append(PageBreak())
    
    # Conclusiones comparativas
    story.append(Paragraph("CONCLUSIONES COMPARATIVAS", section_style))
    
    conclusiones_text = """
    El análisis comparativo de "Bioclones" revela una obra que, aunque se inscribe en la tradición de la ciencia ficción, aporta elementos innovadores y contemporáneos que la distinguen de sus predecesores.
    """
    story.append(Paragraph(conclusiones_text, body_style))
    story.append(Spacer(1, 20))
    
    conclusiones_items = [
        "La obra mantiene la tradición temática de la ciencia ficción pero la actualiza con preocupaciones contemporáneas",
        "Las técnicas narrativas experimentales reflejan la fragmentación de la experiencia moderna",
        "El enfoque en la biotecnología anticipa debates actuales sobre ética genética",
        "La integración de elementos poéticos y filosóficos enriquece el género",
        "La obra contribuye a la evolución del género hacia formas más experimentales"
    ]
    
    for item in conclusiones_items:
        story.append(Paragraph(f"• {item}", data_style))
    
    story.append(Spacer(1, 40))
    
    # Información de cierre
    cierre_text = """
    <para align="center" fontSize="11" fontName="Helvetica" textColor="#6b7280">
    — Análisis comparativo generado automáticamente —<br/>
    <br/>
    <b>Investigación literaria comparativa</b><br/>
    <i>Metodología: Análisis comparativo literario</i><br/>
    <br/>
    <font size="9" color="#9ca3af">
    Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    Sistema: Análisis Comparativo Literario Automático
    </font>
    </para>
    """
    story.append(Paragraph(cierre_text, body_style))
    
    # Función para numerar páginas
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.drawRightString(200*cm, 20*cm, text)
        canvas.restoreState()
    
    # Construir el PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print("Documento de comparación creado exitosamente: comparacion_literaria_bioclones.pdf")

if __name__ == "__main__":
    create_comparison_document()





















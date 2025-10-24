#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def create_luxury_pdf():
    # Configuración del documento de lujo
    doc = SimpleDocTemplate(
        "bioclones_novela_luxury.pdf", 
        pagesize=A4,
        rightMargin=2.5*cm, 
        leftMargin=2.5*cm,
        topMargin=3.5*cm, 
        bottomMargin=3*cm,
        title="Bioclones - Una Novela de Ciencia Ficción",
        author="Manuscrito Original Transcrito",
        subject="Ciencia Ficción - Clonación - Identidad Humana",
        creator="Sistema de Transcripción y Formateo Digital de Lujo",
        keywords="ciencia ficción, clonación, identidad, tecnología, futuro, manuscrito"
    )
    
    styles = getSampleStyleSheet()
    
    # Paleta de colores de lujo
    primary_color = HexColor('#0f172a')      # Negro azulado profundo
    secondary_color = HexColor('#1e40af')    # Azul real
    accent_color = HexColor('#dc2626')      # Rojo vibrante
    gold_color = HexColor('#f59e0b')        # Dorado
    silver_color = HexColor('#6b7280')      # Plata
    light_gray = HexColor('#f8fafc')        # Gris muy claro
    text_gray = HexColor('#374151')         # Gris texto
    border_gray = HexColor('#e5e7eb')       # Gris borde
    
    # Estilos de lujo
    title_style = ParagraphStyle(
        'LuxuryTitle',
        parent=styles['Heading1'],
        fontSize=42,
        spaceAfter=80,
        spaceBefore=60,
        alignment=TA_CENTER,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=50,
        borderWidth=5,
        borderColor=gold_color,
        borderPadding=30,
        backColor=light_gray,
        leftIndent=30,
        rightIndent=30
    )
    
    subtitle_style = ParagraphStyle(
        'LuxurySubtitle',
        parent=styles['Heading2'],
        fontSize=24,
        spaceAfter=70,
        spaceBefore=50,
        alignment=TA_CENTER,
        textColor=secondary_color,
        fontName='Helvetica-Oblique',
        leading=30,
        borderWidth=3,
        borderColor=border_gray,
        borderPadding=20,
        backColor=light_gray,
        leftIndent=20,
        rightIndent=20
    )
    
    chapter_style = ParagraphStyle(
        'LuxuryChapter',
        parent=styles['Heading2'],
        fontSize=30,
        spaceAfter=50,
        spaceBefore=70,
        alignment=TA_LEFT,
        textColor=accent_color,
        fontName='Helvetica-Bold',
        leading=38,
        borderWidth=4,
        borderColor=accent_color,
        borderPadding=30,
        backColor=light_gray,
        leftIndent=25,
        rightIndent=25
    )
    
    section_style = ParagraphStyle(
        'LuxurySection',
        parent=styles['Heading3'],
        fontSize=24,
        spaceAfter=40,
        spaceBefore=40,
        alignment=TA_LEFT,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        leading=30,
        borderWidth=2,
        borderColor=border_gray,
        borderPadding=20,
        backColor=light_gray,
        leftIndent=20
    )
    
    body_style = ParagraphStyle(
        'LuxuryBody',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=25,
        spaceBefore=15,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0,
        fontName='Times-Roman',
        leading=24,
        textColor=text_gray
    )
    
    dialogue_style = ParagraphStyle(
        'LuxuryDialogue',
        parent=styles['Normal'],
        fontSize=16,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_LEFT,
        leftIndent=60,
        rightIndent=60,
        fontName='Times-Italic',
        textColor=text_gray,
        leading=22,
        borderWidth=3,
        borderColor=gold_color,
        borderPadding=20,
        backColor=light_gray
    )
    
    quote_style = ParagraphStyle(
        'LuxuryQuote',
        parent=styles['Normal'],
        fontSize=20,
        spaceAfter=30,
        spaceBefore=30,
        alignment=TA_CENTER,
        fontName='Times-Italic',
        textColor=accent_color,
        leftIndent=80,
        rightIndent=80,
        leading=28,
        borderWidth=4,
        borderColor=accent_color,
        borderPadding=25,
        backColor=light_gray
    )
    
    poetry_style = ParagraphStyle(
        'LuxuryPoetry',
        parent=styles['Normal'],
        fontSize=18,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_CENTER,
        fontName='Times-Italic',
        textColor=text_gray,
        leftIndent=100,
        rightIndent=100,
        leading=26,
        borderWidth=2,
        borderColor=border_gray,
        borderPadding=20,
        backColor=light_gray
    )
    
    footnote_style = ParagraphStyle(
        'LuxuryFootnote',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        spaceBefore=8,
        alignment=TA_LEFT,
        fontName='Helvetica',
        textColor=silver_color,
        leftIndent=30,
        leading=16
    )
    
    index_style = ParagraphStyle(
        'LuxuryIndex',
        parent=styles['Normal'],
        fontSize=15,
        spaceAfter=18,
        spaceBefore=10,
        alignment=TA_LEFT,
        fontName='Helvetica',
        textColor=secondary_color,
        leading=20
    )
    
    # Contenido del libro
    story = []
    
    # Portada de lujo
    story.append(Spacer(1, 6*inch))
    
    # Título principal con decoración de lujo
    story.append(Paragraph("◆ BIOCLONES ◆", title_style))
    story.append(Spacer(1, 0.8*inch))
    story.append(Paragraph("Una Novela de Ciencia Ficción", subtitle_style))
    story.append(Spacer(1, 2.5*inch))
    
    # Línea decorativa de lujo
    story.append(Paragraph("◆" * 50, body_style))
    story.append(Spacer(1, 2*inch))
    
    # Información del manuscrito de lujo
    info_text = """
    <para align="center" fontSize="18" fontName="Helvetica" textColor="#374151">
    <b>MANUSCRITO ORIGINAL</b><br/>
    <br/>
    <i>Transcrito y formateado digitalmente</i><br/>
    """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <b>Una historia sobre la naturaleza humana<br/>
    en la era de la clonación</b><br/>
    <br/>
    <font size="14" color="#6b7280">
    Género: Ciencia Ficción | Tema: Clonación e Identidad<br/>
    Estilo: Narrativa Experimental | Tono: Filosófico-Existencial<br/>
    Formato: Edición de Lujo Digital
    </font>
    </para>
    """
    story.append(Paragraph(info_text, body_style))
    story.append(PageBreak())
    
    # Índice de lujo
    story.append(Paragraph("◆ ÍNDICE ◆", chapter_style))
    story.append(Spacer(1, 60))
    
    # Tabla de índice de lujo
    index_data = [
        ['Capítulo', 'Título', 'Página'],
        ['I', 'Nuestro objetivo', '3'],
        ['II', 'Elisa y Canon', '4'], 
        ['III', 'Error y Acierto', '5'],
        ['IV', 'Dios Clones', '6'],
        ['V', 'Sophie y yo', '8'],
        ['VI', 'Borradores', '9']
    ]
    
    index_table = Table(index_data, colWidths=[2.5*cm, 10*cm, 2.5*cm])
    index_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 15),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('TEXTCOLOR', (0, 0), (-1, -1), secondary_color),
        ('LINEBELOW', (0, 0), (-1, 0), 4, accent_color),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [light_gray, white]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 20),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 18),
    ]))
    
    story.append(index_table)
    story.append(Spacer(1, 50))
    
    # Nota sobre el manuscrito de lujo
    nota_text = """
    <para align="center" fontSize="14" fontName="Helvetica" textColor="#6b7280">
    <i>Este manuscrito ha sido transcrito fielmente del original,<br/>
    preservando la estructura, estilo y esencia del autor.<br/>
    Edición de lujo digital para preservación y estudio.</i>
    </para>
    """
    story.append(Paragraph(nota_text, body_style))
    story.append(PageBreak())
    
    # Nuestro objetivo
    story.append(Paragraph("◆ CAPÍTULO I ◆", chapter_style))
    story.append(Paragraph("Nuestro objetivo", section_style))
    
    objetivo_text = """
    Era la primera vez que visitábamos una de las donde se clonaban cultivos. Una restricción de DNA – Francisco me hizo usar área restringida para personas con sus expertises muy dedicados a la genética con alto acceso en el organismo. Con grandes pilares de color azul, minimalista y apuntalado para generar mucha altura vi la entrada del gran complejo. Nuestras credenciales fueron actualizadas de inmediato. A nuestra llegada nos esperaba Sophie, amiga de Roger, siempre me pareció muy atractiva e inteligente.
    """
    story.append(Paragraph(objetivo_text, body_style))
    
    # Cita destacada de lujo
    story.append(Paragraph("¡Bienvenida a la Capital Biológica! – exclamó con gran calidez", quote_style))
    
    objetivo_continuacion = """
    aunque suele tener lenguaje no verbal para expresar su entusiasmo. Estábamos con credenciales para la razón y analítica, como consecuencia de que las clásicas acerca de un tópico en lo específico. Pero eso fue muy breve.
    """
    story.append(Paragraph(objetivo_continuacion, body_style))
    story.append(Spacer(1, 35))
    
    objetivo_text2 = """
    No traigo valijas y maletas y una misión de colas a hacer a nueva investigación. Las diferentes salas que parecen no tener fin. Con una curiosidad y emoción, caminé como la de un niño en una juguetería, recorrimos las diferentes áreas del complejo. Sophie continuaba muy bien en sus explicaciones.
    """
    story.append(Paragraph(objetivo_text2, body_style))
    story.append(Spacer(1, 35))
    
    objetivo_text3 = """
    Mientras me distraía observando los trajes blancos radiactivos del personal, dejamos nuestro espacio reducido de trabajo, un lugar lleno de servidumbre a donde pones la mirada. Negros, blancos, verdes, altos, bajos, nuevos, viejos. Los técnicos de todo tipo de seguridad. Completa y racional. Un solo error que fue con su sistema, Don Entrevista, muy sofisticado. Esperando que Sophie tuviera la misma emoción que nosotros, solo dispuso su pronto despedida al llegar al lugar. Disfrutamos con el morbo de ver qué hacían que hacían las otras áreas, rápido. Descargamos las nuevas actualizaciones a la fuente matriz del sistema paladiánico y metódico, trabajando hasta casi nueve de la noche.
    """
    story.append(Paragraph(objetivo_text3, body_style))
    story.append(Spacer(1, 35))
    
    objetivo_text4 = """
    Se sorprenden llegando al final de la jornada a sus martes, recordando que el complejo tenía los mejores salarios y ventajas competitivas de las sesiones extracurriculares que ponían muy celosos al personal, como la secreta a veces todos querían. Todos aluden en su contrato: G. R. E. E.
    """
    story.append(Paragraph(objetivo_text4, body_style))
    story.append(Spacer(1, 35))
    
    objetivo_text5 = """
    Cuando me imaginaba un salario diez veces más grande, y lo multiplicaba por años que me faltaban hasta la esperanza de vida, esto sin gastar en nada, tenía un total en activos que me llevaban a una fantasía de ser alguien con dinero.
    """
    story.append(Paragraph(objetivo_text5, body_style))
    
    # Nota al pie de lujo
    story.append(Paragraph("¹ G.R.E.E.: Posiblemente un acrónimo relacionado con la gestión de recursos genéticos y experimentales.", footnote_style))
    story.append(PageBreak())
    
    # Elisa y Canon
    story.append(Paragraph("◆ CAPÍTULO II ◆", chapter_style))
    story.append(Paragraph("Elisa y Canon", section_style))
    story.append(Spacer(1, 60))
    story.append(PageBreak())
    
    # Error y Acierto
    story.append(Paragraph("◆ CAPÍTULO III ◆", chapter_style))
    story.append(Paragraph("Error y Acierto", section_style))
    
    error_text = """
    El murmullo terminó en la sala donde se rumoraba la mayoría de los antibombas que nos protegían. Pasó más rápido el protocolo que a mi mente no le dio más oportunidades de rumorear mis pensamientos filosóficos – existencialistas. Toda esta noche no pude dormir, todo evocaba a la Eternidad. Todo fue un compartido sentimiento compartido – todo fue todo y a la vez nada.
    """
    story.append(Paragraph(error_text, body_style))
    story.append(Spacer(1, 40))
    
    story.append(Paragraph("Capítulo", section_style))
    
    capitulo_text = """
    Desde que toda la semana se habló de lo sucedido. La conclusión de la mayoría era ¿Qué será de nosotros?
    """
    story.append(Paragraph(capitulo_text, body_style))
    story.append(PageBreak())
    
    # Capítulo 2
    story.append(Paragraph("◆ CAPÍTULO IV ◆", chapter_style))
    story.append(Paragraph("Dios Clones", section_style))
    
    cap2_text = """
    Los accesos que habían pasado parecía que era pequeño para la plataforma, porque no habían tenido índices en días. Los bancos y la línea educativa, tenía unos acuerdos y era un mito. La realidad era que fue la primera vez que pasaba en una misión extraordinadaria. Una lucha constante y la guerra era en la Tierra no en la especie. Se pasaba todos los días ahí, hasta las aplicaciones donde crecía de lo sucedido.
    """
    story.append(Paragraph(cap2_text, body_style))
    story.append(Spacer(1, 35))
    
    anthony_text = """
    Anthony toda la semana estuvo callado y sin melancolía como si alguien lo hubiera notado su lesión. Por la primera vez que sentía simpatía por un clon. Siempre tuve la idea de que ellos eran más neutrales que yo. Todo pasa por algo y ese algo crea suerte en una carisma, inclusive existe muchos cerebros en los medios secretos de lo sucedido.
    """
    story.append(Paragraph(anthony_text, body_style))
    story.append(Spacer(1, 30))
    
    # Diálogo de lujo
    story.append(Paragraph("– ¡Tengo miedo de regresar a la Tierra! – exclamó Anthony.", dialogue_style))
    story.append(Paragraph("– Creo que todos – respondió, mientras observaba su cara blanca, pálida, que reflejaba un miedo muy genuino.", dialogue_style))
    story.append(Spacer(1, 35))
    
    voluntades_text = """
    Nuestras voluntades como profesionales extra planetarios iba hacia objetivos cada vez más extraordinarios, buscaban el origen. Nuestra economía biológica y acercarnos.
    """
    story.append(Paragraph(voluntades_text, body_style))
    story.append(Spacer(1, 35))
    
    valia_text = """
    Valía cada vez más para algún día emprender algo que nos acaudalara los bolsillos y no de nuestro pase.
    """
    story.append(Paragraph(valia_text, body_style))
    story.append(Spacer(1, 35))
    
    plantas_text = """
    De salida a plantas más pacíficas, donde la lucha de clases lo encuentra en una balanza más neutral. Otro de nuestros antepasados más formados, radicaba en cuervos, expresados para vivir el suceso de que era ganador exitoso que ayuda a protestar la economía. Lo encuentra esa una volatil donde que los ataques nucleares se expandieron alrededor del glúteo.
    """
    story.append(Paragraph(plantas_text, body_style))
    story.append(Spacer(1, 35))
    
    sube_baja_text = """
    Todo apuntaba a un sube y baja constante. Lo que terminamos lo gastamos rápido. Dado el costo de vida de, sumado a los salarios nos autodestruimos fugazmente. No sé si la depresión era constante pero lo positivo y la superación personal se convirtió en una especie de culto.
    """
    story.append(Paragraph(sube_baja_text, body_style))
    story.append(Spacer(1, 35))
    
    plenitud_text = """
    Donde un se sentía en plenitud cuando estamos junto personas muy positivas.
    """
    story.append(Paragraph(plenitud_text, body_style))
    story.append(Spacer(1, 35))
    
    biotecnologia_text = """
    Antes de terminar, nuestra bienvenida a Anthony recibió una gratificación alarmante y muy poco frecuente. Pronto nos encontrábamos en la área de Biotecnología donde se reforzaban los experimentos de DNA – Francisco y Creo cuando vemos los – hobbies como un trabajo, cambia mucho la forma de hacer las cosas. Siempre que nuestros horarios se extendían nos disgustaba, pero ahora lo vimos como algo de primera instancia.
    """
    story.append(Paragraph(biotecnologia_text, body_style))
    story.append(PageBreak())
    
    # Sophie y yo
    story.append(Paragraph("◆ CAPÍTULO V ◆", chapter_style))
    story.append(Paragraph("Sophie y yo", section_style))
    
    sophie_text = """
    Sophie y yo teníamos muchas cosas en común tales que siempre salían a brillar en las conversaciones que teníamos. Todo lo que yo pensaba ella lo adivinaba con mucha naturalidad que a veces me sorprendía. No habíamos pasado mucho tiempo juntos y sentía como me enamoraba día a día.
    """
    story.append(Paragraph(sophie_text, body_style))
    story.append(Spacer(1, 35))
    
    sophie_text2 = """
    Nuestra idea de estar juntos todo el tiempo no salía si solo era lo que yo quería y sentía, pero observaba cómo su sonrisa era más natural y genuina al verme. Era como la música. Se sentía en la década que fue compuesta la nota musical. Es decir eso ya pasó de moda y suena antigua. Era de esos tipos de pensamiento emoción gozosos con un rastro de melancolía.
    """
    story.append(Paragraph(sophie_text2, body_style))
    story.append(PageBreak())
    
    # Borradores
    story.append(Paragraph("◆ CAPÍTULO VI ◆", chapter_style))
    story.append(Paragraph("Borradores", section_style))
    story.append(Paragraph("Rápido", section_style))
    story.append(Paragraph("Una novela de Bio Clones 19", body_style))
    story.append(Spacer(1, 40))
    
    borrador_text = """
    Podría ser por rabia, ahora quiero decir. Ahora que no estoy en el mismo lugar, tengo una idea clara. Al día que llegamos después de la noche y al no haber nadie que estuviéramos Descansando, creo que el mundo es sucio.
    """
    story.append(Paragraph(borrador_text, body_style))
    story.append(Spacer(1, 35))
    
    ojos_text = """
    Ojos que parecen adivinar. Los había asistido sobre ahora, según se va o viene para el que...
    """
    story.append(Paragraph(ojos_text, body_style))
    story.append(Spacer(1, 35))
    
    # Poesía formateada de lujo
    senti_text = """
    <para align="center" fontSize="18" fontName="Times-Italic" textColor="#374151" leading="26">
    Sentí resbalarse en mis pies como las manos.<br/>
    Esos que ya no vigías, como cansados de tanto.<br/>
    Sentí esa que va siendo carnal con el tiempo.<br/>
    Una mañana gris. No frágil pero serís.<br/>
    Porque lo sabes, como son las mujeres.<br/>
    Yo creo que está bien, es este tiempo...
    </para>
    """
    story.append(Paragraph(senti_text, poetry_style))
    story.append(Spacer(1, 35))
    
    # Diálogo de lujo
    story.append(Paragraph("– ¿Me quieres responder?", dialogue_style))
    story.append(Paragraph("– ¿Qué es un pasado el amor?", dialogue_style))
    story.append(Paragraph("– No lo sé.", dialogue_style))
    story.append(Spacer(1, 35))
    
    aparto_text = """
    Apartó su mirada de la mía, sus ojos lucían Ven y conocen a bordo de mí.
    """
    story.append(Paragraph(aparto_text, body_style))
    story.append(Spacer(1, 35))
    
    recorde_text = """
    En dos segundos y micro segundos, recordé todos mis apegos, desesperanzas y frustraciones de lo que me construyó como Ángel hacia otros.
    """
    story.append(Paragraph(recorde_text, body_style))
    story.append(Spacer(1, 35))
    
    corazon_text = """
    Ella robó mi corazón a pasos mientras yo veía su clasismo reflejado en cómo trataba a los demás, que así me gustaba...
    """
    story.append(Paragraph(corazon_text, body_style))
    story.append(Spacer(1, 35))
    
    encerrado_text = """
    No sabía que estaba encerrado hasta donde más sus defectos. Pero traté de llevar la conversación hacia un descanso, pero ella se retiró como voluntariamente lo habría
    """
    story.append(Paragraph(encerrado_text, body_style))
    story.append(Spacer(1, 35))
    
    desayuno_text = """
    Tomaba el desayuno y la comida con ella en las semanas siguientes. Una y otra vuelta al mismo tema, a la misma conversación.
    """
    story.append(Paragraph(desayuno_text, body_style))
    story.append(Spacer(1, 70))
    
    # Fin del manuscrito de lujo
    story.append(Paragraph("◆ FIN DEL MANUSCRITO ◆", section_style))
    story.append(Spacer(1, 60))
    
    # Información de cierre de lujo
    cierre_text = """
    <para align="center" fontSize="16" fontName="Helvetica" textColor="#6b7280">
    — Fin del manuscrito original —<br/>
    <br/>
    <b>Transcrito y formateado digitalmente</b><br/>
    <i>Una historia sobre la naturaleza humana en la era de la clonación</i><br/>
    <br/>
    <font size="14" color="#9ca3af">
    Manuscrito preservado y digitalizado para futuras generaciones<br/>
    Formato: PDF de Lujo | Fecha: """ + datetime.now().strftime("%B %Y") + """<br/>
    <br/>
    <i>Edición especial de preservación digital</i>
    </font>
    </para>
    """
    story.append(Paragraph(cierre_text, body_style))
    
    # Función para numerar páginas de lujo
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 13)
        page_num = canvas.getPageNumber()
        text = f"Página {page_num}"
        canvas.drawRightString(200*cm, 20*cm, text)
        # Agregar línea decorativa de lujo
        canvas.setStrokeColor(HexColor('#f59e0b'))
        canvas.setLineWidth(3)
        canvas.line(2*cm, 1.5*cm, 19*cm, 1.5*cm)
        # Agregar símbolo decorativo de lujo
        canvas.setFillColor(HexColor('#f59e0b'))
        canvas.circle(10.5*cm, 1.5*cm, 4, fill=1)
        canvas.setFillColor(white)
        canvas.circle(10.5*cm, 1.5*cm, 2, fill=1)
        canvas.restoreState()
    
    # Construir el PDF
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print("PDF de lujo creado exitosamente: bioclones_novela_luxury.pdf")

if __name__ == "__main__":
    create_luxury_pdf()

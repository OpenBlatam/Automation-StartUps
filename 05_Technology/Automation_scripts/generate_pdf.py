#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def create_pdf():
    # Crear el documento PDF
    doc = SimpleDocTemplate("bioclones_novela.pdf", pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # Obtener estilos
    styles = getSampleStyleSheet()
    
    # Crear estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor='darkblue'
    )
    
    chapter_style = ParagraphStyle(
        'CustomChapter',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        spaceBefore=20,
        alignment=TA_LEFT,
        textColor='darkred'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=15,
        spaceBefore=15,
        alignment=TA_LEFT,
        textColor='darkgreen'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=TA_JUSTIFY,
        leftIndent=0,
        rightIndent=0
    )
    
    # Contenido del libro
    story = []
    
    # Título principal
    story.append(Paragraph("BIOCLONES", title_style))
    story.append(Paragraph("Una Novela", subtitle_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 30))
    
    # Nuestro objetivo
    story.append(Paragraph("Nuestro objetivo", chapter_style))
    
    objetivo_text = """
    Era la primera vez que visitábamos una de las donde se clonaban cultivos. Una restricción de DNA – Francisco me hizo usar área restringida para personas con sus expertises muy dedicados a la genética con alto acceso en el organismo. Con grandes pilares de color azul, minimalista y apuntalado para generar mucha altura vi la entrada del gran complejo. Nuestras credenciales fueron actualizadas de inmediato. A nuestra llegada nos esperaba Sophie, amiga de Roger, siempre me pareció muy atractiva e inteligente. ¡Bienvenida a la Capital Biológica! – exclamó con gran calidez, aunque suele tener lenguaje no verbal para expresar su entusiasmo. Estábamos con credenciales para la razón y analítica, como consecuencia de que las clásicas acerca de un tópico en lo específico. Pero eso fue muy breve.
    """
    story.append(Paragraph(objetivo_text, body_style))
    story.append(Spacer(1, 12))
    
    objetivo_text2 = """
    No traigo valijas y maletas y una misión de colas a hacer a nueva investigación. Las diferentes salas que parecen no tener fin. Con una curiosidad y emoción, caminé como la de un niño en una juguetería, recorrimos las diferentes áreas del complejo. Sophie continuaba muy bien en sus explicaciones.
    """
    story.append(Paragraph(objetivo_text2, body_style))
    story.append(Spacer(1, 12))
    
    objetivo_text3 = """
    Mientras me distraía observando los trajes blancos radiactivos del personal, dejamos nuestro espacio reducido de trabajo, un lugar lleno de servidumbre a donde pones la mirada. Negros, blancos, verdes, altos, bajos, nuevos, viejos. Los técnicos de todo tipo de seguridad. Completa y racional. Un solo error que fue con su sistema, Don Entrevista, muy sofisticado. Esperando que Sophie tuviera la misma emoción que nosotros, solo dispuso su pronto despedida al llegar al lugar. Disfrutamos con el morbo de ver qué hacían que hacían las otras áreas, rápido. Descargamos las nuevas actualizaciones a la fuente matriz del sistema paladiánico y metódico, trabajando hasta casi nueve de la noche. Se sorprenden llegando al final de la jornada a sus martes, recordando que el complejo tenía los mejores salarios y ventajas competitivas de las sesiones extracurriculares que ponían muy celosos al personal, como la secreta a veces todos querían. Todos aluden en su contrato: G. R. E. E.
    """
    story.append(Paragraph(objetivo_text3, body_style))
    story.append(Spacer(1, 12))
    
    objetivo_text4 = """
    Cuando me imaginaba un salario diez veces más grande, y lo multiplicaba por años que me faltaban hasta la esperanza de vida, esto sin gastar en nada, tenía un total en activos que me llevaban a una fantasía de ser alguien con dinero.
    """
    story.append(Paragraph(objetivo_text4, body_style))
    story.append(Spacer(1, 20))
    
    # Línea separadora
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 20))
    
    # Elisa y Canon
    story.append(Paragraph("Elisa y Canon", chapter_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 20))
    
    # Error y Acierto
    story.append(Paragraph("Error y Acierto", chapter_style))
    
    error_text = """
    El murmullo terminó en la sala donde se rumoraba la mayoría de los antibombas que nos protegían. Pasó más rápido el protocolo que a mi mente no le dio más oportunidades de rumorear mis pensamientos filosóficos – existencialistas. Toda esta noche no pude dormir, todo evocaba a la Eternidad. Todo fue un compartido sentimiento compartido – todo fue todo y a la vez nada.
    """
    story.append(Paragraph(error_text, body_style))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Capítulo", subtitle_style))
    
    capitulo_text = """
    Desde que toda la semana se habló de lo sucedido. La conclusión de la mayoría era ¿Qué será de nosotros?
    """
    story.append(Paragraph(capitulo_text, body_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 20))
    
    # Capítulo 2
    story.append(Paragraph("Capítulo 2 - Dios Clones", chapter_style))
    
    cap2_text = """
    Los accesos que habían pasado parecía que era pequeño para la plataforma, porque no habían tenido índices en días. Los bancos y la línea educativa, tenía unos acuerdos y era un mito. La realidad era que fue la primera vez que pasaba en una misión extraordinadaria. Una lucha constante y la guerra era en la Tierra no en la especie. Se pasaba todos los días ahí, hasta las aplicaciones donde crecía de lo sucedido.
    """
    story.append(Paragraph(cap2_text, body_style))
    story.append(Spacer(1, 12))
    
    anthony_text = """
    Anthony toda la semana estuvo callado y sin melancolía como si alguien lo hubiera notado su lesión. Por la primera vez que sentía simpatía por un clon. Siempre tuve la idea de que ellos eran más neutrales que yo. Todo pasa por algo y ese algo crea suerte en una carisma, inclusive existe muchos cerebros en los medios secretos de lo sucedido. – ¡Tengo miedo de regresar a la Tierra! – exclamó Anthony.
    """
    story.append(Paragraph(anthony_text, body_style))
    story.append(Spacer(1, 12))
    
    respuesta_text = """
    – Creo que todos – respondió, mientras observaba su cara blanca, pálida, que reflejaba un miedo muy genuino.
    """
    story.append(Paragraph(respuesta_text, body_style))
    story.append(Spacer(1, 12))
    
    voluntades_text = """
    Nuestras voluntades como profesionales extra planetarios iba hacia objetivos cada vez más extraordinarios, buscaban el origen. Nuestra economía biológica y acercarnos.
    """
    story.append(Paragraph(voluntades_text, body_style))
    story.append(Spacer(1, 12))
    
    valia_text = """
    Valía cada vez más para algún día emprender algo que nos acaudalara los bolsillos y no de nuestro pase.
    """
    story.append(Paragraph(valia_text, body_style))
    story.append(Spacer(1, 12))
    
    plantas_text = """
    De salida a plantas más pacíficas, donde la lucha de clases lo encuentra en una balanza más neutral. Otro de nuestros antepasados más formados, radicaba en cuervos, expresados para vivir el suceso de que era ganador exitoso que ayuda a protestar la economía. Lo encuentra esa una volatil donde que los ataques nucleares se expandieron alrededor del glúteo.
    """
    story.append(Paragraph(plantas_text, body_style))
    story.append(Spacer(1, 12))
    
    sube_baja_text = """
    Todo apuntaba a un sube y baja constante. Lo que terminamos lo gastamos rápido. Dado el costo de vida de, sumado a los salarios nos autodestruimos fugazmente. No sé si la depresión era constante pero lo positivo y la superación personal se convirtió en una especie de culto.
    """
    story.append(Paragraph(sube_baja_text, body_style))
    story.append(Spacer(1, 12))
    
    plenitud_text = """
    Donde un se sentía en plenitud cuando estamos junto personas muy positivas.
    """
    story.append(Paragraph(plenitud_text, body_style))
    story.append(Spacer(1, 12))
    
    biotecnologia_text = """
    Antes de terminar, nuestra bienvenida a Anthony recibió una gratificación alarmante y muy poco frecuente. Pronto nos encontrábamos en la área de Biotecnología donde se reforzaban los experimentos de DNA – Francisco y Creo cuando vemos los – hobbies como un trabajo, cambia mucho la forma de hacer las cosas. Siempre que nuestros horarios se extendían nos disgustaba, pero ahora lo vimos como algo de primera instancia.
    """
    story.append(Paragraph(biotecnologia_text, body_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 20))
    
    # Sophie y yo
    story.append(Paragraph("Sophie y yo", chapter_style))
    
    sophie_text = """
    Sophie y yo teníamos muchas cosas en común tales que siempre salían a brillar en las conversaciones que teníamos. Todo lo que yo pensaba ella lo adivinaba con mucha naturalidad que a veces me sorprendía. No habíamos pasado mucho tiempo juntos y sentía como me enamoraba día a día.
    """
    story.append(Paragraph(sophie_text, body_style))
    story.append(Spacer(1, 12))
    
    sophie_text2 = """
    Nuestra idea de estar juntos todo el tiempo no salía si solo era lo que yo quería y sentía, pero observaba cómo su sonrisa era más natural y genuina al verme. Era como la música. Se sentía en la década que fue compuesta la nota musical. Es decir eso ya pasó de moda y suena antigua. Era de esos tipos de pensamiento emoción gozosos con un rastro de melancolía.
    """
    story.append(Paragraph(sophie_text2, body_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("─" * 50, body_style))
    story.append(Spacer(1, 20))
    
    # Borradores
    story.append(Paragraph("Borradores", chapter_style))
    story.append(Paragraph("Rápido", subtitle_style))
    story.append(Paragraph("Una novela de Bio Clones 19", body_style))
    story.append(Spacer(1, 12))
    
    borrador_text = """
    Podría ser por rabia, ahora quiero decir. Ahora que no estoy en el mismo lugar, tengo una idea clara. Al día que llegamos después de la noche y al no haber nadie que estuviéramos Descansando, creo que el mundo es sucio.
    """
    story.append(Paragraph(borrador_text, body_style))
    story.append(Spacer(1, 12))
    
    ojos_text = """
    Ojos que parecen adivinar. Los había asistido sobre ahora, según se va o viene para el que...
    """
    story.append(Paragraph(ojos_text, body_style))
    story.append(Spacer(1, 12))
    
    senti_text = """
    Sentí resbalarse en mis pies como las manos.
    Esos que ya no vigías, como cansados de tanto.
    Sentí esa que va siendo carnal con el tiempo.
    Una mañana gris. No frágil pero serís.
    Porque lo sabes, como son las mujeres.
    Yo creo que está bien, es este tiempo...
    """
    story.append(Paragraph(senti_text, body_style))
    story.append(Spacer(1, 12))
    
    dialogo_text = """
    – ¿Me quieres responder?
    – ¿Qué es un pasado el amor?
    – No lo sé.
    """
    story.append(Paragraph(dialogo_text, body_style))
    story.append(Spacer(1, 12))
    
    aparto_text = """
    Apartó su mirada de la mía, sus ojos lucían Ven y conocen a bordo de mí.
    """
    story.append(Paragraph(aparto_text, body_style))
    story.append(Spacer(1, 12))
    
    recorde_text = """
    En dos segundos y micro segundos, recordé todos mis apegos, desesperanzas y frustraciones de lo que me construyó como Ángel hacia otros.
    """
    story.append(Paragraph(recorde_text, body_style))
    story.append(Spacer(1, 12))
    
    corazon_text = """
    Ella robó mi corazón a pasos mientras yo veía su clasismo reflejado en cómo trataba a los demás, que así me gustaba...
    """
    story.append(Paragraph(corazon_text, body_style))
    story.append(Spacer(1, 12))
    
    encerrado_text = """
    No sabía que estaba encerrado hasta donde más sus defectos. Pero traté de llevar la conversación hacia un descanso, pero ella se retiró como voluntariamente lo habría
    """
    story.append(Paragraph(encerrado_text, body_style))
    story.append(Spacer(1, 12))
    
    desayuno_text = """
    Tomaba el desayuno y la comida con ella en las semanas siguientes. Una y otra vuelta al mismo tema, a la misma conversación.
    """
    story.append(Paragraph(desayuno_text, body_style))
    story.append(Spacer(1, 30))
    
    # Fin del manuscrito
    story.append(Paragraph("Fin del manuscrito", subtitle_style))
    
    # Construir el PDF
    doc.build(story)
    print("PDF creado exitosamente: bioclones_novela.pdf")

if __name__ == "__main__":
    create_pdf()
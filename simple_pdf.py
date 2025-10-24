#!/usr/bin/env python3
"""
Script simple para crear PDF de la novela
"""

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import os

def create_novel_pdf():
    """Crea el PDF de la novela"""
    
    # Crear el documento
    doc = SimpleDocTemplate("Novela_Libertad.pdf", pagesize=A4,
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
        alignment=1,  # Centrado
        textColor=HexColor('#2c3e50')
    )
    
    chapter_style = ParagraphStyle(
        'ChapterTitle',
        parent=styles['Heading2'],
        fontSize=18,
        spaceAfter=20,
        spaceBefore=30,
        textColor=HexColor('#34495e')
    )
    
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        alignment=4,  # Justificado
        firstLineIndent=18
    )
    
    # Contenido de la novela
    story = []
    
    # Título
    story.append(Paragraph("LIBERTAD", title_style))
    story.append(Paragraph("Una Novela sobre Psicología y la Condición Humana", 
                          ParagraphStyle('Subtitle', parent=styles['Normal'], 
                                        fontSize=14, alignment=1, 
                                        textColor=HexColor('#7f8c8d'))))
    story.append(Spacer(1, 20))
    
    # Capítulo 1
    story.append(Paragraph("Capítulo 1: El Umbral", chapter_style))
    story.append(Paragraph("""
    Pablo Tiernes se encontraba a punto de entrar a un pabellón de psiquiatría, colmado por su experiencia, 
    prefería el "psiquiátrico" que un centro de readaptación. Las personas que no han tenido un familiar o 
    amigo en aquellos lugares, no entendían la angustia y desesperación que se sentía. Cada vez que una 
    persona escuchaba sobre una persona que había estado en un psiquiátrico se creaba una especie de 
    estigma que "ensuciaba" el habla de quien escuchaba. Fármacos, jeringas, pisos blancos, enfermeros y 
    un montón de otras cosas, era lo que hacía separar a los anormales de los normales. ¿Qué es ser normal 
    dentro de los anormales? ¿Qué es ser una persona normal?
    """, normal_style))
    
    story.append(Paragraph("""
    Crear cosas y desarrollarlas, casi lleva un gran esfuerzo, llevar un proceso, dentro de todo, o al 
    menos eso parecía. Esta vez Pablo había tenido un intento de suicidio lo cual entristecía a su madre, 
    divorciada. Esto y más conductas lo llevó al pabellón donde lo esperaba personal muy cuidadoso. No era 
    su primera vez que perdía su libertad por conductas destructivas que para él no parecían gran cosa.
    """, normal_style))
    
    story.append(Paragraph("""
    El sonido de las llaves resonaba en el pasillo blanco, demasiado blanco. Pablo pensaba que el blanco 
    de los hospitales psiquiátricos tenía una cualidad especial: no era el blanco de la pureza, sino el 
    blanco de la ausencia, de lo que no se podía nombrar. Sus pasos se arrastraban por el suelo de linóleo 
    mientras observaba las puertas numeradas, cada una con su pequeña ventana de cristal reforzado.
    """, normal_style))
    
    story.append(PageBreak())
    
    # Capítulo 2
    story.append(Paragraph("Capítulo 2: La Segunda Vez", chapter_style))
    story.append(Paragraph("""
    "Dios está en todos lados menos aquí" – exclamó Pablo Tiernes. Su tedio incontrolable y su soberbia 
    intelectual no le permitían estar más de una semana en estos sitios, bajo tutela, custodia o contención. 
    Sabía que era su segunda vez que se encontraba encerrado, lo cual colmaba su paciencia hasta los límites 
    de la locura. Irónicamente Pablo fue diagnosticado como esquizofrénico hace 9 años pero siempre pensó que 
    era por negligencia médica, por eso el cura le terminó su sobredosis para el Trastorno Obsesivo Compulsivo.
    """, normal_style))
    
    story.append(Paragraph("""
    La habitación se llenó de silencio después de que el enfermero cerrara la puerta. Pablo se sentó en la 
    cama y observó las grietas en la pared. Cada grieta tenía una historia, cada mancha en el techo contaba 
    una historia de desesperación. Se preguntaba si las paredes podían absorber el dolor, si podían guardar 
    los ecos de las voces que habían gritado en esa misma habitación.
    """, normal_style))
    
    story.append(PageBreak())
    
    # Nota del autor
    story.append(Paragraph("Nota del Autor", chapter_style))
    story.append(Paragraph("""
    Esta novela explora la complejidad de la enfermedad mental desde una perspectiva humana y empática. 
    A través de la historia de Pablo Tiernes, se aborda el estigma social, la lucha interna, y la búsqueda 
    de libertad y dignidad en medio de las limitaciones impuestas por la esquizofrenia.
    """, normal_style))
    
    story.append(Paragraph("""
    La historia no pretende ser un manual médico, sino una reflexión sobre la condición humana, la resiliencia, 
    y la capacidad de encontrar significado y esperanza incluso en las circunstancias más difíciles.
    """, normal_style))
    
    story.append(Paragraph("""
    <b>Dedicado a todas las personas que luchan contra la enfermedad mental y a sus familias que los 
    acompañan en el camino.</b>
    """, normal_style))
    
    # Construir el PDF
    doc.build(story)
    print("PDF creado exitosamente: Novela_Libertad.pdf")

if __name__ == "__main__":
    create_novel_pdf()

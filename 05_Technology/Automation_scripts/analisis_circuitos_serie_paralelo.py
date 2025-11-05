#!/usr/bin/env python3
"""
Generador de PDF para Análisis de Circuitos en Serie y Paralelo
Autor: Asistente AI
Fecha: 2024
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, Line, Circle, String
from reportlab.graphics import renderPDF
from reportlab.lib.colors import black, blue, red, green
import os

def create_circuit_diagram():
    """Crear diagrama simple de circuitos en serie y paralelo"""
    d = Drawing(400, 200)
    
    # Circuito en serie
    # Batería
    d.add(Rect(50, 150, 30, 20, fillColor=colors.lightblue, strokeColor=black))
    d.add(String(65, 160, "V", fontSize=10, textAnchor="middle"))
    
    # Líneas del circuito en serie
    d.add(Line(80, 160, 120, 160))  # Línea horizontal
    d.add(Line(120, 160, 120, 140))  # Línea vertical
    d.add(Line(120, 140, 160, 140))  # Línea horizontal
    d.add(Line(160, 140, 160, 120))  # Línea vertical
    d.add(Line(160, 120, 200, 120))  # Línea horizontal
    d.add(Line(200, 120, 200, 100))  # Línea vertical
    d.add(Line(200, 100, 240, 100))  # Línea horizontal
    d.add(Line(240, 100, 240, 80))   # Línea vertical
    d.add(Line(240, 80, 280, 80))    # Línea horizontal
    d.add(Line(280, 80, 280, 100))   # Línea vertical
    d.add(Line(280, 100, 320, 100))  # Línea horizontal
    d.add(Line(320, 100, 320, 120))  # Línea vertical
    d.add(Line(320, 120, 360, 120))  # Línea horizontal
    d.add(Line(360, 120, 360, 140))  # Línea vertical
    d.add(Line(360, 140, 400, 140))  # Línea horizontal
    d.add(Line(400, 140, 400, 160))  # Línea vertical
    d.add(Line(400, 160, 50, 160))   # Línea de retorno
    
    # Resistencias/Lámparas en serie
    d.add(Rect(140, 135, 20, 10, fillColor=colors.yellow, strokeColor=black))
    d.add(String(150, 140, "R1", fontSize=8, textAnchor="middle"))
    
    d.add(Rect(180, 115, 20, 10, fillColor=colors.yellow, strokeColor=black))
    d.add(String(190, 120, "R2", fontSize=8, textAnchor="middle"))
    
    d.add(Rect(220, 95, 20, 10, fillColor=colors.yellow, strokeColor=black))
    d.add(String(230, 100, "R3", fontSize=8, textAnchor="middle"))
    
    # Título del diagrama
    d.add(String(200, 180, "Circuito en Serie", fontSize=12, textAnchor="middle"))
    
    return d

def create_parallel_circuit_diagram():
    """Crear diagrama de circuito en paralelo"""
    d = Drawing(400, 200)
    
    # Batería
    d.add(Rect(50, 150, 30, 20, fillColor=colors.lightblue, strokeColor=black))
    d.add(String(65, 160, "V", fontSize=10, textAnchor="middle"))
    
    # Líneas principales
    d.add(Line(80, 160, 200, 160))  # Línea superior
    d.add(Line(200, 160, 200, 140))  # Línea vertical principal
    d.add(Line(200, 140, 300, 140))  # Línea horizontal principal
    d.add(Line(300, 140, 300, 160))  # Línea vertical de retorno
    d.add(Line(300, 160, 350, 160))  # Línea de retorno
    d.add(Line(350, 160, 350, 140))  # Línea vertical final
    d.add(Line(350, 140, 50, 140))   # Línea de retorno inferior
    d.add(Line(50, 140, 50, 160))    # Línea vertical inicial
    
    # Ramas en paralelo
    # Rama 1
    d.add(Line(200, 140, 200, 120))  # Línea vertical rama 1
    d.add(Line(200, 120, 250, 120))  # Línea horizontal rama 1
    d.add(Line(250, 120, 250, 100))  # Línea vertical rama 1
    d.add(Line(250, 100, 300, 100))  # Línea horizontal rama 1
    d.add(Line(300, 100, 300, 120))  # Línea vertical rama 1
    d.add(Line(300, 120, 300, 140))  # Línea vertical rama 1
    
    # Rama 2
    d.add(Line(200, 140, 200, 80))   # Línea vertical rama 2
    d.add(Line(200, 80, 250, 80))    # Línea horizontal rama 2
    d.add(Line(250, 80, 250, 60))    # Línea vertical rama 2
    d.add(Line(250, 60, 300, 60))    # Línea horizontal rama 2
    d.add(Line(300, 60, 300, 80))    # Línea vertical rama 2
    d.add(Line(300, 80, 300, 140))   # Línea vertical rama 2
    
    # Rama 3
    d.add(Line(200, 140, 200, 40))   # Línea vertical rama 3
    d.add(Line(200, 40, 250, 40))    # Línea horizontal rama 3
    d.add(Line(250, 40, 250, 20))    # Línea vertical rama 3
    d.add(Line(250, 20, 300, 20))    # Línea horizontal rama 3
    d.add(Line(300, 20, 300, 40))    # Línea vertical rama 3
    d.add(Line(300, 40, 300, 140))   # Línea vertical rama 3
    
    # Resistencias en paralelo
    d.add(Rect(240, 95, 20, 10, fillColor=colors.yellow, strokeColor=black))
    d.add(String(250, 100, "R1", fontSize=8, textAnchor="middle"))
    
    d.add(Rect(240, 55, 20, 10, fillColor=colors.yellow, strokeColor=black))
    d.add(String(250, 60, "R2", fontSize=8, textAnchor="middle"))
    
    d.add(Rect(240, 15, 20, 10, fillColor=colors.yellow, strokeColor=black))
    d.add(String(250, 20, "R3", fontSize=8, textAnchor="middle"))
    
    # Título del diagrama
    d.add(String(200, 180, "Circuito en Paralelo", fontSize=12, textAnchor="middle"))
    
    return d

def create_pdf():
    """Crear el documento PDF completo"""
    filename = "/Users/adan/Documents/documentos_blatam/analisis_circuitos_serie_paralelo.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=12,
        spaceAfter=8,
        spaceBefore=12,
        textColor=colors.darkred
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_JUSTIFY
    )
    
    # Contenido del documento
    story = []
    
    # Título principal
    story.append(Paragraph("ANÁLISIS DE CIRCUITOS EN SERIE Y PARALELO", title_style))
    story.append(Spacer(1, 12))
    
    # Información del curso
    story.append(Paragraph("Foro de Análisis de Circuitos Eléctricos", heading_style))
    story.append(Paragraph("Objetivos de Aprendizaje:", subheading_style))
    story.append(Paragraph("• Analizar la distribución de corriente y tensión en circuitos en serie y en paralelo", normal_style))
    story.append(Paragraph("• Determinar la potencia activa, aparente y reactiva", normal_style))
    story.append(Paragraph("• Evaluar el efecto de la resonancia en circuitos RCL", normal_style))
    story.append(Paragraph("• Describir aplicaciones prácticas de estos conceptos", normal_style))
    story.append(Spacer(1, 20))
    
    # 1. Circuito en Serie
    story.append(Paragraph("1. ANÁLISIS DE CIRCUITOS EN SERIE", heading_style))
    
    # Diagrama de circuito en serie
    story.append(create_circuit_diagram())
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.1 Comportamiento con Múltiples Lámparas", subheading_style))
    story.append(Paragraph("Cuando añadimos más lámparas en serie a un circuito que inicialmente tiene una lámpara, una resistencia y una batería, ocurren los siguientes cambios:", normal_style))
    
    story.append(Paragraph("Efectos en la corriente:", subheading_style))
    story.append(Paragraph("• La corriente total del circuito <b>disminuye</b> significativamente", normal_style))
    story.append(Paragraph("• Esto se debe a que la resistencia total del circuito aumenta (Rt = R1 + R2 + R3 + ...)", normal_style))
    story.append(Paragraph("• Según la Ley de Ohm: I = V/R, al aumentar R, la corriente I disminuye", normal_style))
    
    story.append(Paragraph("Efectos en la tensión:", subheading_style))
    story.append(Paragraph("• La tensión de la batería se distribuye entre todos los elementos del circuito", normal_style))
    story.append(Paragraph("• Cada lámpara recibe una fracción de la tensión total: V1 = I × R1, V2 = I × R2, etc.", normal_style))
    story.append(Paragraph("• La suma de todas las caídas de tensión es igual a la tensión de la batería", normal_style))
    
    story.append(Paragraph("Implicaciones prácticas:", subheading_style))
    story.append(Paragraph("• Las lámparas brillarán menos (menor intensidad luminosa)", normal_style))
    story.append(Paragraph("• Si una lámpara se quema, todo el circuito se interrumpe", normal_style))
    story.append(Paragraph("• La potencia total disponible se distribuye entre más elementos", normal_style))
    
    story.append(PageBreak())
    
    # 2. Circuito en Paralelo
    story.append(Paragraph("2. ANÁLISIS DE CIRCUITOS EN PARALELO", heading_style))
    
    # Diagrama de circuito en paralelo
    story.append(create_parallel_circuit_diagram())
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.1 Ventajas en Sistemas Domésticos", subheading_style))
    story.append(Paragraph("En un sistema eléctrico doméstico, los dispositivos están conectados en paralelo, lo que ofrece múltiples ventajas:", normal_style))
    
    story.append(Paragraph("Ventajas de seguridad:", subheading_style))
    story.append(Paragraph("• <b>Independencia de dispositivos</b>: Si un dispositivo falla, los demás continúan funcionando", normal_style))
    story.append(Paragraph("• <b>Protección individual</b>: Cada circuito puede tener su propio interruptor y fusible", normal_style))
    story.append(Paragraph("• <b>Aislamiento de fallas</b>: Un cortocircuito en un dispositivo no afecta a los demás", normal_style))
    
    story.append(Paragraph("Ventajas de eficiencia energética:", subheading_style))
    story.append(Paragraph("• <b>Tensión constante</b>: Todos los dispositivos reciben la tensión nominal (120V o 220V)", normal_style))
    story.append(Paragraph("• <b>Corriente independiente</b>: Cada dispositivo consume solo la corriente que necesita", normal_style))
    story.append(Paragraph("• <b>Potencia óptima</b>: Los dispositivos funcionan a su potencia nominal", normal_style))
    story.append(Paragraph("• <b>Control selectivo</b>: Se puede encender/apagar dispositivos individualmente", normal_style))
    
    # 3. Análisis de Potencia
    story.append(Paragraph("3. ANÁLISIS DE POTENCIA EN CIRCUITOS", heading_style))
    
    story.append(Paragraph("3.1 Potencia Activa (P)", subheading_style))
    story.append(Paragraph("• En serie: P = I² × Rtotal, donde I es la corriente común", normal_style))
    story.append(Paragraph("• En paralelo: P = Σ(V²/Ri), donde cada dispositivo tiene su propia resistencia", normal_style))
    
    story.append(Paragraph("3.2 Potencia Aparente (S)", subheading_style))
    story.append(Paragraph("• S = V × I (en ambos tipos de circuito)", normal_style))
    story.append(Paragraph("• En paralelo es mayor debido a la mayor corriente total", normal_style))
    
    story.append(Paragraph("3.3 Potencia Reactiva (Q)", subheading_style))
    story.append(Paragraph("• Relevante cuando hay elementos inductivos o capacitivos", normal_style))
    story.append(Paragraph("• En circuitos RCL: Q = V × I × sin(φ), donde φ es el ángulo de desfase", normal_style))
    
    # 4. Resonancia en Circuitos RCL
    story.append(Paragraph("4. RESONANCIA EN CIRCUITOS RCL", heading_style))
    
    story.append(Paragraph("4.1 Resonancia en Serie", subheading_style))
    story.append(Paragraph("• Frecuencia de resonancia: fr = 1/(2π√(LC))", normal_style))
    story.append(Paragraph("• A la frecuencia de resonancia, XL = XC, resultando en impedancia mínima", normal_style))
    story.append(Paragraph("• La corriente es máxima y está en fase con la tensión", normal_style))
    
    story.append(Paragraph("4.2 Resonancia en Paralelo", subheading_style))
    story.append(Paragraph("• Misma frecuencia de resonancia que en serie", normal_style))
    story.append(Paragraph("• Impedancia máxima a la frecuencia de resonancia", normal_style))
    story.append(Paragraph("• La corriente es mínima y está en fase con la tensión", normal_style))
    
    story.append(Paragraph("4.3 Aplicaciones Prácticas", subheading_style))
    story.append(Paragraph("• <b>Filtros de frecuencia</b>: Separar señales de diferentes frecuencias", normal_style))
    story.append(Paragraph("• <b>Sintonización de radio</b>: Seleccionar estaciones específicas", normal_style))
    story.append(Paragraph("• <b>Compensación de factor de potencia</b>: Reducir la potencia reactiva en sistemas industriales", normal_style))
    story.append(Paragraph("• <b>Osciladores</b>: Generar señales de frecuencia específica", normal_style))
    
    # 5. Conclusiones
    story.append(Paragraph("5. CONCLUSIONES", heading_style))
    story.append(Paragraph("Los circuitos en serie y paralelo tienen aplicaciones específicas según las necesidades del sistema. Los circuitos en serie son útiles para aplicaciones donde se requiere control de corriente y distribución de tensión, mientras que los circuitos en paralelo son ideales para sistemas domésticos e industriales donde se necesita independencia, seguridad y eficiencia energética.", normal_style))
    
    story.append(Paragraph("La comprensión de estos conceptos es fundamental para el diseño y análisis de sistemas eléctricos eficientes y seguros, permitiendo optimizar el rendimiento energético y garantizar la protección de los equipos y usuarios.", normal_style))
    
    # Tabla comparativa
    story.append(Spacer(1, 20))
    story.append(Paragraph("TABLA COMPARATIVA: SERIE vs PARALELO", subheading_style))
    
    data = [
        ['Aspecto', 'Circuito en Serie', 'Circuito en Paralelo'],
        ['Corriente', 'Igual en todos los elementos', 'Se distribuye entre ramas'],
        ['Tensión', 'Se distribuye entre elementos', 'Igual en todas las ramas'],
        ['Resistencia Total', 'Rt = R1 + R2 + R3 + ...', '1/Rt = 1/R1 + 1/R2 + 1/R3 + ...'],
        ['Falla de un elemento', 'Interrumpe todo el circuito', 'Solo afecta esa rama'],
        ['Control individual', 'No es posible', 'Posible por rama'],
        ['Aplicación típica', 'Sistemas de control', 'Sistemas domésticos']
    ]
    
    table = Table(data, colWidths=[2*inch, 2.5*inch, 2.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Pie de página
    story.append(Paragraph("Documento generado para el Foro de Análisis de Circuitos Eléctricos", 
                          ParagraphStyle('Footer', parent=styles['Normal'], fontSize=9, 
                                       alignment=TA_CENTER, textColor=colors.grey)))
    
    # Construir el PDF
    doc.build(story)
    return filename

if __name__ == "__main__":
    try:
        filename = create_pdf()
        print(f"PDF creado exitosamente: {filename}")
    except Exception as e:
        print(f"Error al crear el PDF: {e}")
        print("Asegúrate de tener instalado reportlab: pip install reportlab")

#!/usr/bin/env python3
"""
Generador de PDF para Ejercicios de Probabilidad y Estadística
Foro 2 - Semana 3
Autor: Asistente AI
Fecha: 2024
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.colors import black, blue, red, green, darkblue, darkred
import math

def create_pdf():
    """Crear el documento PDF completo con las soluciones"""
    filename = "/Users/adan/Documents/documentos_blatam/foro_2_ejercicios_probabilidad.pdf"
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
    
    math_style = ParagraphStyle(
        'MathStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=6,
        alignment=TA_LEFT,
        leftIndent=20
    )
    
    # Contenido del documento
    story = []
    
    # Título principal
    story.append(Paragraph("FORO 2 - SEMANA 3", title_style))
    story.append(Paragraph("EJERCICIOS DE PROBABILIDAD Y ESTADÍSTICA", title_style))
    story.append(Spacer(1, 12))
    
    # Información del curso
    story.append(Paragraph("Resolución de Ejercicios de Probabilidad", heading_style))
    story.append(Spacer(1, 20))
    
    # EJERCICIO 1
    story.append(Paragraph("EJERCICIO 1 - MEDIA Y VARIANZA", heading_style))
    story.append(Paragraph("Mediante un estudio se determinó el número de veces que los compradores de un producto habían visto un anuncio televisivo antes de comprar el producto. Los resultados se muestran a continuación:", normal_style))
    
    # Tabla de datos
    data1 = [
        ['Número de veces que los compradores vieron el anuncio', '1', '2', '3', '4', '5'],
        ['Porcentaje de compradores', '25%', '18%', '17%', '20%', '20%']
    ]
    
    table1 = Table(data1, colWidths=[2.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
    table1.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table1)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("Considere que la información mostrada se comparta como una variable aleatoria discreta, calcule:", normal_style))
    
    story.append(Paragraph("a) Media (Un punto)", subheading_style))
    story.append(Paragraph("Para calcular la media de una variable aleatoria discreta, utilizamos la fórmula:", normal_style))
    story.append(Paragraph("μ = Σ(x × P(x))", math_style))
    story.append(Paragraph("Donde x es el valor de la variable y P(x) es su probabilidad.", normal_style))
    
    story.append(Paragraph("Cálculo paso a paso:", normal_style))
    story.append(Paragraph("μ = (1 × 0.25) + (2 × 0.18) + (3 × 0.17) + (4 × 0.20) + (5 × 0.20)", math_style))
    story.append(Paragraph("μ = 0.25 + 0.36 + 0.51 + 0.80 + 1.00", math_style))
    story.append(Paragraph("μ = 2.92", math_style))
    
    story.append(Paragraph("b) Varianza (Un punto)", subheading_style))
    story.append(Paragraph("Para calcular la varianza, utilizamos la fórmula:", normal_style))
    story.append(Paragraph("σ² = Σ[(x - μ)² × P(x)]", math_style))
    story.append(Paragraph("Donde μ es la media calculada anteriormente.", normal_style))
    
    story.append(Paragraph("Cálculo paso a paso:", normal_style))
    story.append(Paragraph("σ² = [(1-2.92)² × 0.25] + [(2-2.92)² × 0.18] + [(3-2.92)² × 0.17] + [(4-2.92)² × 0.20] + [(5-2.92)² × 0.20]", math_style))
    story.append(Paragraph("σ² = [(-1.92)² × 0.25] + [(-0.92)² × 0.18] + [(0.08)² × 0.17] + [(1.08)² × 0.20] + [(2.08)² × 0.20]", math_style))
    story.append(Paragraph("σ² = [3.6864 × 0.25] + [0.8464 × 0.18] + [0.0064 × 0.17] + [1.1664 × 0.20] + [4.3264 × 0.20]", math_style))
    story.append(Paragraph("σ² = 0.9216 + 0.1524 + 0.0011 + 0.2333 + 0.8653", math_style))
    story.append(Paragraph("σ² = 2.1737", math_style))
    
    story.append(PageBreak())
    
    # EJERCICIO 2
    story.append(Paragraph("EJERCICIO 2 - DISTRIBUCIÓN HIPERGEOMÉTRICA", heading_style))
    story.append(Paragraph("En un estudio sobre la eficiencia de distintos tipos de baterías, se cuenta con un lote de 20 unidades, de las cuales 12 son recargables y 8 son desechables. Se seleccionan aleatoriamente 5 baterías sin reemplazo para ser evaluadas en un nuevo dispositivo portátil. ¿Cuál es la probabilidad de que exactamente 3 de las baterías seleccionadas sean recargables? (Dos puntos)", normal_style))
    
    story.append(Paragraph("Datos:", subheading_style))
    story.append(Paragraph("• N = 20 (población total)", math_style))
    story.append(Paragraph("• K = 12 (baterías recargables)", math_style))
    story.append(Paragraph("• n = 5 (muestra seleccionada)", math_style))
    story.append(Paragraph("• x = 3 (baterías recargables en la muestra)", math_style))
    
    story.append(Paragraph("Solución:", subheading_style))
    story.append(Paragraph("Este es un problema de distribución hipergeométrica. La fórmula es:", normal_style))
    story.append(Paragraph("P(X = x) = C(K,x) × C(N-K, n-x) / C(N,n)", math_style))
    
    story.append(Paragraph("Donde C(a,b) representa las combinaciones de 'a' elementos tomados de 'b' en 'b'.", normal_style))
    
    story.append(Paragraph("Cálculo de las combinaciones:", normal_style))
    story.append(Paragraph("C(12,3) = 12! / (3! × 9!) = 220", math_style))
    story.append(Paragraph("C(8,2) = 8! / (2! × 6!) = 28", math_style))
    story.append(Paragraph("C(20,5) = 20! / (5! × 15!) = 15,504", math_style))
    
    story.append(Paragraph("Aplicando la fórmula:", normal_style))
    story.append(Paragraph("P(X = 3) = C(12,3) × C(8,2) / C(20,5)", math_style))
    story.append(Paragraph("P(X = 3) = (220 × 28) / 15,504", math_style))
    story.append(Paragraph("P(X = 3) = 6,160 / 15,504", math_style))
    story.append(Paragraph("P(X = 3) = 0.3972", math_style))
    
    story.append(Paragraph("Respuesta: La probabilidad de que exactamente 3 de las 5 baterías seleccionadas sean recargables es 0.3972 (39.72%).", normal_style))
    
    story.append(PageBreak())
    
    # EJERCICIO 3
    story.append(Paragraph("EJERCICIO 3 - DISTRIBUCIÓN DE POISSON", heading_style))
    story.append(Paragraph("En una estación de servicio, se atienden en promedio 5 vehículos por hora. ¿Cuál es la probabilidad de que en una hora seleccionada al azar se atiendan exactamente 2 vehículos? (Dos puntos)", normal_style))
    
    story.append(Paragraph("Datos:", subheading_style))
    story.append(Paragraph("• λ = 5 (tasa promedio de vehículos por hora)", math_style))
    story.append(Paragraph("• x = 2 (número de vehículos que queremos calcular)", math_style))
    
    story.append(Paragraph("Solución:", subheading_style))
    story.append(Paragraph("Este es un problema de distribución de Poisson. La fórmula es:", normal_style))
    story.append(Paragraph("P(X = x) = (e^(-λ) × λ^x) / x!", math_style))
    
    story.append(Paragraph("Cálculo paso a paso:", normal_style))
    story.append(Paragraph("P(X = 2) = (e^(-5) × 5^2) / 2!", math_style))
    story.append(Paragraph("P(X = 2) = (0.0067 × 25) / 2", math_style))
    story.append(Paragraph("P(X = 2) = 0.1675 / 2", math_style))
    story.append(Paragraph("P(X = 2) = 0.0838", math_style))
    
    story.append(Paragraph("Respuesta: La probabilidad de que se atiendan exactamente 2 vehículos en una hora es 0.0838 (8.38%).", normal_style))
    
    # EJERCICIO 4
    story.append(Paragraph("EJERCICIO 4 - DISTRIBUCIÓN BINOMIAL", heading_style))
    story.append(Paragraph("La probabilidad de que un cliente potencial elegido al azar realice una compra es de 0.20. Si un agente de ventas visita 6 clientes, ¿cuál es la probabilidad de que realice exactamente 4 ventas? (Dos puntos)", normal_style))
    
    story.append(Paragraph("Datos:", subheading_style))
    story.append(Paragraph("• n = 6 (número de clientes visitados)", math_style))
    story.append(Paragraph("• p = 0.20 (probabilidad de éxito - realizar una compra)", math_style))
    story.append(Paragraph("• x = 4 (número de ventas que queremos calcular)", math_style))
    
    story.append(Paragraph("Solución:", subheading_style))
    story.append(Paragraph("Este es un problema de distribución binomial. La fórmula es:", normal_style))
    story.append(Paragraph("P(X = x) = C(n,x) × p^x × (1-p)^(n-x)", math_style))
    
    story.append(Paragraph("Cálculo de las combinaciones:", normal_style))
    story.append(Paragraph("C(6,4) = 6! / (4! × 2!) = 15", math_style))
    
    story.append(Paragraph("Aplicando la fórmula:", normal_style))
    story.append(Paragraph("P(X = 4) = C(6,4) × (0.20)^4 × (0.80)^2", math_style))
    story.append(Paragraph("P(X = 4) = 15 × 0.0016 × 0.64", math_style))
    story.append(Paragraph("P(X = 4) = 15 × 0.001024", math_style))
    story.append(Paragraph("P(X = 4) = 0.0154", math_style))
    
    story.append(Paragraph("Respuesta: La probabilidad de que el agente realice exactamente 4 ventas de 6 clientes visitados es 0.0154 (1.54%).", normal_style))
    
    # Tabla resumen de fórmulas
    story.append(Spacer(1, 20))
    story.append(Paragraph("FÓRMULAS UTILIZADAS", subheading_style))
    
    data_formulas = [
        ['Distribución', 'Fórmula', 'Parámetros'],
        ['Media de Variable Discreta', 'μ = Σ(x × P(x))', 'x: valor, P(x): probabilidad'],
        ['Varianza de Variable Discreta', 'σ² = Σ[(x - μ)² × P(x)]', 'μ: media'],
        ['Hipergeométrica', 'P(X=x) = C(K,x)×C(N-K,n-x)/C(N,n)', 'N: población, K: éxitos, n: muestra'],
        ['Poisson', 'P(X=x) = (e^(-λ)×λ^x)/x!', 'λ: tasa promedio'],
        ['Binomial', 'P(X=x) = C(n,x)×p^x×(1-p)^(n-x)', 'n: ensayos, p: probabilidad éxito']
    ]
    
    table_formulas = Table(data_formulas, colWidths=[2*inch, 3*inch, 2*inch])
    table_formulas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(table_formulas)
    story.append(Spacer(1, 20))
    
    # Pie de página
    story.append(Paragraph("Documento generado para Foro 2 - Semana 3", 
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

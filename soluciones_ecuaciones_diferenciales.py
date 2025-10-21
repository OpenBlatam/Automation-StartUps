#!/usr/bin/env python3
"""
Generador de PDF para Soluciones de Ecuaciones Diferenciales y Transformadas de Laplace
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
import os

def create_pdf():
    """Crear el documento PDF completo con las soluciones"""
    filename = "/Users/adan/Documents/documentos_blatam/soluciones_ecuaciones_diferenciales.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=18)
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
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
    story.append(Paragraph("SOLUCIONES DE ECUACIONES DIFERENCIALES Y TRANSFORMADAS DE LAPLACE", title_style))
    story.append(Spacer(1, 12))
    
    # Información del curso
    story.append(Paragraph("Ejercicios Resueltos - Lecturas 4 y 5", heading_style))
    story.append(Spacer(1, 20))
    
    # LECTURA 4
    story.append(Paragraph("LECTURA 4 - SISTEMAS MASA-RESORTE Y CIRCUITOS LRC", heading_style))
    story.append(Paragraph("Resolver el ejercicio A o el ejercicio B (Solo uno de los dos):", subheading_style))
    story.append(Spacer(1, 12))
    
    # Ejercicio A
    story.append(Paragraph("A. Ecuación de movimiento para el sistema masa-resorte amortiguado", subheading_style))
    
    story.append(Paragraph("Datos:", subheading_style))
    story.append(Paragraph("• Peso (W) = 4 lb => Masa (m) = W/g = 4/32 = 1/8 slug", math_style))
    story.append(Paragraph("• Constante del resorte (k) = 6 lb/pie", math_style))
    story.append(Paragraph("• Fuerza de amortiguamiento (β) = 1 (numéricamente igual a la velocidad)", math_style))
    story.append(Paragraph("• Posición inicial x(0) = 1 pie (arriba del equilibrio, se toma como positivo)", math_style))
    story.append(Paragraph("• Velocidad inicial x'(0) = 9 pies/s (hacia abajo, se toma como positivo)", math_style))
    
    story.append(Paragraph("Ecuación diferencial:", subheading_style))
    story.append(Paragraph("m x'' + β x' + k x = 0", math_style))
    story.append(Paragraph("(1/8)x'' + 1x' + 6x = 0", math_style))
    story.append(Paragraph("Multiplicando por 8: x'' + 8x' + 48x = 0", math_style))
    
    story.append(Paragraph("Ecuación característica:", subheading_style))
    story.append(Paragraph("r² + 8r + 48 = 0", math_style))
    story.append(Paragraph("Resolviendo con la fórmula cuadrática:", math_style))
    story.append(Paragraph("r = [-8 ± sqrt(8² - 4×1×48)] / 2 = [-8 ± sqrt(64 - 192)] / 2", math_style))
    story.append(Paragraph("r = [-8 ± sqrt(-128)] / 2 = [-8 ± 8i×sqrt(2)] / 2 = -4 ± 4i×sqrt(2)", math_style))
    
    story.append(Paragraph("Solución general (caso subamortiguado):", subheading_style))
    story.append(Paragraph("x(t) = e^(-4t) × [C1 cos(4sqrt(2)t) + C2 sin(4sqrt(2)t)]", math_style))
    
    story.append(Paragraph("Aplicando condiciones iniciales:", subheading_style))
    story.append(Paragraph("x(0) = 1 => 1 = C1", math_style))
    story.append(Paragraph("x'(0) = 9 => 9 = -4C1 + 4sqrt(2)C2", math_style))
    story.append(Paragraph("Sustituyendo C1 = 1: 9 = -4 + 4sqrt(2)C2", math_style))
    story.append(Paragraph("13 = 4sqrt(2)C2 => C2 = 13 / (4sqrt(2)) = (13sqrt(2)) / 8", math_style))
    
    story.append(Paragraph("Ecuación de movimiento final:", subheading_style))
    story.append(Paragraph("x(t) = e^(-4t) × [cos(4sqrt(2)t) + (13sqrt(2)/8)sin(4sqrt(2)t)]", math_style))
    
    story.append(PageBreak())
    
    # Ejercicio B
    story.append(Paragraph("B. Función q(t) para el circuito LRC en serie", subheading_style))
    
    story.append(Paragraph("Datos:", subheading_style))
    story.append(Paragraph("• L = 1/5 h", math_style))
    story.append(Paragraph("• R = 22 Ω", math_style))
    story.append(Paragraph("• C = 1/350 f", math_style))
    story.append(Paragraph("• E(t) = 0 V", math_style))
    story.append(Paragraph("• q(0) = 7 C", math_style))
    story.append(Paragraph("• i(0) = q'(0) = 0 A", math_style))
    
    story.append(Paragraph("Ecuación diferencial:", subheading_style))
    story.append(Paragraph("L q'' + R q' + (1/C) q = E(t)", math_style))
    story.append(Paragraph("(1/5)q'' + 22q' + 350q = 0", math_style))
    story.append(Paragraph("Multiplicando por 5: q'' + 110q' + 1750q = 0", math_style))
    
    story.append(Paragraph("Ecuación característica:", subheading_style))
    story.append(Paragraph("r² + 110r + 1750 = 0", math_style))
    story.append(Paragraph("Resolviendo con la fórmula cuadrática:", math_style))
    story.append(Paragraph("r = [-110 ± sqrt(110² - 4×1×1750)] / 2 = [-110 ± sqrt(12100 - 7000)] / 2", math_style))
    story.append(Paragraph("r = [-110 ± sqrt(5100)] / 2 = -55 ± 5sqrt(51)", math_style))
    story.append(Paragraph("r1 = -55 + 5sqrt(51)", math_style))
    story.append(Paragraph("r2 = -55 - 5sqrt(51)", math_style))
    
    story.append(Paragraph("Solución general (caso sobreamortiguado):", subheading_style))
    story.append(Paragraph("q(t) = C1 e^(r1 t) + C2 e^(r2 t)", math_style))
    
    story.append(Paragraph("Aplicando condiciones iniciales:", subheading_style))
    story.append(Paragraph("q(0) = 7 => C1 + C2 = 7", math_style))
    story.append(Paragraph("q'(0) = 0 => C1 r1 + C2 r2 = 0", math_style))
    story.append(Paragraph("Resolviendo el sistema:", math_style))
    story.append(Paragraph("C1 = (357 + 77sqrt(51)) / 102", math_style))
    story.append(Paragraph("C2 = (357 - 77sqrt(51)) / 102", math_style))
    
    story.append(Paragraph("Función q(t) final:", subheading_style))
    story.append(Paragraph("q(t) = [(357 + 77sqrt(51)) / 102] × e^[(-55 + 5sqrt(51))t] + [(357 - 77sqrt(51)) / 102] × e^[(-55 - 5sqrt(51))t]", math_style))
    
    story.append(Paragraph("¿Alguna vez la carga en el capacitor es igual a cero?", subheading_style))
    story.append(Paragraph("No. Dado que q(0) = 7 y q'(0) = 0, la carga comienza en un máximo local. Ambas exponenciales decaen hacia cero, y aunque C1 es positivo y C2 es negativo, la función q(t) se mantiene positiva y asintóticamente se acerca a cero sin cruzarlo.", normal_style))
    
    story.append(PageBreak())
    
    # LECTURA 5
    story.append(Paragraph("LECTURA 5 - TRANSFORMADAS DE LAPLACE", heading_style))
    story.append(Paragraph("Resolver todos los ejercicios siguientes:", subheading_style))
    story.append(Spacer(1, 12))
    
    # Ejercicio 1
    story.append(Paragraph("1. Calcular la transformada de Laplace de 3 + t⁴ + sin(2t)", subheading_style))
    
    story.append(Paragraph("L{3} = 3/s", math_style))
    story.append(Paragraph("L{t⁴} = 4! / s^(4+1) = 24 / s⁵", math_style))
    story.append(Paragraph("L{sin(2t)} = 2 / (s² + 2²) = 2 / (s² + 4)", math_style))
    
    story.append(Paragraph("Resultado:", subheading_style))
    story.append(Paragraph("L{3 + t⁴ + sin(2t)} = 3/s + 24/s⁵ + 2/(s² + 4)", math_style))
    
    # Ejercicio 2
    story.append(Paragraph("2. Calcular la transformada inversa de Laplace de 4 / (s² - 9)", subheading_style))
    
    story.append(Paragraph("Sabemos que L⁻¹{a / (s² - a²)} = sinh(at)", math_style))
    story.append(Paragraph("En este caso, a² = 9, por lo tanto a = 3.", math_style))
    story.append(Paragraph("L⁻¹{4 / (s² - 9)} = (4/3) × L⁻¹{3 / (s² - 3²)}", math_style))
    
    story.append(Paragraph("Resultado:", subheading_style))
    story.append(Paragraph("L⁻¹{4 / (s² - 9)} = (4/3)sinh(3t)", math_style))
    
    # Ejercicio 3
    story.append(Paragraph("3. Resolver el problema de valores iniciales: 4y'' - y = 1 con y(0) = 0, y'(0) = 1/2", subheading_style))
    
    story.append(Paragraph("Ecuación homogénea: 4y'' - y = 0", subheading_style))
    story.append(Paragraph("• Ecuación característica: 4r² - 1 = 0 => r² = 1/4 => r = ±1/2", math_style))
    story.append(Paragraph("• Solución complementaria: y_c(t) = C1 e^(t/2) + C2 e^(-t/2)", math_style))
    
    story.append(Paragraph("Solución particular: Para y_p = A, tenemos 4(0) - A = 1 => A = -1", subheading_style))
    story.append(Paragraph("• y_p(t) = -1", math_style))
    
    story.append(Paragraph("Solución general: y(t) = C1 e^(t/2) + C2 e^(-t/2) - 1", subheading_style))
    
    story.append(Paragraph("Aplicando condiciones iniciales:", subheading_style))
    story.append(Paragraph("• y(0) = 0 => 0 = C1 + C2 - 1 => C1 + C2 = 1", math_style))
    story.append(Paragraph("• y'(0) = 1/2 => 1/2 = (1/2)C1 - (1/2)C2 => C1 - C2 = 1", math_style))
    story.append(Paragraph("• Resolviendo el sistema: C1 = 1, C2 = 0", math_style))
    
    story.append(Paragraph("Solución final:", subheading_style))
    story.append(Paragraph("y(t) = e^(t/2) - 1", math_style))
    
    # Ejercicio 4
    story.append(Paragraph("4. Resolver el problema de valores iniciales: y'' - 3y' + 2y = 2e^(2t) con y(0) = 0, y'(0) = 4", subheading_style))
    
    story.append(Paragraph("Ecuación homogénea: y'' - 3y' + 2y = 0", subheading_style))
    story.append(Paragraph("• Ecuación característica: r² - 3r + 2 = 0 => (r - 1)(r - 2) = 0 => r1 = 1, r2 = 2", math_style))
    story.append(Paragraph("• Solución complementaria: y_c(t) = C1 e^t + C2 e^(2t)", math_style))
    
    story.append(Paragraph("Solución particular: Como 2e^(2t) es parte de la solución complementaria, proponemos y_p = At e^(2t)", subheading_style))
    story.append(Paragraph("• y_p' = A e^(2t) + 2At e^(2t) = A(1 + 2t)e^(2t)", math_style))
    story.append(Paragraph("• y_p'' = A(4 + 4t)e^(2t)", math_style))
    story.append(Paragraph("• Sustituyendo en la ecuación diferencial: A = 2", math_style))
    story.append(Paragraph("• y_p(t) = 2t e^(2t)", math_style))
    
    story.append(Paragraph("Solución general: y(t) = C1 e^t + C2 e^(2t) + 2t e^(2t)", subheading_style))
    
    story.append(Paragraph("Aplicando condiciones iniciales:", subheading_style))
    story.append(Paragraph("• y(0) = 0 => C1 + C2 = 0", math_style))
    story.append(Paragraph("• y'(0) = 4 => C1 + 2C2 + 2 = 4 => C1 + 2C2 = 2", math_style))
    story.append(Paragraph("• Resolviendo el sistema: C1 = -2, C2 = 2", math_style))
    
    story.append(Paragraph("Solución final:", subheading_style))
    story.append(Paragraph("y(t) = -2e^t + 2e^(2t) + 2t e^(2t) = -2e^t + (2 + 2t)e^(2t)", math_style))
    
    # Tabla de fórmulas útiles
    story.append(Spacer(1, 20))
    story.append(Paragraph("FÓRMULAS ÚTILES", subheading_style))
    
    data = [
        ['Transformada', 'Función Original'],
        ['L{1}', '1/s'],
        ['L{t^n}', 'n! / s^(n+1)'],
        ['L{e^(at)}', '1 / (s - a)'],
        ['L{sin(at)}', 'a / (s² + a²)'],
        ['L{cos(at)}', 's / (s² + a²)'],
        ['L{sinh(at)}', 'a / (s² - a²)'],
        ['L{cosh(at)}', 's / (s² - a²)']
    ]
    
    table = Table(data, colWidths=[2.5*inch, 3*inch])
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
    story.append(Paragraph("Documento generado para ejercicios de Ecuaciones Diferenciales", 
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

#!/usr/bin/env python3
"""
Script para convertir el documento Word a PDF
"""

import os
import subprocess
import sys

def convert_word_to_pdf():
    """Convertir documento Word a PDF usando LibreOffice"""
    
    word_file = "Entregable2_Completo.docx"
    
    if not os.path.exists(word_file):
        print(f"Error: No se encontró el archivo {word_file}")
        return False
    
    try:
        # Intentar usar LibreOffice para convertir
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', '.',
            word_file
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            pdf_file = "Entregable2_Completo.pdf"
            if os.path.exists(pdf_file):
                print(f"PDF creado exitosamente: {pdf_file}")
                return True
            else:
                print("Error: El PDF no se generó correctamente")
                return False
        else:
            print(f"Error al convertir: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("LibreOffice no está instalado. Intentando con pandoc...")
        
        try:
            # Intentar con pandoc
            cmd = [
                'pandoc',
                word_file,
                '-o',
                'Entregable2_Completo.pdf'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("PDF creado exitosamente con pandoc")
                return True
            else:
                print(f"Error con pandoc: {result.stderr}")
                return False
                
        except FileNotFoundError:
            print("Ni LibreOffice ni pandoc están instalados.")
            print("Instalando LibreOffice...")
            
            # Intentar instalar LibreOffice en macOS
            try:
                subprocess.run(['brew', 'install', '--cask', 'libreoffice'], check=True)
                print("LibreOffice instalado. Intentando conversión nuevamente...")
                return convert_word_to_pdf()
            except:
                print("No se pudo instalar LibreOffice automáticamente.")
                print("Por favor, instala LibreOffice manualmente o usa el documento Word directamente.")
                return False

def create_html_version():
    """Crear una versión HTML del documento para visualización"""
    
    html_content = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entregable 2: Ecuaciones Diferenciales</title>
    <style>
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        h2 {
            color: #34495e;
            margin-top: 30px;
        }
        h3 {
            color: #7f8c8d;
        }
        .exercise {
            background-color: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }
        .solution {
            background-color: #e8f5e8;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        code {
            background-color: #f1f2f6;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        .math {
            font-style: italic;
            color: #2c3e50;
        }
    </style>
</head>
<body>
    <h1>ENTREGABLE 2: ECUACIONES DIFERENCIALES</h1>
    
    <h2>UNIVERSIDAD [NOMBRE DE LA UNIVERSIDAD]</h2>
    <h2>FACULTAD DE [NOMBRE DE LA FACULTAD]</h2>
    <h2>DEPARTAMENTO DE MATEMÁTICAS</h2>
    
    <hr>
    
    <h1>Reporte de Investigación: Aplicaciones de las Ecuaciones Diferenciales</h1>
    
    <hr>
    
    <p><strong>Materia:</strong> Ecuaciones Diferenciales</p>
    <p><strong>Profesor:</strong> [Nombre del Profesor]</p>
    <p><strong>Alumno:</strong> [Tu Nombre Completo]</p>
    <p><strong>Matrícula:</strong> [Tu Matrícula]</p>
    <p><strong>Carrera:</strong> [Tu Carrera]</p>
    <p><strong>Fecha:</strong> [Fecha Actual]</p>
    
    <h1>PARTE A: REPORTE DE INVESTIGACIÓN</h1>
    
    <h2>INTRODUCCIÓN</h2>
    <p>Las ecuaciones diferenciales constituyen una herramienta matemática fundamental en el análisis y modelado de fenómenos dinámicos que involucran cambios continuos en el tiempo o en el espacio. Estas ecuaciones relacionan una función desconocida con sus derivadas, permitiendo describir matemáticamente procesos naturales, físicos, químicos, biológicos y tecnológicos.</p>
    
    <p>En el contexto de la ingeniería, las ecuaciones diferenciales son indispensables para el diseño, análisis y optimización de sistemas complejos. Desde el modelado de circuitos eléctricos hasta el análisis de estructuras mecánicas, pasando por el control de procesos industriales y la simulación de sistemas dinámicos, estas ecuaciones proporcionan el marco matemático necesario para comprender y predecir el comportamiento de sistemas reales.</p>
    
    <p>La importancia del estudio de las ecuaciones diferenciales radica en su capacidad para transformar problemas prácticos complejos en modelos matemáticos manejables, facilitando así la toma de decisiones técnicas fundamentadas y el desarrollo de soluciones innovadoras a los desafíos de la ingeniería moderna.</p>
    
    <h2>APLICACIONES A LA INGENIERÍA EN GENERAL Y A [TU CARRERA] EN PARTICULAR</h2>
    
    <h3>Aplicaciones Generales en Ingeniería</h3>
    
    <h4>1. Ingeniería Mecánica</h4>
    <ul>
        <li><strong>Vibraciones y Oscilaciones:</strong> Las ecuaciones diferenciales de segundo orden modelan sistemas vibratorios como amortiguadores, suspensiones de vehículos y estructuras sometidas a cargas dinámicas.</li>
        <li><strong>Transferencia de Calor:</strong> La ecuación del calor (ecuación diferencial parcial) describe la distribución de temperatura en sólidos, esencial para el diseño de intercambiadores de calor y sistemas de refrigeración.</li>
        <li><strong>Dinámica de Fluidos:</strong> Las ecuaciones de Navier-Stokes modelan el comportamiento de fluidos, fundamentales en el diseño de turbinas, bombas y sistemas de ventilación.</li>
    </ul>
    
    <h4>2. Ingeniería Eléctrica</h4>
    <ul>
        <li><strong>Circuitos RLC:</strong> Los circuitos eléctricos con resistencias, inductores y capacitores se modelan mediante ecuaciones diferenciales lineales de segundo orden.</li>
        <li><strong>Sistemas de Control:</strong> La teoría de control utiliza ecuaciones diferenciales para diseñar sistemas de retroalimentación que mantengan la estabilidad y el rendimiento deseado.</li>
        <li><strong>Transmisión de Señales:</strong> Las ecuaciones de onda describen la propagación de señales electromagnéticas en cables y sistemas de comunicación.</li>
    </ul>
    
    <h4>3. Ingeniería Química</h4>
    <ul>
        <li><strong>Cinética de Reacciones:</strong> Las ecuaciones diferenciales modelan la velocidad de reacciones químicas y la concentración de reactivos y productos en el tiempo.</li>
        <li><strong>Transferencia de Masa:</strong> Los procesos de difusión y convección se describen mediante ecuaciones diferenciales parciales.</li>
        <li><strong>Reactores Químicos:</strong> El diseño y optimización de reactores requiere el modelado matemático de procesos de mezclado y reacción.</li>
    </ul>
    
    <h4>4. Ingeniería Civil</h4>
    <ul>
        <li><strong>Análisis Estructural:</strong> Las ecuaciones diferenciales modelan la respuesta dinámica de estructuras sometidas a cargas variables como sismos y viento.</li>
        <li><strong>Mecánica de Suelos:</strong> El comportamiento de suelos bajo carga se modela mediante ecuaciones diferenciales que consideran la consolidación y la deformación.</li>
        <li><strong>Hidráulica:</strong> El flujo de agua en canales y tuberías se describe mediante ecuaciones diferenciales que consideran la conservación de masa y momentum.</li>
    </ul>
    
    <h3>Aplicaciones Específicas en [TU CARRERA]</h3>
    
    <p><strong>Si estudias Ingeniería Mecánica:</strong></p>
    <ul>
        <li>Modelado de sistemas de suspensión automotriz</li>
        <li>Análisis de vibraciones en máquinas rotativas</li>
        <li>Diseño de sistemas de control de temperatura en motores</li>
        <li>Simulación de procesos de manufactura</li>
    </ul>
    
    <p><strong>Si estudias Ingeniería Eléctrica:</strong></p>
    <ul>
        <li>Diseño de filtros analógicos y digitales</li>
        <li>Análisis de estabilidad en sistemas de potencia</li>
        <li>Modelado de convertidores de energía</li>
        <li>Sistemas de comunicación inalámbrica</li>
    </ul>
    
    <p><strong>Si estudias Ingeniería Química:</strong></p>
    <ul>
        <li>Optimización de procesos de separación</li>
        <li>Control de reactores de polimerización</li>
        <li>Modelado de sistemas de intercambio de calor</li>
        <li>Análisis de procesos de fermentación</li>
    </ul>
    
    <p><strong>Si estudias Ingeniería Civil:</strong></p>
    <ul>
        <li>Análisis sísmico de estructuras</li>
        <li>Modelado de flujo de tráfico</li>
        <li>Diseño de sistemas de drenaje</li>
        <li>Análisis de estabilidad de taludes</li>
    </ul>
    
    <h2>CONCLUSIONES</h2>
    <p>El estudio de las ecuaciones diferenciales representa un pilar fundamental en la formación de cualquier ingeniero, ya que proporciona las herramientas matemáticas necesarias para abordar problemas complejos del mundo real. A través de este análisis, he comprendido que estas ecuaciones no son meros ejercicios académicos, sino herramientas prácticas que permiten modelar, analizar y optimizar sistemas tecnológicos.</p>
    
    <p>La importancia de dominar los diferentes métodos de solución (separación de variables, ecuaciones homogéneas, exactas, lineales, transformada de Laplace, etc.) radica en la versatilidad que proporcionan para abordar diversos tipos de problemas. Cada método tiene su ámbito de aplicación específico, y la elección del método adecuado puede significar la diferencia entre una solución elegante y eficiente o un proceso tedioso y propenso a errores.</p>
    
    <p>En mi carrera específica, las ecuaciones diferenciales me permitirán abordar desafíos técnicos con una perspectiva matemática sólida, facilitando el diseño de soluciones innovadoras y la optimización de procesos existentes. El conocimiento de estas herramientas matemáticas me prepara para enfrentar los retos de la ingeniería moderna, donde la modelación matemática y la simulación computacional son cada vez más importantes.</p>
    
    <p>Finalmente, reconozco que el dominio de las ecuaciones diferenciales no solo es importante para el éxito académico, sino que constituye una competencia profesional esencial que me permitirá contribuir de manera significativa al desarrollo tecnológico y la resolución de problemas de ingeniería en mi campo de especialización.</p>
    
    <h1>PARTE B: EJERCICIOS DE REPASO</h1>
    
    <h2>EJERCICIOS DE MÉTODOS ANTERIORES</h2>
    
    <div class="exercise">
        <h3>Ejercicio 1: Separación de Variables</h3>
        <p><strong>Resolver:</strong> y' = -2^(x-y)</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Separando variables:</p>
            <p>dy/dx = -2^(x-y) = -2^x/2^y</p>
            <p>2^y dy = -2^x dx</p>
            <p>Integrando ambos lados:</p>
            <p>∫ 2^y dy = -∫ 2^x dx</p>
            <p>2^y/ln(2) = -2^x/ln(2) + C</p>
            <p>2^y = -2^x + C ln(2)</p>
            <p><strong>y = log₂(-2^x + C ln(2))</strong></p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 2: Ecuaciones Diferenciales Homogéneas</h3>
        <p><strong>Resolver:</strong> (x² + y²)dx - 2xy dy = 0</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Esta es una ecuación homogénea. Hacemos la sustitución y = vx, entonces dy = v dx + x dv.</p>
            <p>Sustituyendo y resolviendo paso a paso:</p>
            <p><strong>x² - y² = C₁x</strong></p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 3: Ecuaciones Diferenciales Exactas y Factor Integrante</h3>
        <p><strong>Resolver:</strong> (2xy + 3)dx + (x² - 1)dy = 0</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Verificamos que es exacta y resolvemos:</p>
            <p><strong>x²y + 3x - y = C</strong></p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 4: Ecuaciones Diferenciales Lineales de Primer Orden</h3>
        <p><strong>Resolver:</strong> y' + y/x = x²</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Usando factor integrante:</p>
            <p><strong>y = x³/4 + C/x</strong></p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 5: Lineales de Orden Superior Homogéneas</h3>
        <p><strong>Resolver:</strong> y'' - 3y' + 2y = 0</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Ecuación característica: r² - 3r + 2 = 0</p>
            <p>Raíces: r = 1, 2</p>
            <p><strong>y = C₁ e^x + C₂ e^(2x)</strong></p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 6: Lineales de Orden Superior No Homogéneas</h3>
        <p><strong>Resolver:</strong> y'' - 3y' + 2y = 4e^(3x)</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Solución homogénea: y_h = C₁ e^x + C₂ e^(2x)</p>
            <p>Solución particular: y_p = 2e^(3x)</p>
            <p><strong>y = C₁ e^x + C₂ e^(2x) + 2e^(3x)</strong></p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 7: Solución de EDO usando Transformada de Laplace</h3>
        <p><strong>Resolver:</strong> y'' + 4y' + 4y = e^(-2t) con y(0) = 1 e y'(0) = 0</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Aplicando transformada de Laplace y resolviendo:</p>
            <p><strong>y(t) = e^(-2t)(1 + 2t + t²/2)</strong></p>
        </div>
    </div>
    
    <h2>EJERCICIOS ADICIONALES DE ESTA SEMANA</h2>
    
    <div class="exercise">
        <h3>Ejercicio 8: Serie de Fourier</h3>
        <p><strong>Desarrollar en serie de Fourier la función periódica de período 2π dada por:</strong></p>
        <p>f(x) = {0 si -π ≤ x < 0</p>
        <p>       {x si 0 ≤ x < π</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Calculando coeficientes de Fourier:</p>
            <p>a₀ = π/2</p>
            <p>aₙ = ((-1)ⁿ - 1)/(π n²)</p>
            <p>bₙ = (-1)^(n+1)/n</p>
            <p><strong>f(x) = π/4 + Σₙ₌₁^∞ [((-1)ⁿ - 1)/(π n²) cos(nx) + (-1)^(n+1)/n sin(nx)]</strong></p>
            <p><strong>Código para SageMath Cell:</strong></p>
            <code>
f = piecewise([((-pi,0), 0), ((0,pi), x)])
n = 1  # Cambiar este valor de 1 a 10
s = f.fourier_series_partial_sum(n)
plot(f,(-2*pi,2*pi), thickness=3) + plot(s,(x,-2*pi,2*pi), color='red', thickness=1)
            </code>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 9: Ecuación Diferencial con Condiciones Iniciales</h3>
        <p><strong>Resolver:</strong> x''(t) + 4x(t) = f(t) donde x(1) = 0 e x'(1) = n</p>
        <div class="solution">
            <p><strong>Solución:</strong></p>
            <p>Ecuación homogénea: x''(t) + 4x(t) = 0</p>
            <p>Ecuación característica: r² + 4 = 0, entonces r = ±2i</p>
            <p>Solución homogénea: x_h(t) = C₁ cos(2t) + C₂ sin(2t)</p>
            <p>Solución general: x(t) = C₁ cos(2t) + C₂ sin(2t) + x_p(t)</p>
            <p>Aplicando condiciones iniciales se obtienen C₁ y C₂.</p>
        </div>
    </div>
    
    <div class="exercise">
        <h3>Ejercicio 10: Ecuación Diferencial Parcial</h3>
        <p><strong>Verificar que la función dada es solución de la ecuación diferencial parcial:</strong></p>
        <p>∂²u/∂x∂y = x + y³</p>
        <p><strong>Función propuesta:</strong></p>
        <p>u(x,y) = (1/2)x²y + (1/4)xy⁴ - (1/4)y⁴ + 2y² - (9/2)y + x² - 3x - 29</p>
        <div class="solution">
            <p><strong>Verificación:</strong></p>
            <p>∂u/∂x = xy + (1/4)y⁴ + 2x - 3</p>
            <p>∂²u/∂x∂y = x + y³</p>
            <p>Como ∂²u/∂x∂y = x + y³, se verifica que la función propuesta es efectivamente una solución de la ecuación diferencial parcial dada.</p>
        </div>
    </div>
    
    <hr>
    <p style="text-align: center; color: #7f8c8d; font-size: 0.9em;">
        <strong>FIN DEL ENTREGABLE 2</strong><br>
        Ecuaciones Diferenciales - Reporte de Investigación y Ejercicios
    </p>
</body>
</html>
    """
    
    with open("Entregable2_Completo.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("Versión HTML creada: Entregable2_Completo.html")
    return True

if __name__ == "__main__":
    print("Creando versión HTML del documento...")
    create_html_version()
    
    print("\nIntentando convertir Word a PDF...")
    success = convert_word_to_pdf()
    
    if success:
        print("\n✅ Conversión completada exitosamente!")
    else:
        print("\n⚠️ No se pudo convertir a PDF automáticamente.")
        print("Puedes usar el documento Word directamente o abrir el archivo HTML en tu navegador.")
        print("Para convertir manualmente:")
        print("1. Abre el archivo Word con LibreOffice")
        print("2. Ve a Archivo > Exportar como PDF")
        print("3. Guarda como Entregable2_Completo.pdf")

#!/usr/bin/env python3
"""
Generador de Estadísticas Visuales
Genera un archivo HTML con estadísticas visuales del proyecto
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analizar_proyecto_para_visuales(directorio: Path) -> dict:
    """Analiza el proyecto para estadísticas visuales"""
    # Plantillas
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    # Scripts
    scripts = sorted(directorio.glob("*.py"))
    
    # Documentación
    docs = sorted(directorio.glob("*.md"))
    
    # Categorizar plantillas
    categorias = defaultdict(int)
    tamaños = []
    
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        try:
            tamaño = plantilla.stat().st_size
            tamaños.append(tamaño)
        except:
            pass
        
        if any(ind in nombre for ind in ['salud', 'medicina', 'odontologia', 'veterinaria', 'psicologia']):
            categorias['Salud'] += 1
        elif any(ind in nombre for ind in ['educacion', 'investigacion']):
            categorias['Educación'] += 1
        elif any(ind in nombre for ind in ['finanzas', 'contabilidad']):
            categorias['Finanzas'] += 1
        elif any(ind in nombre for ind in ['tecnologia', 'desarrollador', 'ingenieria']):
            categorias['Tecnología'] += 1
        elif any(ind in nombre for ind in ['ventas', 'marketing', 'rrhh']):
            categorias['Negocios'] += 1
        elif any(ind in nombre for ind in ['legal', 'abogacia']):
            categorias['Legal'] += 1
        elif any(ind in nombre for ind in ['diseno', 'arte', 'fotografia', 'musica', 'arquitectura']):
            categorias['Creativo'] += 1
        elif any(ind in nombre for ind in ['consultoria', 'coaching']):
            categorias['Consultoría'] += 1
        elif any(ind in nombre for ind in ['bienes_raices', 'gastronomia', 'turismo', 'fitness']):
            categorias['Servicios'] += 1
        elif any(est in nombre for est in ['navidad', 'verano', 'ano_nuevo']):
            categorias['Estacionales'] += 1
        elif any(emp in nombre for emp in ['startup', 'corporativa']):
            categorias['Empresa'] += 1
        else:
            categorias['General'] += 1
    
    return {
        "plantillas": len(plantillas),
        "scripts": len(scripts),
        "documentacion": len(docs),
        "categorias": dict(categorias),
        "tamaño_promedio": sum(tamaños) / len(tamaños) if tamaños else 0,
        "tamaño_total": sum(tamaños),
        "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generar_html_visuales(analisis: dict) -> str:
    """Genera HTML con estadísticas visuales"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estadísticas Visuales - Firmas de Email</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card h3 {
            color: #667eea;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
            letter-spacing: 1px;
        }
        .stat-card .number {
            font-size: 36px;
            font-weight: 700;
            color: #333;
            margin-bottom: 5px;
        }
        .chart-container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .chart-container h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Estadísticas Visuales - Firmas de Email</h1>
            <p>Análisis completo del proyecto con gráficos interactivos</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Plantillas</h3>
                <div class="number">""" + str(analisis['plantillas']) + """</div>
                <div class="label">Plantillas HTML</div>
            </div>
            
            <div class="stat-card">
                <h3>Scripts</h3>
                <div class="number">""" + str(analisis['scripts']) + """</div>
                <div class="label">Herramientas Python</div>
            </div>
            
            <div class="stat-card">
                <h3>Documentación</h3>
                <div class="number">""" + str(analisis['documentacion']) + """</div>
                <div class="label">Documentos</div>
            </div>
            
            <div class="stat-card">
                <h3>Tamaño Total</h3>
                <div class="number">""" + f"{analisis['tamaño_total'] / 1024:.1f}" + """ KB</div>
                <div class="label">Tamaño del proyecto</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h2>📂 Distribución por Categoría</h2>
            <canvas id="categoriaChart"></canvas>
        </div>
        
        <div class="chart-container">
            <h2>📈 Comparación de Componentes</h2>
            <canvas id="componenteChart"></canvas>
        </div>
    </div>
    
    <script>
        // Gráfico de categorías
        const categoriaCtx = document.getElementById('categoriaChart').getContext('2d');
        const categoriaData = {
            labels: """ + str(list(analisis['categorias'].keys())) + """,
            datasets: [{
                label: 'Plantillas por Categoría',
                data: """ + str(list(analisis['categorias'].values())) + """,
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#4facfe',
                    '#00f2fe', '#43e97b', '#fa709a', '#fee140',
                    '#30cfd0', '#330867', '#ff6b6b', '#4ecdc4'
                ],
                borderWidth: 2
            }]
        };
        new Chart(categoriaCtx, {
            type: 'doughnut',
            data: categoriaData,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            }
        });
        
        // Gráfico de componentes
        const componenteCtx = document.getElementById('componenteChart').getContext('2d');
        const componenteData = {
            labels: ['Plantillas', 'Scripts', 'Documentación'],
            datasets: [{
                label: 'Cantidad',
                data: [""" + str(analisis['plantillas']) + """, """ + str(analisis['scripts']) + """, """ + str(analisis['documentacion']) + """],
                backgroundColor: ['#667eea', '#764ba2', '#f093fb'],
                borderWidth: 2
            }]
        };
        new Chart(componenteCtx, {
            type: 'bar',
            data: componenteData,
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
    
    <div class="footer">
        <p>Estadísticas generadas el """ + analisis['fecha'] + """</p>
        <p>Para regenerar, ejecuta <code>generar_estadisticas_visuales.py</code></p>
    </div>
</body>
</html>
"""
    return html

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Generador de Estadísticas Visuales")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando proyecto...")
    print()
    
    analisis = analizar_proyecto_para_visuales(directorio_actual)
    
    # Generar HTML
    html = generar_html_visuales(analisis)
    
    # Guardar
    archivo_html = directorio_actual / "estadisticas_visuales.html"
    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("=" * 70)
    print("✅ Estadísticas visuales generadas exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_html.name}")
    print()
    print("💡 Abre el archivo en tu navegador para ver los gráficos interactivos")
    print()
    print("📊 Estadísticas:")
    print(f"   - Plantillas: {analisis['plantillas']}")
    print(f"   - Scripts: {analisis['scripts']}")
    print(f"   - Documentación: {analisis['documentacion']}")
    print(f"   - Tamaño total: {analisis['tamaño_total'] / 1024:.1f} KB")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







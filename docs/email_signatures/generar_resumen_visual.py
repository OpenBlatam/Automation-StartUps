#!/usr/bin/env python3
"""
Generador de Resumen Visual
Genera un resumen visual completo del proyecto en formato HTML
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analizar_proyecto_para_resumen(directorio: Path) -> dict:
    """Analiza el proyecto para el resumen visual"""
    # Plantillas
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    # Scripts
    scripts = sorted(directorio.glob("*.py"))
    
    # Documentación
    docs = sorted(directorio.glob("*.md"))
    
    # Herramientas HTML
    herramientas = sorted(directorio.glob("*.html"))
    herramientas = [h for h in herramientas if any(x in h.name.lower() for x in ['generador', 'test', 'preview', 'dashboard', 'estadisticas'])]
    
    # Categorizar
    categorias_plantillas = defaultdict(int)
    categorias_scripts = defaultdict(int)
    
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        if any(ind in nombre for ind in ['salud', 'medicina', 'odontologia', 'veterinaria', 'psicologia', 'farmacia', 'nutricion']):
            categorias_plantillas['Salud'] += 1
        elif any(ind in nombre for ind in ['tecnologia', 'desarrollador', 'ingenieria']):
            categorias_plantillas['Tecnología'] += 1
        elif any(ind in nombre for ind in ['legal', 'abogacia']):
            categorias_plantillas['Legal'] += 1
        elif any(ind in nombre for ind in ['diseno', 'arte', 'fotografia', 'musica', 'arquitectura']):
            categorias_plantillas['Creativo'] += 1
        elif any(ind in nombre for ind in ['ventas', 'marketing', 'rrhh', 'consultoria']):
            categorias_plantillas['Negocios'] += 1
        elif any(est in nombre for est in ['navidad', 'verano', 'ano_nuevo']):
            categorias_plantillas['Estacionales'] += 1
        else:
            categorias_plantillas['General'] += 1
    
    for script in scripts:
        nombre = script.name.lower()
        if 'personalizar' in nombre or 'procesar' in nombre:
            categorias_scripts['Personalización'] += 1
        elif 'validar' in nombre or 'verificar' in nombre:
            categorias_scripts['Validación'] += 1
        elif 'analizar' in nombre or 'estadisticas' in nombre:
            categorias_scripts['Análisis'] += 1
        elif 'generar' in nombre or 'crear' in nombre:
            categorias_scripts['Generación'] += 1
        else:
            categorias_scripts['Utilidades'] += 1
    
    return {
        "plantillas": len(plantillas),
        "scripts": len(scripts),
        "documentacion": len(docs),
        "herramientas": len(herramientas),
        "categorias_plantillas": dict(categorias_plantillas),
        "categorias_scripts": dict(categorias_scripts),
        "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generar_resumen_visual(analisis: dict) -> str:
    """Genera el resumen visual HTML"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resumen Visual - Firmas de Email</title>
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
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }
        .header h1 {
            color: #333;
            font-size: 42px;
            margin-bottom: 10px;
        }
        .header p {
            color: #666;
            font-size: 18px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.2s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
        }
        .stat-card .icon {
            font-size: 48px;
            margin-bottom: 15px;
        }
        .stat-card .number {
            font-size: 42px;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }
        .stat-card .label {
            color: #666;
            font-size: 16px;
        }
        .section {
            background: white;
            border-radius: 12px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            font-size: 28px;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
        }
        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
        }
        .category-card {
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 5px solid #667eea;
        }
        .category-card h3 {
            color: #333;
            font-size: 18px;
            margin-bottom: 10px;
        }
        .category-card .count {
            font-size: 32px;
            font-weight: 700;
            color: #667eea;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 30px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Resumen Visual del Proyecto</h1>
            <p>Firmas de Email Profesionales</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="icon">📧</div>
                <div class="number">""" + str(analisis['plantillas']) + """</div>
                <div class="label">Plantillas HTML</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🐍</div>
                <div class="number">""" + str(analisis['scripts']) + """</div>
                <div class="label">Scripts Python</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">📚</div>
                <div class="number">""" + str(analisis['documentacion']) + """</div>
                <div class="label">Documentos</div>
            </div>
            
            <div class="stat-card">
                <div class="icon">🛠️</div>
                <div class="number">""" + str(analisis['herramientas']) + """</div>
                <div class="label">Herramientas HTML</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📂 Plantillas por Categoría</h2>
            <div class="category-grid">
"""
    
    for categoria, cantidad in sorted(analisis['categorias_plantillas'].items(), key=lambda x: x[1], reverse=True):
        html += f"""
                <div class="category-card">
                    <h3>{categoria}</h3>
                    <div class="count">{cantidad}</div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>🔧 Scripts por Función</h2>
            <div class="category-grid">
"""
    
    for categoria, cantidad in sorted(analisis['categorias_scripts'].items(), key=lambda x: x[1], reverse=True):
        html += f"""
                <div class="category-card">
                    <h3>{categoria}</h3>
                    <div class="count">{cantidad}</div>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>✨ Características Principales</h2>
            <div class="category-grid">
                <div class="category-card">
                    <h3>✅ Compatibilidad</h3>
                    <p>Soporte completo para todos los clientes de email</p>
                </div>
                <div class="category-card">
                    <h3>📱 Responsive</h3>
                    <p>Diseño optimizado para móviles</p>
                </div>
                <div class="category-card">
                    <h3>🎨 Personalización</h3>
                    <p>Herramientas de personalización automática</p>
                </div>
                <div class="category-card">
                    <h3>✅ Validación</h3>
                    <p>Herramientas de validación y testing</p>
                </div>
                <div class="category-card">
                    <h3>📦 Procesamiento</h3>
                    <p>Procesamiento por lotes disponible</p>
                </div>
                <div class="category-card">
                    <h3>🔄 Conversión</h3>
                    <p>Conversión entre múltiples formatos</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Resumen generado el """ + analisis['fecha'] + """</p>
        <p>Para regenerar, ejecuta <code>generar_resumen_visual.py</code></p>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Generador de Resumen Visual")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando proyecto...")
    print()
    
    analisis = analizar_proyecto_para_resumen(directorio_actual)
    
    # Generar HTML
    html = generar_resumen_visual(analisis)
    
    # Guardar
    archivo_html = directorio_actual / "resumen_visual.html"
    with open(archivo_html, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("=" * 70)
    print("✅ Resumen visual generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_html.name}")
    print()
    print("💡 Abre el archivo en tu navegador para ver el resumen visual")
    print()
    print("📊 Estadísticas:")
    print(f"   - Plantillas: {analisis['plantillas']}")
    print(f"   - Scripts: {analisis['scripts']}")
    print(f"   - Documentación: {analisis['documentacion']}")
    print(f"   - Herramientas: {analisis['herramientas']}")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







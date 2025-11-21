#!/usr/bin/env python3
"""
Generador de Dashboard HTML
Genera un dashboard HTML interactivo con todas las estadísticas del proyecto
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analizar_proyecto_para_dashboard(directorio: Path) -> dict:
    """Analiza el proyecto para el dashboard"""
    # Plantillas
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    # Scripts
    scripts = sorted(directorio.glob("*.py"))
    
    # Documentación
    docs = sorted(directorio.glob("*.md"))
    
    # Categorizar plantillas
    categorias = defaultdict(int)
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        if any(ind in nombre for ind in ['salud', 'educacion', 'finanzas', 'tecnologia', 'ventas', 'rrhh', 'marketing', 'legal', 'diseno', 'consultoria', 'medios', 'investigacion', 'coaching', 'bienes_raices', 'gastronomia', 'turismo', 'fitness', 'arte', 'musica', 'fotografia']):
            categorias['Por Industria'] += 1
        elif any(est in nombre for est in ['navidad', 'verano', 'ano_nuevo']):
            categorias['Estacionales'] += 1
        elif any(rol in nombre for rol in ['consultor', 'desarrollador']):
            categorias['Por Rol'] += 1
        elif any(emp in nombre for emp in ['startup', 'corporativa']):
            categorias['Por Empresa'] += 1
        elif any(tem in nombre for tem in ['tema_', 'oscuro', 'azul', 'rojo', 'purpura']):
            categorias['Temáticas'] += 1
        elif any(esp in nombre for esp in ['qr', 'calendario', 'bilingue', 'premium', 'evento']):
            categorias['Especiales'] += 1
        else:
            categorias['Generales'] += 1
    
    # Calcular tamaños
    total_tamaño = 0
    for archivo in plantillas + scripts + docs:
        try:
            total_tamaño += archivo.stat().st_size
        except:
            pass
    
    return {
        "plantillas": len(plantillas),
        "scripts": len(scripts),
        "documentacion": len(docs),
        "categorias": dict(categorias),
        "tamaño_total": total_tamaño,
        "fecha": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def generar_dashboard_html(analisis: dict) -> str:
    """Genera el dashboard HTML"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Firmas de Email</title>
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
            max-width: 1200px;
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
        .header p {
            color: #666;
            font-size: 16px;
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
        .stat-card .label {
            color: #666;
            font-size: 14px;
        }
        .section {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            font-size: 24px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }
        .category-list {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        .category-item {
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        .category-item strong {
            color: #333;
            display: block;
            margin-bottom: 5px;
        }
        .category-item span {
            color: #666;
            font-size: 14px;
        }
        .footer {
            text-align: center;
            color: white;
            padding: 20px;
            font-size: 14px;
        }
        @media (max-width: 768px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard - Firmas de Email</h1>
            <p>Vista general completa del proyecto</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Plantillas</h3>
                <div class="number">""" + str(analisis['plantillas']) + """</div>
                <div class="label">Plantillas HTML disponibles</div>
            </div>
            
            <div class="stat-card">
                <h3>Scripts</h3>
                <div class="number">""" + str(analisis['scripts']) + """</div>
                <div class="label">Herramientas Python</div>
            </div>
            
            <div class="stat-card">
                <h3>Documentación</h3>
                <div class="number">""" + str(analisis['documentacion']) + """</div>
                <div class="label">Documentos de ayuda</div>
            </div>
            
            <div class="stat-card">
                <h3>Tamaño Total</h3>
                <div class="number">""" + f"{analisis['tamaño_total'] / 1024:.1f}" + """ KB</div>
                <div class="label">Tamaño del proyecto</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📂 Distribución por Categoría</h2>
            <div class="category-list">
"""
    
    for categoria, cantidad in sorted(analisis['categorias'].items(), key=lambda x: x[1], reverse=True):
        porcentaje = (cantidad / analisis['plantillas']) * 100 if analisis['plantillas'] > 0 else 0
        html += f"""
                <div class="category-item">
                    <strong>{categoria}</strong>
                    <span>{cantidad} plantillas ({porcentaje:.1f}%)</span>
                </div>
"""
    
    html += """
            </div>
        </div>
        
        <div class="section">
            <h2>🚀 Características Principales</h2>
            <div class="category-list">
                <div class="category-item">
                    <strong>✅ Compatibilidad</strong>
                    <span>Soporte completo para todos los clientes de email</span>
                </div>
                <div class="category-item">
                    <strong>📱 Responsive</strong>
                    <span>Diseño optimizado para móviles</span>
                </div>
                <div class="category-item">
                    <strong>🎨 Personalización</strong>
                    <span>Herramientas de personalización automática</span>
                </div>
                <div class="category-item">
                    <strong>✅ Validación</strong>
                    <span>Herramientas de validación y testing</span>
                </div>
                <div class="category-item">
                    <strong>📦 Procesamiento</strong>
                    <span>Procesamiento por lotes disponible</span>
                </div>
                <div class="category-item">
                    <strong>🔄 Conversión</strong>
                    <span>Conversión entre múltiples formatos</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Dashboard generado el """ + analisis['fecha'] + """</p>
            <p>Para regenerar, ejecuta <code>generar_dashboard.py</code></p>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Generador de Dashboard HTML")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando proyecto...")
    print()
    
    analisis = analizar_proyecto_para_dashboard(directorio_actual)
    
    # Generar dashboard
    dashboard = generar_dashboard_html(analisis)
    
    # Guardar
    archivo_dashboard = directorio_actual / "dashboard.html"
    with open(archivo_dashboard, 'w', encoding='utf-8') as f:
        f.write(dashboard)
    
    print("=" * 70)
    print("✅ Dashboard generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_dashboard.name}")
    print()
    print("💡 Abre el archivo en tu navegador para ver el dashboard interactivo")
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







#!/usr/bin/env python3
"""
Generador de Previews de Firmas
Genera archivos HTML con previews de todas las firmas para visualización
"""

import os
from pathlib import Path
from typing import List
import base64

def leer_plantilla(archivo: str) -> str:
    """Lee el contenido de una plantilla"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def generar_html_preview(plantillas: List[str], archivo_salida: str):
    """Genera un archivo HTML con previews de todas las firmas"""
    html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Preview de Firmas de Email</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f5f5f5;
            padding: 20px;
            line-height: 1.6;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
        }
        .firma-preview {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .firma-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #e8eaed;
        }
        .firma-nombre {
            font-size: 18px;
            font-weight: 600;
            color: #1a73e8;
        }
        .firma-acciones {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary {
            background-color: #1a73e8;
            color: white;
        }
        .btn-primary:hover {
            background-color: #1557b0;
        }
        .btn-secondary {
            background-color: #e8eaed;
            color: #333;
        }
        .btn-secondary:hover {
            background-color: #dadce0;
        }
        .firma-contenido {
            border: 1px solid #e8eaed;
            border-radius: 4px;
            padding: 15px;
            background-color: #fafafa;
            min-height: 200px;
        }
        .firma-contenido iframe {
            width: 100%;
            border: none;
            min-height: 300px;
        }
        .stats {
            display: flex;
            gap: 20px;
            margin-top: 15px;
            font-size: 12px;
            color: #666;
        }
        .stat {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        @media (max-width: 768px) {
            .firma-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 10px;
            }
            .firma-acciones {
                width: 100%;
                flex-direction: column;
            }
            .btn {
                width: 100%;
                text-align: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📧 Preview de Firmas de Email</h1>
"""
    
    for i, plantilla in enumerate(plantillas, 1):
        nombre = Path(plantilla).name
        contenido = leer_plantilla(plantilla)
        
        # Codificar contenido para data URI
        contenido_encoded = base64.b64encode(contenido.encode('utf-8')).decode('utf-8')
        
        # Calcular estadísticas básicas
        tamaño = len(contenido.encode('utf-8'))
        lineas = len(contenido.split('\n'))
        
        html += f"""
        <div class="firma-preview">
            <div class="firma-header">
                <div class="firma-nombre">{i}. {nombre}</div>
                <div class="firma-acciones">
                    <a href="{plantilla}" download class="btn btn-primary">📥 Descargar</a>
                    <a href="{plantilla}" target="_blank" class="btn btn-secondary">👁️ Ver Completo</a>
                </div>
            </div>
            <div class="firma-contenido">
                <iframe srcdoc='{contenido.replace("'", "&#39;")}'></iframe>
            </div>
            <div class="stats">
                <div class="stat">📦 {tamaño:,} bytes</div>
                <div class="stat">📄 {lineas} líneas</div>
            </div>
        </div>
"""
    
    html += """
    </div>
    <script>
        // Auto-ajustar altura de iframes
        document.querySelectorAll('iframe').forEach(iframe => {
            iframe.onload = function() {
                try {
                    const doc = iframe.contentDocument || iframe.contentWindow.document;
                    iframe.style.height = doc.body.scrollHeight + 'px';
                } catch(e) {
                    // Cross-origin, usar altura por defecto
                }
            };
        });
    </script>
</body>
</html>
"""
    
    with open(archivo_salida, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    """Función principal"""
    print("=" * 70)
    print("👁️ Generador de Previews de Firmas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name and "preview" not in p.name]
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    print()
    print("⚡ Generando preview...")
    print()
    
    archivo_salida = directorio_actual / "preview_firmas.html"
    generar_html_preview(plantillas, str(archivo_salida))
    
    print("=" * 70)
    print("✅ Preview generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_salida.name}")
    print(f"📂 Ubicación: {archivo_salida.parent}")
    print()
    print("💡 Abre el archivo en tu navegador para ver todas las firmas")
    print("=" * 70)


if __name__ == "__main__":
    main()







#!/usr/bin/env python3
"""
Generador Automático de DMs para Outreach
Lee datos del CSV y genera DMs personalizados
"""

import csv
import sys
from datetime import datetime
from typing import Dict, Optional

# Templates base (simplificados - usar archivos .md completos para producción)
TEMPLATES = {
    "curso_v1": """¡Felicitaciones por {logro}, {nombre}! 👏
Vi el post y me pregunté: si ya están logrando esto, ¿qué pasaría si potenciaran a su equipo con IA específica para {industria}?
En mis webinars mensuales comparto casos reales de cómo profesionales como {cliente_similar} multiplicaron su productividad 3x en 60 días usando frameworks de IA que enseño en vivo.
¿Te interesaría recibir una invitación exclusiva? Me encantaría saber: ¿en qué proyecto actual visualizas que la IA tendría mayor impacto?""",
    
    "saas_v2": """¡{nombre}! Felicidades por {logro}. Con esos resultados, seguramente están buscando maximizar el retorno de cada dólar invertido en marketing.
Nuestro SaaS de IA optimiza automáticamente tus campañas: identifica los mejores segmentos, personaliza mensajes según comportamiento real y ajusta presupuestos en tiempo real para maximizar conversiones.
¿Actualmente miden el ROI por campaña y segmento, o sienten que hay espacio para optimizar esas métricas?""",
    
    "bulk_v1": """¡{nombre}! Felicidades por {logro}, un logro que demuestra el nivel de ejecución de tu equipo.
Me pregunto: ¿cuántas horas invierten actualmente en crear documentación, reportes o análisis que requieren múltiples fuentes?
He desarrollado una IA que genera documentos completos (informes, análisis, propuestas) con una sola consulta, integrando datos de diferentes fuentes automáticamente.
¿Qué tipo de documentos o reportes les tomaría más valor crear de forma instantánea?"""
}

def generar_utm(producto: str, version: str, industria: str, fuente: str = "linkedin", medio: str = "dm") -> str:
    """Genera URL con UTM parameters"""
    base_url = "https://tusitio.com"  # Cambiar por tu URL real
    campana_map = {
        "curso": "curso-ia",
        "saas": "saas-ia-marketing",
        "bulk": "ia-bulk-docs"
    }
    version_map = {
        "v1": "v1-equipo" if producto == "curso" else "v1-escalabilidad" if producto == "saas" else "v1-tiempo",
        "v2": "v2-competitividad" if producto == "curso" else "v2-roi",
        # Agregar más mapeos según necesidad
    }
    
    campana = campana_map.get(producto, "outreach")
    contenido = version_map.get(version, "general")
    industria_slug = industria.lower().replace(" ", "-")
    
    utm = f"{base_url}?utm_source={fuente}&utm_medium={medio}&utm_campaign={campana}&utm_content={contenido}&utm_term={industria_slug}"
    return utm

def generar_dm(row: Dict[str, str]) -> Optional[str]:
    """Genera DM personalizado desde fila del CSV"""
    nombre = row.get('first_name', '') or row.get('full_name', 'Contacto')
    logro = row.get('achievement', '[LOGRO]')
    industria = row.get('industry', '[INDUSTRIA]')
    producto = row.get('product', 'curso')
    version = row.get('dm_version', 'v1')
    cliente_similar = row.get('cliente_similar', '[CLIENTE_SIMILAR]')
    
    # Seleccionar template
    template_key = f"{producto}_{version}"
    if template_key not in TEMPLATES:
        template_key = f"{producto}_v1"  # Fallback
    
    template = TEMPLATES.get(template_key)
    if not template:
        return None
    
    # Reemplazar variables
    dm = template.format(
        nombre=nombre,
        logro=logro,
        industria=industria,
        cliente_similar=cliente_similar
    )
    
    # Generar UTM si hay final_url
    if row.get('final_url'):
        utm_url = generar_utm(producto, version, industria)
        dm += f"\n\n🔗 Link: {utm_url}"
    
    return dm

def leer_csv_y_generar(archivo_csv: str, output_file: Optional[str] = None):
    """Lee CSV y genera DMs para cada fila"""
    dms_generados = []
    
    try:
        with open(archivo_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                nombre = row.get('full_name') or row.get('first_name', f'Lead {idx}')
                print(f"\n{'='*60}")
                print(f"Generando DM para: {nombre}")
                print(f"{'='*60}")
                
                dm = generar_dm(row)
                if dm:
                    dms_generados.append({
                        'nombre': nombre,
                        'email': row.get('email', ''),
                        'dm': dm
                    })
                    print(dm)
                    print(f"\n---")
                else:
                    print(f"⚠️  No se pudo generar DM (template no encontrado)")
    
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo {archivo_csv}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    # Guardar en archivo si se especifica
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# DMs Generados Automáticamente\n\n")
            f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            for item in dms_generados:
                f.write(f"## {item['nombre']}\n")
                f.write(f"Email: {item['email']}\n\n")
                f.write(f"{item['dm']}\n\n")
                f.write("---\n\n")
        print(f"\n✅ DMs guardados en: {output_file}")
    
    return dms_generados

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python SCRIPT_GENERADOR_DM.py <archivo.csv> [output.md]")
        print("\nEjemplo: python SCRIPT_GENERADOR_DM.py SAMPLE_LEADS_OUTREACH.csv dms_generados.md")
        sys.exit(1)
    
    archivo_csv = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    leer_csv_y_generar(archivo_csv, output_file)


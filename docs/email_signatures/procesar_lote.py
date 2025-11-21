#!/usr/bin/env python3
"""
Procesador por Lote de Firmas de Email
Procesa múltiples plantillas y genera firmas personalizadas en lote
"""

import os
import json
from pathlib import Path
from typing import Dict, List
import re

# Configuraciones para múltiples usuarios
CONFIGURACIONES = [
    {
        "nombre": "usuario_1",
        "config": {
            "nombre": "Juan Pérez",
            "cargo": "Instructor de IA",
            "email": "juan@ejemplo.com",
            "telefono": "+34 600 123 456",
            "website": "https://www.juanperez.com",
            "url_curso": "https://www.juanperez.com/curso",
            "url_webinar": "https://www.juanperez.com/webinar",
            "url_linkedin": "https://linkedin.com/in/juanperez",
            "url_twitter": "https://twitter.com/juanperez",
        }
    },
    {
        "nombre": "usuario_2",
        "config": {
            "nombre": "María García",
            "cargo": "Consultora Senior",
            "email": "maria@ejemplo.com",
            "telefono": "+34 600 654 321",
            "website": "https://www.mariagarcia.com",
            "url_consulta": "https://www.mariagarcia.com/consulta",
            "url_linkedin": "https://linkedin.com/in/mariagarcia",
        }
    },
    # Agrega más configuraciones aquí
]

PLACEHOLDERS = {
    "[Tu Nombre]": "nombre",
    "[Tu Cargo]": "cargo",
    "[tu-email@ejemplo.com]": "email",
    "[+1 234 567 890]": "telefono",
    "[URL_WEBSITE]": "website",
    "[www.tuwebsite.com]": "website",
    "[URL_CURSO]": "url_curso",
    "[URL_WEBINAR]": "url_webinar",
    "[URL_CONSULTA]": "url_consulta",
    "[URL_LINKEDIN]": "url_linkedin",
    "[URL_TWITTER]": "url_twitter",
    "[URL_GITHUB]": "url_github",
    "[URL_YOUTUBE]": "url_youtube",
    "[URL_FACEBOOK]": "url_facebook",
    "[URL_UNSUBSCRIBE]": "url_unsubscribe",
    "[Fecha]": "fecha_webinar",
    "[Tu Empresa/Organización]": "empresa",
}


def procesar_plantilla(archivo_entrada: str, archivo_salida: str, config: Dict[str, str]) -> tuple[bool, str]:
    """Procesa una plantilla con una configuración"""
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        reemplazos = 0
        for placeholder, clave_config in PLACEHOLDERS.items():
            if clave_config in config:
                valor = config[clave_config]
                if placeholder in contenido:
                    contenido = contenido.replace(placeholder, valor)
                    reemplazos += 1
        
        # Extraer dominio del website para www.tuwebsite.com
        if "website" in config and config["website"]:
            website = config["website"]
            dominio = website.replace("https://", "").replace("http://", "").replace("www.", "")
            contenido = contenido.replace("[www.tuwebsite.com]", dominio)
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return True, f"✅ {Path(archivo_entrada).name} → {Path(archivo_salida).name} ({reemplazos} reemplazos)"
    
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def procesar_lote(plantillas: List[str], configuraciones: List[Dict], directorio_salida: str):
    """Procesa múltiples plantillas con múltiples configuraciones"""
    resultados = {
        "exitosos": 0,
        "fallidos": 0,
        "total": 0
    }
    
    print(f"🔄 Procesando {len(plantillas)} plantillas para {len(configuraciones)} usuarios...\n")
    
    for usuario in configuraciones:
        nombre_usuario = usuario["nombre"]
        config = usuario["config"]
        
        print(f"👤 Procesando: {nombre_usuario}")
        print("-" * 60)
        
        for plantilla in plantillas:
            nombre_plantilla = Path(plantilla).stem
            archivo_salida = os.path.join(
                directorio_salida,
                nombre_usuario,
                f"{nombre_plantilla}_personalizada.html"
            )
            
            success, mensaje = procesar_plantilla(plantilla, archivo_salida, config)
            print(f"   {mensaje}")
            
            resultados["total"] += 1
            if success:
                resultados["exitosos"] += 1
            else:
                resultados["fallidos"] += 1
        
        print()
    
    return resultados


def cargar_configuraciones_desde_json(archivo: str) -> List[Dict]:
    """Carga configuraciones desde un archivo JSON"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return [{"nombre": f"usuario_{i+1}", "config": item} for i, item in enumerate(data)]
        elif isinstance(data, dict):
            return [{"nombre": "usuario_1", "config": data}]
        else:
            return []
    except FileNotFoundError:
        print(f"⚠️  Archivo {archivo} no encontrado, usando configuraciones por defecto")
        return CONFIGURACIONES
    except json.JSONDecodeError:
        print(f"❌ Error al leer JSON, usando configuraciones por defecto")
        return CONFIGURACIONES


def main():
    """Función principal"""
    print("=" * 70)
    print("📦 Procesador por Lote de Firmas de Email")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Buscar plantillas
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    
    if not plantillas:
        print("❌ No se encontraron plantillas")
        return
    
    # Filtrar solo plantillas principales (no personalizadas)
    plantillas = [str(p) for p in plantillas if "personalizada" not in p.name]
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    for i, plantilla in enumerate(plantillas[:5], 1):
        print(f"   {i}. {Path(plantilla).name}")
    if len(plantillas) > 5:
        print(f"   ... y {len(plantillas) - 5} más")
    print()
    
    # Cargar configuraciones
    config_json = directorio_actual / "configuraciones_lote.json"
    if config_json.exists():
        print(f"📂 Cargando configuraciones desde {config_json.name}...")
        configuraciones = cargar_configuraciones_desde_json(str(config_json))
    else:
        print("📝 Usando configuraciones por defecto")
        print("💡 Crea 'configuraciones_lote.json' para personalizar")
        configuraciones = CONFIGURACIONES
    
    print(f"👥 Configuraciones: {len(configuraciones)}")
    print()
    
    # Directorio de salida
    directorio_salida = directorio_actual / "lote_personalizadas"
    directorio_salida.mkdir(exist_ok=True)
    
    # Procesar
    resultados = procesar_lote(plantillas, configuraciones, str(directorio_salida))
    
    # Resumen
    print("=" * 70)
    print("📊 Resumen")
    print("=" * 70)
    print(f"✅ Exitosos: {resultados['exitosos']}")
    print(f"❌ Fallidos: {resultados['fallidos']}")
    print(f"📁 Total procesados: {resultados['total']}")
    print(f"📂 Archivos guardados en: {directorio_salida}")
    print()
    print("💡 Estructura de salida:")
    print("   lote_personalizadas/")
    for usuario in configuraciones:
        print(f"   ├── {usuario['nombre']}/")
        print(f"   │   └── [plantillas personalizadas]")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()







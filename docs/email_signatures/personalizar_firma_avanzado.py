#!/usr/bin/env python3
"""
Script Avanzado de Personalización de Firmas de Email
Incluye validación, preview, y múltiples opciones de exportación
"""

import re
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Configuración por defecto
CONFIG = {
    "nombre": "Tu Nombre",
    "cargo": "Tu Cargo",
    "email": "tu-email@ejemplo.com",
    "telefono": "+1 234 567 890",
    "website": "https://www.tuwebsite.com",
    "empresa": "Tu Empresa/Organización",
    "url_curso": "https://www.tuwebsite.com/curso",
    "url_webinar": "https://www.tuwebsite.com/webinar",
    "url_demo": "https://www.tuwebsite.com/demo",
    "url_pricing": "https://www.tuwebsite.com/precios",
    "url_try_now": "https://www.tuwebsite.com/probar",
    "url_examples": "https://www.tuwebsite.com/ejemplos",
    "url_linkedin": "https://www.linkedin.com/in/tu-perfil",
    "url_twitter": "https://twitter.com/tu-usuario",
    "url_youtube": "https://www.youtube.com/c/tu-canal",
    "url_facebook": "https://www.facebook.com/tu-pagina",
    "url_github": "https://github.com/tu-usuario",
    "url_unsubscribe": "https://www.tuwebsite.com/unsubscribe",
    "fecha_webinar": "Próximamente",
    "nombre_saas": "Nombre del SaaS",
    "nombre_producto": "Nombre del Producto",
    "nombre_cliente": "Nombre Cliente",
    "empresa_cliente": "Empresa",
}

PLACEHOLDERS = {
    "[Tu Nombre]": "nombre",
    "[Tu Cargo]": "cargo",
    "[tu-email@ejemplo.com]": "email",
    "[+1234567890]": "telefono",
    "[+1 234 567 890]": "telefono",
    "[URL_WEBSITE]": "website",
    "[www.tuwebsite.com]": "website",
    "[Tu Empresa/Organización]": "empresa",
    "[URL_CURSO]": "url_curso",
    "[URL_WEBINAR]": "url_webinar",
    "[Fecha]": "fecha_webinar",
    "[URL_DEMO]": "url_demo",
    "[URL_PRICING]": "url_pricing",
    "[URL_TRY_NOW]": "url_try_now",
    "[URL_EXAMPLES]": "url_examples",
    "[URL_LINKEDIN]": "url_linkedin",
    "[URL_TWITTER]": "url_twitter",
    "[URL_YOUTUBE]": "url_youtube",
    "[URL_FACEBOOK]": "url_facebook",
    "[URL_GITHUB]": "url_github",
    "[URL_UNSUBSCRIBE]": "url_unsubscribe",
    "[Nombre del SaaS]": "nombre_saas",
    "[Nombre del Producto]": "nombre_producto",
    "[Nombre Cliente]": "nombre_cliente",
    "[Empresa]": "empresa_cliente",
}


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validar_url(url: str) -> bool:
    """Valida formato de URL"""
    pattern = r'^https?://.+'
    return bool(re.match(pattern, url))


def validar_config(config: Dict[str, str]) -> List[str]:
    """Valida la configuración y retorna lista de errores"""
    errores = []
    
    if not config.get("nombre") or config["nombre"] == "Tu Nombre":
        errores.append("⚠️  Nombre no configurado")
    
    if not validar_email(config.get("email", "")):
        errores.append("⚠️  Email inválido")
    
    if config.get("website") and not validar_url(config["website"]):
        errores.append("⚠️  Website debe comenzar con http:// o https://")
    
    return errores


def personalizar_archivo(archivo_entrada: str, archivo_salida: str, config: Dict[str, str]) -> tuple[bool, str]:
    """
    Personaliza un archivo HTML reemplazando los placeholders
    
    Returns:
        (success: bool, message: str)
    """
    try:
        if not os.path.exists(archivo_entrada):
            return False, f"❌ Archivo no encontrado: {archivo_entrada}"
        
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Contar placeholders antes de reemplazar
        placeholders_encontrados = []
        for placeholder in PLACEHOLDERS.keys():
            if placeholder in contenido:
                placeholders_encontrados.append(placeholder)
        
        # Reemplazar todos los placeholders
        reemplazos_realizados = 0
        for placeholder, clave_config in PLACEHOLDERS.items():
            if clave_config in config:
                valor = config[clave_config]
                if placeholder in contenido:
                    contenido = contenido.replace(placeholder, valor)
                    reemplazos_realizados += 1
        
        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar archivo personalizado
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        mensaje = f"✅ {Path(archivo_entrada).name} → {Path(archivo_salida).name} ({reemplazos_realizados} reemplazos)"
        return True, mensaje
    
    except Exception as e:
        return False, f"❌ Error: {str(e)}"


def listar_plantillas(directorio: str = ".") -> Dict[str, List[str]]:
    """Lista todas las plantillas disponibles organizadas por tipo"""
    plantillas = {
        "completas": [],
        "compactas": [],
        "simplificadas": [],
        "minimalistas": [],
        "texto": []
    }
    
    for archivo in Path(directorio).glob("firma_*.html"):
        nombre = archivo.name
        if "compacta" in nombre:
            plantillas["compactas"].append(str(archivo))
        elif "simple" in nombre:
            plantillas["simplificadas"].append(str(archivo))
        elif "minimalista" in nombre:
            plantillas["minimalistas"].append(str(archivo))
        elif "curso" in nombre or "saas" in nombre or "bulk" in nombre:
            if "compacta" not in nombre and "simple" not in nombre and "minimalista" not in nombre:
                plantillas["completas"].append(str(archivo))
    
    for archivo in Path(directorio).glob("firma_*.txt"):
        plantillas["texto"].append(str(archivo))
    
    return plantillas


def generar_preview_html(archivo: str, config: Dict[str, str]) -> str:
    """Genera un preview HTML del archivo personalizado"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        for placeholder, clave_config in PLACEHOLDERS.items():
            if clave_config in config:
                contenido = contenido.replace(placeholder, config[clave_config])
        
        return contenido
    except Exception as e:
        return f"<p style='color: red;'>Error: {e}</p>"


def exportar_config_json(config: Dict[str, str], archivo: str):
    """Exporta la configuración a JSON"""
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


def cargar_config_json(archivo: str) -> Dict[str, str]:
    """Carga la configuración desde JSON"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        print(f"⚠️  Error al leer {archivo}, usando configuración por defecto")
        return {}


def main():
    """Función principal"""
    print("=" * 70)
    print("🚀 Personalizador Avanzado de Firmas de Email v2.0")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    # Cargar configuración guardada si existe
    config_file = directorio_actual / "config.json"
    if config_file.exists():
        print(f"📂 Cargando configuración desde {config_file.name}...")
        config_guardada = cargar_config_json(str(config_file))
        CONFIG.update(config_guardada)
        print("✅ Configuración cargada\n")
    
    # Validar configuración
    print("🔍 Validando configuración...")
    errores = validar_config(CONFIG)
    if errores:
        print("\n".join(errores))
        print("\n💡 Edita el script para corregir estos problemas\n")
    else:
        print("✅ Configuración válida\n")
    
    # Listar plantillas
    plantillas = listar_plantillas(str(directorio_actual))
    
    total = sum(len(v) for v in plantillas.values())
    if total == 0:
        print("❌ No se encontraron plantillas")
        return
    
    print(f"📋 Plantillas encontradas: {total}")
    for tipo, archivos in plantillas.items():
        if archivos:
            print(f"   • {tipo.capitalize()}: {len(archivos)}")
    print()
    
    # Crear directorio de salida
    directorio_salida = directorio_actual / "personalizadas"
    directorio_salida.mkdir(exist_ok=True)
    
    # Procesar todas las plantillas HTML
    print("🔄 Procesando plantillas HTML...")
    print()
    
    exitosos = 0
    fallidos = 0
    
    for tipo, archivos in plantillas.items():
        if tipo == "texto":
            continue  # Procesar texto por separado
        
        for plantilla in archivos:
            nombre_archivo = Path(plantilla).name
            archivo_salida = directorio_salida / nombre_archivo.replace(".html", "_personalizada.html")
            
            success, mensaje = personalizar_archivo(plantilla, str(archivo_salida), CONFIG)
            print(mensaje)
            
            if success:
                exitosos += 1
            else:
                fallidos += 1
    
    # Procesar archivos de texto
    print("\n📄 Procesando archivos de texto...")
    for plantilla in plantillas["texto"]:
        nombre_archivo = Path(plantilla).name
        archivo_salida = directorio_salida / nombre_archivo.replace(".txt", "_personalizada.txt")
        
        success, mensaje = personalizar_archivo(plantilla, str(archivo_salida), CONFIG)
        print(mensaje)
        
        if success:
            exitosos += 1
        else:
            fallidos += 1
    
    # Exportar configuración
    config_export = directorio_salida / "config_exportada.json"
    exportar_config_json(CONFIG, str(config_export))
    print(f"\n💾 Configuración exportada a: {config_export.name}")
    
    # Resumen
    print()
    print("=" * 70)
    print(f"✅ Proceso completado")
    print(f"   • Exitosos: {exitosos}")
    print(f"   • Fallidos: {fallidos}")
    print(f"   • Archivos guardados en: {directorio_salida}")
    print()
    print("📝 Próximos pasos:")
    print("   1. Revisa los archivos en la carpeta 'personalizadas/'")
    print("   2. Abre los HTML en un navegador para previsualizar")
    print("   3. Copia el contenido a tu cliente de email")
    print("   4. Prueba en diferentes dispositivos y clientes")
    print("=" * 70)


if __name__ == "__main__":
    main()







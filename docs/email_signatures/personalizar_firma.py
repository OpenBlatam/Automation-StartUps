#!/usr/bin/env python3
"""
Script de Personalización Automática de Firmas de Email
Permite personalizar las plantillas HTML reemplazando placeholders automáticamente
"""

import re
import os
from pathlib import Path
from typing import Dict, List

# Configuración por defecto - Personaliza estos valores
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

# Mapeo de placeholders a valores de configuración
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


def personalizar_archivo(archivo_entrada: str, archivo_salida: str, config: Dict[str, str]) -> bool:
    """
    Personaliza un archivo HTML reemplazando los placeholders con valores de configuración
    
    Args:
        archivo_entrada: Ruta al archivo de plantilla
        archivo_salida: Ruta donde guardar el archivo personalizado
        config: Diccionario con la configuración
    
    Returns:
        True si se procesó correctamente, False en caso contrario
    """
    try:
        with open(archivo_entrada, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Reemplazar todos los placeholders
        for placeholder, clave_config in PLACEHOLDERS.items():
            if clave_config in config:
                valor = config[clave_config]
                contenido = contenido.replace(placeholder, valor)
        
        # Crear directorio de salida si no existe
        os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)
        
        # Guardar archivo personalizado
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"✅ Personalizado: {archivo_entrada} → {archivo_salida}")
        return True
    
    except Exception as e:
        print(f"❌ Error procesando {archivo_entrada}: {e}")
        return False


def listar_plantillas(directorio: str = ".") -> List[str]:
    """Lista todas las plantillas HTML disponibles"""
    plantillas = []
    for archivo in Path(directorio).glob("firma_*.html"):
        if "simple" not in archivo.name and "compacta" not in archivo.name:
            plantillas.append(str(archivo))
    return sorted(plantillas)


def main():
    """Función principal"""
    print("=" * 60)
    print("Personalizador de Firmas de Email")
    print("=" * 60)
    print()
    
    # Obtener directorio actual
    directorio_actual = Path(__file__).parent
    
    # Listar plantillas disponibles
    plantillas = listar_plantillas(str(directorio_actual))
    
    if not plantillas:
        print("❌ No se encontraron plantillas en el directorio actual")
        return
    
    print(f"📋 Plantillas encontradas: {len(plantillas)}")
    for i, plantilla in enumerate(plantillas, 1):
        print(f"   {i}. {Path(plantilla).name}")
    print()
    
    # Crear directorio de salida
    directorio_salida = directorio_actual / "personalizadas"
    directorio_salida.mkdir(exist_ok=True)
    
    # Procesar cada plantilla
    print("🔄 Procesando plantillas...")
    print()
    
    for plantilla in plantillas:
        nombre_archivo = Path(plantilla).name
        archivo_salida = directorio_salida / nombre_archivo.replace(".html", "_personalizada.html")
        personalizar_archivo(plantilla, str(archivo_salida), CONFIG)
    
    print()
    print("=" * 60)
    print(f"✅ Proceso completado. Archivos guardados en: {directorio_salida}")
    print()
    print("📝 Próximos pasos:")
    print("   1. Revisa los archivos personalizados")
    print("   2. Ajusta la configuración en este script si es necesario")
    print("   3. Copia el contenido HTML a tu cliente de email")
    print("=" * 60)


if __name__ == "__main__":
    main()







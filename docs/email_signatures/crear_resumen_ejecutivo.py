#!/usr/bin/env python3
"""
Creador de Resumen Ejecutivo
Genera un resumen ejecutivo del proyecto en formato markdown
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def contar_por_tipo(directorio: Path) -> dict:
    """Cuenta archivos por tipo"""
    tipos = defaultdict(int)
    
    for archivo in directorio.iterdir():
        if archivo.is_file():
            extension = archivo.suffix.lower()
            if extension:
                tipos[extension] += 1
            else:
                tipos['sin_extension'] += 1
    
    return dict(tipos)

def analizar_plantillas(directorio: Path) -> dict:
    """Analiza las plantillas disponibles"""
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    # Categorizar
    categorias = defaultdict(int)
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        if 'salud' in nombre or 'medicina' in nombre:
            categorias['Salud'] += 1
        elif 'educacion' in nombre or 'educación' in nombre:
            categorias['Educación'] += 1
        elif 'finanzas' in nombre:
            categorias['Finanzas'] += 1
        elif 'tecnologia' in nombre or 'tecnología' in nombre:
            categorias['Tecnología'] += 1
        elif 'ventas' in nombre:
            categorias['Ventas'] += 1
        elif 'rrhh' in nombre or 'recursos_humanos' in nombre:
            categorias['RRHH'] += 1
        elif 'marketing' in nombre:
            categorias['Marketing'] += 1
        elif 'legal' in nombre:
            categorias['Legal'] += 1
        elif 'diseno' in nombre or 'diseño' in nombre:
            categorias['Diseño'] += 1
        elif 'consultoria' in nombre or 'consultoría' in nombre:
            categorias['Consultoría'] += 1
        elif 'medios' in nombre:
            categorias['Medios'] += 1
        elif 'investigacion' in nombre or 'investigación' in nombre:
            categorias['Investigación'] += 1
        elif 'navidad' in nombre or 'verano' in nombre or 'ano_nuevo' in nombre:
            categorias['Estacionales'] += 1
        elif 'startup' in nombre or 'corporativa' in nombre:
            categorias['Empresas'] += 1
        else:
            categorias['Generales'] += 1
    
    return {
        "total": len(plantillas),
        "categorias": dict(categorias)
    }

def generar_resumen_ejecutivo(directorio: Path) -> str:
    """Genera el resumen ejecutivo"""
    resumen = "# 📊 Resumen Ejecutivo - Firmas de Email\n\n"
    resumen += f"**Fecha:** {datetime.now().strftime('%d de %B de %Y')}\n\n"
    
    resumen += "## 🎯 Visión General\n\n"
    resumen += "Este proyecto proporciona una solución completa para la creación, personalización y gestión de firmas de email profesionales.\n\n"
    
    # Estadísticas de plantillas
    analisis_plantillas = analizar_plantillas(directorio)
    resumen += "## 📧 Plantillas Disponibles\n\n"
    resumen += f"**Total de plantillas:** {analisis_plantillas['total']}\n\n"
    
    resumen += "### Por Categoría:\n\n"
    for categoria, cantidad in sorted(analisis_plantillas['categorias'].items()):
        resumen += f"- **{categoria}:** {cantidad} plantilla(s)\n"
    
    resumen += "\n"
    
    # Herramientas
    scripts = sorted(directorio.glob("*.py"))
    herramientas_html = sorted(directorio.glob("*.html"))
    herramientas_html = [h for h in herramientas_html if any(x in h.name for x in ['generador', 'test', 'preview'])]
    docs = sorted(directorio.glob("*.md"))
    
    resumen += "## 🛠️ Herramientas Disponibles\n\n"
    resumen += f"- **Scripts Python:** {len(scripts)} herramientas\n"
    resumen += f"- **Herramientas HTML:** {len(herramientas_html)} herramientas\n"
    resumen += f"- **Documentación:** {len(docs)} documentos\n\n"
    
    # Archivos por tipo
    tipos = contar_por_tipo(directorio)
    resumen += "## 📁 Distribución de Archivos\n\n"
    for tipo, cantidad in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        nombre_tipo = tipo.replace('.', '').upper() if tipo != 'sin_extension' else 'Sin extensión'
        resumen += f"- **{nombre_tipo}:** {cantidad} archivo(s)\n"
    
    resumen += "\n"
    
    # Características principales
    resumen += "## ✨ Características Principales\n\n"
    resumen += "### Compatibilidad\n"
    resumen += "- ✅ Soporte completo para Outlook (VML/MSO)\n"
    resumen += "- ✅ Diseño responsive para móviles\n"
    resumen += "- ✅ Compatible con todos los clientes de email principales\n\n"
    
    resumen += "### Funcionalidades\n"
    resumen += "- 🎨 Múltiples estilos y temas\n"
    resumen += "- 🏢 Plantillas por industria y rol\n"
    resumen += "- 🎯 Herramientas de personalización automática\n"
    resumen += "- ✅ Validación y análisis de calidad\n"
    resumen += "- 📦 Procesamiento por lotes\n"
    resumen += "- 🔄 Conversión entre formatos\n\n"
    
    # Casos de uso
    resumen += "## 💼 Casos de Uso\n\n"
    resumen += "1. **Uso Individual:** Personalización rápida de firma personal\n"
    resumen += "2. **Equipos Pequeños:** Procesamiento por lotes para equipos\n"
    resumen += "3. **Empresas:** Estándares corporativos y branding\n"
    resumen += "4. **Agencias:** Creación de firmas para clientes\n\n"
    
    # Próximos pasos
    resumen += "## 🚀 Próximos Pasos\n\n"
    resumen += "1. Seleccionar una plantilla base\n"
    resumen += "2. Personalizar con `personalizar_firma.py`\n"
    resumen += "3. Validar con `validar_firma.py`\n"
    resumen += "4. Probar en diferentes clientes de email\n"
    resumen += "5. Implementar en tu cliente de email\n\n"
    
    resumen += "---\n\n"
    resumen += f"*Resumen generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return resumen

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Creador de Resumen Ejecutivo")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando proyecto...")
    print()
    
    resumen = generar_resumen_ejecutivo(directorio_actual)
    
    # Guardar
    archivo_resumen = directorio_actual / "RESUMEN_EJECUTIVO.md"
    with open(archivo_resumen, 'w', encoding='utf-8') as f:
        f.write(resumen)
    
    print("=" * 70)
    print("✅ Resumen ejecutivo generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_resumen.name}")
    print()
    print("💡 El resumen incluye:")
    print("   - Visión general del proyecto")
    print("   - Estadísticas de plantillas")
    print("   - Herramientas disponibles")
    print("   - Características principales")
    print("   - Casos de uso")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







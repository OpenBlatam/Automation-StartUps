#!/usr/bin/env python3
"""
Generador de Reporte Completo
Genera un reporte completo del proyecto con todas las métricas y análisis
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def analizar_proyecto_completo(directorio: Path) -> dict:
    """Analiza el proyecto completo"""
    # Plantillas
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    # Scripts
    scripts = sorted(directorio.glob("*.py"))
    
    # Documentación
    docs = sorted(directorio.glob("*.md"))
    
    # Herramientas HTML
    herramientas_html = sorted(directorio.glob("*.html"))
    herramientas_html = [h for h in herramientas_html if any(x in h.name for x in ['generador', 'test', 'preview'])]
    
    # Estadísticas de tamaño
    total_tamaño = 0
    total_lineas = 0
    
    for archivo in plantillas + scripts + docs:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                total_tamaño += len(contenido.encode('utf-8'))
                total_lineas += len(contenido.split('\n'))
        except:
            pass
    
    # Categorizar plantillas
    categorias = defaultdict(int)
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        if any(ind in nombre for ind in ['salud', 'educacion', 'finanzas', 'tecnologia', 'ventas', 'rrhh', 'marketing', 'legal', 'diseno', 'consultoria', 'medios', 'investigacion', 'coaching', 'bienes_raices', 'gastronomia', 'turismo']):
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
    
    return {
        "plantillas": {
            "total": len(plantillas),
            "categorias": dict(categorias)
        },
        "scripts": len(scripts),
        "documentacion": len(docs),
        "herramientas_html": len(herramientas_html),
        "tamaño_total": total_tamaño,
        "lineas_totales": total_lineas,
        "fecha_analisis": datetime.now().isoformat()
    }

def generar_reporte_completo(analisis: dict) -> str:
    """Genera el reporte completo"""
    reporte = "# 📊 Reporte Completo del Proyecto - Firmas de Email\n\n"
    reporte += f"**Fecha de generación:** {datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')}\n\n"
    
    reporte += "## 📈 Resumen Ejecutivo\n\n"
    reporte += f"Este proyecto contiene **{analisis['plantillas']['total']} plantillas HTML** profesionales para firmas de email, "
    reporte += f"**{analisis['scripts']} scripts Python** de automatización, "
    reporte += f"**{analisis['documentacion']} documentos** de ayuda, y "
    reporte += f"**{analisis['herramientas_html']} herramientas HTML** interactivas.\n\n"
    
    reporte += "## 📧 Plantillas Disponibles\n\n"
    reporte += f"**Total:** {analisis['plantillas']['total']} plantillas\n\n"
    
    reporte += "### Distribución por Categoría:\n\n"
    for categoria, cantidad in sorted(analisis['plantillas']['categorias'].items(), key=lambda x: x[1], reverse=True):
        porcentaje = (cantidad / analisis['plantillas']['total']) * 100
        reporte += f"- **{categoria}:** {cantidad} plantillas ({porcentaje:.1f}%)\n"
    
    reporte += "\n"
    
    reporte += "## 🛠️ Herramientas y Scripts\n\n"
    reporte += f"- **Scripts Python:** {analisis['scripts']} herramientas\n"
    reporte += f"- **Herramientas HTML:** {analisis['herramientas_html']} herramientas\n"
    reporte += f"- **Documentación:** {analisis['documentacion']} documentos\n\n"
    
    reporte += "## 📊 Estadísticas de Código\n\n"
    reporte += f"- **Tamaño total:** {analisis['tamaño_total']:,} bytes ({analisis['tamaño_total'] / 1024:.1f} KB)\n"
    reporte += f"- **Líneas totales:** {analisis['lineas_totales']:,} líneas\n"
    reporte += f"- **Tamaño promedio por archivo:** {analisis['tamaño_total'] // (analisis['plantillas']['total'] + analisis['scripts']):,} bytes\n\n"
    
    reporte += "## ✨ Características Principales\n\n"
    reporte += "### Compatibilidad\n"
    reporte += "- ✅ Soporte completo para Outlook (VML/MSO)\n"
    reporte += "- ✅ Diseño responsive para móviles\n"
    reporte += "- ✅ Compatible con Gmail, Apple Mail, Yahoo Mail\n"
    reporte += "- ✅ Validación y testing automatizado\n\n"
    
    reporte += "### Funcionalidades\n"
    reporte += "- 🎨 Múltiples estilos y temas\n"
    reporte += "- 🏢 Plantillas por industria y rol\n"
    reporte += "- 🎯 Personalización automática\n"
    reporte += "- ✅ Validación y análisis de calidad\n"
    reporte += "- 📦 Procesamiento por lotes\n"
    reporte += "- 🔄 Conversión entre formatos\n"
    reporte += "- 📊 Reportes y estadísticas\n\n"
    
    reporte += "## 🎯 Casos de Uso\n\n"
    reporte += "1. **Uso Individual:** Personalización rápida de firma personal\n"
    reporte += "2. **Equipos Pequeños:** Procesamiento por lotes para equipos\n"
    reporte += "3. **Empresas:** Estándares corporativos y branding\n"
    reporte += "4. **Agencias:** Creación de firmas para clientes\n"
    reporte += "5. **Desarrolladores:** Integración en sistemas de email\n\n"
    
    reporte += "## 📚 Documentación Disponible\n\n"
    reporte += "- 📖 README.md - Documentación principal\n"
    reporte += "- 🚀 INICIO_RAPIDO.md - Guía de inicio rápido\n"
    reporte += "- 📚 GUIA_PERSONALIZACION_AVANZADA.md - Personalización avanzada\n"
    reporte += "- 📝 EJEMPLOS_USO.md - Ejemplos prácticos\n"
    reporte += "- 🏢 PLANTILLAS_POR_INDUSTRIA.md - Guía por industria\n"
    reporte += "- 🔄 GUIA_MIGRACION.md - Guía de migración\n"
    reporte += "- ❓ FAQs.md - Preguntas frecuentes\n"
    reporte += "- ✅ CHECKLIST_FINAL.md - Checklist antes de usar\n\n"
    
    reporte += "## 🚀 Próximos Pasos Recomendados\n\n"
    reporte += "1. Revisar `INICIO_RAPIDO.md` para comenzar\n"
    reporte += "2. Seleccionar una plantilla base según tu industria\n"
    reporte += "3. Personalizar con `personalizar_firma.py`\n"
    reporte += "4. Validar con `validar_firma.py`\n"
    reporte += "5. Probar en diferentes clientes de email\n"
    reporte += "6. Implementar en tu cliente de email\n\n"
    
    reporte += "---\n\n"
    reporte += f"*Reporte generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    reporte += "*Para regenerar, ejecuta `generar_reporte_completo.py`*\n"
    
    return reporte

def main():
    """Función principal"""
    print("=" * 70)
    print("📊 Generador de Reporte Completo")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando proyecto completo...")
    print()
    
    analisis = analizar_proyecto_completo(directorio_actual)
    
    # Generar reporte
    reporte = generar_reporte_completo(analisis)
    
    # Guardar
    archivo_reporte = directorio_actual / "REPORTE_COMPLETO.md"
    with open(archivo_reporte, 'w', encoding='utf-8') as f:
        f.write(reporte)
    
    print("=" * 70)
    print("✅ Reporte completo generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_reporte.name}")
    print()
    print("📊 Resumen:")
    print(f"   - Plantillas: {analisis['plantillas']['total']}")
    print(f"   - Scripts: {analisis['scripts']}")
    print(f"   - Documentación: {analisis['documentacion']}")
    print(f"   - Tamaño total: {analisis['tamaño_total']:,} bytes")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







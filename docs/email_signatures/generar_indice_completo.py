#!/usr/bin/env python3
"""
Generador de Índice Completo
Genera un índice completo y navegable de todo el proyecto
"""

import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def categorizar_archivos(directorio: Path) -> dict:
    """Categoriza todos los archivos del proyecto"""
    categorias = {
        "plantillas_html": [],
        "plantillas_texto": [],
        "scripts_python": [],
        "herramientas_html": [],
        "documentacion": [],
        "archivos_config": [],
        "otros": []
    }
    
    for archivo in directorio.iterdir():
        if archivo.is_file():
            nombre = archivo.name.lower()
            extension = archivo.suffix.lower()
            
            if nombre.startswith('firma_') and extension == '.html':
                categorias["plantillas_html"].append(archivo.name)
            elif nombre.startswith('firma_') and extension == '.txt':
                categorias["plantillas_texto"].append(archivo.name)
            elif extension == '.py':
                categorias["scripts_python"].append(archivo.name)
            elif extension == '.html' and any(x in nombre for x in ['generador', 'test', 'preview', 'dashboard']):
                categorias["herramientas_html"].append(archivo.name)
            elif extension == '.md':
                categorias["documentacion"].append(archivo.name)
            elif extension in ['.json', '.vcf']:
                categorias["archivos_config"].append(archivo.name)
            else:
                categorias["otros"].append(archivo.name)
    
    return categorias

def generar_indice_completo(categorias: dict) -> str:
    """Genera el índice completo"""
    indice = "# 📋 Índice Completo del Proyecto\n\n"
    indice += f"**Última actualización:** {datetime.now().strftime('%d de %B de %Y a las %H:%M:%S')}\n\n"
    
    indice += "Este índice proporciona una referencia completa de todos los archivos del proyecto.\n\n"
    
    # Estadísticas
    total_archivos = sum(len(v) for v in categorias.values())
    indice += f"**Total de archivos:** {total_archivos}\n\n"
    
    # Plantillas HTML
    if categorias["plantillas_html"]:
        indice += "## 📧 Plantillas HTML\n\n"
        indice += f"**Total:** {len(categorias['plantillas_html'])} plantillas\n\n"
        
        # Subcategorizar plantillas
        subcategorias = {
            "Por Industria": [],
            "Por Tipo de Empresa": [],
            "Por Rol": [],
            "Estacionales": [],
            "Temáticas": [],
            "Especiales": [],
            "Versiones": [],
            "Generales": []
        }
        
        for plantilla in categorias["plantillas_html"]:
            nombre = plantilla.lower()
            if any(ind in nombre for ind in ['salud', 'educacion', 'finanzas', 'tecnologia', 'ventas', 'rrhh', 'marketing', 'legal', 'diseno', 'consultoria', 'medios', 'investigacion', 'coaching', 'bienes_raices', 'gastronomia', 'turismo', 'fitness', 'arte', 'musica', 'fotografia', 'arquitectura', 'psicologia']):
                subcategorias["Por Industria"].append(plantilla)
            elif any(emp in nombre for emp in ['startup', 'corporativa']):
                subcategorias["Por Tipo de Empresa"].append(plantilla)
            elif any(rol in nombre for rol in ['consultor', 'desarrollador']):
                subcategorias["Por Rol"].append(plantilla)
            elif any(est in nombre for est in ['navidad', 'verano', 'ano_nuevo']):
                subcategorias["Estacionales"].append(plantilla)
            elif any(tem in nombre for tem in ['tema_', 'oscuro', 'azul', 'rojo', 'purpura']):
                subcategorias["Temáticas"].append(plantilla)
            elif any(esp in nombre for esp in ['qr', 'calendario', 'bilingue', 'premium', 'evento']):
                subcategorias["Especiales"].append(plantilla)
            elif any(ver in nombre for ver in ['compacta', 'simple', 'minimalista']):
                subcategorias["Versiones"].append(plantilla)
            else:
                subcategorias["Generales"].append(plantilla)
        
        for subcat, lista in subcategorias.items():
            if lista:
                indice += f"### {subcat}\n\n"
                for archivo in sorted(lista):
                    indice += f"- `{archivo}`\n"
                indice += "\n"
    
    # Plantillas Texto
    if categorias["plantillas_texto"]:
        indice += "## 📄 Plantillas Texto Plano\n\n"
        for archivo in sorted(categorias["plantillas_texto"]):
            indice += f"- `{archivo}`\n"
        indice += "\n"
    
    # Scripts Python
    if categorias["scripts_python"]:
        indice += "## 🐍 Scripts Python\n\n"
        indice += f"**Total:** {len(categorias['scripts_python'])} scripts\n\n"
        
        # Subcategorizar scripts
        subcategorias_scripts = {
            "Personalización": [],
            "Validación": [],
            "Análisis": [],
            "Optimización": [],
            "Conversión": [],
            "Utilidades": [],
            "Documentación": [],
            "Otros": []
        }
        
        for script in categorias["scripts_python"]:
            nombre = script.lower()
            if 'personalizar' in nombre or 'procesar' in nombre or 'variacion' in nombre:
                subcategorias_scripts["Personalización"].append(script)
            elif 'validar' in nombre or 'verificar' in nombre:
                subcategorias_scripts["Validación"].append(script)
            elif 'analizar' in nombre or 'estadisticas' in nombre:
                subcategorias_scripts["Análisis"].append(script)
            elif 'optimizar' in nombre or 'limpiar' in nombre:
                subcategorias_scripts["Optimización"].append(script)
            elif 'converter' in nombre or 'exportar' in nombre:
                subcategorias_scripts["Conversión"].append(script)
            elif 'buscar' in nombre or 'comparar' in nombre or 'cambiar' in nombre or 'generar_qr' in nombre or 'backup' in nombre:
                subcategorias_scripts["Utilidades"].append(script)
            elif 'documentacion' in nombre or 'reporte' in nombre or 'resumen' in nombre or 'guia' in nombre or 'matriz' in nombre or 'dashboard' in nombre or 'manual' in nombre or 'indice' in nombre:
                subcategorias_scripts["Documentación"].append(script)
            else:
                subcategorias_scripts["Otros"].append(script)
        
        for subcat, lista in subcategorias_scripts.items():
            if lista:
                indice += f"### {subcat}\n\n"
                for archivo in sorted(lista):
                    indice += f"- `{archivo}`\n"
                indice += "\n"
    
    # Herramientas HTML
    if categorias["herramientas_html"]:
        indice += "## 🎨 Herramientas HTML\n\n"
        for archivo in sorted(categorias["herramientas_html"]):
            indice += f"- `{archivo}`\n"
        indice += "\n"
    
    # Documentación
    if categorias["documentacion"]:
        indice += "## 📚 Documentación\n\n"
        indice += f"**Total:** {len(categorias['documentacion'])} documentos\n\n"
        
        # Separar por tipo
        principales = []
        generados = []
        
        for doc in categorias["documentacion"]:
            nombre = doc.lower()
            if any(x in nombre for x in ['placeholders', 'documentacion_completa', 'resumen_ejecutivo', 'reporte_completo', 'guia_rapida', 'analisis', 'matriz', 'guia_completa', 'manual', 'indice']):
                generados.append(doc)
            else:
                principales.append(doc)
        
        if principales:
            indice += "### Documentación Principal\n\n"
            for archivo in sorted(principales):
                indice += f"- `{archivo}`\n"
            indice += "\n"
        
        if generados:
            indice += "### Documentación Generada\n\n"
            indice += "*Estos archivos se generan automáticamente*\n\n"
            for archivo in sorted(generados):
                indice += f"- `{archivo}`\n"
            indice += "\n"
    
    # Archivos de Configuración
    if categorias["archivos_config"]:
        indice += "## ⚙️ Archivos de Configuración\n\n"
        for archivo in sorted(categorias["archivos_config"]):
            indice += f"- `{archivo}`\n"
        indice += "\n"
    
    # Otros
    if categorias["otros"]:
        indice += "## 📁 Otros Archivos\n\n"
        for archivo in sorted(categorias["otros"]):
            indice += f"- `{archivo}`\n"
        indice += "\n"
    
    # Resumen
    indice += "## 📊 Resumen por Categoría\n\n"
    indice += f"- **Plantillas HTML:** {len(categorias['plantillas_html'])}\n"
    indice += f"- **Plantillas Texto:** {len(categorias['plantillas_texto'])}\n"
    indice += f"- **Scripts Python:** {len(categorias['scripts_python'])}\n"
    indice += f"- **Herramientas HTML:** {len(categorias['herramientas_html'])}\n"
    indice += f"- **Documentación:** {len(categorias['documentacion'])}\n"
    indice += f"- **Archivos de Configuración:** {len(categorias['archivos_config'])}\n"
    indice += f"- **Otros:** {len(categorias['otros'])}\n"
    indice += f"- **Total:** {total_archivos} archivos\n\n"
    
    indice += "---\n\n"
    indice += f"*Índice generado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    indice += "*Para actualizar, ejecuta `generar_indice_completo.py`*\n"
    
    return indice

def main():
    """Función principal"""
    print("=" * 70)
    print("📋 Generador de Índice Completo")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando y categorizando archivos...")
    print()
    
    categorias = categorizar_archivos(directorio_actual)
    
    # Generar índice
    indice = generar_indice_completo(categorias)
    
    # Guardar
    archivo_indice = directorio_actual / "INDICE_COMPLETO.md"
    with open(archivo_indice, 'w', encoding='utf-8') as f:
        f.write(indice)
    
    print("=" * 70)
    print("✅ Índice completo generado exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_indice.name}")
    print()
    
    # Resumen
    total = sum(len(v) for v in categorias.values())
    print("📊 Resumen:")
    print(f"   - Plantillas HTML: {len(categorias['plantillas_html'])}")
    print(f"   - Scripts Python: {len(categorias['scripts_python'])}")
    print(f"   - Documentación: {len(categorias['documentacion'])}")
    print(f"   - Total: {total} archivos")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







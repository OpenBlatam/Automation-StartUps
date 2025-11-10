#!/usr/bin/env python3
"""
Generador de Documentación Automática
Genera documentación completa del proyecto basada en análisis de archivos
"""

import os
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import json

def analizar_plantilla(archivo: Path) -> Dict:
    """Analiza una plantilla y extrae información"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Extraer información básica
        tamaño = len(contenido.encode('utf-8'))
        lineas = len(contenido.split('\n'))
        
        # Detectar características
        tiene_vml = 'xmlns:v=' in contenido
        tiene_mso = '<!--[if mso]' in contenido
        tiene_media_queries = '@media' in contenido
        tiene_tablas = '<table' in contenido
        tiene_enlaces = 'href=' in contenido
        tiene_imagenes = '<img' in contenido
        
        # Contar placeholders
        import re
        placeholders = re.findall(r'\[([^\]]+)\]', contenido)
        placeholders_unicos = list(set(placeholders))
        
        return {
            "nombre": archivo.name,
            "tamaño": tamaño,
            "lineas": lineas,
            "caracteristicas": {
                "soporte_outlook": tiene_vml and tiene_mso,
                "responsive": tiene_media_queries,
                "usa_tablas": tiene_tablas,
                "tiene_enlaces": tiene_enlaces,
                "tiene_imagenes": tiene_imagenes
            },
            "placeholders": len(placeholders_unicos),
            "placeholders_lista": placeholders_unicos[:10]  # Primeros 10
        }
    except Exception as e:
        return {"nombre": archivo.name, "error": str(e)}

def categorizar_plantillas(plantillas: List[Path]) -> Dict:
    """Categoriza plantillas por tipo"""
    categorias = {
        "por_industria": [],
        "estacionales": [],
        "por_rol": [],
        "por_empresa": [],
        "tematicas": [],
        "especiales": [],
        "otras": []
    }
    
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        
        if any(ind in nombre for ind in ['salud', 'educacion', 'finanzas', 'tecnologia', 'ventas', 'rrhh', 'marketing', 'legal', 'diseno', 'consultoria']):
            categorias["por_industria"].append(plantilla)
        elif any(est in nombre for est in ['navidad', 'verano', 'ano_nuevo', 'año_nuevo']):
            categorias["estacionales"].append(plantilla)
        elif any(rol in nombre for rol in ['consultor', 'desarrollador']):
            categorias["por_rol"].append(plantilla)
        elif any(emp in nombre for emp in ['startup', 'corporativa', 'empresa']):
            categorias["por_empresa"].append(plantilla)
        elif any(tem in nombre for tem in ['tema_', 'oscuro', 'azul', 'rojo', 'purpura', 'púrpura']):
            categorias["tematicas"].append(plantilla)
        elif any(esp in nombre for esp in ['qr', 'calendario', 'bilingue', 'bilingüe', 'premium', 'evento']):
            categorias["especiales"].append(plantilla)
        else:
            categorias["otras"].append(plantilla)
    
    return categorias

def generar_documentacion_completa(directorio: Path) -> str:
    """Genera documentación completa del proyecto"""
    doc = "# 📚 Documentación Completa del Proyecto\n\n"
    doc += f"**Generado automáticamente el:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    
    # Buscar plantillas
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    doc += "## 📊 Resumen General\n\n"
    doc += f"- **Total de plantillas:** {len(plantillas)}\n"
    
    # Categorizar
    categorias = categorizar_plantillas(plantillas)
    
    doc += f"- **Por industria:** {len(categorias['por_industria'])}\n"
    doc += f"- **Estacionales:** {len(categorias['estacionales'])}\n"
    doc += f"- **Por rol:** {len(categorias['por_rol'])}\n"
    doc += f"- **Por empresa:** {len(categorias['por_empresa'])}\n"
    doc += f"- **Temáticas:** {len(categorias['tematicas'])}\n"
    doc += f"- **Especiales:** {len(categorias['especiales'])}\n"
    doc += f"- **Otras:** {len(categorias['otras'])}\n\n"
    
    # Analizar plantillas
    doc += "## 📋 Análisis de Plantillas\n\n"
    
    total_tamaño = 0
    total_lineas = 0
    plantillas_analizadas = []
    
    for plantilla in plantillas:
        analisis = analizar_plantilla(plantilla)
        if "error" not in analisis:
            plantillas_analizadas.append(analisis)
            total_tamaño += analisis["tamaño"]
            total_lineas += analisis["lineas"]
    
    doc += f"- **Tamaño total:** {total_tamaño:,} bytes ({total_tamaño / 1024:.1f} KB)\n"
    doc += f"- **Líneas totales:** {total_lineas:,}\n"
    doc += f"- **Tamaño promedio:** {total_tamaño // len(plantillas_analizadas):,} bytes\n"
    doc += f"- **Líneas promedio:** {total_lineas // len(plantillas_analizadas)}\n\n"
    
    # Características
    doc += "## ✨ Características Técnicas\n\n"
    
    con_outlook = sum(1 for p in plantillas_analizadas if p["caracteristicas"]["soporte_outlook"])
    con_responsive = sum(1 for p in plantillas_analizadas if p["caracteristicas"]["responsive"])
    con_tablas = sum(1 for p in plantillas_analizadas if p["caracteristicas"]["usa_tablas"])
    
    doc += f"- **Soporte Outlook:** {con_outlook} plantillas ({con_outlook * 100 // len(plantillas_analizadas)}%)\n"
    doc += f"- **Responsive:** {con_responsive} plantillas ({con_responsive * 100 // len(plantillas_analizadas)}%)\n"
    doc += f"- **Usa tablas:** {con_tablas} plantillas ({con_tablas * 100 // len(plantillas_analizadas)}%)\n\n"
    
    # Lista de plantillas por categoría
    doc += "## 📂 Plantillas por Categoría\n\n"
    
    for categoria, lista_plantillas in categorias.items():
        if lista_plantillas:
            nombre_categoria = categoria.replace('_', ' ').title()
            doc += f"### {nombre_categoria}\n\n"
            for plantilla in sorted(lista_plantillas):
                doc += f"- `{plantilla.name}`\n"
            doc += "\n"
    
    # Top plantillas
    doc += "## 🏆 Top 10 Plantillas Más Grandes\n\n"
    top_plantillas = sorted(plantillas_analizadas, key=lambda x: x["tamaño"], reverse=True)[:10]
    
    for i, plantilla in enumerate(top_plantillas, 1):
        doc += f"{i}. **{plantilla['nombre']}** - {plantilla['tamaño']:,} bytes, {plantilla['lineas']} líneas\n"
    
    doc += "\n"
    doc += "## 📝 Notas\n\n"
    doc += "- Esta documentación se genera automáticamente\n"
    doc += "- Para actualizar, ejecuta `generar_documentacion.py`\n"
    doc += "- Las plantillas están optimizadas para compatibilidad con clientes de email\n\n"
    
    return doc

def main():
    """Función principal"""
    print("=" * 70)
    print("📚 Generador de Documentación Automática")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando proyecto...")
    print()
    
    documentacion = generar_documentacion_completa(directorio_actual)
    
    # Guardar
    archivo_doc = directorio_actual / "DOCUMENTACION_COMPLETA.md"
    with open(archivo_doc, 'w', encoding='utf-8') as f:
        f.write(documentacion)
    
    print("=" * 70)
    print("✅ Documentación generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_doc.name}")
    print()
    print("💡 La documentación incluye:")
    print("   - Resumen general del proyecto")
    print("   - Análisis de todas las plantillas")
    print("   - Características técnicas")
    print("   - Categorización de plantillas")
    print("   - Top plantillas")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







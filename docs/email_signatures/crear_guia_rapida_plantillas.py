#!/usr/bin/env python3
"""
Creador de Guía Rápida de Plantillas
Genera una guía rápida para seleccionar la plantilla adecuada
"""

import os
from pathlib import Path
from datetime import datetime

def categorizar_plantillas(directorio: Path) -> dict:
    """Categoriza todas las plantillas"""
    plantillas = sorted(directorio.glob("firma_*.html"))
    plantillas = [p for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    categorias = {
        "Por Industria": {
            "Salud": [],
            "Educación": [],
            "Finanzas": [],
            "Tecnología": [],
            "Ventas": [],
            "RRHH": [],
            "Marketing": [],
            "Legal": [],
            "Diseño": [],
            "Consultoría": [],
            "Medios": [],
            "Investigación": [],
            "Coaching": [],
            "Bienes Raíces": [],
            "Gastronomía": [],
            "Turismo": []
        },
        "Por Tipo de Empresa": {
            "Startup": [],
            "Corporativa": []
        },
        "Por Rol": {
            "Consultor": [],
            "Desarrollador": []
        },
        "Estacionales": {
            "Navidad": [],
            "Verano": [],
            "Año Nuevo": []
        },
        "Temáticas": {
            "Oscuro": [],
            "Azul": [],
            "Rojo": [],
            "Púrpura": []
        },
        "Especiales": {
            "Con QR": [],
            "Con Calendario": [],
            "Bilingüe": [],
            "Premium": [],
            "Eventos": []
        },
        "Versiones": {
            "Completa": [],
            "Compacta": [],
            "Simple": [],
            "Minimalista": []
        },
        "Generales": []
    }
    
    for plantilla in plantillas:
        nombre = plantilla.name.lower()
        agregado = False
        
        # Por industria
        if 'salud' in nombre:
            categorias["Por Industria"]["Salud"].append(plantilla.name)
            agregado = True
        elif 'educacion' in nombre or 'educación' in nombre:
            categorias["Por Industria"]["Educación"].append(plantilla.name)
            agregado = True
        elif 'finanzas' in nombre:
            categorias["Por Industria"]["Finanzas"].append(plantilla.name)
            agregado = True
        elif 'tecnologia' in nombre or 'tecnología' in nombre:
            categorias["Por Industria"]["Tecnología"].append(plantilla.name)
            agregado = True
        elif 'ventas' in nombre:
            categorias["Por Industria"]["Ventas"].append(plantilla.name)
            agregado = True
        elif 'rrhh' in nombre or 'recursos_humanos' in nombre:
            categorias["Por Industria"]["RRHH"].append(plantilla.name)
            agregado = True
        elif 'marketing' in nombre:
            categorias["Por Industria"]["Marketing"].append(plantilla.name)
            agregado = True
        elif 'legal' in nombre:
            categorias["Por Industria"]["Legal"].append(plantilla.name)
            agregado = True
        elif 'diseno' in nombre or 'diseño' in nombre:
            categorias["Por Industria"]["Diseño"].append(plantilla.name)
            agregado = True
        elif 'consultoria' in nombre or 'consultoría' in nombre:
            categorias["Por Industria"]["Consultoría"].append(plantilla.name)
            agregado = True
        elif 'medios' in nombre:
            categorias["Por Industria"]["Medios"].append(plantilla.name)
            agregado = True
        elif 'investigacion' in nombre or 'investigación' in nombre:
            categorias["Por Industria"]["Investigación"].append(plantilla.name)
            agregado = True
        elif 'coaching' in nombre:
            categorias["Por Industria"]["Coaching"].append(plantilla.name)
            agregado = True
        elif 'bienes_raices' in nombre or 'bienes_raíces' in nombre:
            categorias["Por Industria"]["Bienes Raíces"].append(plantilla.name)
            agregado = True
        elif 'gastronomia' in nombre or 'gastronomía' in nombre:
            categorias["Por Industria"]["Gastronomía"].append(plantilla.name)
            agregado = True
        elif 'turismo' in nombre:
            categorias["Por Industria"]["Turismo"].append(plantilla.name)
            agregado = True
        
        # Por tipo de empresa
        if 'startup' in nombre:
            categorias["Por Tipo de Empresa"]["Startup"].append(plantilla.name)
            agregado = True
        elif 'corporativa' in nombre:
            categorias["Por Tipo de Empresa"]["Corporativa"].append(plantilla.name)
            agregado = True
        
        # Por rol
        if 'consultor' in nombre and 'consultoria' not in nombre:
            categorias["Por Rol"]["Consultor"].append(plantilla.name)
            agregado = True
        elif 'desarrollador' in nombre:
            categorias["Por Rol"]["Desarrollador"].append(plantilla.name)
            agregado = True
        
        # Estacionales
        if 'navidad' in nombre:
            categorias["Estacionales"]["Navidad"].append(plantilla.name)
            agregado = True
        elif 'verano' in nombre:
            categorias["Estacionales"]["Verano"].append(plantilla.name)
            agregado = True
        elif 'ano_nuevo' in nombre or 'año_nuevo' in nombre:
            categorias["Estacionales"]["Año Nuevo"].append(plantilla.name)
            agregado = True
        
        # Temáticas
        if 'tema_oscuro' in nombre or 'dark' in nombre:
            categorias["Temáticas"]["Oscuro"].append(plantilla.name)
            agregado = True
        elif 'tema_azul' in nombre:
            categorias["Temáticas"]["Azul"].append(plantilla.name)
            agregado = True
        elif 'tema_rojo' in nombre:
            categorias["Temáticas"]["Rojo"].append(plantilla.name)
            agregado = True
        elif 'tema_purpura' in nombre or 'tema_púrpura' in nombre:
            categorias["Temáticas"]["Púrpura"].append(plantilla.name)
            agregado = True
        
        # Especiales
        if 'qr' in nombre:
            categorias["Especiales"]["Con QR"].append(plantilla.name)
            agregado = True
        elif 'calendario' in nombre or 'calendar' in nombre:
            categorias["Especiales"]["Con Calendario"].append(plantilla.name)
            agregado = True
        elif 'bilingue' in nombre or 'bilingüe' in nombre:
            categorias["Especiales"]["Bilingüe"].append(plantilla.name)
            agregado = True
        elif 'premium' in nombre:
            categorias["Especiales"]["Premium"].append(plantilla.name)
            agregado = True
        elif 'evento' in nombre:
            categorias["Especiales"]["Eventos"].append(plantilla.name)
            agregado = True
        
        # Versiones
        if 'compacta' in nombre or 'compact' in nombre:
            categorias["Versiones"]["Compacta"].append(plantilla.name)
            agregado = True
        elif 'simple' in nombre or 'simplificada' in nombre:
            categorias["Versiones"]["Simple"].append(plantilla.name)
            agregado = True
        elif 'minimalista' in nombre:
            categorias["Versiones"]["Minimalista"].append(plantilla.name)
            agregado = True
        elif not any(x in nombre for x in ['compacta', 'simple', 'minimalista', 'premium', 'tema_', 'qr', 'calendario', 'bilingue', 'evento']):
            categorias["Versiones"]["Completa"].append(plantilla.name)
            agregado = True
        
        if not agregado:
            categorias["Generales"].append(plantilla.name)
    
    return categorias

def generar_guia_rapida(categorias: dict) -> str:
    """Genera la guía rápida"""
    guia = "# 🎯 Guía Rápida de Selección de Plantillas\n\n"
    guia += "Esta guía te ayuda a encontrar rápidamente la plantilla adecuada para tus necesidades.\n\n"
    
    guia += "## 📋 Selección por Criterio\n\n"
    
    # Por industria
    guia += "### 🏢 Por Industria\n\n"
    for industria, plantillas in categorias["Por Industria"].items():
        if plantillas:
            guia += f"#### {industria}\n\n"
            for plantilla in plantillas:
                guia += f"- `{plantilla}`\n"
            guia += "\n"
    
    # Por tipo de empresa
    guia += "### 🏛️ Por Tipo de Empresa\n\n"
    for tipo, plantillas in categorias["Por Tipo de Empresa"].items():
        if plantillas:
            guia += f"#### {tipo}\n\n"
            for plantilla in plantillas:
                guia += f"- `{plantilla}`\n"
            guia += "\n"
    
    # Por rol
    guia += "### 👤 Por Rol\n\n"
    for rol, plantillas in categorias["Por Rol"].items():
        if plantillas:
            guia += f"#### {rol}\n\n"
            for plantilla in plantillas:
                guia += f"- `{plantilla}`\n"
            guia += "\n"
    
    # Estacionales
    guia += "### 🎄 Estacionales\n\n"
    for estacion, plantillas in categorias["Estacionales"].items():
        if plantillas:
            guia += f"#### {estacion}\n\n"
            for plantilla in plantillas:
                guia += f"- `{plantilla}`\n"
            guia += "\n"
    
    # Temáticas
    guia += "### 🎨 Temáticas\n\n"
    for tema, plantillas in categorias["Temáticas"].items():
        if plantillas:
            guia += f"#### {tema}\n\n"
            for plantilla in plantillas:
                guia += f"- `{plantilla}`\n"
            guia += "\n"
    
    # Especiales
    guia += "### ⭐ Especiales\n\n"
    for especial, plantillas in categorias["Especiales"].items():
        if plantillas:
            guia += f"#### {especial}\n\n"
            for plantilla in plantillas:
                guia += f"- `{plantilla}`\n"
            guia += "\n"
    
    # Versiones
    guia += "### 📐 Versiones\n\n"
    guia += "Las plantillas están disponibles en diferentes versiones:\n\n"
    for version, plantillas in categorias["Versiones"].items():
        if plantillas:
            guia += f"#### {version}\n\n"
            guia += f"- {len(plantillas)} plantilla(s) disponible(s)\n"
            guia += "- Ejemplos: " + ", ".join(plantillas[:3]) + "\n\n"
    
    # Recomendaciones
    guia += "## 💡 Recomendaciones\n\n"
    guia += "1. **Para uso general:** Usa la versión completa\n"
    guia += "2. **Para espacios limitados:** Usa la versión compacta\n"
    guia += "3. **Para máxima compatibilidad:** Usa la versión simple\n"
    guia += "4. **Para diseño moderno:** Usa la versión minimalista\n"
    guia += "5. **Para eventos especiales:** Usa plantillas estacionales\n\n"
    
    guia += "---\n\n"
    guia += f"*Guía generada automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return guia

def main():
    """Función principal"""
    print("=" * 70)
    print("🎯 Creador de Guía Rápida de Plantillas")
    print("=" * 70)
    print()
    
    directorio_actual = Path(__file__).parent
    
    print("🔍 Analizando y categorizando plantillas...")
    print()
    
    categorias = categorizar_plantillas(directorio_actual)
    
    # Generar guía
    guia = generar_guia_rapida(categorias)
    
    # Guardar
    archivo_guia = directorio_actual / "GUIA_RAPIDA_PLANTILLAS.md"
    with open(archivo_guia, 'w', encoding='utf-8') as f:
        f.write(guia)
    
    print("=" * 70)
    print("✅ Guía rápida generada exitosamente")
    print("=" * 70)
    print(f"📄 Archivo: {archivo_guia.name}")
    print()
    
    # Resumen
    total_plantillas = sum(len(v) for categoria in categorias.values() if isinstance(categoria, dict) for v in categoria.values()) + len(categorias.get("Generales", []))
    print(f"📊 Total de plantillas categorizadas: {total_plantillas}")
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







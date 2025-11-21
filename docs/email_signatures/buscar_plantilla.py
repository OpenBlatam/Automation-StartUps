#!/usr/bin/env python3
"""
Buscador de Plantillas
Busca plantillas por criterios específicos (industria, estilo, características)
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional

def buscar_en_contenido(archivo: str, terminos: List[str]) -> bool:
    """Busca términos en el contenido del archivo"""
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            contenido = f.read().lower()
        
        for termino in terminos:
            if termino.lower() in contenido:
                return True
        return False
    except:
        return False

def buscar_por_nombre(archivo: str, terminos: List[str]) -> bool:
    """Busca términos en el nombre del archivo"""
    nombre = Path(archivo).name.lower()
    for termino in terminos:
        if termino.lower() in nombre:
            return True
    return False

def buscar_por_industria(archivo: str, industria: str) -> bool:
    """Busca plantillas por industria"""
    industrias = {
        "salud": ["salud", "medicina", "médico", "clínica", "hospital"],
        "educacion": ["educación", "educacion", "academia", "campus", "universidad"],
        "finanzas": ["finanzas", "financiero", "inversión", "banco"],
        "tecnologia": ["tecnología", "tecnologia", "tech", "desarrollador", "software"],
        "startup": ["startup", "empresa_startup"],
        "corporativa": ["corporativa", "empresa_corporativa"]
    }
    
    if industria.lower() not in industrias:
        return False
    
    terminos = industrias[industria.lower()]
    return buscar_en_contenido(archivo, terminos) or buscar_por_nombre(archivo, terminos)

def buscar_por_estilo(archivo: str, estilo: str) -> bool:
    """Busca plantillas por estilo"""
    estilos = {
        "minimalista": ["minimalista", "minimal"],
        "compacta": ["compacta", "compact"],
        "simple": ["simple", "simplificada"],
        "premium": ["premium"],
        "completa": ["firma_curso", "firma_saas", "firma_ia_bulk"]
    }
    
    if estilo.lower() not in estilos:
        return False
    
    terminos = estilos[estilo.lower()]
    return buscar_por_nombre(archivo, terminos)

def buscar_por_tema(archivo: str, tema: str) -> bool:
    """Busca plantillas por tema"""
    temas = {
        "navidad": ["navidad", "christmas"],
        "verano": ["verano", "summer"],
        "año nuevo": ["año nuevo", "ano nuevo", "new year"],
        "oscuro": ["oscuro", "dark", "tema_oscuro"],
        "azul": ["azul", "blue", "tema_azul"],
        "rojo": ["rojo", "red", "tema_rojo"],
        "púrpura": ["púrpura", "purple", "purpura", "tema_purpura"]
    }
    
    if tema.lower() not in temas:
        return False
    
    terminos = temas[tema.lower()]
    return buscar_por_nombre(archivo, terminos) or buscar_en_contenido(archivo, terminos)

def buscar_por_caracteristica(archivo: str, caracteristica: str) -> bool:
    """Busca plantillas por características especiales"""
    caracteristicas = {
        "qr": ["qr", "qrcode"],
        "calendario": ["calendario", "calendar"],
        "bilingue": ["bilingue", "bilingüe", "bilingual"],
        "vcard": ["vcard", "vcf"]
    }
    
    if caracteristica.lower() not in caracteristicas:
        return False
    
    terminos = caracteristicas[caracteristica.lower()]
    return buscar_por_nombre(archivo, terminos) or buscar_en_contenido(archivo, terminos)

def buscar_plantillas(criterios: Dict) -> List[str]:
    """Busca plantillas según criterios"""
    directorio_actual = Path(__file__).parent
    plantillas = sorted(directorio_actual.glob("firma_*.html"))
    plantillas = [str(p) for p in plantillas if "variacion" not in p.name and "personalizada" not in p.name]
    
    resultados = []
    
    for plantilla in plantillas:
        coincide = True
        
        # Buscar por industria
        if "industria" in criterios and criterios["industria"]:
            if not buscar_por_industria(plantilla, criterios["industria"]):
                coincide = False
        
        # Buscar por estilo
        if "estilo" in criterios and criterios["estilo"]:
            if not buscar_por_estilo(plantilla, criterios["estilo"]):
                coincide = False
        
        # Buscar por tema
        if "tema" in criterios and criterios["tema"]:
            if not buscar_por_tema(plantilla, criterios["tema"]):
                coincide = False
        
        # Buscar por característica
        if "caracteristica" in criterios and criterios["caracteristica"]:
            if not buscar_por_caracteristica(plantilla, criterios["caracteristica"]):
                coincide = False
        
        # Buscar por término general
        if "termino" in criterios and criterios["termino"]:
            terminos = criterios["termino"].split()
            if not (buscar_por_nombre(plantilla, terminos) or buscar_en_contenido(plantilla, terminos)):
                coincide = False
        
        if coincide:
            resultados.append(plantilla)
    
    return resultados

def main():
    """Función principal"""
    print("=" * 70)
    print("🔍 Buscador de Plantillas")
    print("=" * 70)
    print()
    
    print("Criterios de búsqueda disponibles:")
    print("  1. Industria (salud, educación, finanzas, tecnología, startup, corporativa)")
    print("  2. Estilo (minimalista, compacta, simple, premium, completa)")
    print("  3. Tema (navidad, verano, año nuevo, oscuro, azul, rojo, púrpura)")
    print("  4. Característica (qr, calendario, bilingue, vcard)")
    print("  5. Término general (busca en nombre y contenido)")
    print()
    
    criterios = {}
    
    # Industria
    industria = input("Industria (Enter para omitir): ").strip()
    if industria:
        criterios["industria"] = industria
    
    # Estilo
    estilo = input("Estilo (Enter para omitir): ").strip()
    if estilo:
        criterios["estilo"] = estilo
    
    # Tema
    tema = input("Tema (Enter para omitir): ").strip()
    if tema:
        criterios["tema"] = tema
    
    # Característica
    caracteristica = input("Característica especial (Enter para omitir): ").strip()
    if caracteristica:
        criterios["caracteristica"] = caracteristica
    
    # Término general
    termino = input("Término de búsqueda general (Enter para omitir): ").strip()
    if termino:
        criterios["termino"] = termino
    
    if not criterios:
        print("\n❌ No se especificaron criterios de búsqueda")
        return
    
    print()
    print("🔍 Buscando...")
    print()
    
    resultados = buscar_plantillas(criterios)
    
    if resultados:
        print(f"✅ Se encontraron {len(resultados)} plantilla(s):")
        print()
        for i, plantilla in enumerate(resultados, 1):
            print(f"{i}. {Path(plantilla).name}")
    else:
        print("❌ No se encontraron plantillas que coincidan con los criterios")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    main()







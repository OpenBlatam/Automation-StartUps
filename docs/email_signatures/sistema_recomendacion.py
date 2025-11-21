#!/usr/bin/env python3
"""
Sistema de Recomendación de Plantillas
Recomienda la mejor plantilla basándose en criterios del usuario.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional
import json
from datetime import datetime

class SistemaRecomendacion:
    def __init__(self, directorio: str = "."):
        self.directorio = Path(directorio)
        self.plantillas = {}
        self.perfiles = {}
        self._cargar_perfiles()
    
    def _cargar_perfiles(self) -> None:
        """Carga perfiles de industrias y roles."""
        self.perfiles = {
            'medicina': {
                'keywords': ['medico', 'doctor', 'clinica', 'hospital', 'salud', 'paciente'],
                'plantillas': ['firma_medico', 'firma_oftalmologia', 'firma_dermatologia', 
                              'firma_radiologia', 'firma_enfermeria']
            },
            'tecnologia': {
                'keywords': ['tecnologia', 'tech', 'software', 'desarrollador', 'programador', 'it'],
                'plantillas': ['firma_tecnologia', 'firma_desarrollador', 'firma_ingeniero']
            },
            'educacion': {
                'keywords': ['educacion', 'profesor', 'maestro', 'universidad', 'escuela', 'academico'],
                'plantillas': ['firma_profesor', 'firma_educador']
            },
            'legal': {
                'keywords': ['abogado', 'legal', 'ley', 'juridico', 'derecho'],
                'plantillas': ['firma_abogado', 'firma_legal']
            },
            'ventas': {
                'keywords': ['ventas', 'comercial', 'vendedor', 'sales', 'negocio'],
                'plantillas': ['firma_ventas', 'firma_comercial']
            },
            'marketing': {
                'keywords': ['marketing', 'publicidad', 'social media', 'comunicacion'],
                'plantillas': ['firma_marketing', 'firma_comunicacion']
            },
            'recursos_humanos': {
                'keywords': ['rrhh', 'recursos humanos', 'hr', 'talento', 'personal'],
                'plantillas': ['firma_rrhh', 'firma_recursos_humanos']
            },
            'finanzas': {
                'keywords': ['finanzas', 'contador', 'contabilidad', 'financiero', 'economia'],
                'plantillas': ['firma_contador', 'firma_finanzas']
            },
            'terapias': {
                'keywords': ['terapia', 'terapeuta', 'rehabilitacion', 'psicologia', 'logopedia'],
                'plantillas': ['firma_terapia_ocupacional', 'firma_logopedia', 'firma_psicologia']
            },
            'especialidades_medicas': {
                'keywords': ['podologia', 'oftalmologia', 'dermatologia', 'radiologia'],
                'plantillas': ['firma_podologia', 'firma_oftalmologia', 'firma_dermatologia', 
                              'firma_radiologia']
            }
        }
    
    def cargar_plantillas(self) -> None:
        """Carga todas las plantillas disponibles."""
        archivos_html = list(self.directorio.glob("firma_*.html"))
        
        for archivo in archivos_html:
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    nombre_base = archivo.stem
                    self.plantillas[nombre_base] = {
                        'archivo': archivo.name,
                        'contenido': contenido,
                        'caracteristicas': self._extraer_caracteristicas(contenido, nombre_base)
                    }
            except Exception as e:
                print(f"Error al cargar {archivo.name}: {e}")
    
    def _extraer_caracteristicas(self, contenido: str, nombre: str) -> Dict:
        """Extrae características de una plantilla."""
        # Detectar industria/rol del nombre
        industria = self._detectar_industria(nombre)
        
        # Detectar características visuales
        colores = re.findall(r'#([0-9a-fA-F]{3,6})', contenido)
        color_principal = colores[0] if colores else None
        
        # Detectar elementos
        tiene_calendario = '[URL_CALENDARIO]' in contenido or 'calendario' in contenido.lower()
        tiene_redes_sociales = 'linkedin' in contenido.lower() or 'twitter' in contenido.lower()
        tiene_badge = 'badge' in contenido.lower() or 'gradient' in contenido.lower()
        
        return {
            'industria': industria,
            'color_principal': color_principal,
            'tiene_calendario': tiene_calendario,
            'tiene_redes_sociales': tiene_redes_sociales,
            'tiene_badge': tiene_badge,
            'tamaño': len(contenido),
            'complejidad': self._calcular_complejidad(contenido)
        }
    
    def _detectar_industria(self, nombre: str) -> str:
        """Detecta la industria basándose en el nombre de la plantilla."""
        nombre_lower = nombre.lower()
        
        for industria, perfil in self.perfiles.items():
            if any(kw in nombre_lower for kw in perfil['keywords']):
                return industria
        
        # Detección específica por nombre
        if 'medico' in nombre_lower or 'doctor' in nombre_lower:
            return 'medicina'
        elif 'tecnologia' in nombre_lower or 'desarrollador' in nombre_lower:
            return 'tecnologia'
        elif 'profesor' in nombre_lower or 'educador' in nombre_lower:
            return 'educacion'
        elif 'abogado' in nombre_lower or 'legal' in nombre_lower:
            return 'legal'
        elif 'ventas' in nombre_lower or 'comercial' in nombre_lower:
            return 'ventas'
        elif 'marketing' in nombre_lower:
            return 'marketing'
        elif 'rrhh' in nombre_lower or 'recursos_humanos' in nombre_lower:
            return 'recursos_humanos'
        elif 'contador' in nombre_lower or 'finanzas' in nombre_lower:
            return 'finanzas'
        elif 'terapia' in nombre_lower or 'logopedia' in nombre_lower:
            return 'terapias'
        elif any(esp in nombre_lower for esp in ['oftalmologia', 'dermatologia', 'podologia', 'radiologia']):
            return 'especialidades_medicas'
        
        return 'general'
    
    def _calcular_complejidad(self, contenido: str) -> str:
        """Calcula la complejidad de la plantilla."""
        num_tablas = len(re.findall(r'<table', contenido, re.IGNORECASE))
        num_estilos = len(re.findall(r'style\s*=', contenido, re.IGNORECASE))
        num_scripts = len(re.findall(r'<script', contenido, re.IGNORECASE))
        
        complejidad_score = num_tablas + (num_estilos // 10) + (num_scripts * 5)
        
        if complejidad_score < 10:
            return 'simple'
        elif complejidad_score < 20:
            return 'moderada'
        else:
            return 'avanzada'
    
    def recomendar(self, criterios: Dict) -> List[Dict]:
        """Recomienda plantillas basándose en criterios."""
        if not self.plantillas:
            self.cargar_plantillas()
        
        puntuaciones = []
        
        for nombre, datos in self.plantillas.items():
            puntuacion = 0
            razones = []
            
            # Criterio: Industria/Rol
            if 'industria' in criterios:
                industria_buscada = criterios['industria'].lower()
                industria_plantilla = datos['caracteristicas']['industria']
                
                if industria_buscada == industria_plantilla:
                    puntuacion += 50
                    razones.append(f"Coincide con industria: {industria_plantilla}")
                elif industria_buscada in industria_plantilla or industria_plantilla in industria_buscada:
                    puntuacion += 25
                    razones.append(f"Industria relacionada: {industria_plantilla}")
            
            # Criterio: Complejidad
            if 'complejidad' in criterios:
                complejidad_buscada = criterios['complejidad'].lower()
                complejidad_plantilla = datos['caracteristicas']['complejidad']
                
                if complejidad_buscada == complejidad_plantilla:
                    puntuacion += 20
                    razones.append(f"Complejidad adecuada: {complejidad_plantilla}")
            
            # Criterio: Funcionalidades
            if 'necesita_calendario' in criterios and criterios['necesita_calendario']:
                if datos['caracteristicas']['tiene_calendario']:
                    puntuacion += 15
                    razones.append("Incluye integración de calendario")
            
            if 'necesita_redes_sociales' in criterios and criterios['necesita_redes_sociales']:
                if datos['caracteristicas']['tiene_redes_sociales']:
                    puntuacion += 10
                    razones.append("Incluye enlaces a redes sociales")
            
            if 'necesita_badge' in criterios and criterios['necesita_badge']:
                if datos['caracteristicas']['tiene_badge']:
                    puntuacion += 10
                    razones.append("Incluye badge destacado")
            
            # Criterio: Tamaño
            if 'tamaño_preferido' in criterios:
                tamaño_pref = criterios['tamaño_preferido'].lower()
                tamaño_actual = datos['caracteristicas']['tamaño']
                
                if tamaño_pref == 'pequeño' and tamaño_actual < 5000:
                    puntuacion += 10
                    razones.append("Tamaño compacto")
                elif tamaño_pref == 'medio' and 5000 <= tamaño_actual < 10000:
                    puntuacion += 10
                    razones.append("Tamaño medio")
                elif tamaño_pref == 'grande' and tamaño_actual >= 10000:
                    puntuacion += 10
                    razones.append("Tamaño completo")
            
            puntuaciones.append({
                'plantilla': nombre,
                'archivo': datos['archivo'],
                'puntuacion': puntuacion,
                'razones': razones,
                'caracteristicas': datos['caracteristicas']
            })
        
        # Ordenar por puntuación
        puntuaciones.sort(key=lambda x: x['puntuacion'], reverse=True)
        
        return puntuaciones
    
    def generar_recomendacion_interactiva(self) -> None:
        """Genera una recomendación interactiva."""
        print("\n" + "="*60)
        print("SISTEMA DE RECOMENDACIÓN DE PLANTILLAS")
        print("="*60 + "\n")
        
        criterios = {}
        
        # Industria
        print("¿En qué industria o sector trabajas?")
        print("Opciones: medicina, tecnologia, educacion, legal, ventas, marketing, recursos_humanos, finanzas, terapias, especialidades_medicas")
        industria = input("Industria (o Enter para omitir): ").strip()
        if industria:
            criterios['industria'] = industria
        
        # Complejidad
        print("\n¿Qué nivel de complejidad prefieres?")
        print("Opciones: simple, moderada, avanzada")
        complejidad = input("Complejidad (o Enter para omitir): ").strip()
        if complejidad:
            criterios['complejidad'] = complejidad
        
        # Funcionalidades
        print("\n¿Necesitas alguna funcionalidad específica?")
        calendario = input("¿Integración de calendario? (s/n): ").strip().lower()
        if calendario == 's':
            criterios['necesita_calendario'] = True
        
        redes = input("¿Enlaces a redes sociales? (s/n): ").strip().lower()
        if redes == 's':
            criterios['necesita_redes_sociales'] = True
        
        badge = input("¿Badge destacado? (s/n): ").strip().lower()
        if badge == 's':
            criterios['necesita_badge'] = True
        
        # Tamaño
        print("\n¿Qué tamaño prefieres?")
        tamaño = input("Opciones: pequeño, medio, grande (o Enter para omitir): ").strip()
        if tamaño:
            criterios['tamaño_preferido'] = tamaño
        
        # Generar recomendaciones
        print("\n" + "="*60)
        print("RECOMENDACIONES:")
        print("="*60 + "\n")
        
        recomendaciones = self.recomendar(criterios)
        
        for i, rec in enumerate(recomendaciones[:5], 1):
            print(f"\n{i}. {rec['plantilla']} (Puntuación: {rec['puntuacion']}/100)")
            print(f"   Archivo: {rec['archivo']}")
            if rec['razones']:
                print(f"   Razones:")
                for razon in rec['razones']:
                    print(f"     - {razon}")
            print(f"   Características:")
            print(f"     - Industria: {rec['caracteristicas']['industria']}")
            print(f"     - Complejidad: {rec['caracteristicas']['complejidad']}")
            print(f"     - Tamaño: {rec['caracteristicas']['tamaño']} bytes")

def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de recomendación de plantillas')
    parser.add_argument('-d', '--directorio', default='.', 
                       help='Directorio con las plantillas (default: actual)')
    parser.add_argument('-i', '--interactivo', action='store_true',
                       help='Modo interactivo')
    
    args = parser.parse_args()
    
    sistema = SistemaRecomendacion(args.directorio)
    
    if args.interactivo:
        sistema.generar_recomendacion_interactiva()
    else:
        # Ejemplo de uso programático
        criterios = {
            'industria': 'medicina',
            'complejidad': 'moderada',
            'necesita_calendario': True,
            'necesita_badge': True
        }
        
        recomendaciones = sistema.recomendar(criterios)
        print(f"\nTop 5 recomendaciones:")
        for i, rec in enumerate(recomendaciones[:5], 1):
            print(f"{i}. {rec['plantilla']} - Puntuación: {rec['puntuacion']}/100")

if __name__ == "__main__":
    main()






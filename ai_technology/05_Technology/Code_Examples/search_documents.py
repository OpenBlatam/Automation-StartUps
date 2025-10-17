#!/usr/bin/env python3
"""
Sistema de búsqueda avanzada para documentos empresariales
"""

import os
import re
import json
from datetime import datetime

class DocumentSearcher:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.business_areas = {
            '01_Marketing': 'Marketing',
            '02_Finance': 'Finance',
            '03_Human_Resources': 'Human Resources',
            '04_Operations': 'Operations',
            '05_Technology': 'Technology',
            '06_Strategy': 'Strategy',
            '07_Risk_Management': 'Risk Management',
            '08_AI_Artificial_Intelligence': 'AI & Artificial Intelligence',
            '09_Sales': 'Sales',
            '10_Customer_Service': 'Customer Service',
            '11_Research_Development': 'Research & Development',
            '12_Quality_Assurance': 'Quality Assurance',
            '13_Legal_Compliance': 'Legal & Compliance',
            '14_Procurement': 'Procurement',
            '15_Logistics': 'Logistics',
            '16_Data_Analytics': 'Data Analytics',
            '17_Innovation': 'Innovation',
            '18_Sustainability': 'Sustainability',
            '19_International_Business': 'International Business',
            '20_Project_Management': 'Project Management'
        }
    
    def search_by_keywords(self, keywords, area=None):
        """Buscar documentos por palabras clave"""
        results = []
        search_areas = [area] if area else self.business_areas.keys()
        
        for area_code in search_areas:
            area_path = os.path.join(self.base_path, area_code)
            if not os.path.exists(area_path):
                continue
                
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        file_name = file.lower()
                        
                        # Buscar coincidencias en el nombre del archivo
                        matches = sum(1 for keyword in keywords if keyword.lower() in file_name)
                        if matches > 0:
                            results.append({
                                'file': file,
                                'path': file_path,
                                'area': self.business_areas.get(area_code, area_code),
                                'area_code': area_code,
                                'matches': matches,
                                'relative_path': os.path.relpath(file_path, self.base_path)
                            })
        
        # Ordenar por número de coincidencias
        results.sort(key=lambda x: x['matches'], reverse=True)
        return results
    
    def search_by_content(self, keywords, area=None):
        """Buscar documentos por contenido (solo primeras líneas)"""
        results = []
        search_areas = [area] if area else self.business_areas.keys()
        
        for area_code in search_areas:
            area_path = os.path.join(self.base_path, area_code)
            if not os.path.exists(area_path):
                continue
                
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read(1000)  # Leer solo las primeras 1000 caracteres
                                content_lower = content.lower()
                                
                                matches = sum(1 for keyword in keywords if keyword.lower() in content_lower)
                                if matches > 0:
                                    results.append({
                                        'file': file,
                                        'path': file_path,
                                        'area': self.business_areas.get(area_code, area_code),
                                        'area_code': area_code,
                                        'matches': matches,
                                        'relative_path': os.path.relpath(file_path, self.base_path),
                                        'preview': content[:200] + '...' if len(content) > 200 else content
                                    })
                        except Exception as e:
                            continue
        
        # Ordenar por número de coincidencias
        results.sort(key=lambda x: x['matches'], reverse=True)
        return results
    
    def get_area_statistics(self):
        """Obtener estadísticas por área"""
        stats = {}
        
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_code)
            if os.path.exists(area_path):
                file_count = 0
                for root, dirs, files in os.walk(area_path):
                    file_count += len([f for f in files if f.endswith('.md')])
                
                stats[area_name] = {
                    'code': area_code,
                    'files': file_count,
                    'path': area_path
                }
        
        return stats
    
    def print_results(self, results, max_results=10):
        """Imprimir resultados de búsqueda"""
        if not results:
            print("❌ No se encontraron resultados.")
            return
        
        print(f"🔍 Encontrados {len(results)} resultados:")
        print("=" * 80)
        
        for i, result in enumerate(results[:max_results], 1):
            print(f"{i}. 📄 {result['file']}")
            print(f"   📁 Área: {result['area']}")
            print(f"   📍 Ruta: {result['relative_path']}")
            print(f"   🎯 Coincidencias: {result['matches']}")
            if 'preview' in result:
                print(f"   📝 Vista previa: {result['preview']}")
            print("-" * 80)

def main():
    searcher = DocumentSearcher()
    
    print("🔍 Sistema de Búsqueda de Documentos Empresariales")
    print("=" * 60)
    
    while True:
        print("\n📋 Opciones de búsqueda:")
        print("1. Buscar por palabras clave (nombre de archivo)")
        print("2. Buscar por contenido")
        print("3. Ver estadísticas por área")
        print("4. Salir")
        
        choice = input("\nSeleccione una opción (1-4): ").strip()
        
        if choice == '1':
            keywords = input("Ingrese palabras clave (separadas por espacios): ").strip().split()
            if keywords:
                area = input("Ingrese código de área (opcional, presione Enter para todas): ").strip()
                area = area if area else None
                results = searcher.search_by_keywords(keywords, area)
                searcher.print_results(results)
        
        elif choice == '2':
            keywords = input("Ingrese palabras clave para buscar en contenido: ").strip().split()
            if keywords:
                area = input("Ingrese código de área (opcional, presione Enter para todas): ").strip()
                area = area if area else None
                results = searcher.search_by_content(keywords, area)
                searcher.print_results(results)
        
        elif choice == '3':
            stats = searcher.get_area_statistics()
            print("\n📊 Estadísticas por Área:")
            print("=" * 50)
            for area_name, data in sorted(stats.items(), key=lambda x: x[1]['files'], reverse=True):
                print(f"📁 {area_name}: {data['files']} archivos")
        
        elif choice == '4':
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida. Intente nuevamente.")

if __name__ == "__main__":
    main()





#!/usr/bin/env python3
"""
Sistema de analytics avanzado para el sistema de organización empresarial
"""

import os
import json
import re
from datetime import datetime, timedelta
from collections import Counter, defaultdict
import hashlib

class AnalyticsSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.analytics_file = os.path.join(base_path, "analytics_data.json")
        self.business_areas = [
            '01_Marketing', '02_Finance', '03_Human_Resources', '04_Operations',
            '05_Technology', '06_Strategy', '07_Risk_Management', '08_AI_Artificial_Intelligence',
            '09_Sales', '10_Customer_Service', '11_Research_Development', '12_Quality_Assurance',
            '13_Legal_Compliance', '14_Procurement', '15_Logistics', '16_Data_Analytics',
            '17_Innovation', '18_Sustainability', '19_International_Business', '20_Project_Management'
        ]
    
    def analyze_content_trends(self):
        """Analizar tendencias de contenido"""
        trends = {
            'keywords': Counter(),
            'file_types': Counter(),
            'areas_activity': Counter(),
            'content_themes': Counter(),
            'document_sizes': [],
            'creation_patterns': Counter()
        }
        
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            if not os.path.exists(area_path):
                continue
            
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        
                        # Análisis de nombre de archivo
                        trends['areas_activity'][area] += 1
                        
                        # Análisis de tipo de archivo
                        if 'guide' in file.lower():
                            trends['file_types']['Guides'] += 1
                        elif 'report' in file.lower():
                            trends['file_types']['Reports'] += 1
                        elif 'strategy' in file.lower():
                            trends['file_types']['Strategies'] += 1
                        elif 'template' in file.lower():
                            trends['file_types']['Templates'] += 1
                        else:
                            trends['file_types']['Other'] += 1
                        
                        # Análisis de tamaño
                        try:
                            file_size = os.path.getsize(file_path)
                            trends['document_sizes'].append(file_size)
                        except:
                            pass
                        
                        # Análisis de palabras clave
                        filename_lower = file.lower()
                        keywords = re.findall(r'\b\w+\b', filename_lower)
                        for keyword in keywords:
                            if len(keyword) > 3:  # Solo palabras de más de 3 caracteres
                                trends['keywords'][keyword] += 1
                        
                        # Análisis de temas
                        if any(word in filename_lower for word in ['ai', 'artificial', 'intelligence']):
                            trends['content_themes']['AI & Technology'] += 1
                        elif any(word in filename_lower for word in ['marketing', 'advertising', 'brand']):
                            trends['content_themes']['Marketing'] += 1
                        elif any(word in filename_lower for word in ['strategy', 'planning', 'management']):
                            trends['content_themes']['Strategy'] += 1
                        elif any(word in filename_lower for word in ['risk', 'security', 'compliance']):
                            trends['content_themes']['Risk Management'] += 1
                        elif any(word in filename_lower for word in ['analytics', 'data', 'metrics']):
                            trends['content_themes']['Analytics'] += 1
                        else:
                            trends['content_themes']['Other'] += 1
        
        return trends
    
    def analyze_usage_patterns(self):
        """Analizar patrones de uso"""
        patterns = {
            'area_distribution': {},
            'content_density': {},
            'growth_trends': {},
            'popular_keywords': [],
            'content_gaps': []
        }
        
        total_files = 0
        for area in self.business_areas:
            area_path = os.path.join(self.base_path, area)
            if os.path.exists(area_path):
                file_count = 0
                total_size = 0
                
                for root, dirs, files in os.walk(area_path):
                    for file in files:
                        if file.endswith('.md'):
                            file_path = os.path.join(root, file)
                            try:
                                file_size = os.path.getsize(file_path)
                                total_size += file_size
                                file_count += 1
                            except:
                                pass
                
                patterns['area_distribution'][area] = {
                    'files': file_count,
                    'size': total_size,
                    'avg_size': total_size / file_count if file_count > 0 else 0
                }
                
                total_files += file_count
        
        # Calcular porcentajes
        for area, data in patterns['area_distribution'].items():
            if total_files > 0:
                data['percentage'] = (data['files'] / total_files) * 100
        
        return patterns
    
    def generate_insights(self):
        """Generar insights basados en análisis"""
        trends = self.analyze_content_trends()
        patterns = self.analyze_usage_patterns()
        
        insights = {
            'top_keywords': trends['keywords'].most_common(10),
            'top_areas': sorted(patterns['area_distribution'].items(), 
                              key=lambda x: x[1]['files'], reverse=True)[:5],
            'content_themes': trends['content_themes'].most_common(),
            'file_types': trends['file_types'].most_common(),
            'recommendations': []
        }
        
        # Generar recomendaciones
        if trends['content_themes']['AI & Technology'] > trends['content_themes']['Marketing']:
            insights['recommendations'].append("Considerar expandir contenido de marketing para balancear con tecnología")
        
        if patterns['area_distribution'].get('14_Procurement', {}).get('files', 0) == 0:
            insights['recommendations'].append("Área de Procurement está vacía - considerar agregar contenido")
        
        if patterns['area_distribution'].get('15_Logistics', {}).get('files', 0) == 0:
            insights['recommendations'].append("Área de Logistics está vacía - considerar agregar contenido")
        
        return insights
    
    def create_analytics_report(self):
        """Crear reporte de analytics"""
        trends = self.analyze_content_trends()
        patterns = self.analyze_usage_patterns()
        insights = self.generate_insights()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files': sum(data['files'] for data in patterns['area_distribution'].values()),
                'total_areas': len([area for area, data in patterns['area_distribution'].items() if data['files'] > 0]),
                'total_size': sum(data['size'] for data in patterns['area_distribution'].values())
            },
            'trends': {
                'top_keywords': insights['top_keywords'],
                'content_themes': insights['content_themes'],
                'file_types': insights['file_types']
            },
            'distribution': {
                'top_areas': insights['top_areas'],
                'area_percentages': {area: data.get('percentage', 0) 
                                   for area, data in patterns['area_distribution'].items()}
            },
            'insights': {
                'recommendations': insights['recommendations'],
                'content_gaps': [],
                'growth_opportunities': []
            }
        }
        
        # Guardar reporte
        with open(self.analytics_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def print_analytics_summary(self):
        """Imprimir resumen de analytics"""
        report = self.create_analytics_report()
        
        print("📊 REPORTE DE ANALYTICS - SISTEMA DE ORGANIZACIÓN EMPRESARIAL")
        print("=" * 70)
        
        # Resumen general
        print(f"\n📈 RESUMEN GENERAL:")
        print(f"📁 Total de archivos: {report['summary']['total_files']}")
        print(f"🏢 Áreas activas: {report['summary']['total_areas']}")
        print(f"💾 Tamaño total: {report['summary']['total_size'] / 1024 / 1024:.2f} MB")
        
        # Top áreas
        print(f"\n🏆 TOP 5 ÁREAS CON MÁS CONTENIDO:")
        for i, (area, data) in enumerate(report['distribution']['top_areas'][:5], 1):
            percentage = data.get('percentage', 0)
            print(f"  {i}. {area}: {data['files']} archivos ({percentage:.1f}%)")
        
        # Palabras clave más populares
        print(f"\n🔑 PALABRAS CLAVE MÁS POPULARES:")
        for keyword, count in report['trends']['top_keywords'][:10]:
            print(f"  • {keyword}: {count} ocurrencias")
        
        # Temas de contenido
        print(f"\n📋 TEMAS DE CONTENIDO:")
        for theme, count in report['trends']['content_themes']:
            print(f"  • {theme}: {count} archivos")
        
        # Tipos de archivos
        print(f"\n📄 TIPOS DE ARCHIVOS:")
        for file_type, count in report['trends']['file_types']:
            print(f"  • {file_type}: {count} archivos")
        
        # Recomendaciones
        if report['insights']['recommendations']:
            print(f"\n💡 RECOMENDACIONES:")
            for i, rec in enumerate(report['insights']['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n📊 Reporte guardado en: {self.analytics_file}")

def main():
    analytics = AnalyticsSystem()
    
    print("📊 Sistema de Analytics Avanzado")
    print("=" * 40)
    print("1. Generar reporte completo")
    print("2. Ver resumen de analytics")
    print("3. Analizar tendencias")
    print("4. Salir")
    
    choice = input("\nSeleccione una opción (1-4): ").strip()
    
    if choice == '1':
        report = analytics.create_analytics_report()
        print(f"\n✅ Reporte generado exitosamente")
        print(f"📁 Ubicación: {analytics.analytics_file}")
    
    elif choice == '2':
        analytics.print_analytics_summary()
    
    elif choice == '3':
        trends = analytics.analyze_content_trends()
        print(f"\n📈 Tendencias de contenido:")
        print(f"🔑 Palabras clave más populares:")
        for keyword, count in trends['keywords'].most_common(10):
            print(f"  • {keyword}: {count}")
        
        print(f"\n📋 Tipos de archivos:")
        for file_type, count in trends['file_types'].most_common():
            print(f"  • {file_type}: {count}")
    
    elif choice == '4':
        print("👋 ¡Hasta luego!")
    
    else:
        print("❌ Opción no válida.")

if __name__ == "__main__":
    main()




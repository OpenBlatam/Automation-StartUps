#!/usr/bin/env python3
"""
Analizador de Patrones Avanzado
Identifica patrones en nombres de archivos y contenido para optimizar organización
"""

import os
import re
import json
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

class PatternAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.patterns = defaultdict(list)
        self.keywords = defaultdict(int)
        self.file_types = defaultdict(int)
        self.categories = defaultdict(int)
        
    def analyze_filename_patterns(self):
        """Analiza patrones en nombres de archivos"""
        print("🔍 Analizando patrones de nombres de archivos...")
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                filename = file_path.name
                
                # Patrones comunes
                patterns = {
                    'versioned': r'v\d+|\d{4}|\d{2,3}',
                    'camelCase': r'[A-Z][a-z]+[A-Z]',
                    'snake_case': r'[a-z]+_[a-z]+',
                    'kebab-case': r'[a-z]+-[a-z]+',
                    'numbered': r'^\d+_',
                    'uppercase': r'^[A-Z_]+$',
                    'mixed_case': r'[A-Z][a-z]+[A-Z][a-z]+'
                }
                
                for pattern_name, pattern in patterns.items():
                    if re.search(pattern, filename):
                        self.patterns[pattern_name].append(filename)
                
                # Contar tipos de archivo
                ext = file_path.suffix.lower()
                self.file_types[ext] += 1
                
                # Contar categorías
                if file_path.parent.name.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_')):
                    self.categories[file_path.parent.name] += 1
    
    def analyze_content_keywords(self):
        """Analiza palabras clave en el contenido de archivos"""
        print("📝 Analizando palabras clave en contenido...")
        
        text_extensions = {'.md', '.txt', '.py', '.js', '.ts', '.html', '.css'}
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in text_extensions:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read(5000)  # Primeros 5000 caracteres
                        
                        # Extraer palabras clave
                        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
                        for word in words:
                            if len(word) > 3:  # Solo palabras de más de 3 caracteres
                                self.keywords[word] += 1
                except:
                    continue
    
    def generate_optimization_suggestions(self):
        """Genera sugerencias de optimización basadas en patrones"""
        suggestions = []
        
        # Análisis de patrones de nombres
        if len(self.patterns['versioned']) > 10:
            suggestions.append({
                'type': 'naming',
                'priority': 'high',
                'description': 'Muchos archivos con versiones - considerar sistema de versionado unificado',
                'files_affected': len(self.patterns['versioned'])
            })
        
        if len(self.patterns['uppercase']) > 5:
            suggestions.append({
                'type': 'naming',
                'priority': 'medium',
                'description': 'Archivos en mayúsculas - considerar estandarizar a camelCase o snake_case',
                'files_affected': len(self.patterns['uppercase'])
            })
        
        # Análisis de distribución de categorías
        total_files = sum(self.categories.values())
        for category, count in self.categories.items():
            percentage = (count / total_files) * 100
            if percentage > 30:
                suggestions.append({
                    'type': 'organization',
                    'priority': 'medium',
                    'description': f'Categoría {category} tiene {percentage:.1f}% de archivos - considerar subcategorización',
                    'files_affected': count
                })
        
        # Análisis de tipos de archivo
        if self.file_types['.md'] > 1000:
            suggestions.append({
                'type': 'content',
                'priority': 'low',
                'description': 'Muchos archivos Markdown - considerar estructura de documentación',
                'files_affected': self.file_types['.md']
            })
        
        return suggestions
    
    def create_organization_rules(self):
        """Crea reglas de organización basadas en patrones encontrados"""
        rules = {
            'filename_patterns': {
                'versioned_files': {
                    'pattern': r'v\d+|\d{4}',
                    'suggested_category': '06_Documentation',
                    'reason': 'Archivos versionados suelen ser documentación'
                },
                'uppercase_files': {
                    'pattern': r'^[A-Z_]+$',
                    'suggested_category': '06_Documentation',
                    'reason': 'Archivos en mayúsculas suelen ser documentación importante'
                },
                'camelCase_files': {
                    'pattern': r'[A-Z][a-z]+[A-Z]',
                    'suggested_category': '05_Technology',
                    'reason': 'CamelCase sugiere código o tecnología'
                }
            },
            'content_keywords': {
                'top_keywords': dict(Counter(self.keywords).most_common(20)),
                'category_suggestions': self._suggest_categories_from_keywords()
            }
        }
        
        return rules
    
    def _suggest_categories_from_keywords(self):
        """Sugiere categorías basadas en palabras clave más frecuentes"""
        keyword_categories = {
            'marketing': ['marketing', 'campaign', 'promotion', 'brand', 'advertising'],
            'finance': ['investment', 'financial', 'revenue', 'profit', 'budget'],
            'technology': ['system', 'software', 'development', 'code', 'api'],
            'strategy': ['strategy', 'planning', 'business', 'growth', 'expansion'],
            'sales': ['sales', 'revenue', 'customer', 'client', 'deal']
        }
        
        suggestions = {}
        for category, keywords in keyword_categories.items():
            score = sum(self.keywords.get(kw, 0) for kw in keywords)
            if score > 0:
                suggestions[category] = score
        
        return dict(sorted(suggestions.items(), key=lambda x: x[1], reverse=True))
    
    def generate_report(self):
        """Genera reporte completo de análisis de patrones"""
        self.analyze_filename_patterns()
        self.analyze_content_keywords()
        
        suggestions = self.generate_optimization_suggestions()
        rules = self.create_organization_rules()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files_analyzed': sum(self.categories.values()),
                'patterns_found': len(self.patterns),
                'keywords_analyzed': len(self.keywords),
                'suggestions_generated': len(suggestions)
            },
            'patterns': dict(self.patterns),
            'top_keywords': dict(Counter(self.keywords).most_common(50)),
            'file_types': dict(self.file_types),
            'category_distribution': dict(self.categories),
            'suggestions': suggestions,
            'organization_rules': rules
        }
        
        return report

if __name__ == "__main__":
    analyzer = PatternAnalyzer("/Users/adan/frontier")
    
    print("🚀 Iniciando análisis de patrones avanzado...")
    report = analyzer.generate_report()
    
    print(f"\n📊 RESUMEN DEL ANÁLISIS")
    print(f"Archivos analizados: {report['summary']['total_files_analyzed']}")
    print(f"Patrones encontrados: {report['summary']['patterns_found']}")
    print(f"Palabras clave analizadas: {report['summary']['keywords_analyzed']}")
    print(f"Sugerencias generadas: {report['summary']['suggestions_generated']}")
    
    print(f"\n🔝 TOP 10 PALABRAS CLAVE:")
    for i, (word, count) in enumerate(list(report['top_keywords'].items())[:10], 1):
        print(f"  {i:2d}. {word}: {count}")
    
    print(f"\n📁 DISTRIBUCIÓN POR CATEGORÍAS:")
    for category, count in sorted(report['category_distribution'].items(), key=lambda x: x[1], reverse=True):
        percentage = (count / report['summary']['total_files_analyzed']) * 100
        print(f"  {category}: {count} archivos ({percentage:.1f}%)")
    
    if report['suggestions']:
        print(f"\n💡 SUGERENCIAS DE OPTIMIZACIÓN:")
        for i, suggestion in enumerate(report['suggestions'], 1):
            print(f"  {i}. [{suggestion['priority'].upper()}] {suggestion['description']}")
            print(f"     Archivos afectados: {suggestion['files_affected']}")
    
    # Guardar reporte
    report_path = Path("/Users/adan/frontier") / "pattern_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: {report_path}")




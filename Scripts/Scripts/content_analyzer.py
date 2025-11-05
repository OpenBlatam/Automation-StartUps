#!/usr/bin/env python3
"""
Content Analyzer - Sistema de Análisis de Contenido Avanzado
Analiza y optimiza el contenido de documentos markdown
"""

import os
import re
import json
import hashlib
from datetime import datetime
from collections import Counter, defaultdict
import argparse

class ContentAnalyzer:
    def __init__(self, root_path="."):
        self.root_path = root_path
        self.analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "categories": defaultdict(int),
            "file_types": defaultdict(int),
            "content_stats": {},
            "duplicates": [],
            "large_files": [],
            "missing_metadata": [],
            "broken_links": [],
            "recommendations": []
        }
    
    def analyze_file(self, file_path):
        """Analiza un archivo individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_stats = {
                "path": file_path,
                "size": len(content),
                "lines": len(content.split('\n')),
                "words": len(content.split()),
                "has_metadata": content.startswith('---'),
                "has_tags": bool(re.search(r'#\w+', content)),
                "has_links": bool(re.search(r'\[.*?\]\(.*?\)', content)),
                "has_images": bool(re.search(r'!\[.*?\]\(.*?\)', content)),
                "has_code": bool(re.search(r'```', content)),
                "has_tables": bool(re.search(r'\|.*\|', content))
            }
            
            # Detectar categoría
            category = self.detect_category(file_path, content)
            file_stats["category"] = category
            
            # Detectar tipo de archivo
            file_type = self.detect_file_type(file_path, content)
            file_stats["file_type"] = file_type
            
            return file_stats
            
        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return None
    
    def detect_category(self, file_path, content):
        """Detecta la categoría del archivo"""
        path_lower = file_path.lower()
        content_lower = content.lower()
        
        if 'vc' in path_lower or 'venture' in content_lower:
            return 'vc'
        elif 'marketing' in path_lower or 'marketing' in content_lower:
            return 'marketing'
        elif 'ai' in path_lower or 'artificial intelligence' in content_lower:
            return 'ai'
        elif 'business' in path_lower or 'strategy' in content_lower:
            return 'business'
        elif 'finance' in path_lower or 'financial' in content_lower:
            return 'finance'
        elif 'operations' in path_lower or 'hr' in path_lower:
            return 'operations'
        elif 'sales' in path_lower or 'customer' in path_lower:
            return 'sales'
        elif 'research' in path_lower or 'development' in path_lower:
            return 'research'
        elif 'legal' in path_lower or 'compliance' in path_lower:
            return 'legal'
        else:
            return 'general'
    
    def detect_file_type(self, file_path, content):
        """Detecta el tipo de archivo"""
        filename = os.path.basename(file_path).lower()
        content_lower = content.lower()
        
        if 'strategy' in filename or 'strategy' in content_lower:
            return 'strategy'
        elif 'template' in filename or 'template' in content_lower:
            return 'template'
        elif 'analysis' in filename or 'analysis' in content_lower:
            return 'analysis'
        elif 'guide' in filename or 'guide' in content_lower:
            return 'guide'
        elif 'checklist' in filename or 'checklist' in content_lower:
            return 'checklist'
        elif 'tool' in filename or 'script' in filename:
            return 'tool'
        elif 'report' in filename or 'report' in content_lower:
            return 'report'
        else:
            return 'document'
    
    def find_duplicates(self, files_data):
        """Encuentra archivos duplicados"""
        content_hashes = defaultdict(list)
        
        for file_data in files_data:
            if file_data:
                file_path = file_data['path']
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    content_hash = hashlib.md5(content.encode()).hexdigest()
                    content_hashes[content_hash].append(file_path)
                except:
                    continue
        
        duplicates = []
        for hash_val, files in content_hashes.items():
            if len(files) > 1:
                duplicates.append({
                    "hash": hash_val,
                    "files": files,
                    "count": len(files)
                })
        
        return duplicates
    
    def find_large_files(self, files_data, size_threshold=10000):
        """Encuentra archivos grandes"""
        large_files = []
        for file_data in files_data:
            if file_data and file_data['size'] > size_threshold:
                large_files.append({
                    "path": file_data['path'],
                    "size": file_data['size'],
                    "lines": file_data['lines'],
                    "words": file_data['words']
                })
        
        return sorted(large_files, key=lambda x: x['size'], reverse=True)
    
    def find_missing_metadata(self, files_data):
        """Encuentra archivos sin metadatos"""
        missing_metadata = []
        for file_data in files_data:
            if file_data and not file_data['has_metadata']:
                missing_metadata.append({
                    "path": file_data['path'],
                    "category": file_data['category'],
                    "file_type": file_data['file_type']
                })
        
        return missing_metadata
    
    def find_broken_links(self, files_data):
        """Encuentra enlaces rotos"""
        broken_links = []
        
        for file_data in files_data:
            if file_data:
                file_path = file_data['path']
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Buscar enlaces markdown
                    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
                    
                    for link_text, link_url in links:
                        if not link_url.startswith('http') and not link_url.startswith('#'):
                            # Verificar si el archivo existe
                            if not os.path.exists(link_url):
                                broken_links.append({
                                    "file": file_path,
                                    "link_text": link_text,
                                    "link_url": link_url
                                })
                except:
                    continue
        
        return broken_links
    
    def generate_recommendations(self, files_data):
        """Genera recomendaciones de optimización"""
        recommendations = []
        
        # Analizar estadísticas generales
        total_files = len([f for f in files_data if f])
        large_files = self.find_large_files(files_data)
        missing_metadata = self.find_missing_metadata(files_data)
        duplicates = self.find_duplicates(files_data)
        
        if len(large_files) > 0:
            recommendations.append({
                "type": "optimization",
                "priority": "high",
                "title": "Archivos grandes detectados",
                "description": f"Se encontraron {len(large_files)} archivos grandes que podrían beneficiarse de división o compresión",
                "action": "Considerar dividir archivos grandes en secciones más manejables"
            })
        
        if len(missing_metadata) > 0:
            recommendations.append({
                "type": "metadata",
                "priority": "medium",
                "title": "Metadatos faltantes",
                "description": f"Se encontraron {len(missing_metadata)} archivos sin metadatos",
                "action": "Agregar metadatos YAML a los archivos principales"
            })
        
        if len(duplicates) > 0:
            recommendations.append({
                "type": "cleanup",
                "priority": "high",
                "title": "Archivos duplicados",
                "description": f"Se encontraron {len(duplicates)} grupos de archivos duplicados",
                "action": "Revisar y eliminar duplicados innecesarios"
            })
        
        # Recomendaciones por categoría
        categories = Counter([f['category'] for f in files_data if f])
        for category, count in categories.most_common():
            if count > 50:
                recommendations.append({
                    "type": "organization",
                    "priority": "medium",
                    "title": f"Categoría {category} muy grande",
                    "description": f"La categoría {category} tiene {count} archivos",
                    "action": f"Considerar crear subcarpetas en {category}"
                })
        
        return recommendations
    
    def analyze_all(self):
        """Analiza todos los archivos markdown"""
        print("🔍 Iniciando análisis de contenido...")
        
        # Encontrar todos los archivos markdown
        markdown_files = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
        
        print(f"📄 Encontrados {len(markdown_files)} archivos markdown")
        
        # Analizar cada archivo
        files_data = []
        for file_path in markdown_files:
            file_data = self.analyze_file(file_path)
            files_data.append(file_data)
        
        # Procesar resultados
        self.analysis_results["total_files"] = len([f for f in files_data if f])
        
        # Categorías
        for file_data in files_data:
            if file_data:
                self.analysis_results["categories"][file_data["category"]] += 1
                self.analysis_results["file_types"][file_data["file_type"]] += 1
        
        # Estadísticas de contenido
        self.analysis_results["content_stats"] = {
            "total_size": sum(f["size"] for f in files_data if f),
            "total_lines": sum(f["lines"] for f in files_data if f),
            "total_words": sum(f["words"] for f in files_data if f),
            "files_with_metadata": sum(1 for f in files_data if f and f["has_metadata"]),
            "files_with_tags": sum(1 for f in files_data if f and f["has_tags"]),
            "files_with_links": sum(1 for f in files_data if f and f["has_links"]),
            "files_with_images": sum(1 for f in files_data if f and f["has_images"]),
            "files_with_code": sum(1 for f in files_data if f and f["has_code"]),
            "files_with_tables": sum(1 for f in files_data if f and f["has_tables"])
        }
        
        # Análisis específicos
        self.analysis_results["duplicates"] = self.find_duplicates(files_data)
        self.analysis_results["large_files"] = self.find_large_files(files_data)
        self.analysis_results["missing_metadata"] = self.find_missing_metadata(files_data)
        self.analysis_results["broken_links"] = self.find_broken_links(files_data)
        self.analysis_results["recommendations"] = self.generate_recommendations(files_data)
        
        print("✅ Análisis completado")
        return self.analysis_results
    
    def save_report(self, output_file="content_analysis_report.json"):
        """Guarda el reporte de análisis"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen del análisis"""
        results = self.analysis_results
        
        print("\n" + "="*50)
        print("📊 RESUMEN DEL ANÁLISIS DE CONTENIDO")
        print("="*50)
        
        print(f"📄 Total archivos analizados: {results['total_files']}")
        print(f"📊 Total tamaño: {results['content_stats']['total_size']:,} caracteres")
        print(f"📝 Total líneas: {results['content_stats']['total_lines']:,}")
        print(f"🔤 Total palabras: {results['content_stats']['total_words']:,}")
        
        print("\n📂 Archivos por categoría:")
        for category, count in sorted(results['categories'].items()):
            print(f"  {category}: {count}")
        
        print("\n📋 Archivos por tipo:")
        for file_type, count in sorted(results['file_types'].items()):
            print(f"  {file_type}: {count}")
        
        print(f"\n🏷️  Archivos con metadatos: {results['content_stats']['files_with_metadata']}")
        print(f"🔗 Archivos con enlaces: {results['content_stats']['files_with_links']}")
        print(f"🖼️  Archivos con imágenes: {results['content_stats']['files_with_images']}")
        print(f"💻 Archivos con código: {results['content_stats']['files_with_code']}")
        
        print(f"\n⚠️  Archivos duplicados: {len(results['duplicates'])}")
        print(f"📏 Archivos grandes: {len(results['large_files'])}")
        print(f"❌ Archivos sin metadatos: {len(results['missing_metadata'])}")
        print(f"🔗 Enlaces rotos: {len(results['broken_links'])}")
        
        print(f"\n💡 Recomendaciones: {len(results['recommendations'])}")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"  {i}. {rec['title']} ({rec['priority']})")

def main():
    parser = argparse.ArgumentParser(description='Analizador de contenido avanzado')
    parser.add_argument('--path', default='.', help='Ruta del directorio a analizar')
    parser.add_argument('--output', default='content_analysis_report.json', help='Archivo de salida')
    parser.add_argument('--summary', action='store_true', help='Mostrar resumen en consola')
    
    args = parser.parse_args()
    
    analyzer = ContentAnalyzer(args.path)
    results = analyzer.analyze_all()
    
    analyzer.save_report(args.output)
    
    if args.summary:
        analyzer.print_summary()

if __name__ == "__main__":
    main()















#!/usr/bin/env python3
"""
Analizador de Dependencias Avanzado
Identifica relaciones entre archivos y optimiza la estructura organizacional
"""

import os
import re
import json
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

class DependencyAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.dependencies = defaultdict(list)
        self.file_relationships = defaultdict(set)
        self.content_similarity = defaultdict(dict)
        self.cross_references = defaultdict(list)
        
    def analyze_file_dependencies(self):
        """Analiza dependencias entre archivos"""
        print("🔗 Analizando dependencias entre archivos...")
        
        # Patrones de referencias comunes
        reference_patterns = [
            r'\[([^\]]+)\]\(([^)]+)\)',  # Markdown links
            r'!\[([^\]]*)\]\(([^)]+)\)',  # Markdown images
            r'import\s+["\']([^"\']+)["\']',  # Python imports
            r'from\s+([^\s]+)\s+import',  # Python from imports
            r'require\(["\']([^"\']+)["\']\)',  # Node.js requires
            r'@import\s+["\']([^"\']+)["\']',  # CSS imports
            r'<link[^>]+href=["\']([^"\']+)["\']',  # HTML links
            r'<script[^>]+src=["\']([^"\']+)["\']',  # HTML scripts
            r'<img[^>]+src=["\']([^"\']+)["\']',  # HTML images
        ]
        
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.md', '.py', '.js', '.ts', '.html', '.css']:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for pattern in reference_patterns:
                            matches = re.findall(pattern, content)
                            for match in matches:
                                if isinstance(match, tuple):
                                    ref_file = match[1] if len(match) > 1 else match[0]
                                else:
                                    ref_file = match
                                
                                # Normalizar referencia
                                ref_file = self._normalize_reference(ref_file, file_path)
                                if ref_file:
                                    self.dependencies[str(file_path)].append(ref_file)
                                    self.file_relationships[str(file_path)].add(ref_file)
                                    
                except Exception as e:
                    continue
    
    def analyze_content_similarity(self):
        """Analiza similitud de contenido entre archivos"""
        print("📊 Analizando similitud de contenido...")
        
        text_files = []
        for file_path in self.project_root.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_files.append((str(file_path), content))
            except:
                continue
        
        # Análisis de similitud básico
        for i, (file1, content1) in enumerate(text_files):
            for j, (file2, content2) in enumerate(text_files[i+1:], i+1):
                similarity = self._calculate_similarity(content1, content2)
                if similarity > 0.3:  # Umbral de similitud
                    self.content_similarity[file1][file2] = similarity
                    self.content_similarity[file2][file1] = similarity
    
    def analyze_cross_references(self):
        """Analiza referencias cruzadas entre categorías"""
        print("🔄 Analizando referencias cruzadas...")
        
        for file_path, deps in self.dependencies.items():
            file_category = self._get_file_category(file_path)
            for dep in deps:
                dep_category = self._get_file_category(dep)
                if file_category != dep_category and dep_category:
                    self.cross_references[file_category].append({
                        'file': file_path,
                        'references': dep,
                        'target_category': dep_category
                    })
    
    def suggest_optimizations(self):
        """Sugiere optimizaciones basadas en análisis de dependencias"""
        suggestions = []
        
        # Sugerir archivos relacionados que deberían estar juntos
        for file1, similarities in self.content_similarity.items():
            for file2, similarity in similarities.items():
                if similarity > 0.7:  # Alta similitud
                    cat1 = self._get_file_category(file1)
                    cat2 = self._get_file_category(file2)
                    if cat1 != cat2:
                        suggestions.append({
                            'type': 'relocation',
                            'priority': 'high',
                            'description': f'Archivos altamente similares en categorías diferentes',
                            'files': [file1, file2],
                            'similarity': similarity,
                            'suggested_action': f'Mover ambos archivos a la misma categoría'
                        })
        
        # Sugerir categorías con muchas referencias cruzadas
        for category, refs in self.cross_references.items():
            if len(refs) > 10:
                suggestions.append({
                    'type': 'cross_reference',
                    'priority': 'medium',
                    'description': f'Categoría {category} tiene muchas referencias cruzadas',
                    'count': len(refs),
                    'suggested_action': f'Revisar organización de {category}'
                })
        
        # Sugerir archivos huérfanos (sin dependencias)
        orphan_files = []
        for file_path in self.project_root.rglob("*.md"):
            file_str = str(file_path)
            if file_str not in self.dependencies or len(self.dependencies[file_str]) == 0:
                # Verificar si es referenciado por otros archivos
                is_referenced = any(file_str in deps for deps in self.dependencies.values())
                if not is_referenced:
                    orphan_files.append(file_str)
        
        if orphan_files:
            suggestions.append({
                'type': 'orphan_files',
                'priority': 'low',
                'description': f'Archivos huérfanos encontrados',
                'count': len(orphan_files),
                'files': orphan_files[:10],  # Mostrar solo los primeros 10
                'suggested_action': 'Revisar si estos archivos son necesarios'
            })
        
        return suggestions
    
    def _normalize_reference(self, ref, source_file):
        """Normaliza una referencia de archivo"""
        # Remover fragmentos de URL
        ref = ref.split('#')[0].split('?')[0]
        
        # Si es una ruta relativa, convertir a absoluta
        if not ref.startswith('/') and not ref.startswith('http'):
            source_dir = source_file.parent
            ref_path = source_dir / ref
            if ref_path.exists():
                return str(ref_path.resolve())
        
        # Buscar archivo en el proyecto
        for file_path in self.project_root.rglob("*"):
            if file_path.name == ref or file_path.stem == ref:
                return str(file_path)
        
        return None
    
    def _get_file_category(self, file_path):
        """Obtiene la categoría de un archivo"""
        path = Path(file_path)
        for part in path.parts:
            if part.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_')):
                return part
        return None
    
    def _calculate_similarity(self, content1, content2):
        """Calcula similitud básica entre dos contenidos"""
        # Extraer palabras clave
        words1 = set(re.findall(r'\b\w+\b', content1.lower()))
        words2 = set(re.findall(r'\b\w+\b', content2.lower()))
        
        # Calcular similitud de Jaccard
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0
    
    def generate_dependency_report(self):
        """Genera reporte completo de dependencias"""
        self.analyze_file_dependencies()
        self.analyze_content_similarity()
        self.analyze_cross_references()
        
        suggestions = self.suggest_optimizations()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_files_analyzed': len(self.dependencies),
                'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
                'similar_files_found': len(self.content_similarity),
                'cross_references': len(self.cross_references),
                'suggestions_generated': len(suggestions)
            },
            'dependencies': dict(self.dependencies),
            'content_similarity': dict(self.content_similarity),
            'cross_references': dict(self.cross_references),
            'suggestions': suggestions
        }
        
        return report

if __name__ == "__main__":
    analyzer = DependencyAnalyzer("/Users/adan/frontier")
    
    print("🚀 Iniciando análisis de dependencias avanzado...")
    report = analyzer.generate_dependency_report()
    
    print(f"\n📊 RESUMEN DEL ANÁLISIS DE DEPENDENCIAS")
    print(f"Archivos analizados: {report['summary']['total_files_analyzed']}")
    print(f"Dependencias encontradas: {report['summary']['total_dependencies']}")
    print(f"Archivos similares: {report['summary']['similar_files_found']}")
    print(f"Referencias cruzadas: {report['summary']['cross_references']}")
    print(f"Sugerencias generadas: {report['summary']['suggestions_generated']}")
    
    if report['suggestions']:
        print(f"\n💡 SUGERENCIAS DE OPTIMIZACIÓN:")
        for i, suggestion in enumerate(report['suggestions'], 1):
            print(f"  {i}. [{suggestion['priority'].upper()}] {suggestion['description']}")
            if 'count' in suggestion:
                print(f"     Cantidad: {suggestion['count']}")
            if 'similarity' in suggestion:
                print(f"     Similitud: {suggestion['similarity']:.2%}")
    
    # Guardar reporte
    report_path = Path("/Users/adan/frontier") / "dependency_analysis_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Reporte guardado en: {report_path}")
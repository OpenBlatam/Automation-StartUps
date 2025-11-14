#!/usr/bin/env python3
"""
Optimizador Semántico Avanzado
Analiza contenido semántico y optimiza la organización basada en significado
"""

import os
import re
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
import difflib

class SemanticOptimizer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.content_analysis = defaultdict(dict)
        self.semantic_clusters = defaultdict(list)
        self.duplicate_detection = defaultdict(list)
        self.optimizations_applied = []
        
    def analyze_content_semantics(self):
        """Analiza el contenido semántico de todos los archivos"""
        print("🧠 Analizando contenido semántico...")
        
        text_files = []
        for file_path in self.project_root.rglob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    text_files.append((str(file_path), content))
            except:
                continue
        
        # Análisis semántico básico
        for file_path, content in text_files:
            analysis = self._analyze_file_semantics(content)
            self.content_analysis[file_path] = analysis
            
            # Detectar duplicados
            content_hash = hashlib.md5(content.encode()).hexdigest()
            self.duplicate_detection[content_hash].append(file_path)
    
    def create_semantic_clusters(self):
        """Crea clusters semánticos basados en contenido similar"""
        print("🔗 Creando clusters semánticos...")
        
        # Agrupar archivos por temas semánticos
        topic_clusters = defaultdict(list)
        
        for file_path, analysis in self.content_analysis.items():
            main_topics = analysis.get('main_topics', [])
            for topic in main_topics:
                topic_clusters[topic].append(file_path)
        
        # Crear clusters por similitud de contenido
        for file_path, analysis in self.content_analysis.items():
            content_vector = analysis.get('content_vector', [])
            if content_vector:
                # Buscar archivos similares
                similar_files = []
                for other_file, other_analysis in self.content_analysis.items():
                    if file_path != other_file:
                        other_vector = other_analysis.get('content_vector', [])
                        if other_vector:
                            similarity = self._calculate_vector_similarity(content_vector, other_vector)
                            if similarity > 0.7:  # Umbral de similitud
                                similar_files.append((other_file, similarity))
                
                if similar_files:
                    cluster_id = f"cluster_{len(self.semantic_clusters)}"
                    self.semantic_clusters[cluster_id] = [file_path] + [f[0] for f in similar_files]
    
    def detect_and_handle_duplicates(self):
        """Detecta y maneja archivos duplicados"""
        print("🔍 Detectando duplicados...")
        
        duplicates_handled = 0
        for content_hash, files in self.duplicate_detection.items():
            if len(files) > 1:
                print(f"  📄 Duplicados encontrados: {len(files)} archivos")
                
                # Mantener el archivo más reciente y mover otros a archivo
                files_with_dates = []
                for file_path in files:
                    try:
                        stat = Path(file_path).stat()
                        files_with_dates.append((file_path, stat.st_mtime))
                    except:
                        files_with_dates.append((file_path, 0))
                
                files_with_dates.sort(key=lambda x: x[1], reverse=True)
                keep_file = files_with_dates[0][0]
                duplicate_files = [f[0] for f in files_with_dates[1:]]
                
                # Crear directorio de duplicados
                duplicates_dir = self.project_root / "99_Duplicates"
                duplicates_dir.mkdir(exist_ok=True)
                
                for dup_file in duplicate_files:
                    try:
                        target_path = duplicates_dir / Path(dup_file).name
                        if not target_path.exists():
                            os.rename(dup_file, str(target_path))
                            self.optimizations_applied.append(f"Moved duplicate {Path(dup_file).name} to Duplicates")
                            duplicates_handled += 1
                    except Exception as e:
                        print(f"    ❌ Error moviendo {dup_file}: {e}")
        
        print(f"  ✅ Duplicados manejados: {duplicates_handled}")
    
    def optimize_semantic_clusters(self):
        """Optimiza la organización basada en clusters semánticos"""
        print("🎯 Optimizando clusters semánticos...")
        
        for cluster_id, files in self.semantic_clusters.items():
            if len(files) > 2:  # Solo clusters con más de 2 archivos
                print(f"  📁 Optimizando cluster {cluster_id} con {len(files)} archivos")
                
                # Determinar categoría objetivo basada en mayoría
                categories = [self._get_file_category(f) for f in files]
                category_counts = Counter(categories)
                target_category = category_counts.most_common(1)[0][0]
                
                if target_category:
                    # Crear subcategoría para el cluster
                    cluster_dir = self.project_root / target_category / f"Semantic_Cluster_{cluster_id}"
                    cluster_dir.mkdir(exist_ok=True)
                    
                    # Mover archivos del cluster
                    for file_path in files:
                        if self._get_file_category(file_path) != target_category:
                            try:
                                target_path = cluster_dir / Path(file_path).name
                                if not target_path.exists():
                                    os.rename(file_path, str(target_path))
                                    self.optimizations_applied.append(f"Moved {Path(file_path).name} to semantic cluster")
                            except Exception as e:
                                print(f"    ❌ Error moviendo {file_path}: {e}")
    
    def create_semantic_index(self):
        """Crea un índice semántico del proyecto"""
        print("📚 Creando índice semántico...")
        
        semantic_index = {
            'timestamp': datetime.now().isoformat(),
            'total_files_analyzed': len(self.content_analysis),
            'semantic_clusters': len(self.semantic_clusters),
            'duplicates_found': sum(len(files) - 1 for files in self.duplicate_detection.values() if len(files) > 1),
            'topics': defaultdict(int),
            'clusters': dict(self.semantic_clusters),
            'content_analysis': dict(self.content_analysis)
        }
        
        # Contar temas principales
        for analysis in self.content_analysis.values():
            for topic in analysis.get('main_topics', []):
                semantic_index['topics'][topic] += 1
        
        # Guardar índice semántico
        index_path = self.project_root / "97_Analysis_Reports" / "semantic_index.json"
        index_path.parent.mkdir(exist_ok=True)
        
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(semantic_index, f, indent=2, ensure_ascii=False)
        
        print(f"  💾 Índice semántico guardado en: {index_path}")
    
    def create_content_relationships_map(self):
        """Crea un mapa de relaciones de contenido"""
        print("🗺️  Creando mapa de relaciones de contenido...")
        
        relationships_file = self.project_root / "00_Version_Management" / "CONTENT_RELATIONSHIPS.md"
        relationships_file.parent.mkdir(exist_ok=True)
        
        with open(relationships_file, 'w', encoding='utf-8') as f:
            f.write("# Mapa de Relaciones de Contenido\n\n")
            f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Clusters Semánticos\n\n")
            for cluster_id, files in self.semantic_clusters.items():
                f.write(f"### Cluster {cluster_id} ({len(files)} archivos)\n\n")
                for file_path in files:
                    f.write(f"- `{Path(file_path).name}`\n")
                f.write("\n")
            
            f.write("## Temas Principales\n\n")
            topic_counts = Counter()
            for analysis in self.content_analysis.values():
                for topic in analysis.get('main_topics', []):
                    topic_counts[topic] += 1
            
            for topic, count in topic_counts.most_common(20):
                f.write(f"- **{topic}**: {count} archivos\n")
            
            f.write("\n## Archivos Duplicados\n\n")
            for content_hash, files in self.duplicate_detection.items():
                if len(files) > 1:
                    f.write(f"### Hash: {content_hash[:8]}... ({len(files)} archivos)\n")
                    for file_path in files:
                        f.write(f"- `{Path(file_path).name}`\n")
                    f.write("\n")
    
    def _analyze_file_semantics(self, content):
        """Analiza el contenido semántico de un archivo"""
        # Extraer palabras clave principales
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        word_freq = Counter(words)
        
        # Filtrar palabras comunes
        common_words = {'the', 'and', 'for', 'are', 'with', 'this', 'that', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 'which', 'their', 'time', 'will', 'about', 'if', 'up', 'out', 'many', 'then', 'them', 'can', 'only', 'other', 'new', 'some', 'what', 'your', 'when', 'very', 'just', 'into', 'over', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'most', 'its', 'no', 'may', 'say', 'she', 'these', 'him', 'more', 'go', 'see', 'number', 'no', 'way', 'could', 'people', 'my', 'than', 'first', 'water', 'been', 'call', 'who', 'oil', 'its', 'now', 'find', 'long', 'down', 'day', 'did', 'get', 'come', 'made', 'may', 'part'}
        
        filtered_words = {word: count for word, count in word_freq.items() 
                         if word not in common_words and len(word) > 3}
        
        # Identificar temas principales
        main_topics = list(dict(Counter(filtered_words).most_common(10)).keys())
        
        # Crear vector de contenido
        content_vector = list(filtered_words.keys())[:50]  # Top 50 palabras
        
        return {
            'word_count': len(words),
            'unique_words': len(set(words)),
            'main_topics': main_topics,
            'content_vector': content_vector,
            'top_words': dict(Counter(filtered_words).most_common(20))
        }
    
    def _calculate_vector_similarity(self, vec1, vec2):
        """Calcula similitud entre dos vectores de contenido"""
        if not vec1 or not vec2:
            return 0
        
        set1 = set(vec1)
        set2 = set(vec2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0
    
    def _get_file_category(self, file_path):
        """Obtiene la categoría de un archivo"""
        path = Path(file_path)
        for part in path.parts:
            if part.startswith(('01_', '02_', '03_', '04_', '05_', '06_', '07_', '08_', '09_', '10_', '97_', '98_', '99_')):
                return part
        return None
    
    def run_semantic_optimization(self):
        """Ejecuta la optimización semántica completa"""
        print("🚀 Iniciando optimización semántica avanzada...")
        
        self.analyze_content_semantics()
        self.create_semantic_clusters()
        self.detect_and_handle_duplicates()
        self.optimize_semantic_clusters()
        self.create_semantic_index()
        self.create_content_relationships_map()
        
        print(f"\n✅ Optimización semántica completada!")
        print(f"Mejoras aplicadas: {len(self.optimizations_applied)}")
        
        return self.optimizations_applied

if __name__ == "__main__":
    optimizer = SemanticOptimizer("/Users/adan/frontier")
    optimizations = optimizer.run_semantic_optimization()
    
    print(f"\n📋 RESUMEN DE OPTIMIZACIONES SEMÁNTICAS:")
    for i, opt in enumerate(optimizations, 1):
        print(f"  {i:3d}. {opt}")



#!/usr/bin/env python3
"""
Advanced Indexing System - Sistema de Indexación Avanzada
Crea índices inteligentes y sistemas de búsqueda avanzados
"""

import os
import json
import re
import sqlite3
from datetime import datetime
from collections import defaultdict, Counter
import argparse

class AdvancedIndexingSystem:
    def __init__(self, root_path=".", db_path="content_index.db"):
        self.root_path = root_path
        self.db_path = db_path
        self.index_data = {
            "timestamp": datetime.now().isoformat(),
            "total_files": 0,
            "indexed_files": 0,
            "categories": defaultdict(int),
            "tags": defaultdict(int),
            "keywords": defaultdict(int),
            "file_relationships": defaultdict(list),
            "search_index": {}
        }
    
    def create_database(self):
        """Crea la base de datos SQLite para el índice"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de archivos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE,
                filename TEXT,
                category TEXT,
                file_type TEXT,
                size INTEGER,
                lines INTEGER,
                words INTEGER,
                last_modified TEXT,
                content_hash TEXT
            )
        ''')
        
        # Tabla de contenido
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                section_title TEXT,
                content TEXT,
                section_type TEXT,
                position INTEGER,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        # Tabla de tags
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                tag TEXT,
                tag_type TEXT,
                position INTEGER,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        # Tabla de keywords
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                keyword TEXT,
                frequency INTEGER,
                context TEXT,
                FOREIGN KEY (file_id) REFERENCES files (id)
            )
        ''')
        
        # Tabla de relaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_file_id INTEGER,
                target_file_id INTEGER,
                relationship_type TEXT,
                strength REAL,
                FOREIGN KEY (source_file_id) REFERENCES files (id),
                FOREIGN KEY (target_file_id) REFERENCES files (id)
            )
        ''')
        
        # Índices para búsqueda rápida
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_category ON files (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_type ON files (file_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags (tag)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_keywords_keyword ON keywords (keyword)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_section ON content (section_title)')
        
        conn.commit()
        conn.close()
    
    def index_file(self, file_path):
        """Indexa un archivo individual"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Información básica del archivo
            file_info = {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size": len(content),
                "lines": len(content.split('\n')),
                "words": len(content.split()),
                "last_modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat(),
                "content_hash": hash(content)
            }
            
            # Detectar categoría y tipo
            file_info["category"] = self.detect_category(file_path, content)
            file_info["file_type"] = self.detect_file_type(file_path, content)
            
            # Extraer secciones
            sections = self.extract_sections(content)
            
            # Extraer tags
            tags = self.extract_tags(content)
            
            # Extraer keywords
            keywords = self.extract_keywords(content)
            
            # Detectar relaciones
            relationships = self.detect_relationships(file_path, content)
            
            return {
                "file_info": file_info,
                "sections": sections,
                "tags": tags,
                "keywords": keywords,
                "relationships": relationships
            }
            
        except Exception as e:
            print(f"Error indexando {file_path}: {e}")
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
    
    def extract_sections(self, content):
        """Extrae secciones del contenido"""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            "title": "Inicio",
            "content": "",
            "type": "introduction",
            "position": 0
        }
        
        for i, line in enumerate(lines):
            # Detectar headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Guardar sección anterior
                if current_section["content"]:
                    current_section["content"] = current_section["content"].strip()
                    sections.append(current_section.copy())
                
                # Iniciar nueva sección
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                # Determinar tipo de sección
                section_type = self.determine_section_type(title, level)
                
                current_section = {
                    "title": title,
                    "content": line + '\n',
                    "type": section_type,
                    "position": i
                }
            else:
                current_section["content"] += line + '\n'
        
        # Agregar última sección
        if current_section["content"]:
            current_section["content"] = current_section["content"].strip()
            sections.append(current_section)
        
        return sections
    
    def determine_section_type(self, title, level):
        """Determina el tipo de sección basado en el título y nivel"""
        title_lower = title.lower()
        
        if level == 1:
            return "main_title"
        elif level == 2:
            if any(word in title_lower for word in ['introducción', 'introduction', 'resumen', 'summary']):
                return "introduction"
            elif any(word in title_lower for word in ['conclusión', 'conclusion', 'resumen', 'summary']):
                return "conclusion"
            elif any(word in title_lower for word in ['método', 'method', 'proceso', 'process']):
                return "methodology"
            elif any(word in title_lower for word in ['resultado', 'result', 'análisis', 'analysis']):
                return "results"
            else:
                return "section"
        elif level == 3:
            return "subsection"
        else:
            return "detail"
    
    def extract_tags(self, content):
        """Extrae tags del contenido"""
        tags = []
        
        # Tags en metadatos YAML
        yaml_match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            tag_matches = re.findall(r'tags?:\s*\[(.*?)\]', yaml_content)
            for match in tag_matches:
                tag_list = [tag.strip().strip('"\'') for tag in match.split(',')]
                for tag in tag_list:
                    if tag:
                        tags.append({"tag": tag, "type": "yaml", "position": 0})
        
        # Tags en el contenido (#tag)
        tag_matches = re.findall(r'#(\w+)', content)
        for i, tag in enumerate(tag_matches):
            tags.append({"tag": tag, "type": "content", "position": i})
        
        # Tags por categoría de contenido
        content_lower = content.lower()
        category_tags = []
        
        if 'vc' in content_lower or 'venture' in content_lower:
            category_tags.append("vc")
        if 'marketing' in content_lower:
            category_tags.append("marketing")
        if 'ai' in content_lower or 'artificial intelligence' in content_lower:
            category_tags.append("ai")
        if 'strategy' in content_lower:
            category_tags.append("strategy")
        if 'template' in content_lower:
            category_tags.append("template")
        if 'analysis' in content_lower:
            category_tags.append("analysis")
        
        for tag in category_tags:
            tags.append({"tag": tag, "type": "category", "position": 0})
        
        return tags
    
    def extract_keywords(self, content):
        """Extrae palabras clave del contenido"""
        # Limpiar contenido
        content_clean = re.sub(r'[^\w\s]', ' ', content.lower())
        words = content_clean.split()
        
        # Filtrar palabras comunes
        stop_words = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esa', 'esos', 'estas', 'estos', 'otra', 'otras', 'otro', 'otros', 'otra', 'otras'
        }
        
        # Contar palabras
        word_count = Counter()
        for word in words:
            if len(word) > 3 and word not in stop_words:
                word_count[word] += 1
        
        # Obtener keywords más frecuentes
        keywords = []
        for word, count in word_count.most_common(20):
            # Buscar contexto de la palabra
            context = self.find_keyword_context(content, word)
            keywords.append({
                "keyword": word,
                "frequency": count,
                "context": context
            })
        
        return keywords
    
    def find_keyword_context(self, content, keyword):
        """Encuentra el contexto de una palabra clave"""
        pattern = rf'\b{re.escape(keyword)}\b'
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        
        if matches:
            # Tomar el primer match y extraer contexto
            match = matches[0]
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].strip()
            return context
        
        return ""
    
    def detect_relationships(self, file_path, content):
        """Detecta relaciones entre archivos"""
        relationships = []
        
        # Enlaces internos
        internal_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for link_text, link_url in internal_links:
            if not link_url.startswith('http') and not link_url.startswith('#'):
                relationships.append({
                    "type": "internal_link",
                    "target": link_url,
                    "text": link_text,
                    "strength": 0.8
                })
        
        # Referencias a otros archivos
        file_references = re.findall(r'`([^`]+\.md)`', content)
        for ref in file_references:
            relationships.append({
                "type": "file_reference",
                "target": ref,
                "text": ref,
                "strength": 0.6
            })
        
        # Referencias por nombre de archivo
        filename = os.path.basename(file_path)
        if 'vc' in filename.lower():
            relationships.append({
                "type": "category_relation",
                "target": "vc",
                "text": "Venture Capital",
                "strength": 0.9
            })
        elif 'marketing' in filename.lower():
            relationships.append({
                "type": "category_relation",
                "target": "marketing",
                "text": "Marketing",
                "strength": 0.9
            })
        
        return relationships
    
    def save_to_database(self, file_data):
        """Guarda los datos indexados en la base de datos"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insertar archivo
            file_info = file_data["file_info"]
            cursor.execute('''
                INSERT OR REPLACE INTO files 
                (path, filename, category, file_type, size, lines, words, last_modified, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_info["path"], file_info["filename"], file_info["category"],
                file_info["file_type"], file_info["size"], file_info["lines"],
                file_info["words"], file_info["last_modified"], file_info["content_hash"]
            ))
            
            file_id = cursor.lastrowid
            
            # Insertar secciones
            for section in file_data["sections"]:
                cursor.execute('''
                    INSERT INTO content (file_id, section_title, content, section_type, position)
                    VALUES (?, ?, ?, ?, ?)
                ''', (file_id, section["title"], section["content"], section["type"], section["position"]))
            
            # Insertar tags
            for tag in file_data["tags"]:
                cursor.execute('''
                    INSERT INTO tags (file_id, tag, tag_type, position)
                    VALUES (?, ?, ?, ?)
                ''', (file_id, tag["tag"], tag["type"], tag["position"]))
            
            # Insertar keywords
            for keyword in file_data["keywords"]:
                cursor.execute('''
                    INSERT INTO keywords (file_id, keyword, frequency, context)
                    VALUES (?, ?, ?, ?)
                ''', (file_id, keyword["keyword"], keyword["frequency"], keyword["context"]))
            
            # Insertar relaciones
            for rel in file_data["relationships"]:
                cursor.execute('''
                    INSERT INTO relationships (source_file_id, target_file_id, relationship_type, strength)
                    VALUES (?, ?, ?, ?)
                ''', (file_id, rel["target"], rel["type"], rel["strength"]))
            
            conn.commit()
            
        except Exception as e:
            print(f"Error guardando en base de datos: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def build_index(self):
        """Construye el índice completo"""
        print("🔍 Construyendo índice avanzado...")
        
        # Crear base de datos
        self.create_database()
        
        # Encontrar todos los archivos markdown
        markdown_files = []
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.md'):
                    markdown_files.append(os.path.join(root, file))
        
        print(f"📄 Encontrados {len(markdown_files)} archivos markdown")
        
        # Indexar cada archivo
        for file_path in markdown_files:
            print(f"📊 Indexando: {os.path.basename(file_path)}")
            
            file_data = self.index_file(file_path)
            if file_data:
                self.save_to_database(file_data)
                self.index_data["indexed_files"] += 1
                
                # Actualizar estadísticas
                file_info = file_data["file_info"]
                self.index_data["categories"][file_info["category"]] += 1
                
                for tag in file_data["tags"]:
                    self.index_data["tags"][tag["tag"]] += 1
                
                for keyword in file_data["keywords"]:
                    self.index_data["keywords"][keyword["keyword"]] += keyword["frequency"]
        
        self.index_data["total_files"] = len(markdown_files)
        
        print("✅ Índice construido exitosamente")
        return self.index_data
    
    def search(self, query, limit=10):
        """Busca en el índice"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Búsqueda en contenido
        cursor.execute('''
            SELECT f.path, f.filename, f.category, c.section_title, c.content
            FROM files f
            JOIN content c ON f.id = c.file_id
            WHERE c.content LIKE ? OR c.section_title LIKE ?
            ORDER BY f.category, f.filename
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def get_recommendations(self, file_path, limit=5):
        """Obtiene recomendaciones basadas en relaciones"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Buscar archivos relacionados
        cursor.execute('''
            SELECT DISTINCT f2.path, f2.filename, f2.category, r.relationship_type, r.strength
            FROM files f1
            JOIN relationships r ON f1.id = r.source_file_id
            JOIN files f2 ON r.target_file_id = f2.id
            WHERE f1.path = ?
            ORDER BY r.strength DESC
            LIMIT ?
        ''', (file_path, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        return results
    
    def save_report(self, output_file="advanced_indexing_report.json"):
        """Guarda el reporte de indexación"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.index_data, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen del índice"""
        print("\n" + "="*60)
        print("📊 RESUMEN DEL ÍNDICE AVANZADO")
        print("="*60)
        
        print(f"📄 Total archivos: {self.index_data['total_files']}")
        print(f"📊 Archivos indexados: {self.index_data['indexed_files']}")
        print(f"🗄️  Base de datos: {self.db_path}")
        
        print("\n📂 Archivos por categoría:")
        for category, count in sorted(self.index_data['categories'].items()):
            print(f"  {category}: {count}")
        
        print("\n🏷️  Tags más comunes:")
        for tag, count in Counter(self.index_data['tags']).most_common(10):
            print(f"  #{tag}: {count}")
        
        print("\n🔤 Keywords más comunes:")
        for keyword, count in Counter(self.index_data['keywords']).most_common(10):
            print(f"  {keyword}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Sistema de indexación avanzada')
    parser.add_argument('--path', default='.', help='Ruta del directorio a indexar')
    parser.add_argument('--db', default='content_index.db', help='Archivo de base de datos')
    parser.add_argument('--output', default='advanced_indexing_report.json', help='Archivo de reporte')
    parser.add_argument('--search', help='Término de búsqueda')
    parser.add_argument('--recommendations', help='Archivo para obtener recomendaciones')
    
    args = parser.parse_args()
    
    indexer = AdvancedIndexingSystem(args.path, args.db)
    
    if args.search:
        # Buscar
        results = indexer.search(args.search)
        print(f"🔍 Resultados para '{args.search}':")
        for result in results:
            print(f"  - {result[1]} ({result[2]}) - {result[3]}")
    elif args.recommendations:
        # Recomendaciones
        results = indexer.get_recommendations(args.recommendations)
        print(f"💡 Recomendaciones para '{args.recommendations}':")
        for result in results:
            print(f"  - {result[1]} ({result[2]}) - {result[3]} (strength: {result[4]})")
    else:
        # Construir índice
        indexer.build_index()
        indexer.save_report(args.output)
        indexer.print_summary()

if __name__ == "__main__":
    main()















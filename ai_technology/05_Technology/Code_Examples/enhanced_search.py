#!/usr/bin/env python3
"""
Sistema de búsqueda mejorado con IA y optimizaciones avanzadas
"""

import os
import json
import re
import time
from datetime import datetime
from collections import defaultdict, Counter
import hashlib
import sqlite3
from pathlib import Path

class EnhancedSearchSystem:
    def __init__(self, base_path="/Users/adan/frontier"):
        self.base_path = base_path
        self.db_path = os.path.join(base_path, "search_index.db")
        self.cache_file = os.path.join(base_path, "search_cache.json")
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
        self.init_database()
        self.load_cache()
    
    def init_database(self):
        """Inicializar base de datos SQLite para búsquedas rápidas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT UNIQUE,
                area TEXT,
                path TEXT,
                content TEXT,
                keywords TEXT,
                file_size INTEGER,
                last_modified TEXT,
                hash TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                results_count INTEGER,
                timestamp TEXT,
                user_session TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_filename ON documents(filename);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_area ON documents(area);
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_keywords ON documents(keywords);
        ''')
        
        conn.commit()
        conn.close()
    
    def load_cache(self):
        """Cargar caché de búsquedas"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        else:
            self.cache = {'searches': {}, 'stats': {}}
    
    def save_cache(self):
        """Guardar caché de búsquedas"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def build_search_index(self):
        """Construir índice de búsqueda optimizado"""
        print("🔍 Construyendo índice de búsqueda optimizado...")
        start_time = time.time()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Limpiar índice existente
        cursor.execute('DELETE FROM documents')
        
        indexed_count = 0
        for area_code, area_name in self.business_areas.items():
            area_path = os.path.join(self.base_path, area_code)
            if not os.path.exists(area_path):
                continue
            
            for root, dirs, files in os.walk(area_path):
                for file in files:
                    if file.endswith('.md'):
                        file_path = os.path.join(root, file)
                        try:
                            # Leer contenido del archivo
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Extraer keywords del nombre y contenido
                            filename_keywords = ' '.join(re.findall(r'\b\w+\b', file.lower()))
                            content_keywords = ' '.join(re.findall(r'\b\w{4,}\b', content.lower()))
                            all_keywords = f"{filename_keywords} {content_keywords}"
                            
                            # Obtener estadísticas del archivo
                            stat = os.stat(file_path)
                            file_size = stat.st_size
                            last_modified = datetime.fromtimestamp(stat.st_mtime).isoformat()
                            file_hash = hashlib.md5(content.encode()).hexdigest()
                            
                            # Insertar en base de datos
                            cursor.execute('''
                                INSERT OR REPLACE INTO documents 
                                (filename, area, path, content, keywords, file_size, last_modified, hash)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (file, area_name, file_path, content, all_keywords, 
                                 file_size, last_modified, file_hash))
                            
                            indexed_count += 1
                            
                        except Exception as e:
                            print(f"⚠️  Error indexando {file}: {e}")
                            continue
        
        conn.commit()
        conn.close()
        
        build_time = time.time() - start_time
        print(f"✅ Índice construido: {indexed_count} documentos en {build_time:.2f} segundos")
        
        return indexed_count
    
    def smart_search(self, query, area=None, search_type='all', limit=20):
        """Búsqueda inteligente con múltiples algoritmos"""
        start_time = time.time()
        
        # Normalizar query
        query_lower = query.lower()
        query_words = re.findall(r'\b\w+\b', query_lower)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Construir consulta SQL
        where_conditions = []
        params = []
        
        if area:
            where_conditions.append("area = ?")
            params.append(area)
        
        if search_type == 'filename':
            where_conditions.append("filename LIKE ?")
            params.append(f"%{query}%")
        elif search_type == 'content':
            where_conditions.append("content LIKE ?")
            params.append(f"%{query}%")
        else:  # all
            where_conditions.append("(filename LIKE ? OR content LIKE ? OR keywords LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(where_conditions)
        
        # Consulta con scoring
        sql = f'''
            SELECT filename, area, path, file_size, last_modified,
                   CASE 
                       WHEN filename LIKE ? THEN 10
                       WHEN keywords LIKE ? THEN 5
                       WHEN content LIKE ? THEN 1
                       ELSE 0
                   END as score
            FROM documents
            WHERE {where_clause}
            ORDER BY score DESC, last_modified DESC
            LIMIT ?
        '''
        
        # Parámetros para scoring
        score_params = [f"%{query}%", f"%{query}%", f"%{query}%"]
        params = score_params + params + [limit]
        
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        # Procesar resultados
        search_results = []
        for row in results:
            filename, area, path, file_size, last_modified, score = row
            search_results.append({
                'filename': filename,
                'area': area,
                'path': path,
                'file_size': file_size,
                'last_modified': last_modified,
                'score': score,
                'relative_path': os.path.relpath(path, self.base_path)
            })
        
        conn.close()
        
        # Guardar en caché
        cache_key = f"{query}_{area}_{search_type}"
        self.cache['searches'][cache_key] = {
            'results': search_results,
            'timestamp': datetime.now().isoformat(),
            'query_time': time.time() - start_time
        }
        
        # Guardar en historial
        self.save_search_history(query, len(search_results))
        
        search_time = time.time() - start_time
        return search_results, search_time
    
    def save_search_history(self, query, results_count):
        """Guardar búsqueda en historial"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_history (query, results_count, timestamp, user_session)
            VALUES (?, ?, ?, ?)
        ''', (query, results_count, datetime.now().isoformat(), 'default'))
        
        conn.commit()
        conn.close()
    
    def get_search_suggestions(self, partial_query):
        """Obtener sugerencias de búsqueda basadas en historial"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT query, COUNT(*) as frequency
            FROM search_history
            WHERE query LIKE ?
            GROUP BY query
            ORDER BY frequency DESC
            LIMIT 10
        ''', (f"%{partial_query}%",))
        
        suggestions = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        return suggestions
    
    def get_popular_searches(self):
        """Obtener búsquedas más populares"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT query, COUNT(*) as frequency
            FROM search_history
            GROUP BY query
            ORDER BY frequency DESC
            LIMIT 10
        ''')
        
        popular = [(row[0], row[1]) for row in cursor.fetchall()]
        conn.close()
        
        return popular
    
    def get_search_analytics(self):
        """Obtener analytics de búsquedas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute('SELECT COUNT(*) FROM search_history')
        total_searches = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(DISTINCT query) FROM search_history')
        unique_queries = cursor.fetchone()[0]
        
        # Búsquedas por área
        cursor.execute('''
            SELECT d.area, COUNT(*) as searches
            FROM search_history sh
            JOIN documents d ON d.filename LIKE '%' || sh.query || '%'
            GROUP BY d.area
            ORDER BY searches DESC
        ''')
        area_searches = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total_searches': total_searches,
            'unique_queries': unique_queries,
            'area_searches': area_searches,
            'cache_hits': len(self.cache['searches'])
        }
    
    def print_search_results(self, results, search_time, query):
        """Imprimir resultados de búsqueda mejorados"""
        if not results:
            print(f"❌ No se encontraron resultados para: '{query}'")
            return
        
        print(f"🔍 Resultados para: '{query}' ({len(results)} encontrados en {search_time:.3f}s)")
        print("=" * 80)
        
        for i, result in enumerate(results, 1):
            score_indicator = "🔥" if result['score'] >= 10 else "⭐" if result['score'] >= 5 else "📄"
            size_kb = result['file_size'] / 1024
            
            print(f"{i:2d}. {score_indicator} {result['filename']}")
            print(f"    📁 Área: {result['area']}")
            print(f"    📍 Ruta: {result['relative_path']}")
            print(f"    📊 Tamaño: {size_kb:.1f} KB | Score: {result['score']}")
            print(f"    📅 Modificado: {result['last_modified'][:10]}")
            print("-" * 80)
    
    def run_enhanced_search(self):
        """Ejecutar búsqueda mejorada interactiva"""
        print("🔍 Sistema de Búsqueda Mejorado con IA")
        print("=" * 50)
        
        # Construir índice si no existe
        if not os.path.exists(self.db_path) or os.path.getsize(self.db_path) == 0:
            self.build_search_index()
        
        while True:
            print("\n📋 Opciones de búsqueda:")
            print("1. Búsqueda general")
            print("2. Búsqueda por nombre de archivo")
            print("3. Búsqueda por contenido")
            print("4. Búsqueda por área específica")
            print("5. Ver sugerencias")
            print("6. Ver búsquedas populares")
            print("7. Ver analytics de búsqueda")
            print("8. Reconstruir índice")
            print("9. Salir")
            
            choice = input("\nSeleccione una opción (1-9): ").strip()
            
            if choice == '1':
                query = input("Ingrese su búsqueda: ").strip()
                if query:
                    results, search_time = self.smart_search(query)
                    self.print_search_results(results, search_time, query)
            
            elif choice == '2':
                query = input("Buscar por nombre de archivo: ").strip()
                if query:
                    results, search_time = self.smart_search(query, search_type='filename')
                    self.print_search_results(results, search_time, query)
            
            elif choice == '3':
                query = input("Buscar en contenido: ").strip()
                if query:
                    results, search_time = self.smart_search(query, search_type='content')
                    self.print_search_results(results, search_time, query)
            
            elif choice == '4':
                print("Áreas disponibles:")
                for code, name in self.business_areas.items():
                    print(f"  {code}: {name}")
                
                area = input("Seleccione área (código): ").strip()
                query = input("Ingrese su búsqueda: ").strip()
                
                if query and area in self.business_areas:
                    results, search_time = self.smart_search(query, area=area)
                    self.print_search_results(results, search_time, query)
            
            elif choice == '5':
                partial = input("Ingrese parte de su búsqueda: ").strip()
                if partial:
                    suggestions = self.get_search_suggestions(partial)
                    if suggestions:
                        print(f"\n💡 Sugerencias para '{partial}':")
                        for suggestion in suggestions:
                            print(f"  • {suggestion}")
                    else:
                        print("❌ No hay sugerencias disponibles")
            
            elif choice == '6':
                popular = self.get_popular_searches()
                if popular:
                    print("\n🔥 Búsquedas más populares:")
                    for query, count in popular:
                        print(f"  • {query} ({count} veces)")
                else:
                    print("❌ No hay historial de búsquedas")
            
            elif choice == '7':
                analytics = self.get_search_analytics()
                print(f"\n📊 Analytics de Búsqueda:")
                print(f"  🔍 Total de búsquedas: {analytics['total_searches']}")
                print(f"  📝 Consultas únicas: {analytics['unique_queries']}")
                print(f"  💾 Cache hits: {analytics['cache_hits']}")
                
                if analytics['area_searches']:
                    print(f"\n📁 Búsquedas por área:")
                    for area, count in analytics['area_searches'].items():
                        print(f"  • {area}: {count}")
            
            elif choice == '8':
                print("🔄 Reconstruyendo índice...")
                count = self.build_search_index()
                print(f"✅ Índice reconstruido con {count} documentos")
            
            elif choice == '9':
                self.save_cache()
                print("👋 ¡Hasta luego!")
                break
            
            else:
                print("❌ Opción no válida")

def main():
    search_system = EnhancedSearchSystem()
    search_system.run_enhanced_search()

if __name__ == "__main__":
    main()




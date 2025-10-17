#!/usr/bin/env python3
"""
Large Files Optimizer - Optimizador de Archivos Grandes
Divide y optimiza archivos markdown grandes para mejor manejo
"""

import os
import re
import argparse
from datetime import datetime

class LargeFilesOptimizer:
    def __init__(self, root_path="."):
        self.root_path = root_path
        self.optimization_results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": [],
            "files_created": [],
            "total_size_reduction": 0,
            "recommendations": []
        }
    
    def analyze_large_file(self, file_path, size_threshold=50000):
        """Analiza un archivo grande y determina cómo dividirlo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = len(content)
            lines = content.split('\n')
            total_lines = len(lines)
            
            if file_size < size_threshold:
                return None
            
            analysis = {
                "file_path": file_path,
                "size": file_size,
                "lines": total_lines,
                "sections": [],
                "recommended_divisions": [],
                "optimization_opportunities": []
            }
            
            # Detectar secciones por headers
            sections = self.detect_sections(content)
            analysis["sections"] = sections
            
            # Recomendar divisiones
            divisions = self.recommend_divisions(sections, file_size)
            analysis["recommended_divisions"] = divisions
            
            # Oportunidades de optimización
            optimizations = self.find_optimization_opportunities(content)
            analysis["optimization_opportunities"] = optimizations
            
            return analysis
            
        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return None
    
    def detect_sections(self, content):
        """Detecta secciones en el contenido basado en headers"""
        sections = []
        lines = content.split('\n')
        
        current_section = {
            "title": "Inicio",
            "level": 0,
            "start_line": 0,
            "end_line": 0,
            "content": "",
            "size": 0
        }
        
        for i, line in enumerate(lines):
            # Detectar headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            
            if header_match:
                # Guardar sección anterior
                if current_section["content"]:
                    current_section["end_line"] = i - 1
                    current_section["size"] = len(current_section["content"])
                    sections.append(current_section.copy())
                
                # Iniciar nueva sección
                level = len(header_match.group(1))
                title = header_match.group(2).strip()
                
                current_section = {
                    "title": title,
                    "level": level,
                    "start_line": i,
                    "end_line": i,
                    "content": line + '\n',
                    "size": len(line)
                }
            else:
                current_section["content"] += line + '\n'
                current_section["size"] += len(line) + 1
        
        # Agregar última sección
        if current_section["content"]:
            current_section["end_line"] = len(lines) - 1
            sections.append(current_section)
        
        return sections
    
    def recommend_divisions(self, sections, total_size):
        """Recomienda cómo dividir el archivo"""
        divisions = []
        target_size = 10000  # 10KB por archivo
        current_group = []
        current_size = 0
        
        for section in sections:
            # Si agregar esta sección excede el tamaño objetivo
            if current_size + section["size"] > target_size and current_group:
                # Crear división
                division = {
                    "title": self.generate_division_title(current_group),
                    "sections": current_group.copy(),
                    "total_size": current_size,
                    "recommended_filename": self.generate_filename(current_group[0]["title"])
                }
                divisions.append(division)
                
                # Reiniciar grupo
                current_group = [section]
                current_size = section["size"]
            else:
                current_group.append(section)
                current_size += section["size"]
        
        # Agregar último grupo
        if current_group:
            division = {
                "title": self.generate_division_title(current_group),
                "sections": current_group.copy(),
                "total_size": current_size,
                "recommended_filename": self.generate_filename(current_group[0]["title"])
            }
            divisions.append(division)
        
        return divisions
    
    def generate_division_title(self, sections):
        """Genera un título para la división"""
        if len(sections) == 1:
            return sections[0]["title"]
        else:
            return f"{sections[0]['title']} y {len(sections)-1} secciones más"
    
    def generate_filename(self, title):
        """Genera un nombre de archivo basado en el título"""
        # Limpiar título
        filename = re.sub(r'[^\w\s-]', '', title)
        filename = re.sub(r'[-\s]+', '_', filename)
        filename = filename.lower()
        
        # Limitar longitud
        if len(filename) > 50:
            filename = filename[:50]
        
        return f"{filename}.md"
    
    def find_optimization_opportunities(self, content):
        """Encuentra oportunidades de optimización"""
        opportunities = []
        
        # Líneas vacías excesivas
        empty_lines = content.count('\n\n\n')
        if empty_lines > 10:
            opportunities.append({
                "type": "cleanup",
                "description": f"Eliminar {empty_lines} grupos de líneas vacías excesivas",
                "impact": "medium"
            })
        
        # Enlaces repetidos
        links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        link_texts = [link[0] for link in links]
        duplicates = [text for text in set(link_texts) if link_texts.count(text) > 3]
        if duplicates:
            opportunities.append({
                "type": "links",
                "description": f"Optimizar {len(duplicates)} enlaces duplicados",
                "impact": "low"
            })
        
        # Código repetido
        code_blocks = re.findall(r'```[\s\S]*?```', content)
        if len(code_blocks) > 5:
            opportunities.append({
                "type": "code",
                "description": f"Extraer {len(code_blocks)} bloques de código a archivos separados",
                "impact": "high"
            })
        
        return opportunities
    
    def divide_large_file(self, file_path, divisions, output_dir=None):
        """Divide un archivo grande en archivos más pequeños"""
        if not output_dir:
            output_dir = os.path.dirname(file_path)
        
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        divided_dir = os.path.join(output_dir, f"{base_name}_divided")
        
        # Crear directorio para archivos divididos
        os.makedirs(divided_dir, exist_ok=True)
        
        created_files = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            for i, division in enumerate(divisions):
                filename = f"{i+1:02d}_{division['recommended_filename']}"
                file_path_new = os.path.join(divided_dir, filename)
                
                # Extraer contenido de la división
                division_content = []
                for section in division["sections"]:
                    start_line = section["start_line"]
                    end_line = section["end_line"]
                    division_content.extend(lines[start_line:end_line+1])
                
                # Agregar metadatos
                metadata = f"""---
title: "{division['title']}"
source_file: "{os.path.basename(file_path)}"
division: {i+1} of {len(divisions)}
created: "{datetime.now().isoformat()}"
size: {division['total_size']} characters
---

"""
                
                # Escribir archivo dividido
                with open(file_path_new, 'w', encoding='utf-8') as f:
                    f.write(metadata)
                    f.write('\n'.join(division_content))
                
                created_files.append({
                    "filename": filename,
                    "path": file_path_new,
                    "size": division['total_size'],
                    "sections": len(division['sections'])
                })
                
                print(f"✅ Creado: {filename} ({division['total_size']} caracteres)")
        
        except Exception as e:
            print(f"Error dividiendo archivo: {e}")
            return []
        
        return created_files
    
    def optimize_content(self, content):
        """Optimiza el contenido de un archivo"""
        optimized = content
        
        # Eliminar líneas vacías excesivas
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)
        
        # Eliminar espacios al final de líneas
        optimized = re.sub(r' +$', '', optimized, flags=re.MULTILINE)
        
        # Normalizar saltos de línea
        optimized = optimized.replace('\r\n', '\n').replace('\r', '\n')
        
        return optimized
    
    def process_large_files(self, size_threshold=50000, auto_divide=False):
        """Procesa todos los archivos grandes"""
        print(f"🔍 Buscando archivos grandes (> {size_threshold} caracteres)...")
        
        large_files = []
        
        # Encontrar archivos grandes
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if len(content) > size_threshold:
                            large_files.append(file_path)
                    except:
                        continue
        
        print(f"📄 Encontrados {len(large_files)} archivos grandes")
        
        for file_path in large_files:
            print(f"\n📊 Analizando: {os.path.basename(file_path)}")
            
            analysis = self.analyze_large_file(file_path, size_threshold)
            if not analysis:
                continue
            
            self.optimization_results["files_processed"].append(analysis)
            
            print(f"   📏 Tamaño: {analysis['size']:,} caracteres")
            print(f"   📝 Líneas: {analysis['lines']:,}")
            print(f"   📂 Secciones: {len(analysis['sections'])}")
            print(f"   🔄 Divisiones recomendadas: {len(analysis['recommended_divisions'])}")
            
            # Mostrar oportunidades de optimización
            if analysis['optimization_opportunities']:
                print("   💡 Oportunidades de optimización:")
                for opp in analysis['optimization_opportunities']:
                    print(f"      - {opp['description']} ({opp['impact']})")
            
            # Dividir archivo si se solicita
            if auto_divide and analysis['recommended_divisions']:
                print(f"   🔄 Dividiendo archivo...")
                created_files = self.divide_large_file(file_path, analysis['recommended_divisions'])
                self.optimization_results["files_created"].extend(created_files)
                
                # Optimizar archivo original
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    optimized_content = self.optimize_content(original_content)
                    
                    # Crear backup
                    backup_path = f"{file_path}.backup"
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    
                    # Escribir contenido optimizado
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(optimized_content)
                    
                    size_reduction = len(original_content) - len(optimized_content)
                    self.optimization_results["total_size_reduction"] += size_reduction
                    
                    print(f"   ✅ Archivo optimizado (reducción: {size_reduction:,} caracteres)")
                    
                except Exception as e:
                    print(f"   ❌ Error optimizando archivo: {e}")
        
        return self.optimization_results
    
    def save_report(self, output_file="large_files_optimization_report.json"):
        """Guarda el reporte de optimización"""
        import json
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.optimization_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen de la optimización"""
        results = self.optimization_results
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE OPTIMIZACIÓN DE ARCHIVOS GRANDES")
        print("="*60)
        
        print(f"📄 Archivos procesados: {len(results['files_processed'])}")
        print(f"📁 Archivos creados: {len(results['files_created'])}")
        print(f"💾 Reducción total de tamaño: {results['total_size_reduction']:,} caracteres")
        
        if results['files_processed']:
            print("\n📋 Archivos procesados:")
            for file_info in results['files_processed']:
                filename = os.path.basename(file_info['file_path'])
                print(f"  - {filename}: {file_info['size']:,} caracteres, {len(file_info['sections'])} secciones")
        
        if results['files_created']:
            print("\n📁 Archivos creados:")
            for file_info in results['files_created']:
                print(f"  - {file_info['filename']}: {file_info['size']:,} caracteres, {file_info['sections']} secciones")

def main():
    parser = argparse.ArgumentParser(description='Optimizador de archivos grandes')
    parser.add_argument('--path', default='.', help='Ruta del directorio a analizar')
    parser.add_argument('--threshold', type=int, default=50000, help='Umbral de tamaño en caracteres')
    parser.add_argument('--divide', action='store_true', help='Dividir archivos automáticamente')
    parser.add_argument('--output', default='large_files_optimization_report.json', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    optimizer = LargeFilesOptimizer(args.path)
    results = optimizer.process_large_files(args.threshold, args.divide)
    
    optimizer.save_report(args.output)
    optimizer.print_summary()

if __name__ == "__main__":
    main()















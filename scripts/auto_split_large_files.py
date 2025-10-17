#!/usr/bin/env python3
"""
Auto Split Large Files - Sistema de División Automática de Archivos Grandes
Divide automáticamente archivos markdown grandes en archivos más manejables
"""

import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path

class AutoSplitLargeFiles:
    def __init__(self, root_path=".", max_size=50000, max_lines=2000):
        self.root_path = root_path
        self.max_size = max_size
        self.max_lines = max_lines
        self.split_results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": [],
            "files_created": [],
            "total_original_size": 0,
            "total_new_size": 0,
            "reduction_percentage": 0
        }
    
    def analyze_file_structure(self, file_path):
        """Analiza la estructura de un archivo para determinar la mejor forma de dividirlo"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            total_lines = len(lines)
            total_size = len(content)
            
            if total_size < self.max_size and total_lines < self.max_lines:
                return None
            
            # Detectar secciones por headers
            sections = self.detect_sections(lines)
            
            # Detectar bloques de código
            code_blocks = self.detect_code_blocks(content)
            
            # Detectar listas largas
            long_lists = self.detect_long_lists(lines)
            
            # Detectar tablas grandes
            large_tables = self.detect_large_tables(content)
            
            analysis = {
                "file_path": file_path,
                "total_size": total_size,
                "total_lines": total_lines,
                "sections": sections,
                "code_blocks": code_blocks,
                "long_lists": long_lists,
                "large_tables": large_tables,
                "split_strategy": self.determine_split_strategy(sections, code_blocks, long_lists, large_tables)
            }
            
            return analysis
            
        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return None
    
    def detect_sections(self, lines):
        """Detecta secciones basadas en headers markdown"""
        sections = []
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
    
    def detect_code_blocks(self, content):
        """Detecta bloques de código en el contenido"""
        code_blocks = []
        pattern = r'```(\w+)?\n(.*?)\n```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code = match.group(2)
            
            code_blocks.append({
                "language": language,
                "content": code,
                "start": match.start(),
                "end": match.end(),
                "size": len(code)
            })
        
        return code_blocks
    
    def detect_long_lists(self, lines):
        """Detecta listas largas en el contenido"""
        long_lists = []
        current_list = []
        in_list = False
        
        for i, line in enumerate(lines):
            # Detectar inicio de lista
            if re.match(r'^\s*[-*+]\s+', line) or re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    in_list = True
                    current_list = [i]
                else:
                    current_list.append(i)
            else:
                if in_list and len(current_list) > 10:  # Lista larga
                    long_lists.append({
                        "start_line": current_list[0],
                        "end_line": current_list[-1],
                        "length": len(current_list),
                        "content": '\n'.join(lines[current_list[0]:current_list[-1]+1])
                    })
                in_list = False
                current_list = []
        
        return long_lists
    
    def detect_large_tables(self, content):
        """Detecta tablas grandes en el contenido"""
        large_tables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '|' in line and line.count('|') > 3:  # Posible tabla
                table_lines = []
                j = i
                
                # Recopilar líneas de la tabla
                while j < len(lines) and '|' in lines[j]:
                    table_lines.append(lines[j])
                    j += 1
                
                if len(table_lines) > 10:  # Tabla grande
                    large_tables.append({
                        "start_line": i,
                        "end_line": j - 1,
                        "rows": len(table_lines),
                        "content": '\n'.join(table_lines)
                    })
        
        return large_tables
    
    def determine_split_strategy(self, sections, code_blocks, long_lists, large_tables):
        """Determina la mejor estrategia para dividir el archivo"""
        strategies = []
        
        # Estrategia por secciones
        if len(sections) > 5:
            strategies.append({
                "type": "sections",
                "priority": "high",
                "description": f"Dividir por {len(sections)} secciones",
                "method": "split_by_sections"
            })
        
        # Estrategia por bloques de código
        if len(code_blocks) > 3:
            strategies.append({
                "type": "code_blocks",
                "priority": "medium",
                "description": f"Extraer {len(code_blocks)} bloques de código",
                "method": "extract_code_blocks"
            })
        
        # Estrategia por listas largas
        if len(long_lists) > 2:
            strategies.append({
                "type": "long_lists",
                "priority": "medium",
                "description": f"Extraer {len(long_lists)} listas largas",
                "method": "extract_long_lists"
            })
        
        # Estrategia por tablas grandes
        if len(large_tables) > 1:
            strategies.append({
                "type": "large_tables",
                "priority": "low",
                "description": f"Extraer {len(large_tables)} tablas grandes",
                "method": "extract_large_tables"
            })
        
        return strategies
    
    def split_by_sections(self, analysis):
        """Divide el archivo por secciones"""
        file_path = analysis["file_path"]
        sections = analysis["sections"]
        
        # Crear directorio para archivos divididos
        base_name = Path(file_path).stem
        split_dir = Path(file_path).parent / f"{base_name}_split"
        split_dir.mkdir(exist_ok=True)
        
        created_files = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            lines = content.split('\n')
            
            # Agrupar secciones en archivos más pequeños
            current_file_sections = []
            current_size = 0
            file_index = 1
            
            for section in sections:
                # Si agregar esta sección excede el tamaño máximo
                if current_size + section["size"] > self.max_size and current_file_sections:
                    # Crear archivo con las secciones actuales
                    filename = f"{file_index:02d}_{self.generate_filename(current_file_sections[0]['title'])}"
                    file_path_new = split_dir / filename
                    
                    self.create_split_file(file_path_new, current_file_sections, lines)
                    created_files.append({
                        "filename": filename,
                        "path": str(file_path_new),
                        "sections": len(current_file_sections),
                        "size": current_size
                    })
                    
                    # Reiniciar para nuevo archivo
                    current_file_sections = [section]
                    current_size = section["size"]
                    file_index += 1
                else:
                    current_file_sections.append(section)
                    current_size += section["size"]
            
            # Crear último archivo
            if current_file_sections:
                filename = f"{file_index:02d}_{self.generate_filename(current_file_sections[0]['title'])}"
                file_path_new = split_dir / filename
                
                self.create_split_file(file_path_new, current_file_sections, lines)
                created_files.append({
                    "filename": filename,
                    "path": str(file_path_new),
                    "sections": len(current_file_sections),
                    "size": current_size
                })
            
            # Crear archivo índice
            self.create_index_file(split_dir, created_files, analysis)
            
        except Exception as e:
            print(f"Error dividiendo archivo: {e}")
            return []
        
        return created_files
    
    def create_split_file(self, file_path, sections, all_lines):
        """Crea un archivo dividido con las secciones especificadas"""
        content_parts = []
        
        # Agregar metadatos
        metadata = f"""---
title: "{sections[0]['title']}"
source_file: "{Path(file_path).parent.parent.name}/{Path(file_path).parent.parent.name}.md"
created: "{datetime.now().isoformat()}"
sections: {len(sections)}
---
"""
        content_parts.append(metadata)
        content_parts.append("")
        
        # Agregar contenido de las secciones
        for section in sections:
            start_line = section["start_line"]
            end_line = section["end_line"]
            section_content = '\n'.join(all_lines[start_line:end_line+1])
            content_parts.append(section_content)
            content_parts.append("")
        
        # Escribir archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content_parts))
    
    def create_index_file(self, split_dir, created_files, analysis):
        """Crea un archivo índice para los archivos divididos"""
        index_content = f"""# 📁 Índice de Archivos Divididos

**Archivo original:** {Path(analysis['file_path']).name}  
**Fecha de división:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Total archivos creados:** {len(created_files)}  
**Tamaño original:** {analysis['total_size']:,} caracteres  

## 📄 Archivos Creados

"""
        
        for i, file_info in enumerate(created_files, 1):
            index_content += f"{i}. **{file_info['filename']}**\n"
            index_content += f"   - Secciones: {file_info['sections']}\n"
            index_content += f"   - Tamaño: {file_info['size']:,} caracteres\n"
            index_content += f"   - Ruta: `{file_info['path']}`\n\n"
        
        index_content += """
## 🔗 Navegación

- [Volver al archivo original](../{original_file})
- [Ver todos los archivos divididos](./)

## 📊 Estadísticas

- **Reducción de tamaño promedio:** {reduction_percentage:.1f}%
- **Archivos más pequeños:** Mejor navegación y búsqueda
- **Organización mejorada:** Contenido estructurado por secciones
"""
        
        # Reemplazar placeholders
        original_file = Path(analysis['file_path']).name
        total_original_size = analysis['total_size']
        total_new_size = sum(f['size'] for f in created_files)
        reduction_percentage = ((total_original_size - total_new_size) / total_original_size) * 100
        
        index_content = index_content.replace('{original_file}', original_file)
        index_content = index_content.replace('{reduction_percentage}', str(reduction_percentage))
        
        # Escribir archivo índice
        index_path = split_dir / "README.md"
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
    
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
    
    def process_large_files(self, auto_split=False):
        """Procesa todos los archivos grandes"""
        print(f"🔍 Buscando archivos grandes (> {self.max_size} caracteres o > {self.max_lines} líneas)...")
        
        large_files = []
        
        # Encontrar archivos grandes
        for root, dirs, files in os.walk(self.root_path):
            for file in files:
                if file.endswith('.md'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if len(content) > self.max_size or len(content.split('\n')) > self.max_lines:
                            large_files.append(file_path)
                    except:
                        continue
        
        print(f"📄 Encontrados {len(large_files)} archivos grandes")
        
        for file_path in large_files:
            print(f"\n📊 Analizando: {os.path.basename(file_path)}")
            
            analysis = self.analyze_file_structure(file_path)
            if not analysis:
                continue
            
            self.split_results["files_processed"].append(analysis)
            self.split_results["total_original_size"] += analysis["total_size"]
            
            print(f"   📏 Tamaño: {analysis['total_size']:,} caracteres")
            print(f"   📝 Líneas: {analysis['total_lines']:,}")
            print(f"   📂 Secciones: {len(analysis['sections'])}")
            print(f"   💻 Bloques de código: {len(analysis['code_blocks'])}")
            print(f"   📋 Listas largas: {len(analysis['long_lists'])}")
            print(f"   📊 Tablas grandes: {len(analysis['large_tables'])}")
            
            # Mostrar estrategias de división
            if analysis['split_strategy']:
                print("   🔄 Estrategias de división:")
                for strategy in analysis['split_strategy']:
                    print(f"      - {strategy['description']} ({strategy['priority']})")
            
            # Dividir archivo si se solicita
            if auto_split and analysis['split_strategy']:
                print(f"   🔄 Dividiendo archivo...")
                created_files = self.split_by_sections(analysis)
                self.split_results["files_created"].extend(created_files)
                
                total_new_size = sum(f['size'] for f in created_files)
                self.split_results["total_new_size"] += total_new_size
                
                print(f"   ✅ Archivo dividido en {len(created_files)} archivos")
        
        # Calcular porcentaje de reducción
        if self.split_results["total_original_size"] > 0:
            self.split_results["reduction_percentage"] = (
                (self.split_results["total_original_size"] - self.split_results["total_new_size"]) / 
                self.split_results["total_original_size"]
            ) * 100
        
        return self.split_results
    
    def save_report(self, output_file="auto_split_report.json"):
        """Guarda el reporte de división"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.split_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen de la división"""
        results = self.split_results
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE DIVISIÓN AUTOMÁTICA")
        print("="*60)
        
        print(f"📄 Archivos procesados: {len(results['files_processed'])}")
        print(f"📁 Archivos creados: {len(results['files_created'])}")
        print(f"💾 Tamaño original: {results['total_original_size']:,} caracteres")
        print(f"💾 Tamaño nuevo: {results['total_new_size']:,} caracteres")
        print(f"📉 Reducción: {results['reduction_percentage']:.1f}%")
        
        if results['files_created']:
            print("\n📁 Archivos creados:")
            for file_info in results['files_created']:
                print(f"  - {file_info['filename']}: {file_info['sections']} secciones, {file_info['size']:,} caracteres")

def main():
    parser = argparse.ArgumentParser(description='División automática de archivos grandes')
    parser.add_argument('--path', default='.', help='Ruta del directorio a analizar')
    parser.add_argument('--max-size', type=int, default=50000, help='Tamaño máximo en caracteres')
    parser.add_argument('--max-lines', type=int, default=2000, help='Número máximo de líneas')
    parser.add_argument('--split', action='store_true', help='Dividir archivos automáticamente')
    parser.add_argument('--output', default='auto_split_report.json', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    splitter = AutoSplitLargeFiles(args.path, args.max_size, args.max_lines)
    results = splitter.process_large_files(args.split)
    
    splitter.save_report(args.output)
    splitter.print_summary()

if __name__ == "__main__":
    main()















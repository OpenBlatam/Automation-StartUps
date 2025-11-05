#!/usr/bin/env python3
"""
Advanced Compression System - Sistema de Compresión Avanzada
Implementa compresión inteligente y optimización de archivos
"""

import os
import gzip
import bz2
import lzma
import zlib
import json
import re
from datetime import datetime
from pathlib import Path
import argparse

class AdvancedCompressionSystem:
    def __init__(self, root_path=".", compression_dir="compressed"):
        self.root_path = root_path
        self.compression_dir = compression_dir
        self.compression_results = {
            "timestamp": datetime.now().isoformat(),
            "files_processed": [],
            "compression_stats": {
                "gzip": {"files": 0, "total_size": 0, "compressed_size": 0},
                "bz2": {"files": 0, "total_size": 0, "compressed_size": 0},
                "lzma": {"files": 0, "total_size": 0, "compressed_size": 0},
                "zlib": {"files": 0, "total_size": 0, "compressed_size": 0}
            },
            "optimization_opportunities": []
        }
        
        # Crear directorio de compresión
        os.makedirs(compression_dir, exist_ok=True)
    
    def analyze_file_for_compression(self, file_path):
        """Analiza un archivo para determinar la mejor estrategia de compresión"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = len(content)
            lines = content.split('\n')
            total_lines = len(lines)
            
            analysis = {
                "file_path": file_path,
                "original_size": file_size,
                "lines": total_lines,
                "compression_ratio": 0,
                "best_algorithm": "gzip",
                "optimization_opportunities": []
            }
            
            # Detectar patrones de compresión
            patterns = self.detect_compression_patterns(content)
            analysis["patterns"] = patterns
            
            # Determinar mejor algoritmo
            best_algorithm = self.determine_best_algorithm(content, patterns)
            analysis["best_algorithm"] = best_algorithm
            
            # Detectar oportunidades de optimización
            optimizations = self.detect_optimization_opportunities(content)
            analysis["optimization_opportunities"] = optimizations
            
            return analysis
            
        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return None
    
    def detect_compression_patterns(self, content):
        """Detecta patrones que afectan la compresión"""
        patterns = {
            "repetitive_text": 0,
            "whitespace": 0,
            "duplicate_lines": 0,
            "structured_data": 0,
            "code_blocks": 0,
            "tables": 0
        }
        
        lines = content.split('\n')
        
        # Detectar texto repetitivo
        words = content.split()
        word_count = {}
        for word in words:
            word_count[word] = word_count.get(word, 0) + 1
        
        repetitive_words = sum(1 for count in word_count.values() if count > 10)
        patterns["repetitive_text"] = repetitive_words
        
        # Detectar espacios en blanco
        whitespace_lines = sum(1 for line in lines if line.strip() == '')
        patterns["whitespace"] = whitespace_lines
        
        # Detectar líneas duplicadas
        line_count = {}
        for line in lines:
            line_count[line] = line_count.get(line, 0) + 1
        
        duplicate_lines = sum(1 for count in line_count.values() if count > 1)
        patterns["duplicate_lines"] = duplicate_lines
        
        # Detectar datos estructurados
        json_blocks = len(re.findall(r'\{[^}]*\}', content))
        yaml_blocks = len(re.findall(r'^---\n.*?\n---', content, re.DOTALL))
        patterns["structured_data"] = json_blocks + yaml_blocks
        
        # Detectar bloques de código
        code_blocks = len(re.findall(r'```[\s\S]*?```', content))
        patterns["code_blocks"] = code_blocks
        
        # Detectar tablas
        table_lines = sum(1 for line in lines if '|' in line and line.count('|') > 2)
        patterns["tables"] = table_lines
        
        return patterns
    
    def determine_best_algorithm(self, content, patterns):
        """Determina el mejor algoritmo de compresión basado en los patrones"""
        # GZIP es bueno para texto general
        if patterns["repetitive_text"] > 50:
            return "gzip"
        
        # BZ2 es bueno para datos estructurados
        if patterns["structured_data"] > 10:
            return "bz2"
        
        # LZMA es bueno para archivos grandes con mucha repetición
        if len(content) > 1000000 and patterns["repetitive_text"] > 100:
            return "lzma"
        
        # ZLIB es bueno para código
        if patterns["code_blocks"] > 5:
            return "zlib"
        
        return "gzip"  # Por defecto
    
    def detect_optimization_opportunities(self, content):
        """Detecta oportunidades de optimización antes de la compresión"""
        opportunities = []
        
        # Líneas vacías excesivas
        lines = content.split('\n')
        empty_lines = sum(1 for line in lines if line.strip() == '')
        if empty_lines > len(lines) * 0.1:  # Más del 10% son líneas vacías
            opportunities.append({
                "type": "whitespace_cleanup",
                "description": f"Eliminar {empty_lines} líneas vacías excesivas",
                "impact": "medium"
            })
        
        # Espacios al final de líneas
        trailing_spaces = sum(1 for line in lines if line.endswith(' '))
        if trailing_spaces > 0:
            opportunities.append({
                "type": "trailing_spaces",
                "description": f"Eliminar espacios al final de {trailing_spaces} líneas",
                "impact": "low"
            })
        
        # Líneas duplicadas
        line_count = {}
        for line in lines:
            line_count[line] = line_count.get(line, 0) + 1
        
        duplicate_lines = sum(1 for count in line_count.values() if count > 1)
        if duplicate_lines > 10:
            opportunities.append({
                "type": "duplicate_lines",
                "description": f"Eliminar {duplicate_lines} líneas duplicadas",
                "impact": "high"
            })
        
        # Normalizar saltos de línea
        if '\r\n' in content or '\r' in content:
            opportunities.append({
                "type": "line_endings",
                "description": "Normalizar saltos de línea a Unix",
                "impact": "low"
            })
        
        return opportunities
    
    def optimize_content(self, content, opportunities):
        """Optimiza el contenido antes de la compresión"""
        optimized = content
        
        for opp in opportunities:
            if opp["type"] == "whitespace_cleanup":
                # Eliminar líneas vacías excesivas
                lines = optimized.split('\n')
                cleaned_lines = []
                empty_count = 0
                
                for line in lines:
                    if line.strip() == '':
                        empty_count += 1
                        if empty_count <= 2:  # Máximo 2 líneas vacías consecutivas
                            cleaned_lines.append(line)
                    else:
                        empty_count = 0
                        cleaned_lines.append(line)
                
                optimized = '\n'.join(cleaned_lines)
            
            elif opp["type"] == "trailing_spaces":
                # Eliminar espacios al final de líneas
                lines = optimized.split('\n')
                cleaned_lines = [line.rstrip() for line in lines]
                optimized = '\n'.join(cleaned_lines)
            
            elif opp["type"] == "duplicate_lines":
                # Eliminar líneas duplicadas consecutivas
                lines = optimized.split('\n')
                cleaned_lines = []
                prev_line = None
                
                for line in lines:
                    if line != prev_line:
                        cleaned_lines.append(line)
                    prev_line = line
                
                optimized = '\n'.join(cleaned_lines)
            
            elif opp["type"] == "line_endings":
                # Normalizar saltos de línea
                optimized = optimized.replace('\r\n', '\n').replace('\r', '\n')
        
        return optimized
    
    def compress_file(self, file_path, algorithm="gzip", optimize=True):
        """Comprime un archivo usando el algoritmo especificado"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_size = len(content)
            
            # Optimizar contenido si se solicita
            if optimize:
                analysis = self.analyze_file_for_compression(file_path)
                if analysis and analysis["optimization_opportunities"]:
                    content = self.optimize_content(content, analysis["optimization_opportunities"])
            
            # Comprimir según el algoritmo
            if algorithm == "gzip":
                compressed_data = gzip.compress(content.encode('utf-8'))
            elif algorithm == "bz2":
                compressed_data = bz2.compress(content.encode('utf-8'))
            elif algorithm == "lzma":
                compressed_data = lzma.compress(content.encode('utf-8'))
            elif algorithm == "zlib":
                compressed_data = zlib.compress(content.encode('utf-8'))
            else:
                raise ValueError(f"Algoritmo no soportado: {algorithm}")
            
            compressed_size = len(compressed_data)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            # Crear nombre del archivo comprimido
            base_name = Path(file_path).stem
            compressed_filename = f"{base_name}.{algorithm}"
            compressed_path = os.path.join(self.compression_dir, compressed_filename)
            
            # Guardar archivo comprimido
            with open(compressed_path, 'wb') as f:
                f.write(compressed_data)
            
            # Actualizar estadísticas
            self.compression_results["compression_stats"][algorithm]["files"] += 1
            self.compression_results["compression_stats"][algorithm]["total_size"] += original_size
            self.compression_results["compression_stats"][algorithm]["compressed_size"] += compressed_size
            
            result = {
                "file_path": file_path,
                "compressed_path": compressed_path,
                "algorithm": algorithm,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "optimized": optimize
            }
            
            self.compression_results["files_processed"].append(result)
            
            return result
            
        except Exception as e:
            print(f"Error comprimiendo {file_path}: {e}")
            return None
    
    def compress_directory(self, algorithm="auto", optimize=True, size_threshold=10000):
        """Comprime todos los archivos en un directorio"""
        print(f"🔍 Buscando archivos para comprimir (> {size_threshold} bytes)...")
        
        files_to_compress = []
        
        # Encontrar archivos para comprimir
        for root, dirs, files in os.walk(self.root_path):
            # Excluir directorios de compresión y backup
            dirs[:] = [d for d in dirs if d not in ['compressed', 'backups']]
            
            for file in files:
                if file.endswith('.md') or file.endswith('.txt') or file.endswith('.json'):
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > size_threshold:
                            files_to_compress.append(file_path)
                    except:
                        continue
        
        print(f"📄 Encontrados {len(files_to_compress)} archivos para comprimir")
        
        for file_path in files_to_compress:
            print(f"📊 Comprimiendo: {os.path.basename(file_path)}")
            
            # Determinar algoritmo si es automático
            if algorithm == "auto":
                analysis = self.analyze_file_for_compression(file_path)
                if analysis:
                    chosen_algorithm = analysis["best_algorithm"]
                else:
                    chosen_algorithm = "gzip"
            else:
                chosen_algorithm = algorithm
            
            # Comprimir archivo
            result = self.compress_file(file_path, chosen_algorithm, optimize)
            if result:
                print(f"   ✅ Comprimido con {chosen_algorithm}: {result['compression_ratio']:.1f}%")
                
                # Mostrar oportunidades de optimización
                if result.get("optimization_opportunities"):
                    print("   💡 Oportunidades de optimización:")
                    for opp in result["optimization_opportunities"]:
                        print(f"      - {opp['description']} ({opp['impact']})")
        
        return self.compression_results
    
    def decompress_file(self, compressed_path, output_path=None):
        """Descomprime un archivo"""
        try:
            # Determinar algoritmo por extensión
            if compressed_path.endswith('.gzip'):
                algorithm = "gzip"
            elif compressed_path.endswith('.bz2'):
                algorithm = "bz2"
            elif compressed_path.endswith('.lzma'):
                algorithm = "lzma"
            elif compressed_path.endswith('.zlib'):
                algorithm = "zlib"
            else:
                raise ValueError("No se puede determinar el algoritmo de compresión")
            
            # Leer archivo comprimido
            with open(compressed_path, 'rb') as f:
                compressed_data = f.read()
            
            # Descomprimir
            if algorithm == "gzip":
                decompressed_data = gzip.decompress(compressed_data)
            elif algorithm == "bz2":
                decompressed_data = bz2.decompress(compressed_data)
            elif algorithm == "lzma":
                decompressed_data = lzma.decompress(compressed_data)
            elif algorithm == "zlib":
                decompressed_data = zlib.decompress(compressed_data)
            
            # Determinar ruta de salida
            if not output_path:
                output_path = compressed_path.replace(f'.{algorithm}', '')
            
            # Guardar archivo descomprimido
            with open(output_path, 'wb') as f:
                f.write(decompressed_data)
            
            print(f"✅ Archivo descomprimido: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Error descomprimiendo {compressed_path}: {e}")
            return None
    
    def save_report(self, output_file="compression_report.json"):
        """Guarda el reporte de compresión"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.compression_results, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Reporte guardado en {output_file}")
    
    def print_summary(self):
        """Imprime un resumen de la compresión"""
        results = self.compression_results
        
        print("\n" + "="*60)
        print("📊 RESUMEN DE COMPRESIÓN AVANZADA")
        print("="*60)
        
        print(f"📄 Archivos procesados: {len(results['files_processed'])}")
        print(f"📁 Directorio de compresión: {self.compression_dir}")
        
        print("\n📊 Estadísticas por algoritmo:")
        for algorithm, stats in results["compression_stats"].items():
            if stats["files"] > 0:
                total_ratio = (1 - stats["compressed_size"] / stats["total_size"]) * 100
                print(f"  {algorithm.upper()}:")
                print(f"    Archivos: {stats['files']}")
                print(f"    Tamaño original: {stats['total_size']:,} bytes")
                print(f"    Tamaño comprimido: {stats['compressed_size']:,} bytes")
                print(f"    Ratio de compresión: {total_ratio:.1f}%")
        
        if results["files_processed"]:
            print("\n📋 Archivos comprimidos:")
            for file_info in results["files_processed"][:10]:  # Mostrar solo los primeros 10
                filename = os.path.basename(file_info["file_path"])
                print(f"  - {filename}: {file_info['compression_ratio']:.1f}% ({file_info['algorithm']})")
            
            if len(results["files_processed"]) > 10:
                print(f"  ... y {len(results['files_processed']) - 10} archivos más")

def main():
    parser = argparse.ArgumentParser(description='Sistema de compresión avanzada')
    parser.add_argument('--path', default='.', help='Ruta del directorio a comprimir')
    parser.add_argument('--algorithm', default='auto', choices=['auto', 'gzip', 'bz2', 'lzma', 'zlib'], help='Algoritmo de compresión')
    parser.add_argument('--threshold', type=int, default=10000, help='Umbral de tamaño en bytes')
    parser.add_argument('--optimize', action='store_true', help='Optimizar contenido antes de comprimir')
    parser.add_argument('--decompress', help='Descomprimir archivo específico')
    parser.add_argument('--output', default='compression_report.json', help='Archivo de reporte')
    
    args = parser.parse_args()
    
    compressor = AdvancedCompressionSystem(args.path)
    
    if args.decompress:
        compressor.decompress_file(args.decompress)
    else:
        results = compressor.compress_directory(args.algorithm, args.optimize, args.threshold)
        compressor.save_report(args.output)
        compressor.print_summary()

if __name__ == "__main__":
    main()















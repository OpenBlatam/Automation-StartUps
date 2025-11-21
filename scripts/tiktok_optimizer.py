#!/usr/bin/env python3
"""
Optimizador de rendimiento para procesamiento de videos
Analiza y optimiza configuración para mejor rendimiento
"""

import os
import sys
import json
import logging
import psutil
import multiprocessing
from typing import Dict, Any, Optional
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Optimizador de rendimiento del sistema"""
    
    def __init__(self):
        """Inicializa el optimizador"""
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.disk_space_gb = psutil.disk_usage('/').free / (1024**3)
    
    def analyze_system(self) -> Dict[str, Any]:
        """
        Analiza el sistema y recomienda configuración
        
        Returns:
            Diccionario con análisis y recomendaciones
        """
        analysis = {
            'system': {
                'cpu_cores': self.cpu_count,
                'memory_gb': round(self.memory_gb, 2),
                'disk_space_gb': round(self.disk_space_gb, 2),
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': psutil.virtual_memory().percent
            },
            'recommendations': {}
        }
        
        # Recomendaciones de workers
        if self.cpu_count >= 8:
            recommended_workers = min(6, self.cpu_count - 2)
        elif self.cpu_count >= 4:
            recommended_workers = min(3, self.cpu_count - 1)
        else:
            recommended_workers = 1
        
        analysis['recommendations']['queue_workers'] = recommended_workers
        
        # Recomendaciones de threads para edición
        if self.cpu_count >= 8:
            recommended_threads = 8
        elif self.cpu_count >= 4:
            recommended_threads = 4
        else:
            recommended_threads = 2
        
        analysis['recommendations']['video_threads'] = recommended_threads
        
        # Recomendaciones de memoria
        if self.memory_gb >= 16:
            analysis['recommendations']['batch_size'] = 10
            analysis['recommendations']['cache_enabled'] = True
        elif self.memory_gb >= 8:
            analysis['recommendations']['batch_size'] = 5
            analysis['recommendations']['cache_enabled'] = True
        else:
            analysis['recommendations']['batch_size'] = 3
            analysis['recommendations']['cache_enabled'] = False
        
        # Recomendaciones de calidad
        if self.disk_space_gb < 10:
            analysis['recommendations']['auto_compress'] = True
            analysis['recommendations']['quality'] = 'medium'
        else:
            analysis['recommendations']['auto_compress'] = False
            analysis['recommendations']['quality'] = 'high'
        
        # Warnings
        warnings = []
        if self.memory_gb < 4:
            warnings.append("Memoria baja. Considera reducir workers.")
        if self.disk_space_gb < 5:
            warnings.append("Espacio en disco bajo. Limpia archivos temporales.")
        if psutil.cpu_percent(interval=1) > 80:
            warnings.append("CPU con alta carga. Reduce workers.")
        
        analysis['warnings'] = warnings
        
        return analysis
    
    def generate_config(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Genera archivo de configuración optimizado
        
        Args:
            output_path: Ruta donde guardar la configuración
            
        Returns:
            Configuración generada
        """
        analysis = self.analyze_system()
        
        config = {
            'queue': {
                'max_workers': analysis['recommendations']['queue_workers'],
                'retry_delay': 5,
                'max_retries': 3
            },
            'video_editing': {
                'threads': analysis['recommendations']['video_threads'],
                'preset': 'medium',
                'quality': analysis['recommendations']['quality']
            },
            'batch_processing': {
                'batch_size': analysis['recommendations']['batch_size'],
                'parallel_downloads': min(3, analysis['recommendations']['queue_workers'])
            },
            'cache': {
                'enabled': analysis['recommendations']['cache_enabled'],
                'max_size_gb': min(10, self.disk_space_gb * 0.1)
            },
            'compression': {
                'auto_compress': analysis['recommendations']['auto_compress'],
                'target_size_mb': 50,
                'quality': analysis['recommendations']['quality']
            },
            'system': analysis['system'],
            'warnings': analysis['warnings']
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuración guardada en: {output_path}")
        
        return config
    
    def optimize_cache(self, cache_dir: str, max_size_gb: float = 10):
        """
        Optimiza el cache eliminando archivos antiguos
        
        Args:
            cache_dir: Directorio del cache
            max_size_gb: Tamaño máximo en GB
        """
        cache_path = Path(cache_dir)
        if not cache_path.exists():
            logger.warning(f"Directorio de cache no existe: {cache_dir}")
            return
        
        # Calcular tamaño actual
        total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
        total_size_gb = total_size / (1024**3)
        
        logger.info(f"Tamaño actual del cache: {total_size_gb:.2f} GB")
        
        if total_size_gb <= max_size_gb:
            logger.info("Cache dentro del límite, no se necesita limpieza")
            return
        
        # Ordenar archivos por fecha de modificación (más antiguos primero)
        files = [(f, f.stat().st_mtime) for f in cache_path.rglob('*') if f.is_file()]
        files.sort(key=lambda x: x[1])
        
        # Eliminar archivos hasta estar bajo el límite
        deleted_size = 0
        deleted_count = 0
        
        for file_path, _ in files:
            if total_size_gb - (deleted_size / (1024**3)) <= max_size_gb:
                break
            
            file_size = file_path.stat().st_size
            try:
                file_path.unlink()
                deleted_size += file_size
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Error eliminando {file_path}: {e}")
        
        logger.info(f"Cache optimizado: {deleted_count} archivos eliminados, "
                   f"{deleted_size / (1024**3):.2f} GB liberados")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Optimizador de rendimiento')
    parser.add_argument('command', choices=['analyze', 'config', 'optimize-cache'], help='Comando')
    parser.add_argument('-o', '--output', help='Archivo de salida para config')
    parser.add_argument('-d', '--cache-dir', default='~/.tiktok_cache', help='Directorio de cache')
    parser.add_argument('-s', '--max-size', type=float, default=10, help='Tamaño máximo de cache en GB')
    
    args = parser.parse_args()
    
    optimizer = PerformanceOptimizer()
    
    if args.command == 'analyze':
        analysis = optimizer.analyze_system()
        print(json.dumps(analysis, indent=2, ensure_ascii=False))
    
    elif args.command == 'config':
        config = optimizer.generate_config(args.output)
        if not args.output:
            print(json.dumps(config, indent=2, ensure_ascii=False))
    
    elif args.command == 'optimize-cache':
        cache_dir = Path(args.cache_dir).expanduser()
        optimizer.optimize_cache(str(cache_dir), args.max_size)


if __name__ == '__main__':
    try:
        import psutil
    except ImportError:
        print("Error: psutil no está instalado. Instálalo con: pip install psutil")
        sys.exit(1)
    
    main()



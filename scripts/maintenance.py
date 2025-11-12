#!/usr/bin/env python3
"""
Scripts de mantenimiento para TikTok Auto Edit
Limpieza, optimización y tareas de mantenimiento automáticas
"""

import os
import sys
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MaintenanceManager:
    """Gestor de tareas de mantenimiento"""
    
    def __init__(self):
        """Inicializa el gestor de mantenimiento"""
        self.temp_dirs = [
            Path('/tmp/tiktok_downloads'),
            Path('/tmp/tiktok_edited'),
            Path('/tmp/tiktok_*')
        ]
    
    def clean_temp_files(self, days_old: int = 1):
        """
        Limpia archivos temporales antiguos
        
        Args:
            days_old: Días de antigüedad para considerar archivos temporales
        """
        logger.info(f"Limpiando archivos temporales (más de {days_old} días)...")
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        cleaned = 0
        total_size = 0
        
        # Limpiar directorios temporales conocidos
        for temp_pattern in ['/tmp/tiktok_downloads', '/tmp/tiktok_edited']:
            temp_dir = Path(temp_pattern)
            if temp_dir.exists():
                for item in temp_dir.iterdir():
                    try:
                        if item.is_file():
                            mtime = datetime.fromtimestamp(item.stat().st_mtime)
                            if mtime < cutoff_time:
                                size = item.stat().st_size
                                item.unlink()
                                cleaned += 1
                                total_size += size
                        elif item.is_dir():
                            # Limpiar directorios vacíos o antiguos
                            mtime = datetime.fromtimestamp(item.stat().st_mtime)
                            if mtime < cutoff_time:
                                try:
                                    shutil.rmtree(item)
                                    cleaned += 1
                                except:
                                    pass
                    except Exception as e:
                        logger.warning(f"Error limpiando {item}: {e}")
        
        logger.info(f"✅ {cleaned} archivos/directorios eliminados ({total_size / 1024 / 1024:.2f} MB)")
        return cleaned
    
    def clean_old_logs(self, days_old: int = 7):
        """
        Limpia logs antiguos
        
        Args:
            days_old: Días de antigüedad para logs
        """
        logger.info(f"Limpiando logs antiguos (más de {days_old} días)...")
        
        cutoff_time = datetime.now() - timedelta(days=days_old)
        cleaned = 0
        
        # Buscar archivos de log
        log_patterns = ['*.log', '*.log.*']
        for pattern in log_patterns:
            for log_file in Path('/tmp').glob(pattern):
                try:
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if mtime < cutoff_time:
                        log_file.unlink()
                        cleaned += 1
                except Exception as e:
                    logger.warning(f"Error limpiando log {log_file}: {e}")
        
        logger.info(f"✅ {cleaned} archivos de log eliminados")
        return cleaned
    
    def optimize_databases(self):
        """Optimiza bases de datos SQLite"""
        logger.info("Optimizando bases de datos...")
        
        import sqlite3
        
        databases = [
            Path.home() / '.tiktok_analytics.db',
            Path.home() / '.tiktok_queue.db'
        ]
        
        optimized = 0
        for db_path in databases:
            if db_path.exists():
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Vacuum para optimizar
                    cursor.execute('VACUUM')
                    
                    # Analizar para actualizar estadísticas
                    cursor.execute('ANALYZE')
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"  ✓ Optimizado: {db_path.name}")
                    optimized += 1
                except Exception as e:
                    logger.warning(f"Error optimizando {db_path}: {e}")
        
        logger.info(f"✅ {optimized} bases de datos optimizadas")
        return optimized
    
    def check_disk_space(self, min_gb: float = 5.0) -> bool:
        """
        Verifica espacio en disco
        
        Args:
            min_gb: Mínimo de GB requeridos
            
        Returns:
            True si hay suficiente espacio
        """
        import shutil
        
        total, used, free = shutil.disk_usage('/')
        free_gb = free / (1024**3)
        
        logger.info(f"Espacio en disco disponible: {free_gb:.2f} GB")
        
        if free_gb < min_gb:
            logger.warning(f"⚠️  Poco espacio en disco: {free_gb:.2f} GB (mínimo: {min_gb} GB)")
            return False
        
        return True
    
    def generate_maintenance_report(self) -> Dict[str, Any]:
        """
        Genera reporte de mantenimiento
        
        Returns:
            Diccionario con información de mantenimiento
        """
        import shutil
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'disk_space': {},
            'databases': {},
            'cache': {},
            'temp_files': {}
        }
        
        # Espacio en disco
        total, used, free = shutil.disk_usage('/')
        report['disk_space'] = {
            'total_gb': round(total / (1024**3), 2),
            'used_gb': round(used / (1024**3), 2),
            'free_gb': round(free / (1024**3), 2),
            'usage_percent': round((used / total) * 100, 2)
        }
        
        # Tamaño de bases de datos
        databases = {
            'analytics': Path.home() / '.tiktok_analytics.db',
            'queue': Path.home() / '.tiktok_queue.db'
        }
        
        for name, db_path in databases.items():
            if db_path.exists():
                size = db_path.stat().st_size
                report['databases'][name] = {
                    'size_mb': round(size / (1024 * 1024), 2),
                    'exists': True
                }
            else:
                report['databases'][name] = {'exists': False}
        
        # Tamaño de cache
        cache_dir = Path.home() / '.tiktok_cache'
        if cache_dir.exists():
            total_size = sum(f.stat().st_size for f in cache_dir.rglob('*') if f.is_file())
            file_count = len(list(cache_dir.rglob('*')))
            report['cache'] = {
                'size_mb': round(total_size / (1024 * 1024), 2),
                'file_count': file_count,
                'exists': True
            }
        else:
            report['cache'] = {'exists': False}
        
        # Archivos temporales
        temp_dirs = ['/tmp/tiktok_downloads', '/tmp/tiktok_edited']
        total_temp_size = 0
        temp_file_count = 0
        
        for temp_dir in temp_dirs:
            temp_path = Path(temp_dir)
            if temp_path.exists():
                for item in temp_path.rglob('*'):
                    if item.is_file():
                        total_temp_size += item.stat().st_size
                        temp_file_count += 1
        
        report['temp_files'] = {
            'size_mb': round(total_temp_size / (1024 * 1024), 2),
            'file_count': temp_file_count
        }
        
        return report
    
    def run_full_maintenance(self):
        """Ejecuta mantenimiento completo"""
        logger.info("="*60)
        logger.info("🔧 Ejecutando mantenimiento completo")
        logger.info("="*60)
        
        # Verificar espacio
        if not self.check_disk_space():
            logger.warning("Espacio en disco bajo, considerando limpieza...")
        
        # Limpiar temporales
        self.clean_temp_files(days_old=1)
        
        # Limpiar logs
        self.clean_old_logs(days_old=7)
        
        # Optimizar bases de datos
        self.optimize_databases()
        
        # Generar reporte
        report = self.generate_maintenance_report()
        
        logger.info("="*60)
        logger.info("✅ Mantenimiento completado")
        logger.info("="*60)
        
        return report


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Mantenimiento del sistema TikTok Auto Edit')
    parser.add_argument('command', choices=['clean', 'optimize', 'check', 'report', 'full'],
                       help='Comando de mantenimiento')
    parser.add_argument('-d', '--days', type=int, default=1,
                       help='Días de antigüedad para limpieza')
    parser.add_argument('-j', '--json', action='store_true',
                       help='Salida en formato JSON')
    
    args = parser.parse_args()
    
    manager = MaintenanceManager()
    
    if args.command == 'clean':
        manager.clean_temp_files(days_old=args.days)
        manager.clean_old_logs(days_old=7)
    
    elif args.command == 'optimize':
        manager.optimize_databases()
    
    elif args.command == 'check':
        manager.check_disk_space()
    
    elif args.command == 'report':
        report = manager.generate_maintenance_report()
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))
        else:
            print("\n📊 Reporte de Mantenimiento")
            print("="*60)
            print(f"Espacio en disco: {report['disk_space']['free_gb']} GB libres")
            print(f"Cache: {report['cache'].get('size_mb', 0)} MB")
            print(f"Archivos temporales: {report['temp_files']['size_mb']} MB")
            print("="*60)
    
    elif args.command == 'full':
        report = manager.run_full_maintenance()
        if args.json:
            print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()



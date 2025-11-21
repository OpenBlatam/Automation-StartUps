#!/usr/bin/env python3
"""
Sistema de backup y restore para TikTok Auto Edit
Backup de configuración, analytics, templates y cache
"""

import os
import sys
import json
import shutil
import logging
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BackupManager:
    """Gestor de backups del sistema"""
    
    def __init__(self, backup_dir: Optional[str] = None):
        """
        Inicializa el gestor de backups
        
        Args:
            backup_dir: Directorio donde guardar backups
        """
        self.backup_dir = Path(backup_dir or "~/.tiktok_backups").expanduser()
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Directorios y archivos a respaldar
        self.backup_items = {
            'analytics': Path.home() / '.tiktok_analytics.db',
            'queue': Path.home() / '.tiktok_queue.db',
            'templates': Path.home() / '.tiktok_templates',
            'cache': Path.home() / '.tiktok_cache',
            'config': Path.home() / '.tiktok_config.json'
        }
    
    def create_backup(self, include_cache: bool = False) -> str:
        """
        Crea un backup completo del sistema
        
        Args:
            include_cache: Si incluir el cache (puede ser grande)
            
        Returns:
            Ruta al archivo de backup creado
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = self.backup_dir / f"tiktok_backup_{timestamp}.tar.gz"
        
        logger.info(f"Creando backup: {backup_file}")
        
        with tarfile.open(backup_file, 'w:gz') as tar:
            # Backup de analytics
            if self.backup_items['analytics'].exists():
                tar.add(self.backup_items['analytics'], arcname='analytics.db')
                logger.info("  ✓ Analytics respaldado")
            
            # Backup de queue
            if self.backup_items['queue'].exists():
                tar.add(self.backup_items['queue'], arcname='queue.db')
                logger.info("  ✓ Queue respaldado")
            
            # Backup de templates
            if self.backup_items['templates'].exists():
                tar.add(self.backup_items['templates'], arcname='templates')
                logger.info("  ✓ Templates respaldados")
            
            # Backup de config
            if self.backup_items['config'].exists():
                tar.add(self.backup_items['config'], arcname='config.json')
                logger.info("  ✓ Configuración respaldada")
            
            # Backup de cache (opcional)
            if include_cache and self.backup_items['cache'].exists():
                tar.add(self.backup_items['cache'], arcname='cache')
                logger.info("  ✓ Cache respaldado")
            
            # Metadata del backup
            metadata = {
                'timestamp': timestamp,
                'created_at': datetime.now().isoformat(),
                'include_cache': include_cache,
                'items': {
                    'analytics': self.backup_items['analytics'].exists(),
                    'queue': self.backup_items['queue'].exists(),
                    'templates': self.backup_items['templates'].exists(),
                    'config': self.backup_items['config'].exists(),
                    'cache': include_cache and self.backup_items['cache'].exists()
                }
            }
            
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                json.dump(metadata, f, indent=2)
                temp_path = f.name
            
            tar.add(temp_path, arcname='backup_metadata.json')
            os.unlink(temp_path)
        
        size_mb = backup_file.stat().st_size / (1024 * 1024)
        logger.info(f"✅ Backup creado: {backup_file} ({size_mb:.2f} MB)")
        
        return str(backup_file)
    
    def restore_backup(self, backup_file: str, restore_cache: bool = False):
        """
        Restaura un backup
        
        Args:
            backup_file: Ruta al archivo de backup
            restore_cache: Si restaurar el cache
        """
        backup_path = Path(backup_file)
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup no encontrado: {backup_file}")
        
        logger.info(f"Restaurando backup: {backup_file}")
        
        # Leer metadata
        with tarfile.open(backup_path, 'r:gz') as tar:
            try:
                metadata_file = tar.extractfile('backup_metadata.json')
                if metadata_file:
                    metadata = json.load(metadata_file)
                    logger.info(f"  Backup creado: {metadata.get('created_at')}")
            except:
                logger.warning("  No se encontró metadata en el backup")
            
            # Restaurar archivos
            members = tar.getmembers()
            for member in members:
                if member.name == 'backup_metadata.json':
                    continue
                
                if member.name == 'cache' and not restore_cache:
                    continue
                
                tar.extract(member, path=Path.home())
                logger.info(f"  ✓ Restaurado: {member.name}")
        
        logger.info("✅ Backup restaurado exitosamente")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        Lista todos los backups disponibles
        
        Returns:
            Lista de backups con información
        """
        backups = []
        
        for backup_file in self.backup_dir.glob('tiktok_backup_*.tar.gz'):
            try:
                stat = backup_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                
                # Intentar leer metadata
                with tarfile.open(backup_file, 'r:gz') as tar:
                    try:
                        metadata_file = tar.extractfile('backup_metadata.json')
                        if metadata_file:
                            metadata = json.load(metadata_file)
                            created_at = metadata.get('created_at', 'Unknown')
                        else:
                            created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    except:
                        created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                backups.append({
                    'file': str(backup_file),
                    'name': backup_file.name,
                    'size_mb': round(size_mb, 2),
                    'created_at': created_at
                })
            except Exception as e:
                logger.warning(f"Error leyendo backup {backup_file}: {e}")
        
        # Ordenar por fecha (más reciente primero)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """
        Elimina backups antiguos
        
        Args:
            keep_days: Días de backups a mantener
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        backups = self.list_backups()
        
        deleted = 0
        for backup in backups:
            try:
                backup_date = datetime.fromisoformat(backup['created_at'])
                if backup_date < cutoff_date:
                    Path(backup['file']).unlink()
                    logger.info(f"Eliminado backup antiguo: {backup['name']}")
                    deleted += 1
            except Exception as e:
                logger.warning(f"Error procesando backup {backup['name']}: {e}")
        
        logger.info(f"✅ {deleted} backups antiguos eliminados")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de backup y restore')
    parser.add_argument('command', choices=['create', 'restore', 'list', 'cleanup'],
                       help='Comando a ejecutar')
    parser.add_argument('-f', '--file', help='Archivo de backup (para restore)')
    parser.add_argument('-c', '--cache', action='store_true',
                       help='Incluir cache en backup')
    parser.add_argument('-d', '--days', type=int, default=30,
                       help='Días de backups a mantener (para cleanup)')
    
    args = parser.parse_args()
    
    manager = BackupManager()
    
    if args.command == 'create':
        backup_file = manager.create_backup(include_cache=args.cache)
        print(f"\n✅ Backup creado: {backup_file}")
    
    elif args.command == 'restore':
        if not args.file:
            print("Error: Se requiere --file para restaurar")
            sys.exit(1)
        manager.restore_backup(args.file, restore_cache=args.cache)
        print("\n✅ Backup restaurado")
    
    elif args.command == 'list':
        backups = manager.list_backups()
        if backups:
            print("\n📦 Backups disponibles:\n")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup['name']}")
                print(f"   Tamaño: {backup['size_mb']} MB")
                print(f"   Fecha: {backup['created_at']}")
                print()
        else:
            print("No hay backups disponibles")
    
    elif args.command == 'cleanup':
        manager.cleanup_old_backups(keep_days=args.days)
        print(f"\n✅ Limpieza completada (manteniendo últimos {args.days} días)")


if __name__ == '__main__':
    main()



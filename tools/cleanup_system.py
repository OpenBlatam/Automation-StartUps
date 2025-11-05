#!/usr/bin/env python3
"""
Limpieza y Mantenimiento del Sistema

Limpia archivos temporales, logs antiguos, backups viejos y optimiza el espacio en disco.
"""
import sys
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict

# Configuración
BASE_DIR = Path(__file__).parent.parent
CLEANUP_CONFIG = {
    'reports': {
        'dir': BASE_DIR / 'reports',
        'keep_days': 30,
        'keep_count': 100,
        'extensions': ['.md', '.html', '.json']
    },
    'exports': {
        'dir': BASE_DIR / 'exports',
        'keep_days': 14,
        'keep_count': 50,
        'extensions': ['.xlsx', '.csv', '.json', '.html']
    },
    'backups': {
        'dir': BASE_DIR / 'backups',
        'keep_days': 90,
        'keep_count': 30,
        'extensions': ['.csv', '.zip', '.tar.gz']
    },
    'logs': {
        'dir': BASE_DIR / 'logs',
        'keep_days': 7,
        'keep_count': 50,
        'extensions': ['.log', '.txt']
    },
    'temp': {
        'dir': BASE_DIR / 'temp',
        'keep_days': 1,
        'keep_count': 10,
        'extensions': ['*']
    },
    'versions': {
        'dir': BASE_DIR / 'versions',
        'keep_days': 60,
        'keep_count': 20,
        'extensions': ['.csv', '.json']
    }
}

def get_directory_size(path: Path) -> int:
    """Calcula tamaño total de un directorio en bytes"""
    total = 0
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                total += entry.stat().st_size
    except:
        pass
    return total

def format_size(size_bytes: int) -> str:
    """Formatea tamaño en formato legible"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def cleanup_directory(config: Dict, dry_run: bool = True) -> Dict:
    """Limpia un directorio según la configuración"""
    directory = config['dir']
    keep_days = config['keep_days']
    keep_count = config['keep_count']
    extensions = config['extensions']
    
    if not directory.exists():
        return {
            'exists': False,
            'deleted': 0,
            'freed': 0,
            'kept': 0
        }
    
    cutoff_date = datetime.now() - timedelta(days=keep_days)
    cutoff_timestamp = cutoff_date.timestamp()
    
    # Encontrar todos los archivos
    files = []
    for ext in extensions:
        if ext == '*':
            pattern = '**/*'
        else:
            pattern = f'**/*{ext}'
        
        files.extend(list(directory.glob(pattern)))
    
    # Filtrar solo archivos (no directorios)
    files = [f for f in files if f.is_file()]
    
    # Ordenar por fecha de modificación (más recientes primero)
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    to_delete = []
    to_keep = []
    
    for i, file in enumerate(files):
        file_mtime = file.stat().st_mtime
        file_age_days = (datetime.now().timestamp() - file_mtime) / (24 * 60 * 60)
        
        # Eliminar si:
        # 1. Es más viejo que keep_days Y está más allá de keep_count
        # 2. O solo está más allá de keep_count (si keep_days es muy grande)
        if file_mtime < cutoff_timestamp or i >= keep_count:
            to_delete.append((file, file_age_days))
        else:
            to_keep.append(file)
    
    # Calcular espacio a liberar
    freed_bytes = sum(f.stat().st_size for f, _ in to_delete)
    
    # Eliminar archivos (si no es dry-run)
    deleted_count = 0
    if not dry_run:
        for file, age in to_delete:
            try:
                file.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"  ⚠️  Error eliminando {file.name}: {e}")
    
    return {
        'exists': True,
        'deleted': len(to_delete) if dry_run else deleted_count,
        'freed': freed_bytes,
        'kept': len(to_keep),
        'total': len(files)
    }

def cleanup_empty_directories(base_dir: Path, dry_run: bool = True) -> int:
    """Elimina directorios vacíos"""
    empty_dirs = []
    
    for directory in base_dir.rglob('*'):
        if directory.is_dir() and not any(directory.iterdir()):
            empty_dirs.append(directory)
    
    if not dry_run:
        for directory in empty_dirs:
            try:
                directory.rmdir()
            except:
                pass
    
    return len(empty_dirs)

def analyze_disk_usage() -> Dict:
    """Analiza uso de disco por directorio"""
    usage = {}
    
    for category, config in CLEANUP_CONFIG.items():
        directory = config['dir']
        if directory.exists():
            size = get_directory_size(directory)
            usage[category] = {
                'path': str(directory),
                'size': size,
                'formatted': format_size(size)
            }
    
    return usage

def main():
    dry_run = '--apply' not in sys.argv
    
    print("=" * 80)
    print("🧹 Limpieza y Mantenimiento del Sistema")
    print("=" * 80)
    print()
    
    if dry_run:
        print("🔍 MODO DRY-RUN (no se eliminarán archivos)")
        print("   Usa --apply para aplicar cambios")
        print()
    else:
        print("⚠️  MODO APLICACIÓN (se eliminarán archivos)")
        print()
        confirm = input("¿Continuar? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelado")
            return
    
    # Analizar uso de disco
    print("📊 Análisis de uso de disco:")
    print()
    disk_usage = analyze_disk_usage()
    
    total_size = sum(usage['size'] for usage in disk_usage.values())
    
    for category, usage_info in disk_usage.items():
        print(f"  {category:12} {usage_info['formatted']:>12} - {usage_info['path']}")
    
    print(f"\n  {'TOTAL':12} {format_size(total_size):>12}")
    print()
    
    # Limpiar cada categoría
    print("🧹 Limpiando directorios...")
    print()
    
    total_deleted = 0
    total_freed = 0
    
    for category, config in CLEANUP_CONFIG.items():
        print(f"📁 {category}:")
        
        result = cleanup_directory(config, dry_run=dry_run)
        
        if not result['exists']:
            print(f"  ⚠️  Directorio no existe")
            continue
        
        print(f"  Total archivos: {result['total']}")
        print(f"  Se mantendrán: {result['kept']}")
        print(f"  Se eliminarán: {result['deleted']}")
        print(f"  Espacio a liberar: {format_size(result['freed'])}")
        
        total_deleted += result['deleted']
        total_freed += result['freed']
        print()
    
    # Limpiar directorios vacíos
    print("📂 Limpiando directorios vacíos...")
    empty_count = cleanup_empty_directories(BASE_DIR, dry_run=dry_run)
    print(f"  Directorios vacíos: {empty_count}")
    print()
    
    # Resumen
    print("=" * 80)
    print("📊 Resumen")
    print("=" * 80)
    print(f"  🗑️  Archivos a eliminar: {total_deleted}")
    print(f"  💾 Espacio a liberar: {format_size(total_freed)}")
    print(f"  📂 Directorios vacíos: {empty_count}")
    print()
    
    if dry_run:
        print("💡 Para aplicar estos cambios, ejecuta:")
        print(f"   python3 {sys.argv[0]} --apply")
    else:
        print("✅ Limpieza completada")

if __name__ == '__main__':
    main()


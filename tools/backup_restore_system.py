#!/usr/bin/env python3
"""
Sistema de Backup y Restore
Crea backups automáticos del CSV Master y permite restaurar versiones anteriores
"""
import csv
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from hashlib import md5

BACKUP_DIR = "backups"
BACKUP_METADATA = "backup_metadata.json"

def calculate_hash(file_path):
    """Calcula hash MD5 de un archivo"""
    hash_md5 = md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def load_metadata(backup_dir):
    """Carga metadata de backups"""
    metadata_path = backup_dir / BACKUP_METADATA
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_metadata(backup_dir, metadata):
    """Guarda metadata de backups"""
    metadata_path = backup_dir / BACKUP_METADATA
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def create_backup(csv_path, backup_dir, reason="Manual backup"):
    """Crea un backup del CSV Master"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    if not csv_path.exists():
        print(f"❌ Archivo no encontrado: {csv_path}")
        return False
    
    # Calcular hash del archivo actual
    current_hash = calculate_hash(csv_path)
    
    # Cargar metadata
    metadata = load_metadata(backup_dir)
    
    # Verificar si ya existe un backup con el mismo hash (evitar duplicados)
    for backup_info in metadata:
        if backup_info.get('hash') == current_hash:
            print(f"ℹ️  Ya existe un backup idéntico: {backup_info['backup_file']}")
            return False
    
    # Crear nombre de backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"creatives_backup_{timestamp}.csv"
    backup_path = backup_dir / backup_filename
    
    # Copiar archivo
    shutil.copy2(csv_path, backup_path)
    
    # Obtener tamaño
    file_size = csv_path.stat().st_size
    
    # Crear entrada de metadata
    backup_info = {
        'backup_file': backup_filename,
        'timestamp': datetime.now().isoformat(),
        'hash': current_hash,
        'size': file_size,
        'reason': reason,
        'source_file': str(csv_path)
    }
    
    metadata.append(backup_info)
    
    # Mantener solo últimos 50 backups
    if len(metadata) > 50:
        oldest = metadata.pop(0)
        oldest_path = backup_dir / oldest['backup_file']
        if oldest_path.exists():
            oldest_path.unlink()
        print(f"🗑️  Backup antiguo eliminado: {oldest['backup_file']}")
    
    # Guardar metadata
    save_metadata(backup_dir, metadata)
    
    print(f"✅ Backup creado: {backup_filename}")
    print(f"   Hash: {current_hash[:12]}...")
    print(f"   Tamaño: {file_size:,} bytes")
    print(f"   Razón: {reason}")
    
    return True

def list_backups(backup_dir):
    """Lista todos los backups disponibles"""
    metadata = load_metadata(backup_dir)
    
    if not metadata:
        print("ℹ️  No hay backups disponibles")
        return []
    
    print("=" * 80)
    print("📋 Lista de Backups")
    print("=" * 80)
    print()
    
    # Ordenar por timestamp (más reciente primero)
    sorted_backups = sorted(metadata, key=lambda x: x['timestamp'], reverse=True)
    
    for i, backup_info in enumerate(sorted_backups, 1):
        timestamp = datetime.fromisoformat(backup_info['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        size_mb = backup_info['size'] / (1024 * 1024)
        
        print(f"{i}. {backup_info['backup_file']}")
        print(f"   📅 {timestamp}")
        print(f"   📊 Tamaño: {size_mb:.2f} MB")
        print(f"   💬 {backup_info.get('reason', 'N/A')}")
        print(f"   🔑 Hash: {backup_info['hash'][:12]}...")
        print()
    
    return sorted_backups

def restore_backup(backup_filename, csv_path, backup_dir):
    """Restaura un backup"""
    backup_path = backup_dir / backup_filename
    
    if not backup_path.exists():
        print(f"❌ Backup no encontrado: {backup_filename}")
        return False
    
    # Crear backup del archivo actual antes de restaurar
    if csv_path.exists():
        current_backup = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        current_backup_path = backup_dir / current_backup
        shutil.copy2(csv_path, current_backup_path)
        print(f"✅ Backup del archivo actual creado: {current_backup}")
    
    # Restaurar backup
    shutil.copy2(backup_path, csv_path)
    print(f"✅ Backup restaurado: {backup_filename}")
    print(f"   Archivo restaurado a: {csv_path}")
    
    return True

def auto_backup(csv_path, backup_dir, max_age_days=7):
    """Crea backup automático si el último es muy antiguo"""
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    metadata = load_metadata(backup_dir)
    
    if metadata:
        last_backup = sorted(metadata, key=lambda x: x['timestamp'], reverse=True)[0]
        last_backup_time = datetime.fromisoformat(last_backup['timestamp'])
        days_since_backup = (datetime.now() - last_backup_time).days
        
        if days_since_backup < max_age_days:
            print(f"ℹ️  Último backup tiene {days_since_backup} día(s). No se necesita nuevo backup.")
            return False
    
    return create_backup(csv_path, backup_dir, "Auto-backup")

def main():
    print("=" * 80)
    print("💾 Sistema de Backup y Restore")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    backup_dir = root_dir / BACKUP_DIR
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 backup_restore_system.py create [reason]")
        print("  python3 backup_restore_system.py list")
        print("  python3 backup_restore_system.py restore <backup_filename>")
        print("  python3 backup_restore_system.py auto")
        print()
        return
    
    command = sys.argv[1]
    
    if command == 'create':
        reason = sys.argv[2] if len(sys.argv) > 2 else "Manual backup"
        create_backup(csv_path, backup_dir, reason)
    
    elif command == 'list':
        list_backups(backup_dir)
    
    elif command == 'restore':
        if len(sys.argv) < 3:
            print("❌ Especifica el nombre del backup a restaurar")
            return
        
        backup_filename = sys.argv[2]
        
        response = input(f"⚠️  ¿Restaurar {backup_filename}? Esto sobrescribirá el CSV actual. (s/n): ")
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            restore_backup(backup_filename, csv_path, backup_dir)
        else:
            print("❌ Restore cancelado")
    
    elif command == 'auto':
        auto_backup(csv_path, backup_dir)
    
    else:
        print(f"❌ Comando desconocido: {command}")

if __name__ == '__main__':
    main()


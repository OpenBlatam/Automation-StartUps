#!/usr/bin/env python3
"""
Sistema de versionado de creativos
Rastrea cambios en creativos y permite revertir a versiones anteriores
"""
import csv
import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from hashlib import md5

VERSION_DIR = "versions"
METADATA_FILE = "version_metadata.json"

def calculate_file_hash(file_path):
    """Calcula hash MD5 de un archivo"""
    hash_md5 = md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except:
        return None

def load_metadata(versions_dir):
    """Carga metadata de versiones"""
    metadata_path = versions_dir / METADATA_FILE
    if metadata_path.exists():
        with open(metadata_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_metadata(versions_dir, metadata):
    """Guarda metadata de versiones"""
    metadata_path = versions_dir / METADATA_FILE
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

def create_version(creative_file, source_dir, versions_dir, reason="Auto-save"):
    """Crea una versión de un creative"""
    source_path = source_dir / creative_file
    
    if not source_path.exists():
        print(f"❌ Archivo no encontrado: {creative_file}")
        return False
    
    # Calcular hash
    file_hash = calculate_file_hash(source_path)
    if not file_hash:
        print(f"❌ Error calculando hash: {creative_file}")
        return False
    
    # Cargar metadata
    metadata = load_metadata(versions_dir)
    
    # Crear nombre de versión
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    version_name = f"{creative_file}_{timestamp}"
    version_path = versions_dir / version_name
    
    # Copiar archivo
    shutil.copy2(source_path, version_path)
    
    # Actualizar metadata
    if creative_file not in metadata:
        metadata[creative_file] = []
    
    version_info = {
        'version': version_name,
        'timestamp': datetime.now().isoformat(),
        'hash': file_hash,
        'reason': reason,
        'size': source_path.stat().st_size
    }
    
    metadata[creative_file].append(version_info)
    
    # Mantener solo últimas 10 versiones por archivo
    if len(metadata[creative_file]) > 10:
        oldest = metadata[creative_file].pop(0)
        oldest_path = versions_dir / oldest['version']
        if oldest_path.exists():
            oldest_path.unlink()
    
    # Guardar metadata
    save_metadata(versions_dir, metadata)
    
    print(f"✅ Versión creada: {version_name}")
    return True

def list_versions(creative_file, versions_dir):
    """Lista versiones de un creative"""
    metadata = load_metadata(versions_dir)
    
    if creative_file not in metadata or not metadata[creative_file]:
        print(f"ℹ️  No hay versiones para: {creative_file}")
        return []
    
    versions = metadata[creative_file]
    print(f"\n📋 Versiones de {creative_file}:")
    print("-" * 80)
    
    for i, version in enumerate(reversed(versions), 1):
        timestamp = datetime.fromisoformat(version['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i}. {version['version']}")
        print(f"   📅 {timestamp}")
        print(f"   💬 {version.get('reason', 'N/A')}")
        print(f"   📊 Tamaño: {version['size']:,} bytes")
        print(f"   🔑 Hash: {version['hash'][:12]}...")
        print()
    
    return versions

def restore_version(creative_file, version_name, source_dir, versions_dir):
    """Restaura una versión anterior"""
    version_path = versions_dir / version_name
    
    if not version_path.exists():
        print(f"❌ Versión no encontrada: {version_name}")
        return False
    
    # Backup del archivo actual
    source_path = source_dir / creative_file
    if source_path.exists():
        backup_name = f"{creative_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = source_dir / backup_name
        shutil.copy2(source_path, backup_path)
        print(f"✅ Backup creado: {backup_name}")
    
    # Restaurar versión
    shutil.copy2(version_path, source_path)
    print(f"✅ Versión restaurada: {version_name}")
    
    return True

def compare_versions(creative_file, version1, version2, versions_dir):
    """Compara dos versiones"""
    path1 = versions_dir / version1
    path2 = versions_dir / version2
    
    if not path1.exists() or not path2.exists():
        print("❌ Una o ambas versiones no existen")
        return False
    
    hash1 = calculate_file_hash(path1)
    hash2 = calculate_file_hash(path2)
    
    if hash1 == hash2:
        print("✅ Las versiones son idénticas")
    else:
        print("⚠️  Las versiones son diferentes")
        print(f"   {version1}: {hash1[:12]}...")
        print(f"   {version2}: {hash2[:12]}...")
    
    return hash1 != hash2

def auto_version_all_creatives(csv_path, assets_dir, versions_dir):
    """Crea versiones automáticas de todos los creativos en CSV"""
    creatives = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        creatives = list(reader)
    
    versions_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Creando versiones para {len(creatives)} creativos...")
    print()
    
    created = 0
    skipped = 0
    
    for creative in creatives:
        creative_file = creative.get('creative_file', '')
        if not creative_file:
            continue
        
        # Buscar en diferentes ubicaciones
        found = False
        for base_dir in [assets_dir / 'linkedin', assets_dir]:
            source_path = base_dir / creative_file
            if source_path.exists():
                if create_version(creative_file, base_dir, versions_dir, "Auto-version"):
                    created += 1
                else:
                    skipped += 1
                found = True
                break
        
        if not found:
            skipped += 1
            print(f"⚠️  No encontrado: {creative_file}")
    
    print()
    print(f"✅ Versiones creadas: {created}")
    print(f"⚠️  Omitidos: {skipped}")

def main():
    print("=" * 80)
    print("📦 Sistema de Versionado de Creativos")
    print("=" * 80)
    print()
    
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    assets_dir = root_dir / 'assets'
    versions_dir = root_dir / VERSION_DIR
    csv_path = root_dir / 'docs' / 'LINKEDIN_ADS_CREATIVES_MASTER.csv'
    
    versions_dir.mkdir(parents=True, exist_ok=True)
    
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python3 create_version_control.py create <creative_file> [reason]")
        print("  python3 create_version_control.py list <creative_file>")
        print("  python3 create_version_control.py restore <creative_file> <version_name>")
        print("  python3 create_version_control.py compare <creative_file> <version1> <version2>")
        print("  python3 create_version_control.py auto-version")
        print()
        return
    
    command = sys.argv[1]
    
    if command == 'create':
        if len(sys.argv) < 3:
            print("❌ Especifica el archivo a versionar")
            return
        
        creative_file = sys.argv[2]
        reason = sys.argv[3] if len(sys.argv) > 3 else "Manual version"
        
        # Buscar archivo
        found = False
        for base_dir in [assets_dir / 'linkedin', assets_dir]:
            source_path = base_dir / creative_file
            if source_path.exists():
                create_version(creative_file, base_dir, versions_dir, reason)
                found = True
                break
        
        if not found:
            print(f"❌ Archivo no encontrado: {creative_file}")
    
    elif command == 'list':
        if len(sys.argv) < 3:
            print("❌ Especifica el archivo")
            return
        
        creative_file = sys.argv[2]
        list_versions(creative_file, versions_dir)
    
    elif command == 'restore':
        if len(sys.argv) < 4:
            print("❌ Especifica archivo y versión")
            return
        
        creative_file = sys.argv[2]
        version_name = sys.argv[3]
        
        # Buscar archivo original
        found = False
        for base_dir in [assets_dir / 'linkedin', assets_dir]:
            source_path = base_dir / creative_file
            if source_path.exists() or not source_path.exists():  # Permitir restaurar aunque no exista
                restore_version(creative_file, version_name, base_dir, versions_dir)
                found = True
                break
        
        if not found:
            print(f"⚠️  Archivo original no encontrado, restaurando a: assets/linkedin/")
            restore_version(creative_file, version_name, assets_dir / 'linkedin', versions_dir)
    
    elif command == 'compare':
        if len(sys.argv) < 5:
            print("❌ Especifica archivo y dos versiones")
            return
        
        creative_file = sys.argv[2]
        version1 = sys.argv[3]
        version2 = sys.argv[4]
        compare_versions(creative_file, version1, version2, versions_dir)
    
    elif command == 'auto-version':
        if not csv_path.exists():
            print("❌ CSV Master no encontrado")
            return
        auto_version_all_creatives(csv_path, assets_dir, versions_dir)
    
    else:
        print(f"❌ Comando desconocido: {command}")

if __name__ == '__main__':
    main()


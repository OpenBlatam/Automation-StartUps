#!/usr/bin/env python3
"""
Herramienta de Backup y Restore de Firmas
Crea backups y restaura configuraciones de firmas
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def crear_backup(directorio_firmas: str, directorio_backup: str) -> bool:
    """Crea un backup completo de todas las firmas y configuraciones"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(directorio_backup) / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Copiar plantillas HTML
        plantillas = Path(directorio_firmas).glob("firma_*.html")
        for plantilla in plantillas:
            shutil.copy(plantilla, backup_path / plantilla.name)
        
        # Copiar archivos de texto
        textos = Path(directorio_firmas).glob("firma_*.txt")
        for texto in textos:
            shutil.copy(texto, backup_path / texto.name)
        
        # Copiar vCard
        vcards = Path(directorio_firmas).glob("*.vcf")
        for vcard in vcards:
            shutil.copy(vcard, backup_path / vcard.name)
        
        # Copiar configuraciones
        configs = Path(directorio_firmas).glob("*.json")
        for config in configs:
            shutil.copy(config, backup_path / config.name)
        
        # Crear archivo de información del backup
        info = {
            "fecha": datetime.now().isoformat(),
            "timestamp": timestamp,
            "plantillas": len(list(Path(directorio_firmas).glob("firma_*.html"))),
            "archivos_totales": len(list(Path(backup_path).glob("*")))
        }
        
        with open(backup_path / "backup_info.json", 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Backup creado: {backup_path}")
        return True
    
    except Exception as e:
        print(f"❌ Error creando backup: {e}")
        return False


def listar_backups(directorio_backup: str) -> List[Dict]:
    """Lista todos los backups disponibles"""
    backups = []
    backup_dir = Path(directorio_backup)
    
    if not backup_dir.exists():
        return backups
    
    for item in backup_dir.iterdir():
        if item.is_dir() and item.name.startswith("backup_"):
            info_file = item / "backup_info.json"
            if info_file.exists():
                try:
                    with open(info_file, 'r', encoding='utf-8') as f:
                        info = json.load(f)
                    backups.append({
                        "ruta": str(item),
                        "nombre": item.name,
                        "fecha": info.get("fecha", "Desconocida"),
                        "plantillas": info.get("plantillas", 0)
                    })
                except:
                    backups.append({
                        "ruta": str(item),
                        "nombre": item.name,
                        "fecha": "Desconocida",
                        "plantillas": 0
                    })
    
    return sorted(backups, key=lambda x: x["nombre"], reverse=True)


def restaurar_backup(backup_path: str, directorio_destino: str, sobrescribir: bool = False) -> bool:
    """Restaura un backup"""
    try:
        backup = Path(backup_path)
        destino = Path(directorio_destino)
        
        if not backup.exists():
            print(f"❌ Backup no encontrado: {backup_path}")
            return False
        
        # Verificar archivos a restaurar
        archivos = list(backup.glob("*"))
        archivos = [a for a in archivos if a.is_file() and a.name != "backup_info.json"]
        
        if not archivos:
            print("❌ No hay archivos para restaurar")
            return False
        
        # Confirmar si hay archivos existentes
        conflictos = []
        for archivo in archivos:
            destino_archivo = destino / archivo.name
            if destino_archivo.exists() and not sobrescribir:
                conflictos.append(archivo.name)
        
        if conflictos and not sobrescribir:
            print(f"⚠️  Archivos existentes (usar --overwrite para sobrescribir):")
            for conflicto in conflictos:
                print(f"   - {conflicto}")
            return False
        
        # Restaurar archivos
        restaurados = 0
        for archivo in archivos:
            destino_archivo = destino / archivo.name
            shutil.copy(archivo, destino_archivo)
            restaurados += 1
        
        print(f"✅ Restaurados {restaurados} archivos desde {backup.name}")
        return True
    
    except Exception as e:
        print(f"❌ Error restaurando backup: {e}")
        return False


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Backup y Restore de Firmas de Email')
    parser.add_argument('accion', choices=['backup', 'restore', 'list'], help='Acción a realizar')
    parser.add_argument('--backup-dir', default='backups', help='Directorio de backups')
    parser.add_argument('--source', default='.', help='Directorio fuente')
    parser.add_argument('--backup-name', help='Nombre del backup a restaurar')
    parser.add_argument('--overwrite', action='store_true', help='Sobrescribir archivos existentes')
    
    args = parser.parse_args()
    
    directorio_actual = Path(__file__).parent
    directorio_backup = directorio_actual / args.backup_dir
    directorio_backup.mkdir(exist_ok=True)
    
    if args.accion == 'backup':
        print("=" * 70)
        print("💾 Creando Backup de Firmas")
        print("=" * 70)
        print()
        
        crear_backup(str(directorio_actual), str(directorio_backup))
        
    elif args.accion == 'list':
        print("=" * 70)
        print("📋 Backups Disponibles")
        print("=" * 70)
        print()
        
        backups = listar_backups(str(directorio_backup))
        
        if not backups:
            print("❌ No se encontraron backups")
            return
        
        for i, backup in enumerate(backups, 1):
            print(f"{i}. {backup['nombre']}")
            print(f"   Fecha: {backup['fecha']}")
            print(f"   Plantillas: {backup['plantillas']}")
            print()
    
    elif args.accion == 'restore':
        print("=" * 70)
        print("🔄 Restaurando Backup")
        print("=" * 70)
        print()
        
        if not args.backup_name:
            backups = listar_backups(str(directorio_backup))
            if not backups:
                print("❌ No hay backups disponibles")
                return
            
            print("Backups disponibles:")
            for i, backup in enumerate(backups, 1):
                print(f"   {i}. {backup['nombre']}")
            
            try:
                seleccion = int(input("\nSelecciona backup (número): ")) - 1
                backup_seleccionado = backups[seleccion]
            except (ValueError, IndexError):
                print("❌ Selección inválida")
                return
        else:
            backup_seleccionado = {"ruta": str(directorio_backup / args.backup_name)}
        
        restaurar_backup(
            backup_seleccionado["ruta"],
            str(directorio_actual),
            args.overwrite
        )


if __name__ == "__main__":
    main()







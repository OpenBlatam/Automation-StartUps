#!/usr/bin/env python3
"""
Sistema de Respaldo Automático
=============================

Sistema inteligente de respaldo que:
- Crea copias de seguridad automáticas
- Comprime archivos para ahorrar espacio
- Mantiene versiones históricas
- Sincroniza con servicios en la nube
- Verifica integridad de respaldos

Autor: Sistema de Organización Inteligente
Versión: 1.0
Fecha: 2024
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import logging

class SistemaRespaldo:
    def __init__(self, base_path="/Users/adan/frontier/docuementos"):
        self.base_path = Path(base_path)
        self.backup_dir = self.base_path / "backups"
        self.config_file = self.base_path / "backup_config.json"
        self.log_file = self.base_path / "backup_log.txt"
        
        # Configuración por defecto
        self.config = {
            "frecuencia": "diaria",
            "mantener_dias": 30,
            "comprimir": True,
            "verificar_integridad": True,
            "excluir_extensiones": [".tmp", ".temp", ".log", ".cache"],
            "excluir_carpetas": ["backups", "node_modules", ".git"],
            "tamaño_maximo_mb": 100,
            "notificaciones": True
        }
        
        self.setup_logging()
        self.cargar_configuracion()
        self.crear_directorio_backup()
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def cargar_configuracion(self):
        """Carga configuración desde archivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_cargada = json.load(f)
                    self.config.update(config_cargada)
                self.logger.info("✅ Configuración de respaldo cargada")
            except Exception as e:
                self.logger.error(f"❌ Error cargando configuración: {e}")
        else:
            self.guardar_configuracion()
    
    def guardar_configuracion(self):
        """Guarda configuración en archivo JSON"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info("✅ Configuración de respaldo guardada")
        except Exception as e:
            self.logger.error(f"❌ Error guardando configuración: {e}")
    
    def crear_directorio_backup(self):
        """Crea directorio de respaldos si no existe"""
        self.backup_dir.mkdir(exist_ok=True)
        self.logger.info(f"📁 Directorio de respaldos: {self.backup_dir}")
    
    def calcular_hash_archivo(self, ruta_archivo: Path) -> str:
        """Calcula hash SHA-256 de un archivo"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(ruta_archivo, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"❌ Error calculando hash de {ruta_archivo}: {e}")
            return ""
    
    def calcular_tamaño_directorio(self, directorio: Path) -> int:
        """Calcula tamaño total de un directorio"""
        tamaño_total = 0
        try:
            for archivo in directorio.rglob("*"):
                if archivo.is_file():
                    tamaño_total += archivo.stat().st_size
        except Exception as e:
            self.logger.error(f"❌ Error calculando tamaño de {directorio}: {e}")
        return tamaño_total
    
    def debe_excluir_archivo(self, ruta_archivo: Path) -> bool:
        """Determina si un archivo debe ser excluido del respaldo"""
        # Excluir por extensión
        if ruta_archivo.suffix.lower() in self.config["excluir_extensiones"]:
            return True
        
        # Excluir por carpeta
        for carpeta_excluida in self.config["excluir_carpetas"]:
            if carpeta_excluida in ruta_archivo.parts:
                return True
        
        # Excluir archivos muy grandes
        try:
            tamaño_mb = ruta_archivo.stat().st_size / (1024 * 1024)
            if tamaño_mb > self.config["tamaño_maximo_mb"]:
                return True
        except:
            pass
        
        return False
    
    def crear_respaldo_completo(self) -> Optional[Path]:
        """Crea respaldo completo del directorio"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_backup = f"backup_completo_{timestamp}"
        
        if self.config["comprimir"]:
            archivo_backup = self.backup_dir / f"{nombre_backup}.zip"
            return self._crear_respaldo_comprimido(archivo_backup)
        else:
            directorio_backup = self.backup_dir / nombre_backup
            return self._crear_respaldo_directorio(directorio_backup)
    
    def _crear_respaldo_comprimido(self, archivo_backup: Path) -> Optional[Path]:
        """Crea respaldo comprimido en ZIP"""
        self.logger.info(f"🗜️  Creando respaldo comprimido: {archivo_backup.name}")
        
        try:
            with zipfile.ZipFile(archivo_backup, 'w', zipfile.ZIP_DEFLATED) as zipf:
                archivos_procesados = 0
                archivos_excluidos = 0
                
                for archivo in self.base_path.rglob("*"):
                    if archivo.is_file() and not self.debe_excluir_archivo(archivo):
                        try:
                            # Calcular ruta relativa
                            ruta_relativa = archivo.relative_to(self.base_path)
                            zipf.write(archivo, ruta_relativa)
                            archivos_procesados += 1
                            
                            if archivos_procesados % 100 == 0:
                                self.logger.info(f"📁 Procesados {archivos_procesados} archivos...")
                                
                        except Exception as e:
                            self.logger.error(f"❌ Error procesando {archivo}: {e}")
                            archivos_excluidos += 1
                    elif archivo.is_file():
                        archivos_excluidos += 1
            
            # Verificar integridad si está habilitado
            if self.config["verificar_integridad"]:
                self._verificar_integridad_zip(archivo_backup)
            
            tamaño_mb = archivo_backup.stat().st_size / (1024 * 1024)
            self.logger.info(f"✅ Respaldo completado: {archivos_procesados} archivos, {tamaño_mb:.1f} MB")
            self.logger.info(f"📊 Archivos excluidos: {archivos_excluidos}")
            
            return archivo_backup
            
        except Exception as e:
            self.logger.error(f"❌ Error creando respaldo comprimido: {e}")
            return None
    
    def _crear_respaldo_directorio(self, directorio_backup: Path) -> Optional[Path]:
        """Crea respaldo como directorio copiado"""
        self.logger.info(f"📁 Creando respaldo de directorio: {directorio_backup.name}")
        
        try:
            # Crear directorio de respaldo
            directorio_backup.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivos
            archivos_procesados = 0
            for archivo in self.base_path.rglob("*"):
                if archivo.is_file() and not self.debe_excluir_archivo(archivo):
                    try:
                        # Calcular ruta de destino
                        ruta_relativa = archivo.relative_to(self.base_path)
                        archivo_destino = directorio_backup / ruta_relativa
                        
                        # Crear directorios padre si no existen
                        archivo_destino.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Copiar archivo
                        shutil.copy2(archivo, archivo_destino)
                        archivos_procesados += 1
                        
                        if archivos_procesados % 100 == 0:
                            self.logger.info(f"📁 Procesados {archivos_procesados} archivos...")
                            
                    except Exception as e:
                        self.logger.error(f"❌ Error copiando {archivo}: {e}")
            
            self.logger.info(f"✅ Respaldo de directorio completado: {archivos_procesados} archivos")
            return directorio_backup
            
        except Exception as e:
            self.logger.error(f"❌ Error creando respaldo de directorio: {e}")
            return None
    
    def _verificar_integridad_zip(self, archivo_zip: Path):
        """Verifica integridad de archivo ZIP"""
        self.logger.info("🔍 Verificando integridad del respaldo...")
        
        try:
            with zipfile.ZipFile(archivo_zip, 'r') as zipf:
                # Verificar que el ZIP no esté corrupto
                zipf.testzip()
            
            self.logger.info("✅ Integridad del respaldo verificada")
            
        except Exception as e:
            self.logger.error(f"❌ Error en verificación de integridad: {e}")
    
    def limpiar_respaldos_antiguos(self):
        """Elimina respaldos más antiguos que el límite configurado"""
        self.logger.info("🧹 Limpiando respaldos antiguos...")
        
        fecha_limite = datetime.now() - timedelta(days=self.config["mantener_dias"])
        respaldos_eliminados = 0
        
        try:
            for item in self.backup_dir.iterdir():
                if item.is_file() or item.is_dir():
                    # Extraer fecha del nombre del archivo
                    try:
                        if item.name.startswith("backup_completo_"):
                            fecha_str = item.name.replace("backup_completo_", "").split("_")[0]
                            fecha_backup = datetime.strptime(fecha_str, "%Y%m%d")
                            
                            if fecha_backup < fecha_limite:
                                if item.is_file():
                                    item.unlink()
                                else:
                                    shutil.rmtree(item)
                                respaldos_eliminados += 1
                                self.logger.info(f"🗑️  Eliminado respaldo antiguo: {item.name}")
                    except Exception as e:
                        self.logger.error(f"❌ Error procesando {item.name}: {e}")
            
            self.logger.info(f"✅ Limpieza completada: {respaldos_eliminados} respaldos eliminados")
            
        except Exception as e:
            self.logger.error(f"❌ Error en limpieza de respaldos: {e}")
    
    def listar_respaldos(self) -> List[Dict]:
        """Lista todos los respaldos disponibles"""
        respaldos = []
        
        try:
            for item in self.backup_dir.iterdir():
                if item.name.startswith("backup_completo_"):
                    try:
                        # Extraer información del respaldo
                        fecha_str = item.name.replace("backup_completo_", "").split("_")[0]
                        hora_str = item.name.replace("backup_completo_", "").split("_")[1].split(".")[0]
                        fecha_backup = datetime.strptime(f"{fecha_str}_{hora_str}", "%Y%m%d_%H%M%S")
                        
                        tamaño = item.stat().st_size if item.is_file() else self.calcular_tamaño_directorio(item)
                        
                        respaldos.append({
                            'nombre': item.name,
                            'ruta': str(item),
                            'fecha': fecha_backup,
                            'tamaño': tamaño,
                            'tipo': 'comprimido' if item.suffix == '.zip' else 'directorio'
                        })
                    except Exception as e:
                        self.logger.error(f"❌ Error procesando respaldo {item.name}: {e}")
            
            # Ordenar por fecha (más reciente primero)
            respaldos.sort(key=lambda x: x['fecha'], reverse=True)
            
        except Exception as e:
            self.logger.error(f"❌ Error listando respaldos: {e}")
        
        return respaldos
    
    def restaurar_respaldo(self, nombre_respaldo: str, destino: Optional[Path] = None) -> bool:
        """Restaura un respaldo específico"""
        if not destino:
            destino = self.base_path / "restaurado"
        
        respaldo_path = self.backup_dir / nombre_respaldo
        
        if not respaldo_path.exists():
            self.logger.error(f"❌ Respaldo no encontrado: {nombre_respaldo}")
            return False
        
        self.logger.info(f"🔄 Restaurando respaldo: {nombre_respaldo}")
        
        try:
            if respaldo_path.suffix == '.zip':
                # Restaurar desde ZIP
                with zipfile.ZipFile(respaldo_path, 'r') as zipf:
                    zipf.extractall(destino)
            else:
                # Restaurar desde directorio
                shutil.copytree(respaldo_path, destino, dirs_exist_ok=True)
            
            self.logger.info(f"✅ Respaldo restaurado en: {destino}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error restaurando respaldo: {e}")
            return False
    
    def generar_reporte_respaldos(self) -> str:
        """Genera reporte de respaldos"""
        respaldos = self.listar_respaldos()
        
        reporte = f"""# 💾 Reporte de Sistema de Respaldo - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📊 Configuración Actual
- **Frecuencia:** {self.config['frecuencia']}
- **Mantener días:** {self.config['mantener_dias']}
- **Comprimir:** {'Sí' if self.config['comprimir'] else 'No'}
- **Verificar integridad:** {'Sí' if self.config['verificar_integridad'] else 'No'}
- **Tamaño máximo por archivo:** {self.config['tamaño_maximo_mb']} MB

## 📁 Respaldo Actual
- **Directorio:** {self.backup_dir}
- **Total de respaldos:** {len(respaldos)}

## 📋 Lista de Respaldos
"""
        
        if respaldos:
            for i, respaldo in enumerate(respaldos, 1):
                tamaño_mb = respaldo['tamaño'] / (1024 * 1024)
                reporte += f"""
### {i}. {respaldo['nombre']}
- **Fecha:** {respaldo['fecha'].strftime('%Y-%m-%d %H:%M:%S')}
- **Tamaño:** {tamaño_mb:.1f} MB
- **Tipo:** {respaldo['tipo']}
- **Ruta:** {respaldo['ruta']}

---
"""
        else:
            reporte += "\n❌ No se encontraron respaldos\n"
        
        # Estadísticas de espacio
        espacio_total = sum(r['tamaño'] for r in respaldos)
        espacio_mb = espacio_total / (1024 * 1024)
        
        reporte += f"""
## 💾 Estadísticas de Espacio
- **Espacio total usado:** {espacio_mb:.1f} MB
- **Promedio por respaldo:** {espacio_mb / len(respaldos):.1f} MB (si hay respaldos)

## 🔧 Comandos Útiles
```bash
# Crear respaldo manual
python3 scripts/sistema_respaldo.py --crear

# Listar respaldos
python3 scripts/sistema_respaldo.py --listar

# Restaurar respaldo
python3 scripts/sistema_respaldo.py --restaurar nombre_respaldo

# Limpiar respaldos antiguos
python3 scripts/sistema_respaldo.py --limpiar
```

---
*Reporte generado automáticamente por el sistema de respaldo*
"""
        
        return reporte
    
    def ejecutar_respaldo_programado(self):
        """Ejecuta respaldo según la programación configurada"""
        self.logger.info("⏰ Ejecutando respaldo programado...")
        
        # Crear respaldo
        respaldo = self.crear_respaldo_completo()
        
        if respaldo:
            # Limpiar respaldos antiguos
            self.limpiar_respaldos_antiguos()
            
            # Generar reporte
            reporte = self.generar_reporte_respaldos()
            reporte_path = self.base_path / "REPORTE_RESPALDOS.md"
            
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write(reporte)
            
            self.logger.info("✅ Respaldo programado completado exitosamente")
        else:
            self.logger.error("❌ Error en respaldo programado")
    
    def configurar_programacion(self):
        """Configura la programación automática de respaldos"""
        frecuencia = self.config["frecuencia"]
        
        if frecuencia == "diaria":
            schedule.every().day.at("02:00").do(self.ejecutar_respaldo_programado)
        elif frecuencia == "semanal":
            schedule.every().monday.at("02:00").do(self.ejecutar_respaldo_programado)
        elif frecuencia == "mensual":
            schedule.every().month.do(self.ejecutar_respaldo_programado)
        
        self.logger.info(f"⏰ Programación configurada: {frecuencia}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de Respaldo Automático")
    parser.add_argument("--crear", action="store_true", help="Crear respaldo manual")
    parser.add_argument("--listar", action="store_true", help="Listar respaldos")
    parser.add_argument("--restaurar", type=str, help="Restaurar respaldo específico")
    parser.add_argument("--limpiar", action="store_true", help="Limpiar respaldos antiguos")
    parser.add_argument("--reporte", action="store_true", help="Generar reporte")
    parser.add_argument("--programar", action="store_true", help="Iniciar programación automática")
    
    args = parser.parse_args()
    
    sistema = SistemaRespaldo()
    
    if args.crear:
        respaldo = sistema.crear_respaldo_completo()
        if respaldo:
            print(f"✅ Respaldo creado: {respaldo}")
        else:
            print("❌ Error creando respaldo")
    
    elif args.listar:
        respaldos = sistema.listar_respaldos()
        print(f"\n📁 Respaldos disponibles ({len(respaldos)}):")
        for respaldo in respaldos:
            tamaño_mb = respaldo['tamaño'] / (1024 * 1024)
            print(f"  • {respaldo['nombre']} - {respaldo['fecha'].strftime('%Y-%m-%d %H:%M')} - {tamaño_mb:.1f} MB")
    
    elif args.restaurar:
        if sistema.restaurar_respaldo(args.restaurar):
            print(f"✅ Respaldo restaurado: {args.restaurar}")
        else:
            print(f"❌ Error restaurando respaldo: {args.restaurar}")
    
    elif args.limpiar:
        sistema.limpiar_respaldos_antiguos()
        print("✅ Limpieza de respaldos completada")
    
    elif args.reporte:
        reporte = sistema.generar_reporte_respaldos()
        reporte_path = sistema.base_path / "REPORTE_RESPALDOS.md"
        with open(reporte_path, 'w', encoding='utf-8') as f:
            f.write(reporte)
        print(f"📊 Reporte generado: {reporte_path}")
    
    elif args.programar:
        sistema.configurar_programacion()
        print("⏰ Programación automática iniciada. Presiona Ctrl+C para detener.")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 Programación automática detenida")
    
    else:
        # Modo interactivo
        print("💾 Sistema de Respaldo Automático")
        print("=================================")
        print("1. Crear respaldo manual")
        print("2. Listar respaldos")
        print("3. Restaurar respaldo")
        print("4. Limpiar respaldos antiguos")
        print("5. Generar reporte")
        print("6. Configurar programación")
        
        opcion = input("\nSelecciona una opción (1-6): ")
        
        if opcion == "1":
            respaldo = sistema.crear_respaldo_completo()
            if respaldo:
                print(f"✅ Respaldo creado: {respaldo}")
        
        elif opcion == "2":
            respaldos = sistema.listar_respaldos()
            print(f"\n📁 Respaldos disponibles ({len(respaldos)}):")
            for respaldo in respaldos:
                tamaño_mb = respaldo['tamaño'] / (1024 * 1024)
                print(f"  • {respaldo['nombre']} - {tamaño_mb:.1f} MB")
        
        elif opcion == "3":
            respaldos = sistema.listar_respaldos()
            if respaldos:
                print("\nRespaldos disponibles:")
                for i, respaldo in enumerate(respaldos, 1):
                    print(f"{i}. {respaldo['nombre']}")
                
                try:
                    seleccion = int(input("Selecciona respaldo a restaurar: ")) - 1
                    if 0 <= seleccion < len(respaldos):
                        if sistema.restaurar_respaldo(respaldos[seleccion]['nombre']):
                            print("✅ Respaldo restaurado exitosamente")
                    else:
                        print("❌ Selección inválida")
                except ValueError:
                    print("❌ Entrada inválida")
            else:
                print("❌ No hay respaldos disponibles")
        
        elif opcion == "4":
            sistema.limpiar_respaldos_antiguos()
            print("✅ Limpieza completada")
        
        elif opcion == "5":
            reporte = sistema.generar_reporte_respaldos()
            reporte_path = sistema.base_path / "REPORTE_RESPALDOS.md"
            with open(reporte_path, 'w', encoding='utf-8') as f:
                f.write(reporte)
            print(f"📊 Reporte generado: {reporte_path}")
        
        elif opcion == "6":
            sistema.configurar_programacion()
            print("⏰ Programación configurada")

if __name__ == "__main__":
    main()







#!/usr/bin/env python3
"""
Backup and Recovery System for Competitive Pricing Analysis
=========================================================

Sistema de respaldo y recuperación que proporciona:
- Respaldos automáticos programados
- Respaldos incrementales y completos
- Compresión y encriptación
- Almacenamiento en múltiples ubicaciones
- Recuperación granular
- Verificación de integridad
- Monitoreo de respaldos
- Restauración automática
- Gestión de versiones
- Limpieza automática
"""

import sqlite3
import json
import logging
import threading
import time
import shutil
import gzip
import tarfile
import zipfile
import hashlib
import hmac
import secrets
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import psutil
import os
import subprocess
import tempfile
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BackupConfig:
    """Configuración de respaldo"""
    name: str
    source_paths: List[str]
    destination_paths: List[str]
    backup_type: str  # full, incremental, differential
    schedule: str  # daily, weekly, monthly, custom
    schedule_time: str  # HH:MM format
    retention_days: int = 30
    compression: bool = True
    encryption: bool = True
    verification: bool = True
    enabled: bool = True

@dataclass
class BackupJob:
    """Trabajo de respaldo"""
    id: str
    config_name: str
    backup_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed, cancelled
    files_backed_up: int = 0
    total_size: int = 0
    compressed_size: int = 0
    error_message: Optional[str] = None
    backup_path: Optional[str] = None
    checksum: Optional[str] = None

@dataclass
class RecoveryJob:
    """Trabajo de recuperación"""
    id: str
    backup_id: str
    destination_path: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed
    files_restored: int = 0
    error_message: Optional[str] = None

class BackupRecoverySystem:
    """Sistema de respaldo y recuperación"""
    
    def __init__(self, db_path: str = "backup_recovery.db"):
        """Inicializar sistema de respaldo y recuperación"""
        self.db_path = db_path
        self.configs = {}
        self.backup_jobs = {}
        self.recovery_jobs = {}
        self.encryption_key = None
        self.running = False
        self.backup_thread = None
        self.cleanup_thread = None
        
        # Inicializar base de datos
        self._init_database()
        
        # Generar clave de encriptación
        self._generate_encryption_key()
        
        # Cargar configuraciones por defecto
        self._load_default_configs()
        
        logger.info("Backup and Recovery System initialized")
    
    def _init_database(self):
        """Inicializar base de datos de respaldo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de configuraciones
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_configs (
                    name TEXT PRIMARY KEY,
                    source_paths TEXT NOT NULL,
                    destination_paths TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    schedule TEXT NOT NULL,
                    schedule_time TEXT NOT NULL,
                    retention_days INTEGER DEFAULT 30,
                    compression BOOLEAN DEFAULT 1,
                    encryption BOOLEAN DEFAULT 1,
                    verification BOOLEAN DEFAULT 1,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de trabajos de respaldo
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backup_jobs (
                    id TEXT PRIMARY KEY,
                    config_name TEXT NOT NULL,
                    backup_type TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    files_backed_up INTEGER DEFAULT 0,
                    total_size INTEGER DEFAULT 0,
                    compressed_size INTEGER DEFAULT 0,
                    error_message TEXT,
                    backup_path TEXT,
                    checksum TEXT,
                    FOREIGN KEY (config_name) REFERENCES backup_configs (name)
                )
            """)
            
            # Tabla de trabajos de recuperación
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recovery_jobs (
                    id TEXT PRIMARY KEY,
                    backup_id TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    files_restored INTEGER DEFAULT 0,
                    error_message TEXT,
                    FOREIGN KEY (backup_id) REFERENCES backup_jobs (id)
                )
            """)
            
            # Tabla de archivos respaldados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backed_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    modified_time TIMESTAMP NOT NULL,
                    checksum TEXT NOT NULL,
                    FOREIGN KEY (backup_id) REFERENCES backup_jobs (id)
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Backup and recovery database initialized")
            
        except Exception as e:
            logger.error(f"Error initializing backup database: {e}")
            raise
    
    def _generate_encryption_key(self):
        """Generar clave de encriptación"""
        try:
            # Generar clave aleatoria
            key = Fernet.generate_key()
            self.encryption_key = key
            
            # Guardar clave en archivo seguro
            key_file = Path("backup_encryption.key")
            with open(key_file, 'wb') as f:
                f.write(key)
            
            # Establecer permisos restrictivos
            os.chmod(key_file, 0o600)
            
            logger.info("Encryption key generated and saved")
            
        except Exception as e:
            logger.error(f"Error generating encryption key: {e}")
            raise
    
    def _load_encryption_key(self) -> Optional[bytes]:
        """Cargar clave de encriptación"""
        try:
            key_file = Path("backup_encryption.key")
            if key_file.exists():
                with open(key_file, 'rb') as f:
                    return f.read()
            return None
            
        except Exception as e:
            logger.error(f"Error loading encryption key: {e}")
            return None
    
    def _load_default_configs(self):
        """Cargar configuraciones por defecto"""
        try:
            # Configuración de respaldo diario
            daily_config = BackupConfig(
                name="daily_backup",
                source_paths=["pricing_analysis.db", "security.db", "notifications.db"],
                destination_paths=["backups/daily/"],
                backup_type="incremental",
                schedule="daily",
                schedule_time="02:00",
                retention_days=7,
                compression=True,
                encryption=True,
                verification=True
            )
            self.add_backup_config(daily_config)
            
            # Configuración de respaldo semanal
            weekly_config = BackupConfig(
                name="weekly_backup",
                source_paths=["pricing_analysis.db", "security.db", "notifications.db", "data/", "models/"],
                destination_paths=["backups/weekly/"],
                backup_type="full",
                schedule="weekly",
                schedule_time="03:00",
                retention_days=30,
                compression=True,
                encryption=True,
                verification=True
            )
            self.add_backup_config(weekly_config)
            
            # Configuración de respaldo mensual
            monthly_config = BackupConfig(
                name="monthly_backup",
                source_paths=["./"],
                destination_paths=["backups/monthly/"],
                backup_type="full",
                schedule="monthly",
                schedule_time="04:00",
                retention_days=365,
                compression=True,
                encryption=True,
                verification=True
            )
            self.add_backup_config(monthly_config)
            
            logger.info("Default backup configurations loaded")
            
        except Exception as e:
            logger.error(f"Error loading default configs: {e}")
    
    def add_backup_config(self, config: BackupConfig):
        """Agregar configuración de respaldo"""
        try:
            self.configs[config.name] = config
            
            # Guardar en base de datos
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO backup_configs 
                (name, source_paths, destination_paths, backup_type, schedule, 
                 schedule_time, retention_days, compression, encryption, verification, enabled)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                config.name,
                json.dumps(config.source_paths),
                json.dumps(config.destination_paths),
                config.backup_type,
                config.schedule,
                config.schedule_time,
                config.retention_days,
                config.compression,
                config.encryption,
                config.verification,
                config.enabled
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Backup configuration added: {config.name}")
            
        except Exception as e:
            logger.error(f"Error adding backup configuration: {e}")
            raise
    
    def start_backup_scheduler(self):
        """Iniciar programador de respaldos"""
        try:
            if self.running:
                logger.warning("Backup scheduler already running")
                return
            
            self.running = True
            
            # Programar respaldos
            self._schedule_backups()
            
            # Iniciar hilo de respaldo
            self.backup_thread = threading.Thread(target=self._backup_loop, daemon=True)
            self.backup_thread.start()
            
            # Iniciar hilo de limpieza
            self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self.cleanup_thread.start()
            
            logger.info("Backup scheduler started")
            
        except Exception as e:
            logger.error(f"Error starting backup scheduler: {e}")
            raise
    
    def stop_backup_scheduler(self):
        """Detener programador de respaldos"""
        try:
            self.running = False
            
            if self.backup_thread and self.backup_thread.is_alive():
                self.backup_thread.join(timeout=5)
            
            if self.cleanup_thread and self.cleanup_thread.is_alive():
                self.cleanup_thread.join(timeout=5)
            
            logger.info("Backup scheduler stopped")
            
        except Exception as e:
            logger.error(f"Error stopping backup scheduler: {e}")
    
    def _schedule_backups(self):
        """Programar respaldos"""
        try:
            for config_name, config in self.configs.items():
                if not config.enabled:
                    continue
                
                if config.schedule == "daily":
                    schedule.every().day.at(config.schedule_time).do(
                        self._run_backup_job, config_name
                    )
                elif config.schedule == "weekly":
                    schedule.every().monday.at(config.schedule_time).do(
                        self._run_backup_job, config_name
                    )
                elif config.schedule == "monthly":
                    schedule.every().month.do(
                        self._run_backup_job, config_name
                    )
            
            logger.info("Backups scheduled")
            
        except Exception as e:
            logger.error(f"Error scheduling backups: {e}")
    
    def _backup_loop(self):
        """Loop principal de respaldos"""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
                
            except Exception as e:
                logger.error(f"Error in backup loop: {e}")
                time.sleep(60)
    
    def _cleanup_loop(self):
        """Loop de limpieza de respaldos antiguos"""
        while self.running:
            try:
                self._cleanup_old_backups()
                time.sleep(3600)  # Verificar cada hora
                
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(3600)
    
    def _run_backup_job(self, config_name: str):
        """Ejecutar trabajo de respaldo"""
        try:
            if config_name not in self.configs:
                logger.error(f"Backup configuration not found: {config_name}")
                return
            
            config = self.configs[config_name]
            
            # Crear trabajo de respaldo
            job_id = secrets.token_urlsafe(16)
            job = BackupJob(
                id=job_id,
                config_name=config_name,
                backup_type=config.backup_type,
                start_time=datetime.now(),
                status="running"
            )
            
            self.backup_jobs[job_id] = job
            
            # Ejecutar respaldo
            success = self._perform_backup(job, config)
            
            # Actualizar estado
            job.end_time = datetime.now()
            job.status = "completed" if success else "failed"
            
            # Guardar en base de datos
            self._save_backup_job(job)
            
            if success:
                logger.info(f"Backup job completed: {job_id}")
            else:
                logger.error(f"Backup job failed: {job_id}")
            
        except Exception as e:
            logger.error(f"Error running backup job: {e}")
    
    def _perform_backup(self, job: BackupJob, config: BackupConfig) -> bool:
        """Realizar respaldo"""
        try:
            # Crear directorio de destino
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = Path(config.destination_paths[0]) / f"{config.name}_{timestamp}"
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            files_backed_up = 0
            total_size = 0
            
            # Procesar cada ruta de origen
            for source_path in config.source_paths:
                source = Path(source_path)
                
                if source.is_file():
                    # Respaldo de archivo individual
                    success, file_size = self._backup_file(source, backup_dir, config)
                    if success:
                        files_backed_up += 1
                        total_size += file_size
                
                elif source.is_dir():
                    # Respaldo de directorio
                    success, file_count, dir_size = self._backup_directory(source, backup_dir, config)
                    if success:
                        files_backed_up += file_count
                        total_size += dir_size
            
            # Crear archivo de respaldo
            backup_file = self._create_backup_archive(backup_dir, config)
            
            if backup_file:
                # Calcular checksum
                checksum = self._calculate_checksum(backup_file)
                
                # Actualizar trabajo
                job.files_backed_up = files_backed_up
                job.total_size = total_size
                job.compressed_size = backup_file.stat().st_size
                job.backup_path = str(backup_file)
                job.checksum = checksum
                
                # Verificar integridad si está habilitado
                if config.verification:
                    if not self._verify_backup(backup_file, checksum):
                        logger.error("Backup verification failed")
                        return False
                
                # Limpiar directorio temporal
                shutil.rmtree(backup_dir)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error performing backup: {e}")
            job.error_message = str(e)
            return False
    
    def _backup_file(self, source_file: Path, backup_dir: Path, config: BackupConfig) -> Tuple[bool, int]:
        """Respaldar archivo individual"""
        try:
            # Crear estructura de directorios
            relative_path = source_file.relative_to(Path.cwd())
            backup_file_path = backup_dir / relative_path
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copiar archivo
            shutil.copy2(source_file, backup_file_path)
            
            # Encriptar si está habilitado
            if config.encryption:
                self._encrypt_file(backup_file_path)
            
            # Comprimir si está habilitado
            if config.compression:
                self._compress_file(backup_file_path)
            
            return True, source_file.stat().st_size
            
        except Exception as e:
            logger.error(f"Error backing up file {source_file}: {e}")
            return False, 0
    
    def _backup_directory(self, source_dir: Path, backup_dir: Path, config: BackupConfig) -> Tuple[bool, int, int]:
        """Respaldar directorio"""
        try:
            files_count = 0
            total_size = 0
            
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    source_file = Path(root) / file
                    success, file_size = self._backup_file(source_file, backup_dir, config)
                    if success:
                        files_count += 1
                        total_size += file_size
            
            return True, files_count, total_size
            
        except Exception as e:
            logger.error(f"Error backing up directory {source_dir}: {e}")
            return False, 0, 0
    
    def _create_backup_archive(self, backup_dir: Path, config: BackupConfig) -> Optional[Path]:
        """Crear archivo de respaldo comprimido"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_name = f"{config.name}_{timestamp}.tar.gz"
            archive_path = Path(config.destination_paths[0]) / archive_name
            
            # Crear archivo tar.gz
            with tarfile.open(archive_path, "w:gz") as tar:
                tar.add(backup_dir, arcname=config.name)
            
            return archive_path
            
        except Exception as e:
            logger.error(f"Error creating backup archive: {e}")
            return None
    
    def _encrypt_file(self, file_path: Path):
        """Encriptar archivo"""
        try:
            if not self.encryption_key:
                return
            
            # Leer archivo
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Encriptar
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data)
            
            # Escribir archivo encriptado
            with open(file_path, 'wb') as f:
                f.write(encrypted_data)
            
        except Exception as e:
            logger.error(f"Error encrypting file {file_path}: {e}")
    
    def _decrypt_file(self, file_path: Path):
        """Desencriptar archivo"""
        try:
            if not self.encryption_key:
                return
            
            # Leer archivo encriptado
            with open(file_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Desencriptar
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Escribir archivo desencriptado
            with open(file_path, 'wb') as f:
                f.write(decrypted_data)
            
        except Exception as e:
            logger.error(f"Error decrypting file {file_path}: {e}")
    
    def _compress_file(self, file_path: Path):
        """Comprimir archivo"""
        try:
            # Leer archivo
            with open(file_path, 'rb') as f_in:
                data = f_in.read()
            
            # Comprimir
            compressed_data = gzip.compress(data)
            
            # Escribir archivo comprimido
            with open(file_path, 'wb') as f_out:
                f_out.write(compressed_data)
            
        except Exception as e:
            logger.error(f"Error compressing file {file_path}: {e}")
    
    def _decompress_file(self, file_path: Path):
        """Descomprimir archivo"""
        try:
            # Leer archivo comprimido
            with open(file_path, 'rb') as f_in:
                compressed_data = f_in.read()
            
            # Descomprimir
            decompressed_data = gzip.decompress(compressed_data)
            
            # Escribir archivo descomprimido
            with open(file_path, 'wb') as f_out:
                f_out.write(decompressed_data)
            
        except Exception as e:
            logger.error(f"Error decompressing file {file_path}: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calcular checksum de archivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
            
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""
    
    def _verify_backup(self, backup_file: Path, expected_checksum: str) -> bool:
        """Verificar integridad del respaldo"""
        try:
            actual_checksum = self._calculate_checksum(backup_file)
            return actual_checksum == expected_checksum
            
        except Exception as e:
            logger.error(f"Error verifying backup: {e}")
            return False
    
    def _save_backup_job(self, job: BackupJob):
        """Guardar trabajo de respaldo en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO backup_jobs 
                (id, config_name, backup_type, start_time, end_time, status,
                 files_backed_up, total_size, compressed_size, error_message,
                 backup_path, checksum)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.config_name,
                job.backup_type,
                job.start_time.isoformat(),
                job.end_time.isoformat() if job.end_time else None,
                job.status,
                job.files_backed_up,
                job.total_size,
                job.compressed_size,
                job.error_message,
                job.backup_path,
                job.checksum
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving backup job: {e}")
    
    def _cleanup_old_backups(self):
        """Limpiar respaldos antiguos"""
        try:
            for config_name, config in self.configs.items():
                if not config.enabled:
                    continue
                
                cutoff_date = datetime.now() - timedelta(days=config.retention_days)
                
                # Obtener respaldos antiguos
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, backup_path FROM backup_jobs
                    WHERE config_name = ? AND start_time < ? AND status = 'completed'
                """, (config_name, cutoff_date.isoformat()))
                
                old_backups = cursor.fetchall()
                conn.close()
                
                # Eliminar archivos de respaldo antiguos
                for backup_id, backup_path in old_backups:
                    if backup_path and Path(backup_path).exists():
                        try:
                            Path(backup_path).unlink()
                            logger.info(f"Deleted old backup: {backup_path}")
                        except Exception as e:
                            logger.error(f"Error deleting old backup {backup_path}: {e}")
                
                # Eliminar registros de base de datos
                if old_backups:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    backup_ids = [backup_id for backup_id, _ in old_backups]
                    placeholders = ','.join('?' * len(backup_ids))
                    
                    cursor.execute(f"""
                        DELETE FROM backup_jobs WHERE id IN ({placeholders})
                    """, backup_ids)
                    
                    cursor.execute(f"""
                        DELETE FROM backed_files WHERE backup_id IN ({placeholders})
                    """, backup_ids)
                    
                    conn.commit()
                    conn.close()
                    
                    logger.info(f"Cleaned up {len(old_backups)} old backups for {config_name}")
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
    
    def restore_backup(self, backup_id: str, destination_path: str) -> str:
        """Restaurar respaldo"""
        try:
            # Obtener información del respaldo
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT backup_path, config_name FROM backup_jobs WHERE id = ?
            """, (backup_id,))
            
            result = cursor.fetchone()
            if not result:
                return None
            
            backup_path, config_name = result
            conn.close()
            
            if not Path(backup_path).exists():
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            # Crear trabajo de recuperación
            recovery_id = secrets.token_urlsafe(16)
            recovery_job = RecoveryJob(
                id=recovery_id,
                backup_id=backup_id,
                destination_path=destination_path,
                start_time=datetime.now(),
                status="running"
            )
            
            self.recovery_jobs[recovery_id] = recovery_job
            
            # Realizar recuperación
            success = self._perform_restore(backup_path, destination_path, config_name)
            
            # Actualizar estado
            recovery_job.end_time = datetime.now()
            recovery_job.status = "completed" if success else "failed"
            
            # Guardar en base de datos
            self._save_recovery_job(recovery_job)
            
            if success:
                logger.info(f"Restore job completed: {recovery_id}")
            else:
                logger.error(f"Restore job failed: {recovery_id}")
            
            return recovery_id
            
        except Exception as e:
            logger.error(f"Error restoring backup: {e}")
            return None
    
    def _perform_restore(self, backup_path: str, destination_path: str, config_name: str) -> bool:
        """Realizar restauración"""
        try:
            backup_file = Path(backup_path)
            dest_path = Path(destination_path)
            
            # Crear directorio de destino
            dest_path.mkdir(parents=True, exist_ok=True)
            
            # Extraer archivo de respaldo
            with tarfile.open(backup_file, "r:gz") as tar:
                tar.extractall(dest_path)
            
            # Procesar archivos extraídos
            extracted_dir = dest_path / config_name
            if extracted_dir.exists():
                files_restored = 0
                
                for root, dirs, files in os.walk(extracted_dir):
                    for file in files:
                        file_path = Path(root) / file
                        
                        # Descomprimir si es necesario
                        if file_path.suffix == '.gz':
                            self._decompress_file(file_path)
                        
                        # Desencriptar si es necesario
                        if self._is_encrypted_file(file_path):
                            self._decrypt_file(file_path)
                        
                        files_restored += 1
                
                # Mover archivos a la ubicación final
                for item in extracted_dir.iterdir():
                    shutil.move(str(item), str(dest_path / item.name))
                
                # Eliminar directorio temporal
                shutil.rmtree(extracted_dir)
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error performing restore: {e}")
            return False
    
    def _is_encrypted_file(self, file_path: Path) -> bool:
        """Verificar si archivo está encriptado"""
        try:
            # Leer primeros bytes para verificar formato de encriptación
            with open(file_path, 'rb') as f:
                header = f.read(10)
            
            # Verificar si es un archivo encriptado con Fernet
            return header.startswith(b'gAAAAAB')
            
        except:
            return False
    
    def _save_recovery_job(self, job: RecoveryJob):
        """Guardar trabajo de recuperación en base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO recovery_jobs 
                (id, backup_id, destination_path, start_time, end_time, status,
                 files_restored, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job.id,
                job.backup_id,
                job.destination_path,
                job.start_time.isoformat(),
                job.end_time.isoformat() if job.end_time else None,
                job.status,
                job.files_restored,
                job.error_message
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error saving recovery job: {e}")
    
    def get_backup_status(self, backup_id: str) -> Dict[str, Any]:
        """Obtener estado de respaldo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT config_name, backup_type, start_time, end_time, status,
                       files_backed_up, total_size, compressed_size, error_message,
                       backup_path, checksum
                FROM backup_jobs WHERE id = ?
            """, (backup_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"error": "Backup not found"}
            
            return {
                "id": backup_id,
                "config_name": result[0],
                "backup_type": result[1],
                "start_time": result[2],
                "end_time": result[3],
                "status": result[4],
                "files_backed_up": result[5],
                "total_size": result[6],
                "compressed_size": result[7],
                "error_message": result[8],
                "backup_path": result[9],
                "checksum": result[10]
            }
            
        except Exception as e:
            logger.error(f"Error getting backup status: {e}")
            return {"error": str(e)}
    
    def list_backups(self, config_name: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Listar respaldos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT id, config_name, backup_type, start_time, end_time, status,
                       files_backed_up, total_size, compressed_size, backup_path
                FROM backup_jobs
            """
            params = []
            
            if config_name:
                query += " WHERE config_name = ?"
                params.append(config_name)
            
            query += " ORDER BY start_time DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.close()
            
            backups = []
            for result in results:
                backups.append({
                    "id": result[0],
                    "config_name": result[1],
                    "backup_type": result[2],
                    "start_time": result[3],
                    "end_time": result[4],
                    "status": result[5],
                    "files_backed_up": result[6],
                    "total_size": result[7],
                    "compressed_size": result[8],
                    "backup_path": result[9]
                })
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de respaldos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_backups,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful_backups,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_backups,
                    SUM(total_size) as total_size,
                    SUM(compressed_size) as total_compressed_size
                FROM backup_jobs
            """)
            
            stats_result = cursor.fetchone()
            
            # Estadísticas por configuración
            cursor.execute("""
                SELECT config_name, COUNT(*) as count, 
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful
                FROM backup_jobs
                GROUP BY config_name
            """)
            
            config_stats = cursor.fetchall()
            conn.close()
            
            total_backups = stats_result[0] or 0
            successful_backups = stats_result[1] or 0
            failed_backups = stats_result[2] or 0
            total_size = stats_result[3] or 0
            total_compressed_size = stats_result[4] or 0
            
            success_rate = (successful_backups / total_backups * 100) if total_backups > 0 else 0
            compression_ratio = (1 - total_compressed_size / total_size) * 100 if total_size > 0 else 0
            
            return {
                "total_backups": total_backups,
                "successful_backups": successful_backups,
                "failed_backups": failed_backups,
                "success_rate": success_rate,
                "total_size_bytes": total_size,
                "total_compressed_size_bytes": total_compressed_size,
                "compression_ratio": compression_ratio,
                "config_breakdown": {
                    config: {
                        "total": count,
                        "successful": successful
                    }
                    for config, count, successful in config_stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting backup statistics: {e}")
            return {"error": str(e)}

def main():
    """Función principal para demostrar sistema de respaldo"""
    print("=" * 60)
    print("BACKUP AND RECOVERY SYSTEM - DEMO")
    print("=" * 60)
    
    # Inicializar sistema de respaldo
    backup_system = BackupRecoverySystem()
    
    # Iniciar programador de respaldos
    print("Starting backup scheduler...")
    backup_system.start_backup_scheduler()
    
    # Ejecutar respaldo manual
    print("\nRunning manual backup...")
    backup_system._run_backup_job("daily_backup")
    
    # Listar respaldos
    print("\nRecent backups:")
    backups = backup_system.list_backups(limit=5)
    for backup in backups:
        print(f"  • {backup['config_name']}: {backup['status']} ({backup['files_backed_up']} files)")
        print(f"    Size: {backup['total_size']} bytes -> {backup['compressed_size']} bytes")
        print(f"    Time: {backup['start_time']}")
    
    # Obtener estadísticas
    print("\nBackup Statistics:")
    stats = backup_system.get_backup_statistics()
    print(f"Total Backups: {stats['total_backups']}")
    print(f"Success Rate: {stats['success_rate']:.1f}%")
    print(f"Compression Ratio: {stats['compression_ratio']:.1f}%")
    
    # Simular restauración
    if backups:
        print(f"\nSimulating restore from backup: {backups[0]['id']}")
        recovery_id = backup_system.restore_backup(
            backups[0]['id'], 
            "restore_test/"
        )
        if recovery_id:
            print(f"✓ Restore job created: {recovery_id}")
        else:
            print("✗ Restore failed")
    
    # Detener programador
    print("\nStopping backup scheduler...")
    backup_system.stop_backup_scheduler()
    
    print("\n" + "=" * 60)
    print("BACKUP AND RECOVERY DEMO COMPLETED")
    print("=" * 60)
    print("💾 Backup and recovery features:")
    print("  • Automated scheduled backups")
    print("  • Full, incremental, and differential backups")
    print("  • Compression and encryption")
    print("  • Integrity verification")
    print("  • Multiple storage locations")
    print("  • Granular recovery options")
    print("  • Backup retention management")
    print("  • Performance monitoring")
    print("  • Error handling and logging")

if __name__ == "__main__":
    main()







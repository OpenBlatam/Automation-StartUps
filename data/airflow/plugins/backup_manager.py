"""
Sistema de Backups Automáticos con Soporte Multi-Cloud - Versión Mejorada.

Proporciona:
- Backups automáticos de bases de datos
- Backups de archivos y directorios
- Soporte para AWS S3, Azure Blob Storage, GCP Cloud Storage
- Encriptación de backups
- Verificación de integridad
- Retención automática
- Retry logic robusto
- Validación de espacio en disco
- Métricas y monitoreo
- Paralelización de backups
"""
import logging
import os
import gzip
import shutil
import tarfile
import time
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

try:
    from azure.storage.blob import BlobServiceClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from google.cloud import storage as gcs_storage
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from data.airflow.plugins.backup_encryption import BackupEncryption
from data.airflow.plugins.backup_notifications import BackupNotifier

logger = logging.getLogger(__name__)

# Intentar importar tenacity para retry mejorado
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log,
        after_log
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False


def retry_with_backoff(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para retry con backoff exponencial.
    
    Args:
        max_attempts: Número máximo de intentos
        backoff_factor: Factor de backoff exponencial
        exceptions: Excepciones que deben retry
    """
    def decorator(func: Callable) -> Callable:
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=backoff_factor, min=1, max=60),
                retry=retry_if_exception_type(exceptions),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                after=after_log(logger, logging.INFO),
                reraise=True
            )
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        else:
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = min(backoff_factor ** attempt, 60)
                            logger.warning(
                                f"Intento {attempt + 1}/{max_attempts} falló: {e}. "
                                f"Reintentando en {wait_time:.1f}s"
                            )
                            time.sleep(wait_time)
                        else:
                            raise
                if last_exception:
                    raise last_exception
                raise RuntimeError("Función falló sin excepción")
            return wrapper
    return decorator


class BackupType(Enum):
    """Tipos de backup disponibles."""
    FULL = "full"
    INCREMENTAL = "incremental"
    DIFFERENTIAL = "differential"


class BackupStatus(Enum):
    """Estados de backup."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class BackupConfig:
    """Configuración de backup."""
    backup_type: BackupType = BackupType.FULL
    encrypt: bool = True
    compress: bool = True
    verify_integrity: bool = True
    retention_days: int = 30
    cloud_sync: bool = True
    cloud_provider: Optional[str] = None  # 'aws', 'azure', 'gcp'
    cloud_config: Optional[Dict[str, Any]] = None
    min_disk_space_gb: float = 5.0  # Espacio mínimo requerido en GB
    max_parallel_backups: int = 3  # Máximo de backups paralelos
    enable_metrics: bool = True  # Habilitar métricas
    timeout_seconds: Optional[int] = None  # Timeout para operaciones


@dataclass
class BackupResult:
    """Resultado de un backup."""
    backup_id: str
    status: BackupStatus
    file_path: Optional[str] = None
    cloud_path: Optional[str] = None
    size_bytes: int = 0
    checksum: Optional[str] = None
    created_at: datetime = None
    duration_seconds: float = 0.0
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    compression_ratio: Optional[float] = None  # Ratio de compresión
    encryption_time: Optional[float] = None  # Tiempo de encriptación
    upload_time: Optional[float] = None  # Tiempo de subida a nube
    disk_usage_before: Optional[float] = None  # Uso de disco antes
    disk_usage_after: Optional[float] = None  # Uso de disco después


class DatabaseBackup:
    """Backup de bases de datos."""
    
    def __init__(self, connection_string: str, db_type: str = "postgresql"):
        """
        Inicializa backup de base de datos.
        
        Args:
            connection_string: Connection string de la BD
            db_type: Tipo de BD (postgresql, mysql, etc.)
        """
        self.connection_string = connection_string
        self.db_type = db_type
    
    def create_backup(
        self,
        output_path: str,
        tables: Optional[List[str]] = None,
        schema_only: bool = False
    ) -> BackupResult:
        """
        Crea backup de base de datos.
        
        Args:
            output_path: Ruta del archivo de backup
            tables: Tablas específicas (None = todas)
            schema_only: Solo schema sin datos
        """
        backup_id = f"db-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        start_time = datetime.now()
        
        try:
            if self.db_type == "postgresql":
                return self._backup_postgresql(
                    output_path, backup_id, tables, schema_only, start_time
                )
            elif self.db_type == "mysql":
                return self._backup_mysql(
                    output_path, backup_id, tables, schema_only, start_time
                )
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            return BackupResult(
                backup_id=backup_id,
                status=BackupStatus.FAILED,
                error=str(e),
                created_at=start_time
            )
    
    def _backup_postgresql(
        self,
        output_path: str,
        backup_id: str,
        tables: Optional[List[str]],
        schema_only: bool,
        start_time: datetime
    ) -> BackupResult:
        """Backup de PostgreSQL usando pg_dump."""
        import subprocess
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ["pg_dump", self.connection_string]
        
        if schema_only:
            cmd.append("--schema-only")
        else:
            cmd.append("--data-only" if "--schema-only" not in str(cmd) else "")
        
        if tables:
            for table in tables:
                cmd.extend(["--table", table])
        
        with open(output_path, 'wb') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )
        
        file_size = output_file.stat().st_size
        checksum = self._calculate_checksum(output_path)
        duration = (datetime.now() - start_time).total_seconds()
        
        return BackupResult(
            backup_id=backup_id,
            status=BackupStatus.COMPLETED,
            file_path=output_path,
            size_bytes=file_size,
            checksum=checksum,
            created_at=start_time,
            duration_seconds=duration
        )
    
    def _backup_mysql(
        self,
        output_path: str,
        backup_id: str,
        tables: Optional[List[str]],
        schema_only: bool,
        start_time: datetime
    ) -> BackupResult:
        """Backup de MySQL usando mysqldump."""
        import subprocess
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        cmd = ["mysqldump", self.connection_string]
        
        if schema_only:
            cmd.append("--no-data")
        
        if tables:
            cmd.extend(tables)
        
        with open(output_path, 'wb') as f:
            result = subprocess.run(
                cmd,
                stdout=f,
                stderr=subprocess.PIPE,
                check=True
            )
        
        file_size = output_file.stat().st_size
        checksum = self._calculate_checksum(output_path)
        duration = (datetime.now() - start_time).total_seconds()
        
        return BackupResult(
            backup_id=backup_id,
            status=BackupStatus.COMPLETED,
            file_path=output_path,
            size_bytes=file_size,
            checksum=checksum,
            created_at=start_time,
            duration_seconds=duration
        )
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum SHA256 de un archivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class FileBackup:
    """Backup de archivos y directorios."""
    
    def create_backup(
        self,
        source_paths: Union[str, List[str]],
        output_path: str,
        exclude_patterns: Optional[List[str]] = None
    ) -> BackupResult:
        """
        Crea backup de archivos/directorios.
        
        Args:
            source_paths: Ruta(s) a respaldar
            output_path: Ruta del archivo de backup (.tar.gz)
            exclude_patterns: Patrones a excluir
        """
        backup_id = f"file-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        start_time = datetime.now()
        
        try:
            if isinstance(source_paths, str):
                source_paths = [source_paths]
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Crear archivo tar.gz
            with tarfile.open(output_path, "w:gz") as tar:
                for source_path in source_paths:
                    source = Path(source_path)
                    if not source.exists():
                        logger.warning(f"Source path does not exist: {source_path}")
                        continue
                    
                    if source.is_file():
                        tar.add(source, arcname=source.name, filter=self._filter_excludes(exclude_patterns))
                    elif source.is_dir():
                        tar.add(source, arcname=source.name, filter=self._filter_excludes(exclude_patterns))
            
            file_size = output_file.stat().st_size
            checksum = self._calculate_checksum(output_path)
            duration = (datetime.now() - start_time).total_seconds()
            
            return BackupResult(
                backup_id=backup_id,
                status=BackupStatus.COMPLETED,
                file_path=output_path,
                size_bytes=file_size,
                checksum=checksum,
                created_at=start_time,
                duration_seconds=duration
            )
        except Exception as e:
            logger.error(f"File backup failed: {e}", exc_info=True)
            return BackupResult(
                backup_id=backup_id,
                status=BackupStatus.FAILED,
                error=str(e),
                created_at=start_time
            )
    
    def _filter_excludes(self, exclude_patterns: Optional[List[str]]):
        """Filtro para excluir patrones."""
        if not exclude_patterns:
            return None
        
        def filter_func(tarinfo):
            import fnmatch
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(tarinfo.name, pattern):
                    return None
            return tarinfo
        
        return filter_func
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum SHA256 de un archivo."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()


class CloudSync:
    """Sincronización con servicios de nube."""
    
    def __init__(self, provider: str, config: Dict[str, Any]):
        """
        Inicializa sincronización con nube.
        
        Args:
            provider: 'aws', 'azure', 'gcp'
            config: Configuración específica del proveedor
        """
        self.provider = provider
        self.config = config
        self._client = None
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        encrypt: bool = False,
        encryption_key: Optional[bytes] = None
    ) -> bool:
        """
        Sube archivo a la nube.
        
        Args:
            local_path: Ruta local del archivo
            remote_path: Ruta remota (bucket/key)
            encrypt: Si encriptar antes de subir
            encryption_key: Clave de encriptación
        """
        try:
            if encrypt and encryption_key:
                # Encriptar antes de subir
                from data.airflow.plugins.backup_encryption import BackupEncryption
                enc = BackupEncryption(encryption_key)
                encrypted_path = local_path + ".encrypted"
                enc.encrypt_file(local_path, encrypted_path)
                local_path = encrypted_path
            
            if self.provider == "aws":
                return self._upload_to_s3(local_path, remote_path)
            elif self.provider == "azure":
                return self._upload_to_azure(local_path, remote_path)
            elif self.provider == "gcp":
                return self._upload_to_gcp(local_path, remote_path)
            else:
                raise ValueError(f"Unsupported cloud provider: {self.provider}")
        except Exception as e:
            logger.error(f"Cloud upload failed: {e}", exc_info=True)
            return False
    
    def _upload_to_s3(self, local_path: str, remote_path: str) -> bool:
        """Sube a AWS S3."""
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 not available")
        
        bucket = self.config.get("bucket")
        if not bucket:
            raise ValueError("S3 bucket not configured")
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.config.get("access_key_id"),
            aws_secret_access_key=self.config.get("secret_access_key"),
            region_name=self.config.get("region", "us-east-1")
        )
        
        try:
            s3_client.upload_file(
                local_path,
                bucket,
                remote_path,
                ExtraArgs={
                    'ServerSideEncryption': 'AES256',
                    'Metadata': {
                        'backup-date': datetime.now().isoformat(),
                        'original-size': str(Path(local_path).stat().st_size)
                    }
                }
            )
            logger.info(f"Uploaded {local_path} to s3://{bucket}/{remote_path}")
            return True
        except ClientError as e:
            logger.error(f"S3 upload error: {e}")
            return False
    
    def _upload_to_azure(self, local_path: str, remote_path: str) -> bool:
        """Sube a Azure Blob Storage."""
        if not AZURE_AVAILABLE:
            raise ImportError("azure-storage-blob not available")
        
        connection_string = self.config.get("connection_string")
        container = self.config.get("container")
        
        if not connection_string or not container:
            raise ValueError("Azure connection_string and container required")
        
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service.get_blob_client(container=container, blob=remote_path)
        
        with open(local_path, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        
        logger.info(f"Uploaded {local_path} to Azure {container}/{remote_path}")
        return True
    
    def _upload_to_gcp(self, local_path: str, remote_path: str) -> bool:
        """Sube a GCP Cloud Storage."""
        if not GCS_AVAILABLE:
            raise ImportError("google-cloud-storage not available")
        
        bucket_name = self.config.get("bucket")
        credentials_path = self.config.get("credentials_path")
        
        if not bucket_name:
            raise ValueError("GCP bucket not configured")
        
        if credentials_path:
            storage_client = gcs_storage.Client.from_service_account_json(credentials_path)
        else:
            storage_client = gcs_storage.Client()
        
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(remote_path)
        
        blob.upload_from_filename(local_path)
        logger.info(f"Uploaded {local_path} to gs://{bucket_name}/{remote_path}")
        return True
    
    def list_backups(self, prefix: str = "") -> List[Dict[str, Any]]:
        """Lista backups en la nube."""
        try:
            if self.provider == "aws":
                return self._list_s3_backups(prefix)
            elif self.provider == "azure":
                return self._list_azure_backups(prefix)
            elif self.provider == "gcp":
                return self._list_gcp_backups(prefix)
            else:
                return []
        except Exception as e:
            logger.error(f"List backups failed: {e}")
            return []
    
    def _list_s3_backups(self, prefix: str) -> List[Dict[str, Any]]:
        """Lista backups en S3."""
        if not BOTO3_AVAILABLE:
            return []
        
        bucket = self.config.get("bucket")
        s3_client = boto3.client(
            's3',
            aws_access_key_id=self.config.get("access_key_id"),
            aws_secret_access_key=self.config.get("secret_access_key"),
            region_name=self.config.get("region", "us-east-1")
        )
        
        try:
            response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
            return [
                {
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat()
                }
                for obj in response.get('Contents', [])
            ]
        except ClientError:
            return []
    
    def _list_azure_backups(self, prefix: str) -> List[Dict[str, Any]]:
        """Lista backups en Azure."""
        if not AZURE_AVAILABLE:
            return []
        
        connection_string = self.config.get("connection_string")
        container = self.config.get("container")
        
        blob_service = BlobServiceClient.from_connection_string(connection_string)
        container_client = blob_service.get_container_client(container)
        
        blobs = []
        for blob in container_client.list_blobs(name_starts_with=prefix):
            blobs.append({
                'key': blob.name,
                'size': blob.size,
                'last_modified': blob.last_modified.isoformat()
            })
        
        return blobs
    
    def _list_gcp_backups(self, prefix: str) -> List[Dict[str, Any]]:
        """Lista backups en GCP."""
        if not GCS_AVAILABLE:
            return []
        
        bucket_name = self.config.get("bucket")
        credentials_path = self.config.get("credentials_path")
        
        if credentials_path:
            storage_client = gcs_storage.Client.from_service_account_json(credentials_path)
        else:
            storage_client = gcs_storage.Client()
        
        bucket = storage_client.bucket(bucket_name)
        blobs = []
        for blob in bucket.list_blobs(prefix=prefix):
            blobs.append({
                'key': blob.name,
                'size': blob.size,
                'last_modified': blob.updated.isoformat()
            })
        
        return blobs
    
    def delete_old_backups(self, prefix: str, retention_days: int) -> int:
        """Elimina backups antiguos según retención."""
        deleted_count = 0
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        try:
            backups = self.list_backups(prefix)
            for backup in backups:
                backup_date = datetime.fromisoformat(backup['last_modified'])
                if backup_date < cutoff_date:
                    if self._delete_backup(backup['key']):
                        deleted_count += 1
        except Exception as e:
            logger.error(f"Delete old backups failed: {e}")
        
        return deleted_count
    
    def _delete_backup(self, key: str) -> bool:
        """Elimina un backup específico."""
        try:
            if self.provider == "aws":
                bucket = self.config.get("bucket")
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=self.config.get("access_key_id"),
                    aws_secret_access_key=self.config.get("secret_access_key"),
                    region_name=self.config.get("region", "us-east-1")
                )
                s3_client.delete_object(Bucket=bucket, Key=key)
                return True
            # Implementar para Azure y GCP si es necesario
            return False
        except Exception as e:
            logger.error(f"Delete backup failed: {e}")
            return False


class BackupManager:
    """Gestor principal de backups - Versión Mejorada."""
    
    def __init__(
        self,
        backup_dir: str = "/tmp/backups",
        encryption_key: Optional[bytes] = None,
        cloud_config: Optional[Dict[str, Any]] = None
    ):
        """
        Inicializa gestor de backups.
        
        Args:
            backup_dir: Directorio local para backups
            encryption_key: Clave para encriptación (opcional)
            cloud_config: Configuración de nube (opcional)
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.encryption = BackupEncryption(encryption_key) if encryption_key else None
        self.notifier = BackupNotifier()
        
        self.cloud_sync = None
        if cloud_config:
            self.cloud_sync = CloudSync(
                provider=cloud_config.get("provider"),
                config=cloud_config.get("config", {})
            )
        
        self._metrics_lock = threading.Lock()
        self._metrics = {
            'total_backups': 0,
            'successful_backups': 0,
            'failed_backups': 0,
            'total_size_bytes': 0,
            'total_duration_seconds': 0.0
        }
    
    def _check_disk_space(self, required_gb: float) -> tuple[bool, float]:
        """
        Verifica espacio disponible en disco.
        
        Args:
            required_gb: Espacio requerido en GB
        
        Returns:
            Tuple de (tiene_espacio, espacio_disponible_gb)
        """
        try:
            disk_usage = psutil.disk_usage(str(self.backup_dir))
            available_gb = disk_usage.free / (1024 ** 3)
            has_space = available_gb >= required_gb
            return has_space, available_gb
        except Exception as e:
            logger.warning(f"Error checking disk space: {e}")
            return True, float('inf')  # Asumir que hay espacio si no se puede verificar
    
    def _verify_connectivity(self, connection_string: str, db_type: str) -> bool:
        """
        Verifica conectividad a base de datos antes de backup.
        
        Args:
            connection_string: Connection string
            db_type: Tipo de BD
        
        Returns:
            True si conecta, False si no
        """
        try:
            if db_type == "postgresql":
                import psycopg2
                conn = psycopg2.connect(connection_string)
                conn.close()
                return True
            elif db_type == "mysql":
                import mysql.connector
                conn = mysql.connector.connect(connection_string)
                conn.close()
                return True
            return True  # Asumir OK si no se puede verificar
        except Exception as e:
            logger.warning(f"Connectivity check failed: {e}")
            return False
    
    @retry_with_backoff(max_attempts=3, exceptions=(Exception,))
    def backup_database(
        self,
        connection_string: str,
        db_type: str = "postgresql",
        config: Optional[BackupConfig] = None
    ) -> BackupResult:
        """
        Crea backup de base de datos con validaciones mejoradas.
        
        Args:
            connection_string: Connection string de BD
            db_type: Tipo de BD
            config: Configuración de backup
        """
        if config is None:
            config = BackupConfig()
        
        # Validar espacio en disco
        has_space, available_gb = self._check_disk_space(config.min_disk_space_gb)
        if not has_space:
            error_msg = f"Insufficient disk space. Required: {config.min_disk_space_gb}GB, Available: {available_gb:.2f}GB"
            logger.error(error_msg)
            result = BackupResult(
                backup_id=f"db-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                status=BackupStatus.FAILED,
                error=error_msg,
                created_at=datetime.now()
            )
            self.notifier.notify_backup_result(result)
            return result
        
        # Verificar conectividad
        if not self._verify_connectivity(connection_string, db_type):
            error_msg = "Database connectivity check failed"
            logger.warning(error_msg)
            # Continuar de todas formas, puede ser un problema temporal
        
        # Obtener uso de disco antes
        disk_usage_before = self._get_disk_usage()
        
        db_backup = DatabaseBackup(connection_string, db_type)
        output_path = self.backup_dir / f"db-{datetime.now().strftime('%Y%m%d-%H%M%S')}.sql"
        
        try:
            result = db_backup.create_backup(str(output_path))
            
            # Procesar backup según configuración
            if result.status == BackupStatus.COMPLETED:
                result = self._process_backup(result, config)
                result.disk_usage_before = disk_usage_before
                result.disk_usage_after = self._get_disk_usage()
            
            # Actualizar métricas
            self._update_metrics(result)
            
            # Registrar en Prometheus si está disponible
            try:
                from data.airflow.plugins.backup_prometheus import get_backup_metrics
                metrics = get_backup_metrics()
                metrics.record_backup(
                    backup_type='database',
                    status=result.status.value,
                    duration_seconds=result.duration_seconds,
                    size_bytes=result.size_bytes,
                    encryption_time=result.encryption_time,
                    upload_time=result.upload_time,
                    cloud_provider=self.cloud_sync.provider if self.cloud_sync else None
                )
            except Exception:
                pass  # Silenciosamente ignorar si Prometheus no está disponible
            
        except Exception as e:
            logger.error(f"Backup failed: {e}", exc_info=True)
            result = BackupResult(
                backup_id=f"db-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                status=BackupStatus.FAILED,
                error=str(e),
                created_at=datetime.now()
            )
        
        # Notificar
        self.notifier.notify_backup_result(result)
        
        return result
    
    def _get_disk_usage(self) -> float:
        """Obtiene uso de disco en GB."""
        try:
            disk_usage = psutil.disk_usage(str(self.backup_dir))
            return disk_usage.used / (1024 ** 3)
        except Exception:
            return 0.0
    
    def _update_metrics(self, result: BackupResult) -> None:
        """Actualiza métricas de backup."""
        with self._metrics_lock:
            self._metrics['total_backups'] += 1
            if result.status == BackupStatus.COMPLETED:
                self._metrics['successful_backups'] += 1
                self._metrics['total_size_bytes'] += result.size_bytes
                self._metrics['total_duration_seconds'] += result.duration_seconds
            else:
                self._metrics['failed_backups'] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas actuales."""
        with self._metrics_lock:
            metrics = self._metrics.copy()
            if metrics['total_backups'] > 0:
                metrics['success_rate'] = metrics['successful_backups'] / metrics['total_backups']
                metrics['avg_duration_seconds'] = metrics['total_duration_seconds'] / metrics['successful_backups']
            else:
                metrics['success_rate'] = 0.0
                metrics['avg_duration_seconds'] = 0.0
            return metrics
    
    def backup_files(
        self,
        source_paths: Union[str, List[str]],
        config: Optional[BackupConfig] = None
    ) -> BackupResult:
        """
        Crea backup de archivos.
        
        Args:
            source_paths: Ruta(s) a respaldar
            config: Configuración de backup
        """
        if config is None:
            config = BackupConfig()
        
        file_backup = FileBackup()
        output_path = self.backup_dir / f"files-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tar.gz"
        
        result = file_backup.create_backup(source_paths, str(output_path))
        
        # Procesar backup según configuración
        if result.status == BackupStatus.COMPLETED:
            result = self._process_backup(result, config)
        
        # Notificar
        self.notifier.notify_backup_result(result)
        
        return result
    
    def _process_backup(self, result: BackupResult, config: BackupConfig) -> BackupResult:
        """Procesa backup (comprimir, encriptar, subir a nube) con métricas mejoradas."""
        if not result.file_path:
            return result
        
        file_path = Path(result.file_path)
        original_size = file_path.stat().st_size
        
        # Comprimir si no está comprimido
        if config.compress and not file_path.suffix == '.gz':
            compressed_path = str(file_path) + '.gz'
            compress_start = time.time()
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            compressed_size = Path(compressed_path).stat().st_size
            result.compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            
            file_path.unlink()
            result.file_path = compressed_path
            file_path = Path(compressed_path)
            logger.info(f"Compressed backup: {original_size / (1024**2):.2f}MB -> {compressed_size / (1024**2):.2f}MB (ratio: {result.compression_ratio:.2f}x)")
        
        # Encriptar
        if config.encrypt and self.encryption:
            encrypted_path = str(file_path) + '.encrypted'
            encrypt_start = time.time()
            
            if self.encryption.encrypt_file(str(file_path), encrypted_path):
                result.encryption_time = time.time() - encrypt_start
                file_path.unlink()
                result.file_path = encrypted_path
                file_path = Path(encrypted_path)
                logger.info(f"Encrypted backup in {result.encryption_time:.2f}s")
            else:
                logger.error("Encryption failed")
                result.status = BackupStatus.FAILED
                result.error = "Encryption failed"
                return result
        
        # Actualizar tamaño
        result.size_bytes = file_path.stat().st_size
        
        # Verificar integridad
        if config.verify_integrity:
            result.checksum = self._calculate_checksum(str(file_path))
            result.status = BackupStatus.VERIFIED
        
        # Subir a nube con retry
        if config.cloud_sync and self.cloud_sync:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
            remote_path = f"backups/{result.backup_id}/{file_path.name}"
            upload_start = time.time()
            
            try:
                if self._upload_with_retry(str(file_path), remote_path, max_attempts=3):
                    result.cloud_path = remote_path
                    result.upload_time = time.time() - upload_start
                    logger.info(f"Uploaded to cloud in {result.upload_time:.2f}s")
                else:
                    logger.warning("Cloud upload failed after retries")
            except Exception as e:
                logger.error(f"Cloud upload error: {e}")
        
        return result
    
    @retry_with_backoff(max_attempts=3, exceptions=(Exception,))
    def _upload_with_retry(self, local_path: str, remote_path: str, max_attempts: int = 3) -> bool:
        """Sube archivo a nube con retry."""
        if not self.cloud_sync:
            return False
        return self.cloud_sync.upload_file(local_path, remote_path)
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum SHA256."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def backup_multiple_databases(
        self,
        databases: List[Dict[str, Any]],
        config: Optional[BackupConfig] = None
    ) -> List[BackupResult]:
        """
        Hace backup de múltiples bases de datos en paralelo.
        
        Args:
            databases: Lista de dicts con 'connection_string' y 'db_type'
            config: Configuración de backup
        
        Returns:
            Lista de resultados de backup
        """
        if config is None:
            config = BackupConfig()
        
        max_workers = min(config.max_parallel_backups, len(databases))
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.backup_database,
                    db['connection_string'],
                    db.get('db_type', 'postgresql'),
                    config
                ): db
                for db in databases
            }
            
            for future in as_completed(futures):
                db_info = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                    logger.info(f"Completed backup for {db_info.get('name', 'unknown')}: {result.status.value}")
                except Exception as e:
                    logger.error(f"Backup failed for {db_info.get('name', 'unknown')}: {e}")
                    results.append(BackupResult(
                        backup_id=f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                        status=BackupStatus.FAILED,
                        error=str(e),
                        created_at=datetime.now()
                    ))
        
        return results
    
    def cleanup_old_backups(self, retention_days: int) -> Dict[str, Any]:
        """
        Limpia backups antiguos locales y en nube con métricas.
        
        Args:
            retention_days: Días de retención
        
        Returns:
            Dict con estadísticas de limpieza
        """
        deleted_local = 0
        freed_space_bytes = 0
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Limpiar locales
        for backup_file in self.backup_dir.glob("*"):
            if backup_file.is_file():
                file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                if file_time < cutoff_date:
                    file_size = backup_file.stat().st_size
                    backup_file.unlink()
                    deleted_local += 1
                    freed_space_bytes += file_size
        
        # Limpiar en nube
        deleted_cloud = 0
        if self.cloud_sync:
            deleted_cloud = self.cloud_sync.delete_old_backups("backups/", retention_days)
        
        freed_space_gb = freed_space_bytes / (1024 ** 3)
        
        logger.info(
            f"Cleaned up {deleted_local} local and {deleted_cloud} cloud backups. "
            f"Freed {freed_space_gb:.2f}GB"
        )
        
        return {
            'deleted_local': deleted_local,
            'deleted_cloud': deleted_cloud,
            'freed_space_gb': freed_space_gb,
            'freed_space_bytes': freed_space_bytes
        }


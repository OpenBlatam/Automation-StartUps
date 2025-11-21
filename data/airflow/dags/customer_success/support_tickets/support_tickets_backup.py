"""
DAG de Backup Automatizado de Tickets de Soporte

Realiza backups regulares:
- Backup completo de tablas
- Backup incremental
- Compresión de archivos
- Upload a storage externo (S3, GCS, etc.)
- Verificación de integridad
"""
import logging
import os
import subprocess
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    from airflow import DAG
    from airflow.decorators import task, dag
    from airflow.utils.dates import days_ago
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "support",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

BACKUP_BASE_PATH = os.getenv("SUPPORT_BACKUP_PATH", "/tmp/support_backups")
RETENTION_DAYS = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))


@dag(
    dag_id="support_tickets_backup",
    start_date=days_ago(1),
    schedule="0 2 * * *",  # Diario a las 2 AM
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Backup automatizado diario del sistema de tickets",
    tags=["support", "backup", "maintenance"],
)
def support_tickets_backup():
    """DAG de backup automatizado."""
    
    @task(task_id="full_backup")
    def full_backup() -> str:
        """Realiza backup completo de todas las tablas."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Crear directorio de backup
        os.makedirs(BACKUP_BASE_PATH, exist_ok=True)
        
        backup_file = f"{BACKUP_BASE_PATH}/support_full_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        
        # Usar pg_dump para backup completo
        conn = hook.get_connection("postgres_default")
        
        pg_dump_cmd = [
            "pg_dump",
            "-h", conn.host,
            "-U", conn.login,
            "-d", conn.schema,
            "-F", "c",  # Custom format
            "-f", backup_file
        ]
        
        env = os.environ.copy()
        env["PGPASSWORD"] = conn.password
        
        try:
            result = subprocess.run(
                pg_dump_cmd,
                env=env,
                capture_output=True,
                text=True,
                check=True
            )
            
            # Comprimir
            compressed_file = f"{backup_file}.gz"
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # Eliminar archivo sin comprimir
            os.remove(backup_file)
            
            file_size_mb = os.path.getsize(compressed_file) / (1024 * 1024)
            
            logger.info(f"Full backup created: {compressed_file} ({file_size_mb:.2f} MB)")
            return compressed_file
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            raise
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise
    
    @task(task_id="incremental_backup")
    def incremental_backup() -> str:
        """Realiza backup incremental (solo datos nuevos/modificados)."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        os.makedirs(BACKUP_BASE_PATH, exist_ok=True)
        
        # Backup de tickets del último día
        backup_file = f"{BACKUP_BASE_PATH}/support_incremental_{datetime.now().strftime('%Y%m%d')}.csv"
        
        with hook.get_conn() as conn:
            query = """
                SELECT *
                FROM support_tickets
                WHERE updated_at >= CURRENT_DATE - INTERVAL '1 day'
                OR created_at >= CURRENT_DATE - INTERVAL '1 day'
            """
            
            import pandas as pd
            df = pd.read_sql_query(query, conn)
            df.to_csv(backup_file, index=False)
        
        # Comprimir
        compressed_file = f"{backup_file}.gz"
        with open(backup_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.writelines(f_in)
        
        os.remove(backup_file)
        
        logger.info(f"Incremental backup created: {compressed_file}")
        return compressed_file
    
    @task(task_id="verify_backup")
    def verify_backup(backup_file: str) -> Dict[str, Any]:
        """Verifica integridad del backup."""
        try:
            # Verificar que el archivo existe y no está vacío
            if not os.path.exists(backup_file):
                raise Exception(f"Backup file not found: {backup_file}")
            
            file_size = os.path.getsize(backup_file)
            if file_size == 0:
                raise Exception(f"Backup file is empty: {backup_file}")
            
            # Verificar que es un archivo gzip válido
            if backup_file.endswith('.gz'):
                with gzip.open(backup_file, 'rb') as f:
                    # Intentar leer un poco
                    f.read(1024)
            
            logger.info(f"Backup verified: {backup_file} ({file_size / 1024 / 1024:.2f} MB)")
            
            return {
                "backup_file": backup_file,
                "file_size_mb": file_size / 1024 / 1024,
                "verified": True,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Backup verification failed: {e}")
            raise
    
    @task(task_id="upload_to_storage")
    def upload_to_storage(backup_file: str) -> Dict[str, Any]:
        """Sube backup a storage externo (opcional)."""
        # Aquí se integraría con S3, GCS, Azure Blob, etc.
        # Por ahora solo retorna información
        
        result = {
            "backup_file": backup_file,
            "uploaded": False,  # Implementar cuando haya storage configurado
            "storage_type": None,
            "upload_url": None
        }
        
        # Ejemplo para S3 (comentado):
        # try:
        #     import boto3
        #     s3_client = boto3.client('s3')
        #     s3_key = f"support-backups/{os.path.basename(backup_file)}"
        #     s3_client.upload_file(backup_file, 'your-bucket', s3_key)
        #     result["uploaded"] = True
        #     result["storage_type"] = "s3"
        #     result["upload_url"] = f"s3://your-bucket/{s3_key}"
        # except Exception as e:
        #     logger.warning(f"Failed to upload to S3: {e}")
        
        logger.info(f"Backup ready for storage: {backup_file}")
        return result
    
    @task(task_id="cleanup_old_backups")
    def cleanup_old_backups() -> Dict[str, Any]:
        """Limpia backups antiguos según política de retención."""
        import glob
        
        backup_pattern = f"{BACKUP_BASE_PATH}/support_*.gz"
        backup_files = glob.glob(backup_pattern)
        
        deleted_count = 0
        total_size_freed = 0
        
        cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
        
        for backup_file in backup_files:
            file_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
            
            if file_time < cutoff_date:
                file_size = os.path.getsize(backup_file)
                try:
                    os.remove(backup_file)
                    deleted_count += 1
                    total_size_freed += file_size
                    logger.info(f"Deleted old backup: {backup_file}")
                except Exception as e:
                    logger.warning(f"Failed to delete backup {backup_file}: {e}")
        
        return {
            "deleted_count": deleted_count,
            "total_size_freed_mb": total_size_freed / 1024 / 1024,
            "retention_days": RETENTION_DAYS
        }
    
    # Pipeline
    full = full_backup()
    incremental = incremental_backup()
    
    verified_full = verify_backup(full)
    verified_incremental = verify_backup(incremental)
    
    upload_to_storage(verified_full["backup_file"])
    cleanup_old_backups()


dag = support_tickets_backup()


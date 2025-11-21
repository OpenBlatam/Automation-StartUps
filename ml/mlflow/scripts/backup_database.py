#!/usr/bin/env python3
"""
Script para hacer backup de la base de datos de MLflow (PostgreSQL).

Puede ejecutarse manualmente o via CronJob/Airflow.

Uso:
    python backup_database.py --output-dir ./backups
    python backup_database.py --upload-to-s3 s3://bucket/backups/
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None
    print("WARNING: boto3 no instalado. Funcionalidad de S3 deshabilitada.")


def backup_postgres(
    host: str,
    port: int,
    database: str,
    username: str,
    password: str,
    output_file: Path
) -> bool:
    """Crea backup de PostgreSQL usando pg_dump."""
    try:
        # Configurar variables de entorno para pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Ejecutar pg_dump
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', str(port),
            '-U', username,
            '-d', database,
            '-F', 'c',  # Formato custom (binario comprimido)
            '-f', str(output_file)
        ]
        
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"✅ Backup creado exitosamente: {output_file}")
        print(f"   Tamaño: {output_file.stat().st_size / (1024*1024):.2f} MB")
        return True
    
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Error ejecutando pg_dump: {e}")
        print(f"   stdout: {e.stdout}")
        print(f"   stderr: {e.stderr}")
        return False
    except Exception as e:
        print(f"ERROR: Error inesperado: {e}")
        return False


def upload_to_s3(
    file_path: Path,
    s3_bucket: str,
    s3_key: Optional[str] = None
) -> bool:
    """Sube archivo a S3."""
    if not boto3:
        print("ERROR: boto3 no está instalado. Instalar con: pip install boto3")
        return False
    
    try:
        s3_client = boto3.client('s3')
        
        if not s3_key:
            # Generar key basado en timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            s3_key = f"mlflow-backups/{timestamp}_{file_path.name}"
        
        print(f"📤 Subiendo a S3: s3://{s3_bucket}/{s3_key}")
        
        s3_client.upload_file(
            str(file_path),
            s3_bucket,
            s3_key,
            ExtraArgs={
                'ServerSideEncryption': 'AES256',
                'StorageClass': 'STANDARD_IA'  # Infrequent Access
            }
        )
        
        print(f"✅ Archivo subido exitosamente a S3")
        return True
    
    except ClientError as e:
        print(f"ERROR: Error de S3: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Error inesperado: {e}")
        return False


def cleanup_old_backups(
    backup_dir: Path,
    retention_days: int = 7
) -> None:
    """Elimina backups más antiguos que retention_days."""
    from datetime import timedelta
    
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    deleted_count = 0
    
    for backup_file in backup_dir.glob("*.dump"):
        file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
        
        if file_mtime < cutoff_date:
            try:
                backup_file.unlink()
                deleted_count += 1
                print(f"🗑️  Eliminado backup antiguo: {backup_file.name}")
            except Exception as e:
                print(f"WARNING: No se pudo eliminar {backup_file}: {e}")
    
    if deleted_count > 0:
        print(f"✅ Limpieza completada: {deleted_count} archivos eliminados")


def main():
    parser = argparse.ArgumentParser(
        description="Hace backup de la base de datos MLflow (PostgreSQL)"
    )
    parser.add_argument(
        "--host",
        default=os.getenv("PGHOST", "postgres.ml.svc.cluster.local"),
        help="Host de PostgreSQL"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("PGPORT", "5432")),
        help="Puerto de PostgreSQL"
    )
    parser.add_argument(
        "--database",
        default=os.getenv("PGDATABASE", "mlflow"),
        help="Nombre de la base de datos"
    )
    parser.add_argument(
        "--username",
        default=os.getenv("PGUSER", "mlflow"),
        help="Usuario de PostgreSQL"
    )
    parser.add_argument(
        "--password",
        default=os.getenv("PGPASSWORD", ""),
        help="Contraseña de PostgreSQL (o usar env PGPASSWORD)"
    )
    parser.add_argument(
        "--password-from-secret",
        help="Leer password desde Kubernetes secret (formato: namespace/secret-name/key)"
    )
    parser.add_argument(
        "--output-dir",
        default="./backups",
        help="Directorio de salida (default: ./backups)"
    )
    parser.add_argument(
        "--upload-to-s3",
        help="Subir backup a S3 (formato: s3://bucket/path/)"
    )
    parser.add_argument(
        "--retention-days",
        type=int,
        default=7,
        help="Días de retención para backups locales (default: 7)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Limpiar backups antiguos después de crear nuevo backup"
    )
    
    args = parser.parse_args()
    
    # Leer password desde Kubernetes secret si se especifica
    password = args.password
    if args.password_from_secret:
        try:
            import kubernetes
            from kubernetes import client, config
            
            # Cargar configuración de Kubernetes
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            v1 = client.CoreV1Api()
            
            namespace, secret_name_key = args.password_from_secret.split('/', 2)
            secret_name, key = secret_name_key.split('/', 1)
            
            secret = v1.read_namespaced_secret(secret_name, namespace)
            password = secret.data[key].decode('utf-8')
            
            print(f"✅ Password leído desde secret: {namespace}/{secret_name}/{key}")
        except ImportError:
            print("ERROR: kubernetes no está instalado. Instalar con: pip install kubernetes")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Error leyendo secret: {e}")
            sys.exit(1)
    
    if not password:
        print("ERROR: Se requiere password. Usar --password o --password-from-secret")
        sys.exit(1)
    
    print("="*60)
    print("💾 MLflow Database Backup Script")
    print("="*60)
    print(f"Host: {args.host}:{args.port}")
    print(f"Database: {args.database}")
    print(f"Output directory: {args.output_dir}")
    print("="*60)
    
    # Crear directorio de salida
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Nombre de archivo con timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = output_dir / f"mlflow_backup_{timestamp}.dump"
    
    # Crear backup
    if not backup_postgres(
        host=args.host,
        port=args.port,
        database=args.database,
        username=args.username,
        password=password,
        output_file=backup_file
    ):
        sys.exit(1)
    
    # Subir a S3 si se especifica
    if args.upload_to_s3:
        # Parsear S3 URI
        if args.upload_to_s3.startswith('s3://'):
            s3_path = args.upload_to_s3[5:]  # Remover s3://
            parts = s3_path.split('/', 1)
            s3_bucket = parts[0]
            s3_key = parts[1] if len(parts) > 1 else None
        else:
            s3_bucket = args.upload_to_s3
            s3_key = None
        
        if s3_key and not s3_key.endswith('/'):
            s3_key = f"{s3_key}/{backup_file.name}"
        elif not s3_key:
            s3_key = f"mlflow-backups/{backup_file.name}"
        
        if not upload_to_s3(backup_file, s3_bucket, s3_key):
            print("WARNING: Backup local creado pero falló subida a S3")
    
    # Limpiar backups antiguos
    if args.cleanup:
        cleanup_old_backups(output_dir, args.retention_days)
    
    print(f"\n✅ Backup completado: {backup_file.absolute()}")


if __name__ == "__main__":
    main()


"""
Integración con Almacenamiento en la Nube
==========================================

Soporte para S3, Google Cloud Storage, Azure Blob Storage
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, BinaryIO
from pathlib import Path
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BaseCloudStorage(ABC):
    """Clase base para almacenamiento en la nube"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Sube un archivo a la nube"""
        pass
    
    @abstractmethod
    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> bool:
        """Descarga un archivo de la nube"""
        pass
    
    @abstractmethod
    def generate_presigned_url(
        self,
        remote_path: str,
        expiration: timedelta = timedelta(hours=1)
    ) -> str:
        """Genera URL firmada temporal"""
        pass
    
    @abstractmethod
    def list_files(
        self,
        prefix: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Lista archivos en la nube"""
        pass
    
    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Elimina un archivo de la nube"""
        pass


class S3Storage(BaseCloudStorage):
    """Almacenamiento en AWS S3"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError:
            raise ImportError(
                "boto3 es requerido para S3. "
                "Instala con: pip install boto3"
            )
        
        self.bucket_name = config.get("bucket_name")
        self.region = config.get("region", "us-east-1")
        self.access_key = config.get("access_key_id")
        self.secret_key = config.get("secret_access_key")
        
        if not self.bucket_name:
            raise ValueError("bucket_name es requerido para S3")
        
        # Crear cliente S3
        self.s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key
        )
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Sube archivo a S3"""
        try:
            extra_args = {}
            if metadata:
                extra_args['Metadata'] = {
                    str(k): str(v) for k, v in metadata.items()
                }
            
            self.s3_client.upload_file(
                local_path,
                self.bucket_name,
                remote_path,
                ExtraArgs=extra_args
            )
            
            url = f"s3://{self.bucket_name}/{remote_path}"
            self.logger.info(f"Archivo subido a S3: {url}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error subiendo archivo a S3: {e}")
            raise
    
    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> bool:
        """Descarga archivo de S3"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.s3_client.download_file(
                self.bucket_name,
                remote_path,
                local_path
            )
            
            self.logger.info(f"Archivo descargado de S3: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error descargando archivo de S3: {e}")
            return False
    
    def generate_presigned_url(
        self,
        remote_path: str,
        expiration: timedelta = timedelta(hours=1)
    ) -> str:
        """Genera URL presignada de S3"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': remote_path
                },
                ExpiresIn=int(expiration.total_seconds())
            )
            return url
        except Exception as e:
            self.logger.error(f"Error generando URL presignada: {e}")
            raise
    
    def list_files(
        self,
        prefix: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Lista archivos en S3"""
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix or "",
                MaxKeys=max_results
            )
            
            files = []
            for obj in response.get('Contents', []):
                files.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'last_modified': obj['LastModified'].isoformat(),
                    'etag': obj['ETag']
                })
            
            return files
        except Exception as e:
            self.logger.error(f"Error listando archivos en S3: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """Elimina archivo de S3"""
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=remote_path
            )
            self.logger.info(f"Archivo eliminado de S3: {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando archivo de S3: {e}")
            return False


class GoogleCloudStorage(BaseCloudStorage):
    """Almacenamiento en Google Cloud Storage"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from google.cloud import storage
        except ImportError:
            raise ImportError(
                "google-cloud-storage es requerido. "
                "Instala con: pip install google-cloud-storage"
            )
        
        self.bucket_name = config.get("bucket_name")
        self.credentials_path = config.get("credentials_path")
        
        if not self.bucket_name:
            raise ValueError("bucket_name es requerido para GCS")
        
        # Crear cliente
        if self.credentials_path:
            self.storage_client = storage.Client.from_service_account_json(
                self.credentials_path
            )
        else:
            self.storage_client = storage.Client()
        
        self.bucket = self.storage_client.bucket(self.bucket_name)
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Sube archivo a GCS"""
        try:
            blob = self.bucket.blob(remote_path)
            
            if metadata:
                blob.metadata = {str(k): str(v) for k, v in metadata.items()}
            
            blob.upload_from_filename(local_path)
            
            url = f"gs://{self.bucket_name}/{remote_path}"
            self.logger.info(f"Archivo subido a GCS: {url}")
            return url
            
        except Exception as e:
            self.logger.error(f"Error subiendo archivo a GCS: {e}")
            raise
    
    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> bool:
        """Descarga archivo de GCS"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(local_path)
            
            self.logger.info(f"Archivo descargado de GCS: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error descargando archivo de GCS: {e}")
            return False
    
    def generate_presigned_url(
        self,
        remote_path: str,
        expiration: timedelta = timedelta(hours=1)
    ) -> str:
        """Genera URL firmada de GCS"""
        try:
            blob = self.bucket.blob(remote_path)
            url = blob.generate_signed_url(
                expiration=expiration,
                method='GET'
            )
            return url
        except Exception as e:
            self.logger.error(f"Error generando URL firmada: {e}")
            raise
    
    def list_files(
        self,
        prefix: Optional[str] = None,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Lista archivos en GCS"""
        try:
            blobs = self.bucket.list_blobs(
                prefix=prefix or "",
                max_results=max_results
            )
            
            files = []
            for blob in blobs:
                files.append({
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.updated.isoformat() if blob.updated else None,
                    'content_type': blob.content_type
                })
            
            return files
        except Exception as e:
            self.logger.error(f"Error listando archivos en GCS: {e}")
            return []
    
    def delete_file(self, remote_path: str) -> bool:
        """Elimina archivo de GCS"""
        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            self.logger.info(f"Archivo eliminado de GCS: {remote_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando archivo de GCS: {e}")
            return False


def create_cloud_storage(provider: str, config: Dict[str, Any]) -> BaseCloudStorage:
    """Factory para crear almacenamiento en la nube"""
    provider_lower = provider.lower()
    
    if provider_lower == "s3":
        return S3Storage(config)
    elif provider_lower in ["gcs", "google_cloud_storage"]:
        return GoogleCloudStorage(config)
    else:
        raise ValueError(f"Proveedor de almacenamiento no soportado: {provider}")


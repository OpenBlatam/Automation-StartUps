"""
Módulo de Almacenamiento Cloud para Contratos
Preparado para S3, GCS, Azure Blob Storage
"""

from __future__ import annotations

import os
import logging
import hashlib
from typing import Dict, Any, Optional, BinaryIO
from datetime import datetime

logger = logging.getLogger("airflow.task")


class CloudStorageAdapter:
    """Adaptador base para almacenamiento cloud"""
    
    def upload_contract(self, contract_id: str, version_number: int, document_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Sube un contrato al almacenamiento cloud.
        
        Args:
            contract_id: ID del contrato
            version_number: Número de versión
            document_content: Contenido del documento (bytes)
            metadata: Metadatos adicionales
            
        Returns:
            Dict con información de almacenamiento
        """
        raise NotImplementedError
    
    def download_contract(self, contract_id: str, version_number: int) -> bytes:
        """
        Descarga un contrato del almacenamiento cloud.
        
        Args:
            contract_id: ID del contrato
            version_number: Número de versión
            
        Returns:
            Contenido del documento (bytes)
        """
        raise NotImplementedError
    
    def delete_contract(self, contract_id: str, version_number: int) -> bool:
        """
        Elimina un contrato del almacenamiento cloud.
        
        Args:
            contract_id: ID del contrato
            version_number: Número de versión
            
        Returns:
            True si se eliminó exitosamente
        """
        raise NotImplementedError


class S3StorageAdapter(CloudStorageAdapter):
    """Adaptador para Amazon S3"""
    
    def __init__(self, bucket_name: str = None, region: str = None):
        self.bucket_name = bucket_name or os.getenv("S3_CONTRACTS_BUCKET", "")
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self._boto3_available = False
        
        try:
            import boto3
            self.s3_client = boto3.client('s3', region_name=self.region)
            self._boto3_available = True
        except ImportError:
            logger.warning("boto3 no disponible, S3 storage no funcionará")
    
    def upload_contract(self, contract_id: str, version_number: int, document_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sube contrato a S3"""
        if not self._boto3_available:
            raise ImportError("boto3 no disponible")
        
        key = f"contracts/{contract_id}/version_{version_number}.pdf"
        
        try:
            # Calcular hash
            document_hash = hashlib.sha256(document_content).hexdigest()
            
            # Metadata adicional
            s3_metadata = {
                "contract_id": contract_id,
                "version_number": str(version_number),
                "document_hash": document_hash,
                "upload_date": datetime.now().isoformat()
            }
            if metadata:
                s3_metadata.update(metadata)
            
            # Subir a S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=document_content,
                ContentType="application/pdf",
                Metadata=s3_metadata
            )
            
            url = f"s3://{self.bucket_name}/{key}"
            
            logger.info(
                f"Contrato subido a S3",
                extra={
                    "contract_id": contract_id,
                    "version_number": version_number,
                    "bucket": self.bucket_name,
                    "key": key
                }
            )
            
            return {
                "storage_provider": "s3",
                "storage_bucket": self.bucket_name,
                "storage_path": key,
                "storage_url": url,
                "document_hash": document_hash
            }
        except Exception as e:
            logger.error(f"Error subiendo contrato a S3: {e}")
            raise
    
    def download_contract(self, contract_id: str, version_number: int) -> bytes:
        """Descarga contrato de S3"""
        if not self._boto3_available:
            raise ImportError("boto3 no disponible")
        
        key = f"contracts/{contract_id}/version_{version_number}.pdf"
        
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return response['Body'].read()
        except Exception as e:
            logger.error(f"Error descargando contrato de S3: {e}")
            raise
    
    def delete_contract(self, contract_id: str, version_number: int) -> bool:
        """Elimina contrato de S3"""
        if not self._boto3_available:
            raise ImportError("boto3 no disponible")
        
        key = f"contracts/{contract_id}/version_{version_number}.pdf"
        
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
        except Exception as e:
            logger.error(f"Error eliminando contrato de S3: {e}")
            return False


class GCSStorageAdapter(CloudStorageAdapter):
    """Adaptador para Google Cloud Storage"""
    
    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or os.getenv("GCS_CONTRACTS_BUCKET", "")
        self._gcs_available = False
        
        try:
            from google.cloud import storage
            self.storage_client = storage.Client()
            self.bucket = self.storage_client.bucket(self.bucket_name)
            self._gcs_available = True
        except ImportError:
            logger.warning("google-cloud-storage no disponible, GCS storage no funcionará")
    
    def upload_contract(self, contract_id: str, version_number: int, document_content: bytes, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Sube contrato a GCS"""
        if not self._gcs_available:
            raise ImportError("google-cloud-storage no disponible")
        
        blob_name = f"contracts/{contract_id}/version_{version_number}.pdf"
        blob = self.bucket.blob(blob_name)
        
        try:
            document_hash = hashlib.sha256(document_content).hexdigest()
            
            # Metadata
            if metadata:
                blob.metadata = metadata
            blob.metadata = blob.metadata or {}
            blob.metadata.update({
                "contract_id": contract_id,
                "version_number": str(version_number),
                "document_hash": document_hash
            })
            
            blob.upload_from_string(document_content, content_type="application/pdf")
            
            url = f"gs://{self.bucket_name}/{blob_name}"
            
            logger.info(
                f"Contrato subido a GCS",
                extra={
                    "contract_id": contract_id,
                    "version_number": version_number,
                    "bucket": self.bucket_name,
                    "blob": blob_name
                }
            )
            
            return {
                "storage_provider": "gcs",
                "storage_bucket": self.bucket_name,
                "storage_path": blob_name,
                "storage_url": url,
                "document_hash": document_hash
            }
        except Exception as e:
            logger.error(f"Error subiendo contrato a GCS: {e}")
            raise
    
    def download_contract(self, contract_id: str, version_number: int) -> bytes:
        """Descarga contrato de GCS"""
        if not self._gcs_available:
            raise ImportError("google-cloud-storage no disponible")
        
        blob_name = f"contracts/{contract_id}/version_{version_number}.pdf"
        blob = self.bucket.blob(blob_name)
        
        try:
            return blob.download_as_bytes()
        except Exception as e:
            logger.error(f"Error descargando contrato de GCS: {e}")
            raise
    
    def delete_contract(self, contract_id: str, version_number: int) -> bool:
        """Elimina contrato de GCS"""
        if not self._gcs_available:
            raise ImportError("google-cloud-storage no disponible")
        
        blob_name = f"contracts/{contract_id}/version_{version_number}.pdf"
        blob = self.bucket.blob(blob_name)
        
        try:
            blob.delete()
            return True
        except Exception as e:
            logger.error(f"Error eliminando contrato de GCS: {e}")
            return False


def get_storage_adapter(storage_type: str = None) -> Optional[CloudStorageAdapter]:
    """
    Obtiene el adaptador de almacenamiento según configuración.
    
    Args:
        storage_type: Tipo de almacenamiento ('s3', 'gcs', 'local')
        
    Returns:
        Instancia del adaptador o None
    """
    storage_type = storage_type or os.getenv("CONTRACT_STORAGE_TYPE", "local").lower()
    
    if storage_type == "s3":
        return S3StorageAdapter()
    elif storage_type == "gcs":
        return GCSStorageAdapter()
    else:
        logger.info("Usando almacenamiento local (no cloud)")
        return None


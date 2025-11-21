"""
Integración con Google Drive y Dropbox
=======================================

Permite descargar documentos directamente desde Google Drive y Dropbox
para procesamiento automático.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseDriveIntegration(ABC):
    """Clase base para integraciones con servicios de almacenamiento"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def list_files(
        self,
        folder_id: Optional[str] = None,
        file_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Lista archivos en el servicio"""
        pass
    
    @abstractmethod
    def download_file(
        self,
        file_id: str,
        local_path: str
    ) -> bool:
        """Descarga un archivo"""
        pass
    
    @abstractmethod
    def upload_file(
        self,
        local_path: str,
        remote_folder_id: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """Sube un archivo"""
        pass
    
    @abstractmethod
    def watch_folder(
        self,
        folder_id: str,
        webhook_url: str
    ) -> Dict[str, Any]:
        """Configura webhook para cambios en carpeta"""
        pass


class GoogleDriveIntegration(BaseDriveIntegration):
    """Integración con Google Drive"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from google.oauth2.credentials import Credentials
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload
            from googleapiclient.errors import HttpError
        except ImportError:
            raise ImportError(
                "google-api-python-client y google-auth-oauthlib son requeridos. "
                "Instala con: pip install google-api-python-client google-auth-oauthlib"
            )
        
        self.credentials_path = config.get("credentials_path")
        self.token_path = config.get("token_path", "token.pickle")
        self.scopes = config.get("scopes", [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/drive.file'
        ])
        
        self.service = self._authenticate()
    
    def _authenticate(self):
        """Autentica con Google Drive"""
        creds = None
        
        # Cargar token existente
        if Path(self.token_path).exists():
            import pickle
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # Si no hay credenciales válidas, autenticar
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.credentials_path:
                    raise ValueError("credentials_path es requerido para Google Drive")
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.scopes
                )
                creds = flow.run_local_server(port=0)
            
            # Guardar credenciales
            with open(self.token_path, 'wb') as token:
                import pickle
                pickle.dump(creds, token)
        
        return build('drive', 'v3', credentials=creds)
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        file_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Lista archivos en Google Drive"""
        try:
            query = "trashed = false"
            
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            if file_types:
                mime_types = []
                for file_type in file_types:
                    if file_type == "pdf":
                        mime_types.append("application/pdf")
                    elif file_type in ["jpg", "jpeg", "png"]:
                        mime_types.append(f"image/{file_type}")
                
                if mime_types:
                    query += f" and ({' or '.join([f'mimeType=\'{mt}\'' for mt in mime_types])})"
            
            results = self.service.files().list(
                q=query,
                pageSize=100,
                fields="files(id, name, mimeType, size, modifiedTime, createdTime)"
            ).execute()
            
            files = []
            for file in results.get('files', []):
                files.append({
                    'id': file['id'],
                    'name': file['name'],
                    'mime_type': file.get('mimeType', ''),
                    'size': int(file.get('size', 0)),
                    'modified_time': file.get('modifiedTime', ''),
                    'created_time': file.get('createdTime', '')
                })
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listando archivos: {e}")
            return []
    
    def download_file(
        self,
        file_id: str,
        local_path: str
    ) -> bool:
        """Descarga un archivo de Google Drive"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            request = self.service.files().get_media(fileId=file_id)
            with open(local_path, 'wb') as f:
                from googleapiclient.http import MediaIoBaseDownload
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
            
            self.logger.info(f"Archivo descargado: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error descargando archivo: {e}")
            return False
    
    def upload_file(
        self,
        local_path: str,
        remote_folder_id: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """Sube un archivo a Google Drive"""
        try:
            file_metadata = {
                'name': filename or Path(local_path).name
            }
            
            if remote_folder_id:
                file_metadata['parents'] = [remote_folder_id]
            
            media = MediaFileUpload(
                local_path,
                resumable=True
            )
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            file_id = file.get('id')
            self.logger.info(f"Archivo subido: {file_id}")
            return file_id
            
        except Exception as e:
            self.logger.error(f"Error subiendo archivo: {e}")
            raise
    
    def watch_folder(
        self,
        folder_id: str,
        webhook_url: str
    ) -> Dict[str, Any]:
        """Configura webhook para cambios en carpeta"""
        try:
            channel = {
                'id': f"channel-{datetime.now().timestamp()}",
                'type': 'web_hook',
                'address': webhook_url
            }
            
            result = self.service.files().watch(
                fileId=folder_id,
                body=channel
            ).execute()
            
            return {
                'channel_id': result.get('id'),
                'resource_id': result.get('resourceId'),
                'expiration': result.get('expiration')
            }
        except Exception as e:
            self.logger.error(f"Error configurando watch: {e}")
            raise


class DropboxIntegration(BaseDriveIntegration):
    """Integración con Dropbox"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import dropbox
        except ImportError:
            raise ImportError(
                "dropbox es requerido. Instala con: pip install dropbox"
            )
        
        self.access_token = config.get("access_token")
        if not self.access_token:
            raise ValueError("access_token es requerido para Dropbox")
        
        self.dbx = dropbox.Dropbox(self.access_token)
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        file_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Lista archivos en Dropbox"""
        try:
            path = folder_id or ""
            
            result = self.dbx.files_list_folder(path)
            
            files = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    # Filtrar por tipo si se especifica
                    if file_types:
                        ext = Path(entry.name).suffix[1:].lower()
                        if ext not in file_types:
                            continue
                    
                    files.append({
                        'id': entry.id,
                        'name': entry.name,
                        'path': entry.path_lower,
                        'size': entry.size,
                        'modified_time': entry.server_modified.isoformat() if entry.server_modified else None,
                        'mime_type': getattr(entry, 'content_hash', '')
                    })
            
            return files
            
        except Exception as e:
            self.logger.error(f"Error listando archivos: {e}")
            return []
    
    def download_file(
        self,
        file_id: str,
        local_path: str
    ) -> bool:
        """Descarga un archivo de Dropbox"""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Dropbox usa paths, no IDs directamente
            # Si se pasa un ID, necesitarías buscar el path primero
            # Por simplicidad, asumimos que file_id es un path
            metadata, response = self.dbx.files_download(file_id)
            
            with open(local_path, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Archivo descargado: {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error descargando archivo: {e}")
            return False
    
    def upload_file(
        self,
        local_path: str,
        remote_folder_id: Optional[str] = None,
        filename: Optional[str] = None
    ) -> str:
        """Sube un archivo a Dropbox"""
        try:
            remote_path = f"{remote_folder_id or ''}/{filename or Path(local_path).name}"
            remote_path = remote_path.lstrip('/')
            
            with open(local_path, 'rb') as f:
                metadata = self.dbx.files_upload(
                    f.read(),
                    f"/{remote_path}",
                    mode=dropbox.files.WriteMode.overwrite
                )
            
            self.logger.info(f"Archivo subido: {metadata.id}")
            return metadata.id
            
        except Exception as e:
            self.logger.error(f"Error subiendo archivo: {e}")
            raise
    
    def watch_folder(
        self,
        folder_id: str,
        webhook_url: str
    ) -> Dict[str, Any]:
        """Configura webhook para cambios en carpeta (requiere Dropbox Business)"""
        # Dropbox requiere configuración adicional para webhooks
        # Retornar información de configuración
        return {
            'note': 'Dropbox webhooks requieren configuración en el panel de Dropbox',
            'webhook_url': webhook_url,
            'folder_path': folder_id
        }


def create_drive_integration(service: str, config: Dict[str, Any]) -> BaseDriveIntegration:
    """Factory para crear integraciones"""
    service_lower = service.lower()
    
    if service_lower in ["googledrive", "google_drive", "gdrive"]:
        return GoogleDriveIntegration(config)
    elif service_lower == "dropbox":
        return DropboxIntegration(config)
    else:
        raise ValueError(f"Servicio no soportado: {service}")


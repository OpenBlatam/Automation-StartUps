"""
Sistema de Backup y Restore
============================

Backup automático y restore de documentos y metadatos.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging
import json
import shutil
import tarfile
import gzip

logger = logging.getLogger(__name__)


class DocumentBackupManager:
    """Gestor de backups de documentos"""
    
    def __init__(
        self,
        backup_dir: str = "./backups",
        retention_days: int = 30
    ):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.retention_days = retention_days
        self.logger = logging.getLogger(__name__)
    
    def create_backup(
        self,
        documents: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
        include_files: bool = True
    ) -> str:
        """Crea backup completo"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 1. Guardar metadatos de documentos
        metadata_file = backup_path / "documents_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump({
                "documents": documents,
                "backup_metadata": metadata or {},
                "backup_date": datetime.now().isoformat(),
                "total_documents": len(documents)
            }, f, indent=2, ensure_ascii=False)
        
        # 2. Copiar archivos si se especifica
        if include_files:
            files_dir = backup_path / "files"
            files_dir.mkdir()
            
            for doc in documents:
                archive_path = doc.get("archive_path")
                if archive_path and Path(archive_path).exists():
                    file_name = Path(archive_path).name
                    shutil.copy2(archive_path, files_dir / file_name)
        
        # 3. Comprimir backup
        compressed_backup = self._compress_backup(backup_path)
        
        self.logger.info(f"Backup creado: {compressed_backup}")
        return str(compressed_backup)
    
    def restore_backup(
        self,
        backup_path: str,
        target_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """Restaura backup"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            raise FileNotFoundError(f"Backup no encontrado: {backup_path}")
        
        # Descomprimir
        extract_dir = self.backup_dir / "restore_temp"
        extract_dir.mkdir(exist_ok=True)
        
        try:
            if backup_file.suffix == '.gz':
                with tarfile.open(backup_path, 'r:gz') as tar:
                    tar.extractall(extract_dir)
            else:
                shutil.unpack_archive(backup_path, extract_dir)
            
            # Cargar metadatos
            metadata_file = extract_dir / "documents_metadata.json"
            if not metadata_file.exists():
                # Buscar en subdirectorios
                metadata_file = next(extract_dir.rglob("documents_metadata.json"), None)
            
            if not metadata_file:
                raise ValueError("No se encontró metadata en el backup")
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restaurar archivos
            restored_files = []
            files_dir = extract_dir / "files"
            if files_dir.exists():
                target = Path(target_dir) if target_dir else Path("./restored")
                target.mkdir(parents=True, exist_ok=True)
                
                for file_path in files_dir.iterdir():
                    if file_path.is_file():
                        shutil.copy2(file_path, target / file_path.name)
                        restored_files.append(str(target / file_path.name))
            
            return {
                "documents": backup_data.get("documents", []),
                "backup_date": backup_data.get("backup_date"),
                "restored_files": restored_files,
                "total_documents": backup_data.get("total_documents", 0)
            }
        
        finally:
            # Limpiar
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
    
    def _compress_backup(self, backup_path: Path) -> Path:
        """Comprime directorio de backup"""
        compressed_file = backup_path.with_suffix('.tar.gz')
        
        with tarfile.open(compressed_file, 'w:gz') as tar:
            tar.add(backup_path, arcname=backup_path.name)
        
        # Eliminar directorio original
        shutil.rmtree(backup_path)
        
        return compressed_file
    
    def cleanup_old_backups(self):
        """Elimina backups antiguos"""
        cutoff = datetime.now() - timedelta(days=self.retention_days)
        
        for backup_file in self.backup_dir.glob("backup_*.tar.gz"):
            # Extraer fecha del nombre
            try:
                date_str = backup_file.stem.replace('backup_', '').split('_')[0]
                backup_date = datetime.strptime(date_str, "%Y%m%d")
                
                if backup_date < cutoff:
                    backup_file.unlink()
                    self.logger.info(f"Backup antiguo eliminado: {backup_file.name}")
            except Exception as e:
                self.logger.warning(f"Error procesando backup {backup_file.name}: {e}")
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """Lista backups disponibles"""
        backups = []
        
        for backup_file in self.backup_dir.glob("backup_*.tar.gz"):
            try:
                stat = backup_file.stat()
                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
            except Exception as e:
                self.logger.warning(f"Error obteniendo info de backup {backup_file.name}: {e}")
        
        return sorted(backups, key=lambda x: x["created"], reverse=True)


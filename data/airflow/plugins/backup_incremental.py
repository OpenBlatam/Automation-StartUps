"""
Módulo de Backup Incremental Inteligente.

Proporciona:
- Detección automática de cambios
- Backups incrementales basados en cambios
- Optimización de espacio
- Sincronización inteligente
"""
import logging
import hashlib
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class ChangeRecord:
    """Registro de cambio."""
    path: str
    change_type: str  # 'added', 'modified', 'deleted'
    timestamp: datetime
    size: int
    checksum: Optional[str] = None


@dataclass
class IncrementalState:
    """Estado de backup incremental."""
    last_backup_time: datetime
    last_backup_id: str
    file_checksums: Dict[str, str]  # path -> checksum
    total_files: int
    total_size: int


class IntelligentIncrementalBackup:
    """Backup incremental inteligente."""
    
    def __init__(self, state_file: str = "/tmp/backup_incremental_state.json"):
        """
        Inicializa backup incremental.
        
        Args:
            state_file: Archivo para almacenar estado
        """
        self.state_file = Path(state_file)
        self.state: Optional[IncrementalState] = None
        self._load_state()
    
    def _load_state(self) -> None:
        """Carga estado de backup incremental."""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                
                self.state = IncrementalState(
                    last_backup_time=datetime.fromisoformat(data['last_backup_time']),
                    last_backup_id=data['last_backup_id'],
                    file_checksums=data['file_checksums'],
                    total_files=data['total_files'],
                    total_size=data['total_size']
                )
            except Exception as e:
                logger.warning(f"Failed to load incremental state: {e}")
                self.state = None
        else:
            self.state = None
    
    def _save_state(self, backup_id: str, checksums: Dict[str, str]) -> None:
        """Guarda estado de backup incremental."""
        try:
            total_size = sum(
                Path(p).stat().st_size
                for p in checksums.keys()
                if Path(p).exists()
            )
            
            self.state = IncrementalState(
                last_backup_time=datetime.now(),
                last_backup_id=backup_id,
                file_checksums=checksums,
                total_files=len(checksums),
                total_size=total_size
            )
            
            with open(self.state_file, 'w') as f:
                json.dump({
                    'last_backup_time': self.state.last_backup_time.isoformat(),
                    'last_backup_id': self.state.last_backup_id,
                    'file_checksums': self.state.file_checksums,
                    'total_files': self.state.total_files,
                    'total_size': self.state.total_size
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save incremental state: {e}")
    
    def detect_changes(
        self,
        source_paths: List[str],
        exclude_patterns: Optional[List[str]] = None
    ) -> List[ChangeRecord]:
        """
        Detecta cambios desde último backup.
        
        Args:
            source_paths: Rutas a monitorear
            exclude_patterns: Patrones a excluir
        
        Returns:
            Lista de cambios detectados
        """
        changes = []
        current_checksums = {}
        
        # Obtener checksums actuales
        for source_path in source_paths:
            source = Path(source_path)
            if not source.exists():
                continue
            
            if source.is_file():
                current_checksums[str(source)] = self._calculate_checksum(str(source))
            elif source.is_dir():
                for file_path in self._walk_directory(source, exclude_patterns):
                    current_checksums[str(file_path)] = self._calculate_checksum(str(file_path))
        
        # Comparar con estado anterior
        if self.state is None:
            # Primer backup - todos los archivos son nuevos
            for path, checksum in current_checksums.items():
                changes.append(ChangeRecord(
                    path=path,
                    change_type='added',
                    timestamp=datetime.now(),
                    size=Path(path).stat().st_size if Path(path).exists() else 0,
                    checksum=checksum
                ))
        else:
            old_checksums = self.state.file_checksums
            
            # Archivos nuevos o modificados
            for path, checksum in current_checksums.items():
                if path not in old_checksums:
                    changes.append(ChangeRecord(
                        path=path,
                        change_type='added',
                        timestamp=datetime.now(),
                        size=Path(path).stat().st_size if Path(path).exists() else 0,
                        checksum=checksum
                    ))
                elif old_checksums[path] != checksum:
                    changes.append(ChangeRecord(
                        path=path,
                        change_type='modified',
                        timestamp=datetime.now(),
                        size=Path(path).stat().st_size if Path(path).exists() else 0,
                        checksum=checksum
                    ))
            
            # Archivos eliminados
            for path in old_checksums:
                if path not in current_checksums:
                    changes.append(ChangeRecord(
                        path=path,
                        change_type='deleted',
                        timestamp=datetime.now(),
                        size=0,
                        checksum=None
                    ))
        
        return changes
    
    def _walk_directory(
        self,
        directory: Path,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """Recorre directorio excluyendo patrones."""
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            # Filtrar directorios
            if exclude_patterns:
                import fnmatch
                dirs[:] = [d for d in dirs if not any(
                    fnmatch.fnmatch(d, pattern) for pattern in exclude_patterns
                )]
            
            for filename in filenames:
                file_path = Path(root) / filename
                
                # Filtrar archivos
                if exclude_patterns:
                    if any(fnmatch.fnmatch(str(file_path), pattern) for pattern in exclude_patterns):
                        continue
                
                files.append(file_path)
        
        return files
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calcula checksum SHA256 de archivo."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    def get_incremental_backup_size(self, changes: List[ChangeRecord]) -> int:
        """Calcula tamaño estimado del backup incremental."""
        return sum(change.size for change in changes if change.change_type != 'deleted')
    
    def should_do_full_backup(
        self,
        changes: List[ChangeRecord],
        threshold_percent: float = 50.0
    ) -> bool:
        """
        Decide si hacer backup completo o incremental.
        
        Args:
            changes: Cambios detectados
            threshold_percent: Porcentaje de cambios para hacer full backup
        
        Returns:
            True si se debe hacer backup completo
        """
        if self.state is None:
            return True  # Primer backup siempre es completo
        
        if not self.state.file_checksums:
            return True
        
        total_files = len(self.state.file_checksums)
        changed_files = len([c for c in changes if c.change_type != 'deleted'])
        
        if total_files == 0:
            return True
        
        change_percent = (changed_files / total_files) * 100
        
        return change_percent >= threshold_percent
    
    def get_backup_summary(self) -> Dict[str, Any]:
        """Obtiene resumen del estado de backup incremental."""
        if self.state is None:
            return {
                'has_previous_backup': False,
                'message': 'No previous backup found'
            }
        
        return {
            'has_previous_backup': True,
            'last_backup_time': self.state.last_backup_time.isoformat(),
            'last_backup_id': self.state.last_backup_id,
            'total_files': self.state.total_files,
            'total_size_gb': self.state.total_size / (1024 ** 3),
            'days_since_last_backup': (datetime.now() - self.state.last_backup_time).days
        }


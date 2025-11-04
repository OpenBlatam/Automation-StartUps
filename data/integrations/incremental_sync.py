"""
Sincronización incremental inteligente
======================================

Detecta y sincroniza solo cambios desde la última ejecución.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

from .sync_framework import SyncFramework, SyncConfig, SyncDirection
from .connectors import SyncRecord

logger = logging.getLogger(__name__)


@dataclass
class IncrementalSyncState:
    """Estado de sincronización incremental"""
    last_sync_timestamp: Optional[datetime] = None
    last_sync_id: Optional[str] = None
    last_processed_ids: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.last_processed_ids is None:
            self.last_processed_ids = []
        if self.metadata is None:
            self.metadata = {}


class IncrementalSyncManager:
    """Gestiona sincronizaciones incrementales"""
    
    def __init__(self, framework: SyncFramework, db_connection_string: str):
        self.framework = framework
        self.db_connection_string = db_connection_string
        self._init_state_table()
    
    def _init_state_table(self):
        """Inicializa tabla de estado"""
        try:
            import psycopg2
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            
            cur.execute("""
                CREATE TABLE IF NOT EXISTS incremental_sync_state (
                    id SERIAL PRIMARY KEY,
                    sync_key VARCHAR(256) UNIQUE NOT NULL,
                    source_type VARCHAR(64) NOT NULL,
                    target_type VARCHAR(64) NOT NULL,
                    last_sync_timestamp TIMESTAMPTZ,
                    last_sync_id VARCHAR(128),
                    last_processed_ids JSONB,
                    metadata JSONB,
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error inicializando tabla de estado: {e}")
    
    def get_state(self, sync_key: str) -> IncrementalSyncState:
        """Obtiene estado de sincronización"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            cur.execute("""
                SELECT * FROM incremental_sync_state
                WHERE sync_key = %s
            """, (sync_key,))
            
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                return IncrementalSyncState(
                    last_sync_timestamp=row.get('last_sync_timestamp'),
                    last_sync_id=row.get('last_sync_id'),
                    last_processed_ids=row.get('last_processed_ids', []),
                    metadata=row.get('metadata', {})
                )
            
            return IncrementalSyncState()
        
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return IncrementalSyncState()
    
    def save_state(
        self,
        sync_key: str,
        source_type: str,
        target_type: str,
        state: IncrementalSyncState
    ):
        """Guarda estado de sincronización"""
        try:
            import psycopg2
            from psycopg2.extras import Json
            
            conn = psycopg2.connect(self.db_connection_string)
            cur = conn.cursor()
            
            cur.execute("""
                INSERT INTO incremental_sync_state (
                    sync_key, source_type, target_type,
                    last_sync_timestamp, last_sync_id,
                    last_processed_ids, metadata, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (sync_key) DO UPDATE SET
                    last_sync_timestamp = EXCLUDED.last_sync_timestamp,
                    last_sync_id = EXCLUDED.last_sync_id,
                    last_processed_ids = EXCLUDED.last_processed_ids,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """, (
                sync_key,
                source_type,
                target_type,
                state.last_sync_timestamp,
                state.last_sync_id,
                Json(state.last_processed_ids),
                Json(state.metadata)
            ))
            
            conn.commit()
            cur.close()
            conn.close()
        
        except Exception as e:
            logger.error(f"Error guardando estado: {e}")
    
    def sync_incremental(
        self,
        config: SyncConfig,
        sync_key: str,
        lookback_hours: int = 24
    ):
        """
        Ejecuta sincronización incremental.
        
        Args:
            config: Configuración de sincronización
            sync_key: Clave única para este tipo de sync
            lookback_hours: Horas hacia atrás si no hay última sync
        """
        # Obtener estado anterior
        state = self.get_state(sync_key)
        
        # Configurar filtros incrementales
        if state.last_sync_timestamp:
            # Sincronizar desde última vez
            filters = config.filters or {}
            filters["updatedSince"] = state.last_sync_timestamp.isoformat()
            config.filters = filters
        else:
            # Primera vez: usar lookback
            lookback_time = datetime.now() - timedelta(hours=lookback_hours)
            filters = config.filters or {}
            filters["updatedSince"] = lookback_time.isoformat()
            config.filters = filters
        
        # Ejecutar sincronización
        result = self.framework.sync(config, dry_run=False)
        
        # Actualizar estado
        state.last_sync_timestamp = datetime.now()
        state.last_sync_id = result.sync_id
        state.last_processed_ids = [r.source_id for r in result.records]
        state.metadata = {
            "total_records": result.total_records,
            "successful": result.successful,
            "failed": result.failed
        }
        
        self.save_state(
            sync_key,
            config.source_connector_type,
            config.target_connector_type,
            state
        )
        
        return result
    
    def get_sync_key(
        self,
        source_type: str,
        target_type: str,
        direction: str = "source_to_target"
    ) -> str:
        """Genera clave única para sincronización"""
        return f"{source_type}_{target_type}_{direction}"



"""
Sistema de Versionado de Datos para Nómina
Versionado y tracking de cambios en datos críticos
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import json

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class DataVersion:
    """Versión de datos"""
    version: int
    entity_type: str
    entity_id: int
    previous_version: Optional[int]
    changed_fields: Dict[str, Any]
    changed_by: str
    change_reason: Optional[str]
    created_at: datetime
    metadata: Optional[Dict[str, Any]] = None


class PayrollVersioning:
    """Sistema de versionado para datos de nómina"""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
        self._ensure_version_table()
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL"""
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def _ensure_version_table(self) -> None:
        """Crea tabla de versionado si no existe"""
        sql = """
            CREATE TABLE IF NOT EXISTS payroll_data_versions (
                id SERIAL PRIMARY KEY,
                version INT NOT NULL,
                entity_type VARCHAR(64) NOT NULL,
                entity_id INT NOT NULL,
                previous_version INT,
                changed_fields JSONB NOT NULL,
                changed_by VARCHAR(256) NOT NULL,
                change_reason TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                metadata JSONB
            );
            
            CREATE INDEX IF NOT EXISTS idx_version_entity 
                ON payroll_data_versions(entity_type, entity_id);
            CREATE INDEX IF NOT EXISTS idx_version_version 
                ON payroll_data_versions(version);
            CREATE INDEX IF NOT EXISTS idx_version_created 
                ON payroll_data_versions(created_at);
        """
        
        try:
            self.hook.run(sql)
        except Exception as e:
            logger.warning(f"Error creating version table: {e}")
    
    def create_version(
        self,
        entity_type: str,
        entity_id: int,
        changed_fields: Dict[str, Any],
        changed_by: str,
        change_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Crea una nueva versión"""
        # Obtener versión anterior
        previous_sql = """
            SELECT MAX(version)
            FROM payroll_data_versions
            WHERE entity_type = %s AND entity_id = %s
        """
        
        previous_result = self.hook.get_first(
            previous_sql,
            parameters=(entity_type, entity_id)
        )
        
        previous_version = previous_result[0] if previous_result and previous_result[0] else None
        new_version = (previous_version + 1) if previous_version else 1
        
        # Insertar nueva versión
        insert_sql = """
            INSERT INTO payroll_data_versions (
                version, entity_type, entity_id, previous_version,
                changed_fields, changed_by, change_reason, metadata
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        result = self.hook.get_first(
            insert_sql,
            parameters=(
                new_version,
                entity_type,
                entity_id,
                previous_version,
                json.dumps(changed_fields),
                changed_by,
                change_reason,
                json.dumps(metadata) if metadata else None
            )
        )
        
        return result[0] if result else 0
    
    def get_version_history(
        self,
        entity_type: str,
        entity_id: int,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtiene historial de versiones"""
        sql = """
            SELECT 
                version, previous_version, changed_fields,
                changed_by, change_reason, created_at, metadata
            FROM payroll_data_versions
            WHERE entity_type = %s AND entity_id = %s
            ORDER BY version DESC
            LIMIT %s
        """
        
        results = self.hook.get_records(
            sql,
            parameters=(entity_type, entity_id, limit)
        )
        
        versions = []
        for row in results:
            versions.append({
                "version": row[0],
                "previous_version": row[1],
                "changed_fields": row[2] if isinstance(row[2], dict) else json.loads(row[2]) if row[2] else {},
                "changed_by": row[3],
                "change_reason": row[4],
                "created_at": row[5],
                "metadata": row[6] if isinstance(row[6], dict) else json.loads(row[6]) if row[6] else {}
            })
        
        return versions
    
    def get_latest_version(
        self,
        entity_type: str,
        entity_id: int
    ) -> Optional[Dict[str, Any]]:
        """Obtiene la última versión"""
        history = self.get_version_history(entity_type, entity_id, limit=1)
        return history[0] if history else None
    
    def rollback_to_version(
        self,
        entity_type: str,
        entity_id: int,
        target_version: int,
        rolled_back_by: str
    ) -> bool:
        """Rollback a una versión específica"""
        # Obtener cambios necesarios
        history = self.get_version_history(entity_type, entity_id, limit=100)
        
        if not history:
            return False
        
        # Encontrar versión objetivo
        target_version_data = next((v for v in history if v["version"] == target_version), None)
        if not target_version_data:
            return False
        
        # Crear versión de rollback
        rollback_fields = {k: v for k, v in target_version_data["changed_fields"].items()}
        
        self.create_version(
            entity_type=entity_type,
            entity_id=entity_id,
            changed_fields=rollback_fields,
            changed_by=rolled_back_by,
            change_reason=f"Rollback to version {target_version}"
        )
        
        return True


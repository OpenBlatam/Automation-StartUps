"""
Sistema de Migraciones para Nómina
Manejo de migraciones de esquema y datos
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import hashlib

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """Migración de base de datos"""
    version: str
    name: str
    description: str
    up_sql: str
    down_sql: Optional[str] = None
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if self.checksum is None:
            self.checksum = self._calculate_checksum()
    
    def _calculate_checksum(self) -> str:
        """Calcula checksum de la migración"""
        content = f"{self.version}{self.name}{self.up_sql}{self.down_sql or ''}"
        return hashlib.md5(content.encode()).hexdigest()


class PayrollMigrations:
    """Sistema de migraciones para nómina"""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Args:
            postgres_conn_id: ID de conexión de PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self._hook: Optional[PostgresHook] = None
        self._ensure_migrations_table()
    
    @property
    def hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL"""
        if self._hook is None:
            self._hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._hook
    
    def _ensure_migrations_table(self) -> None:
        """Crea tabla de migraciones si no existe"""
        sql = """
            CREATE TABLE IF NOT EXISTS payroll_migrations (
                id SERIAL PRIMARY KEY,
                version VARCHAR(64) UNIQUE NOT NULL,
                name VARCHAR(256) NOT NULL,
                description TEXT,
                checksum VARCHAR(64) NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                applied_by VARCHAR(256),
                execution_time_ms INT,
                success BOOLEAN NOT NULL DEFAULT true,
                error_message TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_migrations_version 
                ON payroll_migrations(version);
            CREATE INDEX IF NOT EXISTS idx_migrations_applied 
                ON payroll_migrations(applied_at);
        """
        
        try:
            self.hook.run(sql)
        except Exception as e:
            logger.warning(f"Error creating migrations table: {e}")
    
    def apply_migration(
        self,
        migration: Migration,
        applied_by: str = "system"
    ) -> bool:
        """Aplica una migración"""
        import time
        
        # Verificar si ya está aplicada
        check_sql = """
            SELECT version, checksum
            FROM payroll_migrations
            WHERE version = %s
        """
        
        existing = self.hook.get_first(check_sql, parameters=(migration.version,))
        
        if existing:
            existing_checksum = existing[1]
            if existing_checksum == migration.checksum:
                logger.info(f"Migration {migration.version} already applied")
                return True
            else:
                logger.error(
                    f"Migration {migration.version} checksum mismatch. "
                    f"Expected {migration.checksum}, got {existing_checksum}"
                )
                return False
        
        # Aplicar migración
        start_time = time.time()
        success = True
        error_message = None
        
        try:
            self.hook.run(migration.up_sql)
            logger.info(f"Migration {migration.version} applied successfully")
        except Exception as e:
            success = False
            error_message = str(e)
            logger.error(f"Error applying migration {migration.version}: {e}")
            raise
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # Registrar migración
        insert_sql = """
            INSERT INTO payroll_migrations (
                version, name, description, checksum,
                applied_by, execution_time_ms, success, error_message
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            self.hook.run(
                insert_sql,
                parameters=(
                    migration.version,
                    migration.name,
                    migration.description,
                    migration.checksum,
                    applied_by,
                    execution_time,
                    success,
                    error_message
                )
            )
        except Exception as e:
            logger.error(f"Error recording migration {migration.version}: {e}")
        
        return success
    
    def rollback_migration(
        self,
        migration: Migration,
        rolled_back_by: str = "system"
    ) -> bool:
        """Rollback de una migración"""
        if not migration.down_sql:
            logger.warning(f"Migration {migration.version} has no rollback SQL")
            return False
        
        try:
            self.hook.run(migration.down_sql)
            
            # Marcar como rollback
            update_sql = """
                UPDATE payroll_migrations
                SET success = false,
                    error_message = 'Rolled back'
                WHERE version = %s
            """
            self.hook.run(update_sql, parameters=(migration.version,))
            
            logger.info(f"Migration {migration.version} rolled back successfully")
            return True
        except Exception as e:
            logger.error(f"Error rolling back migration {migration.version}: {e}")
            return False
    
    def get_applied_migrations(self) -> List[Dict[str, Any]]:
        """Obtiene migraciones aplicadas"""
        sql = """
            SELECT 
                version, name, description, checksum,
                applied_at, applied_by, execution_time_ms, success
            FROM payroll_migrations
            ORDER BY applied_at DESC
        """
        
        results = self.hook.get_records(sql)
        
        migrations = []
        for row in results:
            migrations.append({
                "version": row[0],
                "name": row[1],
                "description": row[2],
                "checksum": row[3],
                "applied_at": row[4],
                "applied_by": row[5],
                "execution_time_ms": row[6],
                "success": row[7]
            })
        
        return migrations
    
    def get_pending_migrations(
        self,
        available_migrations: List[Migration]
    ) -> List[Migration]:
        """Obtiene migraciones pendientes"""
        applied = self.get_applied_migrations()
        applied_versions = {m["version"] for m in applied}
        
        pending = [
            m for m in available_migrations
            if m.version not in applied_versions
        ]
        
        return sorted(pending, key=lambda x: x.version)


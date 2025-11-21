"""
Sistema de Migraciones para Base de Datos
Gestiona migraciones de esquema de forma versionada
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

logger = logging.getLogger(__name__)


class DatabaseMigrator:
    """Gestiona migraciones de base de datos"""
    
    def __init__(self, db_url: str, migrations_dir: str = None):
        self.db_url = db_url
        if migrations_dir is None:
            migrations_dir = Path(__file__).parent.parent.parent / "data" / "db" / "migrations"
        self.migrations_dir = Path(migrations_dir)
        self.migrations_dir.mkdir(exist_ok=True, parents=True)
        self._ensure_migrations_table()
    
    def _ensure_migrations_table(self):
        """Crea tabla de migraciones si no existe"""
        try:
            conn = psycopg2.connect(self.db_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id SERIAL PRIMARY KEY,
                    migration_name VARCHAR(255) UNIQUE NOT NULL,
                    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    checksum VARCHAR(64),
                    execution_time_ms INTEGER
                )
            """)
            
            conn.close()
        except Exception as e:
            logger.error(f"Error creando tabla de migraciones: {e}")
    
    def create_migration(self, name: str, sql_content: str) -> str:
        """Crea un nuevo archivo de migración"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        migration_name = f"{timestamp}_{name}.sql"
        migration_path = self.migrations_dir / migration_name
        
        with open(migration_path, 'w') as f:
            f.write(f"-- Migration: {name}\n")
            f.write(f"-- Created: {datetime.now().isoformat()}\n\n")
            f.write(sql_content)
        
        logger.info(f"Migración creada: {migration_path}")
        return migration_name
    
    def list_migrations(self) -> List[Dict]:
        """Lista todas las migraciones disponibles"""
        migrations = []
        for file in sorted(self.migrations_dir.glob("*.sql")):
            migrations.append({
                "name": file.name,
                "path": str(file),
                "size": file.stat().st_size,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
        return migrations
    
    def get_applied_migrations(self) -> List[str]:
        """Obtiene lista de migraciones aplicadas"""
        try:
            conn = psycopg2.connect(self.db_url)
            cursor = conn.cursor()
            cursor.execute("SELECT migration_name FROM schema_migrations ORDER BY applied_at")
            applied = [row[0] for row in cursor.fetchall()]
            cursor.close()
            conn.close()
            return applied
        except Exception as e:
            logger.error(f"Error obteniendo migraciones aplicadas: {e}")
            return []
    
    def get_pending_migrations(self) -> List[str]:
        """Obtiene migraciones pendientes"""
        all_migrations = [m["name"] for m in self.list_migrations()]
        applied_migrations = self.get_applied_migrations()
        return [m for m in all_migrations if m not in applied_migrations]
    
    def apply_migration(self, migration_name: str, dry_run: bool = False) -> Dict:
        """Aplica una migración específica"""
        migration_path = self.migrations_dir / migration_name
        
        if not migration_path.exists():
            return {"success": False, "error": f"Migración no encontrada: {migration_name}"}
        
        if migration_name in self.get_applied_migrations():
            return {"success": False, "error": f"Migración ya aplicada: {migration_name}"}
        
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "migration": migration_name,
                "message": "Dry run - migración no aplicada"
            }
        
        try:
            start_time = datetime.now()
            
            # Leer SQL
            with open(migration_path, 'r') as f:
                sql_content = f.read()
            
            # Aplicar migración
            conn = psycopg2.connect(self.db_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute(sql_content)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Registrar migración
            import hashlib
            checksum = hashlib.md5(sql_content.encode()).hexdigest()
            
            cursor.execute("""
                INSERT INTO schema_migrations (migration_name, checksum, execution_time_ms)
                VALUES (%s, %s, %s)
            """, (migration_name, checksum, int(execution_time)))
            
            cursor.close()
            conn.close()
            
            logger.info(f"Migración aplicada: {migration_name} ({execution_time:.2f}ms)")
            
            return {
                "success": True,
                "migration": migration_name,
                "execution_time_ms": execution_time
            }
            
        except Exception as e:
            logger.error(f"Error aplicando migración {migration_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def apply_all_pending(self, dry_run: bool = False) -> List[Dict]:
        """Aplica todas las migraciones pendientes"""
        pending = self.get_pending_migrations()
        results = []
        
        for migration in pending:
            result = self.apply_migration(migration, dry_run=dry_run)
            results.append(result)
            
            if not result.get("success") and not dry_run:
                logger.error(f"Migración falló, deteniendo: {migration}")
                break
        
        return results
    
    def rollback_migration(self, migration_name: str) -> Dict:
        """Revierte una migración (requiere migración de rollback)"""
        # Buscar migración de rollback
        rollback_name = migration_name.replace(".sql", "_rollback.sql")
        rollback_path = self.migrations_dir / rollback_name
        
        if not rollback_path.exists():
            return {
                "success": False,
                "error": f"Migración de rollback no encontrada: {rollback_name}"
            }
        
        try:
            with open(rollback_path, 'r') as f:
                rollback_sql = f.read()
            
            conn = psycopg2.connect(self.db_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute(rollback_sql)
            
            # Eliminar registro de migración
            cursor.execute(
                "DELETE FROM schema_migrations WHERE migration_name = %s",
                (migration_name,)
            )
            
            cursor.close()
            conn.close()
            
            logger.info(f"Migración revertida: {migration_name}")
            return {"success": True, "migration": migration_name}
            
        except Exception as e:
            logger.error(f"Error revirtiendo migración: {e}")
            return {"success": False, "error": str(e)}




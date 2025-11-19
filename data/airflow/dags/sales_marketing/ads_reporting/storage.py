"""
Almacenadores modulares de datos.

Separa la lógica de almacenamiento de la lógica de extracción.
Soporta múltiples backends: PostgreSQL, S3, etc.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


class BaseStorage(ABC):
    """Almacenador base abstracto."""
    
    @abstractmethod
    def save_campaign_performance(
        self,
        data: List[Dict[str, Any]],
        table_name: str
    ) -> Dict[str, Any]:
        """
        Guarda datos de rendimiento de campañas.
        
        Args:
            data: Lista de datos de campañas
            table_name: Nombre de la tabla
            
        Returns:
            Diccionario con estadísticas de guardado
        """
        pass
    
    @abstractmethod
    def ensure_table_exists(self, table_name: str, schema: Dict[str, str]) -> None:
        """
        Asegura que una tabla exista con el schema dado.
        
        Args:
            table_name: Nombre de la tabla
            schema: Diccionario con columnas y tipos
        """
        pass


class PostgreSQLStorage(BaseStorage):
    """Almacenador en PostgreSQL."""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Inicializa el almacenador PostgreSQL.
        
        Args:
            postgres_conn_id: Connection ID de PostgreSQL
        """
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgresHook no disponible")
        self.postgres_conn_id = postgres_conn_id
        self.hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    def ensure_table_exists(self, table_name: str, schema: Dict[str, str]) -> None:
        """Crea la tabla si no existe."""
        columns = ", ".join([
            f"{col} {col_type}"
            for col, col_type in schema.items()
        ])
        
        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {columns},
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        # Crear índices comunes
        index_sqls = []
        if "date_start" in schema:
            index_sqls.append(
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_date "
                f"ON {table_name}(date_start, date_stop);"
            )
        if "campaign_id" in schema:
            index_sqls.append(
                f"CREATE INDEX IF NOT EXISTS idx_{table_name}_campaign "
                f"ON {table_name}(campaign_id);"
            )
        
        self.hook.run(create_sql)
        for index_sql in index_sqls:
            try:
                self.hook.run(index_sql)
            except Exception as e:
                logger.warning(f"Error creando índice: {str(e)}")
    
    def save_campaign_performance(
        self,
        data: List[Dict[str, Any]],
        table_name: str
    ) -> Dict[str, Any]:
        """Guarda datos de rendimiento de campañas."""
        if not data:
            return {"saved": 0, "errors": 0}
        
        # Definir schema basado en los datos
        schema = {
            "date_start": "DATE",
            "date_stop": "DATE",
            "campaign_id": "VARCHAR(255)",
            "campaign_name": "TEXT",
            "adset_id": "VARCHAR(255)",
            "adset_name": "TEXT",
            "ad_id": "VARCHAR(255)",
            "ad_name": "TEXT",
            "impressions": "INTEGER",
            "clicks": "INTEGER",
            "ctr": "DECIMAL(10, 4)",
            "cpc": "DECIMAL(10, 4)",
            "conversions": "DECIMAL(10, 2)",
            "roas": "DECIMAL(10, 4)",
            "spend": "DECIMAL(10, 2)",
            "platform": "VARCHAR(50)",
        }
        
        # Asegurar que la tabla existe
        self.ensure_table_exists(table_name, schema)
        
        # Preparar datos para inserción
        saved = 0
        errors = 0
        
        # Construir INSERT
        columns = list(schema.keys())
        placeholders = ", ".join(["%s"] * len(columns))
        insert_sql = f"""
        INSERT INTO {table_name} ({", ".join(columns)})
        VALUES ({placeholders})
        """
        
        for record in data:
            try:
                values = [record.get(col) for col in columns]
                self.hook.run(insert_sql, parameters=values)
                saved += 1
            except Exception as e:
                logger.warning(f"Error guardando registro: {str(e)}")
                errors += 1
        
        return {
            "saved": saved,
            "errors": errors,
            "total": len(data)
        }
    
    def save_audience_performance(
        self,
        data: Dict[str, Any],
        table_name: str
    ) -> Dict[str, Any]:
        """Guarda datos de rendimiento por audiencia."""
        schema = {
            "date_start": "DATE",
            "date_stop": "DATE",
            "audience_type": "VARCHAR(100)",
            "spend": "DECIMAL(10, 2)",
            "conversions": "DECIMAL(10, 2)",
            "revenue": "DECIMAL(10, 2)",
            "cpa": "DECIMAL(10, 2)",
            "cpa_vs_avg_percent": "DECIMAL(10, 2)",
        }
        
        self.ensure_table_exists(table_name, schema)
        
        audiences = data.get("audiences", [])
        saved = 0
        errors = 0
        
        for audience in audiences:
            try:
                insert_sql = f"""
                INSERT INTO {table_name}
                (date_start, date_stop, audience_type, spend, conversions, revenue, cpa, cpa_vs_avg_percent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                self.hook.run(insert_sql, parameters=(
                    data["date_start"],
                    data["date_stop"],
                    audience["audience_type"],
                    audience["spend"],
                    audience["conversions"],
                    audience["revenue"],
                    audience["cpa"],
                    audience.get("cpa_vs_avg", 0)
                ))
                saved += 1
            except Exception as e:
                logger.warning(f"Error guardando audiencia: {str(e)}")
                errors += 1
        
        return {"saved": saved, "errors": errors, "total": len(audiences)}


class S3Storage(BaseStorage):
    """Almacenador en S3 (placeholder para implementación futura)."""
    
    def ensure_table_exists(self, table_name: str, schema: Dict[str, str]) -> None:
        """No-op para S3."""
        pass
    
    def save_campaign_performance(
        self,
        data: List[Dict[str, Any]],
        table_name: str
    ) -> Dict[str, Any]:
        """Guarda datos en S3 (placeholder)."""
        logger.info(f"Guardando {len(data)} registros en S3: {table_name}")
        # Implementar según necesidades
        return {"saved": len(data), "errors": 0}


def get_storage(storage_type: str, **kwargs) -> BaseStorage:
    """
    Factory function para obtener un almacenador.
    
    Args:
        storage_type: Tipo de almacenamiento ("postgres", "s3")
        **kwargs: Parámetros específicos del almacenador
        
    Returns:
        Instancia del almacenador
    """
    if storage_type == "postgres":
        return PostgreSQLStorage(**kwargs)
    elif storage_type == "s3":
        return S3Storage(**kwargs)
    else:
        raise ValueError(f"Tipo de almacenamiento no soportado: {storage_type}")


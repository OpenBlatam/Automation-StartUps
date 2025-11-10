"""
Integración con Bases de Datos para Precios

Gestiona conexiones y operaciones con bases de datos
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    logger.warning("PostgresHook no disponible")

try:
    from airflow.providers.mysql.hooks.mysql import MySqlHook
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("MySqlHook no disponible")


class PriceDatabase:
    """Gestiona operaciones de base de datos para precios"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.db_type = config.get('database_type', 'postgres')
        self.conn_id = config.get('database_conn_id', 'postgres_default')
        self.table_name = config.get('prices_table', 'product_prices')
        self.history_table = config.get('price_history_table', 'price_history')
    
    def get_current_prices(
        self,
        product_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Obtiene precios actuales desde base de datos
        
        Args:
            product_ids: Lista de IDs de productos (None = todos)
        
        Returns:
            Lista de precios actuales
        """
        try:
            if self.db_type == 'postgres' and POSTGRES_AVAILABLE:
                hook = PostgresHook(postgres_conn_id=self.conn_id)
                
                if product_ids:
                    placeholders = ','.join(['%s'] * len(product_ids))
                    query = f"""
                        SELECT product_id, product_name, price, currency, updated_at
                        FROM {self.table_name}
                        WHERE product_id IN ({placeholders})
                    """
                    results = hook.get_records(query, parameters=product_ids)
                else:
                    query = f"""
                        SELECT product_id, product_name, price, currency, updated_at
                        FROM {self.table_name}
                        ORDER BY product_id
                    """
                    results = hook.get_records(query)
                
                return [
                    {
                        'product_id': row[0],
                        'product_name': row[1],
                        'current_price': float(row[2]),
                        'currency': row[3],
                        'updated_at': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                    }
                    for row in results
                ]
            
            elif self.db_type == 'mysql' and MYSQL_AVAILABLE:
                hook = MySqlHook(mysql_conn_id=self.conn_id)
                
                if product_ids:
                    placeholders = ','.join(['%s'] * len(product_ids))
                    query = f"""
                        SELECT product_id, product_name, price, currency, updated_at
                        FROM {self.table_name}
                        WHERE product_id IN ({placeholders})
                    """
                    results = hook.get_records(query, parameters=product_ids)
                else:
                    query = f"""
                        SELECT product_id, product_name, price, currency, updated_at
                        FROM {self.table_name}
                        ORDER BY product_id
                    """
                    results = hook.get_records(query)
                
                return [
                    {
                        'product_id': row[0],
                        'product_name': row[1],
                        'current_price': float(row[2]),
                        'currency': row[3],
                        'updated_at': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                    }
                    for row in results
                ]
            
            else:
                logger.error(f"Tipo de BD no soportado o no disponible: {self.db_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo precios desde BD: {e}")
            return []
    
    def update_prices(
        self,
        price_updates: List[Dict]
    ) -> int:
        """
        Actualiza precios en base de datos
        
        Args:
            price_updates: Lista de actualizaciones de precio
        
        Returns:
            Número de registros actualizados
        """
        if not price_updates:
            return 0
        
        try:
            updated_count = 0
            
            if self.db_type == 'postgres' and POSTGRES_AVAILABLE:
                hook = PostgresHook(postgres_conn_id=self.conn_id)
                
                for update in price_updates:
                    query = f"""
                        UPDATE {self.table_name}
                        SET price = %s, updated_at = %s
                        WHERE product_id = %s
                    """
                    hook.run(
                        query,
                        parameters=(
                            update.get('new_price'),
                            datetime.now(),
                            update.get('product_id')
                        )
                    )
                    updated_count += 1
                    
                    # Registrar en historial
                    self._record_price_history(update, hook)
            
            elif self.db_type == 'mysql' and MYSQL_AVAILABLE:
                hook = MySqlHook(mysql_conn_id=self.conn_id)
                
                for update in price_updates:
                    query = f"""
                        UPDATE {self.table_name}
                        SET price = %s, updated_at = %s
                        WHERE product_id = %s
                    """
                    hook.run(
                        query,
                        parameters=(
                            update.get('new_price'),
                            datetime.now(),
                            update.get('product_id')
                        )
                    )
                    updated_count += 1
                    
                    # Registrar en historial
                    self._record_price_history(update, hook)
            
            logger.info(f"Actualizados {updated_count} precios en BD")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error actualizando precios en BD: {e}")
            return 0
    
    def _record_price_history(
        self,
        update: Dict,
        hook
    ):
        """Registra cambio de precio en tabla de historial"""
        try:
            query = f"""
                INSERT INTO {self.history_table}
                (product_id, product_name, old_price, new_price, change_percent, reason, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            hook.run(
                query,
                parameters=(
                    update.get('product_id'),
                    update.get('product_name'),
                    update.get('current_price'),
                    update.get('new_price'),
                    update.get('price_change_percent', 0),
                    update.get('reason', 'automated_update'),
                    datetime.now(),
                )
            )
        except Exception as e:
            logger.warning(f"Error registrando en historial: {e}")
    
    def get_price_history_from_db(
        self,
        product_id: str,
        days: int = 30
    ) -> List[Dict]:
        """
        Obtiene historial de precios desde BD
        
        Args:
            product_id: ID del producto
            days: Días de historial
        
        Returns:
            Lista de cambios históricos
        """
        try:
            if self.db_type == 'postgres' and POSTGRES_AVAILABLE:
                hook = PostgresHook(postgres_conn_id=self.conn_id)
                
                query = f"""
                    SELECT product_id, product_name, old_price, new_price, 
                           change_percent, reason, created_at
                    FROM {self.history_table}
                    WHERE product_id = %s
                    AND created_at >= NOW() - INTERVAL '%s days'
                    ORDER BY created_at DESC
                """
                results = hook.get_records(query, parameters=(product_id, days))
                
                return [
                    {
                        'product_id': row[0],
                        'product_name': row[1],
                        'old_price': float(row[2]),
                        'new_price': float(row[3]),
                        'change_percent': float(row[4]),
                        'reason': row[5],
                        'timestamp': row[6].isoformat() if hasattr(row[6], 'isoformat') else str(row[6]),
                    }
                    for row in results
                ]
            
            else:
                logger.warning("Historial desde BD no disponible para este tipo de BD")
                return []
                
        except Exception as e:
            logger.error(f"Error obteniendo historial desde BD: {e}")
            return []









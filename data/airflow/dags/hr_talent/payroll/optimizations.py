"""
Optimizaciones y Mejoras de Rendimiento
Batch processing, conexiones pool, queries optimizadas
"""

import logging
from typing import List, Dict, Any, Optional, Callable
from functools import wraps
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


class BatchProcessor:
    """Procesador por lotes para operaciones en masa"""
    
    @staticmethod
    def process_batch(
        items: List[Any],
        processor_func: Callable,
        batch_size: int = 100,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """
        Procesa items en lotes con paralelización
        
        Args:
            items: Lista de items a procesar
            processor_func: Función que procesa un item
            batch_size: Tamaño de lote
            max_workers: Número máximo de workers paralelos
        
        Returns:
            Dict con estadísticas de procesamiento y resultados
        """
        results = {
            "total": len(items),
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "results": []  # Agregar lista de resultados
        }
        
        # Dividir en lotes
        batches = [
            items[i:i + batch_size]
            for i in range(0, len(items), batch_size)
        ]
        
        def process_single_item(item):
            try:
                result = processor_func(item)
                return {"success": True, "result": result, "item": item}
            except Exception as e:
                return {"success": False, "item": item, "error": str(e), "result": None}
        
        # Procesar lotes en paralelo
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for batch in batches:
                futures = [
                    executor.submit(process_single_item, item)
                    for item in batch
                ]
                
                for future in as_completed(futures):
                    result = future.result()
                    results["processed"] += 1
                    
                    if result["success"]:
                        results["successful"] += 1
                        # Agregar resultado si está disponible
                        if result.get("result"):
                            results["results"].append(result["result"])
                    else:
                        results["failed"] += 1
                        results["errors"].append(result.get("error"))
                        # Agregar resultado fallido también
                        if result.get("result"):
                            results["results"].append(result["result"])
        
        return results
    
    @staticmethod
    def batch_insert(
        hook: PostgresHook,
        table: str,
        records: List[Dict[str, Any]],
        batch_size: int = 1000
    ) -> int:
        """
        Inserta registros en lotes para mejor rendimiento
        
        Args:
            hook: Hook de PostgreSQL
            table: Nombre de tabla
            records: Lista de diccionarios con datos
            batch_size: Tamaño de lote
        
        Returns:
            Número de registros insertados
        """
        if not records:
            return 0
        
        total_inserted = 0
        
        # Dividir en lotes
        batches = [
            records[i:i + batch_size]
            for i in range(0, len(records), batch_size)
        ]
        
        for batch in batches:
            if not batch:
                continue
            
            # Construir SQL de inserción
            columns = list(batch[0].keys())
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)
            
            sql = f"""
                INSERT INTO {table} ({columns_str})
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
            """
            
            # Preparar valores
            values_list = [
                tuple(record.get(col) for col in columns)
                for record in batch
            ]
            
            try:
                # Ejecutar en batch
                hook.insert_rows(
                    table=table,
                    rows=values_list,
                    target_fields=columns
                )
                total_inserted += len(batch)
            except Exception as e:
                logger.error(f"Error in batch insert: {e}")
                # Fallback a inserción individual
                for record in batch:
                    try:
                        values = tuple(record.get(col) for col in columns)
                        hook.run(sql, parameters=values)
                        total_inserted += 1
                    except Exception as e2:
                        logger.error(f"Error inserting individual record: {e2}")
        
        return total_inserted


def performance_monitor(func: Callable) -> Callable:
    """Decorador para monitorear rendimiento"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(
                f"{func.__name__} completed in {execution_time:.2f}s"
            )
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {execution_time:.2f}s: {e}"
            )
            raise
    
    return wrapper


class QueryOptimizer:
    """Optimizador de queries"""
    
    @staticmethod
    def optimize_payroll_query(
        period_start: date,
        period_end: date,
        employee_ids: Optional[List[str]] = None
    ) -> str:
        """Genera query optimizada para nómina"""
        conditions = ["pp.period_start = %s", "pp.period_end = %s"]
        params = [period_start, period_end]
        
        if employee_ids:
            placeholders = ", ".join(["%s"] * len(employee_ids))
            conditions.append(f"pp.employee_id IN ({placeholders})")
            params.extend(employee_ids)
        
        where_clause = " AND ".join(conditions)
        
        # Query optimizada con índices apropiados
        sql = f"""
            SELECT 
                pp.id,
                pp.employee_id,
                e.name,
                pp.gross_pay,
                pp.net_pay,
                pp.total_hours
            FROM payroll_pay_periods pp
            INNER JOIN payroll_employees e 
                ON pp.employee_id = e.employee_id
            WHERE {where_clause}
                AND pp.status IN ('calculated', 'reviewed', 'approved', 'paid')
            ORDER BY pp.employee_id
        """
        
        return sql, params


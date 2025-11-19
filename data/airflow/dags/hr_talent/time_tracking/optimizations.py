"""
Optimizaciones de Rendimiento y Caché
Mejora el rendimiento del sistema con caché y optimizaciones
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from functools import wraps
import hashlib
import json
import time

from .storage import TimeTrackingStorage

logger = logging.getLogger(__name__)


class CacheManager:
    """Gestor de caché para optimizar consultas frecuentes"""
    
    def __init__(self, storage: TimeTrackingStorage, ttl_seconds: int = 300):
        self.storage = storage
        self.ttl_seconds = ttl_seconds
        self._cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché"""
        if key not in self._cache:
            return None
        
        cached_item = self._cache[key]
        
        # Verificar expiración
        if datetime.now() > cached_item['expires_at']:
            del self._cache[key]
            return None
        
        return cached_item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena valor en caché"""
        ttl = ttl or self.ttl_seconds
        expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.now()
        }
    
    def invalidate(self, pattern: str) -> None:
        """Invalida caché que coincida con un patrón"""
        keys_to_remove = [k for k in self._cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear(self) -> None:
        """Limpia todo el caché"""
        self._cache.clear()
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera clave de caché"""
        key_parts = [prefix] + [str(arg) for arg in args]
        if kwargs:
            key_parts.append(json.dumps(kwargs, sort_keys=True))
        
        key_string = ':'.join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()


def cached(cache_manager: CacheManager, ttl: int = 300):
    """Decorador para cachear resultados de funciones"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave de caché
            cache_key = cache_manager._generate_key(
                func.__name__,
                *args,
                **kwargs
            )
            
            # Intentar obtener del caché
            cached_result = cache_manager.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return cached_result
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Almacenar en caché
            cache_manager.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, cached result")
            
            return result
        
        return wrapper
    return decorator


class QueryOptimizer:
    """Optimizador de consultas SQL"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def optimize_time_entry_query(
        self,
        employee_id: str,
        start_date: date,
        end_date: date
    ) -> str:
        """Optimiza consulta de entradas de tiempo"""
        # Usar índices específicos
        sql = """
            SELECT 
                ws.id,
                ws.work_date,
                ws.total_hours,
                ws.regular_hours,
                ws.overtime_hours
            FROM time_tracking_work_sessions ws
            WHERE ws.employee_id = %s
                AND ws.work_date BETWEEN %s AND %s
                AND ws.status = 'closed'
            ORDER BY ws.work_date
            LIMIT 1000
        """
        
        return sql
    
    def batch_update_sessions(self, updates: List[Dict[str, Any]]) -> int:
        """Actualiza múltiples sesiones en batch"""
        if not updates:
            return 0
        
        # Construir query de actualización masiva
        sql = """
            UPDATE time_tracking_work_sessions
            SET 
                status = CASE id
        """
        
        # Esto es una simplificación - en producción usaría una mejor estrategia
        # como executemany o COPY FROM
        
        count = 0
        for update in updates:
            session_id = update.get('session_id')
            new_status = update.get('status')
            
            if session_id and new_status:
                update_sql = """
                    UPDATE time_tracking_work_sessions
                    SET status = %s, updated_at = NOW()
                    WHERE id = %s
                """
                self.storage.hook.run(
                    update_sql,
                    parameters=(new_status, session_id)
                )
                count += 1
        
        return count


class PerformanceMonitor:
    """Monitor de rendimiento"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
        self.metrics = {
            'query_count': 0,
            'total_query_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def track_query(self, query_time: float) -> None:
        """Registra tiempo de consulta"""
        self.metrics['query_count'] += 1
        self.metrics['total_query_time'] += query_time
    
    def track_cache_hit(self) -> None:
        """Registra cache hit"""
        self.metrics['cache_hits'] += 1
    
    def track_cache_miss(self) -> None:
        """Registra cache miss"""
        self.metrics['cache_misses'] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento"""
        avg_query_time = (
            self.metrics['total_query_time'] / self.metrics['query_count']
            if self.metrics['query_count'] > 0 else 0
        )
        
        cache_hit_rate = (
            self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        )
        
        return {
            'query_count': self.metrics['query_count'],
            'average_query_time_ms': round(avg_query_time * 1000, 2),
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': round(cache_hit_rate * 100, 2)
        }
    
    def reset(self) -> None:
        """Reinicia métricas"""
        self.metrics = {
            'query_count': 0,
            'total_query_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }


class DatabaseMaintenance:
    """Mantenimiento de base de datos"""
    
    def __init__(self, storage: TimeTrackingStorage):
        self.storage = storage
    
    def optimize_indexes(self) -> Dict[str, Any]:
        """Optimiza índices de la base de datos"""
        # ANALYZE y REINDEX en PostgreSQL
        sql = """
            ANALYZE time_tracking_work_sessions;
            ANALYZE time_tracking_clock_events;
            ANALYZE time_tracking_vacations;
        """
        
        try:
            self.storage.hook.run(sql)
            return {
                "success": True,
                "message": "Indexes optimized"
            }
        except Exception as e:
            logger.error(f"Error optimizing indexes: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def vacuum_tables(self) -> Dict[str, Any]:
        """Ejecuta VACUUM en tablas"""
        sql = """
            VACUUM ANALYZE time_tracking_work_sessions;
            VACUUM ANALYZE time_tracking_clock_events;
        """
        
        try:
            self.storage.hook.run(sql)
            return {
                "success": True,
                "message": "Tables vacuumed"
            }
        except Exception as e:
            logger.error(f"Error vacuuming tables: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def archive_old_data(self, days_to_keep: int = 365) -> Dict[str, Any]:
        """Archiva datos antiguos"""
        cutoff_date = date.today() - timedelta(days=days_to_keep)
        
        # Crear tabla de archivo si no existe
        archive_sql = """
            CREATE TABLE IF NOT EXISTS time_tracking_work_sessions_archive
            (LIKE time_tracking_work_sessions INCLUDING ALL);
        """
        
        self.storage.hook.run(archive_sql)
        
        # Mover datos antiguos
        move_sql = """
            INSERT INTO time_tracking_work_sessions_archive
            SELECT * FROM time_tracking_work_sessions
            WHERE work_date < %s
                AND status = 'closed'
                AND approved = true;
        """
        
        self.storage.hook.run(move_sql, parameters=(cutoff_date,))
        
        # Eliminar datos movidos
        delete_sql = """
            DELETE FROM time_tracking_work_sessions
            WHERE work_date < %s
                AND status = 'closed'
                AND approved = true;
        """
        
        self.storage.hook.run(delete_sql, parameters=(cutoff_date,))
        
        return {
            "success": True,
            "cutoff_date": cutoff_date.isoformat(),
            "archived": True
        }


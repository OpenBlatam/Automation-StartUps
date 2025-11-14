"""
Sistema de Optimización de Rendimiento Avanzado
==============================================

Sistema completo de optimización con caching inteligente,
procesamiento asíncrono, y técnicas avanzadas de rendimiento.
"""

import asyncio
import aiohttp
import aioredis
import threading
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import functools
import weakref
import gc
import psutil
import sqlite3
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
import multiprocessing as mp
from queue import Queue, PriorityQueue
import heapq

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Estrategias de caché"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"

class ProcessingMode(Enum):
    """Modos de procesamiento"""
    SYNC = "sync"
    ASYNC = "async"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"

@dataclass
class PerformanceMetrics:
    """Métricas de rendimiento"""
    operation_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    cache_hit_rate: float
    throughput: float
    latency: float
    timestamp: datetime

@dataclass
class CacheEntry:
    """Entrada de caché"""
    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[float] = None
    size_bytes: int = 0

class IntelligentCache:
    """Sistema de caché inteligente"""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: List[str] = []
        self.access_counts: Dict[str, int] = {}
        self.total_hits = 0
        self.total_misses = 0
        self.lock = threading.RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Verificar TTL
                if entry.ttl and datetime.now() > entry.created_at + timedelta(seconds=entry.ttl):
                    self._remove_entry(key)
                    self.total_misses += 1
                    return None
                
                # Actualizar estadísticas
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
                
                # Actualizar orden de acceso para LRU
                if self.strategy == CacheStrategy.LRU:
                    if key in self.access_order:
                        self.access_order.remove(key)
                    self.access_order.append(key)
                
                self.total_hits += 1
                return entry.value
            else:
                self.total_misses += 1
                return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Establecer valor en caché"""
        with self.lock:
            # Calcular tamaño
            size_bytes = self._calculate_size(value)
            
            # Crear entrada
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                ttl=ttl,
                size_bytes=size_bytes
            )
            
            # Si la clave ya existe, actualizar
            if key in self.cache:
                self._remove_entry(key)
            
            # Verificar espacio disponible
            while len(self.cache) >= self.max_size:
                self._evict_entry()
            
            # Agregar entrada
            self.cache[key] = entry
            self.access_order.append(key)
            self.access_counts[key] = 1
    
    def _remove_entry(self, key: str) -> None:
        """Remover entrada del caché"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            if key in self.access_counts:
                del self.access_counts[key]
    
    def _evict_entry(self) -> None:
        """Expulsar entrada según estrategia"""
        if not self.cache:
            return
        
        if self.strategy == CacheStrategy.LRU:
            # Remover el menos recientemente usado
            if self.access_order:
                key_to_remove = self.access_order[0]
                self._remove_entry(key_to_remove)
        
        elif self.strategy == CacheStrategy.LFU:
            # Remover el menos frecuentemente usado
            if self.access_counts:
                key_to_remove = min(self.access_counts.keys(), 
                                  key=lambda k: self.access_counts[k])
                self._remove_entry(key_to_remove)
        
        elif self.strategy == CacheStrategy.TTL:
            # Remover el más antiguo
            oldest_key = min(self.cache.keys(), 
                            key=lambda k: self.cache[k].created_at)
            self._remove_entry(oldest_key)
    
    def _calculate_size(self, value: Any) -> int:
        """Calcular tamaño aproximado del valor"""
        try:
            return len(json.dumps(value, default=str).encode('utf-8'))
        except:
            return 1024  # Tamaño por defecto
    
    def get_hit_rate(self) -> float:
        """Obtener tasa de aciertos"""
        total = self.total_hits + self.total_misses
        return self.total_hits / total if total > 0 else 0.0
    
    def clear(self) -> None:
        """Limpiar caché"""
        with self.lock:
            self.cache.clear()
            self.access_order.clear()
            self.access_counts.clear()
            self.total_hits = 0
            self.total_misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del caché"""
        with self.lock:
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hit_rate': self.get_hit_rate(),
                'total_hits': self.total_hits,
                'total_misses': self.total_misses,
                'strategy': self.strategy.value,
                'memory_usage': sum(entry.size_bytes for entry in self.cache.values())
            }

class AsyncProcessor:
    """Procesador asíncrono"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks = {}
        self.results = {}
        
    async def process_async(self, func: Callable, *args, **kwargs) -> Any:
        """Procesar función de forma asíncrona"""
        loop = asyncio.get_event_loop()
        
        # Ejecutar en thread pool
        result = await loop.run_in_executor(self.executor, func, *args, **kwargs)
        
        return result
    
    async def process_batch_async(self, tasks: List[Tuple[Callable, tuple, dict]]) -> List[Any]:
        """Procesar lote de tareas de forma asíncrona"""
        loop = asyncio.get_event_loop()
        
        # Crear corrutinas para todas las tareas
        coroutines = []
        for func, args, kwargs in tasks:
            coro = loop.run_in_executor(self.executor, func, *args, **kwargs)
            coroutines.append(coro)
        
        # Ejecutar todas las tareas en paralelo
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        return results
    
    async def process_with_timeout(self, func: Callable, timeout: float, *args, **kwargs) -> Any:
        """Procesar con timeout"""
        try:
            result = await asyncio.wait_for(
                self.process_async(func, *args, **kwargs),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.warning(f"Timeout en procesamiento de {func.__name__}")
            raise
    
    def shutdown(self):
        """Cerrar procesador"""
        self.executor.shutdown(wait=True)

class DatabaseOptimizer:
    """Optimizador de base de datos"""
    
    def __init__(self, db_path: str = "inventory.db"):
        self.db_path = db_path
        self.connection_pool = []
        self.pool_size = 10
        self.pool_lock = threading.Lock()
        self.query_cache = IntelligentCache(max_size=500, strategy=CacheStrategy.LRU)
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Inicializar pool de conexiones"""
        for _ in range(self.pool_size):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=MEMORY")
            self.connection_pool.append(conn)
    
    def get_connection(self) -> sqlite3.Connection:
        """Obtener conexión del pool"""
        with self.pool_lock:
            if self.connection_pool:
                return self.connection_pool.pop()
            else:
                # Crear nueva conexión si el pool está vacío
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.execute("PRAGMA journal_mode=WAL")
                return conn
    
    def return_connection(self, conn: sqlite3.Connection):
        """Devolver conexión al pool"""
        with self.pool_lock:
            if len(self.connection_pool) < self.pool_size:
                self.connection_pool.append(conn)
            else:
                conn.close()
    
    def execute_query_cached(self, query: str, params: tuple = (), cache_ttl: float = 300) -> List[Dict[str, Any]]:
        """Ejecutar query con caché"""
        cache_key = f"query:{hash(query + str(params))}"
        
        # Intentar obtener del caché
        cached_result = self.query_cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Ejecutar query
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            # Convertir a diccionarios
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            # Guardar en caché
            self.query_cache.set(cache_key, results, ttl=cache_ttl)
            
            return results
        
        finally:
            self.return_connection(conn)
    
    def execute_batch_queries(self, queries: List[Tuple[str, tuple]]) -> List[List[Dict[str, Any]]]:
        """Ejecutar múltiples queries en paralelo"""
        with ThreadPoolExecutor(max_workers=min(len(queries), self.pool_size)) as executor:
            futures = []
            for query, params in queries:
                future = executor.submit(self.execute_query_cached, query, params)
                futures.append(future)
            
            results = []
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error en query batch: {e}")
                    results.append([])
            
            return results
    
    def optimize_database(self):
        """Optimizar base de datos"""
        conn = self.get_connection()
        try:
            # Analizar tablas
            conn.execute("ANALYZE")
            
            # Optimizar índices
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            for table in tables:
                # Crear índices si no existen
                cursor.execute(f"PRAGMA index_list({table})")
                existing_indexes = [row[1] for row in cursor.fetchall()]
                
                # Índices comunes para optimización
                common_indexes = [
                    f"idx_{table}_id",
                    f"idx_{table}_created_at",
                    f"idx_{table}_updated_at"
                ]
                
                for index_name in common_indexes:
                    if index_name not in existing_indexes:
                        try:
                            if 'id' in index_name:
                                conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}(id)")
                            elif 'created_at' in index_name:
                                conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}(created_at)")
                            elif 'updated_at' in index_name:
                                conn.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table}(updated_at)")
                        except sqlite3.OperationalError:
                            pass  # Columna no existe
            
            conn.commit()
            logger.info("Base de datos optimizada")
        
        finally:
            self.return_connection(conn)

class MemoryManager:
    """Gestor de memoria avanzado"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% de uso de memoria
        self.cleanup_interval = 60  # segundos
        self.last_cleanup = datetime.now()
        self.memory_stats = []
        
    def get_memory_usage(self) -> Dict[str, float]:
        """Obtener uso de memoria"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent(),
            'available': psutil.virtual_memory().available / 1024 / 1024,  # MB
            'total': psutil.virtual_memory().total / 1024 / 1024  # MB
        }
    
    def should_cleanup(self) -> bool:
        """Determinar si se necesita limpieza de memoria"""
        memory_usage = self.get_memory_usage()
        
        # Verificar umbral de memoria
        if memory_usage['percent'] > self.memory_threshold * 100:
            return True
        
        # Verificar tiempo desde última limpieza
        if (datetime.now() - self.last_cleanup).total_seconds() > self.cleanup_interval:
            return True
        
        return False
    
    def cleanup_memory(self):
        """Limpiar memoria"""
        logger.info("Iniciando limpieza de memoria")
        
        # Forzar recolección de basura
        collected = gc.collect()
        
        # Limpiar referencias débiles
        weakref_collected = 0
        for obj in list(weakref.WeakSet()):
            if obj is None:
                weakref_collected += 1
        
        self.last_cleanup = datetime.now()
        
        memory_after = self.get_memory_usage()
        
        logger.info(f"Limpieza completada: {collected} objetos recolectados, "
                   f"memoria: {memory_after['percent']:.1f}%")
        
        return {
            'objects_collected': collected,
            'weakref_collected': weakref_collected,
            'memory_after': memory_after
        }
    
    def monitor_memory(self):
        """Monitorear memoria continuamente"""
        while True:
            memory_usage = self.get_memory_usage()
            self.memory_stats.append({
                'timestamp': datetime.now(),
                'usage': memory_usage
            })
            
            # Mantener solo los últimos 100 registros
            if len(self.memory_stats) > 100:
                self.memory_stats.pop(0)
            
            if self.should_cleanup():
                self.cleanup_memory()
            
            time.sleep(10)  # Verificar cada 10 segundos

class PerformanceProfiler:
    """Profiler de rendimiento"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.active_profiles = {}
        
    def profile_function(self, func_name: str = None):
        """Decorador para perfilar funciones"""
        def decorator(func):
            name = func_name or func.__name__
            
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = psutil.Process().memory_info().rss
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    end_memory = psutil.Process().memory_info().rss
                    
                    execution_time = end_time - start_time
                    memory_usage = (end_memory - start_memory) / 1024 / 1024  # MB
                    cpu_usage = psutil.Process().cpu_percent()
                    
                    metrics = PerformanceMetrics(
                        operation_name=name,
                        execution_time=execution_time,
                        memory_usage=memory_usage,
                        cpu_usage=cpu_usage,
                        cache_hit_rate=0.0,  # Se calculará por separado
                        throughput=1.0 / execution_time if execution_time > 0 else 0,
                        latency=execution_time,
                        timestamp=datetime.now()
                    )
                    
                    self.metrics.append(metrics)
                    
                    # Mantener solo los últimos 1000 registros
                    if len(self.metrics) > 1000:
                        self.metrics.pop(0)
            
            return wrapper
        return decorator
    
    def start_profile(self, operation_name: str) -> str:
        """Iniciar perfil de operación"""
        profile_id = f"{operation_name}_{int(time.time() * 1000)}"
        
        self.active_profiles[profile_id] = {
            'name': operation_name,
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss,
            'start_cpu': psutil.Process().cpu_percent()
        }
        
        return profile_id
    
    def end_profile(self, profile_id: str) -> PerformanceMetrics:
        """Finalizar perfil de operación"""
        if profile_id not in self.active_profiles:
            raise ValueError(f"Perfil {profile_id} no encontrado")
        
        profile = self.active_profiles[profile_id]
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        end_cpu = psutil.Process().cpu_percent()
        
        execution_time = end_time - profile['start_time']
        memory_usage = (end_memory - profile['start_memory']) / 1024 / 1024
        cpu_usage = end_cpu - profile['start_cpu']
        
        metrics = PerformanceMetrics(
            operation_name=profile['name'],
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            cache_hit_rate=0.0,
            throughput=1.0 / execution_time if execution_time > 0 else 0,
            latency=execution_time,
            timestamp=datetime.now()
        )
        
        self.metrics.append(metrics)
        del self.active_profiles[profile_id]
        
        return metrics
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtener resumen de rendimiento"""
        if not self.metrics:
            return {}
        
        # Agrupar por operación
        operations = {}
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in operations:
                operations[op_name] = []
            operations[op_name].append(metric)
        
        summary = {}
        for op_name, op_metrics in operations.items():
            execution_times = [m.execution_time for m in op_metrics]
            memory_usages = [m.memory_usage for m in op_metrics]
            cpu_usages = [m.cpu_usage for m in op_metrics]
            
            summary[op_name] = {
                'count': len(op_metrics),
                'avg_execution_time': np.mean(execution_times),
                'max_execution_time': np.max(execution_times),
                'min_execution_time': np.min(execution_times),
                'avg_memory_usage': np.mean(memory_usages),
                'max_memory_usage': np.max(memory_usages),
                'avg_cpu_usage': np.mean(cpu_usages),
                'max_cpu_usage': np.max(cpu_usages),
                'total_calls': len(op_metrics)
            }
        
        return summary

class PerformanceOptimizer:
    """Optimizador principal de rendimiento"""
    
    def __init__(self):
        self.cache = IntelligentCache(max_size=2000, strategy=CacheStrategy.LRU)
        self.async_processor = AsyncProcessor(max_workers=20)
        self.db_optimizer = DatabaseOptimizer()
        self.memory_manager = MemoryManager()
        self.profiler = PerformanceProfiler()
        self.is_monitoring = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Iniciar monitoreo de rendimiento"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self._monitor_performance)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            logger.info("Monitoreo de rendimiento iniciado")
    
    def stop_monitoring(self):
        """Detener monitoreo de rendimiento"""
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=5)
            logger.info("Monitoreo de rendimiento detenido")
    
    def _monitor_performance(self):
        """Monitorear rendimiento continuamente"""
        while self.is_monitoring:
            try:
                # Verificar memoria
                if self.memory_manager.should_cleanup():
                    self.memory_manager.cleanup_memory()
                
                # Optimizar base de datos periódicamente
                if datetime.now().hour % 6 == 0:  # Cada 6 horas
                    self.db_optimizer.optimize_database()
                
                time.sleep(30)  # Verificar cada 30 segundos
                
            except Exception as e:
                logger.error(f"Error en monitoreo de rendimiento: {e}")
                time.sleep(60)
    
    @property
    def profile_function(self):
        """Decorador de perfil de función"""
        return self.profiler.profile_function
    
    def optimize_query(self, query: str, params: tuple = (), cache_ttl: float = 300) -> List[Dict[str, Any]]:
        """Optimizar query con caché"""
        return self.db_optimizer.execute_query_cached(query, params, cache_ttl)
    
    async def process_async(self, func: Callable, *args, **kwargs) -> Any:
        """Procesar función de forma asíncrona"""
        return await self.async_processor.process_async(func, *args, **kwargs)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de caché"""
        return self.cache.get_stats()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de memoria"""
        return self.memory_manager.get_memory_usage()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de rendimiento"""
        return self.profiler.get_performance_summary()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        return {
            'cache': self.get_cache_stats(),
            'memory': self.get_memory_stats(),
            'performance': self.get_performance_stats(),
            'monitoring_active': self.is_monitoring,
            'timestamp': datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Cerrar optimizador"""
        self.stop_monitoring()
        self.async_processor.shutdown()
        logger.info("Optimizador de rendimiento cerrado")

# Instancia global del optimizador
performance_optimizer = PerformanceOptimizer()

# Funciones de conveniencia
def optimize_query(query: str, params: tuple = (), cache_ttl: float = 300) -> List[Dict[str, Any]]:
    """Optimizar query"""
    return performance_optimizer.optimize_query(query, params, cache_ttl)

async def process_async(func: Callable, *args, **kwargs) -> Any:
    """Procesar función asíncronamente"""
    return await performance_optimizer.process_async(func, *args, **kwargs)

def profile_function(func_name: str = None):
    """Decorador de perfil de función"""
    return performance_optimizer.profile_function(func_name)

if __name__ == "__main__":
    # Ejemplo de uso
    logger.info("Probando sistema de optimización de rendimiento...")
    
    # Inicializar optimizador
    performance_optimizer.start_monitoring()
    
    try:
        # Probar caché
        cache = IntelligentCache(max_size=100, strategy=CacheStrategy.LRU)
        
        # Agregar datos al caché
        for i in range(50):
            cache.set(f"key_{i}", f"value_{i}", ttl=60)
        
        # Probar acceso
        for i in range(100):
            cache.get(f"key_{i % 50}")
        
        print(f"✅ Caché LRU: Tasa de aciertos {cache.get_hit_rate():.2%}")
        
        # Probar optimización de base de datos
        db_optimizer = DatabaseOptimizer()
        
        # Query optimizada con caché
        result = db_optimizer.execute_query_cached(
            "SELECT COUNT(*) as count FROM inventory",
            cache_ttl=300
        )
        print(f"✅ Query optimizada: {result[0]['count']} registros")
        
        # Probar profiler
        profiler = PerformanceProfiler()
        
        @profiler.profile_function("test_function")
        def test_function():
            time.sleep(0.1)
            return "test_result"
        
        # Ejecutar función perfilada
        for _ in range(10):
            test_function()
        
        summary = profiler.get_performance_summary()
        print(f"✅ Profiler: {len(summary)} operaciones perfiladas")
        
        # Estadísticas del sistema
        stats = performance_optimizer.get_system_stats()
        print(f"✅ Estadísticas del sistema obtenidas")
        print(f"   Caché: {stats['cache']['size']} entradas")
        print(f"   Memoria: {stats['memory']['percent']:.1f}%")
        print(f"   Monitoreo: {'Activo' if stats['monitoring_active'] else 'Inactivo'}")
        
    except Exception as e:
        logger.error(f"Error en pruebas de optimización: {e}")
    
    finally:
        # Cerrar optimizador
        performance_optimizer.shutdown()
    
    print("✅ Sistema de optimización de rendimiento funcionando correctamente")




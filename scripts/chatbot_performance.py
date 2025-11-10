#!/usr/bin/env python3
"""
Optimizaciones de Rendimiento para Chatbots
Incluye profiling, optimizaciones y mejoras de velocidad
"""

import time
import cProfile
import pstats
from functools import wraps
from typing import Callable, Dict, List
from collections import deque
from datetime import datetime


class PerformanceMonitor:
    """Monitor de rendimiento para chatbots"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.response_times = deque(maxlen=max_history)
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_requests = 0
    
    def record_response_time(self, response_time: float):
        """Registra tiempo de respuesta"""
        self.response_times.append(response_time)
        self.total_requests += 1
    
    def record_cache_hit(self):
        """Registra acierto de cache"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Registra fallo de cache"""
        self.cache_misses += 1
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas de rendimiento"""
        if not self.response_times:
            return {
                "total_requests": 0,
                "average_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0,
                "cache_hit_rate": 0.0
            }
        
        response_times_list = list(self.response_times)
        
        return {
            "total_requests": self.total_requests,
            "average_response_time": sum(response_times_list) / len(response_times_list),
            "min_response_time": min(response_times_list),
            "max_response_time": max(response_times_list),
            "p95_response_time": self._percentile(response_times_list, 95),
            "p99_response_time": self._percentile(response_times_list, 99),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": (
                self.cache_hits / (self.cache_hits + self.cache_misses)
                if (self.cache_hits + self.cache_misses) > 0 else 0.0
            )
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcula percentil"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


def performance_timer(func: Callable) -> Callable:
    """Decorador para medir tiempo de ejecución"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        
        # Si el objeto tiene monitor de rendimiento, registrar
        if args and hasattr(args[0], 'performance_monitor'):
            args[0].performance_monitor.record_response_time(execution_time)
        
        return result
    return wrapper


def profile_function(func: Callable, *args, **kwargs):
    """
    Ejecuta una función con profiling.
    
    Returns:
        (result, stats_dict)
    """
    profiler = cProfile.Profile()
    profiler.enable()
    
    result = func(*args, **kwargs)
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    
    # Convertir stats a diccionario
    stats_dict = {
        "total_calls": stats.total_calls,
        "primitive_calls": stats.primitive_calls,
        "total_time": stats.total_tt,
        "cumulative_time": stats.total_cumulative_time
    }
    
    return result, stats_dict


class BatchProcessor:
    """Procesador de mensajes en lote para mejor rendimiento"""
    
    def __init__(self, chatbot_instance, batch_size: int = 10):
        self.chatbot = chatbot_instance
        self.batch_size = batch_size
        self.batch_queue = []
    
    def add_message(self, message: str, **kwargs):
        """Agrega mensaje al lote"""
        self.batch_queue.append((message, kwargs))
        
        if len(self.batch_queue) >= self.batch_size:
            return self.process_batch()
        
        return None
    
    def process_batch(self) -> List[Dict]:
        """Procesa el lote de mensajes"""
        results = []
        
        for message, kwargs in self.batch_queue:
            try:
                result = self.chatbot.process_message(message, **kwargs)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e)})
        
        self.batch_queue.clear()
        return results
    
    def flush(self) -> List[Dict]:
        """Procesa mensajes pendientes"""
        if self.batch_queue:
            return self.process_batch()
        return []


def optimize_faq_search(faqs: List[Dict]) -> Dict:
    """
    Optimiza la estructura de FAQs para búsqueda más rápida.
    Crea índices invertidos y estructuras optimizadas.
    """
    # Índice invertido: palabra -> lista de FAQs
    inverted_index = {}
    
    # Índice por categoría
    category_index = {}
    
    # Índice por keywords
    keyword_index = {}
    
    for faq in faqs:
        faq_id = faq.get('id', '')
        category = faq.get('category', '')
        keywords = faq.get('keywords', [])
        
        # Indexar por categoría
        if category not in category_index:
            category_index[category] = []
        category_index[category].append(faq)
        
        # Indexar por keywords
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower not in keyword_index:
                keyword_index[keyword_lower] = []
            keyword_index[keyword_lower].append(faq)
        
        # Indexar por palabras en pregunta y respuesta
        text = f"{faq.get('question', '')} {faq.get('answer', '')}".lower()
        words = set(text.split())
        
        for word in words:
            if len(word) > 2:  # Ignorar palabras muy cortas
                if word not in inverted_index:
                    inverted_index[word] = []
                if faq not in inverted_index[word]:
                    inverted_index[word].append(faq)
    
    return {
        "inverted_index": inverted_index,
        "category_index": category_index,
        "keyword_index": keyword_index,
        "total_faqs": len(faqs)
    }


class ConnectionPool:
    """Pool de conexiones para mejor rendimiento (simulado)"""
    
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_queue = deque()
    
    def acquire(self):
        """Adquiere una conexión"""
        if self.active_connections < self.max_connections:
            self.active_connections += 1
            return True
        return False
    
    def release(self):
        """Libera una conexión"""
        if self.active_connections > 0:
            self.active_connections -= 1
            return True
        return False
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del pool"""
        return {
            "max_connections": self.max_connections,
            "active_connections": self.active_connections,
            "available_connections": self.max_connections - self.active_connections,
            "utilization": self.active_connections / self.max_connections if self.max_connections > 0 else 0
        }







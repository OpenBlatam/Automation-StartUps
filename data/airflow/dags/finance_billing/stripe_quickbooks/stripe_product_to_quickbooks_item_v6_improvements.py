"""
Mejoras Avanzadas V6 para stripe_product_to_quickbooks_item.py

Este archivo contiene mejoras adicionales que se pueden integrar:
- Async/await support
- Event sourcing y audit trail
- Observability avanzada (tracing, métricas)
- Webhook support para sincronización en tiempo real
- Rate limiting adaptativo mejorado
- Idempotency keys
- Health checks mejorados

Para usar estas mejoras, importa las funciones/clases desde este módulo o
copia el código al archivo principal.
"""
import os
import re
import time
import logging
import json
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, Any, Literal, Union, List
from enum import Enum

logger = logging.getLogger(__name__)

# Intentar importar librerías opcionales
try:
    import asyncio
    from typing import AsyncGenerator, Callable
    ASYNC_AVAILABLE = True
except ImportError:
    ASYNC_AVAILABLE = False

try:
    import uuid
    UUID_AVAILABLE = True
except ImportError:
    UUID_AVAILABLE = False

try:
    import hmac
    import hashlib
    HMAC_AVAILABLE = True
except ImportError:
    HMAC_AVAILABLE = False


# ============================================================================
# EVENT SOURCING Y AUDIT TRAIL
# ============================================================================

@dataclass
class SyncEvent:
    """Evento de sincronización para audit trail."""
    event_id: str
    timestamp: float
    event_type: Literal["sync_started", "sync_completed", "sync_failed", "item_created", "item_updated", "rate_limited"]
    stripe_product_id: Optional[str] = None
    qb_item_id: Optional[str] = None
    action: Optional[str] = None
    duration_ms: Optional[float] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el evento a diccionario."""
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "stripe_product_id": self.stripe_product_id,
            "qb_item_id": self.qb_item_id,
            "action": self.action,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message,
            "metadata": self.metadata
        }


class EventStore:
    """Almacén de eventos para audit trail."""
    
    def __init__(self, max_events: int = 10000):
        self.events: List[SyncEvent] = []
        self.max_events = max_events
    
    def add_event(self, event: SyncEvent) -> None:
        """Agrega un evento al store."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events = self.events[-self.max_events:]
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        stripe_product_id: Optional[str] = None,
        since: Optional[float] = None,
        limit: Optional[int] = None
    ) -> List[SyncEvent]:
        """Obtiene eventos filtrados."""
        filtered = self.events
        
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if stripe_product_id:
            filtered = [e for e in filtered if e.stripe_product_id == stripe_product_id]
        if since:
            filtered = [e for e in filtered if e.timestamp >= since]
        
        if limit:
            filtered = filtered[:limit]
        
        return filtered
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de eventos."""
        if not self.events:
            return {"total": 0}
        
        event_types = {}
        for event in self.events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
        
        return {
            "total": len(self.events),
            "by_type": event_types,
            "oldest": min(e.timestamp for e in self.events) if self.events else None,
            "newest": max(e.timestamp for e in self.events) if self.events else None
        }


# Event store global (importar desde módulo principal si se integra)
_global_event_store = EventStore()


def create_sync_event(
    event_type: str,
    stripe_product_id: Optional[str] = None,
    qb_item_id: Optional[str] = None,
    action: Optional[str] = None,
    duration_ms: Optional[float] = None,
    error_message: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> SyncEvent:
    """Crea un evento de sincronización."""
    event_id = str(uuid.uuid4()) if UUID_AVAILABLE else f"evt_{int(time.time() * 1000)}"
    return SyncEvent(
        event_id=event_id,
        timestamp=time.time(),
        event_type=event_type,
        stripe_product_id=stripe_product_id,
        qb_item_id=qb_item_id,
        action=action,
        duration_ms=duration_ms,
        error_message=error_message,
        metadata=metadata or {}
    )


# ============================================================================
# IDEMPOTENCY SUPPORT
# ============================================================================

class IdempotencyStore:
    """Almacén para keys de idempotencia."""
    
    def __init__(self, ttl_seconds: int = 86400):  # 24 horas
        self.keys: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def check_key(self, key: str) -> Optional[Dict[str, Any]]:
        """Verifica si una key de idempotencia existe."""
        if key not in self.keys:
            return None
        
        entry = self.keys[key]
        # Verificar expiración
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            del self.keys[key]
            return None
        
        return entry["result"]
    
    def store_key(self, key: str, result: Dict[str, Any]) -> None:
        """Almacena una key de idempotencia con su resultado."""
        self.keys[key] = {
            "timestamp": time.time(),
            "result": result
        }
        
        # Limpiar keys expiradas periódicamente
        if len(self.keys) > 10000:
            current_time = time.time()
            expired_keys = [
                k for k, v in self.keys.items()
                if current_time - v["timestamp"] > self.ttl_seconds
            ]
            for k in expired_keys:
                del self.keys[k]


_global_idempotency_store = IdempotencyStore()


def generate_idempotency_key(stripe_product_id: str, precio: float, action: str = "sync") -> str:
    """Genera una key de idempotencia."""
    if not HMAC_AVAILABLE:
        return f"{stripe_product_id}:{precio}:{action}"
    key_string = f"{stripe_product_id}:{precio}:{action}"
    return hashlib.sha256(key_string.encode()).hexdigest()


# ============================================================================
# ENHANCED OBSERVABILITY
# ============================================================================

class ObservabilityManager:
    """Gestor de observabilidad (tracing, métricas, logging estructurado)."""
    
    def __init__(self):
        self.traces: List[Dict[str, Any]] = []
        self.metrics: Dict[str, List[float]] = {}
    
    def start_trace(self, operation: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Inicia un trace."""
        trace_id = str(uuid.uuid4()) if UUID_AVAILABLE else f"trace_{int(time.time() * 1000)}"
        trace = {
            "trace_id": trace_id,
            "operation": operation,
            "start_time": time.time(),
            "metadata": metadata or {}
        }
        self.traces.append(trace)
        return trace_id
    
    def end_trace(self, trace_id: str, success: bool = True, error: Optional[str] = None) -> None:
        """Finaliza un trace."""
        for trace in self.traces:
            if trace["trace_id"] == trace_id:
                trace["end_time"] = time.time()
                trace["duration_ms"] = (trace["end_time"] - trace["start_time"]) * 1000
                trace["success"] = success
                if error:
                    trace["error"] = error
                break
    
    def record_metric(self, name: str, value: float) -> None:
        """Registra una métrica."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(value)
        
        # Mantener solo últimas 1000 mediciones
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_metric_summary(self, name: str) -> Optional[Dict[str, float]]:
        """Obtiene resumen de una métrica."""
        if name not in self.metrics or not self.metrics[name]:
            return None
        
        values = self.metrics[name]
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
            "p95": sorted(values)[int(len(values) * 0.95)] if len(values) > 1 else values[0],
            "p99": sorted(values)[int(len(values) * 0.99)] if len(values) > 1 else values[0]
        }
    
    def get_all_metrics(self) -> Dict[str, Dict[str, float]]:
        """Obtiene resumen de todas las métricas."""
        return {
            name: self.get_metric_summary(name)
            for name in self.metrics.keys()
        }


_global_observability = ObservabilityManager()


# ============================================================================
# ADAPTIVE RATE LIMITING
# ============================================================================

class AdaptiveRateLimiter:
    """Rate limiter adaptativo que ajusta delays basado en respuestas del API."""
    
    def __init__(self, initial_delay: float = 0.1, max_delay: float = 60.0):
        self.current_delay = initial_delay
        self.min_delay = 0.01
        self.max_delay = max_delay
        self.consecutive_429s = 0
        self.last_429_time = None
    
    def wait_if_needed(self) -> None:
        """Espera si es necesario basado en rate limiting."""
        if self.current_delay > self.min_delay:
            time.sleep(self.current_delay)
    
    def record_429(self) -> None:
        """Registra un error 429 y aumenta el delay."""
        self.consecutive_429s += 1
        self.last_429_time = time.time()
        # Aumentar delay exponencialmente
        self.current_delay = min(
            self.current_delay * 2.0,
            self.max_delay
        )
        logger.warning(f"Rate limit hit, aumentando delay a {self.current_delay:.2f}s")
    
    def record_success(self) -> None:
        """Registra una respuesta exitosa y reduce el delay gradualmente."""
        if self.consecutive_429s > 0:
            self.consecutive_429s = max(0, self.consecutive_429s - 1)
        
        # Reducir delay gradualmente si no hay 429s recientes
        if self.last_429_time is None or time.time() - self.last_429_time > 60:
            self.current_delay = max(
                self.min_delay,
                self.current_delay * 0.9  # Reducir 10% cada vez
            )
    
    def get_current_delay(self) -> float:
        """Obtiene el delay actual."""
        return self.current_delay


_global_rate_limiter = AdaptiveRateLimiter()


# ============================================================================
# WEBHOOK SUPPORT
# ============================================================================

@dataclass
class WebhookEvent:
    """Evento de webhook."""
    event_id: str
    event_type: str
    timestamp: float
    payload: Dict[str, Any]
    signature: Optional[str] = None
    
    def validate_signature(self, secret: str) -> bool:
        """Valida la firma del webhook."""
        if not self.signature or not HMAC_AVAILABLE:
            return False
        
        # Crear firma esperada
        payload_str = json.dumps(self.payload, sort_keys=True)
        expected_signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(self.signature, expected_signature)


def process_stripe_webhook_event(
    webhook_event: WebhookEvent,
    secret: Optional[str] = None,
    quickbooks_client: Optional[Any] = None  # QuickBooksClient type
) -> Dict[str, Any]:
    """
    Procesa un evento de webhook de Stripe para sincronización automática.
    
    Args:
        webhook_event: Evento de webhook
        secret: Secret para validar firma (opcional)
        quickbooks_client: Cliente de QuickBooks (opcional)
    
    Returns:
        Dict con resultado del procesamiento
    """
    result = {
        "processed": False,
        "event_type": webhook_event.event_type,
        "timestamp": webhook_event.timestamp,
        "error": None
    }
    
    # Validar firma si se proporciona secret
    if secret:
        if not webhook_event.validate_signature(secret):
            result["error"] = "Invalid webhook signature"
            return result
    
    try:
        # Importar función principal (evitar circular import)
        from stripe_product_to_quickbooks_item import sync_stripe_product_to_quickbooks
        
        # Procesar eventos de producto
        if webhook_event.event_type in ("product.created", "product.updated"):
            payload = webhook_event.payload
            data = payload.get("data", {}).get("object", {})
            
            stripe_product_id = data.get("id")
            nombre_producto = data.get("name")
            
            # Obtener precio del primer price
            prices = data.get("prices", [])
            precio = 0.0
            if prices and len(prices) > 0:
                precio = prices[0].get("unit_amount", 0) / 100.0  # Convertir de centavos
            
            if stripe_product_id and nombre_producto and precio > 0:
                sync_result = sync_stripe_product_to_quickbooks(
                    stripe_product_id=stripe_product_id,
                    nombre_producto=nombre_producto,
                    precio=precio,
                    quickbooks_client=quickbooks_client
                )
                
                result["processed"] = sync_result.success
                result["sync_result"] = sync_result.to_dict()
                result["qb_item_id"] = sync_result.qb_item_id
            else:
                result["error"] = "Missing required product data"
        
        elif webhook_event.event_type == "product.deleted":
            # Manejar eliminación (solo registrar, no eliminar de QB por seguridad)
            logger.info(f"Producto eliminado en Stripe: {webhook_event.payload.get('data', {}).get('object', {}).get('id')}")
            result["processed"] = True
            result["action"] = "logged_only"
        else:
            result["error"] = f"Unsupported event type: {webhook_event.event_type}"
    
    except Exception as e:
        logger.exception(f"Error procesando webhook: {str(e)}")
        result["error"] = str(e)
    
    return result


# ============================================================================
# ENHANCED HEALTH CHECK
# ============================================================================

def get_enhanced_health_check(
    quickbooks_client: Optional[Any] = None,  # QuickBooksClient type
    include_metrics: bool = True,
    include_events: bool = True
) -> Dict[str, Any]:
    """
    Health check mejorado que incluye métricas, eventos y estado del sistema.
    
    Args:
        quickbooks_client: Cliente de QuickBooks (opcional)
        include_metrics: Si incluir métricas de observabilidad
        include_events: Si incluir estadísticas de eventos
    
    Returns:
        Dict con estado completo del sistema
    """
    health = {
        "status": "ok",
        "timestamp": time.time(),
        "checks": {},
        "warnings": [],
        "errors": []
    }
    
    # Health check básico de QuickBooks
    if quickbooks_client:
        try:
            qb_health = quickbooks_client.health_check()
            health["checks"]["quickbooks"] = qb_health
            if qb_health.get("status") != "ok":
                health["status"] = "degraded"
                health["warnings"].append("QuickBooks health check failed")
        except Exception as e:
            health["checks"]["quickbooks"] = {"status": "error", "error": str(e)}
            health["status"] = "error"
            health["errors"].append(f"QuickBooks health check error: {str(e)}")
    
    # Métricas de observabilidad
    if include_metrics:
        try:
            metrics = _global_observability.get_all_metrics()
            health["checks"]["observability"] = {
                "status": "ok",
                "metrics_count": len(metrics),
                "metrics": metrics
            }
        except Exception as e:
            health["checks"]["observability"] = {"status": "warning", "error": str(e)}
            health["warnings"].append(f"Observability error: {str(e)}")
    
    # Estadísticas de eventos
    if include_events:
        try:
            event_stats = _global_event_store.get_event_statistics()
            health["checks"]["events"] = {
                "status": "ok",
                **event_stats
            }
        except Exception as e:
            health["checks"]["events"] = {"status": "warning", "error": str(e)}
            health["warnings"].append(f"Event store error: {str(e)}")
    
    # Rate limiter status
    try:
        health["checks"]["rate_limiter"] = {
            "status": "ok",
            "current_delay": _global_rate_limiter.get_current_delay(),
            "consecutive_429s": _global_rate_limiter.consecutive_429s
        }
    except Exception as e:
        health["checks"]["rate_limiter"] = {"status": "warning", "error": str(e)}
    
    # Idempotency store status
    try:
        idempotency_count = len(_global_idempotency_store.keys)
        health["checks"]["idempotency"] = {
            "status": "ok",
            "active_keys": idempotency_count
        }
    except Exception as e:
        health["checks"]["idempotency"] = {"status": "warning", "error": str(e)}
    
    return health


# ============================================================================
# STREAMING BATCH PROCESSING
# ============================================================================

def stream_sync_products(
    products_generator: Union[List[Dict[str, Any]], Any],  # Iterator o lista
    quickbooks_client: Optional[Any] = None,
    batch_size: int = 100,
    max_workers: int = 5,
    callback: Optional[Callable] = None
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Procesa productos en streams para manejar grandes volúmenes sin cargar todo en memoria.
    
    Args:
        products_generator: Generador o lista de productos
        quickbooks_client: Cliente de QuickBooks
        batch_size: Tamaño de batch para procesamiento
        max_workers: Workers concurrentes
        callback: Función callback para cada batch procesado
    
    Yields:
        Dict con resultado de cada batch
    """
    from stripe_product_to_quickbooks_item import sync_stripe_products_batch
    
    if not hasattr(products_generator, '__iter__'):
        products_generator = iter(products_generator)
    
    batch = []
    batch_number = 0
    
    for product in products_generator:
        batch.append(product)
        
        if len(batch) >= batch_size:
            batch_number += 1
            logger.info(f"Procesando batch {batch_number} con {len(batch)} productos")
            
            try:
                result = sync_stripe_products_batch(
                    products=batch,
                    quickbooks_client=quickbooks_client,
                    max_workers=max_workers
                )
                
                batch_result = {
                    "batch_number": batch_number,
                    "total": result.total,
                    "successful": result.successful,
                    "failed": result.failed,
                    "success_rate": result.success_rate,
                    "duration_ms": result.duration_ms,
                    "timestamp": time.time()
                }
                
                if callback:
                    callback(batch_result)
                
                yield batch_result
                
            except Exception as e:
                logger.exception(f"Error procesando batch {batch_number}: {str(e)}")
                yield {
                    "batch_number": batch_number,
                    "error": str(e),
                    "timestamp": time.time()
                }
            
            batch = []
    
    # Procesar último batch si hay elementos restantes
    if batch:
        batch_number += 1
        logger.info(f"Procesando batch final {batch_number} con {len(batch)} productos")
        
        try:
            result = sync_stripe_products_batch(
                products=batch,
                quickbooks_client=quickbooks_client,
                max_workers=max_workers
            )
            
            batch_result = {
                "batch_number": batch_number,
                "total": result.total,
                "successful": result.successful,
                "failed": result.failed,
                "success_rate": result.success_rate,
                "duration_ms": result.duration_ms,
                "timestamp": time.time()
            }
            
            if callback:
                callback(batch_result)
            
            yield batch_result
            
        except Exception as e:
            logger.exception(f"Error procesando batch final {batch_number}: {str(e)}")
            yield {
                "batch_number": batch_number,
                "error": str(e),
                "timestamp": time.time()
            }


# ============================================================================
# INTELLIGENT CACHE WITH AUTO-INVALIDATION
# ============================================================================

class IntelligentCache:
    """Cache inteligente con invalidación automática basada en tiempo y eventos."""
    
    def __init__(self, default_ttl: int = 3600, max_size: int = 1000):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.access_times: Dict[str, float] = {}
        self.invalidation_callbacks: Dict[str, List[Callable]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Verificar TTL
        if time.time() - entry["timestamp"] > entry.get("ttl", self.default_ttl):
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        self.access_times[key] = time.time()
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena un valor en el cache."""
        # Limpiar si excede tamaño máximo (LRU)
        if len(self.cache) >= self.max_size and key not in self.cache:
            # Eliminar menos recientemente usado
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = {
            "value": value,
            "timestamp": time.time(),
            "ttl": ttl or self.default_ttl
        }
        self.access_times[key] = time.time()
    
    def invalidate(self, key: str) -> None:
        """Invalida una key específica."""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            
            # Ejecutar callbacks de invalidación
            if key in self.invalidation_callbacks:
                for callback in self.invalidation_callbacks[key]:
                    try:
                        callback(key)
                    except Exception as e:
                        logger.warning(f"Error en callback de invalidación: {str(e)}")
    
    def invalidate_pattern(self, pattern: str) -> None:
        """Invalida todas las keys que coincidan con el patrón."""
        import re
        regex = re.compile(pattern)
        keys_to_invalidate = [k for k in self.cache.keys() if regex.match(k)]
        for key in keys_to_invalidate:
            self.invalidate(key)
    
    def clear(self) -> None:
        """Limpia todo el cache."""
        self.cache.clear()
        self.access_times.clear()
    
    def register_invalidation_callback(self, key: str, callback: Callable) -> None:
        """Registra un callback para cuando una key se invalide."""
        if key not in self.invalidation_callbacks:
            self.invalidation_callbacks[key] = []
        self.invalidation_callbacks[key].append(callback)
    
    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": None,  # Requeriría tracking de hits/misses
            "keys": list(self.cache.keys())[:10]  # Primeras 10 keys como muestra
        }


_global_intelligent_cache = IntelligentCache()


# ============================================================================
# METRICS EXPORT (PROMETHEUS/STATSD)
# ============================================================================

class MetricsExporter:
    """Exportador de métricas a Prometheus, StatsD, etc."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.exporters: List[Callable] = []
    
    def register_exporter(self, exporter_func: Callable) -> None:
        """Registra una función exportadora."""
        self.exporters.append(exporter_func)
    
    def export_prometheus_format(self) -> str:
        """Exporta métricas en formato Prometheus."""
        lines = []
        
        for metric_name, metric_data in _global_observability.get_all_metrics().items():
            if metric_data:
                # Gauge
                lines.append(f"# TYPE {metric_name} gauge")
                lines.append(f"{metric_name} {metric_data['mean']}")
                
                # Histogram buckets
                if 'p95' in metric_data and 'p99' in metric_data:
                    lines.append(f"{metric_name}_p95 {metric_data['p95']}")
                    lines.append(f"{metric_name}_p99 {metric_data['p99']}")
        
        return "\n".join(lines)
    
    def export_statsd_format(self) -> List[str]:
        """Exporta métricas en formato StatsD."""
        lines = []
        
        for metric_name, metric_data in _global_observability.get_all_metrics().items():
            if metric_data:
                lines.append(f"{metric_name}:{metric_data['mean']}|g")
                if 'count' in metric_data:
                    lines.append(f"{metric_name}_count:{metric_data['count']}|c")
        
        return lines
    
    def export_json(self) -> Dict[str, Any]:
        """Exporta métricas en formato JSON."""
        return {
            "timestamp": time.time(),
            "metrics": _global_observability.get_all_metrics()
        }
    
    def auto_export(self) -> None:
        """Ejecuta todos los exportadores registrados."""
        for exporter in self.exporters:
            try:
                exporter(self.export_json())
            except Exception as e:
                logger.warning(f"Error en exportador: {str(e)}")


_global_metrics_exporter = MetricsExporter()


# ============================================================================
# DISTRIBUTED TRACING (OpenTelemetry-compatible)
# ============================================================================

class DistributedTracer:
    """Tracer distribuido compatible con OpenTelemetry."""
    
    def __init__(self):
        self.spans: List[Dict[str, Any]] = []
        self.trace_context: Optional[Dict[str, str]] = None
    
    def start_span(
        self,
        name: str,
        parent_span_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> str:
        """Inicia un span de tracing."""
        span_id = str(uuid.uuid4()) if UUID_AVAILABLE else f"span_{int(time.time() * 1000)}"
        
        if not trace_id:
            trace_id = str(uuid.uuid4()) if UUID_AVAILABLE else f"trace_{int(time.time() * 1000)}"
        
        span = {
            "span_id": span_id,
            "trace_id": trace_id,
            "parent_span_id": parent_span_id,
            "name": name,
            "start_time": time.time(),
            "start_time_ns": time.time_ns(),
            "attributes": attributes or {},
            "events": [],
            "status": "ok"
        }
        
        self.spans.append(span)
        return span_id
    
    def end_span(
        self,
        span_id: str,
        status: str = "ok",
        error: Optional[str] = None
    ) -> None:
        """Finaliza un span."""
        for span in self.spans:
            if span["span_id"] == span_id:
                span["end_time"] = time.time()
                span["end_time_ns"] = time.time_ns()
                span["duration_ms"] = (span["end_time"] - span["start_time"]) * 1000
                span["status"] = status
                if error:
                    span["error"] = error
                    span["events"].append({
                        "name": "error",
                        "timestamp": time.time(),
                        "attributes": {"error": error}
                    })
                break
    
    def add_event(
        self,
        span_id: str,
        event_name: str,
        attributes: Optional[Dict[str, Any]] = None
    ) -> None:
        """Agrega un evento a un span."""
        for span in self.spans:
            if span["span_id"] == span_id:
                span["events"].append({
                    "name": event_name,
                    "timestamp": time.time(),
                    "attributes": attributes or {}
                })
                break
    
    def set_attribute(
        self,
        span_id: str,
        key: str,
        value: Any
    ) -> None:
        """Establece un atributo en un span."""
        for span in self.spans:
            if span["span_id"] == span_id:
                span["attributes"][key] = value
                break
    
    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Obtiene todos los spans de un trace."""
        return [s for s in self.spans if s["trace_id"] == trace_id]
    
    def export_trace(self, trace_id: str) -> Dict[str, Any]:
        """Exporta un trace completo en formato OpenTelemetry."""
        spans = self.get_trace(trace_id)
        return {
            "trace_id": trace_id,
            "spans": spans,
            "total_spans": len(spans),
            "duration_ms": (
                max(s.get("end_time", time.time()) for s in spans) -
                min(s.get("start_time", time.time()) for s in spans)
            ) * 1000 if spans else 0
        }


_global_tracer = DistributedTracer()


# ============================================================================
# JSON SCHEMA VALIDATION
# ============================================================================

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


def validate_product_schema(product: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """Valida un producto contra un JSON Schema."""
    if not JSONSCHEMA_AVAILABLE:
        # Validación básica sin jsonschema
        if not isinstance(product, dict):
            return False, "Product must be a dictionary"
        if "stripe_product_id" not in product:
            return False, "Missing required field: stripe_product_id"
        if "nombre_producto" not in product:
            return False, "Missing required field: nombre_producto"
        if "precio" not in product:
            return False, "Missing required field: precio"
        return True, None
    
    schema = {
        "type": "object",
        "required": ["stripe_product_id", "nombre_producto", "precio"],
        "properties": {
            "stripe_product_id": {
                "type": "string",
                "minLength": 1,
                "maxLength": 255,
                "pattern": "^prod_"
            },
            "nombre_producto": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100
            },
            "precio": {
                "type": "number",
                "minimum": 0
            },
            "income_account": {
                "type": "string",
                "maxLength": 100
            }
        },
        "additionalProperties": True
    }
    
    try:
        jsonschema.validate(instance=product, schema=schema)
        return True, None
    except jsonschema.ValidationError as e:
        return False, f"Validation error: {str(e)}"


# ============================================================================
# ADVANCED RETRY STRATEGIES
# ============================================================================

class RetryStrategy:
    """Estrategias avanzadas de retry con diferentes backoff policies."""
    
    @staticmethod
    def exponential_backoff(
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0
    ) -> float:
        """Backoff exponencial."""
        delay = base_delay * (exponential_base ** attempt)
        return min(delay, max_delay)
    
    @staticmethod
    def linear_backoff(
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        increment: float = 1.0
    ) -> float:
        """Backoff lineal."""
        delay = base_delay + (increment * attempt)
        return min(delay, max_delay)
    
    @staticmethod
    def fibonacci_backoff(
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 60.0
    ) -> float:
        """Backoff usando secuencia de Fibonacci."""
        def fib(n):
            if n <= 1:
                return n
            a, b = 0, 1
            for _ in range(n):
                a, b = b, a + b
            return a
        
        delay = base_delay * fib(attempt + 1)
        return min(delay, max_delay)
    
    @staticmethod
    def jittered_backoff(
        attempt: int,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter_factor: float = 0.1,
        strategy: str = "exponential"
    ) -> float:
        """Backoff con jitter aleatorio."""
        import random
        
        if strategy == "exponential":
            delay = RetryStrategy.exponential_backoff(attempt, base_delay, max_delay)
        elif strategy == "linear":
            delay = RetryStrategy.linear_backoff(attempt, base_delay, max_delay)
        else:
            delay = base_delay
        
        jitter = delay * jitter_factor * random.uniform(-1, 1)
        return min(max(delay + jitter, 0), max_delay)


def retry_with_strategy(
    func: Callable,
    max_attempts: int = 3,
    strategy: str = "exponential",
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    retry_on_exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> Any:
    """
    Ejecuta una función con estrategia de retry avanzada.
    
    Args:
        func: Función a ejecutar
        max_attempts: Número máximo de intentos
        strategy: Estrategia de backoff ('exponential', 'linear', 'fibonacci', 'jittered')
        base_delay: Delay base en segundos
        max_delay: Delay máximo en segundos
        retry_on_exceptions: Tupla de excepciones para retry
        *args, **kwargs: Argumentos para la función
    
    Returns:
        Resultado de la función
    
    Raises:
        Última excepción si todos los intentos fallan
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func(*args, **kwargs)
        except retry_on_exceptions as e:
            last_exception = e
            
            if attempt < max_attempts - 1:
                if strategy == "exponential":
                    delay = RetryStrategy.exponential_backoff(attempt, base_delay, max_delay)
                elif strategy == "linear":
                    delay = RetryStrategy.linear_backoff(attempt, base_delay, max_delay)
                elif strategy == "fibonacci":
                    delay = RetryStrategy.fibonacci_backoff(attempt, base_delay, max_delay)
                elif strategy == "jittered":
                    delay = RetryStrategy.jittered_backoff(attempt, base_delay, max_delay)
                else:
                    delay = base_delay
                
                logger.warning(
                    f"Intento {attempt + 1}/{max_attempts} falló, reintentando en {delay:.2f}s: {str(e)}"
                )
                time.sleep(delay)
            else:
                logger.error(f"Todos los intentos fallaron: {str(e)}")
    
    raise last_exception


# ============================================================================
# PERFORMANCE PROFILING
# ============================================================================

class PerformanceProfiler:
    """Profiler de performance para identificar bottlenecks."""
    
    def __init__(self):
        self.profiles: Dict[str, List[float]] = {}
        self.active_profiles: Dict[str, float] = {}
    
    def start_profile(self, operation: str) -> None:
        """Inicia el profiling de una operación."""
        self.active_profiles[operation] = time.time()
    
    def end_profile(self, operation: str) -> float:
        """Finaliza el profiling y retorna la duración."""
        if operation not in self.active_profiles:
            return 0.0
        
        duration = time.time() - self.active_profiles[operation]
        del self.active_profiles[operation]
        
        if operation not in self.profiles:
            self.profiles[operation] = []
        
        self.profiles[operation].append(duration)
        
        # Mantener solo últimas 1000 mediciones
        if len(self.profiles[operation]) > 1000:
            self.profiles[operation] = self.profiles[operation][-1000:]
        
        return duration
    
    def get_profile_summary(self, operation: str) -> Optional[Dict[str, float]]:
        """Obtiene resumen de profiling para una operación."""
        if operation not in self.profiles or not self.profiles[operation]:
            return None
        
        durations = self.profiles[operation]
        return {
            "count": len(durations),
            "total": sum(durations),
            "mean": sum(durations) / len(durations),
            "min": min(durations),
            "max": max(durations),
            "p95": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
            "p99": sorted(durations)[int(len(durations) * 0.99)] if len(durations) > 1 else durations[0]
        }
    
    def get_all_profiles(self) -> Dict[str, Dict[str, float]]:
        """Obtiene resumen de todas las operaciones perfiladas."""
        return {
            op: self.get_profile_summary(op)
            for op in self.profiles.keys()
        }
    
    def identify_bottlenecks(self, threshold_p95: float = 1.0) -> List[Dict[str, Any]]:
        """Identifica operaciones con p95 por encima del umbral."""
        bottlenecks = []
        
        for operation, summary in self.get_all_profiles().items():
            if summary and summary.get("p95", 0) > threshold_p95:
                bottlenecks.append({
                    "operation": operation,
                    "p95": summary["p95"],
                    "mean": summary["mean"],
                    "count": summary["count"]
                })
        
        return sorted(bottlenecks, key=lambda x: x["p95"], reverse=True)


_global_profiler = PerformanceProfiler()


# ============================================================================
# CONNECTION POOLING & AUTO-RECONNECTION
# ============================================================================

class ConnectionManager:
    """Gestor de conexiones con pooling y auto-reconexión."""
    
    def __init__(self, max_pool_size: int = 10, reconnect_attempts: int = 3):
        self.pool: List[Any] = []
        self.max_pool_size = max_pool_size
        self.reconnect_attempts = reconnect_attempts
        self.active_connections: Dict[str, Any] = {}
        self.last_error: Optional[str] = None
    
    def get_connection(self, connection_id: str, factory_func: Callable) -> Any:
        """Obtiene una conexión del pool o crea una nueva."""
        # Intentar reutilizar conexión existente
        if connection_id in self.active_connections:
            conn = self.active_connections[connection_id]
            # Verificar si la conexión sigue válida
            if self._is_connection_valid(conn):
                return conn
        
        # Crear nueva conexión
        if len(self.pool) < self.max_pool_size:
            try:
                conn = factory_func()
                self.active_connections[connection_id] = conn
                self.pool.append(conn)
                return conn
            except Exception as e:
                self.last_error = str(e)
                logger.error(f"Error creando conexión: {str(e)}")
                raise
        
        # Pool lleno, usar round-robin
        conn = self.pool[len(self.pool) % self.max_pool_size]
        return conn
    
    def _is_connection_valid(self, conn: Any) -> bool:
        """Verifica si una conexión es válida."""
        # Implementación básica - puede extenderse
        try:
            return conn is not None and hasattr(conn, '_session')
        except:
            return False
    
    def reconnect(self, connection_id: str, factory_func: Callable) -> Any:
        """Reconecta una conexión que falló."""
        for attempt in range(self.reconnect_attempts):
            try:
                # Limpiar conexión vieja
                if connection_id in self.active_connections:
                    old_conn = self.active_connections[connection_id]
                    try:
                        if hasattr(old_conn, 'close'):
                            old_conn.close()
                    except:
                        pass
                    del self.active_connections[connection_id]
                
                # Crear nueva conexión
                new_conn = factory_func()
                self.active_connections[connection_id] = new_conn
                logger.info(f"Reconexión exitosa en intento {attempt + 1}")
                return new_conn
                
            except Exception as e:
                logger.warning(f"Intento de reconexión {attempt + 1} falló: {str(e)}")
                if attempt < self.reconnect_attempts - 1:
                    time.sleep(RetryStrategy.exponential_backoff(attempt))
        
        raise Exception(f"No se pudo reconectar después de {self.reconnect_attempts} intentos")
    
    def close_all(self) -> None:
        """Cierra todas las conexiones."""
        for conn in self.pool:
            try:
                if hasattr(conn, 'close'):
                    conn.close()
            except:
                pass
        
        self.pool.clear()
        self.active_connections.clear()


_global_connection_manager = ConnectionManager()


# ============================================================================
# INTELLIGENT ALERTING SYSTEM
# ============================================================================

class IntelligentAlertSystem:
    """Sistema de alertas inteligentes con threshold adaptativo."""
    
    def __init__(self):
        self.alert_history: List[Dict[str, Any]] = []
        self.thresholds: Dict[str, float] = {
            "error_rate": 10.0,  # 10% de errores
            "duration_p95": 5000.0,  # 5 segundos
            "cache_miss_rate": 50.0,  # 50% miss rate
            "consecutive_failures": 5.0
        }
        self.alert_cooldown: Dict[str, float] = {}
        self.cooldown_seconds: int = 300  # 5 minutos
    
    def check_and_alert(
        self,
        metric_name: str,
        value: float,
        severity: Literal["info", "warning", "critical"] = "warning"
    ) -> bool:
        """
        Verifica si debe enviar una alerta y la envía si es necesario.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor actual
            severity: Severidad de la alerta
        
        Returns:
            True si se envió una alerta, False si no
        """
        threshold = self.thresholds.get(metric_name)
        if threshold is None:
            return False
        
        # Verificar cooldown
        last_alert_time = self.alert_cooldown.get(metric_name, 0)
        if time.time() - last_alert_time < self.cooldown_seconds:
            return False
        
        # Verificar si excede threshold
        should_alert = False
        if metric_name in ["error_rate", "cache_miss_rate"]:
            should_alert = value > threshold
        elif metric_name in ["duration_p95", "consecutive_failures"]:
            should_alert = value > threshold
        
        if should_alert:
            alert = {
                "metric_name": metric_name,
                "value": value,
                "threshold": threshold,
                "severity": severity,
                "timestamp": time.time()
            }
            self.alert_history.append(alert)
            self.alert_cooldown[metric_name] = time.time()
            
            # Enviar alerta
            self._send_alert(alert)
            return True
        
        return False
    
    def _send_alert(self, alert: Dict[str, Any]) -> None:
        """Envía una alerta (implementar según sistema de notificaciones)."""
        message = (
            f"⚠️ ALERTA {alert['severity'].upper()}: {alert['metric_name']}\n"
            f"Valor: {alert['value']:.2f} (Threshold: {alert['threshold']:.2f})\n"
            f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert['timestamp']))}"
        )
        logger.warning(message)
        # Aquí se podría integrar con Slack, email, etc.
    
    def adjust_threshold(self, metric_name: str, new_threshold: float) -> None:
        """Ajusta un threshold dinámicamente."""
        self.thresholds[metric_name] = new_threshold
        logger.info(f"Threshold ajustado para {metric_name}: {new_threshold}")


_global_alert_system = IntelligentAlertSystem()


# ============================================================================
# AUTO-SCALING WORKERS
# ============================================================================

class AutoScalingWorkerManager:
    """Gestor de workers con auto-scaling basado en carga."""
    
    def __init__(self, min_workers: int = 1, max_workers: int = 20):
        self.min_workers = min_workers
        self.max_workers = max_workers
        self.current_workers = min_workers
        self.performance_history: List[Dict[str, float]] = []
    
    def calculate_optimal_workers(
        self,
        queue_size: int,
        avg_processing_time: float,
        target_throughput: float = 10.0
    ) -> int:
        """
        Calcula el número óptimo de workers basado en carga.
        
        Args:
            queue_size: Tamaño de la cola pendiente
            avg_processing_time: Tiempo promedio de procesamiento (segundos)
            target_throughput: Throughput objetivo (items/segundo)
        
        Returns:
            Número óptimo de workers
        """
        if queue_size == 0:
            return self.min_workers
        
        # Calcular workers necesarios para el throughput objetivo
        items_per_worker_per_sec = 1.0 / avg_processing_time if avg_processing_time > 0 else 1.0
        workers_needed = max(
            self.min_workers,
            min(
                self.max_workers,
                int(queue_size / (target_throughput * avg_processing_time))
            )
        )
        
        # Ajustar basado en histórico
        if self.performance_history:
            recent_perf = self.performance_history[-5:]
            avg_recent_throughput = sum(p.get("throughput", 0) for p in recent_perf) / len(recent_perf)
            
            if avg_recent_throughput < target_throughput * 0.8:
                workers_needed = min(self.max_workers, int(workers_needed * 1.2))
            elif avg_recent_throughput > target_throughput * 1.2:
                workers_needed = max(self.min_workers, int(workers_needed * 0.9))
        
        self.current_workers = workers_needed
        return workers_needed
    
    def record_performance(
        self,
        items_processed: int,
        duration: float,
        workers_used: int
    ) -> None:
        """Registra performance de un batch."""
        throughput = items_processed / duration if duration > 0 else 0
        self.performance_history.append({
            "items_processed": items_processed,
            "duration": duration,
            "throughput": throughput,
            "workers_used": workers_used,
            "timestamp": time.time()
        })
        
        # Mantener solo últimas 100 mediciones
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]


_global_worker_manager = AutoScalingWorkerManager()


# ============================================================================
# ANOMALY DETECTION
# ============================================================================

class AnomalyDetector:
    """Detector de anomalías en performance y métricas."""
    
    def __init__(self):
        self.metric_history: Dict[str, List[float]] = {}
        self.z_score_threshold: float = 2.5
    
    def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        window_size: int = 100
    ) -> Optional[Dict[str, Any]]:
        """
        Detecta si un valor es anómalo usando Z-score.
        
        Args:
            metric_name: Nombre de la métrica
            value: Valor actual
            window_size: Tamaño de ventana para cálculo
        
        Returns:
            Dict con información de anomalía o None
        """
        if metric_name not in self.metric_history:
            self.metric_history[metric_name] = []
        
        history = self.metric_history[metric_name]
        
        # Agregar valor actual
        history.append(value)
        
        # Mantener solo ventana reciente
        if len(history) > window_size:
            history = history[-window_size:]
            self.metric_history[metric_name] = history
        
        # Necesitamos al menos 10 valores para calcular z-score
        if len(history) < 10:
            return None
        
        # Calcular media y desviación estándar
        mean = sum(history[:-1]) / len(history[:-1])
        variance = sum((x - mean) ** 2 for x in history[:-1]) / len(history[:-1])
        std_dev = variance ** 0.5 if variance > 0 else 1.0
        
        # Calcular z-score
        z_score = abs((value - mean) / std_dev) if std_dev > 0 else 0
        
        if z_score > self.z_score_threshold:
            return {
                "metric_name": metric_name,
                "value": value,
                "mean": mean,
                "std_dev": std_dev,
                "z_score": z_score,
                "is_anomaly": True,
                "timestamp": time.time()
            }
        
        return None
    
    def get_metric_stats(self, metric_name: str) -> Optional[Dict[str, float]]:
        """Obtiene estadísticas de una métrica."""
        if metric_name not in self.metric_history or not self.metric_history[metric_name]:
            return None
        
        values = self.metric_history[metric_name]
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance ** 0.5
        
        return {
            "count": len(values),
            "mean": mean,
            "std_dev": std_dev,
            "min": min(values),
            "max": max(values)
        }


_global_anomaly_detector = AnomalyDetector()


# ============================================================================
# ADAPTIVE BATCH SIZING
# ============================================================================

class AdaptiveBatchSizer:
    """Ajusta el tamaño de batch dinámicamente basado en performance."""
    
    def __init__(self, initial_size: int = 50, min_size: int = 10, max_size: int = 200):
        self.initial_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.current_size = initial_size
        self.performance_history: List[Dict[str, Any]] = []
    
    def calculate_optimal_size(
        self,
        success_rate: float,
        avg_duration: float,
        error_rate: float
    ) -> int:
        """
        Calcula el tamaño óptimo de batch basado en performance.
        
        Args:
            success_rate: Tasa de éxito (0-100)
            avg_duration: Duración promedio (ms)
            error_rate: Tasa de errores (0-100)
        
        Returns:
            Tamaño óptimo de batch
        """
        # Registrar performance
        self.performance_history.append({
            "batch_size": self.current_size,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "error_rate": error_rate,
            "timestamp": time.time()
        })
        
        # Mantener solo últimas 20 mediciones
        if len(self.performance_history) > 20:
            self.performance_history = self.performance_history[-20:]
        
        # Lógica de ajuste
        if error_rate > 5.0:
            # Reducir tamaño si hay muchos errores
            self.current_size = max(self.min_size, int(self.current_size * 0.8))
        elif success_rate > 95.0 and avg_duration < 1000:
            # Aumentar tamaño si todo va bien
            self.current_size = min(self.max_size, int(self.current_size * 1.1))
        elif avg_duration > 5000:
            # Reducir si es muy lento
            self.current_size = max(self.min_size, int(self.current_size * 0.9))
        
        return int(self.current_size)
    
    def reset(self) -> None:
        """Resetea al tamaño inicial."""
        self.current_size = self.initial_size
        self.performance_history.clear()


_global_batch_sizer = AdaptiveBatchSizer()


# ============================================================================
# ENHANCED CIRCUIT BREAKER
# ============================================================================

class EnhancedCircuitBreaker:
    """Circuit breaker mejorado con health checks y recovery automático."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60
    ):
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.success_count = 0
        self.state: Literal["closed", "open", "half_open"] = "closed"
        self.last_failure_time: Optional[float] = None
        self.health_check_failures = 0
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Ejecuta una función con circuit breaker.
        
        Args:
            func: Función a ejecutar
            *args, **kwargs: Argumentos de la función
        
        Returns:
            Resultado de la función
        
        Raises:
            Exception: Si el circuit breaker está abierto o la función falla
        """
        # Verificar estado
        if self.state == "open":
            if self.last_failure_time and time.time() - self.last_failure_time > self.timeout:
                # Intentar recuperación
                self.state = "half_open"
                self.success_count = 0
                logger.info("Circuit breaker: intentando recuperación (half_open)")
            else:
                raise Exception("Circuit breaker is OPEN")
        
        # Ejecutar función
        try:
            result = func(*args, **kwargs)
            
            # Éxito
            if self.state == "half_open":
                self.success_count += 1
                if self.success_count >= self.success_threshold:
                    self.state = "closed"
                    self.failure_count = 0
                    logger.info("Circuit breaker: recuperado (closed)")
            elif self.state == "closed":
                self.failure_count = 0
            
            return result
        
        except Exception as e:
            # Falla
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.state == "half_open":
                self.state = "open"
                logger.warning("Circuit breaker: falla en recuperación, abriendo")
            elif self.state == "closed" and self.failure_count >= self.failure_threshold:
                self.state = "open"
                logger.warning(f"Circuit breaker: abierto después de {self.failure_count} fallos")
            
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Realiza un health check del circuit breaker."""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "is_healthy": self.state in ["closed", "half_open"]
        }
    
    def reset(self) -> None:
        """Resetea el circuit breaker manualmente."""
        self.state = "closed"
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        logger.info("Circuit breaker: reseteado manualmente")


_global_circuit_breaker = EnhancedCircuitBreaker()


# ============================================================================
# DATA COMPRESSION FOR BATCHES
# ============================================================================

def compress_batch_data(data: List[Dict[str, Any]]) -> bytes:
    """
    Comprime datos de batch para reducir uso de memoria.
    
    Args:
        data: Lista de diccionarios a comprimir
    
    Returns:
        Datos comprimidos como bytes
    """
    try:
        import json
        import gzip
        
        json_str = json.dumps(data, default=str)
        compressed = gzip.compress(json_str.encode('utf-8'))
        return compressed
    except ImportError:
        # Si gzip no está disponible, retornar sin comprimir
        import json
        return json.dumps(data, default=str).encode('utf-8')


def decompress_batch_data(compressed_data: bytes) -> List[Dict[str, Any]]:
    """
    Descomprime datos de batch.
    
    Args:
        compressed_data: Datos comprimidos
    
    Returns:
        Lista de diccionarios descomprimidos
    """
    try:
        import json
        import gzip
        
        decompressed = gzip.decompress(compressed_data)
        return json.loads(decompressed.decode('utf-8'))
    except ImportError:
        # Si gzip no está disponible, descomprimir JSON simple
        import json
        return json.loads(compressed_data.decode('utf-8'))


# ============================================================================
# REAL-TIME METRICS DASHBOARD
# ============================================================================

class MetricsDashboard:
    """Dashboard de métricas en tiempo real."""
    
    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.last_update: float = 0.0
    
    def update_metric(self, name: str, value: Any) -> None:
        """Actualiza una métrica."""
        self.metrics[name] = {
            "value": value,
            "timestamp": time.time(),
            "updated": True
        }
        self.last_update = time.time()
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obtiene datos completos para dashboard."""
        return {
            "timestamp": time.time(),
            "last_update": self.last_update,
            "metrics": self.metrics,
            "cache_stats": _global_cache_stats.get_stats() if '_global_cache_stats' in globals() else {},
            "alert_system": {
                "active_alerts": len([a for a in _global_alert_system.alert_history 
                                    if time.time() - a["timestamp"] < 3600]) 
                if '_global_alert_system' in globals() else 0
            },
            "circuit_breaker": _global_circuit_breaker.health_check() if '_global_circuit_breaker' in globals() else {},
            "anomalies": self._get_recent_anomalies()
        }
    
    def _get_recent_anomalies(self) -> List[Dict[str, Any]]:
        """Obtiene anomalías recientes."""
        if '_global_anomaly_detector' not in globals():
            return []
        
        # Retornar métricas con z-score alto
        anomalies = []
        for metric_name, values in _global_anomaly_detector.metric_history.items():
            if len(values) >= 10:
                recent_value = values[-1]
                anomaly = _global_anomaly_detector.detect_anomaly(metric_name, recent_value)
                if anomaly:
                    anomalies.append(anomaly)
        
        return anomalies[-10:]  # Últimas 10 anomalías


_global_dashboard = MetricsDashboard()

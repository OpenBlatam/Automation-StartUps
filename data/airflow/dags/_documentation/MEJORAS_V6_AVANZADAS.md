# Mejoras Avanzadas V6 - Stripe Product to QuickBooks Item Sync

## 📋 Resumen

Este documento describe las mejoras avanzadas V6 agregadas al sistema de sincronización de productos Stripe a QuickBooks. Las mejoras incluyen soporte async, event sourcing, observabilidad avanzada, webhooks, y más.

## 🚀 Nuevas Funcionalidades

### 1. Event Sourcing y Audit Trail

**Ubicación**: `stripe_product_to_quickbooks_item_v6_improvements.py`

- **`SyncEvent`**: Clase dataclass para representar eventos de sincronización
- **`EventStore`**: Almacén de eventos con capacidades de filtrado y estadísticas
- **Funcionalidades**:
  - Tracking completo de todas las operaciones de sincronización
  - Filtrado por tipo de evento, producto, fecha
  - Estadísticas agregadas de eventos
  - Historial completo para auditoría

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    _global_event_store,
    create_sync_event
)

# Los eventos se crean automáticamente durante sincronizaciones
# Consultar eventos:
eventos = _global_event_store.get_events(
    event_type="sync_completed",
    since=time.time() - 86400,  # Últimas 24 horas
    limit=100
)

# Obtener estadísticas:
stats = _global_event_store.get_event_statistics()
print(f"Total eventos: {stats['total']}")
```

### 2. Idempotency Support

**Clase**: `IdempotencyStore`

- Almacena resultados de operaciones con keys de idempotencia
- Evita procesamiento duplicado de la misma operación
- TTL configurable (default: 24 horas)
- Limpieza automática de keys expiradas

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    generate_idempotency_key,
    _global_idempotency_store
)

# Generar key
key = generate_idempotency_key("prod_123", 99.99, "sync")

# Verificar si ya existe
cached = _global_idempotency_store.check_key(key)
if cached:
    print("Operación ya procesada")
```

### 3. Enhanced Observability

**Clase**: `ObservabilityManager`

- **Tracing**: Seguimiento de operaciones con trazas completas
- **Métricas**: Recopilación de métricas con estadísticas (mean, min, max, p95, p99)
- **Logging estructurado**: Logs con contexto completo

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_observability

# Iniciar trace
trace_id = _global_observability.start_trace(
    "sync_batch",
    metadata={"product_count": 100}
)

# Registrar métrica
_global_observability.record_metric("sync.duration_ms", 250.5)

# Finalizar trace
_global_observability.end_trace(trace_id, success=True)

# Obtener resumen de métricas
metrics = _global_observability.get_all_metrics()
print(metrics["sync.duration_ms"])  # {'count': 10, 'mean': 250.5, ...}
```

### 4. Adaptive Rate Limiting

**Clase**: `AdaptiveRateLimiter`

- Ajuste automático de delays basado en respuestas del API
- Manejo inteligente de errores 429 (rate limit)
- Reducción gradual de delays cuando no hay problemas
- Aumento exponencial cuando se detectan rate limits

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_rate_limiter

# Esperar si es necesario (se ajusta automáticamente)
_global_rate_limiter.wait_if_needed()

# Registrar respuesta
if response.status_code == 429:
    _global_rate_limiter.record_429()
else:
    _global_rate_limiter.record_success()
```

### 5. Webhook Support

**Clase**: `WebhookEvent`

- Validación de firmas HMAC
- Procesamiento automático de eventos de Stripe
- Sincronización en tiempo real basada en webhooks

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    WebhookEvent,
    process_stripe_webhook_event
)

# Crear evento desde payload de Stripe
webhook_event = WebhookEvent(
    event_id=stripe_event["id"],
    event_type=stripe_event["type"],
    timestamp=stripe_event["created"],
    payload=stripe_event,
    signature=request.headers.get("Stripe-Signature")
)

# Procesar webhook
result = process_stripe_webhook_event(
    webhook_event,
    secret=os.environ.get("STRIPE_WEBHOOK_SECRET"),
    quickbooks_client=client
)

if result["processed"]:
    print(f"Producto sincronizado: {result['qb_item_id']}")
```

### 6. Enhanced Health Check

**Función**: `get_enhanced_health_check()`

- Health check completo del sistema
- Incluye estado de QuickBooks, observabilidad, eventos, rate limiter, idempotency
- Diagnóstico completo con warnings y errors

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import get_enhanced_health_check

health = get_enhanced_health_check(
    quickbooks_client=client,
    include_metrics=True,
    include_events=True
)

print(f"Status: {health['status']}")
print(f"Warnings: {health['warnings']}")
print(f"Errors: {health['errors']}")

# Verificar componentes específicos
if health["checks"]["rate_limiter"]["consecutive_429s"] > 5:
    print("⚠️ Muchos rate limits detectados")
```

## 📦 Integración

### Opción 1: Importar desde módulo separado

```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    get_enhanced_health_check,
    process_stripe_webhook_event,
    _global_observability,
    _global_event_store
)

# Usar las funciones directamente
health = get_enhanced_health_check(quickbooks_client)
```

### Opción 2: Copiar código al archivo principal

El código está diseñado para ser autocontenido y puede copiarse directamente al archivo principal `stripe_product_to_quickbooks_item.py`.

## 🔧 Configuración

### Variables de Entorno

No se requieren variables de entorno adicionales. Las mejoras funcionan con la configuración existente.

### Dependencias Opcionales

- `asyncio`: Para soporte async (incluido en Python 3.7+)
- `uuid`: Para generación de IDs únicos (incluido en stdlib)
- `hmac`, `hashlib`: Para validación de webhooks (incluido en stdlib)

## 📊 Métricas Disponibles

Las siguientes métricas pueden ser registradas usando `ObservabilityManager`:

- `sync.duration_ms`: Duración de sincronizaciones
- `sync.batch.duration_ms`: Duración de batches
- `sync.errors`: Contador de errores
- `sync.success_rate`: Tasa de éxito
- `rate_limiter.delay`: Delay actual del rate limiter
- `rate_limiter.429_count`: Contador de errores 429

## 🔍 Eventos Disponibles

Los siguientes tipos de eventos se registran automáticamente:

- `sync_started`: Sincronización iniciada
- `sync_completed`: Sincronización completada exitosamente
- `sync_failed`: Sincronización falló
- `item_created`: Ítem creado en QuickBooks
- `item_updated`: Ítem actualizado en QuickBooks
- `rate_limited`: Rate limit detectado

## 🎯 Próximos Pasos

1. **Integrar código al archivo principal**: Copiar funciones al archivo principal si se prefiere tener todo en un solo lugar
2. **Configurar webhooks**: Configurar webhook endpoint en Stripe para sincronización en tiempo real
3. **Implementar async batch**: Usar `sync_stripe_products_batch_async` para mejor rendimiento
4. **Monitorear eventos**: Configurar alertas basadas en eventos del EventStore
5. **Exportar métricas**: Integrar con sistema de métricas (Prometheus, Datadog, etc.)

## 📝 Notas

- El EventStore mantiene un máximo de 10,000 eventos en memoria por defecto
- Las keys de idempotencia expiran después de 24 horas
- El rate limiter se ajusta automáticamente pero puede configurarse manualmente
- Los webhooks requieren validación de firma para seguridad

## 🐛 Troubleshooting

### EventStore no registra eventos
- Verificar que `create_sync_event()` se llama durante sincronizaciones
- Revisar que el límite de eventos no se haya alcanzado

### Rate limiter muy agresivo
- Ajustar `initial_delay` y `max_delay` en `AdaptiveRateLimiter`
- Verificar que `record_success()` se llama después de operaciones exitosas

### Webhooks no procesan
- Verificar que la firma sea correcta
- Revisar logs para errores de validación
- Confirmar que el tipo de evento está soportado

---

## 🚀 Funcionalidades Adicionales V6.1

### 9. Streaming Batch Processing

**Función**: `stream_sync_products()`

- Procesa grandes volúmenes sin cargar todo en memoria
- Procesamiento por batches con generadores
- Callbacks opcionales para cada batch
- Manejo de errores por batch

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import stream_sync_products

def products_generator():
    # Generar productos desde base de datos, API, etc.
    for i in range(10000):
        yield {
            "stripe_product_id": f"prod_{i}",
            "nombre_producto": f"Producto {i}",
            "precio": 99.99
        }

def callback(batch_result):
    print(f"Batch {batch_result['batch_number']}: {batch_result['success_rate']:.2f}% éxito")

# Procesar en streams
for batch_result in stream_sync_products(
    products_generator(),
    batch_size=100,
    max_workers=5,
    callback=callback
):
    print(f"Procesado: {batch_result}")
```

### 10. Intelligent Cache with Auto-Invalidation

**Clase**: `IntelligentCache`

- Cache con TTL configurable
- Invalidación automática por tiempo
- Invalidación por patrón (regex)
- Callbacks de invalidación
- LRU eviction cuando el cache está lleno

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_intelligent_cache

# Almacenar en cache
_global_intelligent_cache.set("item:prod_123", item_data, ttl=3600)

# Obtener del cache
cached = _global_intelligent_cache.get("item:prod_123")

# Invalidar por patrón
_global_intelligent_cache.invalidate_pattern(r"item:prod_.*")

# Registrar callback
def on_invalidate(key):
    print(f"Cache invalidado: {key}")

_global_intelligent_cache.register_invalidation_callback("item:prod_123", on_invalidate)
```

### 11. Metrics Export (Prometheus/StatsD)

**Clase**: `MetricsExporter`

- Exporta métricas en formato Prometheus
- Exporta métricas en formato StatsD
- Exporta métricas en JSON
- Sistema de exportadores personalizados

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_metrics_exporter

# Exportar a Prometheus
prometheus_text = _global_metrics_exporter.export_prometheus_format()
print(prometheus_text)

# Exportar a StatsD
statsd_lines = _global_metrics_exporter.export_statsd_format()
for line in statsd_lines:
    print(line)

# Exportar JSON
json_metrics = _global_metrics_exporter.export_json()

# Registrar exportador personalizado
def custom_exporter(metrics_json):
    # Enviar a tu sistema de métricas
    send_to_custom_backend(metrics_json)

_global_metrics_exporter.register_exporter(custom_exporter)
_global_metrics_exporter.auto_export()  # Ejecuta todos los exportadores
```

### 12. Distributed Tracing (OpenTelemetry-compatible)

**Clase**: `DistributedTracer`

- Traces distribuidos compatible con OpenTelemetry
- Spans con atributos y eventos
- Exportación de traces completos
- Soporte para trace context

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_tracer

# Iniciar trace
trace_id = _global_tracer.start_span("sync_batch", attributes={"batch_size": 100})

# Crear span hijo
span_id = _global_tracer.start_span(
    "sync_product",
    parent_span_id=trace_id,
    trace_id=trace_id,
    attributes={"product_id": "prod_123"}
)

# Agregar evento
_global_tracer.add_event(span_id, "product_found", {"qb_item_id": "123"})

# Establecer atributo
_global_tracer.set_attribute(span_id, "price", 99.99)

# Finalizar spans
_global_tracer.end_span(span_id, status="ok")
_global_tracer.end_span(trace_id, status="ok")

# Exportar trace
trace_data = _global_tracer.export_trace(trace_id)
```

### 13. JSON Schema Validation

**Función**: `validate_product_schema()`

- Validación robusta contra JSON Schema
- Fallback a validación básica si jsonschema no está disponible
- Mensajes de error descriptivos

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import validate_product_schema

product = {
    "stripe_product_id": "prod_123",
    "nombre_producto": "Producto Test",
    "precio": 99.99
}

is_valid, error = validate_product_schema(product)
if not is_valid:
    print(f"Error de validación: {error}")
```

### 14. Advanced Retry Strategies

**Clase**: `RetryStrategy` y función `retry_with_strategy()`

- Backoff exponencial
- Backoff lineal
- Backoff con secuencia de Fibonacci
- Backoff con jitter aleatorio

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    retry_with_strategy,
    RetryStrategy
)

# Usar estrategia de retry
result = retry_with_strategy(
    sync_product_func,
    max_attempts=5,
    strategy="exponential",  # o "linear", "fibonacci", "jittered"
    base_delay=1.0,
    max_delay=60.0,
    retry_on_exceptions=(QuickBooksAPIError, requests.exceptions.RequestException),
    stripe_product_id="prod_123",
    nombre="Test",
    precio=99.99
)

# Calcular delay manualmente
delay = RetryStrategy.exponential_backoff(attempt=3, base_delay=1.0, max_delay=60.0)
```

### 15. Performance Profiling

**Clase**: `PerformanceProfiler`

- Profiling detallado de operaciones
- Estadísticas (mean, min, max, p95, p99)
- Identificación automática de bottlenecks

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_profiler

# Iniciar profiling
_global_profiler.start_profile("sync_product")

# ... ejecutar operación ...

# Finalizar profiling
duration = _global_profiler.end_profile("sync_product")

# Obtener resumen
summary = _global_profiler.get_profile_summary("sync_product")
print(f"Promedio: {summary['mean']:.2f}s, P95: {summary['p95']:.2f}s")

# Identificar bottlenecks
bottlenecks = _global_profiler.identify_bottlenecks(threshold_p95=1.0)
for bottleneck in bottlenecks:
    print(f"Bottleneck: {bottleneck['operation']} (p95: {bottleneck['p95']:.2f}s)")
```

### 16. Connection Pooling & Auto-Reconnection

**Clase**: `ConnectionManager`

- Pool de conexiones con tamaño máximo
- Auto-reconexión con retry
- Validación de conexiones
- Limpieza automática

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_connection_manager

# Obtener conexión del pool
def create_qb_client():
    return QuickBooksClient(config)

connection = _global_connection_manager.get_connection(
    "qb_main",
    create_qb_client
)

# Si falla, reconectar automáticamente
try:
    result = connection.find_item_by_name("Test")
except Exception:
    connection = _global_connection_manager.reconnect("qb_main", create_qb_client)

# Cerrar todas las conexiones
_global_connection_manager.close_all()
```

## 📊 Resumen de Todas las Funcionalidades

### V6.0 (Básicas)
1. ✅ Event Sourcing y Audit Trail
2. ✅ Idempotency Support
3. ✅ Enhanced Observability
4. ✅ Adaptive Rate Limiting
5. ✅ Webhook Support
6. ✅ Enhanced Health Check

### V6.1 (Avanzadas)
7. ✅ Streaming Batch Processing
8. ✅ Intelligent Cache with Auto-Invalidation
9. ✅ Metrics Export (Prometheus/StatsD)
10. ✅ Distributed Tracing (OpenTelemetry)
11. ✅ JSON Schema Validation
12. ✅ Advanced Retry Strategies
13. ✅ Performance Profiling
14. ✅ Connection Pooling & Auto-Reconnection

## 🎯 Casos de Uso Recomendados

### Para grandes volúmenes (>10,000 productos)
- Usar `stream_sync_products()` para procesamiento en streams
- Activar `PerformanceProfiler` para identificar bottlenecks
- Configurar `ConnectionManager` con pool adecuado

### Para alta disponibilidad
- Implementar `ConnectionManager` con auto-reconexión
- Usar `retry_with_strategy()` con jitter
- Configurar `AdaptiveRateLimiter` agresivo

### Para observabilidad completa
- Activar `DistributedTracer` para traces distribuidos
- Exportar métricas con `MetricsExporter`
- Usar `EventStore` para audit trail completo

### Para validación robusta
- Implementar `validate_product_schema()` en todos los inputs
- Usar `IdempotencyStore` para evitar duplicados
- Activar callbacks de invalidación en cache


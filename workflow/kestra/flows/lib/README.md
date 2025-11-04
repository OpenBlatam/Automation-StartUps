# Librerías para Workflows de Kestra

Este directorio contiene librerías Python reutilizables para workflows de Kestra, diseñadas para integrarse con APIs externas (HubSpot, ManyChat, etc.) con características avanzadas de resiliencia, observabilidad y performance.

## 📦 Módulos

### 1. `hubspot_client.py`
Cliente para la API de HubSpot con:
- ✅ Retry automático con exponential backoff
- ✅ Manejo de rate limiting (429)
- ✅ Circuit Breaker pattern (protección contra cascading failures)
- ✅ Caché para reducir llamadas repetidas
- ✅ Métricas Prometheus integradas
- ✅ Logging estructurado
- ✅ **Connection pooling avanzado** (httpx o requests con HTTPAdapter)
- ✅ **Configuración robusta** desde variables de entorno
- ✅ **Health checks** integrados
- ✅ **Context managers** para gestión de recursos

**Ejemplo de uso básico:**
```python
from lib.hubspot_client import HubSpotClient

# Carga configuración desde variables de entorno automáticamente
client = HubSpotClient()

# O con configuración explícita
client = HubSpotClient(api_token="your_token", timeout=30)

# Usar como context manager (cierra conexiones automáticamente)
with HubSpotClient() as client:
    result = client.get_contact("123", properties=["firstname", "email"])
    if result.success:
        contact_data = result.data
        print(f"Contact: {contact_data['properties']['firstname']}")
```

**Ejemplo con configuración desde entorno:**
```python
from lib.hubspot_client import HubSpotClient
from lib.config import HubSpotConfig

# Configurar desde variables de entorno
# HUBSPOT_TOKEN=xxx HUBSPOT_TIMEOUT=60 python script.py
config = HubSpotConfig.from_env()
client = HubSpotClient(config=config)
```

### 2. `manychat_client.py`
Cliente para la API de ManyChat con:
- ✅ Retry automático con exponential backoff
- ✅ Validación de mensajes
- ✅ Circuit Breaker pattern
- ✅ Métricas Prometheus integradas
- ✅ Logging estructurado
- ✅ **Connection pooling avanzado** (httpx o requests con HTTPAdapter)
- ✅ **Configuración robusta** desde variables de entorno
- ✅ **Health checks** integrados
- ✅ **Context managers** para gestión de recursos

**Ejemplo de uso básico:**
```python
from lib.manychat_client import ManyChatClient

# Carga configuración desde variables de entorno automáticamente
client = ManyChatClient()

# O con configuración explícita
client = ManyChatClient(api_key="your_key", page_id="your_page_id")

# Usar como context manager (cierra conexiones automáticamente)
with ManyChatClient() as client:
    result = client.send_message(
        subscriber_id="123456",
        message_text="Hola, gracias por tu interés!"
    )
    if result.success:
        print("Mensaje enviado exitosamente")
```

### 3. `webhook_validator.py`
Validación de firmas HMAC para webhooks (HubSpot, etc.).

**Ejemplo de uso:**
```python
from lib.webhook_validator import WebhookValidator

validator = WebhookValidator(secret="your_secret")
is_valid = validator.verify_hubspot_signature(
    raw_body=request_body,
    signature=headers.get("X-HubSpot-Signature-v2"),
    secret="your_secret"
)

if not is_valid:
    raise ValueError("Invalid webhook signature")
```

### 4. `circuit_breaker.py`
Implementación del patrón Circuit Breaker para proteger APIs externas.

**Características:**
- Estados: CLOSED (normal), OPEN (rechaza requests), HALF_OPEN (testing)
- Auto-recovery después de timeout
- Configuración de thresholds
- Logging estructurado

**Ejemplo de uso:**
```python
from lib.circuit_breaker import get_circuit_breaker, CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,
    timeout_seconds=60,
    expected_exception=requests.exceptions.RequestException
)
breaker = get_circuit_breaker("my_api", config)

# Proteger una función
result = breaker.call(my_api_function, arg1, arg2)
```

### 5. `cache.py`
Caché simple con TTL para reducir llamadas repetidas a APIs.

**Características:**
- TTL-based caching
- Key-based invalidation
- Auto-cleanup de entradas expiradas
- Estadísticas de hit/miss rate

**Ejemplo de uso:**
```python
from lib.cache import get_cache

cache = get_cache("my_cache", default_ttl=300)  # 5 minutos

# Obtener o calcular
value = cache.get_or_set(
    key="contact:123",
    func=lambda: expensive_api_call("123"),
    ttl=600  # 10 minutos
)

# Stats
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']}%")
```

### 6. `metrics.py`
Colector de métricas Prometheus para observabilidad.

**Características:**
- Exportación en formato Prometheus text/plain
- Soporte para Counter, Gauge, Histogram
- Labels para segmentación
- Exportación JSON opcional

**Ejemplo de uso:**
```python
from lib.metrics import get_metrics_collector

metrics = get_metrics_collector()

# Registrar métricas
metrics.start_timer("operation")
# ... operación ...
duration = metrics.record_duration("operation")

metrics.add_counter(
    "api_requests_total",
    value=1,
    labels={"operation": "send_message", "status": "success"}
)

# Exportar
prometheus_text = metrics.export_prometheus()
print(prometheus_text)
```

### 7. `health.py` ⭐ NUEVO
Health checks para APIs y servicios.

**Características:**
- Health checks estructurados
- Timeout configurable
- Validación de dependencias
- Resultados agregados

**Ejemplo de uso:**
```python
from lib.health import HealthChecker, create_api_health_check

# Health check individual
result = client.health_check()
print(result["status"])  # "healthy" | "unhealthy" | "degraded"

# Health checker agregado
checker = HealthChecker("my_service")
checker.register_check("hubspot", lambda: create_api_health_check(
    "HubSpot",
    lambda: hubspot_client.health_check()["status"] == "healthy"
))
checker.register_check("manychat", lambda: create_api_health_check(
    "ManyChat",
    lambda: manychat_client.health_check()["status"] == "healthy"
))

overall_health = checker.check()
print(overall_health.status)  # HealthStatus enum
```

### 8. `batch.py` ⭐ NUEVO
Procesamiento batch para operaciones en paralelo.

**Características:**
- Procesamiento paralelo con ThreadPoolExecutor
- Rate limiting por batch
- Retry automático
- Progress tracking
- Resultados agregados

**Ejemplo de uso:**
```python
from lib.batch import BatchProcessor

processor = BatchProcessor(max_workers=5, batch_delay=0.1)

# Procesar lista de contactos
contacts = [{"id": "1"}, {"id": "2"}, {"id": "3"}]

result = processor.process(
    items=contacts,
    process_func=lambda c: hubspot_client.get_contact(c["id"]),
    item_to_dict=lambda c: {"contact_id": c["id"]},
    result_to_dict=lambda r: {"success": r.success}
)

print(f"Success rate: {result.success_rate}%")
print(f"Successful: {result.successful}/{result.total}")
```

## 🚀 Instalación

Las dependencias están listadas en `requirements.txt`:

```bash
pip install -r lib/requirements.txt
```

**Dependencias principales:**
- `requests>=2.31.0` - HTTP client
- `tenacity>=8.2.3` - Retry automático

**Dependencias opcionales:**
- `pydantic>=2.0.0` - Validación de datos
- `httpx>=0.24.0` - HTTP client avanzado
- `cachetools>=5.3.0` - Cache tools

## 📊 Observabilidad

### Métricas Prometheus

Las librerías exportan automáticamente métricas Prometheus:

**HubSpot:**
- `hubspot_api_requests_total{operation="get_contact",status="success|error"}` - Contador de requests
- `hubspot_api_request_duration_seconds{operation="get_contact"}` - Histograma de duración

**ManyChat:**
- `manychat_api_requests_total{operation="send_message",status="success|error"}` - Contador de requests
- `manychat_api_request_duration_seconds{operation="send_message"}` - Histograma de duración

### Logging Estructurado

Todos los módulos usan logging estructurado con contexto:

```python
logger.info("Operation completed", extra={
    "contact_id": "123",
    "duration_ms": 150,
    "status": "success"
})
```

## 🧪 Testing

Tests unitarios están en `lib/tests/`:

```bash
# Ejecutar tests
pytest lib/tests/

# Con coverage
pytest lib/tests/ --cov=lib --cov-report=html
```

## 📝 Mejores Prácticas

1. **Usa circuit breakers** para APIs externas críticas
2. **Habilita caché** para datos que no cambian frecuentemente
3. **Registra métricas** para monitoreo y alertas
4. **Usa retry automático** con exponential backoff
5. **Valida webhooks** con HMAC antes de procesar
6. **Usa context managers** (`with` statement) para gestión automática de recursos
7. **Configura desde variables de entorno** para diferentes entornos (dev/staging/prod)
8. **Aprovecha connection pooling** instalando `httpx` para mejor performance

### 9. `config.py`
Configuración robusta con dataclasses y carga desde variables de entorno.

**Características:**
- ✅ Dataclasses tipadas para configuración
- ✅ Carga automática desde variables de entorno
- ✅ Validación de configuración
- ✅ Valores por defecto sensatos
- ✅ Soporte para múltiples entornos (production, staging, development, test)

**Ejemplo de uso:**
```python
from lib.config import HubSpotConfig, validate_config

# Cargar desde variables de entorno
config = HubSpotConfig.from_env()

# Validar configuración
validate_config(config)

# Usar en cliente
from lib.hubspot_client import HubSpotClient
client = HubSpotClient(config=config)
```

**Variables de entorno para HubSpot:**
```bash
HUBSPOT_TOKEN=xxx
HUBSPOT_BASE_URL=https://api.hubapi.com
HUBSPOT_TIMEOUT=30
HUBSPOT_MAX_RETRIES=3
HUBSPOT_CIRCUIT_BREAKER_ENABLED=true
HUBSPOT_CACHE_ENABLED=true
HUBSPOT_METRICS_ENABLED=true
```

**Variables de entorno para ManyChat:**
```bash
MANYCHAT_API_KEY=xxx
MANYCHAT_PAGE_ID=xxx
MANYCHAT_BASE_URL=https://api.manychat.com
MANYCHAT_TIMEOUT=30
MANYCHAT_MAX_RETRIES=3
MANYCHAT_CIRCUIT_BREAKER_ENABLED=true
MANYCHAT_METRICS_ENABLED=true
```

## 🔄 Versionado

Versión actual: **2.2.0**

### v2.2.0 (Actual)
- ✅ **Connection pooling avanzado** (httpx o requests con HTTPAdapter)
- ✅ **Configuración robusta** desde variables de entorno con dataclasses
- ✅ **Mejora de gestión de recursos** con context managers mejorados
- ✅ **Compatibilidad mejorada** entre httpx y requests

### v2.1.0
- ✅ Health Checks integrados
- ✅ Batch Processing para operaciones paralelas
- ✅ Context Managers para gestión de recursos

### v2.0.0
- ✅ Circuit Breaker pattern integrado
- ✅ Caché para reducir llamadas repetidas
- ✅ Métricas Prometheus integradas
- ✅ Mejor observabilidad y logging

## 📚 Referencias

- [HubSpot API Docs](https://developers.hubspot.com/docs/api/overview)
- [ManyChat API Docs](https://manychat.github.io/dynamic_block_docs/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Prometheus Metrics](https://prometheus.io/docs/instrumenting/exposition_formats/)

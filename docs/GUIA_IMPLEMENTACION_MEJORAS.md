# 🚀 Guía Práctica de Implementación de Mejoras

> **Ejemplos prácticos para implementar las mejoras de arquitectura**

## 📋 Tabla de Contenidos

1. [Quick Start](#quick-start)
2. [Ejemplos por Categoría](#ejemplos-por-categoría)
3. [Patrones de Migración](#patrones-de-migración)
4. [Best Practices](#best-practices)

---

## ⚡ Quick Start

### Instalación

```bash
# Instalar dependencias principales
pip install -r data/airflow/requirements.txt

# Instalar dependencias de desarrollo
pip install -r requirements-dev.txt

# O instalar solo las esenciales
pip install -r data/airflow/requirements-base.txt
```

### Configuración Inicial

```bash
# Variables de entorno
cp data/airflow/ENV_EXAMPLE .env

# Configurar logging estructurado
export LOG_LEVEL=INFO
export LOG_FORMAT=json  # o 'text' para desarrollo
```

---

## 📚 Ejemplos por Categoría

### 1. Validación con Pydantic v2

#### Ejemplo Básico

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class LeadModel(BaseModel):
    """Modelo validado para leads"""
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    company: Optional[str] = None
    tags: List[str] = Field(default_factory=list, max_items=10)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "name": "John Doe",
                "phone": "+1234567890",
                "company": "Acme Corp"
            }
        }

# Uso
def process_lead(data: dict):
    try:
        lead = LeadModel(**data)
        print(f"Processing lead: {lead.email}")
        return lead
    except ValueError as e:
        print(f"Validation error: {e}")
        raise
```

#### Ejemplo con Settings

```python
from pydantic_settings import BaseSettings
from typing import Optional

class AppSettings(BaseSettings):
    """Configuración validada de la aplicación"""
    database_url: str
    redis_url: str = "redis://localhost:6379"
    api_key: str
    log_level: str = "INFO"
    max_retries: int = 3
    timeout: float = 30.0
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = AppSettings()
```

---

### 2. HTTP Async con httpx

#### Ejemplo Básico

```python
import httpx
import asyncio
from typing import List, Dict

async def fetch_single(url: str) -> Dict:
    """Fetch una URL"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()

async def fetch_multiple(urls: List[str]) -> List[Dict]:
    """Fetch múltiples URLs en paralelo"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [client.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [r.json() for r in responses]

# Uso
async def main():
    data = await fetch_single("https://api.example.com/data")
    print(data)
    
    # Fetch en paralelo
    urls = [
        "https://api.example.com/data1",
        "https://api.example.com/data2",
        "https://api.example.com/data3"
    ]
    results = await fetch_multiple(urls)
    print(results)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Ejemplo con Retry y Circuit Breaker

```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from pybreaker import CircuitBreaker

# Circuit breaker para proteger contra fallos en cascada
breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def fetch_with_resilience(url: str) -> Dict:
    """Fetch con retry y circuit breaker"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

---

### 3. Logging Estructurado

#### Configuración con structlog

```python
import structlog
import logging
import sys

def setup_logging(log_level: str = "INFO", json_format: bool = False):
    """Configurar logging estructurado"""
    
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if json_format:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

# Uso
setup_logging()

logger = structlog.get_logger()

def process_lead(lead_id: str, email: str):
    logger.info(
        "processing_lead",
        lead_id=lead_id,
        email=email,
        action="start"
    )
    
    try:
        # Procesar lead
        result = process(lead_id)
        
        logger.info(
            "processing_lead",
            lead_id=lead_id,
            email=email,
            action="complete",
            result="success"
        )
        return result
    except Exception as e:
        logger.error(
            "processing_lead",
            lead_id=lead_id,
            email=email,
            action="failed",
            error=str(e),
            exc_info=True
        )
        raise
```

#### Alternativa con loguru

```python
from loguru import logger
import sys

# Configurar loguru
logger.remove()  # Remover handler por defecto
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
    level="INFO"
)

# Para producción (JSON)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    rotation="100 MB",
    retention="30 days",
    serialize=True,  # JSON format
    level="INFO"
)

# Uso
logger.info("Processing lead", lead_id="123", email="test@example.com")
logger.error("Error occurred", error=str(e), exc_info=True)
```

---

### 4. OpenTelemetry Tracing

#### Configuración

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

def setup_tracing(service_name: str = "airflow-dags"):
    """Configurar OpenTelemetry tracing"""
    
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
    })
    
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint="http://jaeger:4317",
            insecure=True
        )
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(__name__)

# Uso en código
tracer = setup_tracing()

def process_document(doc_id: str):
    with tracer.start_as_current_span("process_document") as span:
        span.set_attribute("doc_id", doc_id)
        span.set_attribute("operation", "process")
        
        try:
            # Procesar documento
            result = process(doc_id)
            
            span.set_attribute("result.status", "success")
            span.set_attribute("result.size", len(result))
            return result
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise
```

---

### 5. Testing Avanzado

#### Tests con pytest-asyncio

```python
import pytest
import httpx
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_fetch_data():
    """Test async function"""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_fetch_with_mock():
    """Test con mock"""
    mock_response = {"data": "test"}
    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.return_value = AsyncMock(
            json=lambda: mock_response,
            status_code=200
        )
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            assert response.json() == mock_response
```

#### Tests con responses (mocking requests)

```python
import pytest
import responses
import requests

@responses.activate
def test_api_call():
    """Test con responses mock"""
    responses.add(
        responses.GET,
        "https://api.example.com/data",
        json={"data": "test"},
        status=200
    )
    
    response = requests.get("https://api.example.com/data")
    assert response.status_code == 200
    assert response.json() == {"data": "test"}
```

#### Property-Based Testing con hypothesis

```python
from hypothesis import given, strategies as st
from pydantic import ValidationError

@given(
    st.emails(),
    st.text(min_size=1, max_size=100),
    st.optional(st.phone_numbers())
)
def test_lead_validation(email: str, name: str, phone: str):
    """Test property-based para validación de leads"""
    try:
        lead = LeadModel(
            email=email,
            name=name,
            phone=phone
        )
        assert lead.email == email
        assert lead.name == name
    except ValidationError:
        # Algunas combinaciones pueden ser inválidas
        pass
```

---

### 6. Caching Avanzado

#### Redis Cache con aiocache

```python
from aiocache import Cache
from aiocache.serializers import JsonSerializer

cache = Cache(
    Cache.REDIS,
    endpoint="localhost",
    port=6379,
    serializer=JsonSerializer(),
    namespace="main"
)

@cache.cached(ttl=3600, key="user:{id}")
async def get_user(user_id: int):
    """Obtener usuario con cache"""
    # Lógica para obtener usuario
    return {"id": user_id, "name": "John"}

# Uso
async def main():
    user = await get_user(123)
    print(user)
```

#### In-Memory Cache con cachetools

```python
from cachetools import TTLCache, LRUCache
from functools import wraps

# TTL Cache
ttl_cache = TTLCache(maxsize=100, ttl=3600)

# LRU Cache
lru_cache = LRUCache(maxsize=1000)

def cached_ttl(func):
    """Decorador para cache con TTL"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in ttl_cache:
            return ttl_cache[key]
        result = func(*args, **kwargs)
        ttl_cache[key] = result
        return result
    return wrapper

@cached_ttl
def expensive_function(x: int) -> int:
    """Función costosa con cache"""
    return x * x
```

---

### 7. Rate Limiting

#### Rate Limiting con aiolimiter

```python
from aiolimiter import AsyncLimiter
import asyncio

limiter = AsyncLimiter(max_rate=10, time_period=1)  # 10 requests per second

async def make_request():
    """Make request with rate limiting"""
    async with limiter:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            return response.json()

# Uso
async def main():
    tasks = [make_request() for _ in range(100)]
    results = await asyncio.gather(*tasks)
    print(f"Processed {len(results)} requests")
```

#### Rate Limiting con slowapi (FastAPI)

```python
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/data")
@limiter.limit("10/minute")
async def get_data(request: Request):
    return {"data": "test"}
```

---

### 8. Connection Pooling

#### Async PostgreSQL con asyncpg

```python
import asyncpg
import asyncio

async def create_pool():
    """Crear connection pool"""
    return await asyncpg.create_pool(
        "postgresql://user:password@localhost/dbname",
        min_size=10,
        max_size=20,
        command_timeout=60
    )

async def query_data(pool):
    """Ejecutar query con pool"""
    async with pool.acquire() as connection:
        rows = await connection.fetch(
            "SELECT * FROM users WHERE id = $1",
            123
        )
        return rows

# Uso
async def main():
    pool = await create_pool()
    try:
        data = await query_data(pool)
        print(data)
    finally:
        await pool.close()
```

---

## 🔄 Patrones de Migración

### Patrón 1: Migrar de requests a httpx

**Antes:**
```python
import requests

def fetch_data(url: str):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()
```

**Después:**
```python
import httpx

async def fetch_data(url: str):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
```

### Patrón 2: Agregar Validación Pydantic

**Antes:**
```python
def process_lead(data: dict):
    if 'email' not in data:
        raise ValueError("Email required")
    if '@' not in data['email']:
        raise ValueError("Invalid email")
    return data
```

**Después:**
```python
from pydantic import BaseModel, EmailStr

class LeadModel(BaseModel):
    email: EmailStr
    name: str

def process_lead(data: dict):
    lead = LeadModel(**data)  # Validación automática
    return lead
```

### Patrón 3: Agregar Logging Estructurado

**Antes:**
```python
import logging

logging.info(f"Processing lead {lead_id} with email {email}")
```

**Después:**
```python
import structlog

logger = structlog.get_logger()
logger.info("processing_lead", lead_id=lead_id, email=email)
```

### Patrón 4: Agregar Circuit Breaker

**Antes:**
```python
def call_external_api():
    try:
        response = requests.get("https://api.example.com/data")
        return response.json()
    except Exception:
        raise
```

**Después:**
```python
from pybreaker import CircuitBreaker

breaker = CircuitBreaker(fail_max=5, timeout_duration=60)

@breaker
def call_external_api():
    response = requests.get("https://api.example.com/data")
    return response.json()
```

---

## ✅ Best Practices

### 1. Validación de Datos
- ✅ Usar Pydantic para todos los modelos de datos
- ✅ Validar entrada en los boundaries de la aplicación
- ✅ Usar tipos específicos (EmailStr, URL, etc.)

### 2. Async Programming
- ✅ Usar httpx para todas las llamadas HTTP nuevas
- ✅ Migrar gradualmente de requests a httpx
- ✅ Usar async/await consistentemente

### 3. Logging
- ✅ Logging estructurado en producción (JSON)
- ✅ Incluir contexto relevante en cada log
- ✅ Usar niveles apropiados (DEBUG, INFO, WARNING, ERROR)

### 4. Error Handling
- ✅ Circuit breakers para servicios externos
- ✅ Retry con exponential backoff
- ✅ Timeouts apropiados

### 5. Testing
- ✅ Tests unitarios para lógica de negocio
- ✅ Tests de integración para APIs
- ✅ Property-based testing para validación

### 6. Performance
- ✅ Connection pooling para bases de datos
- ✅ Caching para datos frecuentemente accedidos
- ✅ Rate limiting para APIs externas

### 7. Observabilidad
- ✅ Tracing distribuido con OpenTelemetry
- ✅ Métricas con Prometheus
- ✅ Logs estructurados

---

## 📝 Checklist de Implementación

Para cada módulo:

- [ ] Validación con Pydantic
- [ ] Logging estructurado
- [ ] Error handling robusto
- [ ] Tests unitarios
- [ ] Circuit breaker (si aplica)
- [ ] Rate limiting (si aplica)
- [ ] Caching (si aplica)
- [ ] Tracing (si aplica)
- [ ] Documentación actualizada

---

**Última actualización**: 2024-12-19
**Versión**: 1.0.0













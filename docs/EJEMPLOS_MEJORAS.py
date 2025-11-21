"""
Ejemplos prácticos de implementación de mejoras de arquitectura
Este archivo contiene ejemplos reutilizables para migrar código existente
"""

# ============================================================================
# 1. VALIDACIÓN CON PYDANTIC V2
# ============================================================================

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

# Ejemplo: Modelo de Lead mejorado
class LeadModel(BaseModel):
    """Modelo validado para leads con Pydantic v2"""
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

# Ejemplo: Settings validado
from pydantic_settings import BaseSettings

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


# ============================================================================
# 2. HTTP ASYNC CON HTTPX
# ============================================================================

import httpx
import asyncio
from typing import List, Dict

async def fetch_single(url: str) -> Dict:
    """Fetch una URL con httpx"""
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


# ============================================================================
# 3. RESILENCIA CON CIRCUIT BREAKER Y RETRY
# ============================================================================

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


# ============================================================================
# 4. LOGGING ESTRUCTURADO
# ============================================================================

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
logger = structlog.get_logger()

def process_lead(lead_id: str, email: str):
    logger.info("processing_lead", lead_id=lead_id, email=email, action="start")
    try:
        result = process(lead_id)
        logger.info("processing_lead", lead_id=lead_id, email=email, action="complete", result="success")
        return result
    except Exception as e:
        logger.error("processing_lead", lead_id=lead_id, email=email, action="failed", error=str(e), exc_info=True)
        raise


# ============================================================================
# 5. OPENTELEMETRY TRACING
# ============================================================================

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
        OTLPSpanExporter(endpoint="http://jaeger:4317", insecure=True)
    )
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(__name__)

tracer = setup_tracing()

def process_document(doc_id: str):
    with tracer.start_as_current_span("process_document") as span:
        span.set_attribute("doc_id", doc_id)
        span.set_attribute("operation", "process")
        
        try:
            result = process(doc_id)
            span.set_attribute("result.status", "success")
            span.set_attribute("result.size", len(result))
            return result
        except Exception as e:
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise


# ============================================================================
# 6. CACHING AVANZADO
# ============================================================================

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
    return {"id": user_id, "name": "John"}


# ============================================================================
# 7. RATE LIMITING
# ============================================================================

from aiolimiter import AsyncLimiter

limiter = AsyncLimiter(max_rate=10, time_period=1)  # 10 requests per second

async def make_request():
    """Make request with rate limiting"""
    async with limiter:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.example.com/data")
            return response.json()


# ============================================================================
# 8. CONNECTION POOLING
# ============================================================================

import asyncpg

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


# ============================================================================
# 9. TESTING AVANZADO
# ============================================================================

import pytest
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


# ============================================================================
# 10. EJEMPLO COMPLETO: FUNCIÓN MEJORADA
# ============================================================================

async def process_lead_improved(lead_data: dict) -> LeadModel:
    """
    Ejemplo completo de función mejorada con todas las mejores prácticas:
    - Validación con Pydantic
    - Logging estructurado
    - Tracing distribuido
    - Circuit breaker
    - Retry logic
    - Caching
    """
    # Validación
    lead = LeadModel(**lead_data)
    
    # Logging
    logger.info("processing_lead", lead_id=lead.email, action="start")
    
    # Tracing
    with tracer.start_as_current_span("process_lead") as span:
        span.set_attribute("lead.email", lead.email)
        span.set_attribute("lead.company", lead.company or "N/A")
        
        try:
            # Check cache
            cached_result = await cache.get(f"lead:{lead.email}")
            if cached_result:
                logger.info("processing_lead", lead_id=lead.email, action="cache_hit")
                return cached_result
            
            # Process with resilience
            result = await fetch_with_resilience(f"https://api.example.com/leads/{lead.email}")
            
            # Cache result
            await cache.set(f"lead:{lead.email}", result, ttl=3600)
            
            # Log success
            logger.info("processing_lead", lead_id=lead.email, action="complete", result="success")
            span.set_attribute("result.status", "success")
            
            return result
            
        except Exception as e:
            logger.error("processing_lead", lead_id=lead.email, action="failed", error=str(e), exc_info=True)
            span.set_attribute("error", True)
            span.set_attribute("error.message", str(e))
            span.record_exception(e)
            raise


if __name__ == "__main__":
    # Setup
    setup_logging()
    tracer = setup_tracing()
    
    # Ejemplo de uso
    lead_data = {
        "email": "test@example.com",
        "name": "Test User",
        "phone": "+1234567890"
    }
    
    result = asyncio.run(process_lead_improved(lead_data))
    print(result)













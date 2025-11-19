"""
Ejemplo de DAG de Airflow mejorado con las nuevas librerías
Este DAG muestra cómo usar Pydantic, httpx, structlog, etc.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

# Nuevas librerías
import structlog
import httpx
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from opentelemetry import trace

# Configurar logging estructurado
logger = structlog.get_logger(__name__)

# Configurar tracing (opcional, si OpenTelemetry está configurado)
try:
    tracer = trace.get_tracer(__name__)
except Exception:
    tracer = None


# ============================================================================
# MODELOS PYDANTIC
# ============================================================================

class LeadModel(BaseModel):
    """Modelo validado para leads"""
    email: EmailStr
    name: str = Field(min_length=1, max_length=100)
    phone: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    company: Optional[str] = None
    source: str = Field(default="web")
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class APIResponse(BaseModel):
    """Modelo para respuesta de API"""
    status: str
    data: Dict[str, Any]
    timestamp: str


# ============================================================================
# FUNCIONES AUXILIARES MEJORADAS
# ============================================================================

async def fetch_lead_data(lead_id: str) -> Dict[str, Any]:
    """
    Fetch datos de lead con httpx async
    Reemplaza requests.get() con httpx async
    """
    url = f"https://api.example.com/leads/{lead_id}"
    
    logger.info("fetching_lead", lead_id=lead_id, url=url)
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            logger.info(
                "fetch_lead_success",
                lead_id=lead_id,
                status_code=response.status_code
            )
            
            return data
    except httpx.HTTPError as e:
        logger.error(
            "fetch_lead_error",
            lead_id=lead_id,
            error=str(e),
            exc_info=True
        )
        raise


def validate_lead_data(data: Dict[str, Any]) -> LeadModel:
    """
    Validar datos de lead con Pydantic
    Reemplaza validaciones manuales
    """
    try:
        lead = LeadModel(**data)
        logger.info("lead_validated", email=lead.email, name=lead.name)
        return lead
    except Exception as e:
        logger.error("lead_validation_failed", error=str(e), data=data)
        raise


# ============================================================================
# DAG MEJORADO
# ============================================================================

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

@dag(
    dag_id="example_improved_lead_processing",
    default_args=default_args,
    description="Ejemplo de DAG mejorado con nuevas librerías",
    schedule="@daily",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    catchup=False,
    tags=["example", "improved", "lead-processing"],
    params={
        "lead_id": Param(
            default="",
            type="string",
            description="ID del lead a procesar",
        ),
    },
)
def example_improved_dag():
    """DAG de ejemplo mostrando las mejoras"""
    
    @task
    def extract_lead_data(**context):
        """
        Extraer datos de lead
        Usa logging estructurado y validación Pydantic
        """
        lead_id = context["params"]["lead_id"]
        
        logger.info(
            "extract_lead_start",
            lead_id=lead_id,
            dag_run_id=context["dag_run"].run_id,
            task_instance_id=context["task_instance"].task_id
        )
        
        # Simular datos (en producción, vendría de una fuente real)
        raw_data = {
            "email": "test@example.com",
            "name": "Test User",
            "phone": "+1234567890",
            "company": "Acme Corp",
            "source": "web"
        }
        
        # Validar con Pydantic
        lead = validate_lead_data(raw_data)
        
        logger.info(
            "extract_lead_complete",
            lead_id=lead_id,
            email=lead.email,
            validated=True
        )
        
        return lead.dict()
    
    @task
    def process_lead(lead_data: Dict[str, Any], **context):
        """
        Procesar lead
        Usa logging estructurado y tracing
        """
        lead_id = context["params"]["lead_id"]
        
        # Tracing (si está disponible)
        span = None
        if tracer:
            span = tracer.start_span("process_lead")
            span.set_attribute("lead_id", lead_id)
            span.set_attribute("email", lead_data.get("email"))
        
        try:
            logger.info(
                "process_lead_start",
                lead_id=lead_id,
                email=lead_data.get("email")
            )
            
            # Lógica de procesamiento
            processed_data = {
                **lead_data,
                "processed_at": pendulum.now().isoformat(),
                "status": "processed"
            }
            
            logger.info(
                "process_lead_complete",
                lead_id=lead_id,
                status="success"
            )
            
            if span:
                span.set_attribute("status", "success")
                span.end()
            
            return processed_data
            
        except Exception as e:
            logger.error(
                "process_lead_error",
                lead_id=lead_id,
                error=str(e),
                exc_info=True
            )
            
            if span:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                span.record_exception(e)
                span.end()
            
            raise
    
    @task
    def save_lead(processed_data: Dict[str, Any], **context):
        """
        Guardar lead procesado
        Usa logging estructurado
        """
        lead_id = context["params"]["lead_id"]
        
        logger.info(
            "save_lead_start",
            lead_id=lead_id,
            email=processed_data.get("email")
        )
        
        # Simular guardado (en producción, sería a base de datos)
        logger.info(
            "save_lead_complete",
            lead_id=lead_id,
            status="saved"
        )
        
        return {"status": "saved", "lead_id": lead_id}
    
    # Definir dependencias
    lead_data = extract_lead_data()
    processed_data = process_lead(lead_data)
    save_lead(processed_data)


# Instanciar el DAG
example_improved_dag_instance = example_improved_dag()













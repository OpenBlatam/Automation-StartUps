from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import re
import os
import hashlib
from functools import lru_cache
from collections import defaultdict

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.stats import Stats
from airflow.models import Variable
from airflow.exceptions import AirflowFailException

# Retry logic mejorado
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    def retry(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Circuit breaker
try:
    from pybreaker import CircuitBreaker
    CIRCUIT_BREAKER_AVAILABLE = True
except ImportError:
    CIRCUIT_BREAKER_AVAILABLE = False
    class CircuitBreaker:
        def __call__(self, func):
            return func

# Procesamiento concurrente
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONCURRENT_AVAILABLE = True
except ImportError:
    CONCURRENT_AVAILABLE = False

# Caché
try:
    from cachetools import TTLCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    class TTLCache(dict):
        def __init__(self, *args, **kwargs):
            super().__init__()

# Structured logging
try:
    import structlog
    STRUCTLOG_AVAILABLE = True
except ImportError:
    STRUCTLOG_AVAILABLE = False

# Validación con Pydantic
try:
    from pydantic import BaseModel, EmailStr, Field, validator, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = None
    EmailStr = str

# Performance profiling
try:
    from time import perf_counter
    PERF_COUNTER_AVAILABLE = True
except ImportError:
    PERF_COUNTER_AVAILABLE = False
    def perf_counter():
        return 0

# DNS validation
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    dns = None

# Métricas Prometheus
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    class DummyMetric:
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    Counter = Histogram = Gauge = DummyMetric

# Notificaciones
try:
    from data.airflow.plugins.etl_notifications import notify_slack
except ImportError:
    def notify_slack(message: str) -> None:
        logger.info(f"Slack notification (not configured): {message}")

# Configurar logger
if STRUCTLOG_AVAILABLE:
    logger = structlog.get_logger(__name__)
else:
    logger = logging.getLogger(__name__)

# ============================================================================
# CONSTANTES Y CONFIGURACIÓN
# ============================================================================

# Timeouts
DEFAULT_TIMEOUT = float(os.getenv("POST_EVENT_TIMEOUT", "30.0"))
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "5.0"))

# Cache TTLs
EMAIL_CACHE_TTL = int(os.getenv("EMAIL_CACHE_TTL", "3600"))
CONTACT_CACHE_TTL = int(os.getenv("CONTACT_CACHE_TTL", "1800"))

# Batch processing
BATCH_SIZE = int(os.getenv("POST_EVENT_BATCH_SIZE", "10"))
MAX_WORKERS = int(os.getenv("POST_EVENT_MAX_WORKERS", "4"))

# Circuit breakers
email_circuit_breaker = CircuitBreaker(
    fail_max=5,
    timeout_duration=60,
    expected_exception=Exception
) if CIRCUIT_BREAKER_AVAILABLE else None

# Caché para evitar procesar el mismo contacto múltiples veces
processed_contacts_cache = TTLCache(maxsize=1000, ttl=CONTACT_CACHE_TTL) if CACHE_AVAILABLE else {}

# Dead Letter Queue
DLQ_PATH = os.getenv("POST_EVENT_DLQ_PATH", "/tmp/post_event_followup_dlq.jsonl")

# Rate limiting
RATE_LIMIT_EMAIL_MAX = int(os.getenv("RATE_LIMIT_EMAIL_MAX", "10"))
RATE_LIMIT_EMAIL_PERIOD = int(os.getenv("RATE_LIMIT_EMAIL_PERIOD", "3600"))

# Performance profiling
class PerformanceProfiler:
    """Profiler simple para medir tiempos de ejecución."""
    def __init__(self):
        self.timings: Dict[str, List[float]] = defaultdict(list)
    
    def time(self, operation: str):
        """Context manager para medir tiempo de operación."""
        class TimingContext:
            def __init__(self, profiler, op):
                self.profiler = profiler
                self.op = op
                self.start = None
            
            def __enter__(self):
                if PERF_COUNTER_AVAILABLE:
                    self.start = perf_counter()
                return self
            
            def __exit__(self, *args):
                if PERF_COUNTER_AVAILABLE and self.start:
                    duration = perf_counter() - self.start
                    self.profiler.timings[self.op].append(duration)
        
        return TimingContext(self, operation)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Obtiene estadísticas de una operación."""
        timings = self.timings.get(operation, [])
        if not timings:
            return {}
        
        return {
            "count": len(timings),
            "total": sum(timings),
            "avg": sum(timings) / len(timings),
            "min": min(timings),
            "max": max(timings),
            "p95": sorted(timings)[int(len(timings) * 0.95)] if len(timings) > 1 else timings[0]
        }

_profiler = PerformanceProfiler()

# Adaptive Batch Sizing
class AdaptiveBatchSizer:
    """Ajusta el tamaño de batch dinámicamente basado en performance."""
    
    def __init__(self, initial_size: int = 10, min_size: int = 5, max_size: int = 50):
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
        """Calcula el tamaño óptimo de batch basado en performance."""
        # Registrar performance
        self.performance_history.append({
            "batch_size": self.current_size,
            "success_rate": success_rate,
            "avg_duration": avg_duration,
            "error_rate": error_rate,
            "timestamp": datetime.utcnow().isoformat()
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
        self.performance_history = []

_adaptive_batch_sizer = AdaptiveBatchSizer()

# Feature Flags
try:
    VARIABLES_AVAILABLE = True
except ImportError:
    VARIABLES_AVAILABLE = False

def get_feature_flag(flag_name: str, default: bool = False) -> bool:
    """Obtiene el valor de un feature flag desde Airflow Variables."""
    if not VARIABLES_AVAILABLE:
        return default
    try:
        flag_value = Variable.get(f"post_event_followup:{flag_name}", default_var=str(default).lower())
        return flag_value.lower() in ["true", "1", "yes", "on"]
    except Exception:
        return default

# Distributed Locking
def acquire_distributed_lock(lock_key: str, timeout_seconds: int = 3600) -> bool:
    """Adquiere un lock distribuido usando Airflow Variables."""
    if not VARIABLES_AVAILABLE:
        return True  # Fallback: permitir ejecución
    
    try:
        existing = Variable.get(lock_key, default_var=None)
        if existing:
            try:
                lock_data = json.loads(existing)
                expires_at = lock_data.get("expires_at", 0)
                now = int(datetime.utcnow().timestamp())
                if expires_at > now:
                    return False
            except Exception:
                pass
        
        now = int(datetime.utcnow().timestamp())
        lock_data = {
            "acquired_at": now,
            "expires_at": now + timeout_seconds,
            "run_id": os.environ.get("AIRFLOW_RUN_ID", "unknown"),
        }
        Variable.set(lock_key, json.dumps(lock_data))
        return True
    except Exception as e:
        logger.warning(f"Failed to acquire lock {lock_key}: {e}")
        return True  # Fallback: permitir ejecución

def release_distributed_lock(lock_key: str) -> None:
    """Libera un lock distribuido."""
    if not VARIABLES_AVAILABLE:
        return
    try:
        Variable.delete(lock_key)
    except Exception as e:
        logger.warning(f"Failed to release lock {lock_key}: {e}")

# Checkpointing
def save_checkpoint(checkpoint_name: str, data: Dict[str, Any]) -> None:
    """Guarda un checkpoint para reanudar procesamiento."""
    if not VARIABLES_AVAILABLE:
        return
    try:
        checkpoint_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": data
        }
        Variable.set(f"post_event_followup:checkpoint:{checkpoint_name}", json.dumps(checkpoint_data))
    except Exception as e:
        logger.warning(f"Failed to save checkpoint {checkpoint_name}: {e}")

def load_checkpoint(checkpoint_name: str) -> Optional[Dict[str, Any]]:
    """Carga un checkpoint para reanudar procesamiento."""
    if not VARIABLES_AVAILABLE:
        return None
    try:
        checkpoint_str = Variable.get(f"post_event_followup:checkpoint:{checkpoint_name}", default_var=None)
        if checkpoint_str:
            checkpoint_data = json.loads(checkpoint_str)
            return checkpoint_data.get("data")
    except Exception as e:
        logger.warning(f"Failed to load checkpoint {checkpoint_name}: {e}")
    return None

# A/B Testing
def assign_ab_group(email: str, experiment_name: str = "email_template") -> str:
    """Asigna contacto a grupo A/B basado en hash del email."""
    email_hash = int(hashlib.md5(f"{email}_{experiment_name}".encode()).hexdigest(), 16)
    return "A" if (email_hash % 2) == 0 else "B"

def get_ab_variant(ab_group: str, experiment_name: str) -> Dict[str, Any]:
    """Obtiene variante A/B para un experimento."""
    variants = {
        "email_template": {
            "A": {"template": "standard", "subject_prefix": ""},
            "B": {"template": "personalized", "subject_prefix": "🎯 "}
        },
        "timing": {
            "A": {"delay_hours": 24},
            "B": {"delay_hours": 18}
        },
        "content": {
            "A": {"cta": "Schedule a call", "tone": "professional"},
            "B": {"cta": "Let's talk!", "tone": "friendly"}
        }
    }
    return variants.get(experiment_name, {}).get(ab_group, {})

# Cohort Analysis
def analyze_cohorts(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analiza contactos agrupados por cohorte (fecha de registro)."""
    cohorts = defaultdict(lambda: {"count": 0, "emails_sent": 0, "total_value": 0})
    
    for contact in contacts:
        created_at = contact.get("created_at")
        if created_at:
            try:
                if isinstance(created_at, str):
                    dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    dt = created_at
                cohort_key = dt.strftime("%Y-%W")  # Año-Semana
                
                cohorts[cohort_key]["count"] += 1
                if contact.get("email_sent"):
                    cohorts[cohort_key]["emails_sent"] += 1
                cohorts[cohort_key]["total_value"] += contact.get("value_analysis", {}).get("estimated_value_usd", 0)
            except Exception:
                pass
    
    return {
        "cohorts": dict(cohorts),
        "total_cohorts": len(cohorts),
        "avg_contacts_per_cohort": sum(c["count"] for c in cohorts.values()) / len(cohorts) if cohorts else 0
    }

# Multi-channel Attribution
def calculate_attribution(contact: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula atribución multi-canal para el contacto."""
    attribution = {
        "channels": [],
        "primary_channel": None,
        "attribution_model": "first_touch"
    }
    
    source = contact.get("source", "")
    utm_source = contact.get("utm_source", "")
    utm_campaign = contact.get("utm_campaign", "")
    utm_medium = contact.get("utm_medium", "")
    
    if utm_source:
        attribution["channels"].append({
            "type": "paid",
            "source": utm_source,
            "campaign": utm_campaign,
            "medium": utm_medium,
            "weight": 0.4
        })
        attribution["primary_channel"] = utm_source
    
    if source in ["feria", "event", "trade_show"]:
        attribution["channels"].append({
            "type": "event",
            "source": source,
            "weight": 0.6
        })
        if not attribution["primary_channel"]:
            attribution["primary_channel"] = source
    
    if not attribution["primary_channel"]:
        attribution["primary_channel"] = "direct"
        attribution["channels"].append({
            "type": "direct",
            "source": "direct",
            "weight": 1.0
        })
    
    return attribution

# S3 Export (opcional)
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False
    boto3 = None

def export_to_s3(data: Dict[str, Any], bucket: str, key: str) -> bool:
    """Exporta datos a S3 para análisis a largo plazo."""
    if not S3_AVAILABLE:
        return False
    try:
        s3_client = boto3.client('s3')
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(data, indent=2),
            ContentType='application/json'
        )
        logger.info(f"Datos exportados a S3: s3://{bucket}/{key}")
        return True
    except Exception as e:
        logger.warning(f"Error exportando a S3: {e}")
        return False

# Análisis de Tendencias Temporales
def analyze_temporal_trends(contacts: List[Dict[str, Any]], hook: PostgresHook) -> Dict[str, Any]:
    """Analiza tendencias temporales comparando con ejecuciones anteriores."""
    trends = {
        "has_trends": False,
        "comparison_period": "7_days",
        "metrics": {}
    }
    
    try:
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener métricas de ejecuciones anteriores (últimos 7 días)
                cur.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as contacts_count,
                        AVG((report_data->>'summary'->>'success_rate')::float) as avg_success_rate,
                        SUM((report_data->>'summary'->>'total_estimated_value_usd')::float) as total_value
                    FROM post_event_executive_reports
                    WHERE created_at >= NOW() - INTERVAL '7 days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                    LIMIT 7
                """)
                
                historical_data = cur.fetchall()
                if len(historical_data) > 1:
                    trends["has_trends"] = True
                    
                    # Calcular tendencias
                    current_contacts = len(contacts)
                    current_success = sum(1 for c in contacts if c.get("email_sent")) / current_contacts * 100 if current_contacts > 0 else 0
                    current_value = sum(c.get("value_analysis", {}).get("estimated_value_usd", 0) for c in contacts)
                    
                    # Comparar con promedio histórico
                    avg_historical_contacts = sum(row[1] for row in historical_data) / len(historical_data) if historical_data else 0
                    avg_historical_success = sum(row[2] or 0 for row in historical_data) / len(historical_data) if historical_data else 0
                    avg_historical_value = sum(row[3] or 0 for row in historical_data) / len(historical_data) if historical_data else 0
                    
                    trends["metrics"] = {
                        "current": {
                            "contacts": current_contacts,
                            "success_rate": round(current_success, 2),
                            "total_value": round(current_value, 2)
                        },
                        "historical_avg": {
                            "contacts": round(avg_historical_contacts, 2),
                            "success_rate": round(avg_historical_success, 2),
                            "total_value": round(avg_historical_value, 2)
                        },
                        "growth": {
                            "contacts": round(((current_contacts - avg_historical_contacts) / avg_historical_contacts * 100) if avg_historical_contacts > 0 else 0, 2),
                            "success_rate": round(current_success - avg_historical_success, 2),
                            "total_value": round(((current_value - avg_historical_value) / avg_historical_value * 100) if avg_historical_value > 0 else 0, 2)
                        }
                    }
    except Exception as e:
        logger.debug(f"Error analizando tendencias temporales: {e}")
        trends["error"] = str(e)
    
    return trends

# Detección de Anomalías Avanzada
def detect_advanced_anomalies(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Detecta anomalías avanzadas en los datos de contactos."""
    anomalies = []
    anomaly_score = 0
    
    if not contacts:
        return {"anomalies": [], "anomaly_score": 0, "severity": "none"}
    
    # Anomalía 1: Volumen inusual
    avg_contacts = 50  # Valor de referencia
    if len(contacts) > avg_contacts * 2:
        anomalies.append({
            "type": "high_volume",
            "severity": "medium",
            "description": f"Volumen inusualmente alto: {len(contacts)} contactos (esperado: ~{avg_contacts})",
            "value": len(contacts)
        })
        anomaly_score += 20
    elif len(contacts) < avg_contacts * 0.2:
        anomalies.append({
            "type": "low_volume",
            "severity": "low",
            "description": f"Volumen inusualmente bajo: {len(contacts)} contactos",
            "value": len(contacts)
        })
        anomaly_score += 10
    
    # Anomalía 2: Tasa de fallos alta
    failure_rate = sum(1 for c in contacts if not c.get("email_sent")) / len(contacts) * 100 if contacts else 0
    if failure_rate > 30:
        anomalies.append({
            "type": "high_failure_rate",
            "severity": "high",
            "description": f"Tasa de fallos muy alta: {failure_rate:.1f}%",
            "value": failure_rate
        })
        anomaly_score += 30
    
    # Anomalía 3: Calidad promedio baja
    avg_quality = sum(c.get("quality_analysis", {}).get("quality_score", 0) for c in contacts) / len(contacts) if contacts else 0
    if avg_quality < 30:
        anomalies.append({
            "type": "low_quality",
            "severity": "medium",
            "description": f"Calidad promedio muy baja: {avg_quality:.1f} puntos",
            "value": avg_quality
        })
        anomaly_score += 20
    
    # Anomalía 4: Distribución de canales inusual
    channels = defaultdict(int)
    for contact in contacts:
        primary_channel = contact.get("attribution", {}).get("primary_channel", "unknown")
        channels[primary_channel] += 1
    
    if len(channels) == 1 and len(contacts) > 10:
        anomalies.append({
            "type": "single_channel",
            "severity": "low",
            "description": f"Todos los contactos provienen de un solo canal: {list(channels.keys())[0]}",
            "value": list(channels.keys())[0]
        })
        anomaly_score += 10
    
    severity = "none"
    if anomaly_score >= 50:
        severity = "high"
    elif anomaly_score >= 30:
        severity = "medium"
    elif anomaly_score > 0:
        severity = "low"
    
    return {
        "anomalies": anomalies,
        "anomaly_score": anomaly_score,
        "severity": severity,
        "anomaly_count": len(anomalies)
    }

# Integración CRM (opcional)
def sync_to_crm(contact: Dict[str, Any], crm_type: str, crm_config: Dict[str, Any]) -> Dict[str, Any]:
    """Sincroniza contacto con CRM (Salesforce/Pipedrive)."""
    sync_result = {
        "synced": False,
        "crm_type": crm_type,
        "crm_id": None,
        "error": None
    }
    
    if crm_type == "salesforce":
        # Placeholder para integración Salesforce
        try:
            # Aquí iría la lógica de integración con Salesforce
            sync_result["synced"] = True
            sync_result["crm_id"] = f"SF_{contact.get('ext_id')}"
        except Exception as e:
            sync_result["error"] = str(e)
    elif crm_type == "pipedrive":
        # Placeholder para integración Pipedrive
        try:
            # Aquí iría la lógica de integración con Pipedrive
            sync_result["synced"] = True
            sync_result["crm_id"] = f"PD_{contact.get('ext_id')}"
        except Exception as e:
            sync_result["error"] = str(e)
    
    return sync_result

# Métricas Prometheus (si está disponible)
if PROMETHEUS_AVAILABLE:
    post_event_contacts_processed = Counter(
        'post_event_contacts_processed_total',
        'Total contacts processed',
        ['status', 'quality_grade']
    )
    post_event_emails_sent = Counter(
        'post_event_emails_sent_total',
        'Total emails sent',
        ['status']
    )
    post_event_processing_time = Histogram(
        'post_event_processing_seconds',
        'Processing time in seconds',
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
    )
    post_event_quality_score = Histogram(
        'post_event_quality_score',
        'Contact quality score distribution',
        buckets=[0, 20, 40, 60, 80, 100]
    )
    post_event_dlq_size = Gauge(
        'post_event_dlq_size',
        'Dead letter queue size'
    )
else:
    post_event_contacts_processed = None
    post_event_emails_sent = None
    post_event_processing_time = None
    post_event_quality_score = None
    post_event_dlq_size = None

# Dominios de email temporales conocidos
DISPOSABLE_EMAIL_DOMAINS = {
    "10minutemail.com", "mailinator.com", "guerrillamail.com", "tempmail.com",
    "throwaway.email", "getnada.com", "temp-mail.org", "mohmal.com",
    "fakeinbox.com", "trashmail.com", "mintemail.com", "yopmail.com"
}

# Modelos Pydantic para validación
if PYDANTIC_AVAILABLE:
    class ContactModel(BaseModel):
        """Modelo de validación para contactos."""
        ext_id: str
        email: EmailStr
        first_name: Optional[str] = None
        last_name: Optional[str] = None
        phone: Optional[str] = None
        company: Optional[str] = None
        source: str
        utm_source: Optional[str] = None
        utm_campaign: Optional[str] = None
        created_at: str
        
        @validator('email')
        def validate_email(cls, v):
            if not v or '@' not in v:
                raise ValueError('Email inválido')
            return v.lower().strip()
        
        @validator('phone')
        def validate_phone(cls, v):
            if v:
                # Limpiar teléfono
                return re.sub(r'[^\d+]', '', v)
            return v
        
        class Config:
            extra = "allow"  # Permitir campos adicionales
else:
    ContactModel = None

def save_to_dlq(item: Dict[str, Any], error: str, context: Dict[str, Any] = None) -> None:
    """Guarda un contacto fallido en dead letter queue."""
    try:
        os.makedirs(os.path.dirname(DLQ_PATH), exist_ok=True)
        dlq_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "contact_data": item,
            "error": error,
            "context": context or {},
            "retried": False,
            "dag_run_id": context.get("dag_run_id") if context else None,
        }
        with open(DLQ_PATH, "a") as f:
            f.write(json.dumps(dlq_record) + "\n")
        if STRUCTLOG_AVAILABLE:
            logger.warning("Contacto guardado en DLQ", email=item.get("email"), error=error)
        else:
            logger.warning(f"Contacto guardado en DLQ: {error}", extra={"email": item.get("email")})
        try:
            Stats.incr("post_event_followup.dlq.saved", 1)
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error guardando en DLQ: {e}", exc_info=True)


@dag(
    dag_id="post_event_followup",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 9 * * *",  # Diario a las 9:00 AM UTC
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Automatización de Seguimiento Post-Evento - Versión Mejorada
    
    Sistema avanzado que automatiza el seguimiento de contactos registrados en ferias:
    - ✅ Detecta contactos nuevos registrados en ferias (hace ~1 día)
    - ✅ Envía emails personalizados con soporte HTML
    - ✅ Templates avanzados con variables y filtros
    - ✅ Retry logic inteligente con exponential backoff
    - ✅ Crea tareas de llamada de seguimiento automáticamente
    - ✅ Notificaciones Slack opcionales
    - ✅ Métricas y tracking completo
    
    **Flujo:**
    1. Health check de servicios críticos (PostgreSQL, email webhook, circuit breakers)
    2. Optimización de queries y verificación de índices
    3. Detecta contactos registrados en ferias hace 1 día (ventana configurable)
    4. Envía email personalizado de agradecimiento y seguimiento (texto + HTML)
    5. Crea tarea de llamada de seguimiento en el sistema (batch processing optimizado)
    6. Verifica estado del Dead Letter Queue
    7. Genera resumen con métricas y notificaciones
    
    **Características Avanzadas:**
    - **Templates avanzados**: Soporta variables `{{variable}}` con filtros `{{variable|upper|default:valor}}`
    - **Emails HTML**: Genera automáticamente versión HTML profesional
    - **Retry inteligente**: Reintentos automáticos con exponential backoff usando tenacity
    - **Circuit Breaker**: Protección contra fallos en cascada del servicio de email
    - **Procesamiento paralelo**: Envío concurrente de emails en batches (opcional)
    - **Idempotencia**: Caché TTL para evitar procesar contactos duplicados
    - **Dead Letter Queue**: Almacenamiento de contactos fallidos para reprocesamiento
    - **Health Check**: Verificación de servicios críticos antes de procesar
    - **Optimización de Queries**: Verificación de índices y actualización de estadísticas
    - **Batch Processing BD**: Inserción optimizada con `executemany` para mejor rendimiento
    - **Validación con Pydantic**: Validación robusta de datos de contactos
    - **Detección de Duplicados**: Verificación en BD y caché para evitar procesamiento múltiple
    - **Análisis de Calidad**: Scoring automático de calidad de contactos (A-F)
    - **Validación de Email**: Verificación DNS (MX records) y detección de emails temporales
    - **Segmentación**: Clasificación automática de contactos por múltiples factores
    - **Análisis de Sentimiento**: Análisis heurístico de sentimiento en mensajes
    - **Predicción de Conversión**: Cálculo de probabilidad de conversión basado en múltiples factores
    - **Recomendaciones Automáticas**: Generación de recomendaciones de acciones por contacto
    - **Cálculo de Valor**: Estimación de valor monetario del contacto (USD)
    - **Generación de Insights**: Insights inteligentes sobre oportunidades y riesgos
    - **Adaptive Batch Processing**: Ajuste dinámico del tamaño de batch basado en performance
    - **Distributed Locking**: Prevención de ejecuciones concurrentes usando Airflow Variables
    - **Feature Flags**: Control dinámico de características vía Airflow Variables
    - **Checkpointing**: Guarda estado para reanudar procesamiento si falla
    - **Optimización de Timing**: Optimiza timing de contacto basado en datos históricos
    - **A/B Testing**: Asignación automática a grupos A/B para experimentación
    - **Multi-channel Attribution**: Atribución de conversiones a múltiples canales
    - **Cohort Analysis**: Análisis de contactos agrupados por fecha de registro
    - **Análisis de Tendencias Temporales**: Comparación con ejecuciones anteriores
    - **Detección de Anomalías Avanzada**: Identificación de patrones inusuales
    - **Exportación a S3**: Exportación de métricas para análisis a largo plazo (opcional)
    - **Executive Reports**: Reportes ejecutivos con métricas clave y recomendaciones
    - **Audit Trail**: Registro completo de auditoría del procesamiento
    - **Performance Profiling**: Medición de tiempos de ejecución (avg, p95, min, max)
    - **Métricas Prometheus**: Exportación de métricas para monitoreo avanzado (opcional)
    - **Notificaciones**: Alertas Slack cuando hay muchos fallos o al completar
    - **Métricas**: Tracking completo con Airflow Stats
    - **Structured Logging**: Logs estructurados con structlog (opcional)
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `email_webhook_url`: Webhook para envío de emails (requerido)
    - `event_source`: Source para identificar contactos de ferias (default: 'feria')
    - `followup_delay_hours`: Horas de espera antes del seguimiento (default: 24)
    - `email_from`: Email remitente (default: marketing@tu-dominio.com)
    - `email_subject_template`: Template para subject (soporta variables {{first_name}}, etc.)
    - `email_body_template`: Template para body (soporta variables y filtros)
    - `email_template`: Template completo (legacy, se separa en subject/body)
    - `enable_html_emails`: Habilitar versión HTML (default: true)
    - `auto_create_call_task`: Crear tarea de llamada automáticamente (default: true)
    - `call_task_due_hours`: Horas hasta la fecha límite de la llamada (default: 48)
    - `max_retry_attempts`: Intentos de retry para emails (default: 3)
    - `slack_webhook_url`: URL de webhook Slack para notificaciones (opcional)
    - `enable_parallel_processing`: Procesar emails en paralelo (default: false)
    - `batch_size`: Tamaño de batch para procesamiento paralelo (default: 10)
    - `max_workers`: Número de workers para procesamiento paralelo (default: 4)
    - `enable_dlq`: Guardar contactos fallidos en Dead Letter Queue (default: true)
    - `enable_circuit_breaker`: Habilitar circuit breaker para email webhook (default: true)
    - `enable_quality_analysis`: Analizar calidad de contactos (default: true)
    - `enable_duplicate_check`: Verificar duplicados en BD (default: true)
    - `enable_adaptive_batch`: Ajuste dinámico del tamaño de batch (default: true)
    - `enable_distributed_lock`: Usar locking distribuido (default: true)
    - `lock_timeout_seconds`: Tiempo de expiración del lock en segundos (default: 3600)
    - `enable_s3_export`: Exportar métricas a S3 (default: false)
    - `s3_bucket`: Bucket S3 para exportación (requerido si enable_s3_export=true)
    - `min_quality_score`: Score mínimo de calidad para procesar (default: 0)
    - `dry_run`: Solo simular sin enviar (default: false)
    
    **Variables de Template Disponibles:**
    - `{{first_name}}`: Nombre del contacto
    - `{{last_name}}`: Apellido del contacto
    - `{{full_name}}`: Nombre completo
    - `{{company}}`: Empresa del contacto
    - `{{email}}`: Email del contacto
    - `{{event_source}}`: Source del evento
    - `{{utm_campaign}}`: Campaña UTM
    
    **Filtros de Template:**
    - `{{variable|upper}}`: Convertir a mayúsculas
    - `{{variable|lower}}`: Convertir a minúsculas
    - `{{variable|title}}`: Formato título
    - `{{variable|capitalize}}`: Primera letra mayúscula
    - `{{variable|default:valor}}`: Valor por defecto
    
    **Ejemplo de Template:**
    ```
    Subject: Gracias {{first_name|title}} - Seguimiento Post-Feria
    Body: Hola {{first_name|title}} {{last_name|title}},
    
    Gracias por visitarnos en {{event_source|title}}...
    ```
    
    **Requisitos:**
    - Tabla `leads` con campo `source` para identificar contactos de ferias
    - Tabla `sales_pipeline` para contactos calificados
    - Tabla `sales_followup_tasks` para tareas de seguimiento
    - Webhook de email configurado y funcional
    
    **Dependencias Opcionales (mejoran rendimiento y robustez):**
    - `tenacity`: Retry logic avanzado con exponential backoff
    - `pybreaker`: Circuit breaker para protección contra fallos
    - `cachetools`: Caché TTL para idempotencia
    - `pydantic`: Validación robusta de datos con modelos tipados
    - `dnspython`: Validación DNS de dominios de email (MX records)
    - `prometheus_client`: Exportación de métricas Prometheus
    - `boto3`: Exportación de métricas a S3 (opcional)
    - `structlog`: Logging estructurado mejorado
    - `concurrent.futures`: Procesamiento paralelo (incluido en Python 3.2+)
    
    **Dead Letter Queue:**
    Los contactos que fallan se guardan en `/tmp/post_event_followup_dlq.jsonl` por defecto.
    Puede configurarse con variable de entorno `POST_EVENT_DLQ_PATH`.
    
    **Variables de Entorno:**
    - `POST_EVENT_TIMEOUT`: Timeout por defecto (default: 30.0)
    - `HTTP_TIMEOUT`: Timeout para requests HTTP (default: 5.0)
    - `EMAIL_CACHE_TTL`: TTL del caché de emails en segundos (default: 3600)
    - `CONTACT_CACHE_TTL`: TTL del caché de contactos en segundos (default: 1800)
    - `POST_EVENT_BATCH_SIZE`: Tamaño de batch para procesamiento paralelo (default: 10)
    - `POST_EVENT_MAX_WORKERS`: Número máximo de workers (default: 4)
    - `POST_EVENT_DLQ_PATH`: Ruta del Dead Letter Queue
    
    **Feature Flags (Airflow Variables):**
    - `post_event_followup:enable_timing_optimization`: Habilitar optimización de timing (default: true)
    - `post_event_followup:enable_advanced_analytics`: Habilitar analytics avanzados (default: true)
    - `post_event_followup:enable_ab_testing`: Habilitar A/B testing (default: false)
    - `post_event_followup:enable_ml_scoring`: Habilitar scoring ML (default: false)
    
    **Checkpoints:**
    Los checkpoints se guardan en Airflow Variables con el prefijo `post_event_followup:checkpoint:`.
    Permiten reanudar procesamiento desde puntos de control si el DAG falla.
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email_webhook_url": Param("", type="string", minLength=1),
        "event_source": Param("feria", type="string", minLength=1),
        "followup_delay_hours": Param(24, type="integer", minimum=1, maximum=72),
        "email_from": Param("marketing@tu-dominio.com", type="string", minLength=3),
        "email_template": Param("", type="string"),
        "auto_create_call_task": Param(True, type="boolean"),
        "call_task_due_hours": Param(48, type="integer", minimum=1, maximum=168),
        "dry_run": Param(False, type="boolean"),
        "request_timeout": Param(30, type="integer", minimum=5, maximum=120),
        "max_contacts_per_run": Param(100, type="integer", minimum=1, maximum=500),
        "enable_html_emails": Param(True, type="boolean"),
        "slack_webhook_url": Param("", type="string"),
        "email_subject_template": Param("", type="string"),
        "email_body_template": Param("", type="string"),
        "enable_parallel_processing": Param(False, type="boolean"),
        "max_retry_attempts": Param(3, type="integer", minimum=1, maximum=10),
        "batch_size": Param(10, type="integer", minimum=1, maximum=50),
        "max_workers": Param(4, type="integer", minimum=1, maximum=10),
        "enable_dlq": Param(True, type="boolean"),
        "enable_circuit_breaker": Param(True, type="boolean"),
        "enable_quality_analysis": Param(True, type="boolean"),
        "enable_duplicate_check": Param(True, type="boolean"),
        "min_quality_score": Param(0, type="integer", minimum=0, maximum=100),
    },
    tags=["sales", "events", "followup", "automation"],
    dagrun_timeout=timedelta(minutes=60),
    max_active_runs=1,
    on_success_callback=lambda context: notify_slack(":white_check_mark: post_event_followup DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: post_event_followup DAG failed"),
)
def post_event_followup() -> None:
    """
    DAG para automatización de seguimiento post-evento de ferias.
    """
    
    def render_template_advanced(template: str, variables: Dict[str, Any]) -> str:
        """
        Renderiza template con variables avanzadas.
        Soporta {{variable}}, {{variable|default}}, {{variable|upper}}, etc.
        """
        if not template:
            return ""
        
        def replace_var(match):
            var_expr = match.group(1)
            parts = var_expr.split("|")
            var_name = parts[0].strip()
            value = variables.get(var_name, "")
            
            # Aplicar filtros
            for filter_name in parts[1:]:
                filter_name = filter_name.strip()
                if filter_name.startswith("default"):
                    default_val = filter_name.split(":", 1)[1] if ":" in filter_name else ""
                    value = value or default_val
                elif filter_name == "upper":
                    value = str(value).upper()
                elif filter_name == "lower":
                    value = str(value).lower()
                elif filter_name == "title":
                    value = str(value).title()
                elif filter_name == "capitalize":
                    value = str(value).capitalize()
            
            return str(value) if value else ""
        
        result = re.sub(r'\{\{([^}]+)\}\}', replace_var, template)
        return result
    
    def generate_html_email(body_text: str, contact: Dict[str, Any]) -> str:
        """
        Genera versión HTML del email con estilo profesional.
        """
        first_name = contact.get("first_name") or "Estimado/a"
        company = contact.get("company") or "nuestra empresa"
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .button {{ display: inline-block; padding: 12px 24px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Gracias por visitarnos</h1>
                </div>
                <div class="content">
                    {body_text.replace(chr(10), '<br>')}
                </div>
                <div class="footer">
                    <p>Este es un email automático de seguimiento post-evento.</p>
                    <p>Si tienes alguna pregunta, no dudes en contactarnos.</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def generate_contact_id(contact: Dict[str, Any]) -> str:
        """Genera ID único para contacto basado en email y timestamp."""
        email = contact.get("email", "")
        created_at = contact.get("created_at", "")
        key = f"{email}_{created_at}"
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def validate_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
        """Valida contacto usando Pydantic si está disponible."""
        if PYDANTIC_AVAILABLE and ContactModel:
            try:
                validated = ContactModel(**contact)
                return validated.dict()
            except ValidationError as e:
                logger.warning(f"Error validando contacto {contact.get('email')}: {e}")
                # Retornar contacto original si falla validación
                return contact
        return contact
    
    def check_duplicate(contact: Dict[str, Any], hook: PostgresHook) -> bool:
        """Verifica si el contacto ya fue procesado (duplicado)."""
        email = contact.get("email", "").lower().strip()
        if not email:
            return False
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Buscar si ya existe un seguimiento post-evento para este email
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM sales_followup_tasks t
                        JOIN sales_pipeline p ON t.pipeline_id = p.id
                        WHERE p.email = %s
                        AND t.metadata->>'post_event_followup' = 'true'
                        AND t.created_at >= NOW() - INTERVAL '7 days'
                    """, (email,))
                    
                    count = cur.fetchone()[0]
                    return count > 0
        except Exception as e:
            logger.error(f"Error verificando duplicado para {email}: {e}")
            return False
    
    def validate_email_domain(email: str) -> Dict[str, Any]:
        """Valida dominio de email con DNS."""
        if not email or "@" not in email:
            return {"valid": False, "reason": "invalid_format"}
        
        domain = email.split("@")[1].lower()
        
        # Verificar si es email temporal
        is_disposable = domain in DISPOSABLE_EMAIL_DOMAINS or any(
            temp in domain for temp in ["temp", "fake", "test", "throwaway"]
        )
        
        # Verificar MX records si DNS está disponible
        has_mx = False
        if DNS_AVAILABLE and not is_disposable:
            try:
                mx_records = dns.resolver.resolve(domain, 'MX')
                has_mx = len(mx_records) > 0
            except Exception:
                has_mx = False
        
        return {
            "valid": True,
            "domain": domain,
            "is_disposable": is_disposable,
            "has_mx": has_mx,
            "is_enterprise": domain.endswith((".com", ".org", ".net", ".edu", ".gov"))
        }
    
    def analyze_sentiment(message: str) -> Dict[str, Any]:
        """Analiza el sentimiento de un mensaje usando heurísticas."""
        if not message:
            return {"sentiment": "neutral", "sentiment_score": 0.0, "confidence": 0.5}
        
        message_lower = message.lower()
        
        positive_words = ["interesado", "interesante", "me gusta", "excelente", "genial", 
                         "perfecto", "bueno", "buena", "sí", "yes", "definitivamente", 
                         "quiero", "necesito", "urgente", "importante", "gracias", 
                         "thanks", "espero", "deseo", "me encanta", "excelente"]
        negative_words = ["no", "not", "nunca", "never", "mala", "bad", "terrible", 
                         "problema", "problem", "error", "queja", "complaint", 
                         "cancelar", "cancel", "devolución", "refund", "insatisfecho"]
        neutral_words = ["información", "info", "consulta", "pregunta", "question", 
                        "más", "more", "detalles", "details"]
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        neutral_count = sum(1 for word in neutral_words if word in message_lower)
        
        total_words = positive_count + negative_count + neutral_count
        sentiment_score = (positive_count - negative_count) / max(total_words, 1) if total_words > 0 else 0.0
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        if sentiment_score > 0.3:
            sentiment = "positive"
        elif sentiment_score < -0.3:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        confidence = min(1.0, total_words / 5.0) if total_words > 0 else 0.5
        
        return {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 3),
            "confidence": round(confidence, 2),
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "message_length": len(message)
        }
    
    def predict_conversion(contact: Dict[str, Any]) -> Dict[str, Any]:
        """Predice probabilidad de conversión basada en múltiples factores."""
        factors = {}
        conversion_score = 0
        
        # Factor 1: Quality score (40% peso)
        quality_score = contact.get("quality_analysis", {}).get("quality_score", 0)
        conversion_score += quality_score * 0.4
        factors["quality_contribution"] = quality_score * 0.4
        
        # Factor 2: Segmentación (30% peso)
        primary_segment = contact.get("segmentation", {}).get("primary_segment", "unknown")
        segment_scores = {
            "high_quality": 80,
            "enterprise_email": 75,
            "event_source": 70,
            "medium_quality": 50,
            "has_company": 45,
            "other_source": 40,
            "low_quality": 20,
            "disposable_email": 10
        }
        segment_score = segment_scores.get(primary_segment, 30)
        conversion_score += segment_score * 0.3
        factors["segment_contribution"] = segment_score * 0.3
        
        # Factor 3: Sentimiento (20% peso)
        sentiment = contact.get("sentiment_analysis", {}).get("sentiment", "neutral")
        sentiment_scores = {"positive": 70, "neutral": 40, "negative": 20}
        sentiment_score = sentiment_scores.get(sentiment, 40)
        conversion_score += sentiment_score * 0.2
        factors["sentiment_contribution"] = sentiment_score * 0.2
        
        # Factor 4: Email validation (10% peso)
        email_validation = contact.get("email_validation", {})
        if email_validation.get("is_enterprise"):
            conversion_score += 10
            factors["enterprise_email_boost"] = 10
        elif email_validation.get("is_disposable"):
            conversion_score -= 10
            factors["disposable_email_penalty"] = -10
        
        conversion_score = max(0, min(conversion_score, 100))
        conversion_probability = conversion_score / 100
        
        if conversion_probability >= 0.7:
            conversion_category = "high"
            days_to_convert = 7
        elif conversion_probability >= 0.5:
            conversion_category = "medium"
            days_to_convert = 14
        elif conversion_probability >= 0.3:
            conversion_category = "low"
            days_to_convert = 30
        else:
            conversion_category = "very_low"
            days_to_convert = 60
        
        return {
            "conversion_score": round(conversion_score, 2),
            "conversion_probability": round(conversion_probability, 3),
            "conversion_category": conversion_category,
            "estimated_days_to_convert": days_to_convert,
            "factors": factors
        }
    
    def calculate_contact_value(contact: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula el valor estimado del contacto basado en múltiples factores."""
        value_score = 0
        value_factors = {}
        
        # Factor 1: Quality score (40% peso)
        quality_score = contact.get("quality_analysis", {}).get("quality_score", 0)
        value_score += quality_score * 0.4
        value_factors["quality_contribution"] = quality_score * 0.4
        
        # Factor 2: Conversion probability (30% peso)
        conversion_prob = contact.get("conversion_prediction", {}).get("conversion_probability", 0.5)
        conversion_value = conversion_prob * 100
        value_score += conversion_value * 0.3
        value_factors["conversion_contribution"] = conversion_value * 0.3
        
        # Factor 3: Segmentación (20% peso)
        primary_segment = contact.get("segmentation", {}).get("primary_segment", "unknown")
        segment_values = {
            "high_quality": 80,
            "enterprise_email": 90,
            "event_source": 70,
            "medium_quality": 50,
            "has_company": 60,
            "other_source": 40,
            "low_quality": 20,
            "disposable_email": 10
        }
        segment_value = segment_values.get(primary_segment, 30)
        value_score += segment_value * 0.2
        value_factors["segment_contribution"] = segment_value * 0.2
        
        # Factor 4: Sentimiento (10% peso)
        sentiment = contact.get("sentiment_analysis", {}).get("sentiment", "neutral")
        sentiment_scores = {"positive": 70, "neutral": 40, "negative": 20}
        sentiment_score = sentiment_scores.get(sentiment, 40)
        value_score += sentiment_score * 0.1
        value_factors["sentiment_contribution"] = sentiment_score * 0.1
        
        # Normalizar a 0-100
        value_score = max(0, min(value_score, 100))
        
        # Estimar valor monetario (heurística simple)
        estimated_value = None
        if value_score >= 80:
            estimated_value = 5000  # Alto valor
            value_tier = "very_high"
        elif value_score >= 60:
            estimated_value = 2000  # Valor medio-alto
            value_tier = "high"
        elif value_score >= 40:
            estimated_value = 1000  # Valor medio
            value_tier = "medium"
        elif value_score >= 20:
            estimated_value = 500  # Valor bajo
            value_tier = "low"
        else:
            estimated_value = 100  # Muy bajo valor
            value_tier = "very_low"
        
        # Ajustar por probabilidad de conversión
        if estimated_value:
            estimated_value = int(estimated_value * conversion_prob)
        
        return {
            "value_score": round(value_score, 2),
            "estimated_value_usd": estimated_value,
            "value_tier": value_tier,
            "factors": value_factors,
            "value_category": (
                "very_high" if value_score >= 80 else
                "high" if value_score >= 60 else
                "medium" if value_score >= 40 else
                "low" if value_score >= 20 else "very_low"
            )
        }
    
    def generate_insights(contact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera insights inteligentes sobre el contacto."""
        insights = []
        
        # Insight 1: Oportunidad de alto valor
        value_score = contact.get("value_analysis", {}).get("value_score", 0)
        if value_score >= 80:
            insights.append({
                "type": "high_value_opportunity",
                "priority": "high",
                "title": "Oportunidad de Alto Valor",
                "description": f"Contacto con value score de {value_score}, probablemente empresa enterprise",
                "recommended_action": "Asignar a representante senior inmediatamente"
            })
        
        # Insight 2: Alta probabilidad de conversión
        conversion_pred = contact.get("conversion_prediction", {})
        if conversion_pred.get("conversion_probability", 0) >= 0.7:
            insights.append({
                "type": "high_conversion_probability",
                "priority": "high",
                "title": "Alta Probabilidad de Conversión",
                "description": f"Probabilidad de conversión: {conversion_pred.get('conversion_probability', 0):.1%}, estimado {conversion_pred.get('estimated_days_to_convert', 0)} días",
                "recommended_action": "Acelerar proceso de seguimiento"
            })
        
        # Insight 3: Sentimiento positivo
        sentiment = contact.get("sentiment_analysis", {})
        if sentiment.get("sentiment") == "positive" and sentiment.get("confidence", 0) > 0.7:
            insights.append({
                "type": "positive_sentiment",
                "priority": "medium",
                "title": "Sentimiento Positivo",
                "description": "Contacto muestra sentimiento muy positivo, alta probabilidad de conversión",
                "recommended_action": "Priorizar contacto y ofrecer demo inmediata"
            })
        
        # Insight 4: Datos faltantes críticos
        missing_critical = []
        if not contact.get("phone"):
            missing_critical.append("teléfono")
        if not contact.get("company"):
            missing_critical.append("empresa")
        
        if missing_critical:
            insights.append({
                "type": "missing_critical_data",
                "priority": "medium",
                "title": "Datos Críticos Faltantes",
                "description": f"Faltan datos importantes: {', '.join(missing_critical)}",
                "recommended_action": "Solicitar información faltante en primer contacto"
            })
        
        # Insight 5: Segmento enterprise
        segmentation = contact.get("segmentation", {})
        if "enterprise_email" in segmentation.get("segments", []):
            insights.append({
                "type": "enterprise_segment",
                "priority": "high",
                "title": "Contacto Enterprise",
                "description": "Contacto clasificado como empresa enterprise",
                "recommended_action": "Asignar a equipo enterprise con pricing especializado"
            })
        
        # Ordenar por prioridad
        priority_order = {"high": 0, "medium": 1, "low": 2}
        insights.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
        
        return insights
    
    def generate_recommendations(contact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Genera recomendaciones de acciones basadas en el análisis del contacto."""
        recommendations = []
        quality_grade = contact.get("quality_analysis", {}).get("grade", "F")
        primary_segment = contact.get("segmentation", {}).get("primary_segment", "unknown")
        conversion_prob = contact.get("conversion_prediction", {}).get("conversion_probability", 0.5)
        sentiment = contact.get("sentiment_analysis", {}).get("sentiment", "neutral")
        
        # Recomendaciones basadas en calidad
        if quality_grade in ["A", "B"]:
            recommendations.append({
                "type": "action",
                "priority": "high",
                "action": "contact_immediately",
                "reason": "High quality contact, prioritize follow-up"
            })
        elif quality_grade == "C":
            recommendations.append({
                "type": "action",
                "priority": "medium",
                "action": "contact_within_24h",
                "reason": "Medium quality contact"
            })
        
        # Recomendaciones basadas en probabilidad de conversión
        if conversion_prob >= 0.7:
            recommendations.append({
                "type": "strategy",
                "priority": "high",
                "action": "assign_to_top_rep",
                "reason": "High conversion probability"
            })
        elif conversion_prob < 0.3:
            recommendations.append({
                "type": "strategy",
                "priority": "low",
                "action": "nurture_sequence",
                "reason": "Low conversion probability, use nurturing"
            })
        
        # Recomendaciones basadas en sentimiento
        if sentiment == "positive":
            recommendations.append({
                "type": "timing",
                "priority": "high",
                "action": "fast_response",
                "reason": "Positive sentiment, capitalize on interest"
            })
        elif sentiment == "negative":
            recommendations.append({
                "type": "approach",
                "priority": "medium",
                "action": "address_concerns",
                "reason": "Negative sentiment detected, address concerns"
            })
        
        # Recomendaciones basadas en segmento
        if primary_segment == "enterprise_email":
            recommendations.append({
                "type": "strategy",
                "priority": "high",
                "action": "enterprise_approach",
                "reason": "Enterprise contact, use specialized approach"
            })
        elif primary_segment == "disposable_email":
            recommendations.append({
                "type": "validation",
                "priority": "medium",
                "action": "verify_contact",
                "reason": "Disposable email detected, verify contact"
            })
        
        # Recomendaciones basadas en datos faltantes
        if not contact.get("phone"):
            recommendations.append({
                "type": "data_collection",
                "priority": "medium",
                "action": "request_phone",
                "reason": "Phone number missing"
            })
        
        if not contact.get("company"):
            recommendations.append({
                "type": "data_collection",
                "priority": "low",
                "action": "request_company",
                "reason": "Company information missing"
            })
        
        # Ordenar por prioridad
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 2))
        
        return recommendations
    
    def optimize_contact_timing(contact: Dict[str, Any], hook: PostgresHook) -> Dict[str, Any]:
        """Optimiza el timing de contacto basado en datos históricos."""
        try:
            email = contact.get("email")
            if not email:
                return contact
            
            # Buscar datos históricos de engagement
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Buscar respuestas anteriores del contacto
                    cur.execute("""
                        SELECT 
                            EXTRACT(HOUR FROM created_at) as hour,
                            EXTRACT(DOW FROM created_at) as day_of_week,
                            COUNT(*) as response_count
                        FROM leads
                        WHERE email = %s
                            AND metadata->>'email_opened' = 'true'
                            AND created_at > NOW() - INTERVAL '90 days'
                        GROUP BY hour, day_of_week
                        ORDER BY response_count DESC
                        LIMIT 1
                    """, (email,))
                    
                    result = cur.fetchone()
                    if result:
                        optimal_hour = int(result[0]) if result[0] else 10
                        optimal_day = int(result[1]) if result[1] else 1  # Lunes
                        
                        # Calcular próxima hora óptima
                        now = datetime.utcnow()
                        next_optimal = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
                        
                        # Si ya pasó hoy, programar para el próximo día óptimo
                        if next_optimal < now:
                            days_ahead = (optimal_day - now.weekday()) % 7
                            if days_ahead == 0:
                                days_ahead = 7
                            next_optimal = next_optimal + timedelta(days=days_ahead)
                        
                        is_optimal_time = (
                            now.hour == optimal_hour and
                            now.weekday() == optimal_day
                        )
                        
                        contact["contact_timing"] = {
                            "optimal_hour": optimal_hour,
                            "optimal_day_of_week": optimal_day,
                            "next_optimal_time": next_optimal.isoformat(),
                            "is_optimal_time": is_optimal_time,
                            "days_until_optimal": (next_optimal - now).days,
                            "recommended_action": "contact_now" if is_optimal_time else f"contact_at_{next_optimal.isoformat()}"
                        }
                    else:
                        # Default: horario de oficina
                        contact["contact_timing"] = {
                            "optimal_hour": 10,
                            "optimal_day_of_week": 1,
                            "next_optimal_time": None,
                            "is_optimal_time": False,
                            "recommended_action": "use_default_timing"
                        }
        except Exception as e:
            logger.debug(f"Error optimizing contact timing: {e}")
            contact["contact_timing"] = {"error": str(e)}
        
        return contact
    
    def segment_contact(contact: Dict[str, Any]) -> Dict[str, Any]:
        """Segmenta contacto basado en múltiples factores."""
        segments = []
        quality_grade = contact.get("quality_analysis", {}).get("grade", "F")
        source = contact.get("source", "").lower()
        company = contact.get("company")
        
        # Segmento por calidad
        if quality_grade in ["A", "B"]:
            segments.append("high_quality")
        elif quality_grade == "C":
            segments.append("medium_quality")
        else:
            segments.append("low_quality")
        
        # Segmento por source
        if source in ["feria", "event", "trade_show"]:
            segments.append("event_source")
        elif source:
            segments.append("other_source")
        
        # Segmento por empresa
        if company:
            segments.append("has_company")
        else:
            segments.append("no_company")
        
        # Segmento por email
        email_validation = contact.get("email_validation", {})
        if email_validation.get("is_disposable"):
            segments.append("disposable_email")
        elif email_validation.get("is_enterprise"):
            segments.append("enterprise_email")
        
        primary_segment = segments[0] if segments else "unknown"
        
        return {
            "segments": segments,
            "primary_segment": primary_segment,
            "segment_count": len(segments)
        }
    
    def analyze_contact_quality(contact: Dict[str, Any]) -> Dict[str, Any]:
        """Analiza la calidad del contacto."""
        quality_score = 0
        factors = {}
        
        # Validar email
        email = contact.get("email", "")
        if email:
            email_validation = validate_email_domain(email)
            contact["email_validation"] = email_validation
            
            if email_validation.get("valid"):
                quality_score += 10
                factors["valid_email"] = True
            if email_validation.get("has_mx"):
                quality_score += 5
                factors["has_mx"] = True
            if email_validation.get("is_enterprise"):
                quality_score += 5
                factors["enterprise_email"] = True
            if email_validation.get("is_disposable"):
                quality_score -= 15
                factors["disposable_email"] = True
        
        # Completitud de datos (max 40 puntos)
        if contact.get("first_name") and contact.get("last_name"):
            quality_score += 15
            factors["has_full_name"] = True
        if contact.get("email"):
            quality_score += 10
            factors["has_email"] = True
        if contact.get("phone"):
            quality_score += 10
            factors["has_phone"] = True
        if contact.get("company"):
            quality_score += 5
            factors["has_company"] = True
        
        # Calidad de source (max 20 puntos)
        source = contact.get("source", "").lower()
        if source in ["feria", "event", "trade_show"]:
            quality_score += 15
            factors["event_source"] = True
        elif source:
            quality_score += 5
            factors["has_source"] = True
        
        # UTM tracking (max 20 puntos)
        if contact.get("utm_campaign"):
            quality_score += 10
            factors["has_campaign"] = True
        if contact.get("utm_source"):
            quality_score += 10
            factors["has_utm_source"] = True
        
        # Metadata (max 20 puntos)
        if contact.get("metadata"):
            quality_score += 10
            factors["has_metadata"] = True
        
        quality_score = min(quality_score, 100)
        
        grade = (
            "A" if quality_score >= 80 else
            "B" if quality_score >= 60 else
            "C" if quality_score >= 40 else
            "D" if quality_score >= 20 else "F"
        )
        
        return {
            "quality_score": quality_score,
            "grade": grade,
            "factors": factors
        }
    
    @task(task_id="get_event_contacts")
    def get_event_contacts() -> List[Dict[str, Any]]:
        """
        Obtiene contactos registrados en ferias hace aproximadamente 1 día.
        Busca en una ventana de tiempo para capturar contactos del día anterior.
        Con idempotencia mejorada usando caché.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        event_source = str(params["event_source"])
        followup_delay_hours = int(params["followup_delay_hours"])
        max_contacts = int(params["max_contacts_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        now = datetime.utcnow()
        
        # Calcular ventana de tiempo: contactos registrados hace ~1 día
        # Ventana: (followup_delay_hours - 4) hasta (followup_delay_hours + 4) horas atrás
        # Esto captura contactos registrados aproximadamente hace 1 día
        window_start = now - timedelta(hours=followup_delay_hours + 4)
        window_end = now - timedelta(hours=followup_delay_hours - 4)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar contactos de ferias en la ventana de tiempo
                # Excluir contactos que ya tienen seguimiento post-evento procesado
                cur.execute("""
                    SELECT DISTINCT
                        l.ext_id,
                        l.email,
                        l.first_name,
                        l.last_name,
                        l.phone,
                        l.company,
                        l.source,
                        l.utm_source,
                        l.utm_campaign,
                        l.created_at,
                        l.metadata,
                        p.id as pipeline_id,
                        p.assigned_to
                    FROM leads l
                    LEFT JOIN sales_pipeline p ON l.ext_id = p.lead_ext_id
                    LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id 
                        AND t.task_type = 'call' 
                        AND t.metadata->>'post_event_followup' = 'true'
                    WHERE l.source = %s
                        AND l.created_at >= %s
                        AND l.created_at <= %s
                        AND l.email IS NOT NULL
                        AND t.id IS NULL  -- No tiene tarea de seguimiento post-evento ya creada
                    ORDER BY l.created_at DESC
                    LIMIT %s
                """, (event_source, window_start, window_end, max_contacts))
                
                columns = [desc[0] for desc in cur.description]
                contacts = []
                
                for row in cur.fetchall():
                    contact = dict(zip(columns, row))
                    # Convertir datetime a string ISO para serialización
                    if contact.get("created_at"):
                        contact["created_at"] = contact["created_at"].isoformat()
                    
                    # Validar contacto
                    contact = validate_contact(contact)
                    
                    # Verificar duplicados en BD
                    if check_duplicate(contact, hook):
                        logger.debug(f"Contacto {contact.get('email')} ya procesado (duplicado), saltando")
                        continue
                    
                    # Generar ID único y verificar idempotencia
                    contact_id = generate_contact_id(contact)
                    contact["_contact_id"] = contact_id
                    
                    # Verificar si ya fue procesado (usando caché)
                    if CACHE_AVAILABLE and contact_id in processed_contacts_cache:
                        logger.debug(f"Contacto {contact.get('email')} ya procesado (caché), saltando")
                        continue
                    
                    # Análisis de calidad
                    quality_analysis = analyze_contact_quality(contact)
                    contact["quality_analysis"] = quality_analysis
                    
                    # Segmentación
                    segmentation = segment_contact(contact)
                    contact["segmentation"] = segmentation
                    
                    # Análisis de sentimiento (si hay mensaje en metadata)
                    metadata = contact.get("metadata") or {}
                    if isinstance(metadata, str):
                        try:
                            metadata = json.loads(metadata)
                        except Exception:
                            metadata = {}
                    message = metadata.get("message") or metadata.get("notes") or ""
                    if message:
                        sentiment_analysis = analyze_sentiment(message)
                        contact["sentiment_analysis"] = sentiment_analysis
                    
                    # Predicción de conversión
                    conversion_prediction = predict_conversion(contact)
                    contact["conversion_prediction"] = conversion_prediction
                    
                    # Cálculo de valor
                    value_analysis = calculate_contact_value(contact)
                    contact["value_analysis"] = value_analysis
                    
                    # Generar insights
                    insights = generate_insights(contact)
                    contact["insights"] = insights
                    
                    # Generar recomendaciones
                    recommendations = generate_recommendations(contact)
                    contact["recommendations"] = recommendations
                    
                    # Optimizar timing de contacto (si feature flag está habilitado)
                    if get_feature_flag("enable_timing_optimization", True):
                        try:
                            hook_temp = PostgresHook(postgres_conn_id=conn_id)
                            contact = optimize_contact_timing(contact, hook_temp)
                        except Exception as e:
                            logger.debug(f"Error optimizing timing: {e}")
                    
                    # A/B Testing (si está habilitado)
                    if get_feature_flag("enable_ab_testing", False):
                        email = contact.get("email", "")
                        if email:
                            ab_group = assign_ab_group(email, "email_template")
                            contact["ab_group"] = ab_group
                            contact["ab_variant"] = get_ab_variant(ab_group, "email_template")
                    
                    # Multi-channel Attribution
                    attribution = calculate_attribution(contact)
                    contact["attribution"] = attribution
                    
                    # Filtrar por calidad mínima si está configurado
                    min_quality = int(params.get("min_quality_score", 0))
                    if quality_analysis["quality_score"] < min_quality:
                        logger.debug(f"Contacto {contact.get('email')} no cumple calidad mínima ({quality_analysis['quality_score']} < {min_quality})")
                        continue
                    
                    contacts.append(contact)
        
        logger.info(f"Encontrados {len(contacts)} contactos de ferias para seguimiento")
        
        # Análisis de calidad agregado
        if contacts:
            avg_quality = sum(c.get("quality_analysis", {}).get("quality_score", 0) for c in contacts) / len(contacts)
            high_quality = sum(1 for c in contacts if c.get("quality_analysis", {}).get("grade") in ["A", "B"])
            logger.info(f"Calidad promedio: {avg_quality:.1f}, Alta calidad (A/B): {high_quality}/{len(contacts)}")
        
        # Registrar métricas
        try:
            Stats.incr("post_event_followup.contacts_found", len(contacts))
            if contacts:
                avg_quality = sum(c.get("quality_analysis", {}).get("quality_score", 0) for c in contacts) / len(contacts)
                Stats.incr("post_event_followup.avg_quality_score", int(avg_quality))
                
                # Métricas Prometheus
                if PROMETHEUS_AVAILABLE:
                    for contact in contacts:
                        grade = contact.get("quality_analysis", {}).get("grade", "F")
                        post_event_contacts_processed.labels(status="found", quality_grade=grade).inc()
                        post_event_quality_score.observe(contact.get("quality_analysis", {}).get("quality_score", 0))
        except Exception:
            pass
        
        return contacts
    
    @task(task_id="send_followup_emails")
    def send_followup_emails(contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Envía emails personalizados de seguimiento a cada contacto.
        Con retry logic mejorado, soporte HTML y performance profiling.
        """
        ctx = get_current_context()
        params = ctx["params"]
        webhook_url = str(params["email_webhook_url"])
        email_from = str(params["email_from"])
        email_template = str(params.get("email_template", ""))
        email_subject_template = str(params.get("email_subject_template", ""))
        email_body_template = str(params.get("email_body_template", ""))
        enable_html = bool(params.get("enable_html_emails", True))
        dry_run = bool(params["dry_run"])
        timeout = int(params["request_timeout"])
        max_retries = int(params.get("max_retry_attempts", 3))
        
        if not webhook_url:
            logger.warning("email_webhook_url no configurado, saltando envío de emails")
            return contacts
        
        def send_single_email(contact: Dict[str, Any]) -> Dict[str, Any]:
            """Envía email a un contacto con retry logic."""
            email = contact.get("email")
            first_name = contact.get("first_name") or "Estimado/a"
            last_name = contact.get("last_name") or ""
            company = contact.get("company") or ""
            
            # Preparar variables para template
            template_vars = {
                "first_name": first_name,
                "last_name": last_name,
                "full_name": f"{first_name} {last_name}".strip(),
                "company": company,
                "email": email,
                "event_source": contact.get("source", "feria"),
                "utm_campaign": contact.get("utm_campaign", ""),
            }
            
            # Renderizar subject
            if email_subject_template:
                subject = render_template_advanced(email_subject_template, template_vars)
            elif email_template:
                subject = email_template.split("\n")[0]
                subject = render_template_advanced(subject, template_vars)
            else:
                subject = f"Gracias por visitarnos en nuestra feria - {first_name}"
            
            # Renderizar body
            if email_body_template:
                body_text = render_template_advanced(email_body_template, template_vars)
            elif email_template:
                body_lines = email_template.split("\n")[1:] if "\n" in email_template else [email_template]
                body_text = "\n".join(body_lines)
                body_text = render_template_advanced(body_text, template_vars)
            else:
                # Template por defecto mejorado
                body_text = f"""Hola {first_name},

¡Gracias por visitar nuestro stand en la feria y por tu interés en nuestros productos/servicios!

Fue un placer conocerte y esperamos que la información que compartimos contigo haya sido útil.

Nos encantaría continuar la conversación y explorar cómo podemos ayudarte a alcanzar tus objetivos.

¿Te gustaría programar una llamada breve para discutir tus necesidades específicas? Estamos aquí para ayudarte.

Quedamos atentos a tu respuesta.

Saludos cordiales,
El equipo de Ventas

---
Este es un email automático de seguimiento post-evento."""
            
            payload = {
                "from": email_from,
                "to": email,
                "subject": subject,
                "text": body_text,
                "metadata": {
                    "lead_ext_id": contact.get("ext_id"),
                    "source": "post_event_followup",
                    "event_source": contact.get("source"),
                    "template": "post_event_custom" if email_template else "post_event_default"
                }
            }
            
            # Agregar HTML si está habilitado
            if enable_html:
                payload["html"] = generate_html_email(body_text, contact)
            
            if dry_run:
                logger.info(f"[DRY RUN] Email sería enviado a {email}: {subject}")
                contact["email_sent"] = False
                contact["email_sent_at"] = None
                return contact
            
            # Enviar con retry logic y circuit breaker
            def send_email_request():
                response = requests.post(
                    webhook_url,
                    json=payload,
                    timeout=timeout
                )
                response.raise_for_status()
                return response
            
            # Aplicar retry si está disponible
            if TENACITY_AVAILABLE:
                send_email_request = retry(
                    stop=stop_after_attempt(max_retries),
                    wait=wait_exponential(multiplier=1, min=2, max=30),
                    retry=retry_if_exception_type((requests.RequestException,)),
                    reraise=True
                )(send_email_request)
            
            # Aplicar circuit breaker si está disponible
            if CIRCUIT_BREAKER_AVAILABLE and email_circuit_breaker:
                send_email_request = email_circuit_breaker(send_email_request)
            
            try:
                send_email_request()
                contact["email_sent"] = True
                contact["email_sent_at"] = datetime.utcnow().isoformat()
                logger.info(f"Email enviado exitosamente a {email}")
                
                # Registrar métricas
                try:
                    Stats.incr("post_event_followup.email_sent", 1)
                    if PROMETHEUS_AVAILABLE:
                        post_event_emails_sent.labels(status="success").inc()
                except Exception:
                    pass
            except Exception as e:
                logger.error(f"Error enviando email a {email} después de {max_retries} intentos: {e}", exc_info=True)
                contact["email_sent"] = False
                contact["email_error"] = str(e)
                
                # Registrar métricas de error
                try:
                    Stats.incr("post_event_followup.email_failed", 1)
                    if PROMETHEUS_AVAILABLE:
                        post_event_emails_sent.labels(status="failed").inc()
                except Exception:
                    pass
            
            return contact
        
        # Procesar contactos con performance profiling
        with _profiler.time("send_followup_emails"):
            
            # Procesar contactos (con o sin paralelización)
            enable_parallel = bool(params.get("enable_parallel_processing", False))
            enable_adaptive_batch = bool(params.get("enable_adaptive_batch", True))
            batch_size = int(params.get("batch_size", BATCH_SIZE))
            if enable_adaptive_batch:
                batch_size = _adaptive_batch_sizer.current_size
            max_workers = int(params.get("max_workers", MAX_WORKERS))
            enable_dlq = bool(params.get("enable_dlq", True))
            
            results = []
        
            if enable_parallel and CONCURRENT_AVAILABLE and len(contacts) > batch_size:
                # Procesamiento paralelo en batches
                logger.info(f"Procesando {len(contacts)} contactos en paralelo (workers: {max_workers})")
                
                def process_batch(batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                    batch_results = []
                    for contact in batch:
                        try:
                            result = send_single_email(contact)
                            batch_results.append(result)
                        except Exception as e:
                            logger.error(f"Error procesando contacto {contact.get('email')}: {e}", exc_info=True)
                            contact["email_sent"] = False
                            contact["email_error"] = str(e)
                            batch_results.append(contact)
                    return batch_results
                
                # Dividir en batches
                batches = [contacts[i:i + batch_size] for i in range(0, len(contacts), batch_size)]
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_batch = {executor.submit(process_batch, batch): batch for batch in batches}
                    
                    for future in as_completed(future_to_batch):
                        batch = future_to_batch[future]
                        try:
                            batch_results = future.result()
                            results.extend(batch_results)
                        except Exception as e:
                            logger.error(f"Error procesando batch: {e}", exc_info=True)
                            # Guardar batch completo en DLQ
                            if enable_dlq:
                                for contact in batch:
                                    save_to_dlq(contact, str(e), ctx)
                                    contact["email_sent"] = False
                                    contact["email_error"] = str(e)
                                    results.append(contact)
            else:
                # Procesamiento secuencial
                for contact in contacts:
                    try:
                        result = send_single_email(contact)
                        results.append(result)
                        
                        # Marcar como procesado en caché
                        if CACHE_AVAILABLE and result.get("_contact_id"):
                            processed_contacts_cache[result["_contact_id"]] = True
                    except Exception as e:
                        logger.error(f"Error procesando contacto {contact.get('email')}: {e}", exc_info=True)
                        contact["email_sent"] = False
                        contact["email_error"] = str(e)
                        
                        # Guardar en DLQ si está habilitado
                        if enable_dlq:
                            save_to_dlq(contact, str(e), ctx)
                        
                        results.append(contact)
            
            sent_count = sum(1 for c in results if c.get("email_sent"))
            failed_count = len(results) - sent_count
            success_rate = (sent_count / len(results) * 100) if results else 0
            
            # Performance stats
            perf_stats = _profiler.get_stats("send_followup_emails")
            if perf_stats:
                avg_time = perf_stats.get('avg', 0)
                p95_time = perf_stats.get('p95', 0)
                logger.info(f"Performance: {avg_time:.2f}s promedio, {p95_time:.2f}s p95")
                
                # Registrar en Prometheus
                if PROMETHEUS_AVAILABLE and post_event_processing_time:
                    post_event_processing_time.observe(avg_time)
                
                # Ajustar batch size adaptativo si está habilitado
                if enable_adaptive_batch and len(results) > 0:
                    error_rate = (failed_count / len(results) * 100) if results else 0
                    _adaptive_batch_sizer.calculate_optimal_size(
                        success_rate=success_rate,
                        avg_duration=avg_time * 1000,  # Convertir a ms
                        error_rate=error_rate
                    )
                    logger.info(f"Batch size adaptativo ajustado a: {_adaptive_batch_sizer.current_size}")
            
            logger.info(f"Emails procesados: {sent_count} enviados, {failed_count} fallidos de {len(results)} totales")
            
            # Notificar si hay muchos fallos
            if failed_count > 0:
                failure_rate = failed_count / len(results) if results else 0
                if failure_rate > 0.2:  # Más del 20% de fallos
                    notify_slack(f"⚠️ post_event_followup: {failed_count}/{len(results)} emails fallaron ({failure_rate*100:.1f}%)")
                
                # Registrar métrica de fallos
                try:
                    Stats.incr("post_event_followup.email_failures", failed_count)
                except Exception:
                    pass
            
            return results
    
    @task(task_id="create_call_followup_tasks")
    def create_call_followup_tasks(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea tareas de llamada de seguimiento para cada contacto procesado.
        Optimizado con batch processing para mejor rendimiento.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        auto_create = bool(params["auto_create_call_task"])
        call_task_due_hours = int(params["call_task_due_hours"])
        dry_run = bool(params["dry_run"])
        batch_size = int(params.get("batch_size", BATCH_SIZE))
        
        if not auto_create:
            logger.info("Auto-creación de tareas deshabilitada")
            return {"created": 0, "skipped": len(contacts), "errors": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Procesar en batches para mejor rendimiento
        total_stats = {"created": 0, "skipped": 0, "errors": 0}
        
        if len(contacts) > batch_size:
            # Procesar en batches
            batches = [contacts[i:i + batch_size] for i in range(0, len(contacts), batch_size)]
            logger.info(f"Procesando {len(contacts)} contactos en {len(batches)} batches")
            
            for i, batch in enumerate(batches, 1):
                logger.info(f"Procesando batch {i}/{len(batches)} ({len(batch)} contactos)")
                batch_stats = process_contacts_batch(batch, hook, call_task_due_hours, dry_run)
                
                total_stats["created"] += batch_stats["created"]
                total_stats["skipped"] += batch_stats["skipped"]
                total_stats["errors"] += batch_stats["errors"]
        else:
            # Procesar todos juntos si son pocos
            total_stats = process_contacts_batch(contacts, hook, call_task_due_hours, dry_run)
        
        logger.info(f"Tareas de seguimiento: {total_stats['created']} creadas, {total_stats['skipped']} saltadas, {total_stats['errors']} errores")
        return total_stats
    
    @task(task_id="analyze_cohorts")
    def analyze_cohorts_task(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analiza contactos agrupados por cohorte (fecha de registro).
        """
        cohort_analysis = analyze_cohorts(contacts)
        logger.info(f"Análisis de cohortes: {cohort_analysis['total_cohorts']} cohortes identificadas")
        return cohort_analysis
    
    @task(task_id="analyze_temporal_trends")
    def analyze_temporal_trends_task(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analiza tendencias temporales comparando con ejecuciones anteriores.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        trends = analyze_temporal_trends(contacts, hook)
        
        if trends.get("has_trends"):
            logger.info(f"Tendencias detectadas: {trends.get('metrics', {})}")
        else:
            logger.info("No hay suficientes datos históricos para análisis de tendencias")
        
        return trends
    
    @task(task_id="detect_anomalies")
    def detect_anomalies_task(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detecta anomalías avanzadas en los datos de contactos.
        """
        anomalies = detect_advanced_anomalies(contacts)
        
        if anomalies["anomaly_count"] > 0:
            logger.warning(f"Anomalías detectadas: {anomalies['anomaly_count']} (severidad: {anomalies['severity']})")
            for anomaly in anomalies["anomalies"]:
                logger.warning(f"  - {anomaly['type']}: {anomaly['description']}")
        else:
            logger.info("No se detectaron anomalías")
        
        return anomalies
    
    @task(task_id="export_metrics")
    def export_metrics_task(
        contacts: List[Dict[str, Any]],
        executive_report: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Exporta métricas a S3 para análisis a largo plazo.
        """
        ctx = get_current_context()
        params = ctx["params"]
        enable_s3_export = bool(params.get("enable_s3_export", False))
        s3_bucket = str(params.get("s3_bucket", ""))
        
        if not enable_s3_export or not s3_bucket or not S3_AVAILABLE:
            return {"exported": False, "reason": "S3 export disabled or not configured"}
        
        try:
            dag_run_id = ctx.get("dag_run", {}).get("run_id", "unknown")
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            s3_key = f"post_event_followup/{timestamp}_{dag_run_id}.json"
            
            export_data = {
                "dag_run_id": dag_run_id,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": executive_report.get("summary", {}),
                "channels": executive_report.get("channels", {}),
                "cohorts": executive_report.get("cohorts", {}),
                "trends": trends,
                "anomalies": anomalies,
                "contacts_count": len(contacts),
                "recommendations": executive_report.get("recommendations", [])
            }
            
            exported = export_to_s3(export_data, s3_bucket, s3_key)
            
            if exported:
                logger.info(f"Métricas exportadas a S3: s3://{s3_bucket}/{s3_key}")
                return {"exported": True, "s3_path": f"s3://{s3_bucket}/{s3_key}"}
            else:
                return {"exported": False, "reason": "S3 export failed"}
        except Exception as e:
            logger.error(f"Error exportando métricas a S3: {e}", exc_info=True)
            return {"exported": False, "error": str(e)}
    
    @task(task_id="generate_executive_report")
    def generate_executive_report(
        contacts: List[Dict[str, Any]], 
        tasks_stats: Dict[str, Any],
        cohort_analysis: Dict[str, Any],
        trends: Dict[str, Any],
        anomalies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera reporte ejecutivo con métricas clave y recomendaciones.
        """
        total_contacts = len(contacts)
        emails_sent = sum(1 for c in contacts if c.get("email_sent"))
        emails_failed = total_contacts - emails_sent
        success_rate = (emails_sent / total_contacts * 100) if total_contacts > 0 else 0
        
        avg_quality = sum(c.get("quality_analysis", {}).get("quality_score", 0) for c in contacts) / total_contacts if contacts else 0
        avg_conversion_prob = sum(c.get("conversion_prediction", {}).get("conversion_probability", 0) for c in contacts) / total_contacts if contacts else 0
        total_value = sum(c.get("value_analysis", {}).get("estimated_value_usd", 0) for c in contacts)
        
        # Análisis de canales
        channels = defaultdict(int)
        for contact in contacts:
            primary_channel = contact.get("attribution", {}).get("primary_channel", "unknown")
            channels[primary_channel] += 1
        
        # Recomendaciones ejecutivas
        recommendations = []
        if success_rate < 80:
            recommendations.append({
                "priority": "high",
                "action": "Investigar causas de fallos en envío de emails",
                "reason": f"Tasa de éxito del {success_rate:.1f}% está por debajo del objetivo"
            })
        
        if avg_quality < 50:
            recommendations.append({
                "priority": "medium",
                "action": "Mejorar calidad de datos de contactos",
                "reason": f"Calidad promedio de {avg_quality:.1f} puntos es baja"
            })
        
        if total_value > 10000:
            recommendations.append({
                "priority": "high",
                "action": "Priorizar seguimiento de contactos de alto valor",
                "reason": f"Valor total estimado de ${total_value:,.2f} USD"
            })
        
        report = {
            "summary": {
                "total_contacts": total_contacts,
                "emails_sent": emails_sent,
                "emails_failed": emails_failed,
                "success_rate": round(success_rate, 2),
                "avg_quality_score": round(avg_quality, 2),
                "avg_conversion_probability": round(avg_conversion_prob, 3),
                "total_estimated_value_usd": round(total_value, 2),
                "tasks_created": tasks_stats.get("created", 0)
            },
            "channels": dict(channels),
            "cohorts": cohort_analysis.get("cohorts", {}),
            "trends": trends,
            "anomalies": anomalies,
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Agregar recomendaciones basadas en anomalías
        if anomalies.get("severity") == "high":
            recommendations.append({
                "priority": "high",
                "action": "Revisar anomalías detectadas inmediatamente",
                "reason": f"Se detectaron {anomalies.get('anomaly_count', 0)} anomalías con severidad alta"
            })
        
        # Agregar recomendaciones basadas en tendencias
        if trends.get("has_trends"):
            growth = trends.get("metrics", {}).get("growth", {})
            if growth.get("contacts", 0) < -20:
                recommendations.append({
                    "priority": "medium",
                    "action": "Investigar disminución en volumen de contactos",
                    "reason": f"Volumen disminuyó {abs(growth.get('contacts', 0)):.1f}% vs promedio histórico"
                })
        
        logger.info("=" * 60)
        logger.info("REPORTE EJECUTIVO - SEGUIMIENTO POST-EVENTO")
        logger.info("=" * 60)
        logger.info(f"Total contactos: {report['summary']['total_contacts']}")
        logger.info(f"Tasa de éxito: {report['summary']['success_rate']:.1f}%")
        logger.info(f"Valor total estimado: ${report['summary']['total_estimated_value_usd']:,.2f} USD")
        logger.info(f"Canales principales: {', '.join(report['channels'].keys())}")
        logger.info(f"Recomendaciones: {len(recommendations)}")
        logger.info("=" * 60)
        
        # Guardar reporte en BD si es posible
        try:
            ctx = get_current_context()
            params = ctx["params"]
            conn_id = str(params["postgres_conn_id"])
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS post_event_executive_reports (
                                id SERIAL PRIMARY KEY,
                                dag_run_id VARCHAR(256),
                                report_data JSONB,
                                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                            )
                        """)
                        cur.execute("""
                            INSERT INTO post_event_executive_reports (dag_run_id, report_data)
                            VALUES (%s, %s)
                        """, (ctx.get("dag_run_id"), json.dumps(report)))
                        conn.commit()
                        logger.info("Reporte ejecutivo guardado en BD")
                    except Exception as e:
                        logger.debug(f"No se pudo guardar reporte en BD: {e}")
        except Exception as e:
            logger.debug(f"Error guardando reporte: {e}")
        
        return report
    
    @task(task_id="create_audit_trail")
    def create_audit_trail(contacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crea registro de auditoría completo del procesamiento.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        audit_summary = {
            "dag_run_id": ctx.get("dag_run_id"),
            "processing_timestamp": datetime.utcnow().isoformat(),
            "total_contacts": len(contacts),
            "contacts_processed": []
        }
        
        for contact in contacts:
            contact_audit = {
                "lead_ext_id": contact.get("ext_id"),
                "email": contact.get("email"),
                "quality_grade": contact.get("quality_analysis", {}).get("grade"),
                "quality_score": contact.get("quality_analysis", {}).get("quality_score"),
                "primary_segment": contact.get("segmentation", {}).get("primary_segment"),
                "conversion_probability": contact.get("conversion_prediction", {}).get("conversion_probability"),
                "sentiment": contact.get("sentiment_analysis", {}).get("sentiment"),
                "email_sent": contact.get("email_sent", False),
                "recommendations_count": len(contact.get("recommendations", [])),
                "processing_steps": {
                    "validated": contact.get("quality_analysis") is not None,
                    "segmented": contact.get("segmentation") is not None,
                    "conversion_predicted": contact.get("conversion_prediction") is not None,
                    "recommendations_generated": len(contact.get("recommendations", [])) > 0
                }
            }
            audit_summary["contacts_processed"].append(contact_audit)
        
        # Guardar en BD si es posible
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    try:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS post_event_audit_trail (
                                id SERIAL PRIMARY KEY,
                                dag_run_id VARCHAR(256),
                                audit_data JSONB,
                                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                            )
                        """)
                        cur.execute("""
                            INSERT INTO post_event_audit_trail (dag_run_id, audit_data)
                            VALUES (%s, %s)
                        """, (audit_summary["dag_run_id"], json.dumps(audit_summary)))
                        conn.commit()
                        logger.info("Audit trail guardado en BD")
                    except Exception as e:
                        logger.debug(f"No se pudo guardar audit trail en BD: {e}")
        except Exception as e:
            logger.debug(f"Error guardando audit trail: {e}")
        
        return audit_summary
    
    @task(task_id="log_summary")
    def log_summary(contacts: List[Dict[str, Any]], tasks_stats: Dict[str, Any]) -> None:
        """
        Registra un resumen del procesamiento para auditoría y seguimiento.
        """
        ctx = get_current_context()
        emails_sent = sum(1 for c in contacts if c.get("email_sent"))
        emails_failed = sum(1 for c in contacts if not c.get("email_sent") and c.get("email"))
        
        # Estadísticas avanzadas
        avg_quality = sum(c.get("quality_analysis", {}).get("quality_score", 0) for c in contacts) / len(contacts) if contacts else 0
        high_quality_count = sum(1 for c in contacts if c.get("quality_analysis", {}).get("grade") in ["A", "B"])
        avg_conversion_prob = sum(c.get("conversion_prediction", {}).get("conversion_probability", 0) for c in contacts) / len(contacts) if contacts else 0
        positive_sentiment_count = sum(1 for c in contacts if c.get("sentiment_analysis", {}).get("sentiment") == "positive")
        total_recommendations = sum(len(c.get("recommendations", [])) for c in contacts)
        total_insights = sum(len(c.get("insights", [])) for c in contacts)
        total_value = sum(c.get("value_analysis", {}).get("estimated_value_usd", 0) for c in contacts)
        high_value_count = sum(1 for c in contacts if c.get("value_analysis", {}).get("value_tier") in ["very_high", "high"])
        
        summary = {
            "total_contacts": len(contacts),
            "emails_sent": emails_sent,
            "emails_failed": emails_failed,
            "call_tasks_created": tasks_stats.get("created", 0),
            "call_tasks_skipped": tasks_stats.get("skipped", 0),
            "call_tasks_errors": tasks_stats.get("errors", 0),
            "avg_quality_score": round(avg_quality, 2),
            "high_quality_count": high_quality_count,
            "avg_conversion_probability": round(avg_conversion_prob, 3),
            "positive_sentiment_count": positive_sentiment_count,
            "total_recommendations": total_recommendations,
            "total_insights": total_insights,
            "total_value_usd": total_value,
            "high_value_count": high_value_count,
            "processing_time": datetime.utcnow().isoformat()
        }
        
        logger.info("=" * 60)
        logger.info("RESUMEN DE SEGUIMIENTO POST-EVENTO")
        logger.info("=" * 60)
        logger.info(f"Total de contactos procesados: {summary['total_contacts']}")
        logger.info(f"Emails enviados: {summary['emails_sent']}")
        logger.info(f"Emails fallidos: {summary['emails_failed']}")
        logger.info(f"Tareas de llamada creadas: {summary['call_tasks_created']}")
        logger.info(f"Tareas de llamada saltadas: {summary['call_tasks_skipped']}")
        logger.info(f"Errores en tareas: {summary['call_tasks_errors']}")
        logger.info(f"Calidad promedio: {summary['avg_quality_score']}")
        logger.info(f"Contactos alta calidad (A/B): {summary['high_quality_count']}")
        logger.info(f"Probabilidad conversión promedio: {summary['avg_conversion_probability']}")
        logger.info(f"Sentimiento positivo: {summary['positive_sentiment_count']}")
        logger.info(f"Total recomendaciones: {summary['total_recommendations']}")
        logger.info(f"Total insights: {summary['total_insights']}")
        logger.info(f"Valor total estimado: ${summary['total_value_usd']:,.2f} USD")
        logger.info(f"Contactos alto valor: {summary['high_value_count']}")
        logger.info("=" * 60)
        
        # Registrar métricas
        try:
            Stats.incr("post_event_followup.contacts_processed", summary["total_contacts"])
            Stats.incr("post_event_followup.emails_sent", summary["emails_sent"])
            Stats.incr("post_event_followup.emails_failed", summary["emails_failed"])
            Stats.incr("post_event_followup.call_tasks_created", summary["call_tasks_created"])
            Stats.incr("post_event_followup.call_tasks_errors", summary["call_tasks_errors"])
        except Exception as e:
            logger.debug(f"No se pudieron registrar métricas: {e}")
        
        # Notificación Slack opcional
        slack_url = ctx["params"].get("slack_webhook_url", "")
        if slack_url and summary["total_contacts"] > 0:
            try:
                success_rate = (summary['emails_sent'] / summary['total_contacts'] * 100) if summary['total_contacts'] > 0 else 0
                message = f"""
📊 *Seguimiento Post-Evento Completado*

✅ Contactos procesados: {summary['total_contacts']}
📧 Emails enviados: {summary['emails_sent']} ({success_rate:.1f}%)
❌ Emails fallidos: {summary['emails_failed']}
📞 Tareas de llamada creadas: {summary['call_tasks_created']}
⚠️ Errores: {summary['call_tasks_errors']}
"""
                notify_slack(message)
            except Exception as e:
                logger.debug(f"No se pudo enviar notificación Slack: {e}")
    
    @task(task_id="check_dlq", trigger_rule="none_failed")
    def check_dlq() -> Dict[str, Any]:
        """
        Verifica el estado del Dead Letter Queue y reporta estadísticas.
        """
        ctx = get_current_context()
        enable_dlq = bool(ctx["params"].get("enable_dlq", True))
        
        if not enable_dlq or not os.path.exists(DLQ_PATH):
            return {"dlq_size": 0, "dlq_path": DLQ_PATH}
        
        try:
            # Contar líneas en DLQ
            dlq_size = 0
            with open(DLQ_PATH, "r") as f:
                for _ in f:
                    dlq_size += 1
            
            logger.info(f"Dead Letter Queue contiene {dlq_size} registros")
            
            # Registrar métricas
            try:
                Stats.incr("post_event_followup.dlq.size", dlq_size)
                if PROMETHEUS_AVAILABLE and post_event_dlq_size:
                    post_event_dlq_size.set(dlq_size)
            except Exception:
                pass
            
            # Alertar si hay muchos registros en DLQ
            if dlq_size > 50:
                notify_slack(f"⚠️ post_event_followup: DLQ tiene {dlq_size} registros pendientes. Revisar necesario.")
            
            return {
                "dlq_size": dlq_size,
                "dlq_path": DLQ_PATH,
                "warning": dlq_size > 50
            }
        except Exception as e:
            logger.error(f"Error verificando DLQ: {e}", exc_info=True)
            return {"dlq_size": 0, "dlq_path": DLQ_PATH, "error": str(e)}
    
    @task(task_id="acquire_lock")
    def acquire_lock() -> Dict[str, Any]:
        """
        Adquiere lock distribuido para prevenir ejecuciones concurrentes.
        """
        ctx = get_current_context()
        params = ctx["params"]
        enable_lock = bool(params.get("enable_distributed_lock", True))
        
        if not enable_lock:
            return {"locked": True, "skip_lock": True}
        
        dag_run_id = ctx.get("dag_run", {}).get("run_id", "default")
        lock_key = f"post_event_followup:execution_lock:{dag_run_id}"
        timeout_seconds = int(params.get("lock_timeout_seconds", 3600))
        
        acquired = acquire_distributed_lock(lock_key, timeout_seconds)
        
        if not acquired:
            try:
                lock_data = Variable.get(lock_key, default_var=None)
                if lock_data:
                    lock_info = json.loads(lock_data)
                    raise AirflowFailException(
                        f"Another execution is already running. Lock acquired at: {lock_info.get('acquired_at', 'unknown')}"
                    )
            except AirflowFailException:
                raise
            except Exception:
                pass
            raise AirflowFailException("Failed to acquire execution lock. Another run may be in progress.")
        
        logger.info(f"Execution lock acquired: {lock_key}")
        return {"locked": True, "lock_key": lock_key}
    
    @task(task_id="release_lock", trigger_rule="all_done")
    def release_lock(lock_info: Dict[str, Any]) -> None:
        """Libera el lock distribuido."""
        if lock_info.get("skip_lock"):
            return
        
        lock_key = lock_info.get("lock_key")
        if lock_key:
            release_distributed_lock(lock_key)
            logger.info(f"Execution lock released: {lock_key}")
    
    @task(task_id="health_check")
    def health_check() -> Dict[str, Any]:
        """
        Health check del sistema antes de procesar contactos.
        Verifica conectividad con servicios críticos.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        webhook_url = str(params.get("email_webhook_url", ""))
        
        health_status = {
            "status": "healthy",
            "checks": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Verificar PostgreSQL
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    health_status["checks"]["postgres"] = "ok"
        except Exception as e:
            health_status["checks"]["postgres"] = f"error: {str(e)}"
            health_status["status"] = "degraded"
            logger.warning(f"Health check PostgreSQL falló: {e}")
        
        # Verificar email webhook (si está configurado)
        if webhook_url:
            try:
                response = requests.head(webhook_url, timeout=5)
                health_status["checks"]["email_webhook"] = "ok" if response.status_code < 500 else "degraded"
            except Exception as e:
                health_status["checks"]["email_webhook"] = f"error: {str(e)}"
                health_status["status"] = "degraded"
                logger.warning(f"Health check email webhook falló: {e}")
        
        # Verificar circuit breaker
        if CIRCUIT_BREAKER_AVAILABLE and email_circuit_breaker:
            state = email_circuit_breaker.current_state if hasattr(email_circuit_breaker, 'current_state') else "unknown"
            health_status["checks"]["circuit_breaker"] = "closed" if state == "closed" else "open"
        
        # Verificar caché
        if CACHE_AVAILABLE:
            cache_size = len(processed_contacts_cache) if isinstance(processed_contacts_cache, dict) else 0
            health_status["checks"]["cache"] = f"ok (size: {cache_size})"
        
        logger.info(f"Health check completado: {health_status['status']}")
        return health_status
    
    @task(task_id="optimize_queries")
    def optimize_queries() -> Dict[str, Any]:
        """
        Optimiza queries y verifica índices necesarios.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        optimizations = {
            "indexes_checked": [],
            "queries_optimized": 0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Verificar índices importantes
                    indexes_to_check = [
                        ("leads", "source", "idx_leads_source"),
                        ("leads", "created_at", "idx_leads_created_at"),
                        ("sales_followup_tasks", "metadata", "idx_followup_tasks_metadata_gin"),
                    ]
                    
                    for table, column, index_name in indexes_to_check:
                        cur.execute("""
                            SELECT EXISTS (
                                SELECT 1 FROM pg_indexes 
                                WHERE tablename = %s AND indexname = %s
                            )
                        """, (table, index_name))
                        
                        exists = cur.fetchone()[0]
                        if not exists:
                            logger.warning(f"Índice {index_name} no existe en {table}.{column}")
                            optimizations["indexes_checked"].append({
                                "table": table,
                                "column": column,
                                "index": index_name,
                                "exists": False
                            })
                        else:
                            optimizations["indexes_checked"].append({
                                "table": table,
                                "column": column,
                                "index": index_name,
                                "exists": True
                            })
                    
                    # ANALYZE para actualizar estadísticas
                    cur.execute("ANALYZE leads")
                    cur.execute("ANALYZE sales_pipeline")
                    cur.execute("ANALYZE sales_followup_tasks")
                    conn.commit()
                    
                    optimizations["queries_optimized"] = 3
                    logger.info("Queries optimizadas y estadísticas actualizadas")
        except Exception as e:
            logger.error(f"Error en optimización de queries: {e}", exc_info=True)
            optimizations["error"] = str(e)
        
        return optimizations
    
    def process_contacts_batch(contacts: List[Dict[str, Any]], hook: PostgresHook, 
                              call_task_due_hours: int, dry_run: bool) -> Dict[str, Any]:
        """
        Procesa un batch de contactos para crear tareas.
        Optimizado para batch processing.
        """
        stats = {"created": 0, "skipped": 0, "errors": 0}
        now = datetime.utcnow()
        due_date = now + timedelta(hours=call_task_due_hours)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Preparar datos para inserción batch
                pipeline_updates = []
                task_inserts = []
                
                for contact in contacts:
                    pipeline_id = contact.get("pipeline_id")
                    lead_ext_id = contact.get("ext_id")
                    
                    if not pipeline_id:
                        # Insertar pipeline si no existe
                        try:
                            cur.execute("""
                                INSERT INTO sales_pipeline (
                                    lead_ext_id, email, first_name, last_name, phone,
                                    score, priority, source, utm_source, utm_campaign,
                                    stage, qualified_at, metadata, created_at
                                ) VALUES (
                                    %s, %s, %s, %s, %s,
                                    50, 'medium', %s, %s, %s,
                                    'qualified', NOW(), %s, NOW()
                                )
                                ON CONFLICT (lead_ext_id) DO UPDATE SET
                                    updated_at = NOW()
                                RETURNING id
                            """, (
                                lead_ext_id,
                                contact.get("email"),
                                contact.get("first_name"),
                                contact.get("last_name"),
                                contact.get("phone"),
                                contact.get("source"),
                                contact.get("utm_source"),
                                contact.get("utm_campaign"),
                                json.dumps(contact.get("metadata", {}))
                            ))
                            
                            result = cur.fetchone()
                            pipeline_id = result[0] if result else None
                            contact["pipeline_id"] = pipeline_id
                        except Exception as e:
                            logger.error(f"Error creando pipeline para {lead_ext_id}: {e}")
                            stats["errors"] += 1
                            continue
                    
                    if not pipeline_id:
                        stats["skipped"] += 1
                        continue
                    
                    # Preparar inserción de tarea
                    first_name = contact.get("first_name") or "Contacto"
                    task_title = f"Llamada de seguimiento post-evento: {first_name} {contact.get('last_name', '')}".strip()
                    task_description = f"""Seguimiento post-evento para contacto registrado en feria.

Contacto: {contact.get('email')}
Registrado: {contact.get('created_at', 'N/A')}

Email de seguimiento: {'Enviado' if contact.get('email_sent') else 'No enviado'}
"""
                    
                    if not dry_run:
                        task_inserts.append((
                            pipeline_id,
                            lead_ext_id,
                            "call",
                            task_title,
                            task_description,
                            "pending",
                            "medium",
                            contact.get("assigned_to"),
                            due_date,
                            json.dumps({
                                "post_event_followup": "true",
                                "event_source": contact.get("source"),
                                "email_sent": contact.get("email_sent", False),
                                "email_sent_at": contact.get("email_sent_at")
                            })
                        ))
                        pipeline_updates.append((due_date, pipeline_id))
                
                # Inserción batch de tareas
                if task_inserts and not dry_run:
                    try:
                        cur.executemany("""
                            INSERT INTO sales_followup_tasks (
                                pipeline_id, lead_ext_id, task_type, task_title,
                                task_description, status, priority, assigned_to,
                                due_date, metadata, created_at
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
                            )
                        """, task_inserts)
                        
                        # Actualización batch de pipeline
                        if pipeline_updates:
                            cur.executemany("""
                                UPDATE sales_pipeline
                                SET next_followup_at = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, pipeline_updates)
                        
                        conn.commit()
                        stats["created"] = len(task_inserts)
                        logger.info(f"Batch procesado: {stats['created']} tareas creadas")
                    except Exception as e:
                        logger.error(f"Error en batch processing: {e}", exc_info=True)
                        conn.rollback()
                        stats["errors"] += len(task_inserts)
                elif dry_run:
                    stats["created"] = len(task_inserts)
        
        return stats
    
    # Pipeline mejorado con distributed locking, health check y optimización
    lock_info = acquire_lock()
    health = health_check()
    optimize = optimize_queries()
    contacts = get_event_contacts()
    contacts_with_emails = send_followup_emails(contacts)
    tasks_stats = create_call_followup_tasks(contacts_with_emails)
    cohort_analysis = analyze_cohorts_task(contacts_with_emails)
    trends = analyze_temporal_trends_task(contacts_with_emails)
    anomalies = detect_anomalies_task(contacts_with_emails)
    executive_report = generate_executive_report(contacts_with_emails, tasks_stats, cohort_analysis, trends, anomalies)
    metrics_export = export_metrics_task(contacts_with_emails, executive_report, trends, anomalies)
    audit_trail = create_audit_trail(contacts_with_emails)
    dlq_stats = check_dlq()
    log_summary(contacts_with_emails, tasks_stats)
    release_lock(lock_info)


dag = post_event_followup()


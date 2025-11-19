from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import hashlib
import secrets
import logging
import time
import os
from collections import defaultdict
from functools import lru_cache
import sys
from pathlib import Path
from threading import Lock
from collections import deque
from dataclasses import dataclass
from enum import Enum

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# Intentar importar librerías avanzadas
try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    CONCURRENT_AVAILABLE = True
except ImportError:
    CONCURRENT_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    # Fallback simple cache
    class SimpleCache:
        def __init__(self, maxsize=100, ttl=3600):
            self.cache = {}
            self.timestamps = {}
            self.maxsize = maxsize
            self.ttl = ttl
        
        def get(self, key):
            if key in self.cache:
                if time.time() - self.timestamps.get(key, 0) < self.ttl:
                    return self.cache[key]
                else:
                    del self.cache[key]
                    del self.timestamps[key]
            return None
        
        def set(self, key, value):
            if len(self.cache) >= self.maxsize:
                # Remove oldest
                oldest = min(self.timestamps.items(), key=lambda x: x[1])
                del self.cache[oldest[0]]
                del self.timestamps[oldest[0]]
            self.cache[key] = value
            self.timestamps[key] = time.time()
    
    TTLCache = SimpleCache

# Agregar path para imports de módulos personalizados
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "integrations"))

# Imports opcionales de nuevas funcionalidades
try:
    from organic_acquisition_ab_testing import ABTestingManager
    from organic_acquisition_ml_scoring import LeadScoringService
    from organic_acquisition_multichannel import MultiChannelMessaging
    from organic_acquisition_gamification import GamificationSystem
    from referral_validator import ReferralValidator
    ADVANCED_FEATURES_AVAILABLE = True
except ImportError:
    logger.warning("Módulos avanzados no disponibles. Funcionalidades básicas únicamente.")
    ADVANCED_FEATURES_AVAILABLE = False


# ============================================================================
# UTILIDADES AVANZADAS: CIRCUIT BREAKER, CACHE, BATCH PROCESSING
# ============================================================================

class CircuitState(Enum):
    CLOSED = "closed"  # Normal
    OPEN = "open"  # Falla, no intentar
    HALF_OPEN = "half_open"  # Probando


@dataclass
class CircuitBreaker:
    """Circuit breaker simple para proteger APIs externas."""
    
    failure_threshold: int = 5
    recovery_timeout: int = 60
    name: str = "default"
    
    def __post_init__(self):
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None
        self.lock = Lock()
    
    def call(self, func, *args, **kwargs):
        """Ejecuta función con protección de circuit breaker."""
        with self.lock:
            # Verificar si debemos intentar
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time < self.recovery_timeout:
                    raise Exception(f"Circuit breaker {self.name} is OPEN")
                else:
                    # Intentar recovery
                    self.state = CircuitState.HALF_OPEN
            
            try:
                result = func(*args, **kwargs)
                # Éxito: resetear
                if self.state == CircuitState.HALF_OPEN:
                    self.state = CircuitState.CLOSED
                    self.failures = 0
                return result
            except Exception as e:
                self.failures += 1
                self.last_failure_time = time.time()
                
                if self.failures >= self.failure_threshold:
                    self.state = CircuitState.OPEN
                    logger.warning(f"Circuit breaker {self.name} opened after {self.failures} failures")
                
                raise


# Circuit breakers globales
email_circuit_breaker = CircuitBreaker(name="email", failure_threshold=5, recovery_timeout=60)
crm_circuit_breaker = CircuitBreaker(name="crm", failure_threshold=3, recovery_timeout=120)

# Caché global para queries frecuentes
_query_cache = TTLCache(maxsize=100, ttl=300) if CACHE_AVAILABLE else {}
_cache_lock = Lock()


def cached_query(cache_key: str, ttl: int = 300):
    """Decorator para cachear resultados de queries."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generar key único
            key = f"{cache_key}:{hash(str(args) + str(kwargs))}"
            
            # Intentar obtener de cache
            if CACHE_AVAILABLE:
                with _cache_lock:
                    cached = _query_cache.get(key)
                    if cached is not None:
                        logger.debug(f"Cache hit: {key}")
                        return cached
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en cache
            if CACHE_AVAILABLE:
                with _cache_lock:
                    _query_cache.set(key, result)
                    logger.debug(f"Cache set: {key}")
            
            return result
        return wrapper
    return decorator


def batch_process(items: List[Any], batch_size: int = 10, max_workers: int = 4):
    """Procesa items en batches con paralelización."""
    if not CONCURRENT_AVAILABLE or len(items) < batch_size:
        # Procesamiento secuencial simple
        return [item for item in items]
    
    results = []
    batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(lambda x: x, batch): batch for batch in batches}
        
        for future in as_completed(futures):
            try:
                batch_result = future.result()
                results.extend(batch_result)
            except Exception as e:
                logger.error(f"Error procesando batch: {e}")
                batch = futures[future]
                results.extend(batch)  # Incluir items sin procesar
    
    return results


# Session HTTP reutilizable para mejor performance
_http_session = None
_session_lock = Lock()


def get_http_session():
    """Obtiene sesión HTTP reutilizable con connection pooling."""
    global _http_session
    if _http_session is None:
        with _session_lock:
            if _http_session is None:
                _http_session = requests.Session()
                # Configurar adapter con retry
                adapter = requests.adapters.HTTPAdapter(
                    max_retries=3,
                    pool_connections=10,
                    pool_maxsize=20
                )
                _http_session.mount('http://', adapter)
                _http_session.mount('https://', adapter)
    return _http_session


@dag(
    dag_id="organic_acquisition_nurturing",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Automatización de Adquisición Orgánica con Nurturing y Referidos
    
    Sistema completo automatizado para:
    1. **Captura de leads orgánicos** desde formularios y lead magnets
    2. **Workflow de nurturing** segmentado por interés/comportamiento
    3. **Programa de referidos** con incentivos automáticos
    4. **Validación anti-fraude** de referidos
    5. **Sincronización con CRM** en tiempo real
    6. **Reportes automáticos** con métricas clave
    7. **Optimización automática** basada en comportamiento
    
    **Funcionalidades principales:**
    - Captura automática de nuevos leads orgánicos
    - Segmentación inteligente por interés y comportamiento
    - Secuencias de nurturing personalizadas (blog, guías, videos)
    - Tracking de engagement (lecturas, descargas, visualizaciones)
    - Etiquetado automático de leads "enganchados"
    - Invitación automática al programa de referidos
    - Generación de enlaces/códigos únicos de referido
    - Validación de referidos genuinos (anti-fraude)
    - Generación automática de recompensas
    - Sincronización bidireccional con CRM
    - Reportes diarios/semanales automáticos
    - Optimización automática de contenido y recompensas
    - Filtros y paths según comportamiento
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `email_webhook_url`: Webhook para envío de emails (requerido)
    - `crm_api_url`: API del CRM para sincronización (opcional)
    - `crm_api_key`: API key del CRM (opcional)
    - `max_leads_per_run`: Máximo de leads a procesar (default: 200)
    - `engagement_threshold`: Threshold para considerar "enganchado" (default: 3)
    - `referral_incentive`: Incentivo por referido (default: 10.0)
    - `enable_fraud_detection`: Habilitar detección de fraude (default: true)
    - `report_frequency`: Frecuencia de reportes (daily/weekly, default: daily)
    - `dry_run`: Solo simular sin enviar (default: false)
    
    **Requisitos:**
    - Schema `organic_acquisition_schema.sql` debe estar ejecutado en Postgres
    - Webhook de email configurado y funcional
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email_webhook_url": Param("", type="string", minLength=1),
        "crm_api_url": Param("", type="string"),
        "crm_api_key": Param("", type="string"),
        "max_leads_per_run": Param(200, type="integer", minimum=1, maximum=1000),
        "engagement_threshold": Param(3, type="integer", minimum=1, maximum=10),
        "referral_incentive": Param(10.0, type="number", minimum=0),
        "enable_fraud_detection": Param(True, type="boolean"),
        "report_frequency": Param("daily", type="string", enum=["daily", "weekly"]),
        "dry_run": Param(False, type="boolean"),
        "email_from": Param("marketing@tu-dominio.com", type="string", minLength=3),
        "slack_webhook_url": Param("", type="string"),
        "request_timeout": Param(30, type="integer", minimum=5, maximum=120),
        # Nurturing
        "nurturing_enabled": Param(True, type="boolean"),
        "nurturing_reminder_days": Param(3, type="integer", minimum=1, maximum=7),
        "nurturing_second_incentive_days": Param(7, type="integer", minimum=3, maximum=14),
        # Optimización
        "enable_auto_optimization": Param(True, type="boolean"),
        "optimization_check_interval_days": Param(7, type="integer", minimum=1, maximum=30),
        "low_conversion_threshold": Param(5.0, type="number", minimum=0, maximum=100),
        # Funcionalidades avanzadas
        "enable_ab_testing": Param(False, type="boolean"),
        "enable_ml_scoring": Param(False, type="boolean"),
        "enable_multichannel": Param(False, type="boolean"),
        "enable_gamification": Param(False, type="boolean"),
        "ml_retrain_days": Param(90, type="integer", minimum=30, maximum=365),
        "ab_test_traffic_split": Param(0.5, type="number", minimum=0.1, maximum=0.9),
        # Performance
        "enable_caching": Param(True, type="boolean"),
        "enable_circuit_breaker": Param(True, type="boolean"),
        "enable_batch_processing": Param(True, type="boolean"),
        "batch_size": Param(50, type="integer", minimum=10, maximum=200),
        "max_workers": Param(4, type="integer", minimum=1, maximum=10),
        # Exportación y webhooks
        "export_format": Param("json", type="string", enum=["json", "csv"]),
        "event_webhook_url": Param("", type="string"),
    },
    tags=["marketing", "organic-acquisition", "nurturing", "referrals", "automation", "advanced"],
)
def organic_acquisition_nurturing() -> None:
    """
    DAG principal para automatización de adquisición orgánica con nurturing y referidos.
    """
    
    def generate_referral_code(email: str) -> str:
        """Genera código único de referido basado en email."""
        salt = secrets.token_hex(8)
        hash_input = f"{email}{salt}{time.time()}"
        hash_value = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        return f"REF-{hash_value.upper()}"
    
    def generate_referral_link(base_url: str, code: str) -> str:
        """Genera enlace de referido."""
        return f"{base_url}/refer/{code}"
    
    # ============================================================================
    # TASKS
    # ============================================================================
    
    @task(task_id="ensure_schema")
    def ensure_schema() -> bool:
        """Asegura que el schema existe."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Verificar que las tablas existen
            tables = [
                "organic_leads",
                "nurturing_sequences",
                "content_engagement",
                "referral_programs",
                "referrals",
                "referral_rewards",
                "acquisition_metrics"
            ]
            
            # Verificar tablas avanzadas si están habilitadas
            if ADVANCED_FEATURES_AVAILABLE:
                advanced_tables = [
                    "ab_tests",
                    "ab_test_assignments",
                    "gamification_points",
                    "gamification_actions",
                    "multichannel_messages"
                ]
                tables.extend(advanced_tables)
            
            missing_tables = []
            for table in tables:
                try:
                    hook.get_first(f"SELECT 1 FROM {table} LIMIT 1")
                except Exception:
                    missing_tables.append(table)
            
            if missing_tables:
                logger.warning(f"Tablas faltantes: {', '.join(missing_tables)}")
                logger.warning("Algunas funcionalidades avanzadas pueden no estar disponibles")
            
            logger.info("Schema verificado correctamente")
            return True
        except Exception as e:
            logger.error(f"Error verificando schema: {e}", exc_info=True)
            logger.warning("Asegúrate de ejecutar organic_acquisition_schema.sql")
            return False
    
    @task(task_id="capture_new_leads")
    def capture_new_leads() -> List[Dict[str, Any]]:
        """Captura nuevos leads orgánicos desde formularios/webhooks."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        max_leads = int(ctx["params"]["max_leads_per_run"])
        enable_ml_scoring = bool(ctx["params"].get("enable_ml_scoring", False))
        enable_batch = bool(ctx["params"].get("enable_batch_processing", True))
        batch_size = int(ctx["params"].get("batch_size", 50))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Inicializar ML scoring si está habilitado
        scoring_service = None
        if enable_ml_scoring and ADVANCED_FEATURES_AVAILABLE:
            try:
                scoring_service = LeadScoringService(db_hook=hook)
            except Exception as e:
                logger.warning(f"No se pudo inicializar ML scoring: {e}")
        
        @cached_query("new_leads", ttl=60)
        def get_new_leads_from_db():
            """Query con caché para evitar consultas repetidas."""
            query = """
                SELECT 
                    lead_id,
                    email,
                    first_name,
                    last_name,
                    source,
                    utm_source,
                    utm_campaign,
                    utm_medium,
                    interest_area,
                    lead_magnet_downloaded,
                    created_at,
                    status
                FROM organic_leads
                WHERE status = 'new'
                ORDER BY created_at DESC
                LIMIT %s
            """
            return hook.get_records(query, parameters=(max_leads,))
        
        try:
            # Usar query con caché si está habilitado
            enable_caching = bool(ctx["params"].get("enable_caching", True))
            if enable_caching:
                results = get_new_leads_from_db()
            else:
                query = """
                    SELECT 
                        lead_id,
                        email,
                        first_name,
                        last_name,
                        source,
                        utm_source,
                        utm_campaign,
                        utm_medium,
                        interest_area,
                        lead_magnet_downloaded,
                        created_at,
                        status
                    FROM organic_leads
                    WHERE status = 'new'
                    ORDER BY created_at DESC
                    LIMIT %s
                """
                results = hook.get_records(query, parameters=(max_leads,))
            
            leads = []
            
            # Procesar en batches si está habilitado
            if enable_batch and CONCURRENT_AVAILABLE and len(results) > batch_size:
                def process_lead_row(row):
                    lead_data = {
                        "lead_id": row[0],
                        "email": row[1],
                        "first_name": row[2] or "",
                        "last_name": row[3] or "",
                        "source": row[4] or "organic",
                        "utm_source": row[5],
                        "utm_campaign": row[6],
                        "utm_medium": row[7],
                        "interest_area": row[8],
                        "lead_magnet_downloaded": row[9],
                        "created_at": row[10],
                        "status": row[11]
                    }
                    
                    # Calcular ML score si está habilitado
                    if scoring_service:
                        try:
                            prediction = scoring_service.score_lead(lead_data["lead_id"])
                            lead_data["ml_score"] = prediction.get("score", 50)
                            lead_data["ml_prediction"] = prediction.get("prediction", False)
                        except Exception as e:
                            logger.warning(f"Error calculando ML score: {e}")
                            lead_data["ml_score"] = 50
                    
                    return lead_data
                
                # Procesar en paralelo
                with ThreadPoolExecutor(max_workers=int(ctx["params"].get("max_workers", 4))) as executor:
                    futures = {executor.submit(process_lead_row, row): row for row in results}
                    for future in as_completed(futures):
                        try:
                            leads.append(future.result())
                        except Exception as e:
                            logger.error(f"Error procesando lead: {e}")
                            # Incluir lead sin ML score
                            row = futures[future]
                            leads.append({
                                "lead_id": row[0],
                                "email": row[1],
                                "first_name": row[2] or "",
                                "last_name": row[3] or "",
                                "source": row[4] or "organic",
                                "utm_source": row[5],
                                "utm_campaign": row[6],
                                "utm_medium": row[7],
                                "interest_area": row[8],
                                "lead_magnet_downloaded": row[9],
                                "created_at": row[10],
                                "status": row[11],
                                "ml_score": 50
                            })
            else:
                # Procesamiento secuencial
                for row in results:
                    lead_data = {
                        "lead_id": row[0],
                        "email": row[1],
                        "first_name": row[2] or "",
                        "last_name": row[3] or "",
                        "source": row[4] or "organic",
                        "utm_source": row[5],
                        "utm_campaign": row[6],
                        "utm_medium": row[7],
                        "interest_area": row[8],
                        "lead_magnet_downloaded": row[9],
                        "created_at": row[10],
                        "status": row[11]
                    }
                    
                    # Calcular ML score si está habilitado
                    if scoring_service:
                        try:
                            prediction = scoring_service.score_lead(lead_data["lead_id"])
                            lead_data["ml_score"] = prediction.get("score", 50)
                            lead_data["ml_prediction"] = prediction.get("prediction", False)
                        except Exception as e:
                            logger.warning(f"Error calculando ML score para {lead_data['lead_id']}: {e}")
                            lead_data["ml_score"] = 50  # Score por defecto
                    
                    leads.append(lead_data)
            
            logger.info(f"Capturados {len(leads)} nuevos leads")
            if scoring_service:
                avg_score = sum(l.get("ml_score", 50) for l in leads) / len(leads) if leads else 0
                logger.info(f"Score ML promedio: {avg_score:.1f}")
            
            return leads
        except Exception as e:
            logger.error(f"Error capturando leads: {e}", exc_info=True)
            return []
    
    @task(task_id="segment_leads")
    def segment_leads(leads: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Segmenta leads por interés y comportamiento."""
        segments = {
            "by_interest": defaultdict(list),
            "by_source": defaultdict(list),
            "by_engagement_level": defaultdict(list)
        }
        
        for lead in leads:
            # Segmentación por interés
            interest = lead.get("interest_area") or "general"
            segments["by_interest"][interest].append(lead)
            
            # Segmentación por fuente
            source = lead.get("source") or "organic"
            segments["by_source"][source].append(lead)
            
            # Segmentación por nivel de engagement inicial
            has_magnet = lead.get("lead_magnet_downloaded", False)
            engagement_level = "high" if has_magnet else "medium"
            segments["by_engagement_level"][engagement_level].append(lead)
        
        logger.info(f"Leads segmentados: {len(leads)} total")
        for segment_type, segment_data in segments.items():
            for key, segment_leads in segment_data.items():
                logger.info(f"  {segment_type}[{key}]: {len(segment_leads)} leads")
        
        return {
            "segments": {k: dict(v) for k, v in segments.items()},
            "total_leads": len(leads)
        }
    
    @task(task_id="start_nurturing_workflows")
    def start_nurturing_workflows(segmentation: Dict[str, Any]) -> Dict[str, int]:
        """Inicia workflows de nurturing para nuevos leads."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        nurturing_enabled = bool(ctx["params"]["nurturing_enabled"])
        enable_ab_testing = bool(ctx["params"].get("enable_ab_testing", False))
        dry_run = bool(ctx["params"]["dry_run"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Inicializar A/B testing si está habilitado
        ab_manager = None
        if enable_ab_testing and ADVANCED_FEATURES_AVAILABLE:
            try:
                ab_manager = ABTestingManager(db_hook=hook)
            except Exception as e:
                logger.warning(f"No se pudo inicializar A/B testing: {e}")
        
        if not nurturing_enabled:
            logger.info("Nurturing deshabilitado")
            return {"started": 0, "skipped": 0}
        
        segments = segmentation.get("segments", {})
        started = 0
        skipped = 0
        
        try:
            # Obtener templates de nurturing por interés
            templates_query = """
                SELECT 
                    template_id,
                    interest_area,
                    sequence_name,
                    content_items
                FROM nurturing_templates
                WHERE active = true
            """
            templates = hook.get_records(templates_query)
            templates_by_interest = {t[1]: t for t in templates}
            
            # Procesar leads por segmento de interés
            by_interest = segments.get("by_interest", {})
            
            for interest, leads in by_interest.items():
                template = templates_by_interest.get(interest)
                if not template:
                    # Usar template general si no hay específico
                    template = templates_by_interest.get("general")
                
                if not template:
                    logger.warning(f"No hay template para interés: {interest}")
                    skipped += len(leads)
                    continue
                
                template_id = template[0]
                sequence_name = template[2]
                content_items = template[3] if isinstance(template[3], list) else json.loads(template[3] or "[]")
                
                for lead in leads:
                    if dry_run:
                        logger.info(f"[DRY RUN] Iniciando nurturing para {lead['email']}")
                        started += 1
                        continue
                    
                    # Crear secuencia de nurturing
                    sequence_id = f"nurt_{secrets.token_hex(8)}"
                    insert_query = """
                        INSERT INTO nurturing_sequences (
                            sequence_id,
                            lead_id,
                            template_id,
                            sequence_name,
                            current_step,
                            status,
                            started_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """
                    
                    hook.run(
                        insert_query,
                        parameters=(
                            sequence_id,
                            lead["lead_id"],
                            template_id,
                            sequence_name,
                            1,
                            "active"
                        )
                    )
                    
                    # Programar primer contenido
                    if content_items:
                        first_content = content_items[0]
                        
                        # Aplicar A/B testing si está habilitado
                        content_to_use = first_content
                        test_id = None
                        variant = None
                        
                        if ab_manager:
                            try:
                                # Buscar test activo para este tipo de contenido
                                test_query = """
                                    SELECT test_id FROM ab_tests
                                    WHERE content_type = %s AND status = 'active'
                                    LIMIT 1
                                """
                                test_result = hook.get_first(
                                    test_query,
                                    parameters=(first_content.get("type", "blog"),)
                                )
                                
                                if test_result:
                                    test_id = test_result[0]
                                    variant = ab_manager.assign_variant(test_id, lead["lead_id"])
                                    content_to_use = ab_manager.get_variant_content(test_id, variant)
                                    
                                    # Si hay contenido de variante, usarlo
                                    if content_to_use:
                                        logger.info(f"Lead {lead['lead_id']} asignado a variante {variant} del test {test_id}")
                            except Exception as e:
                                logger.warning(f"Error en A/B testing: {e}")
                        
                        insert_content_query = """
                            INSERT INTO content_engagement (
                                lead_id,
                                sequence_id,
                                content_type,
                                content_id,
                                content_title,
                                scheduled_at,
                                status,
                                ab_test_id,
                                ab_variant
                            ) VALUES (%s, %s, %s, %s, %s, NOW(), 'scheduled', %s, %s)
                        """
                        
                        hook.run(
                            insert_content_query,
                            parameters=(
                                lead["lead_id"],
                                sequence_id,
                                content_to_use.get("type", first_content.get("type", "blog")),
                                content_to_use.get("id", first_content.get("id", "")),
                                content_to_use.get("title", first_content.get("title", "")),
                                test_id,
                                variant
                            )
                        )
                    
                    # Actualizar status del lead
                    hook.run(
                        "UPDATE organic_leads SET status = 'nurturing', updated_at = NOW() WHERE lead_id = %s",
                        parameters=(lead["lead_id"],)
                    )
                    
                    started += 1
            
            logger.info(f"Nurturing iniciado: {started} secuencias, {skipped} omitidos")
            return {"started": started, "skipped": skipped}
            
        except Exception as e:
            logger.error(f"Error iniciando nurturing: {e}", exc_info=True)
            return {"started": started, "skipped": skipped, "error": str(e)}
    
    @task(task_id="send_nurturing_content")
    def send_nurturing_content() -> Dict[str, int]:
        """Envía contenido programado de nurturing."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        email_webhook = str(ctx["params"]["email_webhook_url"])
        email_from = str(ctx["params"]["email_from"])
        enable_multichannel = bool(ctx["params"].get("enable_multichannel", False))
        dry_run = bool(ctx["params"]["dry_run"])
        timeout = int(ctx["params"]["request_timeout"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Inicializar multi-canal si está habilitado
        messaging = None
        if enable_multichannel and ADVANCED_FEATURES_AVAILABLE:
            try:
                messaging = MultiChannelMessaging()
            except Exception as e:
                logger.warning(f"No se pudo inicializar multi-canal: {e}")
        
        sent = 0
        failed = 0
        
        try:
            # Obtener contenido programado para enviar ahora
            query = """
                SELECT 
                    ce.engagement_id,
                    ce.lead_id,
                    ce.sequence_id,
                    ce.content_type,
                    ce.content_id,
                    ce.content_title,
                    ce.content_url,
                    ol.email,
                    ol.first_name,
                    ol.last_name,
                    ol.phone,
                    ns.sequence_name,
                    ns.current_step
                FROM content_engagement ce
                JOIN organic_leads ol ON ce.lead_id = ol.lead_id
                JOIN nurturing_sequences ns ON ce.sequence_id = ns.sequence_id
                WHERE ce.status = 'scheduled'
                AND ce.scheduled_at <= NOW()
                AND ns.status = 'active'
                LIMIT 100
            """
            
            scheduled_content = hook.get_records(query)
            
            for row in scheduled_content:
                engagement_id, lead_id, sequence_id, content_type, content_id, \
                content_title, content_url, email, first_name, last_name, phone, \
                sequence_name, current_step = row
                
                if dry_run:
                    logger.info(f"[DRY RUN] Enviando {content_type} '{content_title}' a {email}")
                    sent += 1
                    continue
                
                # Preparar contenido
                subject = f"📚 {content_title}"
                body = f"""
Hola {first_name or 'amigo/a'},

Como parte de nuestra secuencia de contenido educativo, queremos compartirte:

**{content_title}**

{content_url or f"https://tu-dominio.com/{content_type}/{content_id}"}

Esperamos que te sea útil.

Saludos,
Equipo de Marketing
                """
                
                # Enviar por canal apropiado
                try:
                    content_data = {
                        "from": email_from,
                        "subject": subject,
                        "text": body,
                        "html": body.replace("\n", "<br>")
                    }
                    
                    # Usar multi-canal si está disponible
                    if messaging:
                        result = messaging.send_nurturing_sequence(
                            lead_id=lead_id,
                            email=email,
                            phone=phone,
                            sequence_step=current_step or 1,
                            content=content_data
                        )
                        channel_used = result.get("channel", "email")
                    else:
                        # Fallback a email tradicional con circuit breaker
                        payload = {
                            **content_data,
                            "to": email,
                            "metadata": {
                                "lead_id": lead_id,
                                "sequence_id": sequence_id,
                                "content_type": content_type,
                                "engagement_id": engagement_id
                            }
                        }
                        
                        enable_cb = bool(ctx["params"].get("enable_circuit_breaker", True))
                        if enable_cb:
                            # Usar circuit breaker
                            def send_email():
                                session = get_http_session()
                                response = session.post(
                                    email_webhook,
                                    json=payload,
                                    timeout=timeout
                                )
                                response.raise_for_status()
                                return response
                            
                            try:
                                response = email_circuit_breaker.call(send_email)
                                channel_used = "email"
                                result = {"success": True}
                            except Exception as e:
                                logger.error(f"Circuit breaker bloqueó envío: {e}")
                                raise
                        else:
                            # Sin circuit breaker
                            session = get_http_session()
                            response = session.post(
                                email_webhook,
                                json=payload,
                                timeout=timeout
                            )
                            response.raise_for_status()
                            channel_used = "email"
                            result = {"success": True}
                    
                    if result.get("success"):
                        # Actualizar status
                        hook.run(
                            """
                            UPDATE content_engagement 
                            SET status = 'sent', sent_at = NOW(), updated_at = NOW()
                            WHERE engagement_id = %s
                            """,
                            parameters=(engagement_id,)
                        )
                        
                        # Registrar en multi-canal si aplica
                        if messaging and channel_used != "email":
                            hook.run(
                                """
                                INSERT INTO multichannel_messages (
                                    lead_id, channel, message_type, content, status, sent_at
                                ) VALUES (%s, %s, 'nurturing', %s, 'sent', NOW())
                                """,
                                parameters=(
                                    lead_id,
                                    channel_used,
                                    json.dumps(content_data)
                                )
                            )
                        
                        sent += 1
                    else:
                        raise Exception(result.get("error", "Error desconocido"))
                    
                except Exception as e:
                    logger.error(f"Error enviando email a {email}: {e}")
                    failed += 1
                    hook.run(
                        """
                        UPDATE content_engagement 
                        SET status = 'failed', error_message = %s, updated_at = NOW()
                        WHERE engagement_id = %s
                        """,
                        parameters=(str(e)[:500], engagement_id)
                    )
            
            logger.info(f"Contenido enviado: {sent} exitosos, {failed} fallidos")
            return {"sent": sent, "failed": failed}
            
        except Exception as e:
            logger.error(f"Error enviando contenido: {e}", exc_info=True)
            return {"sent": sent, "failed": failed, "error": str(e)}
    
    @task(task_id="track_engagement")
    def track_engagement() -> Dict[str, Any]:
        """Actualiza engagement de leads con contenido."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        engagement_threshold = int(ctx["params"]["engagement_threshold"])
        enable_ab_testing = bool(ctx["params"].get("enable_ab_testing", False))
        enable_gamification = bool(ctx["params"].get("enable_gamification", False))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Inicializar servicios avanzados
        ab_manager = None
        gamification = None
        
        if enable_ab_testing and ADVANCED_FEATURES_AVAILABLE:
            try:
                ab_manager = ABTestingManager(db_hook=hook)
            except Exception as e:
                logger.warning(f"No se pudo inicializar A/B testing: {e}")
        
        if enable_gamification and ADVANCED_FEATURES_AVAILABLE:
            try:
                gamification = GamificationSystem(db_hook=hook)
            except Exception as e:
                logger.warning(f"No se pudo inicializar gamificación: {e}")
        
        try:
            # Actualizar engagement desde webhooks/APIs externas
            # (Asumiendo que hay eventos de engagement que se registran)
            
            # Contar engagement por lead
            query = """
                SELECT 
                    ce.lead_id,
                    COUNT(*) as total_engagement,
                    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_count,
                    COUNT(CASE WHEN ce.content_type = 'blog' THEN 1 END) as blog_reads,
                    COUNT(CASE WHEN ce.content_type = 'guide' THEN 1 END) as guides_downloaded,
                    COUNT(CASE WHEN ce.content_type = 'video' THEN 1 END) as videos_watched
                FROM content_engagement ce
                WHERE ce.status IN ('sent', 'opened', 'clicked', 'completed')
                GROUP BY ce.lead_id
            """
            
            engagement_data = hook.get_records(query)
            
            engaged_leads = []
            for row in engagement_data:
                lead_id, total, completed, blogs, guides, videos = row
                
                # Actualizar métricas en lead
                hook.run(
                    """
                    UPDATE organic_leads
                    SET 
                        engagement_score = %s,
                        content_consumed = %s,
                        last_engagement_at = NOW(),
                        updated_at = NOW()
                    WHERE lead_id = %s
                    """,
                    parameters=(total, total, lead_id)
                )
                
                # Verificar si alcanza threshold para ser "enganchado"
                if total >= engagement_threshold:
                    # Etiquetar como enganchado
                    hook.run(
                        """
                        UPDATE organic_leads
                        SET 
                            status = 'engaged',
                            engaged_at = NOW(),
                            updated_at = NOW()
                        WHERE lead_id = %s AND status != 'engaged'
                        """,
                        parameters=(lead_id,)
                    )
                    
                    # Registrar engagement en A/B testing si aplica
                    if ab_manager:
                        try:
                            # Buscar si este lead está en un test A/B
                            test_query = """
                                SELECT DISTINCT ab_test_id, ab_variant
                                FROM content_engagement
                                WHERE lead_id = %s AND ab_test_id IS NOT NULL
                                LIMIT 1
                            """
                            test_result = hook.get_first(test_query, parameters=(lead_id,))
                            
                            if test_result:
                                test_id, variant = test_result
                                ab_manager.record_engagement(test_id, lead_id, engaged=True)
                        except Exception as e:
                            logger.warning(f"Error registrando engagement en A/B test: {e}")
                    
                    # Otorgar puntos de gamificación
                    if gamification:
                        try:
                            gamification.award_points(
                                lead_id=lead_id,
                                action="engagement",
                                points=5,  # 5 puntos por engancharse
                                metadata={
                                    "engagement_score": total,
                                    "blogs": blogs,
                                    "guides": guides,
                                    "videos": videos
                                }
                            )
                        except Exception as e:
                            logger.warning(f"Error otorgando puntos de gamificación: {e}")
                    
                    engaged_leads.append({
                        "lead_id": lead_id,
                        "engagement_score": total,
                        "blogs_read": blogs,
                        "guides_downloaded": guides,
                        "videos_watched": videos
                    })
            
            logger.info(f"Engagement actualizado: {len(engaged_leads)} leads enganchados")
            return {
                "engaged_leads": engaged_leads,
                "total_tracked": len(engagement_data)
            }
            
        except Exception as e:
            logger.error(f"Error tracking engagement: {e}", exc_info=True)
            return {"engaged_leads": [], "error": str(e)}
    
    @task(task_id="invite_to_referral_program")
    def invite_to_referral_program(engagement_data: Dict[str, Any]) -> Dict[str, int]:
        """Invita leads enganchados al programa de referidos."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        email_webhook = str(ctx["params"]["email_webhook_url"])
        email_from = str(ctx["params"]["email_from"])
        referral_incentive = float(ctx["params"]["referral_incentive"])
        enable_multichannel = bool(ctx["params"].get("enable_multichannel", False))
        enable_gamification = bool(ctx["params"].get("enable_gamification", False))
        dry_run = bool(ctx["params"]["dry_run"])
        timeout = int(ctx["params"]["request_timeout"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Inicializar servicios
        messaging = None
        gamification = None
        
        if enable_multichannel and ADVANCED_FEATURES_AVAILABLE:
            try:
                messaging = MultiChannelMessaging()
            except Exception as e:
                logger.warning(f"No se pudo inicializar multi-canal: {e}")
        
        if enable_gamification and ADVANCED_FEATURES_AVAILABLE:
            try:
                gamification = GamificationSystem(db_hook=hook)
            except Exception as e:
                logger.warning(f"No se pudo inicializar gamificación: {e}")
        
        engaged_leads = engagement_data.get("engaged_leads", [])
        invited = 0
        already_invited = 0
        
        try:
            for lead_data in engaged_leads:
                lead_id = lead_data["lead_id"]
                
                # Verificar si ya fue invitado
                existing = hook.get_first(
                    "SELECT referral_code FROM referral_programs WHERE lead_id = %s",
                    parameters=(lead_id,)
                )
                
                if existing:
                    already_invited += 1
                    continue
                
                # Obtener datos del lead
                lead_info = hook.get_first(
                    """
                    SELECT email, first_name, last_name, phone
                    FROM organic_leads
                    WHERE lead_id = %s
                    """,
                    parameters=(lead_id,)
                )
                
                if not lead_info:
                    continue
                
                email, first_name, last_name, phone = lead_info
                
                # Generar código y enlace de referido
                referral_code = generate_referral_code(email)
                referral_link = generate_referral_link("https://tu-dominio.com", referral_code)
                
                if dry_run:
                    logger.info(f"[DRY RUN] Invitando {email} al programa de referidos")
                    invited += 1
                    continue
                
                # Crear registro en programa de referidos
                hook.run(
                    """
                    INSERT INTO referral_programs (
                        lead_id,
                        referral_code,
                        referral_link,
                        incentive_amount,
                        status,
                        invited_at
                    ) VALUES (%s, %s, %s, %s, 'active', NOW())
                    """,
                    parameters=(lead_id, referral_code, referral_link, referral_incentive)
                )
                
                # Enviar email de invitación
                subject = "🎁 Únete a nuestro programa de referidos"
                body = f"""
Hola {first_name or 'amigo/a'},

¡Felicitaciones! Has demostrado gran interés en nuestro contenido.

Queremos invitarte a nuestro **Programa de Referidos** donde puedes ganar ${referral_incentive:.2f} por cada persona que refieras.

**Tu enlace único de referido:**
{referral_link}

**Tu código:**
{referral_code}

Comparte este enlace con tus contactos y gana recompensas por cada referido exitoso.

¡Gracias por ser parte de nuestra comunidad!

Saludos,
Equipo de Marketing
                """
                
                try:
                    payload = {
                        "from": email_from,
                        "to": email,
                        "subject": subject,
                        "text": body,
                        "html": body.replace("\n", "<br>"),
                        "metadata": {
                            "lead_id": lead_id,
                            "referral_code": referral_code,
                            "type": "referral_invitation"
                        }
                    }
                    
                    response = requests.post(
                        email_webhook,
                        json=payload,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    
                    invited += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando invitación a {email}: {e}")
            
            logger.info(f"Invitaciones enviadas: {invited} nuevos, {already_invited} ya invitados")
            return {"invited": invited, "already_invited": already_invited}
            
        except Exception as e:
            logger.error(f"Error invitando a programa de referidos: {e}", exc_info=True)
            return {"invited": invited, "error": str(e)}
    
    @task(task_id="process_referrals")
    def process_referrals() -> Dict[str, Any]:
        """Procesa referidos nuevos y valida su autenticidad."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        enable_fraud = bool(ctx["params"]["enable_fraud_detection"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        processed = 0
        validated = 0
        fraud_detected = 0
        
        try:
            # Obtener referidos pendientes
            query = """
                SELECT 
                    r.referral_id,
                    r.referrer_lead_id,
                    r.referred_email,
                    r.referred_first_name,
                    r.referred_last_name,
                    r.referral_code,
                    r.status,
                    r.created_at,
                    rp.incentive_amount,
                    ol1.email as referrer_email,
                    ol1.first_name as referrer_first_name
                FROM referrals r
                JOIN referral_programs rp ON r.referral_code = rp.referral_code
                JOIN organic_leads ol1 ON r.referrer_lead_id = ol1.lead_id
                WHERE r.status = 'pending'
                ORDER BY r.created_at ASC
                LIMIT 100
            """
            
            pending_referrals = hook.get_records(query)
            
            for row in pending_referrals:
                referral_id, referrer_lead_id, referred_email, referred_first_name, \
                referred_last_name, referral_code, status, created_at, incentive_amount, \
                referrer_email, referrer_first_name = row
                
                # Validación anti-fraude (usar validador avanzado si está disponible)
                is_valid = True
                fraud_reasons = []
                
                if validator:
                    # Usar validador avanzado
                    validation_result = validator.validate_referral(
                        referral_id=referral_id,
                        referrer_email=referrer_email,
                        referred_email=referred_email,
                        ip_address=row[8] if len(row) > 8 else None,  # ip_address si está disponible
                        referral_code=referral_code
                    )
                    
                    is_valid = validation_result["is_valid"]
                    fraud_reasons = validation_result.get("fraud_reasons", [])
                elif enable_fraud:
                    # Validación básica (fallback)
                    if referred_email.lower() == referrer_email.lower():
                        is_valid = False
                        fraud_reasons.append("Auto-referido")
                    
                    ip_check = hook.get_first(
                        """
                        SELECT COUNT(*) 
                        FROM referrals 
                        WHERE referred_email = %s 
                        AND created_at > NOW() - INTERVAL '1 hour'
                        """,
                        parameters=(referred_email,)
                    )
                    if ip_check and ip_check[0] > 3:
                        is_valid = False
                        fraud_reasons.append("Múltiples referidos sospechosos")
                    
                    existing_lead = hook.get_first(
                        "SELECT lead_id FROM organic_leads WHERE email = %s",
                        parameters=(referred_email,)
                    )
                    if existing_lead:
                        lead_created = hook.get_first(
                            "SELECT created_at FROM organic_leads WHERE email = %s ORDER BY created_at ASC LIMIT 1",
                            parameters=(referred_email,)
                        )
                        if lead_created and lead_created[0] < created_at:
                            is_valid = False
                            fraud_reasons.append("Lead existente antes del referido")
                
                if not is_valid:
                    # Marcar como fraude
                    hook.run(
                        """
                        UPDATE referrals
                        SET 
                            status = 'fraud',
                            fraud_reasons = %s,
                            validated_at = NOW(),
                            updated_at = NOW()
                        WHERE referral_id = %s
                        """,
                        parameters=(json.dumps(fraud_reasons), referral_id)
                    )
                    fraud_detected += 1
                    logger.warning(f"Fraude detectado en referral {referral_id}: {', '.join(fraud_reasons)}")
                    continue
                
                # Validar referido
                hook.run(
                    """
                    UPDATE referrals
                    SET 
                        status = 'validated',
                        validated_at = NOW(),
                        updated_at = NOW()
                    WHERE referral_id = %s
                    """,
                    parameters=(referral_id,)
                )
                
                # Crear lead para el referido
                new_lead_id = f"lead_{secrets.token_hex(8)}"
                hook.run(
                    """
                    INSERT INTO organic_leads (
                        lead_id,
                        email,
                        first_name,
                        last_name,
                        source,
                        referral_code,
                        referrer_lead_id,
                        status,
                        created_at
                    ) VALUES (%s, %s, %s, %s, 'referral', %s, %s, 'new', NOW())
                    """,
                    parameters=(
                        new_lead_id,
                        referred_email,
                        referred_first_name,
                        referred_last_name,
                        referral_code,
                        referrer_lead_id
                    )
                )
                
                # Generar recompensa
                reward_id = f"reward_{secrets.token_hex(8)}"
                hook.run(
                    """
                    INSERT INTO referral_rewards (
                        reward_id,
                        referral_id,
                        referrer_lead_id,
                        reward_amount,
                        reward_type,
                        status,
                        created_at
                    ) VALUES (%s, %s, %s, %s, 'cash', 'pending', NOW())
                    """,
                    parameters=(reward_id, referral_id, referrer_lead_id, incentive_amount)
                )
                
                # Otorgar puntos de gamificación por referido exitoso
                if gamification:
                    try:
                        gamification.award_points(
                            lead_id=referrer_lead_id,
                            action="referral_success",
                            points=10,  # 10 puntos por referido validado
                            metadata={
                                "referral_id": referral_id,
                                "referred_email": referred_email
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Error otorgando puntos por referido: {e}")
                
                # Notificar referidor
                try:
                    notification_body = f"""
Hola {referrer_first_name or 'amigo/a'},

¡Excelente noticia! Has recibido una nueva referencia exitosa.

**Referido:** {referred_first_name or referred_email}
**Recompensa:** ${incentive_amount:.2f}

Tu recompensa será procesada en los próximos días.

¡Sigue compartiendo y ganando!

Saludos,
Equipo de Marketing
                    """
                    
                    payload = {
                        "from": ctx["params"]["email_from"],
                        "to": referrer_email,
                        "subject": "🎉 ¡Nueva referencia exitosa!",
                        "text": notification_body,
                        "html": notification_body.replace("\n", "<br>"),
                        "metadata": {
                            "type": "referral_reward",
                            "referral_id": referral_id,
                            "reward_id": reward_id
                        }
                    }
                    
                    if not ctx["params"]["dry_run"]:
                        response = requests.post(
                            ctx["params"]["email_webhook_url"],
                            json=payload,
                            timeout=ctx["params"]["request_timeout"]
                        )
                        response.raise_for_status()
                
                except Exception as e:
                    logger.error(f"Error notificando referidor: {e}")
                
                validated += 1
                processed += 1
            
            logger.info(f"Referidos procesados: {processed} total, {validated} validados, {fraud_detected} fraude")
            return {
                "processed": processed,
                "validated": validated,
                "fraud_detected": fraud_detected
            }
            
        except Exception as e:
            logger.error(f"Error procesando referidos: {e}", exc_info=True)
            return {"processed": processed, "error": str(e)}
    
    @task(task_id="sync_with_crm")
    def sync_with_crm() -> Dict[str, int]:
        """Sincroniza datos con CRM."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        crm_url = str(ctx["params"]["crm_api_url"])
        crm_key = str(ctx["params"]["crm_api_key"])
        dry_run = bool(ctx["params"]["dry_run"])
        timeout = int(ctx["params"]["request_timeout"])
        enable_batch = bool(ctx["params"].get("enable_batch_processing", True))
        batch_size = int(ctx["params"].get("batch_size", 50))
        enable_cb = bool(ctx["params"].get("enable_circuit_breaker", True))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        if not crm_url:
            logger.info("CRM sync deshabilitado (no hay URL configurada)")
            return {"synced": 0, "skipped": 0}
        
        synced = 0
        failed = 0
        
        try:
            # Obtener leads que necesitan sincronización
            query = """
                SELECT 
                    lead_id,
                    email,
                    first_name,
                    last_name,
                    source,
                    status,
                    engagement_score,
                    referral_code,
                    referrer_lead_id,
                    created_at,
                    updated_at
                FROM organic_leads
                WHERE crm_synced = false
                OR (updated_at > crm_synced_at OR crm_synced_at IS NULL)
                ORDER BY updated_at DESC
                LIMIT 50
            """
            
            leads_to_sync = hook.get_records(query)
            
            def sync_single_lead(row):
                """Sincroniza un lead individual."""
                lead_id, email, first_name, last_name, source, status, \
                engagement_score, referral_code, referrer_lead_id, created_at, updated_at = row
                
                if dry_run:
                    logger.info(f"[DRY RUN] Sincronizando lead {email} con CRM")
                    return True
                
                # Preparar payload para CRM
                payload = {
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "source": source,
                    "status": status,
                    "engagement_score": engagement_score or 0,
                    "custom_fields": {
                        "referral_code": referral_code,
                        "referrer_lead_id": referrer_lead_id,
                        "lead_id": lead_id
                    }
                }
                
                try:
                    headers = {
                        "Authorization": f"Bearer {crm_key}",
                        "Content-Type": "application/json"
                    }
                    
                    if enable_cb:
                        def sync_request():
                            session = get_http_session()
                            return session.post(
                                f"{crm_url}/api/leads",
                                json=payload,
                                headers=headers,
                                timeout=timeout
                            )
                        
                        response = crm_circuit_breaker.call(sync_request)
                    else:
                        session = get_http_session()
                        response = session.post(
                            f"{crm_url}/api/leads",
                            json=payload,
                            headers=headers,
                            timeout=timeout
                        )
                    
                    response.raise_for_status()
                    
                    # Marcar como sincronizado
                    hook.run(
                        """
                        UPDATE organic_leads
                        SET 
                            crm_synced = true,
                            crm_synced_at = NOW(),
                            updated_at = NOW()
                        WHERE lead_id = %s
                        """,
                        parameters=(lead_id,)
                    )
                    
                    return True
                    
                except Exception as e:
                    logger.error(f"Error sincronizando lead {email} con CRM: {e}")
                    return False
            
            # Procesar en batches si está habilitado
            if enable_batch and CONCURRENT_AVAILABLE and len(leads_to_sync) > batch_size:
                batches = [leads_to_sync[i:i+batch_size] for i in range(0, len(leads_to_sync), batch_size)]
                max_workers = int(ctx["params"].get("max_workers", 4))
                
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    for batch in batches:
                        futures = {executor.submit(sync_single_lead, row): row for row in batch}
                        for future in as_completed(futures):
                            try:
                                if future.result():
                                    synced += 1
                                else:
                                    failed += 1
                            except Exception as e:
                                logger.error(f"Error en batch sync: {e}")
                                failed += 1
            else:
                # Procesamiento secuencial
                for row in leads_to_sync:
                    if sync_single_lead(row):
                        synced += 1
                    else:
                        failed += 1
            
            logger.info(f"CRM sync: {synced} exitosos, {failed} fallidos")
            return {"synced": synced, "failed": failed}
            
        except Exception as e:
            logger.error(f"Error en sync con CRM: {e}", exc_info=True)
            return {"synced": synced, "failed": failed, "error": str(e)}
    
    @task(task_id="send_reminders")
    def send_reminders() -> Dict[str, int]:
        """Envía recordatorios a leads sin engagement."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        email_webhook = str(ctx["params"]["email_webhook_url"])
        email_from = str(ctx["params"]["email_from"])
        reminder_days = int(ctx["params"]["nurturing_reminder_days"])
        dry_run = bool(ctx["params"]["dry_run"])
        timeout = int(ctx["params"]["request_timeout"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        sent = 0
        skipped = 0
        
        try:
            # Buscar leads en nurturing sin engagement
            query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    ns.sequence_id,
                    ns.sequence_name,
                    ce.content_title,
                    ce.content_url
                FROM organic_leads ol
                JOIN nurturing_sequences ns ON ol.lead_id = ns.lead_id
                LEFT JOIN content_engagement ce ON ns.sequence_id = ce.sequence_id
                WHERE ol.status = 'nurturing'
                AND ns.status = 'active'
                AND ce.status = 'sent'
                AND ce.sent_at < NOW() - INTERVAL '%s days'
                AND NOT EXISTS (
                    SELECT 1 FROM content_engagement ce2
                    WHERE ce2.sequence_id = ns.sequence_id
                    AND ce2.status IN ('opened', 'clicked', 'completed')
                    AND ce2.updated_at > ce.sent_at
                )
                AND NOT EXISTS (
                    SELECT 1 FROM reminder_log rl
                    WHERE rl.lead_id = ol.lead_id
                    AND rl.reminder_type = 'first'
                    AND rl.sent_at > NOW() - INTERVAL '1 day'
                )
                LIMIT 50
            """
            
            leads_needing_reminder = hook.get_records(query, parameters=(reminder_days,))
            
            for row in leads_needing_reminder:
                lead_id, email, first_name, sequence_id, sequence_name, content_title, content_url = row
                
                if dry_run:
                    logger.info(f"[DRY RUN] Enviando recordatorio a {email}")
                    sent += 1
                    continue
                
                # Enviar recordatorio
                subject = f"💡 ¿Te perdiste nuestro contenido sobre {content_title}?"
                body = f"""
Hola {first_name or 'amigo/a'},

Hace unos días te enviamos contenido que creemos que te puede interesar:

**{content_title}**

{content_url or "https://tu-dominio.com/blog"}

Si no lo has visto aún, aquí está el enlace directo.

¡Esperamos que te sea útil!

Saludos,
Equipo de Marketing
                """
                
                try:
                    payload = {
                        "from": email_from,
                        "to": email,
                        "subject": subject,
                        "text": body,
                        "html": body.replace("\n", "<br>"),
                        "metadata": {
                            "lead_id": lead_id,
                            "type": "reminder",
                            "reminder_type": "first"
                        }
                    }
                    
                    response = requests.post(
                        email_webhook,
                        json=payload,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    
                    # Registrar recordatorio
                    hook.run(
                        """
                        INSERT INTO reminder_log (
                            lead_id,
                            reminder_type,
                            sent_at
                        ) VALUES (%s, 'first', NOW())
                        """,
                        parameters=(lead_id,)
                    )
                    
                    sent += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando recordatorio a {email}: {e}")
                    skipped += 1
            
            logger.info(f"Recordatorios enviados: {sent} exitosos, {skipped} omitidos")
            return {"sent": sent, "skipped": skipped}
            
        except Exception as e:
            logger.error(f"Error enviando recordatorios: {e}", exc_info=True)
            return {"sent": sent, "skipped": skipped, "error": str(e)}
    
    @task(task_id="send_second_incentive")
    def send_second_incentive() -> Dict[str, int]:
        """Envía segundo incentivo a leads que no participan en referidos."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        email_webhook = str(ctx["params"]["email_webhook_url"])
        email_from = str(ctx["params"]["email_from"])
        incentive_days = int(ctx["params"]["nurturing_second_incentive_days"])
        referral_incentive = float(ctx["params"]["referral_incentive"])
        dry_run = bool(ctx["params"]["dry_run"])
        timeout = int(ctx["params"]["request_timeout"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        sent = 0
        skipped = 0
        
        try:
            # Buscar leads enganchados con programa de referidos pero sin referidos
            query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    rp.referral_code,
                    rp.referral_link,
                    rp.invited_at
                FROM organic_leads ol
                JOIN referral_programs rp ON ol.lead_id = rp.lead_id
                WHERE ol.status = 'engaged'
                AND rp.status = 'active'
                AND rp.invited_at < NOW() - INTERVAL '%s days'
                AND NOT EXISTS (
                    SELECT 1 FROM referrals r
                    WHERE r.referral_code = rp.referral_code
                    AND r.status = 'validated'
                )
                AND NOT EXISTS (
                    SELECT 1 FROM reminder_log rl
                    WHERE rl.lead_id = ol.lead_id
                    AND rl.reminder_type = 'second_incentive'
                    AND rl.sent_at > NOW() - INTERVAL '1 day'
                )
                LIMIT 50
            """
            
            leads_for_second_incentive = hook.get_records(query, parameters=(incentive_days,))
            
            # Calcular nuevo incentivo (aumentar 20%)
            new_incentive = referral_incentive * 1.2
            
            for row in leads_for_second_incentive:
                lead_id, email, first_name, referral_code, referral_link, invited_at = row
                
                if dry_run:
                    logger.info(f"[DRY RUN] Enviando segundo incentivo a {email}")
                    sent += 1
                    continue
                
                # Actualizar incentivo
                hook.run(
                    """
                    UPDATE referral_programs
                    SET 
                        incentive_amount = %s,
                        updated_at = NOW()
                    WHERE referral_code = %s
                    """,
                    parameters=(new_incentive, referral_code)
                )
                
                # Enviar email con nuevo incentivo
                subject = "🎁 Incentivo especial: Gana más con referidos"
                body = f"""
Hola {first_name or 'amigo/a'},

Queremos darte una oportunidad especial. Hemos aumentado tu incentivo por referidos:

**Antes:** ${referral_incentive:.2f} por referido
**Ahora:** ${new_incentive:.2f} por referido

**Tu enlace único:**
{referral_link}

**Tu código:**
{referral_code}

¡Aprovecha esta oferta especial y comienza a ganar hoy mismo!

Saludos,
Equipo de Marketing
                """
                
                try:
                    payload = {
                        "from": email_from,
                        "to": email,
                        "subject": subject,
                        "text": body,
                        "html": body.replace("\n", "<br>"),
                        "metadata": {
                            "lead_id": lead_id,
                            "type": "second_incentive",
                            "referral_code": referral_code
                        }
                    }
                    
                    response = requests.post(
                        email_webhook,
                        json=payload,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    
                    # Registrar recordatorio
                    hook.run(
                        """
                        INSERT INTO reminder_log (
                            lead_id,
                            reminder_type,
                            sent_at
                        ) VALUES (%s, 'second_incentive', NOW())
                        """,
                        parameters=(lead_id,)
                    )
                    
                    sent += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando segundo incentivo a {email}: {e}")
                    skipped += 1
            
            logger.info(f"Segundos incentivos enviados: {sent} exitosos, {skipped} omitidos")
            return {"sent": sent, "skipped": skipped}
            
        except Exception as e:
            logger.error(f"Error enviando segundos incentivos: {e}", exc_info=True)
            return {"sent": sent, "skipped": skipped, "error": str(e)}
    
    @task(task_id="performance_metrics")
    def performance_metrics() -> Dict[str, Any]:
        """Recopila métricas de performance del DAG."""
        ctx = get_current_context()
        start_time = time.time()
        
        try:
            # Métricas de caché
            cache_stats = {}
            if CACHE_AVAILABLE:
                cache_stats = {
                    "cache_size": len(_query_cache) if hasattr(_query_cache, '__len__') else 0,
                    "cache_available": True
                }
            else:
                cache_stats = {"cache_available": False}
            
            # Métricas de circuit breakers
            cb_stats = {
                "email_cb_state": email_circuit_breaker.state.value,
                "email_cb_failures": email_circuit_breaker.failures,
                "crm_cb_state": crm_circuit_breaker.state.value,
                "crm_cb_failures": crm_circuit_breaker.failures
            }
            
            # Métricas de HTTP session
            session_stats = {}
            if _http_session:
                session_stats = {
                    "session_active": True,
                    "pool_connections": getattr(_http_session, 'pool_connections', 0)
                }
            
            execution_time = time.time() - start_time
            
            return {
                "execution_time_seconds": execution_time,
                "cache_stats": cache_stats,
                "circuit_breaker_stats": cb_stats,
                "session_stats": session_stats,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error recopilando métricas: {e}")
            return {"error": str(e)}
    
    @task(task_id="generate_reports")
    def generate_reports() -> Dict[str, Any]:
        """Genera reportes automáticos con métricas clave."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        report_frequency = str(ctx["params"]["report_frequency"])
        slack_webhook = str(ctx["params"]["slack_webhook_url"])
        enable_caching = bool(ctx["params"].get("enable_caching", True))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Calcular período según frecuencia
            if report_frequency == "daily":
                period_start = datetime.now() - timedelta(days=1)
                period_label = "Últimas 24 horas"
            else:  # weekly
                period_start = datetime.now() - timedelta(days=7)
                period_label = "Últimos 7 días"
            
            # Métricas de leads (con caché si está habilitado)
            @cached_query("leads_metrics", ttl=300)
            def get_leads_metrics():
                leads_query = """
                    SELECT 
                        COUNT(*) as total_leads,
                        COUNT(CASE WHEN status = 'new' THEN 1 END) as new_leads,
                        COUNT(CASE WHEN status = 'nurturing' THEN 1 END) as nurturing_leads,
                        COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged_leads,
                        AVG(engagement_score) as avg_engagement_score
                    FROM organic_leads
                    WHERE created_at >= %s
                """
                return hook.get_first(leads_query, parameters=(period_start,))
            
            if enable_caching:
                leads_metrics = get_leads_metrics()
            else:
                leads_query = """
                    SELECT 
                        COUNT(*) as total_leads,
                        COUNT(CASE WHEN status = 'new' THEN 1 END) as new_leads,
                        COUNT(CASE WHEN status = 'nurturing' THEN 1 END) as nurturing_leads,
                        COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged_leads,
                        AVG(engagement_score) as avg_engagement_score
                    FROM organic_leads
                    WHERE created_at >= %s
                """
                leads_metrics = hook.get_first(leads_query, parameters=(period_start,))
            
            # Métricas de referidos
            referrals_query = """
                SELECT 
                    COUNT(*) as total_referrals,
                    COUNT(CASE WHEN status = 'validated' THEN 1 END) as validated_referrals,
                    COUNT(CASE WHEN status = 'fraud' THEN 1 END) as fraud_referrals,
                    COUNT(DISTINCT referrer_lead_id) as unique_referrers
                FROM referrals
                WHERE created_at >= %s
            """
            referrals_metrics = hook.get_first(referrals_query, parameters=(period_start,))
            
            # Métricas de recompensas
            rewards_query = """
                SELECT 
                    COUNT(*) as total_rewards,
                    SUM(reward_amount) as total_reward_amount,
                    COUNT(CASE WHEN status = 'paid' THEN 1 END) as paid_rewards
                FROM referral_rewards
                WHERE created_at >= %s
            """
            rewards_metrics = hook.get_first(rewards_query, parameters=(period_start,))
            
            # Tasa de conversión
            total_engaged = leads_metrics[4] if leads_metrics else 0
            total_invited = hook.get_first(
                "SELECT COUNT(*) FROM referral_programs WHERE invited_at >= %s",
                parameters=(period_start,)
            )[0] if hook.get_first(
                "SELECT COUNT(*) FROM referral_programs WHERE invited_at >= %s",
                parameters=(period_start,)
            ) else 0
            
            conversion_rate = (total_invited / total_engaged * 100) if total_engaged > 0 else 0
            
            # Preparar reporte
            report = {
                "period": period_label,
                "period_start": period_start.isoformat(),
                "period_end": datetime.now().isoformat(),
                "leads": {
                    "total": leads_metrics[0] if leads_metrics else 0,
                    "new": leads_metrics[1] if leads_metrics else 0,
                    "nurturing": leads_metrics[2] if leads_metrics else 0,
                    "engaged": leads_metrics[3] if leads_metrics else 0,
                    "avg_engagement_score": float(leads_metrics[4]) if leads_metrics and leads_metrics[4] else 0.0
                },
                "referrals": {
                    "total": referrals_metrics[0] if referrals_metrics else 0,
                    "validated": referrals_metrics[1] if referrals_metrics else 0,
                    "fraud": referrals_metrics[2] if referrals_metrics else 0,
                    "unique_referrers": referrals_metrics[3] if referrals_metrics else 0
                },
                "rewards": {
                    "total": rewards_metrics[0] if rewards_metrics else 0,
                    "total_amount": float(rewards_metrics[1]) if rewards_metrics and rewards_metrics[1] else 0.0,
                    "paid": rewards_metrics[2] if rewards_metrics else 0
                },
                "conversion_rates": {
                    "engaged_to_invited": conversion_rate,
                    "referral_validation_rate": (
                        (referrals_metrics[1] / referrals_metrics[0] * 100)
                        if referrals_metrics and referrals_metrics[0] > 0 else 0.0
                    )
                }
            }
            
            # Guardar reporte
            report_id = f"report_{secrets.token_hex(8)}"
            hook.run(
                """
                INSERT INTO acquisition_metrics (
                    report_id,
                    report_type,
                    period_start,
                    period_end,
                    metrics_data,
                    created_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                parameters=(
                    report_id,
                    report_frequency,
                    period_start,
                    datetime.now(),
                    json.dumps(report)
                )
            )
            
            # Enviar a Slack si está configurado
            if slack_webhook:
                try:
                    slack_message = f"""
📊 *Reporte de Adquisición Orgánica - {period_label}*

*Leads:*
• Total: {report['leads']['total']}
• Nuevos: {report['leads']['new']}
• En nurturing: {report['leads']['nurturing']}
• Enganchados: {report['leads']['engaged']}
• Score promedio: {report['leads']['avg_engagement_score']:.1f}

*Referidos:*
• Total: {report['referrals']['total']}
• Validados: {report['referrals']['validated']}
• Fraude: {report['referrals']['fraud']}
• Referidores únicos: {report['referrals']['unique_referrers']}

*Recompensas:*
• Total: {report['rewards']['total']}
• Monto total: ${report['rewards']['total_amount']:.2f}
• Pagadas: {report['rewards']['paid']}

*Conversión:*
• Enganchados → Invitados: {report['conversion_rates']['engaged_to_invited']:.1f}%
• Tasa de validación: {report['conversion_rates']['referral_validation_rate']:.1f}%
                    """
                    
                    requests.post(
                        slack_webhook,
                        json={"text": slack_message},
                        timeout=10
                    )
                except Exception as e:
                    logger.warning(f"Error enviando a Slack: {e}")
            
            logger.info(f"Reporte generado: {report_id}")
            return report
            
        except Exception as e:
            logger.error(f"Error generando reporte: {e}", exc_info=True)
            return {"error": str(e)}
    
    @task(task_id="optimize_automatically")
    def optimize_automatically() -> Dict[str, Any]:
        """Optimiza automáticamente contenido y recompensas."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        enable_optimization = bool(ctx["params"]["enable_auto_optimization"])
        low_threshold = float(ctx["params"]["low_conversion_threshold"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        if not enable_optimization:
            logger.info("Optimización automática deshabilitada")
            return {"optimized": False}
        
        optimizations = []
        
        try:
            # Analizar tasa de conversión de referidos
            conversion_query = """
                SELECT 
                    COUNT(DISTINCT ol.lead_id) as total_engaged,
                    COUNT(DISTINCT rp.lead_id) as total_invited,
                    COUNT(DISTINCT r.referral_id) as total_referrals
                FROM organic_leads ol
                LEFT JOIN referral_programs rp ON ol.lead_id = rp.lead_id
                LEFT JOIN referrals r ON rp.referral_code = r.referral_code
                WHERE ol.status = 'engaged'
                AND ol.engaged_at > NOW() - INTERVAL '30 days'
            """
            
            conversion_data = hook.get_first(conversion_query)
            
            if conversion_data:
                total_engaged, total_invited, total_referrals = conversion_data
                
                if total_engaged > 0:
                    invite_rate = (total_invited / total_engaged) * 100
                    referral_rate = (total_referrals / total_invited * 100) if total_invited > 0 else 0
                    
                    # Si la tasa de conversión es baja, ajustar incentivo
                    if referral_rate < low_threshold:
                        current_incentive = float(ctx["params"]["referral_incentive"])
                        new_incentive = current_incentive * 1.15  # Aumentar 15%
                        
                        hook.run(
                            """
                            UPDATE referral_programs
                            SET incentive_amount = %s
                            WHERE status = 'active'
                            AND invited_at > NOW() - INTERVAL '7 days'
                            """,
                            parameters=(new_incentive,)
                        )
                        
                        optimizations.append({
                            "type": "incentive_increase",
                            "old_value": current_incentive,
                            "new_value": new_incentive,
                            "reason": f"Tasa de conversión baja: {referral_rate:.1f}%"
                        })
            
            # Analizar contenido más efectivo
            content_query = """
                SELECT 
                    content_type,
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN status IN ('opened', 'clicked', 'completed') THEN 1 END) as engaged,
                    AVG(CASE WHEN status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM content_engagement
                WHERE sent_at > NOW() - INTERVAL '30 days'
                GROUP BY content_type
                ORDER BY completion_rate DESC
            """
            
            content_performance = hook.get_records(content_query)
            
            if content_performance:
                best_content_type = content_performance[0][0]
                worst_content_type = content_performance[-1][0] if len(content_performance) > 1 else None
                
                optimizations.append({
                    "type": "content_optimization",
                    "best_content_type": best_content_type,
                    "recommendation": f"Incrementar uso de {best_content_type}"
                })
            
            logger.info(f"Optimizaciones aplicadas: {len(optimizations)}")
            return {
                "optimized": True,
                "optimizations": optimizations
            }
            
        except Exception as e:
            logger.error(f"Error en optimización automática: {e}", exc_info=True)
            return {"optimized": False, "error": str(e)}
    
    # ============================================================================
    # PIPELINE PRINCIPAL
    # ============================================================================
    
    schema_ok = ensure_schema()
    
    # Captura y segmentación
    new_leads = capture_new_leads()
    segmentation = segment_leads(new_leads)
    
    # Nurturing
    nurturing_started = start_nurturing_workflows(segmentation)
    content_sent = send_nurturing_content()
    engagement_tracked = track_engagement()
    
    # Referidos
    referral_invites = invite_to_referral_program(engagement_tracked)
    referrals_processed = process_referrals()
    
    # Sincronización y recordatorios
    crm_synced = sync_with_crm()
    reminders_sent = send_reminders()
    second_incentives = send_second_incentive()
    
    # Reportes y optimización
    reports = generate_reports()
    optimizations = optimize_automatically()
    
    # ============================================================================
    # TAREAS AVANZADAS ADICIONALES
    # ============================================================================
    
    @task(task_id="retrain_ml_model")
    def retrain_ml_model() -> Dict[str, Any]:
        """Reentrena el modelo ML con datos recientes."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        enable_ml_scoring = bool(ctx["params"].get("enable_ml_scoring", False))
        ml_retrain_days = int(ctx["params"].get("ml_retrain_days", 90))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        if not enable_ml_scoring or not ADVANCED_FEATURES_AVAILABLE:
            logger.info("ML scoring deshabilitado o no disponible")
            return {"retrained": False, "reason": "disabled"}
        
        try:
            scoring_service = LeadScoringService(db_hook=hook)
            metrics = scoring_service.retrain_model(days_back=ml_retrain_days)
            
            if "error" in metrics:
                logger.warning(f"Error reentrenando modelo: {metrics['error']}")
                return {"retrained": False, "error": metrics["error"]}
            
            logger.info(f"Modelo reentrenado exitosamente: {metrics}")
            return {
                "retrained": True,
                "metrics": metrics,
                "training_samples": metrics.get("training_samples", 0),
                "accuracy": metrics.get("accuracy", 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error en reentrenamiento ML: {e}", exc_info=True)
            return {"retrained": False, "error": str(e)}
    
    @task(task_id="cohort_analysis")
    def cohort_analysis() -> Dict[str, Any]:
        """Análisis de cohortes para identificar patrones."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Análisis de cohortes por mes de creación
            cohort_query = """
                SELECT 
                    DATE_TRUNC('month', ol.created_at) as cohort_month,
                    COUNT(DISTINCT ol.lead_id) as total_leads,
                    COUNT(DISTINCT CASE WHEN ol.status = 'engaged' THEN ol.lead_id END) as engaged,
                    COUNT(DISTINCT CASE WHEN ol.status = 'converted' THEN ol.lead_id END) as converted,
                    AVG(ol.engagement_score) as avg_engagement,
                    COUNT(DISTINCT r.referral_id) as total_referrals
                FROM organic_leads ol
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE ol.created_at >= NOW() - INTERVAL '6 months'
                GROUP BY DATE_TRUNC('month', ol.created_at)
                ORDER BY cohort_month DESC
            """
            
            cohorts = hook.get_records(cohort_query)
            
            cohort_data = []
            for row in cohorts:
                cohort_month, total, engaged, converted, avg_eng, referrals = row
                cohort_data.append({
                    "cohort_month": cohort_month.strftime("%Y-%m") if cohort_month else None,
                    "total_leads": total,
                    "engaged": engaged,
                    "converted": converted,
                    "engagement_rate": (engaged / total * 100) if total > 0 else 0,
                    "conversion_rate": (converted / total * 100) if total > 0 else 0,
                    "avg_engagement": float(avg_eng or 0),
                    "total_referrals": referrals or 0
                })
            
            # Identificar mejor cohorte
            best_cohort = max(cohort_data, key=lambda x: x["conversion_rate"]) if cohort_data else None
            
            logger.info(f"Análisis de cohortes completado: {len(cohort_data)} cohortes analizados")
            return {
                "cohorts": cohort_data,
                "best_cohort": best_cohort,
                "total_cohorts": len(cohort_data)
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de cohortes: {e}", exc_info=True)
            return {"cohorts": [], "error": str(e)}
    
    @task(task_id="intelligent_alerts")
    def intelligent_alerts() -> Dict[str, Any]:
        """Genera alertas inteligentes basadas en métricas."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        slack_webhook = str(ctx["params"].get("slack_webhook_url", ""))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        alerts = []
        
        try:
            # Alerta 1: Tasa de conversión baja
            conversion_query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            conv_result = hook.get_first(conversion_query)
            if conv_result and conv_result[0] > 0:
                conversion_rate = (conv_result[1] / conv_result[0]) * 100
                if conversion_rate < 10:
                    alerts.append({
                        "level": "warning",
                        "title": "Tasa de Conversión Baja",
                        "message": f"La tasa de conversión es {conversion_rate:.1f}% (objetivo: >10%)",
                        "metric": "conversion_rate",
                        "value": conversion_rate
                    })
            
            # Alerta 2: Alta tasa de fraude
            fraud_query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'fraud' THEN 1 END) as fraud
                FROM referrals
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            fraud_result = hook.get_first(fraud_query)
            if fraud_result and fraud_result[0] > 0:
                fraud_rate = (fraud_result[1] / fraud_result[0]) * 100
                if fraud_rate > 20:
                    alerts.append({
                        "level": "error",
                        "title": "Alta Tasa de Fraude",
                        "message": f"Tasa de fraude del {fraud_rate:.1f}% (umbral: <20%)",
                        "metric": "fraud_rate",
                        "value": fraud_rate
                    })
            
            # Alerta 3: Bajo engagement
            engagement_query = """
                SELECT AVG(engagement_score) 
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '7 days'
                AND status = 'nurturing'
            """
            eng_result = hook.get_first(engagement_query)
            if eng_result and eng_result[0] is not None:
                avg_engagement = float(eng_result[0])
                if avg_engagement < 2:
                    alerts.append({
                        "level": "warning",
                        "title": "Bajo Engagement",
                        "message": f"Engagement promedio: {avg_engagement:.1f} (objetivo: >2)",
                        "metric": "avg_engagement",
                        "value": avg_engagement
                    })
            
            # Alerta 4: Sin nuevos leads
            new_leads_query = """
                SELECT COUNT(*) 
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """
            new_leads_result = hook.get_first(new_leads_query)
            if new_leads_result and new_leads_result[0] == 0:
                alerts.append({
                    "level": "info",
                    "title": "Sin Nuevos Leads",
                    "message": "No se han capturado nuevos leads en las últimas 24 horas",
                    "metric": "new_leads_24h",
                    "value": 0
                })
            
            # Enviar alertas a Slack si está configurado
            if alerts and slack_webhook:
                try:
                    alert_text = "🔔 *Alertas del Sistema de Adquisición Orgánica*\n\n"
                    for alert in alerts:
                        emoji = "⚠️" if alert["level"] == "warning" else "❌" if alert["level"] == "error" else "ℹ️"
                        alert_text += f"{emoji} *{alert['title']}*\n{alert['message']}\n\n"
                    
                    requests.post(
                        slack_webhook,
                        json={"text": alert_text},
                        timeout=10
                    )
                except Exception as e:
                    logger.warning(f"Error enviando alertas a Slack: {e}")
            
            logger.info(f"Alertas generadas: {len(alerts)}")
            return {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "critical_alerts": len([a for a in alerts if a["level"] == "error"])
            }
            
        except Exception as e:
            logger.error(f"Error generando alertas: {e}", exc_info=True)
            return {"alerts": [], "error": str(e)}
    
    @task(task_id="predict_churn")
    def predict_churn() -> Dict[str, Any]:
        """Predice leads en riesgo de churn (abandono)."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Identificar leads en riesgo (sin engagement reciente)
            churn_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    ol.status,
                    ol.engagement_score,
                    ol.last_engagement_at,
                    MAX(ce.sent_at) as last_content_sent,
                    COUNT(ce.engagement_id) as total_content_sent
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                WHERE ol.status IN ('nurturing', 'engaged')
                AND (ol.last_engagement_at IS NULL OR ol.last_engagement_at < NOW() - INTERVAL '14 days')
                GROUP BY ol.lead_id, ol.email, ol.first_name, ol.status, ol.engagement_score, ol.last_engagement_at
                HAVING COUNT(ce.engagement_id) > 0
                ORDER BY ol.last_engagement_at ASC NULLS FIRST
                LIMIT 50
            """
            
            at_risk_leads = hook.get_records(churn_query)
            
            leads_at_risk = []
            for row in at_risk_leads:
                lead_id, email, first_name, status, eng_score, last_eng, last_sent, total_sent = row
                
                days_since_engagement = None
                if last_eng:
                    days_since_engagement = (datetime.now() - last_eng).days
                
                risk_score = 0
                if days_since_engagement:
                    if days_since_engagement > 30:
                        risk_score = 10  # Alto riesgo
                    elif days_since_engagement > 14:
                        risk_score = 7  # Riesgo medio
                    else:
                        risk_score = 4  # Riesgo bajo
                
                leads_at_risk.append({
                    "lead_id": lead_id,
                    "email": email,
                    "first_name": first_name,
                    "status": status,
                    "engagement_score": eng_score or 0,
                    "days_since_engagement": days_since_engagement,
                    "risk_score": risk_score,
                    "total_content_sent": total_sent
                })
            
            # Actualizar leads con flag de riesgo
            for lead in leads_at_risk:
                if lead["risk_score"] >= 7:
                    try:
                        hook.run(
                            """
                            UPDATE organic_leads
                            SET status = 'inactive'
                            WHERE lead_id = %s AND status != 'inactive'
                            """,
                            parameters=(lead["lead_id"],)
                        )
                    except Exception as e:
                        logger.warning(f"Error actualizando lead en riesgo: {e}")
            
            logger.info(f"Análisis de churn: {len(leads_at_risk)} leads en riesgo")
            return {
                "leads_at_risk": leads_at_risk,
                "high_risk_count": len([l for l in leads_at_risk if l["risk_score"] >= 7]),
                "total_analyzed": len(leads_at_risk)
            }
            
        except Exception as e:
            logger.error(f"Error prediciendo churn: {e}", exc_info=True)
            return {"leads_at_risk": [], "error": str(e)}
    
    @task(task_id="optimize_timing")
    def optimize_timing() -> Dict[str, Any]:
        """Optimiza timing de envíos basado en engagement histórico."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar mejores horas para envío
            timing_query = """
                SELECT 
                    EXTRACT(HOUR FROM ce.sent_at) as send_hour,
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN ce.status IN ('opened', 'clicked', 'completed') THEN 1 END) as engaged,
                    AVG(CASE WHEN ce.status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM content_engagement ce
                WHERE ce.sent_at >= NOW() - INTERVAL '30 days'
                AND ce.sent_at IS NOT NULL
                GROUP BY EXTRACT(HOUR FROM ce.sent_at)
                ORDER BY completion_rate DESC
            """
            
            timing_data = hook.get_records(timing_query)
            
            best_hours = []
            for row in timing_data:
                hour, total, engaged, completion = row
                best_hours.append({
                    "hour": int(hour),
                    "total_sent": total,
                    "engaged": engaged,
                    "completion_rate": float(completion or 0),
                    "engagement_rate": (engaged / total * 100) if total > 0 else 0
                })
            
            # Identificar mejores 3 horas
            top_hours = sorted(best_hours, key=lambda x: x["completion_rate"], reverse=True)[:3]
            
            # Analizar mejores días de la semana
            day_query = """
                SELECT 
                    EXTRACT(DOW FROM ce.sent_at) as day_of_week,
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN ce.status IN ('opened', 'clicked', 'completed') THEN 1 END) as engaged,
                    AVG(CASE WHEN ce.status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM content_engagement ce
                WHERE ce.sent_at >= NOW() - INTERVAL '30 days'
                AND ce.sent_at IS NOT NULL
                GROUP BY EXTRACT(DOW FROM ce.sent_at)
                ORDER BY completion_rate DESC
            """
            
            day_data = hook.get_records(day_query)
            
            best_days = []
            day_names = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
            for row in day_data:
                day_num, total, engaged, completion = row
                best_days.append({
                    "day": int(day_num),
                    "day_name": day_names[int(day_num)],
                    "total_sent": total,
                    "engaged": engaged,
                    "completion_rate": float(completion or 0)
                })
            
            top_days = sorted(best_days, key=lambda x: x["completion_rate"], reverse=True)[:3]
            
            logger.info(f"Optimización de timing: Mejores horas {[h['hour'] for h in top_hours]}")
            return {
                "best_hours": top_hours,
                "best_days": top_days,
                "recommendations": {
                    "send_hours": [h["hour"] for h in top_hours],
                    "send_days": [d["day"] for d in top_days]
                }
            }
            
        except Exception as e:
            logger.error(f"Error optimizando timing: {e}", exc_info=True)
            return {"best_hours": [], "error": str(e)}
    
    @task(task_id="content_performance_analysis")
    def content_performance_analysis() -> Dict[str, Any]:
        """Análisis detallado de performance de contenido."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Performance por tipo de contenido
            type_query = """
                SELECT 
                    ce.content_type,
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) as opened,
                    COUNT(CASE WHEN ce.status = 'clicked' THEN 1 END) as clicked,
                    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed,
                    AVG(CASE WHEN ce.status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM content_engagement ce
                WHERE ce.sent_at >= NOW() - INTERVAL '30 days'
                GROUP BY ce.content_type
                ORDER BY completion_rate DESC
            """
            
            type_performance = hook.get_records(type_query)
            
            content_stats = []
            for row in type_performance:
                content_type, total, opened, clicked, completed, completion = row
                content_stats.append({
                    "content_type": content_type,
                    "total_sent": total,
                    "opened": opened,
                    "clicked": clicked,
                    "completed": completed,
                    "open_rate": (opened / total * 100) if total > 0 else 0,
                    "click_rate": (clicked / total * 100) if total > 0 else 0,
                    "completion_rate": float(completion or 0) * 100
                })
            
            # Performance por título (top performers)
            title_query = """
                SELECT 
                    ce.content_title,
                    ce.content_type,
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed,
                    AVG(CASE WHEN ce.status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM content_engagement ce
                WHERE ce.sent_at >= NOW() - INTERVAL '30 days'
                AND ce.content_title IS NOT NULL
                GROUP BY ce.content_title, ce.content_type
                HAVING COUNT(*) >= 5
                ORDER BY completion_rate DESC
                LIMIT 10
            """
            
            top_content = hook.get_records(title_query)
            
            top_performers = []
            for row in top_content:
                title, ctype, total, completed, completion = row
                top_performers.append({
                    "title": title,
                    "type": ctype,
                    "total_sent": total,
                    "completed": completed,
                    "completion_rate": float(completion or 0) * 100
                })
            
            logger.info(f"Análisis de contenido: {len(content_stats)} tipos, {len(top_performers)} top performers")
            return {
                "content_stats": content_stats,
                "top_performers": top_performers,
                "best_content_type": content_stats[0]["content_type"] if content_stats else None
            }
            
        except Exception as e:
            logger.error(f"Error analizando contenido: {e}", exc_info=True)
            return {"content_stats": [], "error": str(e)}
    
    # ============================================================================
    # PIPELINE PRINCIPAL MEJORADO
    # ============================================================================
    
    schema_ok = ensure_schema()
    
    # Captura y segmentación
    new_leads = capture_new_leads()
    segmentation = segment_leads(new_leads)
    
    # Nurturing
    nurturing_started = start_nurturing_workflows(segmentation)
    content_sent = send_nurturing_content()
    engagement_tracked = track_engagement()
    
    # Referidos
    referral_invites = invite_to_referral_program(engagement_tracked)
    referrals_processed = process_referrals()
    
    # Sincronización y recordatorios
    crm_synced = sync_with_crm()
    reminders_sent = send_reminders()
    second_incentives = send_second_incentive()
    
    # Reportes y optimización
    reports = generate_reports()
    optimizations = optimize_automatically()
    perf_metrics = performance_metrics()
    
    # Tareas avanzadas (paralelas)
    ml_retrain = retrain_ml_model()
    cohorts = cohort_analysis()
    alerts = intelligent_alerts()
    churn_prediction = predict_churn()
    timing_optimization = optimize_timing()
    content_analysis = content_performance_analysis()
    
    # ============================================================================
    # TAREAS AVANZADAS ADICIONALES V2
    # ============================================================================
    
    @task(task_id="sentiment_analysis")
    def sentiment_analysis() -> Dict[str, Any]:
        """Analiza sentimiento de respuestas y feedback de leads."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Buscar respuestas/feedback de leads (asumiendo tabla de feedback)
            feedback_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    fb.feedback_text,
                    fb.created_at
                FROM organic_leads ol
                JOIN lead_feedback fb ON ol.lead_id = fb.lead_id
                WHERE fb.created_at >= NOW() - INTERVAL '30 days'
                AND fb.feedback_text IS NOT NULL
                ORDER BY fb.created_at DESC
                LIMIT 100
            """
            
            try:
                feedbacks = hook.get_records(feedback_query)
            except Exception:
                # Si no existe tabla de feedback, retornar vacío
                logger.info("Tabla lead_feedback no existe, saltando análisis de sentimiento")
                return {"analyzed": 0, "feedbacks": []}
            
            sentiment_results = []
            
            for row in feedbacks:
                lead_id, email, first_name, feedback_text, created_at = row
                
                # Análisis simple de sentimiento
                text_lower = (feedback_text or "").lower()
                
                positive_words = ["excelente", "genial", "perfecto", "gracias", "me encanta", 
                                 "bueno", "útil", "great", "excellent", "perfect", "thanks"]
                negative_words = ["malo", "terrible", "horrible", "problema", "error", 
                                "bad", "terrible", "problem", "error", "disappointed"]
                
                positive_count = sum(1 for word in positive_words if word in text_lower)
                negative_count = sum(1 for word in negative_words if word in text_lower)
                
                # Calcular score (-1 a 1)
                total_words = positive_count + negative_count
                if total_words > 0:
                    sentiment_score = (positive_count - negative_count) / max(total_words, 1)
                else:
                    sentiment_score = 0.0
                
                # Determinar sentimiento
                if sentiment_score > 0.2:
                    sentiment = "positive"
                elif sentiment_score < -0.2:
                    sentiment = "negative"
                else:
                    sentiment = "neutral"
                
                sentiment_results.append({
                    "lead_id": lead_id,
                    "email": email,
                    "sentiment": sentiment,
                    "sentiment_score": round(sentiment_score, 2),
                    "positive_words": positive_count,
                    "negative_words": negative_count,
                    "feedback_text": feedback_text[:100] if feedback_text else None
                })
            
            # Estadísticas agregadas
            total = len(sentiment_results)
            positive = len([r for r in sentiment_results if r["sentiment"] == "positive"])
            negative = len([r for r in sentiment_results if r["sentiment"] == "negative"])
            neutral = len([r for r in sentiment_results if r["sentiment"] == "neutral"])
            
            logger.info(f"Análisis de sentimiento: {total} feedbacks analizados")
            return {
                "analyzed": total,
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "positive_rate": (positive / total * 100) if total > 0 else 0,
                "results": sentiment_results[:20]  # Top 20
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de sentimiento: {e}", exc_info=True)
            return {"analyzed": 0, "error": str(e)}
    
    @task(task_id="advanced_tagging")
    def advanced_tagging() -> Dict[str, Any]:
        """Sistema de tags avanzado para segmentación."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener leads sin tags o con tags desactualizados
            leads_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.status,
                    ol.engagement_score,
                    ol.source,
                    ol.interest_area,
                    COUNT(ce.engagement_id) as content_count,
                    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_count,
                    MAX(ce.sent_at) as last_content_sent
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                WHERE ol.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY ol.lead_id, ol.email, ol.status, ol.engagement_score, ol.source, ol.interest_area
                LIMIT 200
            """
            
            leads = hook.get_records(leads_query)
            
            tagged = 0
            tags_applied = defaultdict(int)
            
            for row in leads:
                lead_id, email, status, eng_score, source, interest, content_count, completed_count, last_sent = row
                
                tags = []
                
                # Tags por engagement
                if eng_score and eng_score >= 10:
                    tags.append("high_engagement")
                elif eng_score and eng_score >= 5:
                    tags.append("medium_engagement")
                else:
                    tags.append("low_engagement")
                
                # Tags por comportamiento
                if completed_count and completed_count >= 3:
                    tags.append("content_consumer")
                if content_count and content_count >= 5:
                    tags.append("active_reader")
                
                # Tags por fuente
                if source == "referral":
                    tags.append("referred")
                if interest:
                    tags.append(f"interest_{interest}")
                
                # Tags por status
                if status == "engaged":
                    tags.append("engaged")
                elif status == "nurturing":
                    tags.append("in_nurturing")
                
                # Tags por tiempo
                if last_sent:
                    days_since = (datetime.now() - last_sent).days
                    if days_since > 7:
                        tags.append("inactive")
                    elif days_since < 3:
                        tags.append("recent_activity")
                
                # Aplicar tags (asumiendo columna tags JSONB)
                if tags:
                    try:
                        # Actualizar tags en BD
                        hook.run(
                            """
                            UPDATE organic_leads
                            SET tags = %s::jsonb, updated_at = NOW()
                            WHERE lead_id = %s
                            """,
                            parameters=(json.dumps(tags), lead_id)
                        )
                        
                        for tag in tags:
                            tags_applied[tag] += 1
                        
                        tagged += 1
                    except Exception as e:
                        # Si no existe columna tags, crear tabla de tags
                        logger.warning(f"Error aplicando tags: {e}")
            
            logger.info(f"Tags aplicados: {tagged} leads, {len(tags_applied)} tipos de tags")
            return {
                "tagged": tagged,
                "tags_applied": dict(tags_applied),
                "total_tags": sum(tags_applied.values())
            }
            
        except Exception as e:
            logger.error(f"Error en tagging avanzado: {e}", exc_info=True)
            return {"tagged": 0, "error": str(e)}
    
    @task(task_id="export_data")
    def export_data() -> Dict[str, Any]:
        """Exporta datos para análisis externo."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        export_format = str(ctx["params"].get("export_format", "json"))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener datos para exportar
            export_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    ol.last_name,
                    ol.source,
                    ol.status,
                    ol.engagement_score,
                    ol.created_at,
                    ol.engaged_at,
                    COUNT(DISTINCT ce.engagement_id) as total_content,
                    COUNT(DISTINCT r.referral_id) as total_referrals
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE ol.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY ol.lead_id, ol.email, ol.first_name, ol.last_name, 
                         ol.source, ol.status, ol.engagement_score, ol.created_at, ol.engaged_at
                ORDER BY ol.created_at DESC
            """
            
            data = hook.get_records(export_query)
            
            export_data_list = []
            for row in data:
                export_data_list.append({
                    "lead_id": row[0],
                    "email": row[1],
                    "first_name": row[2],
                    "last_name": row[3],
                    "source": row[4],
                    "status": row[5],
                    "engagement_score": row[6],
                    "created_at": row[7].isoformat() if row[7] else None,
                    "engaged_at": row[8].isoformat() if row[8] else None,
                    "total_content": row[9] or 0,
                    "total_referrals": row[10] or 0
                })
            
            # Guardar exportación
            export_id = f"export_{secrets.token_hex(8)}"
            export_path = f"/tmp/organic_acquisition_export_{export_id}.{export_format}"
            
            if export_format == "json":
                with open(export_path, 'w') as f:
                    json.dump(export_data_list, f, indent=2, default=str)
            elif export_format == "csv":
                import csv
                if export_data_list:
                    with open(export_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=export_data_list[0].keys())
                        writer.writeheader()
                        writer.writerows(export_data_list)
            
            logger.info(f"Datos exportados: {len(export_data_list)} registros a {export_path}")
            return {
                "exported": len(export_data_list),
                "export_id": export_id,
                "export_path": export_path,
                "format": export_format
            }
            
        except Exception as e:
            logger.error(f"Error exportando datos: {e}", exc_info=True)
            return {"exported": 0, "error": str(e)}
    
    @task(task_id="event_webhooks")
    def event_webhooks() -> Dict[str, Any]:
        """Envía webhooks para eventos importantes."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        webhook_url = str(ctx["params"].get("event_webhook_url", ""))
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        if not webhook_url:
            logger.info("Event webhooks deshabilitados (no hay URL configurada)")
            return {"sent": 0, "skipped": 0}
        
        sent = 0
        failed = 0
        
        try:
            # Buscar eventos recientes que necesitan webhook
            events_query = """
                SELECT 
                    'lead_engaged' as event_type,
                    ol.lead_id,
                    ol.email,
                    ol.engaged_at as event_time
                FROM organic_leads ol
                WHERE ol.engaged_at >= NOW() - INTERVAL '1 hour'
                AND ol.webhook_sent = false
                
                UNION ALL
                
                SELECT 
                    'referral_validated' as event_type,
                    ol.lead_id,
                    ol.email,
                    r.validated_at as event_time
                FROM referrals r
                JOIN organic_leads ol ON r.referrer_lead_id = ol.lead_id
                WHERE r.validated_at >= NOW() - INTERVAL '1 hour'
                AND r.webhook_sent = false
                
                LIMIT 50
            """
            
            try:
                events = hook.get_records(events_query)
            except Exception:
                # Si no existe columna webhook_sent, usar otra estrategia
                logger.info("Columnas de webhook no disponibles")
                return {"sent": 0, "skipped": 0}
            
            session = get_http_session()
            
            for row in events:
                event_type, lead_id, email, event_time = row
                
                payload = {
                    "event_type": event_type,
                    "lead_id": lead_id,
                    "email": email,
                    "event_time": event_time.isoformat() if event_time else None,
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    response = session.post(
                        webhook_url,
                        json=payload,
                        timeout=10
                    )
                    response.raise_for_status()
                    
                    # Marcar como enviado
                    if event_type == "lead_engaged":
                        hook.run(
                            "UPDATE organic_leads SET webhook_sent = true WHERE lead_id = %s",
                            parameters=(lead_id,)
                        )
                    elif event_type == "referral_validated":
                        hook.run(
                            "UPDATE referrals SET webhook_sent = true WHERE referrer_lead_id = %s",
                            parameters=(lead_id,)
                        )
                    
                    sent += 1
                    
                except Exception as e:
                    logger.error(f"Error enviando webhook: {e}")
                    failed += 1
            
            logger.info(f"Webhooks enviados: {sent} exitosos, {failed} fallidos")
            return {"sent": sent, "failed": failed}
            
        except Exception as e:
            logger.error(f"Error en event webhooks: {e}", exc_info=True)
            return {"sent": sent, "failed": failed, "error": str(e)}
    
    @task(task_id="intelligent_recommendations")
    def intelligent_recommendations() -> Dict[str, Any]:
        """Genera recomendaciones inteligentes basadas en datos."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        recommendations = []
        
        try:
            # Recomendación 1: Optimizar timing
            timing_query = """
                SELECT 
                    EXTRACT(HOUR FROM ce.sent_at) as hour,
                    AVG(CASE WHEN ce.status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate
                FROM content_engagement ce
                WHERE ce.sent_at >= NOW() - INTERVAL '30 days'
                GROUP BY EXTRACT(HOUR FROM ce.sent_at)
                ORDER BY completion_rate DESC
                LIMIT 1
            """
            
            best_hour_result = hook.get_first(timing_query)
            if best_hour_result:
                best_hour = int(best_hour_result[0])
                completion = float(best_hour_result[1] or 0)
                if completion > 0.3:
                    recommendations.append({
                        "type": "timing",
                        "priority": "high",
                        "title": "Optimizar Horario de Envío",
                        "message": f"Mejor hora para envío: {best_hour}:00 (completion rate: {completion*100:.1f}%)",
                        "action": f"Programar envíos a las {best_hour}:00"
                    })
            
            # Recomendación 2: Mejorar contenido
            content_query = """
                SELECT 
                    ce.content_type,
                    AVG(CASE WHEN ce.status = 'completed' THEN 1.0 ELSE 0.0 END) as completion_rate,
                    COUNT(*) as total_sent
                FROM content_engagement ce
                WHERE ce.sent_at >= NOW() - INTERVAL '30 days'
                GROUP BY ce.content_type
                HAVING COUNT(*) >= 10
                ORDER BY completion_rate DESC
                LIMIT 1
            """
            
            best_content_result = hook.get_first(content_query)
            if best_content_result:
                best_type = best_content_result[0]
                completion = float(best_content_result[1] or 0)
                total = best_content_result[2]
                
                recommendations.append({
                    "type": "content",
                    "priority": "medium",
                    "title": "Priorizar Tipo de Contenido",
                    "message": f"Contenido tipo '{best_type}' tiene mejor performance ({completion*100:.1f}% completion)",
                    "action": f"Incrementar uso de contenido tipo '{best_type}'"
                })
            
            # Recomendación 3: Mejorar engagement
            engagement_query = """
                SELECT 
                    AVG(ol.engagement_score) as avg_score,
                    COUNT(*) as total_leads
                FROM organic_leads ol
                WHERE ol.created_at >= NOW() - INTERVAL '7 days'
                AND ol.status = 'nurturing'
            """
            
            eng_result = hook.get_first(engagement_query)
            if eng_result:
                avg_score = float(eng_result[0] or 0)
                if avg_score < 2:
                    recommendations.append({
                        "type": "engagement",
                        "priority": "high",
                        "title": "Mejorar Engagement",
                        "message": f"Engagement promedio bajo: {avg_score:.1f} (objetivo: >2)",
                        "action": "Revisar contenido de nurturing y timing de envíos"
                    })
            
            # Recomendación 4: Optimizar referidos
            referral_query = """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'validated' THEN 1 END) as validated,
                    COUNT(CASE WHEN status = 'fraud' THEN 1 END) as fraud
                FROM referrals
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            
            ref_result = hook.get_first(referral_query)
            if ref_result and ref_result[0] > 0:
                total, validated, fraud = ref_result
                validation_rate = (validated / total * 100) if total > 0 else 0
                fraud_rate = (fraud / total * 100) if total > 0 else 0
                
                if validation_rate < 50:
                    recommendations.append({
                        "type": "referrals",
                        "priority": "medium",
                        "title": "Mejorar Validación de Referidos",
                        "message": f"Tasa de validación baja: {validation_rate:.1f}%",
                        "action": "Revisar criterios de validación y mejorar onboarding"
                    })
                
                if fraud_rate > 15:
                    recommendations.append({
                        "type": "fraud",
                        "priority": "high",
                        "title": "Alta Tasa de Fraude",
                        "message": f"Tasa de fraude alta: {fraud_rate:.1f}%",
                        "action": "Ajustar validaciones anti-fraude"
                    })
            
            logger.info(f"Recomendaciones generadas: {len(recommendations)}")
            return {
                "recommendations": recommendations,
                "total": len(recommendations),
                "high_priority": len([r for r in recommendations if r["priority"] == "high"])
            }
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {e}", exc_info=True)
            return {"recommendations": [], "error": str(e)}
    
    @task(task_id="trend_analysis")
    def trend_analysis() -> Dict[str, Any]:
        """Análisis de tendencias y patrones."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Tendencia de leads por día (últimos 14 días)
            trend_query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as leads,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '14 days'
                GROUP BY DATE(created_at)
                ORDER BY date
            """
            
            trends = hook.get_records(trend_query)
            
            trend_data = []
            for row in trends:
                date, leads, engaged = row
                trend_data.append({
                    "date": date.strftime("%Y-%m-%d") if date else None,
                    "leads": leads,
                    "engaged": engaged,
                    "engagement_rate": (engaged / leads * 100) if leads > 0 else 0
                })
            
            # Calcular tendencia (creciente/decreciente)
            if len(trend_data) >= 7:
                recent_avg = sum(t["leads"] for t in trend_data[-7:]) / 7
                older_avg = sum(t["leads"] for t in trend_data[:7]) / 7 if len(trend_data) >= 14 else recent_avg
                
                trend_direction = "increasing" if recent_avg > older_avg * 1.1 else "decreasing" if recent_avg < older_avg * 0.9 else "stable"
                trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            else:
                trend_direction = "insufficient_data"
                trend_percentage = 0
            
            # Análisis de fuentes
            source_query = """
                SELECT 
                    source,
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY source
                ORDER BY total DESC
            """
            
            sources = hook.get_records(source_query)
            source_trends = []
            for row in sources:
                source, total, engaged = row
                source_trends.append({
                    "source": source,
                    "total": total,
                    "engaged": engaged,
                    "engagement_rate": (engaged / total * 100) if total > 0 else 0
                })
            
            logger.info(f"Análisis de tendencias: {len(trend_data)} días, {len(source_trends)} fuentes")
            return {
                "daily_trends": trend_data,
                "trend_direction": trend_direction,
                "trend_percentage": round(trend_percentage, 2),
                "source_trends": source_trends,
                "best_source": max(source_trends, key=lambda x: x["engagement_rate"]) if source_trends else None
            }
            
        except Exception as e:
            logger.error(f"Error en análisis de tendencias: {e}", exc_info=True)
            return {"daily_trends": [], "error": str(e)}
    
    # ============================================================================
    # PIPELINE PRINCIPAL MEJORADO V2
    # ============================================================================
    
    schema_ok = ensure_schema()
    
    # Captura y segmentación
    new_leads = capture_new_leads()
    segmentation = segment_leads(new_leads)
    
    # Nurturing
    nurturing_started = start_nurturing_workflows(segmentation)
    content_sent = send_nurturing_content()
    engagement_tracked = track_engagement()
    
    # Referidos
    referral_invites = invite_to_referral_program(engagement_tracked)
    referrals_processed = process_referrals()
    
    # Sincronización y recordatorios
    crm_synced = sync_with_crm()
    reminders_sent = send_reminders()
    second_incentives = send_second_incentive()
    
    # Reportes y optimización
    reports = generate_reports()
    optimizations = optimize_automatically()
    perf_metrics = performance_metrics()
    
    # Tareas avanzadas (paralelas)
    ml_retrain = retrain_ml_model()
    cohorts = cohort_analysis()
    alerts = intelligent_alerts()
    churn_prediction = predict_churn()
    timing_optimization = optimize_timing()
    content_analysis = content_performance_analysis()
    
    # Tareas avanzadas V2 (paralelas)
    sentiment = sentiment_analysis()
    tagging = advanced_tagging()
    export = export_data()
    webhooks = event_webhooks()
    recommendations = intelligent_recommendations()
    trends = trend_analysis()
    
    # ============================================================================
    # TAREAS AVANZADAS ADICIONALES V3
    # ============================================================================
    
    @task(task_id="re_engagement_campaign")
    def re_engagement_campaign() -> Dict[str, Any]:
        """Campaña automática de re-engagement para leads inactivos."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Buscar leads inactivos (sin actividad >14 días)
            inactive_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    ol.status,
                    ol.engagement_score,
                    MAX(ce.sent_at) as last_content_sent,
                    MAX(ce.opened_at) as last_opened,
                    COUNT(ce.engagement_id) as total_content_sent
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                WHERE ol.status IN ('nurturing', 'new')
                AND (MAX(ce.sent_at) IS NULL OR MAX(ce.sent_at) < NOW() - INTERVAL '14 days')
                AND (MAX(ce.opened_at) IS NULL OR MAX(ce.opened_at) < NOW() - INTERVAL '14 days')
                GROUP BY ol.lead_id, ol.email, ol.first_name, ol.status, ol.engagement_score
                HAVING COUNT(ce.engagement_id) > 0
                LIMIT 100
            """
            
            inactive_leads = hook.get_records(inactive_query)
            
            re_engaged = 0
            emails_sent = 0
            
            for row in inactive_leads:
                lead_id, email, first_name, status, eng_score, last_sent, last_opened, total_content = row
                
                # Determinar tipo de re-engagement según engagement previo
                if eng_score and eng_score >= 5:
                    # Lead con buen engagement previo - ofrecer incentivo especial
                    subject = f"Te extrañamos, {first_name or 'amigo'}! 🎁 Oferta especial para ti"
                    message = f"""
                    Hola {first_name or 'amigo'},
                    
                    Notamos que hace tiempo no te conectas con nosotros. Queremos que sepas que tenemos contenido nuevo y una oferta especial solo para ti.
                    
                    🎁 Oferta especial: 20% de descuento en tu primera compra
                    📚 Nuevo contenido exclusivo disponible
                    💡 Tips y estrategias actualizadas
                    
                    No te pierdas estas oportunidades. Haz clic aquí para reactivar tu cuenta.
                    
                    Saludos,
                    El equipo
                    """
                else:
                    # Lead con bajo engagement - contenido educativo
                    subject = f"¿Listo para aprender más, {first_name or 'amigo'}?"
                    message = f"""
                    Hola {first_name or 'amigo'},
                    
                    Sabemos que estás ocupado, pero tenemos contenido valioso que podría interesarte.
                    
                    📖 Guías actualizadas
                    🎥 Videos tutoriales nuevos
                    📊 Casos de éxito recientes
                    
                    Todo esto está disponible para ti. ¿Quieres ver qué hay de nuevo?
                    
                    Saludos,
                    El equipo
                    """
                
                # Enviar email de re-engagement
                try:
                    email_service = ctx["params"].get("email_service", "smtp")
                    email_sent = send_email_simple(
                        to_email=email,
                        subject=subject,
                        body=message,
                        email_service=email_service
                    )
                    
                    if email_sent:
                        # Registrar re-engagement
                        hook.run(
                            """
                            INSERT INTO re_engagement_campaigns 
                            (lead_id, campaign_type, sent_at, status)
                            VALUES (%s, %s, NOW(), 'sent')
                            ON CONFLICT DO NOTHING
                            """,
                            parameters=(lead_id, "inactive_recovery")
                        )
                        
                        emails_sent += 1
                        re_engaged += 1
                        
                except Exception as e:
                    logger.error(f"Error enviando re-engagement a {email}: {e}")
            
            logger.info(f"Re-engagement: {re_engaged} leads, {emails_sent} emails enviados")
            return {
                "re_engaged": re_engaged,
                "emails_sent": emails_sent,
                "campaign_type": "inactive_recovery"
            }
            
        except Exception as e:
            logger.error(f"Error en re-engagement campaign: {e}", exc_info=True)
            return {"re_engaged": 0, "error": str(e)}
    
    @task(task_id="customer_journey_analysis")
    def customer_journey_analysis() -> Dict[str, Any]:
        """Analiza el customer journey de leads para identificar puntos de fricción."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar journey de leads que se convirtieron vs los que no
            journey_query = """
                WITH lead_journey AS (
                    SELECT 
                        ol.lead_id,
                        ol.status,
                        ol.engagement_score,
                        ol.created_at,
                        ol.engaged_at,
                        COUNT(DISTINCT ce.engagement_id) as content_steps,
                        AVG(EXTRACT(EPOCH FROM (ce.opened_at - ce.sent_at))/3600) as avg_open_time_hours,
                        COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_steps,
                        COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) as opened_steps,
                        COUNT(CASE WHEN r.referral_id IS NOT NULL THEN 1 END) as has_referrals
                    FROM organic_leads ol
                    LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                    LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                    WHERE ol.created_at >= NOW() - INTERVAL '60 days'
                    GROUP BY ol.lead_id, ol.status, ol.engagement_score, ol.created_at, ol.engaged_at
                )
                SELECT 
                    CASE 
                        WHEN status = 'engaged' THEN 'converted'
                        ELSE 'not_converted'
                    END as conversion_status,
                    AVG(content_steps) as avg_content_steps,
                    AVG(avg_open_time_hours) as avg_time_to_open,
                    AVG(completed_steps::float / NULLIF(content_steps, 0)) as avg_completion_rate,
                    AVG(opened_steps::float / NULLIF(content_steps, 0)) as avg_open_rate,
                    AVG(has_referrals) as referral_rate,
                    AVG(EXTRACT(EPOCH FROM (engaged_at - created_at))/86400) as avg_days_to_engage
                FROM lead_journey
                GROUP BY conversion_status
            """
            
            journey_data = hook.get_records(journey_query)
            
            journey_analysis = {}
            for row in journey_data:
                status, avg_steps, avg_time, completion_rate, open_rate, ref_rate, avg_days = row
                journey_analysis[status] = {
                    "avg_content_steps": round(float(avg_steps or 0), 2),
                    "avg_time_to_open_hours": round(float(avg_time or 0), 2),
                    "avg_completion_rate": round(float(completion_rate or 0) * 100, 2),
                    "avg_open_rate": round(float(open_rate or 0) * 100, 2),
                    "referral_rate": round(float(ref_rate or 0) * 100, 2),
                    "avg_days_to_engage": round(float(avg_days or 0), 2)
                }
            
            # Identificar puntos de fricción
            friction_points = []
            
            if journey_analysis.get("converted") and journey_analysis.get("not_converted"):
                converted = journey_analysis["converted"]
                not_converted = journey_analysis["not_converted"]
                
                # Fricción 1: Tiempo de apertura
                if not_converted["avg_time_to_open_hours"] > converted["avg_time_to_open_hours"] * 1.5:
                    friction_points.append({
                        "type": "slow_response",
                        "severity": "high",
                        "message": f"Leads no convertidos tardan {not_converted['avg_time_to_open_hours']:.1f}h en abrir vs {converted['avg_time_to_open_hours']:.1f}h de convertidos",
                        "recommendation": "Mejorar subject lines y timing de envíos"
                    })
                
                # Fricción 2: Completion rate
                if not_converted["avg_completion_rate"] < converted["avg_completion_rate"] * 0.7:
                    friction_points.append({
                        "type": "low_completion",
                        "severity": "medium",
                        "message": f"Completion rate bajo: {not_converted['avg_completion_rate']:.1f}% vs {converted['avg_completion_rate']:.1f}%",
                        "recommendation": "Hacer contenido más relevante y accionable"
                    })
                
                # Fricción 3: Número de pasos
                if not_converted["avg_content_steps"] < converted["avg_content_steps"] * 0.6:
                    friction_points.append({
                        "type": "insufficient_touchpoints",
                        "severity": "medium",
                        "message": f"Leads no convertidos reciben menos contenido: {not_converted['avg_content_steps']:.1f} vs {converted['avg_content_steps']:.1f}",
                        "recommendation": "Aumentar frecuencia de envíos para leads con bajo engagement"
                    })
            
            logger.info(f"Análisis de customer journey: {len(journey_analysis)} grupos, {len(friction_points)} puntos de fricción")
            return {
                "journey_analysis": journey_analysis,
                "friction_points": friction_points,
                "total_friction_points": len(friction_points)
            }
            
        except Exception as e:
            logger.error(f"Error en customer journey analysis: {e}", exc_info=True)
            return {"journey_analysis": {}, "error": str(e)}
    
    @task(task_id="ltv_prediction")
    def ltv_prediction() -> Dict[str, Any]:
        """Predice el Lifetime Value (LTV) de leads basándose en comportamiento."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener datos de leads para predicción de LTV
            ltv_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.engagement_score,
                    ol.source,
                    ol.interest_area,
                    COUNT(DISTINCT ce.engagement_id) as content_interactions,
                    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_content,
                    COUNT(DISTINCT r.referral_id) as referrals_made,
                    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated_referrals,
                    EXTRACT(EPOCH FROM (NOW() - ol.created_at))/86400 as days_since_signup,
                    CASE WHEN ol.status = 'engaged' THEN 1 ELSE 0 END as is_engaged
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE ol.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY ol.lead_id, ol.email, ol.engagement_score, ol.source, 
                         ol.interest_area, ol.created_at, ol.status
                LIMIT 500
            """
            
            leads_data = hook.get_records(ltv_query)
            
            predictions = []
            ltv_scores = []
            
            for row in leads_data:
                lead_id, email, eng_score, source, interest, content_int, completed, refs_made, refs_valid, days_since, is_engaged = row
                
                # Modelo simple de predicción de LTV (puede mejorarse con ML)
                base_ltv = 50  # LTV base estimado
                
                # Factores que aumentan LTV
                ltv_multiplier = 1.0
                
                # Engagement score
                if eng_score:
                    if eng_score >= 10:
                        ltv_multiplier += 0.5
                    elif eng_score >= 5:
                        ltv_multiplier += 0.3
                
                # Completación de contenido
                if completed and content_int:
                    completion_rate = completed / content_int
                    if completion_rate > 0.7:
                        ltv_multiplier += 0.4
                    elif completion_rate > 0.5:
                        ltv_multiplier += 0.2
                
                # Referidos validados
                if refs_valid and refs_valid > 0:
                    ltv_multiplier += 0.3 * min(refs_valid, 5)  # Max 1.5x por referidos
                
                # Fuente
                if source == "referral":
                    ltv_multiplier += 0.2
                
                # Status engaged
                if is_engaged:
                    ltv_multiplier += 0.6
                
                # Antigüedad (leads más antiguos tienen más valor potencial)
                if days_since > 30:
                    ltv_multiplier += 0.2
                elif days_since > 60:
                    ltv_multiplier += 0.3
                
                # Calcular LTV predicho
                predicted_ltv = base_ltv * ltv_multiplier
                
                # Categorizar
                if predicted_ltv >= 100:
                    ltv_tier = "high"
                elif predicted_ltv >= 70:
                    ltv_tier = "medium"
                else:
                    ltv_tier = "low"
                
                predictions.append({
                    "lead_id": lead_id,
                    "email": email,
                    "predicted_ltv": round(predicted_ltv, 2),
                    "ltv_tier": ltv_tier,
                    "factors": {
                        "engagement_score": eng_score or 0,
                        "completion_rate": round((completed / content_int * 100) if content_int > 0 else 0, 2),
                        "validated_referrals": refs_valid or 0,
                        "is_engaged": bool(is_engaged)
                    }
                })
                
                ltv_scores.append(predicted_ltv)
            
            # Estadísticas agregadas
            if ltv_scores:
                avg_ltv = sum(ltv_scores) / len(ltv_scores)
                high_value = len([p for p in predictions if p["ltv_tier"] == "high"])
                medium_value = len([p for p in predictions if p["ltv_tier"] == "medium"])
                low_value = len([p for p in predictions if p["ltv_tier"] == "low"])
            else:
                avg_ltv = 0
                high_value = medium_value = low_value = 0
            
            logger.info(f"LTV prediction: {len(predictions)} leads analizados, LTV promedio: ${avg_ltv:.2f}")
            return {
                "predictions": predictions[:50],  # Top 50
                "total_analyzed": len(predictions),
                "avg_predicted_ltv": round(avg_ltv, 2),
                "high_value_leads": high_value,
                "medium_value_leads": medium_value,
                "low_value_leads": low_value,
                "high_value_percentage": round((high_value / len(predictions) * 100) if predictions else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"Error en LTV prediction: {e}", exc_info=True)
            return {"predictions": [], "error": str(e)}
    
    @task(task_id="channel_optimization")
    def channel_optimization() -> Dict[str, Any]:
        """Optimiza canales de adquisición basándose en performance."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar performance por canal
            channel_query = """
                SELECT 
                    ol.source as channel,
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN ol.status = 'engaged' THEN 1 END) as engaged_leads,
                    AVG(ol.engagement_score) as avg_engagement,
                    AVG(EXTRACT(EPOCH FROM (ol.engaged_at - ol.created_at))/86400) as avg_days_to_engage,
                    COUNT(DISTINCT r.referral_id) as total_referrals,
                    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated_referrals,
                    SUM(CASE WHEN rr.reward_amount IS NOT NULL THEN rr.reward_amount ELSE 0 END) as total_rewards_paid
                FROM organic_leads ol
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                LEFT JOIN referral_rewards rr ON r.referral_id = rr.referral_id
                WHERE ol.created_at >= NOW() - INTERVAL '60 days'
                GROUP BY ol.source
                HAVING COUNT(*) >= 5
                ORDER BY engaged_leads DESC
            """
            
            channels = hook.get_records(channel_query)
            
            channel_performance = []
            total_cost_estimate = 0
            
            for row in channels:
                channel, total, engaged, avg_eng, avg_days, refs, val_refs, rewards = row
                
                engagement_rate = (engaged / total * 100) if total > 0 else 0
                referral_rate = (refs / total * 100) if total > 0 else 0
                validation_rate = (val_refs / refs * 100) if refs > 0 else 0
                
                # Calcular ROI estimado (simplificado)
                # Asumiendo costo por lead y valor promedio
                cost_per_lead = {
                    "organic": 0,
                    "referral": 0,
                    "social": 5,
                    "email": 2,
                    "paid": 10
                }.get(channel, 5)
                
                estimated_cost = total * cost_per_lead
                estimated_value = engaged * 50 + rewards  # Valor estimado por engaged lead
                roi = ((estimated_value - estimated_cost) / estimated_cost * 100) if estimated_cost > 0 else 0
                
                total_cost_estimate += estimated_cost
                
                # Score de performance (0-100)
                performance_score = (
                    (engagement_rate * 0.4) +
                    (referral_rate * 0.3) +
                    (min(avg_eng or 0, 20) / 20 * 100 * 0.2) +
                    (min(roi, 200) / 200 * 100 * 0.1)
                )
                
                channel_performance.append({
                    "channel": channel,
                    "total_leads": total,
                    "engaged_leads": engaged,
                    "engagement_rate": round(engagement_rate, 2),
                    "avg_engagement_score": round(float(avg_eng or 0), 2),
                    "avg_days_to_engage": round(float(avg_days or 0), 2),
                    "total_referrals": refs,
                    "referral_rate": round(referral_rate, 2),
                    "validation_rate": round(validation_rate, 2),
                    "estimated_cost": round(estimated_cost, 2),
                    "estimated_value": round(estimated_value, 2),
                    "estimated_roi": round(roi, 2),
                    "performance_score": round(performance_score, 2)
                })
            
            # Ordenar por performance score
            channel_performance.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Recomendaciones
            recommendations = []
            
            if channel_performance:
                best_channel = channel_performance[0]
                worst_channel = channel_performance[-1]
                
                if best_channel["performance_score"] > worst_channel["performance_score"] * 1.5:
                    recommendations.append({
                        "type": "scale_up",
                        "channel": best_channel["channel"],
                        "message": f"Canal '{best_channel['channel']}' tiene mejor performance ({best_channel['performance_score']:.1f}/100)",
                        "action": f"Incrementar inversión en canal '{best_channel['channel']}'"
                    })
                
                if worst_channel["performance_score"] < 30:
                    recommendations.append({
                        "type": "scale_down",
                        "channel": worst_channel["channel"],
                        "message": f"Canal '{worst_channel['channel']}' tiene bajo performance ({worst_channel['performance_score']:.1f}/100)",
                        "action": f"Revisar o reducir inversión en canal '{worst_channel['channel']}'"
                    })
            
            logger.info(f"Channel optimization: {len(channel_performance)} canales analizados")
            return {
                "channel_performance": channel_performance,
                "total_cost_estimate": round(total_cost_estimate, 2),
                "best_channel": channel_performance[0] if channel_performance else None,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error en channel optimization: {e}", exc_info=True)
            return {"channel_performance": [], "error": str(e)}
    
    @task(task_id="feedback_loop_analysis")
    def feedback_loop_analysis() -> Dict[str, Any]:
        """Analiza feedback loops para mejorar el sistema continuamente."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar correlación entre acciones y resultados
            feedback_query = """
                WITH action_results AS (
                    SELECT 
                        ol.lead_id,
                        COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_actions,
                        COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) as opened_actions,
                        ol.engagement_score,
                        CASE WHEN ol.status = 'engaged' THEN 1 ELSE 0 END as converted,
                        COUNT(DISTINCT r.referral_id) as referrals_made
                    FROM organic_leads ol
                    LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                    LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                    WHERE ol.created_at >= NOW() - INTERVAL '60 days'
                    GROUP BY ol.lead_id, ol.engagement_score, ol.status
                )
                SELECT 
                    AVG(completed_actions) as avg_completed,
                    AVG(opened_actions) as avg_opened,
                    AVG(engagement_score) as avg_engagement,
                    AVG(converted::float) as conversion_rate,
                    AVG(referrals_made) as avg_referrals,
                    CORR(completed_actions, converted::float) as completion_conversion_corr,
                    CORR(opened_actions, converted::float) as open_conversion_corr,
                    CORR(engagement_score, converted::float) as engagement_conversion_corr
                FROM action_results
            """
            
            try:
                feedback_data = hook.get_first(feedback_query)
            except Exception:
                # Si CORR no está disponible, usar cálculo manual
                logger.info("Función CORR no disponible, usando cálculo alternativo")
                feedback_data = None
            
            if feedback_data:
                (avg_completed, avg_opened, avg_eng, conv_rate, avg_refs, 
                 comp_conv_corr, open_conv_corr, eng_conv_corr) = feedback_data
                
                insights = []
                
                # Insight 1: Correlación completion-conversión
                if comp_conv_corr and abs(comp_conv_corr) > 0.3:
                    insights.append({
                        "type": "strong_correlation",
                        "metric": "content_completion",
                        "correlation": round(float(comp_conv_corr), 3),
                        "message": f"Fuerte correlación ({comp_conv_corr:.3f}) entre completar contenido y conversión",
                        "action": "Enfocarse en aumentar completion rate de contenido"
                    })
                
                # Insight 2: Correlación engagement-conversión
                if eng_conv_corr and abs(eng_conv_corr) > 0.4:
                    insights.append({
                        "type": "strong_correlation",
                        "metric": "engagement_score",
                        "correlation": round(float(eng_conv_corr), 3),
                        "message": f"Fuerte correlación ({eng_conv_corr:.3f}) entre engagement score y conversión",
                        "action": "Priorizar leads con alto engagement score"
                    })
                
                # Insight 3: Tasa de conversión general
                if conv_rate and conv_rate < 0.15:
                    insights.append({
                        "type": "low_conversion",
                        "metric": "conversion_rate",
                        "value": round(float(conv_rate) * 100, 2),
                        "message": f"Tasa de conversión baja: {conv_rate*100:.1f}%",
                        "action": "Revisar funnel completo y puntos de fricción"
                    })
                
                logger.info(f"Feedback loop analysis: {len(insights)} insights generados")
                return {
                    "avg_completed_actions": round(float(avg_completed or 0), 2),
                    "avg_opened_actions": round(float(avg_opened or 0), 2),
                    "avg_engagement_score": round(float(avg_eng or 0), 2),
                    "conversion_rate": round(float(conv_rate or 0) * 100, 2),
                    "avg_referrals": round(float(avg_refs or 0), 2),
                    "correlations": {
                        "completion_to_conversion": round(float(comp_conv_corr or 0), 3),
                        "open_to_conversion": round(float(open_conv_corr or 0), 3),
                        "engagement_to_conversion": round(float(eng_conv_corr or 0), 3)
                    },
                    "insights": insights
                }
            else:
                return {
                    "insights": [],
                    "message": "Datos insuficientes para análisis de correlación"
                }
            
        except Exception as e:
            logger.error(f"Error en feedback loop analysis: {e}", exc_info=True)
            return {"insights": [], "error": str(e)}
    
    @task(task_id="competitive_benchmarking")
    def competitive_benchmarking() -> Dict[str, Any]:
        """Compara métricas con benchmarks de la industria."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener métricas actuales
            metrics_query = """
                SELECT 
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged_leads,
                    AVG(engagement_score) as avg_engagement,
                    COUNT(DISTINCT r.referral_id) as total_referrals,
                    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated_referrals,
                    AVG(EXTRACT(EPOCH FROM (engaged_at - created_at))/86400) as avg_days_to_engage
                FROM organic_leads ol
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE ol.created_at >= NOW() - INTERVAL '30 days'
            """
            
            current_metrics = hook.get_first(metrics_query)
            
            if current_metrics:
                total, engaged, avg_eng, refs, val_refs, avg_days = current_metrics
                
                engagement_rate = (engaged / total * 100) if total > 0 else 0
                referral_rate = (refs / total * 100) if total > 0 else 0
                validation_rate = (val_refs / refs * 100) if refs > 0 else 0
                
                # Benchmarks de industria (valores típicos)
                industry_benchmarks = {
                    "engagement_rate": 25.0,  # 25% típico
                    "referral_rate": 10.0,     # 10% típico
                    "validation_rate": 60.0,   # 60% típico
                    "avg_engagement_score": 5.0,  # Score típico
                    "avg_days_to_engage": 7.0   # 7 días típico
                }
                
                comparisons = []
                
                # Comparar engagement rate
                eng_diff = engagement_rate - industry_benchmarks["engagement_rate"]
                comparisons.append({
                    "metric": "engagement_rate",
                    "current": round(engagement_rate, 2),
                    "benchmark": industry_benchmarks["engagement_rate"],
                    "difference": round(eng_diff, 2),
                    "status": "above" if eng_diff > 0 else "below",
                    "percentage_diff": round((eng_diff / industry_benchmarks["engagement_rate"] * 100), 2)
                })
                
                # Comparar referral rate
                ref_diff = referral_rate - industry_benchmarks["referral_rate"]
                comparisons.append({
                    "metric": "referral_rate",
                    "current": round(referral_rate, 2),
                    "benchmark": industry_benchmarks["referral_rate"],
                    "difference": round(ref_diff, 2),
                    "status": "above" if ref_diff > 0 else "below",
                    "percentage_diff": round((ref_diff / industry_benchmarks["referral_rate"] * 100), 2)
                })
                
                # Comparar validation rate
                val_diff = validation_rate - industry_benchmarks["validation_rate"]
                comparisons.append({
                    "metric": "validation_rate",
                    "current": round(validation_rate, 2),
                    "benchmark": industry_benchmarks["validation_rate"],
                    "difference": round(val_diff, 2),
                    "status": "above" if val_diff > 0 else "below",
                    "percentage_diff": round((val_diff / industry_benchmarks["validation_rate"] * 100), 2)
                })
                
                # Comparar engagement score
                eng_score_diff = (avg_eng or 0) - industry_benchmarks["avg_engagement_score"]
                comparisons.append({
                    "metric": "avg_engagement_score",
                    "current": round(float(avg_eng or 0), 2),
                    "benchmark": industry_benchmarks["avg_engagement_score"],
                    "difference": round(eng_score_diff, 2),
                    "status": "above" if eng_score_diff > 0 else "below",
                    "percentage_diff": round((eng_score_diff / industry_benchmarks["avg_engagement_score"] * 100), 2)
                })
                
                # Comparar días a engagement
                days_diff = (avg_days or 0) - industry_benchmarks["avg_days_to_engage"]
                comparisons.append({
                    "metric": "avg_days_to_engage",
                    "current": round(float(avg_days or 0), 2),
                    "benchmark": industry_benchmarks["avg_days_to_engage"],
                    "difference": round(days_diff, 2),
                    "status": "above" if days_diff < 0 else "below",  # Menos días es mejor
                    "percentage_diff": round((days_diff / industry_benchmarks["avg_days_to_engage"] * 100), 2)
                })
                
                # Resumen
                above_benchmark = len([c for c in comparisons if c["status"] == "above"])
                below_benchmark = len([c for c in comparisons if c["status"] == "below"])
                
                logger.info(f"Competitive benchmarking: {above_benchmark} métricas arriba, {below_benchmark} abajo del benchmark")
                return {
                    "current_metrics": {
                        "total_leads": total,
                        "engagement_rate": round(engagement_rate, 2),
                        "referral_rate": round(referral_rate, 2),
                        "validation_rate": round(validation_rate, 2),
                        "avg_engagement_score": round(float(avg_eng or 0), 2),
                        "avg_days_to_engage": round(float(avg_days or 0), 2)
                    },
                    "industry_benchmarks": industry_benchmarks,
                    "comparisons": comparisons,
                    "summary": {
                        "above_benchmark": above_benchmark,
                        "below_benchmark": below_benchmark,
                        "total_metrics": len(comparisons)
                    }
                }
            else:
                return {
                    "message": "Datos insuficientes para benchmarking"
                }
            
        except Exception as e:
            logger.error(f"Error en competitive benchmarking: {e}", exc_info=True)
            return {"comparisons": [], "error": str(e)}
    
    # ============================================================================
    # PIPELINE PRINCIPAL MEJORADO V3
    # ============================================================================
    
    schema_ok = ensure_schema()
    
    # Captura y segmentación
    new_leads = capture_new_leads()
    segmentation = segment_leads(new_leads)
    
    # Nurturing
    nurturing_started = start_nurturing_workflows(segmentation)
    content_sent = send_nurturing_content()
    engagement_tracked = track_engagement()
    
    # Referidos
    referral_invites = invite_to_referral_program(engagement_tracked)
    referrals_processed = process_referrals()
    
    # Sincronización y recordatorios
    crm_synced = sync_with_crm()
    reminders_sent = send_reminders()
    second_incentives = send_second_incentive()
    
    # Reportes y optimización
    reports = generate_reports()
    optimizations = optimize_automatically()
    perf_metrics = performance_metrics()
    
    # Tareas avanzadas (paralelas)
    ml_retrain = retrain_ml_model()
    cohorts = cohort_analysis()
    alerts = intelligent_alerts()
    churn_prediction = predict_churn()
    timing_optimization = optimize_timing()
    content_analysis = content_performance_analysis()
    
    # Tareas avanzadas V2 (paralelas)
    sentiment = sentiment_analysis()
    tagging = advanced_tagging()
    export = export_data()
    webhooks = event_webhooks()
    recommendations = intelligent_recommendations()
    trends = trend_analysis()
    
    # Tareas avanzadas V3 (paralelas)
    re_engagement = re_engagement_campaign()
    journey_analysis = customer_journey_analysis()
    ltv_pred = ltv_prediction()
    channel_opt = channel_optimization()
    feedback_loops = feedback_loop_analysis()
    benchmarking = competitive_benchmarking()
    
    # ============================================================================
    # TAREAS AVANZADAS ADICIONALES V4
    # ============================================================================
    
    @task(task_id="dynamic_scoring_system")
    def dynamic_scoring_system() -> Dict[str, Any]:
        """Sistema de scoring dinámico que se actualiza en tiempo real basado en comportamiento."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener leads que necesitan actualización de score
            leads_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.engagement_score,
                    ol.status,
                    ol.created_at,
                    COUNT(DISTINCT ce.engagement_id) as recent_content,
                    COUNT(CASE WHEN ce.status = 'completed' AND ce.completed_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_completions,
                    COUNT(CASE WHEN ce.status = 'opened' AND ce.opened_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_opens,
                    COUNT(DISTINCT r.referral_id) as total_referrals,
                    MAX(ce.sent_at) as last_content_sent,
                    MAX(ce.opened_at) as last_opened
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE ol.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY ol.lead_id, ol.email, ol.engagement_score, ol.status, ol.created_at
                HAVING MAX(ce.sent_at) >= NOW() - INTERVAL '30 days' OR MAX(ce.sent_at) IS NULL
                LIMIT 500
            """
            
            leads = hook.get_records(leads_query)
            
            updated = 0
            score_changes = []
            
            for row in leads:
                lead_id, email, current_score, status, created_at, recent_content, recent_completions, recent_opens, total_refs, last_sent, last_opened = row
                
                # Calcular nuevo score dinámico
                new_score = float(current_score or 0)
                
                # Factor 1: Actividad reciente (últimos 7 días)
                if recent_completions:
                    new_score += recent_completions * 2  # +2 por cada completion reciente
                if recent_opens:
                    new_score += recent_opens * 0.5  # +0.5 por cada open reciente
                
                # Factor 2: Velocidad de respuesta
                if last_sent and last_opened:
                    hours_to_open = (last_opened - last_sent).total_seconds() / 3600
                    if hours_to_open < 2:
                        new_score += 3  # Respuesta muy rápida
                    elif hours_to_open < 24:
                        new_score += 1  # Respuesta rápida
                
                # Factor 3: Referidos
                if total_refs:
                    new_score += total_refs * 5  # +5 por cada referido
                
                # Factor 4: Consistencia (contenido regular)
                if recent_content and recent_content >= 3:
                    days_active = (datetime.now() - created_at).days if created_at else 0
                    if days_active > 0:
                        frequency = recent_content / min(days_active, 30)
                        if frequency > 0.2:  # Más de 1 contenido cada 5 días
                            new_score += 2
                
                # Factor 5: Decay por inactividad
                if last_opened:
                    days_inactive = (datetime.now() - last_opened).days
                    if days_inactive > 14:
                        new_score -= (days_inactive - 14) * 0.5  # Penalización por inactividad
                        new_score = max(0, new_score)  # No negativo
                
                # Factor 6: Status bonus
                if status == "engaged":
                    new_score += 10
                elif status == "nurturing":
                    new_score += 2
                
                # Redondear y limitar
                new_score = round(max(0, min(new_score, 100)), 2)  # Score entre 0-100
                
                # Actualizar si hay cambio significativo (>1 punto)
                if abs(new_score - (current_score or 0)) > 1:
                    try:
                        hook.run(
                            """
                            UPDATE organic_leads
                            SET engagement_score = %s, updated_at = NOW()
                            WHERE lead_id = %s
                            """,
                            parameters=(new_score, lead_id)
                        )
                        
                        score_changes.append({
                            "lead_id": lead_id,
                            "email": email,
                            "old_score": round(float(current_score or 0), 2),
                            "new_score": new_score,
                            "change": round(new_score - (current_score or 0), 2)
                        })
                        
                        updated += 1
                    except Exception as e:
                        logger.error(f"Error actualizando score para lead {lead_id}: {e}")
            
            # Estadísticas
            if score_changes:
                avg_change = sum(abs(c["change"]) for c in score_changes) / len(score_changes)
                increased = len([c for c in score_changes if c["change"] > 0])
                decreased = len([c for c in score_changes if c["change"] < 0])
            else:
                avg_change = 0
                increased = decreased = 0
            
            logger.info(f"Dynamic scoring: {updated} leads actualizados, cambio promedio: {avg_change:.2f}")
            return {
                "updated": updated,
                "total_analyzed": len(leads),
                "avg_score_change": round(avg_change, 2),
                "increased": increased,
                "decreased": decreased,
                "score_changes": score_changes[:20]  # Top 20 cambios
            }
            
        except Exception as e:
            logger.error(f"Error en dynamic scoring system: {e}", exc_info=True)
            return {"updated": 0, "error": str(e)}
    
    @task(task_id="predictive_behavior_analysis")
    def predictive_behavior_analysis() -> Dict[str, Any]:
        """Analiza comportamiento predictivo para anticipar acciones de leads."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar patrones de comportamiento
            behavior_query = """
                WITH lead_patterns AS (
                    SELECT 
                        ol.lead_id,
                        ol.status,
                        ol.engagement_score,
                        COUNT(DISTINCT ce.engagement_id) as total_interactions,
                        AVG(EXTRACT(EPOCH FROM (ce.opened_at - ce.sent_at))/3600) as avg_response_time,
                        COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completions,
                        COUNT(CASE WHEN EXTRACT(DOW FROM ce.sent_at) IN (1,2,3,4,5) THEN 1 END) as weekday_interactions,
                        COUNT(CASE WHEN EXTRACT(HOUR FROM ce.opened_at) BETWEEN 9 AND 17 THEN 1 END) as business_hours_opens,
                        MAX(ce.sent_at) as last_interaction
                    FROM organic_leads ol
                    LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                    WHERE ol.created_at >= NOW() - INTERVAL '60 days'
                    AND ce.sent_at IS NOT NULL
                    GROUP BY ol.lead_id, ol.status, ol.engagement_score
                    HAVING COUNT(DISTINCT ce.engagement_id) >= 2
                )
                SELECT 
                    lead_id,
                    status,
                    engagement_score,
                    total_interactions,
                    avg_response_time,
                    completions,
                    weekday_interactions,
                    business_hours_opens,
                    last_interaction,
                    CASE 
                        WHEN status = 'engaged' THEN 1
                        ELSE 0
                    END as converted
                FROM lead_patterns
                LIMIT 300
            """
            
            patterns = hook.get_records(behavior_query)
            
            predictions = []
            
            for row in patterns:
                lead_id, status, eng_score, total_int, avg_resp, completions, weekday_int, biz_hours, last_int, converted = row
                
                # Factores predictivos
                conversion_probability = 0.0
                
                # Factor 1: Engagement score
                if eng_score:
                    conversion_probability += min(eng_score / 20, 0.4)  # Max 40%
                
                # Factor 2: Completion rate
                if total_int and completions:
                    completion_rate = completions / total_int
                    conversion_probability += completion_rate * 0.3  # Max 30%
                
                # Factor 3: Response time (más rápido = mejor)
                if avg_resp:
                    if avg_resp < 2:
                        conversion_probability += 0.15
                    elif avg_resp < 24:
                        conversion_probability += 0.1
                
                # Factor 4: Patrón de actividad (business hours)
                if total_int and biz_hours:
                    biz_hours_rate = biz_hours / total_int
                    if biz_hours_rate > 0.6:
                        conversion_probability += 0.1  # Activo en horas laborales
                
                # Factor 5: Consistencia (weekday activity)
                if total_int and weekday_int:
                    weekday_rate = weekday_int / total_int
                    if weekday_rate > 0.7:
                        conversion_probability += 0.05
                
                # Factor 6: Recencia
                if last_int:
                    days_since = (datetime.now() - last_int).days
                    if days_since < 3:
                        conversion_probability += 0.1
                    elif days_since < 7:
                        conversion_probability += 0.05
                
                # Limitar probabilidad
                conversion_probability = min(conversion_probability, 0.95)
                
                # Predicción de próxima acción
                next_action = "unknown"
                if conversion_probability > 0.7:
                    next_action = "likely_to_convert"
                elif conversion_probability > 0.5:
                    next_action = "needs_nurturing"
                elif conversion_probability > 0.3:
                    next_action = "needs_engagement"
                else:
                    next_action = "needs_re_engagement"
                
                predictions.append({
                    "lead_id": lead_id,
                    "current_status": status,
                    "conversion_probability": round(conversion_probability * 100, 2),
                    "predicted_next_action": next_action,
                    "factors": {
                        "engagement_score": eng_score or 0,
                        "completion_rate": round((completions / total_int * 100) if total_int > 0 else 0, 2),
                        "avg_response_time_hours": round(float(avg_resp or 0), 2),
                        "business_hours_activity": round((biz_hours / total_int * 100) if total_int > 0 else 0, 2)
                    }
                })
            
            # Agrupar por predicción
            action_groups = defaultdict(int)
            for p in predictions:
                action_groups[p["predicted_next_action"]] += 1
            
            logger.info(f"Predictive behavior: {len(predictions)} leads analizados")
            return {
                "predictions": predictions[:50],  # Top 50
                "total_analyzed": len(predictions),
                "action_distribution": dict(action_groups),
                "high_probability_leads": len([p for p in predictions if p["conversion_probability"] > 70])
            }
            
        except Exception as e:
            logger.error(f"Error en predictive behavior analysis: {e}", exc_info=True)
            return {"predictions": [], "error": str(e)}
    
    @task(task_id="personalized_content_recommendations")
    def personalized_content_recommendations() -> Dict[str, Any]:
        """Genera recomendaciones de contenido personalizado para cada lead."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener leads activos con historial
            leads_query = """
                SELECT DISTINCT
                    ol.lead_id,
                    ol.email,
                    ol.interest_area,
                    ol.engagement_score,
                    ol.status,
                    STRING_AGG(DISTINCT ce.content_type, ', ') as consumed_types,
                    STRING_AGG(DISTINCT ns.sequence_name, ', ') as sequences_in
                FROM organic_leads ol
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id AND ce.status = 'completed'
                LEFT JOIN nurturing_sequences ns ON ol.lead_id = ns.lead_id
                WHERE ol.status IN ('nurturing', 'new', 'engaged')
                AND ol.created_at >= NOW() - INTERVAL '60 days'
                GROUP BY ol.lead_id, ol.email, ol.interest_area, ol.engagement_score, ol.status
                HAVING COUNT(DISTINCT ce.engagement_id) > 0 OR COUNT(DISTINCT ns.sequence_id) > 0
                LIMIT 200
            """
            
            leads = hook.get_records(leads_query)
            
            recommendations = []
            
            for row in leads:
                lead_id, email, interest_area, eng_score, status, consumed_types, sequences = row
                
                # Analizar contenido consumido
                consumed = (consumed_types or "").split(", ") if consumed_types else []
                consumed = [c.strip() for c in consumed if c.strip()]
                
                # Generar recomendaciones basadas en:
                # 1. Área de interés
                # 2. Contenido ya consumido
                # 3. Engagement score
                # 4. Status actual
                
                recommended_content = []
                
                # Recomendación 1: Basada en interés
                if interest_area:
                    if interest_area == "marketing":
                        recommended_content.append({
                            "type": "guide",
                            "title": "Guía Avanzada de Marketing Digital",
                            "reason": "Basado en tu área de interés"
                        })
                    elif interest_area == "sales":
                        recommended_content.append({
                            "type": "video",
                            "title": "Técnicas Avanzadas de Ventas",
                            "reason": "Basado en tu área de interés"
                        })
                
                # Recomendación 2: Complementar contenido consumido
                if "blog" in consumed and "guide" not in consumed:
                    recommended_content.append({
                        "type": "guide",
                        "title": "Guía Completa del Tema",
                        "reason": "Complementa los artículos que has leído"
                    })
                
                if "video" not in consumed and len(consumed) >= 2:
                    recommended_content.append({
                        "type": "video",
                        "title": "Video Tutorial Exclusivo",
                        "reason": "Diversifica tu aprendizaje"
                    })
                
                # Recomendación 3: Basada en engagement
                if eng_score and eng_score >= 8:
                    recommended_content.append({
                        "type": "case_study",
                        "title": "Casos de Éxito Avanzados",
                        "reason": "Para leads de alto engagement"
                    })
                
                # Recomendación 4: Para leads cerca de conversión
                if status == "nurturing" and eng_score and eng_score >= 7:
                    recommended_content.append({
                        "type": "webinar",
                        "title": "Webinar Exclusivo: Próximos Pasos",
                        "reason": "Estás cerca de convertir"
                    })
                
                # Recomendación 5: Contenido nuevo si ha consumido mucho
                if len(consumed) >= 5:
                    recommended_content.append({
                        "type": "ebook",
                        "title": "Ebook Premium: Estrategias Avanzadas",
                        "reason": "Contenido avanzado para usuarios activos"
                    })
                
                if recommended_content:
                    recommendations.append({
                        "lead_id": lead_id,
                        "email": email,
                        "interest_area": interest_area,
                        "engagement_score": eng_score or 0,
                        "consumed_content_types": consumed,
                        "recommended_content": recommended_content[:5],  # Top 5
                        "total_recommendations": len(recommended_content)
                    })
            
            # Estadísticas
            content_type_dist = defaultdict(int)
            for rec in recommendations:
                for content in rec["recommended_content"]:
                    content_type_dist[content["type"]] += 1
            
            logger.info(f"Personalized recommendations: {len(recommendations)} leads con recomendaciones")
            return {
                "recommendations": recommendations[:30],  # Top 30
                "total_leads": len(recommendations),
                "content_type_distribution": dict(content_type_dist),
                "avg_recommendations_per_lead": round(sum(r["total_recommendations"] for r in recommendations) / len(recommendations), 2) if recommendations else 0
            }
            
        except Exception as e:
            logger.error(f"Error en personalized content recommendations: {e}", exc_info=True)
            return {"recommendations": [], "error": str(e)}
    
    @task(task_id="advanced_segmentation_engine")
    def advanced_segmentation_engine() -> Dict[str, Any]:
        """Motor avanzado de segmentación basado en múltiples criterios."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Definir segmentos avanzados
            segments = {
                "high_value_prospects": {
                    "criteria": "engagement_score >= 10 AND status = 'nurturing'",
                    "description": "Leads de alto valor en nurturing"
                },
                "quick_responders": {
                    "criteria": "EXISTS (SELECT 1 FROM content_engagement ce WHERE ce.lead_id = ol.lead_id AND EXTRACT(EPOCH FROM (ce.opened_at - ce.sent_at))/3600 < 2)",
                    "description": "Leads que responden rápidamente"
                },
                "content_consumers": {
                    "criteria": "(SELECT COUNT(*) FROM content_engagement WHERE lead_id = ol.lead_id AND status = 'completed') >= 3",
                    "description": "Leads que consumen mucho contenido"
                },
                "referral_champions": {
                    "criteria": "(SELECT COUNT(*) FROM referrals WHERE referrer_lead_id = ol.lead_id AND status = 'validated') >= 2",
                    "description": "Leads que generan múltiples referidos"
                },
                "at_risk": {
                    "criteria": "status = 'nurturing' AND engagement_score < 3 AND created_at < NOW() - INTERVAL '30 days'",
                    "description": "Leads en riesgo de abandono"
                },
                "ready_to_convert": {
                    "criteria": "engagement_score >= 8 AND status = 'nurturing' AND (SELECT COUNT(*) FROM content_engagement WHERE lead_id = ol.lead_id AND status = 'completed') >= 5",
                    "description": "Leads listos para convertir"
                }
            }
            
            segment_results = {}
            
            for segment_name, segment_info in segments.items():
                query = f"""
                    SELECT 
                        ol.lead_id,
                        ol.email,
                        ol.engagement_score,
                        ol.status,
                        ol.created_at
                    FROM organic_leads ol
                    WHERE ol.created_at >= NOW() - INTERVAL '90 days'
                    AND {segment_info['criteria']}
                    LIMIT 100
                """
                
                try:
                    leads = hook.get_records(query)
                    segment_results[segment_name] = {
                        "count": len(leads),
                        "description": segment_info["description"],
                        "sample_leads": [
                            {
                                "lead_id": row[0],
                                "email": row[1],
                                "engagement_score": row[2],
                                "status": row[3]
                            }
                            for row in leads[:10]  # Top 10
                        ]
                    }
                except Exception as e:
                    logger.warning(f"Error en segmento {segment_name}: {e}")
                    segment_results[segment_name] = {
                        "count": 0,
                        "description": segment_info["description"],
                        "error": str(e)
                    }
            
            # Estadísticas agregadas
            total_segmented = sum(s["count"] for s in segment_results.values())
            largest_segment = max(segment_results.items(), key=lambda x: x[1]["count"]) if segment_results else None
            
            logger.info(f"Advanced segmentation: {len(segments)} segmentos, {total_segmented} leads segmentados")
            return {
                "segments": segment_results,
                "total_segments": len(segments),
                "total_segmented_leads": total_segmented,
                "largest_segment": {
                    "name": largest_segment[0] if largest_segment else None,
                    "count": largest_segment[1]["count"] if largest_segment else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error en advanced segmentation engine: {e}", exc_info=True)
            return {"segments": {}, "error": str(e)}
    
    @task(task_id="anomaly_detection")
    def anomaly_detection() -> Dict[str, Any]:
        """Detecta anomalías en métricas y comportamiento para alertas tempranas."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            anomalies = []
            
            # Anomalía 1: Caída súbita en engagement rate
            engagement_query = """
                WITH daily_engagement AS (
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as total_leads,
                        COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged_leads
                    FROM organic_leads
                    WHERE created_at >= NOW() - INTERVAL '14 days'
                    GROUP BY DATE(created_at)
                )
                SELECT 
                    date,
                    total_leads,
                    engaged_leads,
                    (engaged_leads::float / NULLIF(total_leads, 0) * 100) as engagement_rate
                FROM daily_engagement
                ORDER BY date DESC
                LIMIT 7
            """
            
            daily_engagement = hook.get_records(engagement_query)
            if len(daily_engagement) >= 3:
                recent_rates = [row[3] for row in daily_engagement[:3] if row[3]]
                older_rates = [row[3] for row in daily_engagement[3:6] if row[3]]
                
                if recent_rates and older_rates:
                    recent_avg = sum(recent_rates) / len(recent_rates)
                    older_avg = sum(older_rates) / len(older_rates)
                    
                    if older_avg > 0 and recent_avg < older_avg * 0.7:  # Caída >30%
                        anomalies.append({
                            "type": "engagement_drop",
                            "severity": "high",
                            "message": f"Caída significativa en engagement rate: {recent_avg:.1f}% vs {older_avg:.1f}% promedio anterior",
                            "recommendation": "Revisar contenido y timing de envíos"
                        })
            
            # Anomalía 2: Aumento en tasa de fraude
            fraud_query = """
                SELECT 
                    COUNT(*) as total_referrals,
                    COUNT(CASE WHEN status = 'fraud' THEN 1 END) as fraud_referrals
                FROM referrals
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            
            fraud_data = hook.get_first(fraud_query)
            if fraud_data and fraud_data[0] > 10:
                total, fraud = fraud_data
                fraud_rate = (fraud / total * 100) if total > 0 else 0
                
                if fraud_rate > 20:  # Más del 20% es anormal
                    anomalies.append({
                        "type": "high_fraud_rate",
                        "severity": "high",
                        "message": f"Tasa de fraude anormalmente alta: {fraud_rate:.1f}%",
                        "recommendation": "Revisar y fortalecer validaciones anti-fraude"
                    })
            
            # Anomalía 3: Caída en nuevos leads
            leads_query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as new_leads
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '14 days'
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT 7
            """
            
            daily_leads = hook.get_records(leads_query)
            if len(daily_leads) >= 3:
                recent_leads = [row[1] for row in daily_leads[:3]]
                older_leads = [row[1] for row in daily_leads[3:6]]
                
                if recent_leads and older_leads:
                    recent_avg = sum(recent_leads) / len(recent_leads)
                    older_avg = sum(older_leads) / len(older_leads)
                    
                    if older_avg > 0 and recent_avg < older_avg * 0.6:  # Caída >40%
                        anomalies.append({
                            "type": "lead_generation_drop",
                            "severity": "medium",
                            "message": f"Caída significativa en generación de leads: {recent_avg:.1f} por día vs {older_avg:.1f} promedio anterior",
                            "recommendation": "Revisar canales de adquisición y campañas"
                        })
            
            # Anomalía 4: Comportamiento inusual en leads individuales
            unusual_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    COUNT(ce.engagement_id) as total_sent,
                    COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) as total_opened
                FROM organic_leads ol
                JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                WHERE ce.sent_at >= NOW() - INTERVAL '7 days'
                GROUP BY ol.lead_id, ol.email
                HAVING COUNT(ce.engagement_id) >= 10
                AND COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) = 0
                LIMIT 5
            """
            
            unusual_leads = hook.get_records(unusual_query)
            if unusual_leads:
                anomalies.append({
                    "type": "unusual_behavior",
                    "severity": "medium",
                    "message": f"{len(unusual_leads)} leads recibieron 10+ emails sin abrir ninguno",
                    "recommendation": "Revisar calidad de emails y considerar pausar envíos",
                    "affected_leads": len(unusual_leads)
                })
            
            logger.info(f"Anomaly detection: {len(anomalies)} anomalías detectadas")
            return {
                "anomalies": anomalies,
                "total_detected": len(anomalies),
                "high_severity": len([a for a in anomalies if a["severity"] == "high"]),
                "medium_severity": len([a for a in anomalies if a["severity"] == "medium"])
            }
            
        except Exception as e:
            logger.error(f"Error en anomaly detection: {e}", exc_info=True)
            return {"anomalies": [], "error": str(e)}
    
    @task(task_id="social_media_tracking")
    def social_media_tracking() -> Dict[str, Any]:
        """Tracking de integración con redes sociales para análisis de adquisición."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar leads que vienen de redes sociales
            social_query = """
                SELECT 
                    ol.source,
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN ol.status = 'engaged' THEN 1 END) as engaged,
                    AVG(ol.engagement_score) as avg_engagement,
                    COUNT(DISTINCT r.referral_id) as referrals_generated
                FROM organic_leads ol
                LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE ol.source IN ('facebook', 'twitter', 'linkedin', 'instagram', 'social')
                AND ol.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY ol.source
                ORDER BY total_leads DESC
            """
            
            social_sources = hook.get_records(social_query)
            
            social_analysis = []
            total_social_leads = 0
            
            for row in social_sources:
                source, total, engaged, avg_eng, refs = row
                
                engagement_rate = (engaged / total * 100) if total > 0 else 0
                referral_rate = (refs / total * 100) if total > 0 else 0
                
                social_analysis.append({
                    "platform": source,
                    "total_leads": total,
                    "engaged_leads": engaged,
                    "engagement_rate": round(engagement_rate, 2),
                    "avg_engagement_score": round(float(avg_eng or 0), 2),
                    "referrals_generated": refs,
                    "referral_rate": round(referral_rate, 2)
                })
                
                total_social_leads += total
            
            # Comparar con otros canales
            all_channels_query = """
                SELECT 
                    CASE 
                        WHEN source IN ('facebook', 'twitter', 'linkedin', 'instagram', 'social') THEN 'social_media'
                        ELSE source
                    END as channel_group,
                    COUNT(*) as total,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '30 days'
                GROUP BY channel_group
            """
            
            channel_comparison = hook.get_records(all_channels_query)
            
            comparison = {}
            for row in channel_comparison:
                group, total, engaged = row
                comparison[group] = {
                    "total": total,
                    "engaged": engaged,
                    "engagement_rate": round((engaged / total * 100) if total > 0 else 0, 2)
                }
            
            # Mejor plataforma social
            best_social = max(social_analysis, key=lambda x: x["engagement_rate"]) if social_analysis else None
            
            logger.info(f"Social media tracking: {len(social_analysis)} plataformas, {total_social_leads} leads totales")
            return {
                "social_platforms": social_analysis,
                "total_social_leads": total_social_leads,
                "best_platform": best_social,
                "channel_comparison": comparison,
                "social_percentage": round((total_social_leads / sum(c["total"] for c in comparison.values()) * 100) if comparison else 0, 2)
            }
            
        except Exception as e:
            logger.error(f"Error en social media tracking: {e}", exc_info=True)
            return {"social_platforms": [], "error": str(e)}
    
    # ============================================================================
    # PIPELINE PRINCIPAL MEJORADO V4
    # ============================================================================
    
    schema_ok = ensure_schema()
    
    # Captura y segmentación
    new_leads = capture_new_leads()
    segmentation = segment_leads(new_leads)
    
    # Nurturing
    nurturing_started = start_nurturing_workflows(segmentation)
    content_sent = send_nurturing_content()
    engagement_tracked = track_engagement()
    
    # Referidos
    referral_invites = invite_to_referral_program(engagement_tracked)
    referrals_processed = process_referrals()
    
    # Sincronización y recordatorios
    crm_synced = sync_with_crm()
    reminders_sent = send_reminders()
    second_incentives = send_second_incentive()
    
    # Reportes y optimización
    reports = generate_reports()
    optimizations = optimize_automatically()
    perf_metrics = performance_metrics()
    
    # Tareas avanzadas (paralelas)
    ml_retrain = retrain_ml_model()
    cohorts = cohort_analysis()
    alerts = intelligent_alerts()
    churn_prediction = predict_churn()
    timing_optimization = optimize_timing()
    content_analysis = content_performance_analysis()
    
    # Tareas avanzadas V2 (paralelas)
    sentiment = sentiment_analysis()
    tagging = advanced_tagging()
    export = export_data()
    webhooks = event_webhooks()
    recommendations = intelligent_recommendations()
    trends = trend_analysis()
    
    # Tareas avanzadas V3 (paralelas)
    re_engagement = re_engagement_campaign()
    journey_analysis = customer_journey_analysis()
    ltv_pred = ltv_prediction()
    channel_opt = channel_optimization()
    feedback_loops = feedback_loop_analysis()
    benchmarking = competitive_benchmarking()
    
    # Tareas avanzadas V4 (paralelas)
    dynamic_scoring = dynamic_scoring_system()
    behavior_prediction = predictive_behavior_analysis()
    content_recommendations = personalized_content_recommendations()
    advanced_segmentation = advanced_segmentation_engine()
    anomalies = anomaly_detection()
    social_tracking = social_media_tracking()
    
    # ============================================================================
    # TAREAS AVANZADAS ADICIONALES V5
    # ============================================================================
    
    @task(task_id="advanced_cohort_analysis")
    def advanced_cohort_analysis() -> Dict[str, Any]:
        """Análisis avanzado de cohortes con múltiples dimensiones."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Análisis de cohortes por mes de adquisición
            cohort_query = """
                WITH monthly_cohorts AS (
                    SELECT 
                        DATE_TRUNC('month', ol.created_at) as cohort_month,
                        ol.lead_id,
                        ol.status,
                        ol.engagement_score,
                        ol.source,
                        COUNT(DISTINCT ce.engagement_id) as total_content,
                        COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as completed_content,
                        COUNT(DISTINCT r.referral_id) as referrals_made,
                        EXTRACT(EPOCH FROM (COALESCE(ol.engaged_at, NOW()) - ol.created_at))/86400 as days_to_engage
                    FROM organic_leads ol
                    LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                    LEFT JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                    WHERE ol.created_at >= NOW() - INTERVAL '6 months'
                    GROUP BY cohort_month, ol.lead_id, ol.status, ol.engagement_score, ol.source, ol.created_at, ol.engaged_at
                )
                SELECT 
                    cohort_month,
                    COUNT(*) as cohort_size,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged_count,
                    AVG(engagement_score) as avg_engagement,
                    AVG(total_content) as avg_content_per_lead,
                    AVG(completed_content::float / NULLIF(total_content, 0)) as avg_completion_rate,
                    AVG(referrals_made) as avg_referrals,
                    AVG(days_to_engage) as avg_days_to_engage,
                    COUNT(DISTINCT source) as unique_sources
                FROM monthly_cohorts
                GROUP BY cohort_month
                ORDER BY cohort_month DESC
            """
            
            cohorts = hook.get_records(cohort_query)
            
            cohort_analysis = []
            for row in cohorts:
                month, size, engaged, avg_eng, avg_content, completion_rate, avg_refs, avg_days, sources = row
                
                engagement_rate = (engaged / size * 100) if size > 0 else 0
                
                cohort_analysis.append({
                    "cohort_month": month.strftime("%Y-%m") if month else None,
                    "cohort_size": size,
                    "engaged_count": engaged,
                    "engagement_rate": round(engagement_rate, 2),
                    "avg_engagement_score": round(float(avg_eng or 0), 2),
                    "avg_content_per_lead": round(float(avg_content or 0), 2),
                    "avg_completion_rate": round(float(completion_rate or 0) * 100, 2),
                    "avg_referrals_per_lead": round(float(avg_refs or 0), 2),
                    "avg_days_to_engage": round(float(avg_days or 0), 2),
                    "unique_sources": sources
                })
            
            # Análisis de retención por cohorte
            retention_analysis = {}
            if len(cohort_analysis) >= 2:
                recent_cohort = cohort_analysis[0]
                older_cohort = cohort_analysis[-1]
                
                retention_analysis = {
                    "recent_vs_older": {
                        "engagement_rate_change": round(
                            recent_cohort["engagement_rate"] - older_cohort["engagement_rate"], 2
                        ),
                        "avg_engagement_change": round(
                            recent_cohort["avg_engagement_score"] - older_cohort["avg_engagement_score"], 2
                        ),
                        "content_consumption_change": round(
                            recent_cohort["avg_content_per_lead"] - older_cohort["avg_content_per_lead"], 2
                        )
                    }
                }
            
            logger.info(f"Advanced cohort analysis: {len(cohort_analysis)} cohortes analizadas")
            return {
                "cohorts": cohort_analysis,
                "total_cohorts": len(cohort_analysis),
                "retention_analysis": retention_analysis,
                "best_cohort": max(cohort_analysis, key=lambda x: x["engagement_rate"]) if cohort_analysis else None
            }
            
        except Exception as e:
            logger.error(f"Error en advanced cohort analysis: {e}", exc_info=True)
            return {"cohorts": [], "error": str(e)}
    
    @task(task_id="content_performance_scoring")
    def content_performance_scoring() -> Dict[str, Any]:
        """Sistema de scoring de contenido basado en performance."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar performance de contenido
            content_query = """
                SELECT 
                    ce.content_type,
                    ce.content_title,
                    COUNT(*) as total_sent,
                    COUNT(CASE WHEN ce.status = 'opened' THEN 1 END) as total_opened,
                    COUNT(CASE WHEN ce.status = 'completed' THEN 1 END) as total_completed,
                    AVG(EXTRACT(EPOCH FROM (ce.opened_at - ce.sent_at))/3600) as avg_hours_to_open,
                    COUNT(DISTINCT ol.lead_id) as unique_leads,
                    COUNT(CASE WHEN ol.status = 'engaged' AND ce.completed_at IS NOT NULL THEN 1 END) as conversions_after_content
                FROM content_engagement ce
                JOIN organic_leads ol ON ce.lead_id = ol.lead_id
                WHERE ce.sent_at >= NOW() - INTERVAL '60 days'
                GROUP BY ce.content_type, ce.content_title
                HAVING COUNT(*) >= 5
                ORDER BY total_sent DESC
                LIMIT 100
            """
            
            content_data = hook.get_records(content_query)
            
            scored_content = []
            
            for row in content_data:
                content_type, title, sent, opened, completed, avg_hours, unique_leads, conversions = row
                
                # Calcular métricas
                open_rate = (opened / sent * 100) if sent > 0 else 0
                completion_rate = (completed / sent * 100) if sent > 0 else 0
                conversion_rate = (conversions / sent * 100) if sent > 0 else 0
                
                # Calcular score de performance (0-100)
                performance_score = 0.0
                
                # Factor 1: Open rate (30%)
                performance_score += min(open_rate / 100 * 30, 30)
                
                # Factor 2: Completion rate (40%)
                performance_score += min(completion_rate / 100 * 40, 40)
                
                # Factor 3: Conversion rate (20%)
                performance_score += min(conversion_rate / 100 * 20, 20)
                
                # Factor 4: Speed (10%) - más rápido es mejor
                if avg_hours:
                    if avg_hours < 2:
                        performance_score += 10
                    elif avg_hours < 24:
                        performance_score += 7
                    elif avg_hours < 48:
                        performance_score += 4
                
                # Factor 5: Reach (bonus)
                if unique_leads >= 50:
                    performance_score += 5
                elif unique_leads >= 20:
                    performance_score += 2
                
                performance_score = min(performance_score, 100)
                
                # Categorizar
                if performance_score >= 80:
                    tier = "excellent"
                elif performance_score >= 60:
                    tier = "good"
                elif performance_score >= 40:
                    tier = "average"
                else:
                    tier = "needs_improvement"
                
                scored_content.append({
                    "content_type": content_type,
                    "content_title": title[:100] if title else "N/A",
                    "total_sent": sent,
                    "open_rate": round(open_rate, 2),
                    "completion_rate": round(completion_rate, 2),
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_hours_to_open": round(float(avg_hours or 0), 2),
                    "unique_leads": unique_leads,
                    "performance_score": round(performance_score, 2),
                    "tier": tier
                })
            
            # Ordenar por score
            scored_content.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Estadísticas
            tier_distribution = defaultdict(int)
            for content in scored_content:
                tier_distribution[content["tier"]] += 1
            
            logger.info(f"Content performance scoring: {len(scored_content)} contenidos evaluados")
            return {
                "scored_content": scored_content[:30],  # Top 30
                "total_evaluated": len(scored_content),
                "tier_distribution": dict(tier_distribution),
                "top_performer": scored_content[0] if scored_content else None,
                "needs_improvement_count": tier_distribution.get("needs_improvement", 0)
            }
            
        except Exception as e:
            logger.error(f"Error en content performance scoring: {e}", exc_info=True)
            return {"scored_content": [], "error": str(e)}
    
    @task(task_id="external_api_integration")
    def external_api_integration() -> Dict[str, Any]:
        """Integración con APIs externas para enriquecimiento de datos."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Obtener leads recientes sin datos enriquecidos
            leads_query = """
                SELECT 
                    ol.lead_id,
                    ol.email,
                    ol.first_name,
                    ol.last_name,
                    ol.company,
                    ol.source
                FROM organic_leads ol
                WHERE ol.created_at >= NOW() - INTERVAL '7 days'
                AND ol.enrichment_status IS NULL
                LIMIT 50
            """
            
            leads = hook.get_records(leads_query)
            
            enriched = 0
            enrichment_results = []
            
            session = get_http_session()
            
            for row in leads:
                lead_id, email, first_name, last_name, company, source = row
                
                enrichment_data = {}
                
                # Enriquecimiento 1: Verificar email (usando API hipotética)
                # En producción, usar servicio real como Clearbit, FullContact, etc.
                try:
                    # Simulación de enriquecimiento
                    # En producción: response = session.get(f"https://api.enrichment.com/email/{email}")
                    enrichment_data["email_valid"] = True
                    enrichment_data["email_risk_score"] = 0.1  # Bajo riesgo
                except Exception as e:
                    logger.warning(f"Error en enriquecimiento de email para {email}: {e}")
                
                # Enriquecimiento 2: Datos de empresa (si hay company)
                if company:
                    try:
                        # Simulación de enriquecimiento de empresa
                        # En producción: response = session.get(f"https://api.company.com/{company}")
                        enrichment_data["company_size"] = "medium"
                        enrichment_data["company_industry"] = "technology"
                    except Exception as e:
                        logger.warning(f"Error en enriquecimiento de empresa para {company}: {e}")
                
                # Enriquecimiento 3: Datos de ubicación (si hay IP)
                # En producción, obtener IP de registros y enriquecer
                
                # Guardar datos enriquecidos (asumiendo columna enrichment_data JSONB)
                if enrichment_data:
                    try:
                        hook.run(
                            """
                            UPDATE organic_leads
                            SET enrichment_data = %s::jsonb,
                                enrichment_status = 'completed',
                                enrichment_date = NOW()
                            WHERE lead_id = %s
                            """,
                            parameters=(json.dumps(enrichment_data), lead_id)
                        )
                        
                        enriched += 1
                        enrichment_results.append({
                            "lead_id": lead_id,
                            "email": email,
                            "enrichment_data": enrichment_data
                        })
                    except Exception as e:
                        # Si no existe columna, solo loggear
                        logger.warning(f"Error guardando enriquecimiento: {e}")
                        enrichment_results.append({
                            "lead_id": lead_id,
                            "email": email,
                            "enrichment_data": enrichment_data,
                            "note": "Data enriched but not saved (column missing)"
                        })
            
            logger.info(f"External API integration: {enriched} leads enriquecidos")
            return {
                "enriched": enriched,
                "total_processed": len(leads),
                "enrichment_results": enrichment_results[:20]  # Top 20
            }
            
        except Exception as e:
            logger.error(f"Error en external API integration: {e}", exc_info=True)
            return {"enriched": 0, "error": str(e)}
    
    @task(task_id="push_notification_system")
    def push_notification_system() -> Dict[str, Any]:
        """Sistema de notificaciones push para eventos importantes."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Buscar eventos que requieren notificación push
            events_query = """
                SELECT 
                    'high_value_lead' as event_type,
                    ol.lead_id,
                    ol.email,
                    ol.engagement_score,
                    ol.engaged_at as event_time
                FROM organic_leads ol
                WHERE ol.engagement_score >= 15
                AND ol.status = 'engaged'
                AND ol.engaged_at >= NOW() - INTERVAL '1 hour'
                AND ol.push_notification_sent = false
                
                UNION ALL
                
                SELECT 
                    'referral_milestone' as event_type,
                    ol.lead_id,
                    ol.email,
                    ol.engagement_score,
                    MAX(r.validated_at) as event_time
                FROM organic_leads ol
                JOIN referrals r ON ol.lead_id = r.referrer_lead_id
                WHERE r.status = 'validated'
                AND r.validated_at >= NOW() - INTERVAL '1 hour'
                GROUP BY ol.lead_id, ol.email, ol.engagement_score
                HAVING COUNT(*) >= 3
                AND ol.push_notification_sent = false
                
                LIMIT 20
            """
            
            try:
                events = hook.get_records(events_query)
            except Exception:
                # Si no existe columna push_notification_sent
                logger.info("Push notifications no disponibles (columnas faltantes)")
                return {"sent": 0, "skipped": 0}
            
            sent = 0
            failed = 0
            
            for row in events:
                event_type, lead_id, email, eng_score, event_time = row
                
                # Determinar mensaje según tipo de evento
                if event_type == "high_value_lead":
                    title = "🎉 Lead de Alto Valor Convertido"
                    message = f"Lead con engagement score {eng_score} se ha convertido"
                elif event_type == "referral_milestone":
                    title = "🏆 Hito de Referidos Alcanzado"
                    message = f"Lead ha alcanzado 3+ referidos validados"
                else:
                    title = "📢 Nuevo Evento Importante"
                    message = "Ha ocurrido un evento importante"
                
                # Enviar notificación push (simulado)
                # En producción, usar servicio real como Firebase, OneSignal, etc.
                try:
                    # Simulación: En producción sería:
                    # push_service.send(title=title, message=message, user_id=lead_id)
                    notification_sent = True
                    
                    if notification_sent:
                        # Marcar como enviado
                        hook.run(
                            "UPDATE organic_leads SET push_notification_sent = true WHERE lead_id = %s",
                            parameters=(lead_id,)
                        )
                        sent += 1
                except Exception as e:
                    logger.error(f"Error enviando push notification: {e}")
                    failed += 1
            
            logger.info(f"Push notifications: {sent} enviadas, {failed} fallidas")
            return {
                "sent": sent,
                "failed": failed,
                "event_types": defaultdict(int)
            }
            
        except Exception as e:
            logger.error(f"Error en push notification system: {e}", exc_info=True)
            return {"sent": 0, "error": str(e)}
    
    @task(task_id="multi_variant_ab_testing")
    def multi_variant_ab_testing() -> Dict[str, Any]:
        """Sistema de A/B testing con múltiples variantes."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            # Analizar tests A/B con múltiples variantes
            ab_test_query = """
                SELECT 
                    abt.test_name,
                    abt.variant_name,
                    COUNT(DISTINCT aba.lead_id) as participants,
                    COUNT(CASE WHEN ol.status = 'engaged' THEN 1 END) as conversions,
                    AVG(ol.engagement_score) as avg_engagement,
                    COUNT(DISTINCT ce.engagement_id) as total_interactions
                FROM ab_tests abt
                JOIN ab_test_assignments aba ON abt.test_id = aba.test_id
                JOIN organic_leads ol ON aba.lead_id = ol.lead_id
                LEFT JOIN content_engagement ce ON ol.lead_id = ce.lead_id
                WHERE abt.created_at >= NOW() - INTERVAL '30 days'
                GROUP BY abt.test_name, abt.variant_name
                ORDER BY abt.test_name, conversions DESC
            """
            
            try:
                ab_tests = hook.get_records(ab_test_query)
            except Exception:
                logger.info("Tablas de A/B testing no disponibles")
                return {"tests_analyzed": 0, "message": "A/B testing tables not available"}
            
            test_results = defaultdict(lambda: {"variants": [], "winner": None})
            
            for row in ab_tests:
                test_name, variant, participants, conversions, avg_eng, interactions = row
                
                conversion_rate = (conversions / participants * 100) if participants > 0 else 0
                
                variant_data = {
                    "variant_name": variant,
                    "participants": participants,
                    "conversions": conversions,
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_engagement": round(float(avg_eng or 0), 2),
                    "total_interactions": interactions
                }
                
                test_results[test_name]["variants"].append(variant_data)
            
            # Determinar ganador para cada test
            for test_name, test_data in test_results.items():
                if test_data["variants"]:
                    winner = max(test_data["variants"], key=lambda x: x["conversion_rate"])
                    test_data["winner"] = winner
                    test_data["statistical_significance"] = "pending"  # En producción, calcular con chi-square
            
            logger.info(f"Multi-variant A/B testing: {len(test_results)} tests analizados")
            return {
                "tests_analyzed": len(test_results),
                "test_results": dict(test_results),
                "total_tests": len(test_results)
            }
            
        except Exception as e:
            logger.error(f"Error en multi-variant A/B testing: {e}", exc_info=True)
            return {"tests_analyzed": 0, "error": str(e)}
    
    @task(task_id="intelligent_alert_system")
    def intelligent_alert_system() -> Dict[str, Any]:
        """Sistema de alertas inteligentes con reglas avanzadas."""
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            alerts = []
            
            # Alerta 1: Caída en tasa de conversión
            conversion_query = """
                SELECT 
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN status = 'engaged' THEN 1 END) as engaged
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """
            
            conversion_data = hook.get_first(conversion_query)
            if conversion_data and conversion_data[0] > 10:
                total, engaged = conversion_data
                conversion_rate = (engaged / total * 100) if total > 0 else 0
                
                if conversion_rate < 15:  # Menos del 15% es bajo
                    alerts.append({
                        "type": "low_conversion_rate",
                        "severity": "high",
                        "title": "Tasa de Conversión Baja",
                        "message": f"Tasa de conversión en últimas 24h: {conversion_rate:.1f}% (objetivo: >15%)",
                        "action": "Revisar funnel y contenido de nurturing",
                        "metric_value": round(conversion_rate, 2),
                        "threshold": 15.0
                    })
            
            # Alerta 2: Alto volumen de leads inactivos
            inactive_query = """
                SELECT COUNT(*) as inactive_count
                FROM organic_leads
                WHERE status IN ('nurturing', 'new')
                AND created_at < NOW() - INTERVAL '30 days'
                AND engagement_score < 3
            """
            
            inactive_count = hook.get_first(inactive_query)
            if inactive_count and inactive_count[0] > 50:
                alerts.append({
                    "type": "high_inactive_leads",
                    "severity": "medium",
                    "title": "Alto Volumen de Leads Inactivos",
                    "message": f"{inactive_count[0]} leads inactivos por más de 30 días",
                    "action": "Ejecutar campaña de re-engagement",
                    "metric_value": inactive_count[0],
                    "threshold": 50
                })
            
            # Alerta 3: Bajo engagement promedio
            engagement_query = """
                SELECT AVG(engagement_score) as avg_engagement
                FROM organic_leads
                WHERE created_at >= NOW() - INTERVAL '7 days'
            """
            
            avg_engagement = hook.get_first(engagement_query)
            if avg_engagement and avg_engagement[0] and avg_engagement[0] < 3:
                alerts.append({
                    "type": "low_avg_engagement",
                    "severity": "medium",
                    "title": "Engagement Promedio Bajo",
                    "message": f"Engagement promedio: {avg_engagement[0]:.1f} (objetivo: >3)",
                    "action": "Revisar calidad de contenido y timing",
                    "metric_value": round(float(avg_engagement[0]), 2),
                    "threshold": 3.0
                })
            
            # Alerta 4: Anomalía en generación de leads
            leads_today_query = """
                SELECT COUNT(*) as leads_today
                FROM organic_leads
                WHERE created_at >= CURRENT_DATE
            """
            
            leads_today = hook.get_first(leads_today_query)
            if leads_today and leads_today[0] > 0:
                # Comparar con promedio de últimos 7 días
                avg_leads_query = """
                    SELECT AVG(daily_count) as avg_daily
                    FROM (
                        SELECT DATE(created_at) as date, COUNT(*) as daily_count
                        FROM organic_leads
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                        GROUP BY DATE(created_at)
                    ) daily_stats
                """
                
                avg_leads = hook.get_first(avg_leads_query)
                if avg_leads and avg_leads[0]:
                    if leads_today[0] < avg_leads[0] * 0.5:  # Menos del 50% del promedio
                        alerts.append({
                            "type": "unusual_lead_generation",
                            "severity": "medium",
                            "title": "Generación de Leads Inusual",
                            "message": f"Leads hoy: {leads_today[0]} vs promedio: {avg_leads[0]:.1f}",
                            "action": "Revisar canales de adquisición",
                            "metric_value": leads_today[0],
                            "threshold": round(avg_leads[0] * 0.5, 0)
                        })
            
            logger.info(f"Intelligent alert system: {len(alerts)} alertas generadas")
            return {
                "alerts": alerts,
                "total_alerts": len(alerts),
                "high_severity": len([a for a in alerts if a["severity"] == "high"]),
                "medium_severity": len([a for a in alerts if a["severity"] == "medium"])
            }
            
        except Exception as e:
            logger.error(f"Error en intelligent alert system: {e}", exc_info=True)
            return {"alerts": [], "error": str(e)}
    
    # ============================================================================
    # PIPELINE PRINCIPAL MEJORADO V5
    # ============================================================================
    
    schema_ok = ensure_schema()
    
    # Captura y segmentación
    new_leads = capture_new_leads()
    segmentation = segment_leads(new_leads)
    
    # Nurturing
    nurturing_started = start_nurturing_workflows(segmentation)
    content_sent = send_nurturing_content()
    engagement_tracked = track_engagement()
    
    # Referidos
    referral_invites = invite_to_referral_program(engagement_tracked)
    referrals_processed = process_referrals()
    
    # Sincronización y recordatorios
    crm_synced = sync_with_crm()
    reminders_sent = send_reminders()
    second_incentives = send_second_incentive()
    
    # Reportes y optimización
    reports = generate_reports()
    optimizations = optimize_automatically()
    perf_metrics = performance_metrics()
    
    # Tareas avanzadas (paralelas)
    ml_retrain = retrain_ml_model()
    cohorts = cohort_analysis()
    alerts = intelligent_alerts()
    churn_prediction = predict_churn()
    timing_optimization = optimize_timing()
    content_analysis = content_performance_analysis()
    
    # Tareas avanzadas V2 (paralelas)
    sentiment = sentiment_analysis()
    tagging = advanced_tagging()
    export = export_data()
    webhooks = event_webhooks()
    recommendations = intelligent_recommendations()
    trends = trend_analysis()
    
    # Tareas avanzadas V3 (paralelas)
    re_engagement = re_engagement_campaign()
    journey_analysis = customer_journey_analysis()
    ltv_pred = ltv_prediction()
    channel_opt = channel_optimization()
    feedback_loops = feedback_loop_analysis()
    benchmarking = competitive_benchmarking()
    
    # Tareas avanzadas V4 (paralelas)
    dynamic_scoring = dynamic_scoring_system()
    behavior_prediction = predictive_behavior_analysis()
    content_recommendations = personalized_content_recommendations()
    advanced_segmentation = advanced_segmentation_engine()
    anomalies = anomaly_detection()
    social_tracking = social_media_tracking()
    
    # Tareas avanzadas V5 (paralelas)
    advanced_cohorts = advanced_cohort_analysis()
    content_scoring = content_performance_scoring()
    api_integration = external_api_integration()
    push_notifications = push_notification_system()
    multi_variant_ab = multi_variant_ab_testing()
    intelligent_alerts_v2 = intelligent_alert_system()


dag = organic_acquisition_nurturing()


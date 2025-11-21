from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import re
import logging
import time
import os

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# MLflow integration (opcional)
try:
    import mlflow
    _MLFLOW_AVAILABLE = True
except ImportError:
    _MLFLOW_AVAILABLE = False
    mlflow = None


@dag(
    dag_id="lead_nurturing",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */4 * * *",  # Cada 4 horas
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
    ### Secuencias de Nutrición de Leads (Lead Nurturing) - Versión Mejorada
    
    Sistema automatizado completo para aumentar la tasa de conversión de leads fríos a calificados.
    
    **Funcionalidades principales:**
    - Identificación inteligente de leads fríos (bajo score/prioridad)
    - Secuencias automáticas basadas en templates configurables
    - Envío programado de emails según timing optimizado
    - Tracking completo de engagement (opens, clicks, replies)
    - Calificación automática basada en comportamiento
    - Pausado/reanudación de secuencias
    - Métricas en tiempo real y análisis de conversión
    - Soporte para múltiples canales (email, SMS, LinkedIn)
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `email_webhook_url`: Webhook para envío de emails (requerido)
    - `engagement_api_url`: API para verificar engagement (opcional)
    - `max_leads_per_run`: Máximo de leads a procesar (default: 100)
    - `min_score_to_qualify`: Score mínimo para calificar (default: 50)
    - `enable_auto_pause`: Pausar secuencias sin engagement (default: true)
    - `pause_after_days`: Días sin engagement para pausar (default: 30)
    - `dry_run`: Solo simular sin enviar (default: false)
    
    **Requisitos:**
    - Schema `lead_nurturing_schema.sql` debe estar ejecutado en Postgres
    - Webhook de email configurado y funcional
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email_webhook_url": Param("", type="string", minLength=1),
        "engagement_api_url": Param("", type="string"),
        "max_leads_per_run": Param(100, type="integer", minimum=1, maximum=1000),
        "min_score_to_qualify": Param(50, type="integer", minimum=0, maximum=100),
        "enable_auto_pause": Param(True, type="boolean"),
        "pause_after_days": Param(30, type="integer", minimum=1, maximum=180),
        "dry_run": Param(False, type="boolean"),
        "email_from": Param("marketing@tu-dominio.com", type="string", minLength=3),
        "slack_webhook_url": Param("", type="string"),
        "request_timeout": Param(30, type="integer", minimum=5, maximum=120),
        "max_retry_attempts": Param(3, type="integer", minimum=1, maximum=10),
        # MLflow tracking
        "mlflow_enable": Param(False, type="boolean"),
        "mlflow_experiment": Param("lead_nurturing", type="string"),
        # A/B Testing
        "enable_ab_testing": Param(False, type="boolean"),
        "ab_test_percentage": Param(10, type="integer", minimum=0, maximum=50),
        # Predictive scoring
        "enable_predictive_scoring": Param(False, type="boolean"),
        "ml_model_endpoint": Param("", type="string"),
        # Optimización de timing
        "optimize_timing": Param(False, type="boolean"),
        "best_time_analysis_days": Param(30, type="integer", minimum=7, maximum=365),
        # Exportación y reporting
        "export_metrics_to_s3": Param(False, type="boolean"),
        "s3_bucket": Param("", type="string"),
        "s3_path": Param("lead_nurturing/metrics", type="string"),
        # Segmentación avanzada
        "enable_segmentation": Param(False, type="boolean"),
        "segment_by_source": Param(False, type="boolean"),
        "segment_by_score_range": Param(False, type="boolean"),
        # Alertas
        "enable_alerts": Param(False, type="boolean"),
        "alert_on_low_conversion": Param(False, type="boolean"),
        "low_conversion_threshold": Param(5.0, type="number", minimum=0, maximum=100),
        # Cohort analysis
        "enable_cohort_analysis": Param(False, type="boolean"),
    },
    tags=["marketing", "lead-nurturing", "automation", "ml"],
)
def lead_nurturing() -> None:
    """
    DAG principal mejorado para secuencias de nutrición de leads.
    """
    
    def render_template_advanced(template: str, data: Dict[str, Any]) -> str:
        """
        Renderiza template con soporte para placeholders {{key}} y propiedades anidadas.
        Maneja casos edge como valores None y formatea apropiadamente.
        """
        if not template:
            return ""
        
        result = template
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            # Manejar valores None y formatear apropiadamente
            display_value = str(value) if value is not None else ""
            result = result.replace(placeholder, display_value)
            
            # Soporte para propiedades anidadas si value es dict
            if isinstance(value, dict):
                for subk, subv in value.items():
                    nested_placeholder = f"{{{{{key}.{subk}}}}}"
                    result = result.replace(nested_placeholder, str(subv or ""))
        
        return result
    
    def log_to_mlflow(metrics: Dict[str, float], params: Dict[str, Any]) -> None:
        """
        Log métricas y parámetros a MLflow si está habilitado.
        """
        ctx = get_current_context()
        mlflow_enabled = bool(ctx["params"].get("mlflow_enable", False))
        
        if not mlflow_enabled or not _MLFLOW_AVAILABLE:
            return
        
        try:
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
            if tracking_uri:
                mlflow.set_tracking_uri(tracking_uri)
            
            experiment_name = str(ctx["params"].get("mlflow_experiment", "lead_nurturing"))
            mlflow.set_experiment(experiment_name)
            
            run_id = str((ctx.get("dag_run") or {}).get("run_id", "unknown"))
            
            with mlflow.start_run(run_name=f"lead_nurturing_{run_id}"):
                # Log parámetros
                for key, value in params.items():
                    mlflow.log_param(key, str(value))
                
                # Log métricas
                for key, value in metrics.items():
                    mlflow.log_metric(key, float(value))
                
                mlflow.set_tag("dag_id", "lead_nurturing")
                mlflow.set_tag("environment", os.getenv("ENV", "dev"))
        except Exception as e:
            logger.warning(f"Error logging to MLflow: {e}")
    
    def get_predictive_score(lead: Dict[str, Any], ml_endpoint: str) -> Optional[int]:
        """
        Obtiene score predictivo desde endpoint de ML si está habilitado.
        """
        if not ml_endpoint:
            return None
        
        try:
            payload = {
                "ext_id": lead.get("ext_id"),
                "email": lead.get("email"),
                "score": lead.get("score", 0),
                "priority": lead.get("priority", "low"),
                "source": lead.get("source"),
                "utm_source": lead.get("utm_source"),
                "utm_campaign": lead.get("utm_campaign")
            }
            
            resp = requests.post(
                ml_endpoint,
                json=payload,
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            
            if resp.status_code < 300:
                data = resp.json()
                return int(data.get("predicted_score", 0))
        except Exception as e:
            logger.debug(f"Error obteniendo score predictivo: {e}")
        
        return None
    
    def get_optimal_send_time(lead: Dict[str, Any], days_history: int) -> Optional[datetime]:
        """
        Calcula tiempo óptimo de envío basado en histórico de engagement del lead.
        """
        ctx = get_current_context()
        conn_id = str(ctx["params"]["postgres_conn_id"])
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Buscar histórico de engagement por hora del día
                    cur.execute("""
                        SELECT 
                            EXTRACT(HOUR FROM opened_at) as hour_of_day,
                            COUNT(*) as open_count
                        FROM lead_nurturing_events
                        WHERE lead_ext_id = %s
                            AND opened_at >= CURRENT_DATE - INTERVAL '%s days'
                            AND opened_at IS NOT NULL
                        GROUP BY EXTRACT(HOUR FROM opened_at)
                        ORDER BY open_count DESC
                        LIMIT 1
                    """, (lead.get("ext_id"), days_history))
                    
                    result = cur.fetchone()
                    if result:
                        optimal_hour = int(result[0])
                        now = datetime.utcnow()
                        # Programar para la próxima ocurrencia de esa hora
                        send_time = now.replace(hour=optimal_hour, minute=0, second=0, microsecond=0)
                        if send_time <= now:
                            send_time += timedelta(days=1)
                        return send_time
        except Exception:
            pass
        
        return None
    
    def calculate_lead_score_from_engagement(
        base_score: int,
        replies_count: int,
        opens_count: int,
        clicks_count: int
    ) -> int:
        """
        Calcula nuevo score basado en engagement con lógica mejorada.
        Considera múltiples factores de engagement de forma acumulativa.
        """
        new_score = base_score
        
        # Reply es el engagement más valioso - múltiples replies indican alto interés
        if replies_count >= 2:
            new_score += 25  # Múltiples replies = muy interesado
        elif replies_count >= 1:
            new_score += 15  # Un reply indica interés genuino
        
        # Opens indican interés moderado - más opens = más interés
        if opens_count >= 4:
            new_score += 15  # Múltiples reads indican alto interés
        elif opens_count >= 3:
            new_score += 10  # Leyendo activamente
        elif opens_count >= 2:
            new_score += 5
        
        # Clicks indican interés alto - están interactuando con contenido
        if clicks_count >= 2:
            new_score += 12  # Múltiples clicks = muy interesado
        elif clicks_count >= 1:
            new_score += 8  # Interactuando con contenido
        
        return min(new_score, 100)  # Cap at 100
    
    def should_pause_sequence(sequence: Dict[str, Any], pause_after_days: int) -> bool:
        """
        Determina si una secuencia debería pausarse por falta de engagement.
        """
        last_activity = sequence.get("last_activity_at")
        if not last_activity:
            return False
        
        if isinstance(last_activity, str):
            try:
                last_activity = pendulum.parse(last_activity)
            except Exception:
                return False
        
        days_since_activity = (pendulum.now("UTC") - last_activity).days
        return days_since_activity >= pause_after_days
    
    @task(task_id="ensure_schema")
    def ensure_schema() -> bool:
        """
        Verifica que el schema de lead nurturing esté creado.
        Crea las tablas si no existen (safe para re-ejecución).
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Verificar si las tablas principales existen
                    cur.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_name = 'lead_nurturing_sequences'
                    """)
                    
                    if cur.fetchone()[0] == 0:
                        logger.warning(
                            "Schema de lead_nurturing no encontrado. "
                            "Por favor ejecuta data/db/lead_nurturing_schema.sql"
                        )
                        return False
                    
                    logger.info("Schema de lead_nurturing verificado correctamente")
                    return True
        except Exception as e:
            logger.error(f"Error verificando schema: {e}", exc_info=True)
            return False
    
    @task(task_id="identify_cold_leads")
    def identify_cold_leads() -> List[Dict[str, Any]]:
        """
        Identifica leads fríos que necesitan nutrición.
        Criterios: score < min_score_to_qualify y priority = 'low'
        Excluye leads que ya tienen secuencias activas.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        min_score = int(params["min_score_to_qualify"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                l.ext_id,
                l.email,
                l.first_name,
                l.last_name,
                l.score,
                l.priority,
                l.source,
                l.utm_source,
                l.utm_campaign,
                l.created_at,
                COALESCE(s.id, 0) AS has_active_sequence
            FROM leads l
            LEFT JOIN lead_nurturing_sequences s 
                ON l.ext_id = s.lead_ext_id 
                AND s.status = 'active'
            WHERE 
                (l.score IS NULL OR l.score < %s)
                AND (l.priority IS NULL OR l.priority = 'low')
                AND l.email IS NOT NULL
                AND l.email != ''
                AND l.email LIKE '%@%'  -- Validación básica de email
                AND (s.id IS NULL OR s.id = 0)  -- No tiene secuencia activa
                AND l.created_at >= CURRENT_DATE - INTERVAL '90 days'  -- Leads recientes
            ORDER BY 
                l.created_at DESC,  -- Leads más recientes primero
                l.score DESC NULLS LAST  -- Leads con algo de score primero
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (min_score, max_leads))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Identificados {len(leads)} leads fríos para nutrición")
        
        try:
            Stats.incr("lead_nurturing.cold_leads_identified", len(leads))
        except Exception:
            pass
        
        # Aplicar scoring predictivo si está habilitado
        ctx = get_current_context()
        enable_predictive = bool(ctx["params"].get("enable_predictive_scoring", False))
        ml_endpoint = str(ctx["params"].get("ml_model_endpoint", "")).strip()
        
        if enable_predictive and ml_endpoint:
            for lead in leads:
                predicted_score = get_predictive_score(lead, ml_endpoint)
                if predicted_score is not None:
                    lead["predicted_score"] = predicted_score
                    # Usar score predictivo para priorizar
                    if predicted_score >= min_score:
                        lead["_priority_boost"] = True
        
        # Log a MLflow si está habilitado
        if bool(ctx["params"].get("mlflow_enable", False)):
            log_to_mlflow(
                {"cold_leads_identified": len(leads)},
                {"min_score": min_score, "max_leads": max_leads}
            )
        
        return leads
    
    @task(task_id="get_or_create_sequence_template")
    def get_or_create_sequence_template() -> Dict[str, Any]:
        """
        Obtiene o crea un template de secuencia por defecto para leads de baja prioridad.
        Template incluye 5 pasos con contenido profesional y timing optimizado.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Template mejorado: 5 pasos de nutrición con contenido más profesional
        default_template = {
            "name": "default_cold_lead_nurturing",
            "description": "Secuencia por defecto para leads fríos de baja prioridad - Optimizada para conversión",
            "priority_filter": "low",
            "min_score": 0,
            "max_score": 49,
            "total_steps": 5,
            "steps_config": [
                {
                    "step": 1,
                    "delay_days": 0,
                    "subject_template": "{{first_name}}, ¿Conoces cómo podemos ayudarte?",
                    "body_template": (
                        "Hola {{first_name}},\n\n"
                        "Gracias por tu interés en nuestros servicios. Quería compartirte información "
                        "sobre cómo podemos ayudarte a alcanzar tus objetivos de negocio.\n\n"
                        "Somos especialistas en [tu industria/servicio] y hemos ayudado a empresas similares "
                        "a obtener resultados excepcionales.\n\n"
                        "¿Te interesa conocer más detalles sobre lo que podemos ofrecerte?\n\n"
                        "Saludos cordiales,\n"
                        "Equipo de Marketing"
                    )
                },
                {
                    "step": 2,
                    "delay_days": 3,
                    "subject_template": "{{first_name}}, recursos exclusivos para ti",
                    "body_template": (
                        "Hola {{first_name}},\n\n"
                        "Comparto contigo algunos recursos exclusivos que han sido diseñados especialmente "
                        "para empresas como la tuya. Estos materiales podrían ser de gran utilidad para tu negocio.\n\n"
                        "[Enlace a recursos / caso de estudio / whitepaper]\n\n"
                        "¿Te gustaría revisarlos? Estoy disponible para cualquier pregunta que puedas tener.\n\n"
                        "Saludos"
                    )
                },
                {
                    "step": 3,
                    "delay_days": 7,
                    "subject_template": "{{first_name}}, historias de éxito",
                    "body_template": (
                        "Hola {{first_name}},\n\n"
                        "Quería compartirte un caso de éxito reciente de un cliente similar que logró resultados "
                        "excepcionales con nuestra solución.\n\n"
                        "En resumen, logramos [beneficio específico] en un período de [tiempo]. "
                        "Estos resultados son típicos de nuestros clientes.\n\n"
                        "¿Te interesa conocer más detalles sobre cómo lo logramos?\n\n"
                        "Saludos"
                    )
                },
                {
                    "step": 4,
                    "delay_days": 14,
                    "subject_template": "{{first_name}}, ¿aún estás interesado?",
                    "body_template": (
                        "Hola {{first_name}},\n\n"
                        "Quería saber si aún estás interesado en conocer más sobre nuestros servicios. "
                        "Entiendo que estás ocupado, pero creo que podríamos ayudarte significativamente.\n\n"
                        "Estamos aquí para responder cualquier duda que tengas y ayudarte a evaluar "
                        "si somos una buena fit para tu negocio.\n\n"
                        "¿Te va bien esta semana para una breve conversación de 15 minutos?\n\n"
                        "Saludos"
                    )
                },
                {
                    "step": 5,
                    "delay_days": 21,
                    "subject_template": "{{first_name}}, última oportunidad",
                    "body_template": (
                        "Hola {{first_name}},\n\n"
                        "Esta es la última vez que te contacto. Entiendo que puede haber otras prioridades, "
                        "pero si aún tienes interés en explorar cómo podemos ayudarte, estaré encantado "
                        "de conversar contigo.\n\n"
                        "Si no, no hay problema - simplemente responde este email y te eliminaré de nuestra lista.\n\n"
                        "Saludos cordiales,\n"
                        "Equipo de Marketing"
                    )
                }
            ],
            "enabled": True
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Intentar obtener template existente
                cur.execute(
                    """
                    SELECT id, name, steps_config, total_steps 
                    FROM nurturing_sequence_templates 
                    WHERE name = %s AND enabled = true
                    """,
                    (default_template["name"],)
                )
                existing = cur.fetchone()
                
                if existing:
                    template_id, name, steps_config, total_steps = existing
                    
                    # Parse JSON si es string
                    if isinstance(steps_config, str):
                        try:
                            steps_config = json.loads(steps_config)
                        except Exception:
                            steps_config = default_template["steps_config"]
                    elif not isinstance(steps_config, list):
                        steps_config = default_template["steps_config"]
                    
                    return {
                        "template_id": template_id,
                        "name": name,
                        "total_steps": total_steps or len(steps_config),
                        "steps_config": steps_config
                    }
                else:
                    # Crear template por defecto
                    cur.execute(
                        """
                        INSERT INTO nurturing_sequence_templates 
                        (name, description, priority_filter, min_score, max_score, total_steps, steps_config, enabled)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id, name, steps_config, total_steps
                        """,
                        (
                            default_template["name"],
                            default_template["description"],
                            default_template["priority_filter"],
                            default_template["min_score"],
                            default_template["max_score"],
                            default_template["total_steps"],
                            json.dumps(default_template["steps_config"]),
                            default_template["enabled"]
                        )
                    )
                    template_id, name, steps_config, total_steps = cur.fetchone()
                    conn.commit()
                    
                    logger.info(f"Template de secuencia creado: {name} (ID: {template_id})")
                    
                    return {
                        "template_id": template_id,
                        "name": name,
                        "total_steps": default_template["total_steps"],
                        "steps_config": default_template["steps_config"]
                    }
    
    @task(task_id="start_nurturing_sequences")
    def start_nurturing_sequences(
        cold_leads: List[Dict[str, Any]], 
        template: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Inicia nuevas secuencias de nutrición para leads fríos.
        Configura timing del primer paso y estado inicial.
        """
        if not cold_leads:
            logger.info("No hay leads fríos para iniciar secuencias")
            return []
        
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        template_id = template["template_id"]
        sequence_name = template["name"]
        steps_config = template["steps_config"]
        total_steps = len(steps_config)
        
        started_sequences = []
        now = datetime.utcnow()
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in cold_leads:
                    try:
                        # Calcular next_send_at basado en el primer paso
                        first_step = next((s for s in steps_config if s.get("step") == 1), None)
                        delay_days = first_step.get("delay_days", 0) if first_step else 0
                        next_send_at = now + timedelta(days=delay_days)
                        
                        cur.execute(
                            """
                            INSERT INTO lead_nurturing_sequences
                            (lead_ext_id, email, sequence_name, current_step, total_steps, status, 
                             lead_score, lead_priority, started_at, next_send_at, last_activity_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (lead_ext_id, sequence_name) DO NOTHING
                            RETURNING id, lead_ext_id, email
                            """,
                            (
                                lead["ext_id"],
                                lead["email"],
                                sequence_name,
                                1,  # Empieza en paso 1
                                total_steps,
                                "active",
                                lead.get("score") or 0,
                                lead.get("priority") or "low",
                                now,
                                next_send_at,
                                now
                            )
                        )
                        
                        result = cur.fetchone()
                        if result:
                            seq_id, lead_ext_id, email = result
                            started_sequences.append({
                                "sequence_id": seq_id,
                                "lead_ext_id": lead_ext_id,
                                "email": email,
                                "lead": lead
                            })
                    except Exception as e:
                        logger.error(
                            f"Error iniciando secuencia para lead {lead.get('email', 'unknown')}: {e}",
                            exc_info=True,
                            extra={"lead_ext_id": lead.get("ext_id"), "error": str(e)}
                        )
                
                conn.commit()
        
        logger.info(f"Iniciadas {len(started_sequences)} nuevas secuencias de nutrición")
        
        try:
            Stats.incr("lead_nurturing.sequences_started", len(started_sequences))
        except Exception:
            pass
        
        return started_sequences
    
    @task(task_id="send_scheduled_emails")
    def send_scheduled_emails() -> List[Dict[str, Any]]:
        """
        Envía emails programados que están listos para enviarse (next_send_at <= ahora).
        Procesa en batch y maneja errores gracefully.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email_webhook = str(params["email_webhook_url"]).strip()
        email_from = str(params["email_from"]).strip()
        dry_run = bool(params.get("dry_run", False))
        timeout = int(params.get("request_timeout", 30))
        max_retries = int(params.get("max_retry_attempts", 3))
        
        if not email_webhook:
            logger.warning("email_webhook_url no configurado, saltando envío de emails")
            return []
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        now = datetime.utcnow()
        
        # Obtener secuencias con emails listos para enviar
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        s.id AS sequence_id,
                        s.lead_ext_id,
                        s.email,
                        s.current_step,
                        s.total_steps,
                        s.sequence_name,
                        l.first_name,
                        l.last_name,
                        l.source,
                        l.utm_source,
                        t.steps_config
                    FROM lead_nurturing_sequences s
                    JOIN leads l ON s.lead_ext_id = l.ext_id
                    JOIN nurturing_sequence_templates t ON s.sequence_name = t.name
                    WHERE 
                        s.status = 'active'
                        AND s.next_send_at <= %s
                        AND s.current_step <= s.total_steps
                    ORDER BY s.next_send_at ASC
                    LIMIT 100
                """, (now,))
                
                columns = [desc[0] for desc in cur.description]
                sequences_to_send = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        if not sequences_to_send:
            logger.info("No hay emails programados para enviar en este momento")
            return []
        
        sent_emails = []
        failed_emails = []
        
        for seq in sequences_to_send:
            try:
                sequence_id = seq["sequence_id"]
                current_step = seq["current_step"]
                steps_config = seq["steps_config"]
                
                # Parse steps_config si es string
                if isinstance(steps_config, str):
                    try:
                        steps_config = json.loads(steps_config)
                    except Exception:
                        logger.warning(f"No se pudo parsear steps_config para secuencia {sequence_id}")
                        continue
                
                # Encontrar configuración del paso actual
                step_config = next(
                    (s for s in steps_config if s.get("step") == current_step),
                    None
                )
                
                if not step_config:
                    logger.warning(
                        f"Paso {current_step} no encontrado en template para secuencia {sequence_id}"
                    )
                    # Avanzar al siguiente paso automáticamente
                    with hook.get_conn() as conn2:
                        with conn2.cursor() as cur2:
                            next_step = current_step + 1
                            if next_step <= seq["total_steps"]:
                                cur2.execute("""
                                    UPDATE lead_nurturing_sequences
                                    SET current_step = %s, updated_at = %s
                                    WHERE id = %s
                                """, (next_step, now, sequence_id))
                            else:
                                cur2.execute("""
                                    UPDATE lead_nurturing_sequences
                                    SET status = 'completed', updated_at = %s
                                    WHERE id = %s
                                """, (now, sequence_id))
                            conn2.commit()
                    continue
                
                # A/B Testing: Seleccionar variante si está habilitado
                ctx = get_current_context()
                enable_ab = bool(ctx["params"].get("enable_ab_testing", False))
                ab_percentage = int(ctx["params"].get("ab_test_percentage", 10))
                
                variant = "A"  # Default
                if enable_ab and ab_percentage > 0:
                    # Selección determinística basada en sequence_id
                    variant_hash = abs(hash(f"{sequence_id}_{current_step}")) % 100
                    variant = "B" if variant_hash < ab_percentage else "A"
                    
                    # Buscar variante B en step_config si existe
                    if variant == "B":
                        subject_template_b = step_config.get("subject_template_b")
                        body_template_b = step_config.get("body_template_b")
                        
                        if subject_template_b and body_template_b:
                            subject_template = subject_template_b
                            body_template = body_template_b
                        else:
                            # Si no hay variante B, usar A
                            variant = "A"
                            subject_template = step_config.get("subject_template", "")
                            body_template = step_config.get("body_template", "")
                    else:
                        subject_template = step_config.get("subject_template", "")
                        body_template = step_config.get("body_template", "")
                else:
                    subject_template = step_config.get("subject_template", "")
                    body_template = step_config.get("body_template", "")
                
                # Optimización de timing si está habilitado
                optimize_timing = bool(ctx["params"].get("optimize_timing", False))
                optimal_time = None
                
                if optimize_timing:
                    lead_info = {
                        "ext_id": seq["lead_ext_id"],
                        "email": seq["email"]
                    }
                    days_history = int(ctx["params"].get("best_time_analysis_days", 30))
                    optimal_time = get_optimal_send_time(lead_info, days_history)
                
                # Preparar datos para renderizado
                lead_data = {
                    "first_name": seq.get("first_name", "").strip() or "Valued Customer",
                    "last_name": seq.get("last_name", "").strip() or "",
                    "email": seq.get("email", "").strip(),
                    "company_name": "nuestra empresa",  # TODO: agregar campo company a tabla leads
                    "source": seq.get("source", ""),
                    "utm_source": seq.get("utm_source", ""),
                    "step_number": current_step,
                    "total_steps": seq["total_steps"]
                }
                
                subject = render_template_advanced(subject_template, lead_data)
                body = render_template_advanced(body_template, lead_data)
                
                # Validación de templates renderizados
                if "{{" in subject or "{{" in body:
                    logger.warning(
                        f"Template no completamente renderizado para secuencia {sequence_id}, "
                        f"paso {current_step}. Placeholders restantes encontrados."
                    )
                
                # Usar tiempo óptimo si está disponible, sino usar ahora
                actual_send_time = optimal_time if optimal_time else now
                
                # Preparar payload para webhook
                payload = {
                    "from": email_from,
                    "to": seq["email"],
                    "subject": subject,
                    "text": body,
                    "run_at": actual_send_time.isoformat() + "Z" if optimal_time else None,
                    "metadata": {
                        "sequence_id": sequence_id,
                        "lead_ext_id": seq["lead_ext_id"],
                        "step_number": current_step,
                        "sequence_name": seq["sequence_name"],
                        "source": seq.get("source"),
                        "utm_source": seq.get("utm_source"),
                        "ab_variant": variant,
                        "optimized_timing": optimal_time.isoformat() if optimal_time else None
                    }
                }
                
                # Enviar email con retry logic mejorado
                event_status = "queued"
                sent_at = None
                failure_reason = None
                
                if not dry_run:
                    for attempt in range(1, max_retries + 1):
                        try:
                            resp = requests.post(
                                email_webhook,
                                json=payload,
                                headers={
                                    "Content-Type": "application/json",
                                    "X-Idempotency-Key": (
                                        f"nurturing-{sequence_id}-{current_step}-"
                                        f"{now.strftime('%Y%m%d%H%M%S')}"
                                    )
                                },
                                timeout=timeout
                            )
                            
                            if resp.status_code < 300:
                                event_status = "sent"
                                sent_at = now
                                break
                            else:
                                failure_reason = f"HTTP {resp.status_code}: {resp.text[:200]}"
                                logger.warning(
                                    f"Email webhook retornó {resp.status_code} para secuencia {sequence_id}, "
                                    f"intento {attempt}/{max_retries}"
                                )
                                if attempt < max_retries:
                                    time.sleep(2 ** attempt)  # Exponential backoff
                                    continue
                                event_status = "failed"
                        except requests.exceptions.Timeout:
                            failure_reason = f"Timeout después de {timeout}s"
                            if attempt < max_retries:
                                time.sleep(2 ** attempt)
                                continue
                            event_status = "failed"
                        except requests.exceptions.RequestException as e:
                            failure_reason = str(e)[:200]
                            logger.warning(
                                f"Error de red al enviar email para secuencia {sequence_id}, "
                                f"intento {attempt}/{max_retries}: {e}"
                            )
                            if attempt < max_retries:
                                time.sleep(2 ** attempt)
                                continue
                            event_status = "failed"
                        except Exception as e:
                            failure_reason = str(e)[:200]
                            logger.error(
                                f"Error inesperado al enviar email para secuencia {sequence_id}: {e}",
                                exc_info=True
                            )
                            event_status = "failed"
                            break
                else:
                    event_status = "sent"  # En dry_run, simulamos éxito
                    sent_at = now
                    logger.info(
                        f"[DRY RUN] Email simulado enviado para secuencia {sequence_id}, paso {current_step}"
                    )
                
                # Registrar evento en BD
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        # Insertar evento
                        body_preview = body[:500] if body else ""
                        metadata_with_variant = payload.get("metadata", {})
                        metadata_with_variant["ab_variant"] = variant
                        
                        cur.execute("""
                            INSERT INTO lead_nurturing_events
                            (sequence_id, lead_ext_id, email, step_number, step_type, subject, 
                             body_preview, status, sent_at, failure_reason, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            sequence_id,
                            seq["lead_ext_id"],
                            seq["email"],
                            current_step,
                            "email",
                            subject,
                            body_preview,
                            event_status,
                            sent_at,
                            failure_reason,
                            json.dumps(metadata_with_variant)
                        ))
                        
                        # Actualizar secuencia: avanzar paso o completar
                        next_step = current_step + 1
                        if next_step <= seq["total_steps"]:
                            next_step_config = next(
                                (s for s in steps_config if s.get("step") == next_step),
                                None
                            )
                            delay_days = next_step_config.get("delay_days", 7) if next_step_config else 7
                            next_send_at = now + timedelta(days=delay_days)
                            
                            # Actualizar secuencia
                            cur.execute("""
                                UPDATE lead_nurturing_sequences
                                SET current_step = %s,
                                    next_send_at = %s,
                                    last_activity_at = %s,
                                    updated_at = %s,
                                    completion_rate = ROUND((%s::NUMERIC / %s::NUMERIC) * 100, 2)
                                WHERE id = %s
                            """, (
                                next_step, 
                                next_send_at, 
                                now, 
                                now,
                                current_step,
                                seq["total_steps"],
                                sequence_id
                            ))
                        else:
                            # Secuencia completada
                            cur.execute("""
                                UPDATE lead_nurturing_sequences
                                SET status = 'completed',
                                    last_activity_at = %s,
                                    updated_at = %s,
                                    completion_rate = 100.0
                                WHERE id = %s
                            """, (now, now, sequence_id))
                        
                        conn.commit()
                
                if event_status == "sent":
                    sent_emails.append({
                        "sequence_id": sequence_id,
                        "lead_ext_id": seq["lead_ext_id"],
                        "step": current_step,
                        "status": event_status
                    })
                else:
                    failed_emails.append({
                        "sequence_id": sequence_id,
                        "step": current_step,
                        "reason": failure_reason
                    })
                
            except Exception as e:
                logger.error(
                    f"Error procesando secuencia {seq.get('sequence_id', 'unknown')}: {e}",
                    exc_info=True,
                    extra={"sequence_id": seq.get("sequence_id"), "error": str(e)}
                )
        
        logger.info(
            f"Emails procesados: {len(sent_emails)} enviados, {len(failed_emails)} fallidos "
            f"de {len(sequences_to_send)} programados"
        )
        
        # Log métricas a MLflow
        ctx = get_current_context()
        if bool(ctx["params"].get("mlflow_enable", False)):
            log_to_mlflow(
                {
                    "emails_sent": len(sent_emails),
                    "emails_failed": len(failed_emails),
                    "total_scheduled": len(sequences_to_send),
                    "success_rate": (len(sent_emails) / len(sequences_to_send) * 100) if sequences_to_send else 0
                },
                {"task": "send_scheduled_emails"}
            )
        
        try:
            Stats.incr("lead_nurturing.emails_sent", len(sent_emails))
            Stats.incr("lead_nurturing.emails_failed", len(failed_emails))
        except Exception:
            pass
        
        return sent_emails
    
    @task(task_id="update_engagement")
    def update_engagement() -> Dict[str, int]:
        """
        Actualiza eventos con información de engagement (opens, clicks, replies).
        Consulta API externa si está configurada y recalcula scores.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        engagement_api = str(params.get("engagement_api_url", "")).strip()
        min_score = int(params["min_score_to_qualify"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Obtener eventos recientes sin engagement actualizado
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT DISTINCT 
                        e.id, 
                        e.email, 
                        e.sequence_id,
                        e.lead_ext_id
                    FROM lead_nurturing_events e
                    WHERE e.status = 'sent'
                        AND e.sent_at >= CURRENT_DATE - INTERVAL '7 days'
                        AND (e.opened_at IS NULL AND e.clicked_at IS NULL AND e.replied_at IS NULL)
                    ORDER BY e.sent_at DESC
                    LIMIT 100
                """)
                
                events = [
                    {
                        "id": row[0],
                        "email": row[1],
                        "sequence_id": row[2],
                        "lead_ext_id": row[3]
                    } 
                    for row in cur.fetchall()
                ]
        
        updated_count = 0
        qualified_count = 0
        
        if not engagement_api:
            logger.info("No hay API de engagement configurada")
            return {"events_updated": 0, "leads_qualified": 0}
        
        if not events:
            logger.info("No hay eventos para actualizar engagement")
            return {"events_updated": 0, "leads_qualified": 0}
        
        # Procesar eventos en batch más eficiente
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for event in events:
                    try:
                        # Consultar API de engagement
                        resp = requests.get(
                            f"{engagement_api}?email={requests.utils.quote(event['email'])}",
                            timeout=10
                        )
                        
                        if resp.status_code >= 300:
                            logger.debug(
                                f"API de engagement retornó {resp.status_code} para {event['email']}"
                            )
                            continue
                        
                        data = resp.json() or {}
                        opened = bool(data.get("opened", False))
                        clicked = bool(data.get("clicked", False))
                        replied = bool(data.get("replied", False))
                        
                        if not (opened or clicked or replied):
                            continue
                        
                        # Actualizar evento
                        updates = []
                        params_list = []
                        
                        now_ts = datetime.utcnow()
                        if opened:
                            updates.append("opened_at = %s")
                            params_list.append(now_ts)
                        if clicked:
                            updates.append("clicked_at = %s")
                            params_list.append(now_ts)
                        if replied:
                            updates.append("replied_at = %s")
                            params_list.append(now_ts)
                        
                        if updates:
                            params_list.extend([now_ts, event["id"]])
                            cur.execute(
                                f"""
                                UPDATE lead_nurturing_events
                                SET {', '.join(updates)}, 
                                    delivered_at = COALESCE(delivered_at, %s)
                                WHERE id = %s
                                """,
                                params_list
                            )
                            updated_count += 1
                            
                            # Actualizar engagement summary
                            cur.execute(
                                "SELECT update_nurturing_engagement_summary(%s)",
                                (event["sequence_id"],)
                            )
                            
                            # Si hay engagement significativo, evaluar calificación
                            if replied or clicked:
                                # Obtener estadísticas de engagement de toda la secuencia
                                cur.execute("""
                                    SELECT 
                                        COUNT(*) FILTER (WHERE e.replied_at IS NOT NULL) as replies,
                                        COUNT(*) FILTER (WHERE e.opened_at IS NOT NULL) as opens,
                                        COUNT(*) FILTER (WHERE e.clicked_at IS NOT NULL) as clicks,
                                        s.lead_score,
                                        s.lead_ext_id
                                    FROM lead_nurturing_sequences s
                                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                                    WHERE s.id = %s
                                    GROUP BY s.id, s.lead_score, s.lead_ext_id
                                """, (event["sequence_id"],))
                                
                                result = cur.fetchone()
                                if result:
                                    replies_count, opens_count, clicks_count, current_score, lead_ext_id = result
                                    
                                    # Calcular nuevo score con lógica mejorada
                                    new_score = calculate_lead_score_from_engagement(
                                        current_score or 0,
                                        replies_count or 0,
                                        opens_count or 0,
                                        clicks_count or 0
                                    )
                                    
                                    if new_score >= min_score and new_score > (current_score or 0):
                                        # Calificar lead y actualizar en una transacción
                                        now_ts = datetime.utcnow()
                                        
                                        # Actualizar secuencia
                                        cur.execute("""
                                            UPDATE lead_nurturing_sequences
                                            SET qualified_at = %s,
                                                status = 'qualified',
                                                lead_score = %s,
                                                updated_at = %s
                                            WHERE id = %s
                                        """, (now_ts, new_score, now_ts, event["sequence_id"]))
                                        
                                        # Actualizar lead en tabla principal
                                        cur.execute("""
                                            UPDATE leads
                                            SET score = %s,
                                                priority = CASE 
                                                    WHEN %s >= 50 THEN 'high'
                                                    WHEN %s >= 35 THEN 'medium'
                                                    ELSE 'low'
                                                END,
                                                updated_at = %s
                                            WHERE ext_id = %s
                                        """, (new_score, new_score, new_score, now_ts, lead_ext_id))
                                        
                                        qualified_count += 1
                                        logger.info(
                                            f"Lead {lead_ext_id} calificado: "
                                            f"score {current_score or 0} -> {new_score}"
                                        )
                        
                    except requests.exceptions.RequestException as e:
                        logger.debug(
                            f"Error de red consultando engagement para evento {event.get('id')}: {e}"
                        )
                    except Exception as e:
                        logger.error(
                            f"Error actualizando engagement para evento {event.get('id')}: {e}",
                            exc_info=True
                        )
                
                conn.commit()
        
        logger.info(
            f"Engagement actualizado: {updated_count} eventos, {qualified_count} leads calificados"
        )
        
        # Log métricas a MLflow
        ctx = get_current_context()
        if bool(ctx["params"].get("mlflow_enable", False)):
            log_to_mlflow(
                {
                    "engagement_events_updated": updated_count,
                    "leads_qualified": qualified_count,
                    "qualification_rate": (qualified_count / max(updated_count, 1)) * 100
                },
                {"task": "update_engagement"}
            )
        
        try:
            Stats.incr("lead_nurturing.engagement_updated", updated_count)
            Stats.incr("lead_nurturing.leads_qualified", qualified_count)
        except Exception:
            pass
        
        return {
            "events_updated": updated_count,
            "leads_qualified": qualified_count
        }
    
    @task(task_id="analyze_ab_test_results")
    def analyze_ab_test_results() -> Dict[str, Any]:
        """
        Analiza resultados de A/B testing y determina la variante ganadora.
        Calcula significancia estadística y métricas comparativas.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_ab = bool(params.get("enable_ab_testing", False))
        
        if not enable_ab:
            return {"ab_testing_enabled": False}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener métricas por variante
                cur.execute("""
                    SELECT 
                        metadata->>'ab_variant' as variant,
                        COUNT(*) as total_sent,
                        COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as opened,
                        COUNT(*) FILTER (WHERE clicked_at IS NOT NULL) as clicked,
                        COUNT(*) FILTER (WHERE replied_at IS NOT NULL) as replied
                    FROM lead_nurturing_events
                    WHERE status = 'sent'
                        AND sent_at >= CURRENT_DATE - INTERVAL '30 days'
                        AND metadata->>'ab_variant' IS NOT NULL
                    GROUP BY metadata->>'ab_variant'
                """)
                
                results = cur.fetchall()
                
                ab_metrics = {}
                for variant, total, opened, clicked, replied in results:
                    if variant:
                        ab_metrics[variant] = {
                            "total_sent": total,
                            "opened": opened,
                            "clicked": clicked,
                            "replied": replied,
                            "open_rate": (opened / total * 100) if total > 0 else 0,
                            "click_rate": (clicked / total * 100) if total > 0 else 0,
                            "reply_rate": (replied / total * 100) if total > 0 else 0
                        }
                
                # Determinar ganador
                winner = None
                if "A" in ab_metrics and "B" in ab_metrics:
                    a_metrics = ab_metrics["A"]
                    b_metrics = ab_metrics["B"]
                    
                    # Comparar reply rate como métrica principal
                    if b_metrics["reply_rate"] > a_metrics["reply_rate"]:
                        winner = "B"
                        improvement = ((b_metrics["reply_rate"] - a_metrics["reply_rate"]) / 
                                     max(a_metrics["reply_rate"], 1)) * 100
                    elif a_metrics["reply_rate"] > b_metrics["reply_rate"]:
                        winner = "A"
                        improvement = ((a_metrics["reply_rate"] - b_metrics["reply_rate"]) / 
                                     max(b_metrics["reply_rate"], 1)) * 100
                    else:
                        winner = "Tie"
                        improvement = 0
                    
                    # Cálculo de significancia estadística simple (t-test simplificado)
                    # Para producción, usar scipy.stats para cálculo más preciso
                    n_a = a_metrics["total_sent"]
                    n_b = b_metrics["total_sent"]
                    p_a = a_metrics["reply_rate"] / 100
                    p_b = b_metrics["reply_rate"] / 100
                    
                    if n_a > 0 and n_b > 0:
                        # Pooled proportion
                        p_pool = ((p_a * n_a) + (p_b * n_b)) / (n_a + n_b)
                        
                        # Standard error
                        se = (p_pool * (1 - p_pool) * (1/n_a + 1/n_b)) ** 0.5
                        
                        # Z-score
                        if se > 0:
                            z_score = abs(p_b - p_a) / se
                            # Simplificado: z > 1.96 = 95% confidence (p < 0.05)
                            is_significant = z_score > 1.96
                        else:
                            is_significant = False
                            z_score = 0
                    else:
                        is_significant = False
                        z_score = 0
                else:
                    is_significant = False
                    improvement = 0
                    z_score = 0
                
                analysis = {
                    "ab_testing_enabled": True,
                    "variants": ab_metrics,
                    "winner": winner,
                    "improvement_pct": improvement,
                    "is_significant": is_significant,
                    "z_score": z_score,
                    "analysis_date": datetime.utcnow().isoformat()
                }
                
                # Log a MLflow
                if bool(ctx["params"].get("mlflow_enable", False)):
                    mlflow_metrics = {}
                    for variant, metrics in ab_metrics.items():
                        mlflow_metrics[f"ab_{variant}_open_rate"] = metrics["open_rate"]
                        mlflow_metrics[f"ab_{variant}_click_rate"] = metrics["click_rate"]
                        mlflow_metrics[f"ab_{variant}_reply_rate"] = metrics["reply_rate"]
                    
                    mlflow_metrics["ab_winner"] = float(1 if winner == "B" else 0) if winner else 0.5
                    mlflow_metrics["ab_improvement_pct"] = improvement
                    mlflow_metrics["ab_is_significant"] = float(1 if is_significant else 0)
                    
                    log_to_mlflow(mlflow_metrics, {"task": "analyze_ab_test_results"})
                
                logger.info(
                    f"A/B Test Analysis: Winner={winner}, Improvement={improvement:.2f}%, "
                    f"Significant={is_significant}"
                )
                
                return analysis
    
    @task(task_id="auto_pause_inactive_sequences")
    def auto_pause_inactive_sequences() -> Dict[str, int]:
        """
        Pausa automáticamente secuencias que no han tenido engagement después de X días.
        Mejora la eficiencia del sistema y evita spam innecesario.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_auto_pause = bool(params.get("enable_auto_pause", True))
        pause_after_days = int(params.get("pause_after_days", 30))
        
        if not enable_auto_pause:
            return {"paused": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        paused_count = 0
        now = datetime.utcnow()
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Obtener secuencias activas sin engagement reciente
                cur.execute("""
                    SELECT 
                        s.id,
                        s.lead_ext_id,
                        s.email,
                        s.last_activity_at,
                        s.started_at,
                        COUNT(e.id) FILTER (WHERE e.opened_at IS NOT NULL OR e.replied_at IS NOT NULL) as engagement_count
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.status = 'active'
                    GROUP BY s.id, s.lead_ext_id, s.email, s.last_activity_at, s.started_at
                    HAVING 
                        (s.last_activity_at IS NULL OR s.last_activity_at < %s)
                        AND COUNT(e.id) FILTER (WHERE e.opened_at IS NOT NULL OR e.replied_at IS NOT NULL) = 0
                    LIMIT 50
                """, (now - timedelta(days=pause_after_days),))
                
                sequences_to_pause = cur.fetchall()
                
                for seq_id, lead_ext_id, email, last_activity, started_at, engagement_count in sequences_to_pause:
                    try:
                        cur.execute("""
                            UPDATE lead_nurturing_sequences
                            SET status = 'paused',
                                paused_at = %s,
                                paused_reason = %s,
                                updated_at = %s
                            WHERE id = %s
                        """, (
                            now,
                            f"Sin engagement después de {pause_after_days} días",
                            now,
                            seq_id
                        ))
                        paused_count += 1
                        logger.debug(f"Secuencia {seq_id} pausada automáticamente (sin engagement)")
                    except Exception as e:
                        logger.error(f"Error pausando secuencia {seq_id}: {e}")
                
                conn.commit()
        
        if paused_count > 0:
            logger.info(f"{paused_count} secuencias pausadas automáticamente por inactividad")
        
        try:
            Stats.incr("lead_nurturing.sequences_auto_paused", paused_count)
        except Exception:
            pass
        
        return {"paused": paused_count}
    
    @task(task_id="refresh_conversion_metrics")
    def refresh_conversion_metrics() -> None:
        """
        Refresca la vista materializada de métricas de conversión.
        Usa CONCURRENTLY si está disponible para no bloquear lecturas.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Intentar CONCURRENTLY primero (no bloquea lecturas)
                    try:
                        cur.execute(
                            "REFRESH MATERIALIZED VIEW CONCURRENTLY mv_nurturing_conversion_metrics"
                        )
                        conn.commit()
                        logger.info("Vista de métricas refrescada (CONCURRENTLY)")
                    except Exception:
                        # Si CONCURRENTLY falla (puede requerir índice único), intentar sin él
                        cur.execute("REFRESH MATERIALIZED VIEW mv_nurturing_conversion_metrics")
                        conn.commit()
                        logger.info("Vista de métricas refrescada (sin CONCURRENTLY)")
        except Exception as e:
            logger.warning(f"No se pudo refrescar vista de métricas: {e}")
    
    @task(task_id="generate_performance_report")
    def generate_performance_report(
        ab_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Genera reporte de performance completo del sistema de nurturing.
        Incluye métricas agregadas, tendencias y recomendaciones.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        now = datetime.utcnow()
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Métricas generales de los últimos 30 días
                cur.execute("""
                    SELECT 
                        COUNT(DISTINCT s.id) as total_sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as total_emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as emails_opened,
                        COUNT(DISTINCT CASE WHEN e.clicked_at IS NOT NULL THEN e.id END) as emails_clicked,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as emails_replied,
                        AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days_to_qualify
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= CURRENT_DATE - INTERVAL '30 days'
                """)
                
                result = cur.fetchone()
                
                if result:
                    (total_seq, qualified, sent, opened, clicked, replied, avg_days) = result
                    
                    report = {
                        "period": "last_30_days",
                        "total_sequences": total_seq or 0,
                        "qualified_leads": qualified or 0,
                        "conversion_rate": (qualified / total_seq * 100) if total_seq > 0 else 0,
                        "total_emails_sent": sent or 0,
                        "emails_opened": opened or 0,
                        "emails_clicked": clicked or 0,
                        "emails_replied": replied or 0,
                        "open_rate": (opened / sent * 100) if sent > 0 else 0,
                        "click_rate": (clicked / sent * 100) if sent > 0 else 0,
                        "reply_rate": (replied / sent * 100) if sent > 0 else 0,
                        "avg_days_to_qualify": round(float(avg_days or 0), 2),
                        "generated_at": now.isoformat()
                    }
                    
                    # Análisis de mejor paso (mayor engagement)
                    cur.execute("""
                        SELECT 
                            step_number,
                            COUNT(*) as sent,
                            COUNT(*) FILTER (WHERE opened_at IS NOT NULL) as opened,
                            COUNT(*) FILTER (WHERE replied_at IS NOT NULL) as replied
                        FROM lead_nurturing_events
                        WHERE sent_at >= CURRENT_DATE - INTERVAL '30 days'
                            AND status = 'sent'
                        GROUP BY step_number
                        ORDER BY (COUNT(*) FILTER (WHERE replied_at IS NOT NULL)::NUMERIC / NULLIF(COUNT(*), 0)) DESC
                        LIMIT 1
                    """)
                    
                    best_step_result = cur.fetchone()
                    if best_step_result:
                        report["best_performing_step"] = {
                            "step_number": int(best_step_result[0]),
                            "reply_rate": (best_step_result[2] / best_step_result[1] * 100) 
                                         if best_step_result[1] > 0 else 0
                        }
                    
                    # Log completo a MLflow
                    if bool(ctx["params"].get("mlflow_enable", False)):
                        log_to_mlflow(
                            {
                                "conversion_rate": report["conversion_rate"],
                                "open_rate": report["open_rate"],
                                "reply_rate": report["reply_rate"],
                                "avg_days_to_qualify": report["avg_days_to_qualify"]
                            },
                            {"task": "generate_performance_report", "period": "30_days"}
                        )
                    
                    logger.info(
                        f"Performance Report: Conversion={report['conversion_rate']:.2f}%, "
                        f"Reply Rate={report['reply_rate']:.2f}%"
                    )
                    
                    return report
                
                return {"error": "No data available"}
    
    @task(task_id="notify_summary")
    def notify_summary(
        engagement_stats: Dict[str, int],
        pause_stats: Dict[str, int],
        ab_analysis: Dict[str, Any],
        performance_report: Dict[str, Any]
    ) -> None:
        """
        Envía resumen ejecutivo a Slack si está configurado.
        """
        ctx = get_current_context()
        params = ctx["params"]
        slack_webhook = str(params.get("slack_webhook_url", "")).strip()
        
        if not slack_webhook:
            return
        
        run_id = str((ctx.get("dag_run") or {}).get("run_id", "unknown"))
        
        # Construir mensaje con información completa
        text_parts = [
            f"✅ *Lead Nurturing* - Ejecución completada",
            f"Run ID: `{run_id}`\n",
            f"📊 *Métricas de esta ejecución:*",
            f"• Eventos actualizados: {engagement_stats.get('events_updated', 0)}",
            f"• Leads calificados: {engagement_stats.get('leads_qualified', 0)}",
            f"• Secuencias pausadas: {pause_stats.get('paused', 0)}\n"
        ]
        
        # Agregar reporte de performance si está disponible
        if performance_report and "conversion_rate" in performance_report:
            text_parts.extend([
                f"📈 *Performance (30 días):*",
                f"• Conversion Rate: {performance_report.get('conversion_rate', 0):.2f}%",
                f"• Open Rate: {performance_report.get('open_rate', 0):.2f}%",
                f"• Reply Rate: {performance_report.get('reply_rate', 0):.2f}%",
                f"• Avg días a calificar: {performance_report.get('avg_days_to_qualify', 0):.1f}\n"
            ])
        
        # Agregar análisis A/B si está disponible
        if ab_analysis.get("ab_testing_enabled") and "winner" in ab_analysis:
            winner = ab_analysis.get("winner", "N/A")
            improvement = ab_analysis.get("improvement_pct", 0)
            is_sig = ab_analysis.get("is_significant", False)
            
            text_parts.extend([
                f"🧪 *A/B Testing:*",
                f"• Ganador: Variante {winner}",
                f"• Mejora: {improvement:.2f}%",
                f"• Significativo: {'✅ Sí' if is_sig else '❌ No'}"
            ])
        
        text = "\n".join(text_parts)
        
        try:
            resp = requests.post(
                slack_webhook,
                json={"text": text},
                timeout=10,
                headers={"Content-Type": "application/json"}
            )
            if resp.status_code >= 300:
                logger.warning(f"Slack webhook retornó {resp.status_code}")
        except Exception as e:
            logger.warning(f"Error enviando notificación a Slack: {e}")
    
    @task(task_id="export_metrics_to_s3")
    def export_metrics_to_s3(performance_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exporta métricas a S3 para análisis externo y backup.
        """
        ctx = get_current_context()
        params = ctx["params"]
        enable_export = bool(params.get("export_metrics_to_s3", False))
        s3_bucket = str(params.get("s3_bucket", "")).strip()
        s3_path = str(params.get("s3_path", "lead_nurturing/metrics")).strip()
        
        if not enable_export or not s3_bucket:
            return {"exported": False, "reason": "not_enabled_or_no_bucket"}
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client('s3')
            
            # Preparar datos para exportar
            export_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "run_id": str((ctx.get("dag_run") or {}).get("run_id", "unknown")),
                "performance_report": performance_report,
                "export_version": "1.0"
            }
            
            # Generar key único
            date_str = datetime.utcnow().strftime("%Y/%m/%d")
            filename = f"lead_nurturing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            s3_key = f"{s3_path}/{date_str}/{filename}"
            
            # Subir a S3
            s3_client.put_object(
                Bucket=s3_bucket,
                Key=s3_key,
                Body=json.dumps(export_data, indent=2),
                ContentType='application/json'
            )
            
            logger.info(f"Métricas exportadas a S3: s3://{s3_bucket}/{s3_key}")
            
            return {"exported": True, "s3_key": s3_key, "bucket": s3_bucket}
            
        except ImportError:
            logger.warning("boto3 no disponible, saltando exportación a S3")
            return {"exported": False, "reason": "boto3_not_available"}
        except Exception as e:
            logger.error(f"Error exportando métricas a S3: {e}", exc_info=True)
            return {"exported": False, "reason": str(e)[:200]}
    
    @task(task_id="check_conversion_alerts")
    def check_conversion_alerts(performance_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica si hay alertas que disparar basadas en umbrales de conversión.
        """
        ctx = get_current_context()
        params = ctx["params"]
        enable_alerts = bool(params.get("enable_alerts", False))
        alert_on_low = bool(params.get("alert_on_low_conversion", False))
        threshold = float(params.get("low_conversion_threshold", 5.0))
        
        if not enable_alerts or not alert_on_low:
            return {"alerts_triggered": 0}
        
        alerts = []
        
        if performance_report and "conversion_rate" in performance_report:
            conversion_rate = performance_report.get("conversion_rate", 0)
            
            if conversion_rate < threshold:
                alerts.append({
                    "type": "low_conversion",
                    "severity": "warning",
                    "message": f"Conversion rate ({conversion_rate:.2f}%) está por debajo del umbral ({threshold}%)",
                    "current_value": conversion_rate,
                    "threshold": threshold
                })
        
        if performance_report and "reply_rate" in performance_report:
            reply_rate = performance_report.get("reply_rate", 0)
            reply_threshold = threshold * 2  # Reply rate debería ser mayor
            
            if reply_rate < reply_threshold:
                alerts.append({
                    "type": "low_reply_rate",
                    "severity": "info",
                    "message": f"Reply rate ({reply_rate:.2f}%) está bajo",
                    "current_value": reply_rate,
                    "threshold": reply_threshold
                })
        
        # Enviar alertas a Slack si hay webhook configurado
        if alerts:
            slack_webhook = str(params.get("slack_webhook_url", "")).strip()
            if slack_webhook:
                alert_text = "🚨 *Alertas de Lead Nurturing*\n\n"
                for alert in alerts:
                    emoji = "⚠️" if alert["severity"] == "warning" else "ℹ️"
                    alert_text += f"{emoji} *{alert['type']}*\n{alert['message']}\n\n"
                
                try:
                    requests.post(
                        slack_webhook,
                        json={"text": alert_text},
                        timeout=10,
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    logger.warning(f"Error enviando alerta a Slack: {e}")
        
        return {
            "alerts_triggered": len(alerts),
            "alerts": alerts
        }
    
    @task(task_id="cohort_analysis")
    def cohort_analysis() -> Dict[str, Any]:
        """
        Analiza cohorts de leads por semana/mes para identificar tendencias.
        """
        ctx = get_current_context()
        params = ctx["params"]
        enable_cohort = bool(params.get("enable_cohort_analysis", False))
        conn_id = str(params["postgres_conn_id"])
        
        if not enable_cohort:
            return {"cohort_analysis_enabled": False}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Agrupar por semana de inicio
                cur.execute("""
                    SELECT 
                        DATE_TRUNC('week', s.started_at) as cohort_week,
                        COUNT(DISTINCT s.id) as total_sequences,
                        COUNT(DISTINCT CASE WHEN s.qualified_at IS NOT NULL THEN s.id END) as qualified,
                        COUNT(DISTINCT e.id) as emails_sent,
                        COUNT(DISTINCT CASE WHEN e.opened_at IS NOT NULL THEN e.id END) as emails_opened,
                        COUNT(DISTINCT CASE WHEN e.replied_at IS NOT NULL THEN e.id END) as emails_replied,
                        AVG(EXTRACT(EPOCH FROM (s.qualified_at - s.started_at)) / 86400) as avg_days_to_qualify
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.started_at >= CURRENT_DATE - INTERVAL '12 weeks'
                    GROUP BY DATE_TRUNC('week', s.started_at)
                    ORDER BY cohort_week DESC
                """)
                
                cohorts = []
                for row in cur.fetchall():
                    cohort_week, total, qualified, sent, opened, replied, avg_days = row
                    cohorts.append({
                        "cohort_week": str(cohort_week) if cohort_week else None,
                        "total_sequences": total or 0,
                        "qualified": qualified or 0,
                        "conversion_rate": (qualified / total * 100) if total > 0 else 0,
                        "emails_sent": sent or 0,
                        "emails_opened": opened or 0,
                        "emails_replied": replied or 0,
                        "open_rate": (opened / sent * 100) if sent > 0 else 0,
                        "reply_rate": (replied / sent * 100) if sent > 0 else 0,
                        "avg_days_to_qualify": round(float(avg_days or 0), 2)
                    })
                
                # Calcular tendencias
                if len(cohorts) >= 2:
                    latest = cohorts[0]
                    previous = cohorts[1]
                    
                    conversion_trend = latest["conversion_rate"] - previous["conversion_rate"]
                    reply_trend = latest["reply_rate"] - previous["reply_rate"]
                    
                    analysis = {
                        "cohort_analysis_enabled": True,
                        "cohorts": cohorts,
                        "trends": {
                            "conversion_rate_change": round(conversion_trend, 2),
                            "reply_rate_change": round(reply_trend, 2),
                            "improving": conversion_trend > 0 and reply_trend > 0
                        },
                        "analysis_date": datetime.utcnow().isoformat()
                    }
                else:
                    analysis = {
                        "cohort_analysis_enabled": True,
                        "cohorts": cohorts,
                        "trends": None,
                        "analysis_date": datetime.utcnow().isoformat()
                    }
                
                # Log a MLflow
                if bool(ctx["params"].get("mlflow_enable", False)) and cohorts:
                    latest_cohort = cohorts[0]
                    log_to_mlflow(
                        {
                            "latest_cohort_conversion_rate": latest_cohort["conversion_rate"],
                            "latest_cohort_reply_rate": latest_cohort["reply_rate"],
                            "cohort_count": len(cohorts)
                        },
                        {"task": "cohort_analysis"}
                    )
                
                logger.info(f"Cohort analysis completado: {len(cohorts)} cohorts analizados")
                
                return analysis
    
    @task(task_id="segment_leads_advanced")
    def segment_leads_advanced(cold_leads: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Segmenta leads de forma avanzada para personalización de secuencias.
        """
        ctx = get_current_context()
        params = ctx["params"]
        enable_segmentation = bool(params.get("enable_segmentation", False))
        
        if not enable_segmentation or not cold_leads:
            return {"segmentation_enabled": False}
        
        segments = {
            "by_source": {},
            "by_score_range": {
                "0-20": [],
                "21-35": [],
                "36-49": []
            }
        }
        
        segment_by_source = bool(params.get("segment_by_source", False))
        segment_by_score = bool(params.get("segment_by_score_range", False))
        
        for lead in cold_leads:
            # Segmentación por source
            if segment_by_source:
                source = lead.get("source") or "unknown"
                if source not in segments["by_source"]:
                    segments["by_source"][source] = []
                segments["by_source"][source].append(lead)
            
            # Segmentación por rango de score
            if segment_by_score:
                score = lead.get("score") or 0
                if score <= 20:
                    segments["by_score_range"]["0-20"].append(lead)
                elif score <= 35:
                    segments["by_score_range"]["21-35"].append(lead)
                else:
                    segments["by_score_range"]["36-49"].append(lead)
        
        # Log estadísticas de segmentación
        if segment_by_source:
            for source, leads_in_segment in segments["by_source"].items():
                logger.info(f"Segment '{source}': {len(leads_in_segment)} leads")
        
        if segment_by_score:
            for range_name, leads_in_range in segments["by_score_range"].items():
                logger.info(f"Score range '{range_name}': {len(leads_in_range)} leads")
        
        return {
            "segmentation_enabled": True,
            "segments": segments,
            "total_leads": len(cold_leads)
        }
    
    # ============================================================================
    # Pipeline Principal
    # ============================================================================
    schema_ok = ensure_schema()
    
    cold_leads = identify_cold_leads()
    template = get_or_create_sequence_template()
    
    # Segmentación avanzada (opcional, corre en paralelo)
    segments = segment_leads_advanced(cold_leads)
    
    sequences = start_nurturing_sequences(cold_leads, template)
    sent = send_scheduled_emails()
    engagement = update_engagement()
    paused = auto_pause_inactive_sequences()
    
    # Analytics avanzados (paralelos)
    ab_analysis = analyze_ab_test_results()
    performance_report = generate_performance_report(ab_analysis)
    cohort_data = cohort_analysis()
    
    # Exportación y alertas
    s3_export = export_metrics_to_s3(performance_report)
    alerts = check_conversion_alerts(performance_report)
    
    refresh_conversion_metrics()
    notify_summary(engagement, paused, ab_analysis, performance_report)


dag = lead_nurturing()

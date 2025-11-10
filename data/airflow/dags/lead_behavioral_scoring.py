from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_behavioral_scoring",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Scoring Basado en Comportamiento
    
    Calcula score dinámico basado en comportamiento del lead:
    - Visitas a sitio web
    - Descargas de contenido
    - Clicks en emails
    - Engagement en redes sociales
    - Interacciones con chatbot
    - Tiempo en página
    - Páginas visitadas
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `max_leads_per_run`: Máximo de leads a procesar (default: 200)
    - `behavior_decay_days`: Días para decay de comportamiento (default: 30)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_leads_per_run": Param(200, type="integer", minimum=1, maximum=1000),
        "behavior_decay_days": Param(30, type="integer", minimum=7, maximum=90),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "behavioral", "scoring", "automation"],
)
def lead_behavioral_scoring() -> None:
    """
    DAG para scoring basado en comportamiento.
    """
    
    @task(task_id="collect_behavioral_data")
    def collect_behavioral_data() -> List[Dict[str, Any]]:
        """Recolecta datos de comportamiento."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Obtener leads con datos de comportamiento
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.id,
                        p.lead_ext_id,
                        p.email,
                        p.score,
                        p.stage,
                        p.metadata
                    FROM sales_pipeline p
                    WHERE 
                        p.stage NOT IN ('closed_won', 'closed_lost')
                        AND p.metadata IS NOT NULL
                    ORDER BY p.priority DESC, p.score DESC
                    LIMIT %s
                """, (max_leads,))
                
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Recolectados {len(leads)} leads con datos de comportamiento")
        return leads
    
    @task(task_id="calculate_behavioral_score")
    def calculate_behavioral_score(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calcula score basado en comportamiento."""
        ctx = get_current_context()
        params = ctx["params"]
        decay_days = int(params["behavior_decay_days"])
        
        scored_leads = []
        
        for lead in leads:
            behavioral_score = calculate_behavior_score(lead, decay_days)
            lead["behavioral_score"] = behavioral_score
            lead["behavioral_signals"] = extract_behavioral_signals(lead)
            scored_leads.append(lead)
        
        return scored_leads
    
    @task(task_id="update_behavioral_scores")
    def update_behavioral_scores(scored_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Actualiza scores basados en comportamiento."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"updated": 0, "errors": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in scored_leads:
                    try:
                        behavioral_score = lead.get("behavioral_score", 0)
                        behavioral_signals = lead.get("behavioral_signals", {})
                        
                        if not dry_run:
                            existing_metadata = lead.get("metadata") or {}
                            if isinstance(existing_metadata, str):
                                existing_metadata = json.loads(existing_metadata)
                            
                            updated_metadata = {
                                **existing_metadata,
                                "behavioral": {
                                    "score": behavioral_score,
                                    "signals": behavioral_signals,
                                    "updated_at": datetime.utcnow().isoformat()
                                }
                            }
                            
                            # Combinar score base con behavioral score
                            base_score = lead.get("score", 0)
                            # Behavioral score puede agregar hasta 30 puntos
                            new_score = min(base_score + behavioral_score, 100)
                            
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    score = %s,
                                    metadata = %s::jsonb,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (new_score, json.dumps(updated_metadata), lead["id"]))
                            
                            conn.commit()
                            stats["updated"] += 1
                            
                            logger.info(f"Lead {lead['lead_ext_id']} - Behavioral Score: +{behavioral_score}, New Total: {new_score}")
                        else:
                            logger.info(f"[DRY RUN] Lead {lead['lead_ext_id']} - Behavioral Score: +{behavioral_score}")
                    
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error actualizando behavioral score {lead.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Actualización de behavioral scores completada: {stats}")
        return stats
    
    def calculate_behavior_score(lead: Dict[str, Any], decay_days: int) -> int:
        """Calcula score basado en comportamiento."""
        metadata = lead.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        score = 0
        
        # Eventos de comportamiento (deberían venir de tracking)
        behavioral_data = metadata.get("behavioral", {})
        events = behavioral_data.get("events", [])
        
        # Peso de eventos según tipo
        event_weights = {
            "page_visit": 1,
            "download": 5,
            "email_open": 2,
            "email_click": 3,
            "form_submit": 10,
            "demo_request": 20,
            "pricing_view": 8,
            "chatbot_interaction": 3,
            "video_watch": 4,
            "webinar_register": 15
        }
        
        # Calcular score con decay temporal
        now = datetime.utcnow()
        for event in events:
            event_type = event.get("type", "")
            event_time = datetime.fromisoformat(event.get("timestamp", now.isoformat()).replace('Z', '+00:00'))
            
            # Aplicar decay
            days_ago = (now - event_time.replace(tzinfo=None)).days
            if days_ago > decay_days:
                continue  # Evento muy antiguo
            
            decay_factor = 1.0 - (days_ago / decay_days)
            weight = event_weights.get(event_type, 1)
            
            score += int(weight * decay_factor)
        
        # Bonus por frecuencia
        if len(events) > 10:
            score += 5  # Lead muy activo
        elif len(events) > 5:
            score += 2
        
        # Cap en 30 puntos
        return min(score, 30)
    
    def extract_behavioral_signals(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae señales de comportamiento."""
        metadata = lead.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        behavioral_data = metadata.get("behavioral", {})
        events = behavioral_data.get("events", [])
        
        signals = {
            "total_events": len(events),
            "recent_events": len([e for e in events if is_recent_event(e)]),
            "has_download": any(e.get("type") == "download" for e in events),
            "has_demo_request": any(e.get("type") == "demo_request" for e in events),
            "has_pricing_view": any(e.get("type") == "pricing_view" for e in events),
            "has_webinar_register": any(e.get("type") == "webinar_register" for e in events),
            "last_event_type": events[-1].get("type") if events else None,
            "last_event_time": events[-1].get("timestamp") if events else None
        }
        
        return signals
    
    def is_recent_event(event: Dict[str, Any], days: int = 7) -> bool:
        """Verifica si evento es reciente."""
        try:
            event_time = datetime.fromisoformat(event.get("timestamp", "").replace('Z', '+00:00'))
            days_ago = (datetime.utcnow() - event_time.replace(tzinfo=None)).days
            return days_ago <= days
        except:
            return False
    
    # Pipeline
    leads = collect_behavioral_data()
    scored_leads = calculate_behavioral_score(leads)
    stats = update_behavioral_scores(scored_leads)


dag = lead_behavioral_scoring()


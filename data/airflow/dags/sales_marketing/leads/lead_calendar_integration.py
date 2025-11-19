from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import requests

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_calendar_integration",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */4 * * *",  # Cada 4 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Integración con Calendarios
    
    Sincroniza reuniones y eventos con calendarios:
    - Crear eventos de seguimiento en calendario
    - Sincronizar reuniones desde CRM
    - Enviar recordatorios de reuniones
    - Detectar disponibilidad de vendedores
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `calendar_api_url`: URL del servicio de calendario
    - `calendar_type`: Tipo de calendario ('google', 'outlook', 'calendly')
    - `auto_create_events`: Crear eventos automáticamente (default: true)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "calendar_api_url": Param("", type="string"),
        "calendar_type": Param("google", type="string", enum=["google", "outlook", "calendly"]),
        "auto_create_events": Param(True, type="boolean"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "calendar", "integration", "automation"],
)
def lead_calendar_integration() -> None:
    """
    DAG para integración con calendarios.
    """
    
    @task(task_id="get_upcoming_meetings")
    def get_upcoming_meetings() -> List[Dict[str, Any]]:
        """Obtiene reuniones próximas desde pipeline."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Leads con meeting_scheduled stage
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        p.id,
                        p.lead_ext_id,
                        p.email,
                        p.first_name,
                        p.last_name,
                        p.assigned_to,
                        p.metadata
                    FROM sales_pipeline p
                    WHERE 
                        p.stage = 'meeting_scheduled'
                        AND (p.metadata->>'meeting_scheduled_at')::timestamp >= NOW()
                        AND (p.metadata->>'calendar_event_id') IS NULL
                """)
                
                columns = [desc[0] for desc in cur.description]
                meetings = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontradas {len(meetings)} reuniones para crear eventos")
        return meetings
    
    @task(task_id="create_calendar_events")
    def create_calendar_events(meetings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Crea eventos en calendario."""
        ctx = get_current_context()
        params = ctx["params"]
        calendar_api_url = str(params["calendar_api_url"])
        calendar_type = str(params["calendar_type"])
        auto_create = bool(params["auto_create_events"])
        dry_run = bool(params["dry_run"])
        
        if not auto_create or not calendar_api_url:
            return {"created": 0, "errors": 0}
        
        stats = {"created": 0, "errors": 0}
        hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
        
        for meeting in meetings:
            try:
                metadata = meeting.get("metadata") or {}
                if isinstance(metadata, str):
                    metadata = json.loads(metadata)
                
                meeting_time = metadata.get("meeting_scheduled_at")
                if not meeting_time:
                    continue
                
                # Crear evento en calendario
                event_data = {
                    "title": f"Reunión con {meeting.get('first_name', 'Lead')} {meeting.get('last_name', '')}",
                    "description": f"Reunión de ventas con lead {meeting['lead_ext_id']}",
                    "start_time": meeting_time,
                    "end_time": (datetime.fromisoformat(meeting_time.replace('Z', '+00:00')) + timedelta(hours=1)).isoformat(),
                    "attendees": [
                        meeting["email"],
                        meeting.get("assigned_to")
                    ],
                    "location": metadata.get("meeting_location", "Virtual"),
                    "lead_id": meeting["lead_ext_id"]
                }
                
                if not dry_run:
                    # Llamar API de calendario
                    response = requests.post(
                        calendar_api_url,
                        json=event_data,
                        timeout=10
                    )
                    response.raise_for_status()
                    
                    event_result = response.json()
                    event_id = event_result.get("event_id") or event_result.get("id")
                    
                    # Guardar event_id en metadata
                    updated_metadata = {
                        **metadata,
                        "calendar_event_id": event_id,
                        "calendar_type": calendar_type,
                        "calendar_event_created_at": datetime.utcnow().isoformat()
                    }
                    
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET metadata = %s::jsonb,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (json.dumps(updated_metadata), meeting["id"]))
                            
                            conn.commit()
                    
                    stats["created"] += 1
                    logger.info(f"Evento creado para lead {meeting['lead_ext_id']}: {event_id}")
                else:
                    logger.info(f"[DRY RUN] Evento sería creado para {meeting['lead_ext_id']}")
                    stats["created"] += 1
            
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error creando evento para {meeting.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Creación de eventos completada: {stats}")
        return stats
    
    # Pipeline
    meetings = get_upcoming_meetings()
    stats = create_calendar_events(meetings)


dag = lead_calendar_integration()


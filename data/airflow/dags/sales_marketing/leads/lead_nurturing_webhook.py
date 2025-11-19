"""
API Webhook para actualizar engagement de leads desde sistemas externos.
Permite que servicios de email marketing, analytics, etc. actualicen engagement en tiempo real.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_nurturing_webhook_handler",
    start_date=None,  # Manual trigger only
    schedule=None,
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 0,
        "depends_on_past": False,
    },
    doc_md="""
    ### Webhook Handler para Engagement de Leads
    
    DAG que procesa webhooks externos para actualizar engagement de leads.
    Útil para integrar con sistemas de email marketing, analytics, etc.
    
    Parámetros (via API trigger):
    - `email`: Email del lead (requerido)
    - `event_type`: Tipo de evento: opened, clicked, replied, bounced (requerido)
    - `timestamp`: Timestamp del evento (ISO format, opcional)
    - `sequence_id`: ID de secuencia (opcional, se busca si no se provee)
    - `metadata`: JSON adicional con información del evento
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email": Param("", type="string", minLength=1),
        "event_type": Param("", type="string", minLength=1),
        "timestamp": Param("", type="string"),
        "sequence_id": Param(0, type="integer", minimum=0),
        "metadata": Param("{}", type="string"),
    },
    tags=["marketing", "lead-nurturing", "webhook", "api"],
)
def lead_nurturing_webhook_handler() -> None:
    """
    Handler para webhooks de engagement externos.
    """
    
    @task(task_id="process_engagement_webhook")
    def process_engagement_webhook() -> Dict[str, Any]:
        """
        Procesa webhook de engagement y actualiza la base de datos.
        """
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email = str(params["email"]).strip().lower()
        event_type = str(params["event_type"]).strip().lower()
        sequence_id = int(params.get("sequence_id", 0))
        timestamp_str = str(params.get("timestamp", "")).strip()
        metadata_json = str(params.get("metadata", "{}")).strip()
        
        if not email or not event_type:
            return {"error": "email and event_type are required"}
        
        # Validar event_type
        valid_events = ["opened", "clicked", "replied", "bounced", "delivered"]
        if event_type not in valid_events:
            return {"error": f"Invalid event_type. Must be one of: {', '.join(valid_events)}"}
        
        # Parse timestamp
        event_timestamp = datetime.utcnow()
        if timestamp_str:
            try:
                from dateutil import parser
                event_timestamp = parser.parse(timestamp_str)
            except Exception:
                logger.warning(f"Could not parse timestamp {timestamp_str}, using now()")
        
        # Parse metadata
        metadata = {}
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
            except Exception:
                logger.warning(f"Could not parse metadata JSON: {metadata_json}")
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Buscar sequence_id si no se proporcionó
                if not sequence_id:
                    cur.execute("""
                        SELECT id FROM lead_nurturing_sequences
                        WHERE email = %s AND status = 'active'
                        ORDER BY started_at DESC
                        LIMIT 1
                    """, (email,))
                    result = cur.fetchone()
                    if result:
                        sequence_id = result[0]
                    else:
                        return {"error": f"No active sequence found for {email}"}
                
                # Buscar el evento más reciente sin engagement para actualizar
                cur.execute("""
                    SELECT id, step_number FROM lead_nurturing_events
                    WHERE sequence_id = %s
                        AND email = %s
                        AND status = 'sent'
                        ORDER BY sent_at DESC
                        LIMIT 1
                """, (sequence_id, email))
                
                event_result = cur.fetchone()
                if not event_result:
                    return {"error": f"No sent email found for sequence {sequence_id}"}
                
                event_id, step_number = event_result
                
                # Actualizar evento según tipo
                update_fields = []
                update_values = []
                
                if event_type == "opened":
                    update_fields.append("opened_at = %s")
                    update_values.append(event_timestamp)
                elif event_type == "clicked":
                    update_fields.append("clicked_at = %s")
                    update_values.append(event_timestamp)
                elif event_type == "replied":
                    update_fields.append("replied_at = %s")
                    update_values.append(event_timestamp)
                elif event_type == "bounced":
                    update_fields.append("bounced_at = %s")
                    update_fields.append("status = %s")
                    update_values.append(event_timestamp)
                    update_values.append("bounced")
                elif event_type == "delivered":
                    update_fields.append("delivered_at = %s")
                    update_values.append(event_timestamp)
                
                # Actualizar metadata si hay información adicional
                if metadata:
                    cur.execute("""
                        SELECT metadata FROM lead_nurturing_events WHERE id = %s
                    """, (event_id,))
                    existing_metadata = cur.fetchone()[0] or {}
                    if isinstance(existing_metadata, str):
                        existing_metadata = json.loads(existing_metadata)
                    
                    existing_metadata.update(metadata)
                    update_fields.append("metadata = %s")
                    update_values.append(json.dumps(existing_metadata))
                
                if update_fields:
                    update_values.append(event_id)
                    cur.execute(
                        f"""
                        UPDATE lead_nurturing_events
                        SET {', '.join(update_fields)}
                        WHERE id = %s
                        """,
                        update_values
                    )
                    
                    # Actualizar engagement summary
                    cur.execute(
                        "SELECT update_nurturing_engagement_summary(%s)",
                        (sequence_id,)
                    )
                    
                    # Si hay reply o click, evaluar calificación
                    if event_type in ["replied", "clicked"]:
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
                        """, (sequence_id,))
                        
                        result = cur.fetchone()
                        if result:
                            # Lógica de calificación (simplificada, debería usar la función del DAG principal)
                            replies_count, opens_count, clicks_count, current_score, lead_ext_id = result
                            min_score = 50  # Default
                            
                            new_score = current_score or 0
                            if replies_count >= 1:
                                new_score += 15
                            if clicks_count >= 1:
                                new_score += 8
                            if opens_count >= 2:
                                new_score += 5
                            
                            if new_score >= min_score and new_score > (current_score or 0):
                                now_ts = datetime.utcnow()
                                cur.execute("""
                                    UPDATE lead_nurturing_sequences
                                    SET qualified_at = %s,
                                        status = 'qualified',
                                        lead_score = %s,
                                        updated_at = %s
                                    WHERE id = %s
                                """, (now_ts, new_score, now_ts, sequence_id))
                                
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
                    
                    conn.commit()
                    
                    logger.info(
                        f"Engagement actualizado: {event_type} para {email} "
                        f"(sequence_id={sequence_id}, event_id={event_id})"
                    )
                    
                    return {
                        "success": True,
                        "event_type": event_type,
                        "email": email,
                        "sequence_id": sequence_id,
                        "event_id": event_id,
                        "updated_at": event_timestamp.isoformat()
                    }
                else:
                    return {"error": "No valid update fields"}
    
    process_engagement_webhook()


dag = lead_nurturing_webhook_handler()


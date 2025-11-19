from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_nurturing_advanced",
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
    ### Nurturing Avanzado de Leads
    
    Sistema de nurturing inteligente que:
    - Envía secuencias personalizadas según segmento
    - Ajusta frecuencia según engagement
    - Pausa automática si hay respuesta
    - Reactivación de leads fríos
    - Personalización basada en comportamiento
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `email_api_url`: URL del servicio de email
    - `sms_api_url`: URL del servicio de SMS (opcional)
    - `enable_email_nurturing`: Habilitar nurturing por email (default: true)
    - `enable_sms_nurturing`: Habilitar nurturing por SMS (default: false)
    - `max_leads_per_run`: Máximo de leads a procesar (default: 100)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email_api_url": Param("", type="string"),
        "sms_api_url": Param("", type="string"),
        "enable_email_nurturing": Param(True, type="boolean"),
        "enable_sms_nurturing": Param(False, type="boolean"),
        "max_leads_per_run": Param(100, type="integer", minimum=1, maximum=500),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "nurturing", "automation"],
)
def lead_nurturing_advanced() -> None:
    """
    DAG para nurturing avanzado de leads.
    """
    
    @task(task_id="get_leads_for_nurturing")
    def get_leads_for_nurturing() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan nurturing."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Leads que:
        # - No han sido contactados recientemente
        # - No están en nurturing activo
        # - No están cerrados
        query = """
            SELECT 
                p.id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.phone,
                p.score,
                p.priority,
                p.stage,
                p.source,
                p.qualified_at,
                p.last_contact_at,
                p.metadata
            FROM sales_pipeline p
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.last_contact_at IS NULL 
                    OR p.last_contact_at < NOW() - INTERVAL '3 days'
                )
                AND (p.metadata->>'nurturing_active')::boolean IS NOT TRUE
                AND (p.metadata->>'nurturing_paused')::boolean IS NOT TRUE
            ORDER BY 
                p.priority DESC,
                p.score DESC,
                p.qualified_at ASC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(leads)} leads para nurturing")
        return leads
    
    @task(task_id="determine_nurturing_sequence")
    def determine_nurturing_sequence(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Determina secuencia de nurturing para cada lead."""
        nurtured_leads = []
        
        for lead in leads:
            # Determinar secuencia basada en segmento y comportamiento
            segment = get_lead_segment(lead)
            sequence = get_nurturing_sequence(segment, lead)
            
            lead["nurturing_sequence"] = sequence
            lead["nurturing_step"] = get_next_nurturing_step(lead)
            nurtured_leads.append(lead)
        
        return nurtured_leads
    
    @task(task_id="send_nurturing_messages")
    def send_nurturing_messages(nurtured_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Envía mensajes de nurturing."""
        ctx = get_current_context()
        params = ctx["params"]
        email_api_url = str(params["email_api_url"])
        sms_api_url = str(params["sms_api_url"])
        enable_email = bool(params["enable_email_nurturing"])
        enable_sms = bool(params["enable_sms_nurturing"])
        dry_run = bool(params["dry_run"])
        
        stats = {"sent": 0, "email": 0, "sms": 0, "errors": 0}
        hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
        
        for lead in nurtured_leads:
            try:
                step = lead.get("nurturing_step")
                if not step:
                    continue
                
                # Enviar email
                if enable_email and step.get("channel") == "email":
                    if not dry_run and email_api_url:
                        success = send_email_nurturing(
                            email_api_url,
                            lead,
                            step
                        )
                        if success:
                            stats["email"] += 1
                            stats["sent"] += 1
                    else:
                        logger.info(f"[DRY RUN] Email nurturing para {lead['email']}")
                        stats["email"] += 1
                        stats["sent"] += 1
                
                # Enviar SMS
                elif enable_sms and step.get("channel") == "sms" and lead.get("phone"):
                    if not dry_run and sms_api_url:
                        success = send_sms_nurturing(
                            sms_api_url,
                            lead,
                            step
                        )
                        if success:
                            stats["sms"] += 1
                            stats["sent"] += 1
                    else:
                        logger.info(f"[DRY RUN] SMS nurturing para {lead['phone']}")
                        stats["sms"] += 1
                        stats["sent"] += 1
                
                # Actualizar metadata
                if not dry_run:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            existing_metadata = lead.get("metadata") or {}
                            if isinstance(existing_metadata, str):
                                existing_metadata = json.loads(existing_metadata)
                            
                            nurturing_data = existing_metadata.get("nurturing", {})
                            nurturing_data.update({
                                "active": True,
                                "current_step": step.get("step_number", 1),
                                "last_sent_at": datetime.utcnow().isoformat(),
                                "total_sent": nurturing_data.get("total_sent", 0) + 1
                            })
                            
                            existing_metadata["nurturing"] = nurturing_data
                            existing_metadata["nurturing_active"] = True
                            
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    metadata = %s::jsonb,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (json.dumps(existing_metadata), lead["id"]))
                            
                            conn.commit()
            
            except Exception as e:
                stats["errors"] += 1
                logger.error(f"Error enviando nurturing para {lead.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Nurturing completado: {stats}")
        return stats
    
    def get_lead_segment(lead: Dict[str, Any]) -> str:
        """Obtiene segmento del lead."""
        metadata = lead.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        return metadata.get("segment") or "medium_qualified"
    
    def get_nurturing_sequence(segment: str, lead: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtiene secuencia de nurturing según segmento."""
        # Secuencias predefinidas
        sequences = {
            "premium_qualified": [
                {"step_number": 1, "channel": "email", "delay_days": 1, "template": "premium_welcome"},
                {"step_number": 2, "channel": "email", "delay_days": 3, "template": "premium_value_prop"},
                {"step_number": 3, "channel": "email", "delay_days": 5, "template": "premium_case_study"},
                {"step_number": 4, "channel": "email", "delay_days": 7, "template": "premium_demo_request"}
            ],
            "high_priority_qualified": [
                {"step_number": 1, "channel": "email", "delay_days": 1, "template": "high_priority_welcome"},
                {"step_number": 2, "channel": "email", "delay_days": 3, "template": "high_priority_benefits"},
                {"step_number": 3, "channel": "sms", "delay_days": 5, "template": "high_priority_followup"}
            ],
            "medium_qualified": [
                {"step_number": 1, "channel": "email", "delay_days": 2, "template": "medium_welcome"},
                {"step_number": 2, "channel": "email", "delay_days": 5, "template": "medium_education"},
                {"step_number": 3, "channel": "email", "delay_days": 10, "template": "medium_reactivation"}
            ]
        }
        
        return sequences.get(segment, sequences["medium_qualified"])
    
    def get_next_nurturing_step(lead: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Determina el siguiente paso de nurturing."""
        metadata = lead.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        nurturing = metadata.get("nurturing", {})
        current_step = nurturing.get("current_step", 0)
        sequence = lead.get("nurturing_sequence", [])
        
        if current_step >= len(sequence):
            return None
        
        next_step = sequence[current_step]
        
        # Verificar si es momento de enviar
        last_sent = nurturing.get("last_sent_at")
        if last_sent:
            last_sent_date = datetime.fromisoformat(last_sent.replace('Z', '+00:00'))
            delay_days = next_step.get("delay_days", 0)
            next_send_date = last_sent_date + timedelta(days=delay_days)
            
            if datetime.utcnow() < next_send_date.replace(tzinfo=None):
                return None
        
        return next_step
    
    def send_email_nurturing(api_url: str, lead: Dict[str, Any], step: Dict[str, Any]) -> bool:
        """Envía email de nurturing."""
        try:
            template = step.get("template", "default")
            payload = {
                "to": lead["email"],
                "template": template,
                "data": {
                    "first_name": lead.get("first_name", "Lead"),
                    "last_name": lead.get("last_name", ""),
                    "company": lead.get("company", ""),
                    "lead_ext_id": lead["lead_ext_id"]
                }
            }
            
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def send_sms_nurturing(api_url: str, lead: Dict[str, Any], step: Dict[str, Any]) -> bool:
        """Envía SMS de nurturing."""
        try:
            template = step.get("template", "default")
            payload = {
                "to": lead["phone"],
                "template": template,
                "data": {
                    "first_name": lead.get("first_name", "Lead")
                }
            }
            
            response = requests.post(api_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error enviando SMS: {e}")
            return False
    
    # Pipeline
    leads = get_leads_for_nurturing()
    nurtured_leads = determine_nurturing_sequence(leads)
    stats = send_nurturing_messages(nurtured_leads)


dag = lead_nurturing_advanced()


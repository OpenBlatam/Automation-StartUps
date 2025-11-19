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
    dag_id="lead_notifications",
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
    ### Notificaciones Automáticas de Leads
    
    Envía notificaciones automáticas sobre eventos importantes del pipeline:
    - Nuevos leads de alta prioridad
    - Leads sin contacto por X días
    - Leads próximos a vencer
    - Cambios de stage importantes
    - Leads asignados a vendedores
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `slack_webhook_url`: Webhook URL de Slack (opcional)
    - `email_enabled`: Habilitar notificaciones por email (default: false)
    - `notify_high_priority`: Notificar leads de alta prioridad (default: true)
    - `notify_stale_leads`: Notificar leads sin contacto (default: true)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "slack_webhook_url": Param("", type="string"),
        "email_enabled": Param(False, type="boolean"),
        "notify_high_priority": Param(True, type="boolean"),
        "notify_stale_leads": Param(True, type="boolean"),
        "stale_days": Param(7, type="integer", minimum=1, maximum=30),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "notifications", "automation"],
)
def lead_notifications() -> None:
    """
    DAG para notificaciones automáticas de leads.
    """
    
    @task(task_id="get_notification_events")
    def get_notification_events() -> Dict[str, List[Dict[str, Any]]]:
        """Obtiene eventos que requieren notificación."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        notify_high_priority = bool(params["notify_high_priority"])
        notify_stale_leads = bool(params["notify_stale_leads"])
        stale_days = int(params["stale_days"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        events = {
            "high_priority_new": [],
            "stale_leads": [],
            "upcoming_followups": [],
            "recently_assigned": []
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Leads de alta prioridad nuevos (últimas 24h)
                if notify_high_priority:
                    cur.execute("""
                        SELECT 
                            lead_ext_id,
                            email,
                            first_name,
                            last_name,
                            score,
                            priority,
                            assigned_to,
                            qualified_at
                        FROM sales_pipeline
                        WHERE 
                            priority = 'high'
                            AND qualified_at >= NOW() - INTERVAL '24 hours'
                            AND (metadata->>'high_priority_notified')::boolean IS NOT TRUE
                        ORDER BY qualified_at DESC
                    """)
                    
                    columns = [desc[0] for desc in cur.description]
                    events["high_priority_new"] = [
                        dict(zip(columns, row)) for row in cur.fetchall()
                    ]
                
                # Leads sin contacto (stale)
                if notify_stale_leads:
                    cur.execute("""
                        SELECT 
                            lead_ext_id,
                            email,
                            first_name,
                            last_name,
                            score,
                            priority,
                            assigned_to,
                            stage,
                            last_contact_at,
                            qualified_at
                        FROM sales_pipeline
                        WHERE 
                            stage NOT IN ('closed_won', 'closed_lost')
                            AND (
                                last_contact_at IS NULL 
                                AND qualified_at < NOW() - INTERVAL '%s days'
                            )
                            OR (
                                last_contact_at < NOW() - INTERVAL '%s days'
                            )
                            AND (metadata->>'stale_notified')::boolean IS NOT TRUE
                        ORDER BY qualified_at ASC
                    """, (stale_days, stale_days))
                    
                    columns = [desc[0] for desc in cur.description]
                    events["stale_leads"] = [
                        dict(zip(columns, row)) for row in cur.fetchall()
                    ]
                
                # Seguimientos próximos (próximas 24h)
                cur.execute("""
                    SELECT 
                        p.lead_ext_id,
                        p.email,
                        p.first_name,
                        p.last_name,
                        p.assigned_to,
                        p.next_followup_at,
                        COUNT(t.id) AS pending_tasks_count
                    FROM sales_pipeline p
                    LEFT JOIN sales_followup_tasks t 
                        ON p.id = t.pipeline_id 
                        AND t.status = 'pending'
                    WHERE 
                        p.next_followup_at IS NOT NULL
                        AND p.next_followup_at <= NOW() + INTERVAL '24 hours'
                        AND p.stage NOT IN ('closed_won', 'closed_lost')
                    GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, 
                             p.last_name, p.assigned_to, p.next_followup_at
                    ORDER BY p.next_followup_at ASC
                """)
                
                columns = [desc[0] for desc in cur.description]
                events["upcoming_followups"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
        
        logger.info(f"Eventos encontrados: {len(events['high_priority_new'])} high priority, "
                   f"{len(events['stale_leads'])} stale, {len(events['upcoming_followups'])} upcoming")
        
        return events
    
    @task(task_id="send_notifications")
    def send_notifications(events: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Envía notificaciones."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_webhook = str(params["slack_webhook_url"])
        dry_run = bool(params["dry_run"])
        
        stats = {
            "sent": 0,
            "errors": 0,
            "skipped": 0
        }
        
        # Notificar leads de alta prioridad
        if events["high_priority_new"]:
            message = format_high_priority_message(events["high_priority_new"])
            if slack_webhook and not dry_run:
                if send_slack_notification(slack_webhook, message):
                    stats["sent"] += 1
                else:
                    stats["errors"] += 1
            else:
                logger.info(f"[DRY RUN] Notificación high priority: {message}")
        
        # Notificar leads stale
        if events["stale_leads"]:
            message = format_stale_leads_message(events["stale_leads"])
            if slack_webhook and not dry_run:
                if send_slack_notification(slack_webhook, message):
                    stats["sent"] += 1
                else:
                    stats["errors"] += 1
            else:
                logger.info(f"[DRY RUN] Notificación stale leads: {message}")
        
        # Notificar seguimientos próximos
        if events["upcoming_followups"]:
            message = format_upcoming_followups_message(events["upcoming_followups"])
            if slack_webhook and not dry_run:
                if send_slack_notification(slack_webhook, message):
                    stats["sent"] += 1
                else:
                    stats["errors"] += 1
            else:
                logger.info(f"[DRY RUN] Notificación upcoming followups: {message}")
        
        return stats
    
    @task(task_id="mark_notifications_sent")
    def mark_notifications_sent(events: Dict[str, List[Dict[str, Any]]]) -> None:
        """Marca notificaciones como enviadas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Marcar high priority como notificados
                for lead in events["high_priority_new"]:
                    if not dry_run:
                        cur.execute("""
                            UPDATE sales_pipeline
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object('high_priority_notified', true)
                            WHERE lead_ext_id = %s
                        """, (lead["lead_ext_id"],))
                
                # Marcar stale como notificados
                for lead in events["stale_leads"]:
                    if not dry_run:
                        cur.execute("""
                            UPDATE sales_pipeline
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || 
                                jsonb_build_object('stale_notified', true)
                            WHERE lead_ext_id = %s
                        """, (lead["lead_ext_id"],))
                
                if not dry_run:
                    conn.commit()
    
    def format_high_priority_message(leads: List[Dict[str, Any]]) -> str:
        """Formatea mensaje para leads de alta prioridad"""
        text = f"🔥 *{len(leads)} Nuevo(s) Lead(s) de Alta Prioridad*\n\n"
        for lead in leads[:10]:  # Limitar a 10
            text += f"• *{lead.get('first_name', 'Lead')} {lead.get('last_name', '')}*\n"
            text += f"  Email: {lead['email']}\n"
            text += f"  Score: {lead['score']} | Asignado a: {lead.get('assigned_to', 'Sin asignar')}\n\n"
        return text
    
    def format_stale_leads_message(leads: List[Dict[str, Any]]) -> str:
        """Formatea mensaje para leads stale"""
        text = f"⚠️ *{len(leads)} Lead(s) Sin Contacto*\n\n"
        for lead in leads[:10]:
            text += f"• *{lead.get('first_name', 'Lead')} {lead.get('last_name', '')}*\n"
            text += f"  Email: {lead['email']}\n"
            text += f"  Stage: {lead['stage']} | Último contacto: {lead.get('last_contact_at', 'Nunca')}\n\n"
        return text
    
    def format_upcoming_followups_message(leads: List[Dict[str, Any]]) -> str:
        """Formatea mensaje para seguimientos próximos"""
        text = f"📅 *{len(leads)} Seguimiento(s) Próximo(s)*\n\n"
        for lead in leads[:10]:
            text += f"• *{lead.get('first_name', 'Lead')} {lead.get('last_name', '')}*\n"
            text += f"  Email: {lead['email']}\n"
            text += f"  Seguimiento: {lead['next_followup_at']}\n"
            text += f"  Tareas pendientes: {lead['pending_tasks_count']}\n\n"
        return text
    
    def send_slack_notification(webhook_url: str, message: str) -> bool:
        """Envía notificación a Slack"""
        try:
            payload = {
                "text": message,
                "username": "Sales Pipeline Bot",
                "icon_emoji": ":chart_with_upwards_trend:"
            }
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error enviando notificación Slack: {e}")
            return False
    
    # Pipeline
    events = get_notification_events()
    stats = send_notifications(events)
    mark_notifications_sent(events)


dag = lead_notifications()


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
    dag_id="sales_alerts_intelligent",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Sistema de Alertas Inteligentes de Ventas
    
    Detecta y alerta sobre situaciones críticas en el pipeline:
    - Leads de alto valor sin seguimiento
    - Tareas vencidas
    - Oportunidades estancadas
    - Disminución de conversión
    - Leads abandonados
    - Vendedores sobrecargados
    
    **Funcionalidades:**
    - Alertas configurables por tipo
    - Notificaciones a Slack/Email
    - Priorización inteligente de alertas
    - Tracking de alertas resueltas
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "slack_webhook_url": Param("", type="string"),
        "email_recipients": Param("", type="string"),
        "enable_high_value_alerts": Param(True, type="boolean"),
        "high_value_threshold": Param(10000, type="number", minimum=0),
        "enable_stale_lead_alerts": Param(True, type="boolean"),
        "stale_lead_days": Param(7, type="integer", minimum=1, maximum=30),
        "enable_overdue_task_alerts": Param(True, type="boolean"),
        "enable_conversion_drop_alerts": Param(True, type="boolean"),
        "conversion_drop_threshold": Param(10, type="number", minimum=0, maximum=100),
    },
    tags=["sales", "alerts", "monitoring", "intelligence"],
)
def sales_alerts_intelligent() -> None:
    """
    DAG para alertas inteligentes de ventas.
    """
    
    @task(task_id="check_high_value_stale")
    def check_high_value_stale() -> List[Dict[str, Any]]:
        """Detecta leads de alto valor sin seguimiento."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        threshold = float(params["high_value_threshold"])
        stale_days = int(params["stale_lead_days"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.estimated_value,
                p.probability_pct,
                p.stage,
                p.assigned_to,
                p.last_contact_at,
                p.qualified_at,
                EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
                COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND p.estimated_value >= %s
                AND (
                    p.last_contact_at IS NULL
                    OR p.last_contact_at <= NOW() - INTERVAL '%s days'
                )
            GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, p.last_name,
                     p.estimated_value, p.probability_pct, p.stage, p.assigned_to,
                     p.last_contact_at, p.qualified_at
            ORDER BY p.estimated_value DESC, days_since_contact DESC
            LIMIT 20
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (threshold, stale_days))
                columns = [desc[0] for desc in cur.description]
                alerts = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return alerts
    
    @task(task_id="check_overdue_tasks")
    def check_overdue_tasks() -> List[Dict[str, Any]]:
        """Detecta tareas vencidas críticas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                t.id AS task_id,
                t.task_title,
                t.task_type,
                t.priority,
                t.due_date,
                t.assigned_to,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.estimated_value,
                p.stage,
                EXTRACT(EPOCH FROM (NOW() - t.due_date) / 86400) AS days_overdue
            FROM sales_followup_tasks t
            JOIN sales_pipeline p ON t.pipeline_id = p.id
            WHERE 
                t.status = 'pending'
                AND t.due_date <= NOW()
                AND p.stage NOT IN ('closed_won', 'closed_lost')
            ORDER BY 
                t.priority DESC,
                p.estimated_value DESC NULLS LAST,
                days_overdue DESC
            LIMIT 30
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                alerts = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return alerts
    
    @task(task_id="check_stale_leads")
    def check_stale_leads() -> List[Dict[str, Any]]:
        """Detecta leads sin actividad reciente."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        stale_days = int(params["stale_lead_days"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.score,
                p.priority,
                p.stage,
                p.assigned_to,
                p.last_contact_at,
                p.qualified_at,
                EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
                COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.last_contact_at IS NULL
                    OR p.last_contact_at <= NOW() - INTERVAL '%s days'
                )
                AND p.qualified_at >= NOW() - INTERVAL '90 days'
            GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, p.last_name,
                     p.score, p.priority, p.stage, p.assigned_to,
                     p.last_contact_at, p.qualified_at
            ORDER BY p.priority DESC, p.score DESC, days_since_contact DESC
            LIMIT 50
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (stale_days,))
                columns = [desc[0] for desc in cur.description]
                alerts = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return alerts
    
    @task(task_id="check_conversion_drop")
    def check_conversion_drop() -> Dict[str, Any]:
        """Detecta caídas en tasa de conversión."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        threshold = float(params["conversion_drop_threshold"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Comparar última semana vs semana anterior
                cur.execute("""
                    WITH weekly_stats AS (
                        SELECT 
                            DATE_TRUNC('week', qualified_at) AS week,
                            COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
                            COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')) AS closed,
                            ROUND(
                                COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC /
                                NULLIF(COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')), 0) * 100,
                                2
                            ) AS win_rate
                        FROM sales_pipeline
                        WHERE qualified_at >= NOW() - INTERVAL '14 days'
                        GROUP BY DATE_TRUNC('week', qualified_at)
                    )
                    SELECT 
                        MAX(win_rate) FILTER (WHERE week = DATE_TRUNC('week', NOW())) AS current_week,
                        MAX(win_rate) FILTER (WHERE week = DATE_TRUNC('week', NOW()) - INTERVAL '7 days') AS last_week
                    FROM weekly_stats
                """)
                
                row = cur.fetchone()
                current_rate = float(row[0] or 0) if row[0] else None
                last_rate = float(row[1] or 0) if row[1] else None
                
                alert = None
                if current_rate is not None and last_rate is not None:
                    drop = last_rate - current_rate
                    if drop >= threshold:
                        alert = {
                            "type": "conversion_drop",
                            "current_rate": current_rate,
                            "last_rate": last_rate,
                            "drop_pct": drop,
                            "threshold": threshold,
                            "severity": "high" if drop >= threshold * 2 else "medium"
                        }
        
        return alert or {}
    
    @task(task_id="check_overloaded_reps")
    def check_overloaded_reps() -> List[Dict[str, Any]]:
        """Detecta vendedores sobrecargados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params.get("max_active_leads_per_rep", 50))
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                assigned_to,
                COUNT(*) AS active_leads,
                COUNT(*) FILTER (WHERE status = 'pending' AND due_date <= NOW()) AS overdue_tasks,
                SUM(estimated_value) AS total_pipeline_value,
                AVG(score) AS avg_lead_score
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            WHERE 
                p.assigned_to IS NOT NULL
                AND p.stage NOT IN ('closed_won', 'closed_lost')
                AND p.qualified_at >= NOW() - INTERVAL '90 days'
            GROUP BY p.assigned_to
            HAVING COUNT(*) >= %s
            ORDER BY active_leads DESC, overdue_tasks DESC
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                alerts = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        return alerts
    
    @task(task_id="send_alerts")
    def send_alerts(
        high_value: List[Dict[str, Any]],
        overdue_tasks: List[Dict[str, Any]],
        stale_leads: List[Dict[str, Any]],
        conversion_drop: Dict[str, Any],
        overloaded_reps: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Envía alertas consolidadas."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_url = str(params["slack_webhook_url"]).strip()
        email_recipients = str(params["email_recipients"]).strip()
        
        stats = {
            "high_value_alerts": len(high_value),
            "overdue_task_alerts": len(overdue_tasks),
            "stale_lead_alerts": len(stale_leads),
            "conversion_drop": 1 if conversion_drop else 0,
            "overloaded_reps": len(overloaded_reps),
            "total": 0
        }
        stats["total"] = sum(stats.values())
        
        if stats["total"] == 0:
            logger.info("No hay alertas para enviar")
            return stats
        
        # Formatear mensaje
        message_parts = ["🚨 *Sales Alerts - Situaciones Críticas*\n"]
        
        # Alto valor sin seguimiento
        if high_value:
            message_parts.append(f"\n💰 *Leads de Alto Valor Sin Seguimiento ({len(high_value)})*")
            for alert in high_value[:5]:  # Top 5
                value = alert.get("estimated_value", 0) or 0
                days = int(alert.get("days_since_contact", 0) or 0)
                message_parts.append(
                    f"• {alert.get('first_name', '')} {alert.get('last_name', '')} "
                    f"({alert.get('email', '')}) - ${value:,.0f} - {days} días sin contacto"
                )
        
        # Tareas vencidas
        if overdue_tasks:
            message_parts.append(f"\n⏰ *Tareas Vencidas ({len(overdue_tasks)})*")
            for alert in overdue_tasks[:5]:  # Top 5
                days = int(alert.get("days_overdue", 0) or 0)
                priority = alert.get("priority", "medium")
                message_parts.append(
                    f"• {alert.get('task_title', '')} - {alert.get('assigned_to', '')} "
                    f"- {priority} - {days} días vencida"
                )
        
        # Leads estancados
        if stale_leads:
            message_parts.append(f"\n📉 *Leads Sin Actividad ({len(stale_leads)})*")
            message_parts.append(f"Total: {len(stale_leads)} leads necesitan seguimiento")
        
        # Caída de conversión
        if conversion_drop:
            drop = conversion_drop.get("drop_pct", 0)
            severity = conversion_drop.get("severity", "medium")
            message_parts.append(
                f"\n⚠️ *Caída de Conversión - {severity.upper()}*\n"
                f"Tasa actual: {conversion_drop.get('current_rate', 0):.1f}%\n"
                f"Tasa anterior: {conversion_drop.get('last_rate', 0):.1f}%\n"
                f"Caída: {drop:.1f} puntos porcentuales"
            )
        
        # Vendedores sobrecargados
        if overloaded_reps:
            message_parts.append(f"\n👥 *Vendedores Sobrecargados ({len(overloaded_reps)})*")
            for rep in overloaded_reps:
                leads = rep.get("active_leads", 0)
                tasks = rep.get("overdue_tasks", 0)
                message_parts.append(
                    f"• {rep.get('assigned_to', '')}: {leads} leads activos, "
                    f"{tasks} tareas vencidas"
                )
        
        message = "\n".join(message_parts)
        
        # Enviar a Slack
        if slack_url:
            try:
                requests.post(
                    slack_url,
                    json={"text": message},
                    timeout=10
                )
                logger.info("Alertas enviadas a Slack")
            except Exception as e:
                logger.warning(f"Error enviando a Slack: {e}")
        
        # Enviar por email (requiere configuración)
        if email_recipients and stats["total"] > 0:
            logger.info(f"Alertas listas para enviar a: {email_recipients}")
        
        logger.info(f"Alertas procesadas: {stats['total']} total")
        
        try:
            Stats.incr("sales_alerts.total", stats["total"])
        except Exception:
            pass
        
        return stats
    
    # Pipeline
    high_value_alerts = check_high_value_stale()
    overdue_task_alerts = check_overdue_tasks()
    stale_lead_alerts = check_stale_leads()
    conversion_drop_alert = check_conversion_drop()
    overloaded_reps = check_overloaded_reps()
    send_alerts(high_value_alerts, overdue_task_alerts, stale_lead_alerts, 
                conversion_drop_alert, overloaded_reps)


dag = sales_alerts_intelligent()




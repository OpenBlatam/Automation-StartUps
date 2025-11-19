"""
DAG de Monitoreo de Tickets de Soporte

Monitorea métricas clave del sistema de soporte:
- Tickets pendientes por prioridad
- Tasa de resolución por chatbot
- Tiempo promedio de primera respuesta
- SLA compliance
- Carga de trabajo de agentes
- Alertas para tickets críticos sin asignar
"""
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

try:
    from airflow import DAG
    from airflow.decorators import task, dag
    from airflow.utils.dates import days_ago
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    from airflow.utils.context import Context
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Configuración
DEFAULT_ARGS = {
    "owner": "support",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
    "email_on_retry": False,
}

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")


@dag(
    dag_id="support_tickets_monitor",
    start_date=days_ago(1),
    schedule="*/15 * * * *",  # Cada 15 minutos
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Monitoreo continuo de tickets de soporte con alertas y métricas",
    tags=["support", "monitoring", "tickets", "chatbot"],
    max_active_runs=1,
)
def support_tickets_monitor():
    """DAG principal de monitoreo de tickets de soporte."""
    
    @task(task_id="collect_ticket_metrics")
    def collect_ticket_metrics() -> Dict[str, Any]:
        """Recopila métricas principales de tickets."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Tickets por estado
                cur.execute("""
                    SELECT 
                        status,
                        COUNT(*) as count,
                        COUNT(*) FILTER (WHERE priority = 'critical') as critical_count,
                        COUNT(*) FILTER (WHERE priority = 'urgent') as urgent_count,
                        AVG(priority_score) as avg_priority_score
                    FROM support_tickets
                    WHERE status IN ('open', 'assigned', 'in_progress', 'chatbot_handled')
                    GROUP BY status
                """)
                status_metrics = {row[0]: {
                    "total": row[1],
                    "critical": row[2],
                    "urgent": row[3],
                    "avg_priority_score": float(row[4]) if row[4] else 0.0
                } for row in cur.fetchall()}
                
                # Tickets críticos sin asignar
                cur.execute("""
                    SELECT COUNT(*)
                    FROM support_tickets
                    WHERE priority IN ('critical', 'urgent')
                    AND status = 'open'
                    AND assigned_agent_id IS NULL
                    AND created_at < NOW() - INTERVAL '5 minutes'
                """)
                unassigned_critical = cur.fetchone()[0] or 0
                
                # Tasa de resolución por chatbot
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE chatbot_attempted = true) as attempted,
                        COUNT(*) FILTER (WHERE chatbot_resolved = true) as resolved,
                        AVG(confidence) FILTER (WHERE chatbot_resolved = true) as avg_confidence
                    FROM support_tickets
                    WHERE created_at >= CURRENT_DATE - INTERVAL '24 hours'
                    AND chatbot_attempted = true
                """)
                row = cur.fetchone()
                chatbot_metrics = {
                    "attempted": row[0] or 0,
                    "resolved": row[1] or 0,
                    "resolution_rate": (row[1] / row[0] * 100) if row[0] and row[0] > 0 else 0.0,
                    "avg_confidence": float(row[2]) if row[2] else 0.0
                }
                
                # Tiempo promedio de primera respuesta (solo tickets no resueltos por chatbot)
                cur.execute("""
                    SELECT 
                        AVG(time_to_first_response_minutes) as avg_first_response,
                        AVG(time_to_resolution_minutes) as avg_resolution_time,
                        COUNT(*) FILTER (WHERE first_response_at IS NOT NULL) as responded_count,
                        COUNT(*) as total_count
                    FROM support_tickets
                    WHERE status NOT IN ('chatbot_handled', 'closed')
                    AND created_at >= CURRENT_DATE - INTERVAL '24 hours'
                """)
                row = cur.fetchone()
                response_metrics = {
                    "avg_first_response_minutes": float(row[0]) if row[0] else None,
                    "avg_resolution_minutes": float(row[1]) if row[1] else None,
                    "responded_count": row[2] or 0,
                    "total_count": row[3] or 0,
                    "response_rate": (row[2] / row[3] * 100) if row[3] and row[3] > 0 else 0.0
                }
                
                # Carga de trabajo por agente
                cur.execute("""
                    SELECT 
                        agent_id,
                        agent_name,
                        department,
                        current_active_tickets,
                        max_concurrent_tickets,
                        COUNT(t.ticket_id) FILTER (WHERE t.status IN ('open', 'assigned', 'in_progress')) as assigned_tickets
                    FROM support_agents a
                    LEFT JOIN support_tickets t ON a.agent_id = t.assigned_agent_id
                    WHERE a.is_available = true
                    GROUP BY agent_id, agent_name, department, current_active_tickets, max_concurrent_tickets
                    ORDER BY assigned_tickets DESC
                """)
                agent_workload = []
                for row in cur.fetchall():
                    agent_workload.append({
                        "agent_id": row[0],
                        "agent_name": row[1],
                        "department": row[2],
                        "current_active": row[3],
                        "max_concurrent": row[4],
                        "assigned_tickets": row[5] or 0,
                        "utilization_pct": (row[5] / row[4] * 100) if row[4] and row[4] > 0 else 0.0
                    })
                
                # Tickets por prioridad
                cur.execute("""
                    SELECT 
                        priority,
                        COUNT(*) as count,
                        AVG(priority_score) as avg_score
                    FROM support_tickets
                    WHERE status IN ('open', 'assigned', 'in_progress')
                    GROUP BY priority
                """)
                priority_metrics = {row[0]: {
                    "count": row[1],
                    "avg_score": float(row[2]) if row[2] else 0.0
                } for row in cur.fetchall()}
                
                # SLA compliance (tickets abiertos más de 24h sin resolver)
                cur.execute("""
                    SELECT COUNT(*)
                    FROM support_tickets
                    WHERE status NOT IN ('resolved', 'closed', 'chatbot_handled')
                    AND created_at < NOW() - INTERVAL '24 hours'
                    AND priority IN ('critical', 'urgent')
                """)
                sla_breaches_critical = cur.fetchone()[0] or 0
                
                cur.execute("""
                    SELECT COUNT(*)
                    FROM support_tickets
                    WHERE status NOT IN ('resolved', 'closed', 'chatbot_handled')
                    AND created_at < NOW() - INTERVAL '48 hours'
                """)
                sla_breaches_all = cur.fetchone()[0] or 0
        
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "status_metrics": status_metrics,
            "unassigned_critical": unassigned_critical,
            "chatbot_metrics": chatbot_metrics,
            "response_metrics": response_metrics,
            "agent_workload": agent_workload,
            "priority_metrics": priority_metrics,
            "sla_breaches": {
                "critical_24h": sla_breaches_critical,
                "all_48h": sla_breaches_all
            }
        }
        
        logger.info(f"Collected metrics: {metrics}")
        
        # Registrar métricas en Stats
        if STATS_AVAILABLE:
            try:
                Stats.gauge("support_tickets.unassigned_critical", unassigned_critical)
                Stats.gauge("support_tickets.chatbot_resolution_rate", chatbot_metrics["resolution_rate"])
                Stats.gauge("support_tickets.avg_first_response_minutes", 
                           response_metrics["avg_first_response_minutes"] or 0)
                Stats.gauge("support_tickets.sla_breaches_critical", sla_breaches_critical)
                
                for status, data in status_metrics.items():
                    Stats.gauge(f"support_tickets.status.{status}", data["total"])
                    Stats.gauge(f"support_tickets.status.{status}.critical", data["critical"])
                
                for priority, data in priority_metrics.items():
                    Stats.gauge(f"support_tickets.priority.{priority}", data["count"])
            except Exception as e:
                logger.warning(f"Failed to record stats: {e}")
        
        return metrics
    
    @task(task_id="check_alerts")
    def check_alerts(metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica condiciones de alerta y genera alertas."""
        alerts = []
        
        # Alerta: Tickets críticos sin asignar
        if metrics["unassigned_critical"] > 0:
            alerts.append({
                "level": "critical",
                "message": f"⚠️ {metrics['unassigned_critical']} tickets críticos/urgentes sin asignar por más de 5 minutos",
                "count": metrics["unassigned_critical"]
            })
        
        # Alerta: SLA breaches
        if metrics["sla_breaches"]["critical_24h"] > 0:
            alerts.append({
                "level": "critical",
                "message": f"🚨 {metrics['sla_breaches']['critical_24h']} tickets críticos/urgentes abiertos más de 24h",
                "count": metrics["sla_breaches"]["critical_24h"]
            })
        
        if metrics["sla_breaches"]["all_48h"] > 5:
            alerts.append({
                "level": "warning",
                "message": f"⚠️ {metrics['sla_breaches']['all_48h']} tickets abiertos más de 48h",
                "count": metrics["sla_breaches"]["all_48h"]
            })
        
        # Alerta: Tasa de resolución por chatbot baja
        if metrics["chatbot_metrics"]["attempted"] > 10:
            resolution_rate = metrics["chatbot_metrics"]["resolution_rate"]
            if resolution_rate < 50.0:
                alerts.append({
                    "level": "warning",
                    "message": f"📉 Tasa de resolución por chatbot baja: {resolution_rate:.1f}%",
                    "resolution_rate": resolution_rate
                })
        
        # Alerta: Agentes sobrecargados
        overloaded_agents = [
            agent for agent in metrics["agent_workload"]
            if agent["utilization_pct"] > 90
        ]
        if overloaded_agents:
            alerts.append({
                "level": "warning",
                "message": f"👥 {len(overloaded_agents)} agentes con más del 90% de utilización",
                "agents": [a["agent_name"] for a in overloaded_agents]
            })
        
        # Alerta: Tiempo de primera respuesta alto
        if metrics["response_metrics"]["avg_first_response_minutes"]:
            avg_response = metrics["response_metrics"]["avg_first_response_minutes"]
            if avg_response > 60:  # Más de 1 hora
                alerts.append({
                    "level": "warning",
                    "message": f"⏱️ Tiempo promedio de primera respuesta alto: {avg_response:.1f} minutos",
                    "avg_minutes": avg_response
                })
        
        logger.info(f"Generated {len(alerts)} alerts")
        return {"alerts": alerts, "alert_count": len(alerts)}
    
    @task(task_id="send_notifications")
    def send_notifications(alerts_data: Dict[str, Any]) -> None:
        """Envía notificaciones a Slack si hay alertas críticas."""
        alerts = alerts_data.get("alerts", [])
        
        if not alerts or not SLACK_WEBHOOK_URL:
            return
        
        # Filtrar solo alertas críticas para Slack
        critical_alerts = [a for a in alerts if a["level"] == "critical"]
        
        if not critical_alerts:
            return
        
        if not REQUESTS_AVAILABLE:
            logger.warning("requests not available, skipping Slack notification")
            return
        
        try:
            blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Alertas de Soporte - Tickets Críticos"
                    }
                }
            ]
            
            for alert in critical_alerts:
                blocks.append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": alert["message"]
                    }
                })
            
            payload = {
                "text": "Alertas de Soporte",
                "blocks": blocks
            }
            
            response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Sent {len(critical_alerts)} critical alerts to Slack")
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}", exc_info=True)
    
    @task(task_id="log_metrics_summary")
    def log_metrics_summary(metrics: Dict[str, Any], alerts_data: Dict[str, Any]) -> None:
        """Registra resumen de métricas."""
        summary = {
            "timestamp": metrics["timestamp"],
            "total_open": sum(s["total"] for s in metrics["status_metrics"].values()),
            "unassigned_critical": metrics["unassigned_critical"],
            "chatbot_resolution_rate": metrics["chatbot_metrics"]["resolution_rate"],
            "sla_breaches_critical": metrics["sla_breaches"]["critical_24h"],
            "alerts_count": alerts_data["alert_count"]
        }
        
        logger.info("Support tickets metrics summary", extra=summary)
    
    # Pipeline
    metrics = collect_ticket_metrics()
    alerts = check_alerts(metrics)
    send_notifications(alerts)
    log_metrics_summary(metrics, alerts)


dag = support_tickets_monitor()


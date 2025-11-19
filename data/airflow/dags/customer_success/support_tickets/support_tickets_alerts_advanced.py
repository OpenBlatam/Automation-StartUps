"""
DAG de Alertas Avanzadas para Tickets de Soporte

Alertas inteligentes basadas en:
- Patrones de comportamiento
- Tendencias anómalas
- Violaciones de SLA
- Degradación de métricas
- Alertas predictivas
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

DEFAULT_ARGS = {
    "owner": "support",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", "")
PAGERDUTY_INTEGRATION_KEY = os.getenv("PAGERDUTY_INTEGRATION_KEY", "")


@dag(
    dag_id="support_tickets_alerts_advanced",
    start_date=days_ago(1),
    schedule="*/5 * * * *",  # Cada 5 minutos
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Alertas avanzadas e inteligentes para tickets de soporte",
    tags=["support", "alerts", "monitoring"],
)
def support_tickets_alerts_advanced():
    """DAG de alertas avanzadas."""
    
    @task(task_id="detect_anomalies")
    def detect_anomalies() -> Dict[str, Any]:
        """Detecta anomalías en métricas."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        anomalies = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Anomalía: Aumento súbito de tickets
                cur.execute("""
                    WITH hourly_counts AS (
                        SELECT 
                            DATE_TRUNC('hour', created_at) as hour,
                            COUNT(*) as count
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '24 hours'
                        GROUP BY DATE_TRUNC('hour', created_at)
                    ),
                    stats AS (
                        SELECT 
                            AVG(count) as avg_count,
                            STDDEV(count) as stddev_count
                        FROM hourly_counts
                    )
                    SELECT 
                        hc.hour,
                        hc.count,
                        s.avg_count,
                        s.stddev_count
                    FROM hourly_counts hc
                    CROSS JOIN stats s
                    WHERE hc.count > s.avg_count + (s.stddev_count * 2)
                    ORDER BY hc.hour DESC
                    LIMIT 5
                """)
                
                for row in cur.fetchall():
                    anomalies.append({
                        "type": "volume_spike",
                        "hour": row[0],
                        "count": row[1],
                        "avg_count": float(row[2]),
                        "severity": "high"
                    })
                
                # Anomalía: Tasa de resolución por chatbot cayendo
                cur.execute("""
                    WITH recent_rate AS (
                        SELECT 
                            COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
                            NULLIF(COUNT(*) FILTER (WHERE chatbot_attempted = true), 0) * 100 as rate
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '6 hours'
                        AND chatbot_attempted = true
                    ),
                    historical_rate AS (
                        SELECT 
                            COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
                            NULLIF(COUNT(*) FILTER (WHERE chatbot_attempted = true), 0) * 100 as rate
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                        AND created_at < NOW() - INTERVAL '1 day'
                        AND chatbot_attempted = true
                    )
                    SELECT 
                        r.rate as recent,
                        h.rate as historical
                    FROM recent_rate r
                    CROSS JOIN historical_rate h
                    WHERE r.rate < h.rate - 20
                """)
                
                row = cur.fetchone()
                if row:
                    anomalies.append({
                        "type": "chatbot_performance_degradation",
                        "recent_rate": float(row[0]) if row[0] else 0,
                        "historical_rate": float(row[1]) if row[1] else 0,
                        "severity": "medium"
                    })
                
                # Anomalía: Tiempo de respuesta aumentando
                cur.execute("""
                    WITH recent_avg AS (
                        SELECT AVG(time_to_first_response_minutes) as avg_time
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '6 hours'
                        AND chatbot_resolved = false
                        AND time_to_first_response_minutes IS NOT NULL
                    ),
                    historical_avg AS (
                        SELECT AVG(time_to_first_response_minutes) as avg_time
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '7 days'
                        AND created_at < NOW() - INTERVAL '1 day'
                        AND chatbot_resolved = false
                        AND time_to_first_response_minutes IS NOT NULL
                    )
                    SELECT 
                        r.avg_time as recent,
                        h.avg_time as historical
                    FROM recent_avg r
                    CROSS JOIN historical_avg h
                    WHERE r.avg_time > h.avg_time * 1.5
                """)
                
                row = cur.fetchone()
                if row:
                    anomalies.append({
                        "type": "response_time_increase",
                        "recent_avg": float(row[0]) if row[0] else 0,
                        "historical_avg": float(row[1]) if row[1] else 0,
                        "severity": "high"
                    })
        
        return {
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "timestamp": datetime.now().isoformat()
        }
    
    @task(task_id="check_sla_breaches")
    def check_sla_breaches() -> Dict[str, Any]:
        """Verifica violaciones de SLA."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        breaches = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Tickets críticos sin respuesta en 1 hora
                cur.execute("""
                    SELECT 
                        ticket_id,
                        subject,
                        customer_email,
                        priority,
                        created_at,
                        EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_open
                    FROM support_tickets
                    WHERE priority IN ('critical', 'urgent')
                    AND status NOT IN ('resolved', 'closed', 'chatbot_handled')
                    AND (first_response_at IS NULL OR first_response_at > created_at + INTERVAL '1 hour')
                    AND created_at < NOW() - INTERVAL '1 hour'
                    ORDER BY created_at ASC
                """)
                
                for row in cur.fetchall():
                    breaches.append({
                        "ticket_id": row[0],
                        "subject": row[1],
                        "customer_email": row[2],
                        "priority": row[3],
                        "minutes_open": float(row[5]),
                        "sla_type": "first_response",
                        "severity": "critical"
                    })
                
                # Tickets abiertos más de 48 horas
                cur.execute("""
                    SELECT 
                        ticket_id,
                        subject,
                        customer_email,
                        priority,
                        created_at,
                        EXTRACT(EPOCH FROM (NOW() - created_at))/60 as minutes_open
                    FROM support_tickets
                    WHERE status NOT IN ('resolved', 'closed', 'chatbot_handled')
                    AND created_at < NOW() - INTERVAL '48 hours'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT 20
                """)
                
                for row in cur.fetchall():
                    breaches.append({
                        "ticket_id": row[0],
                        "subject": row[1],
                        "customer_email": row[2],
                        "priority": row[3],
                        "minutes_open": float(row[5]),
                        "sla_type": "resolution_time",
                        "severity": "high" if row[3] in ["critical", "urgent"] else "medium"
                    })
        
        return {
            "breaches": breaches,
            "breach_count": len(breaches),
            "critical_breaches": len([b for b in breaches if b["severity"] == "critical"])
        }
    
    @task(task_id="predictive_alerts")
    def predictive_alerts() -> Dict[str, Any]:
        """Alertas predictivas basadas en tendencias."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        alerts = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Predecir sobrecarga de agentes
                cur.execute("""
                    SELECT 
                        a.agent_id,
                        a.agent_name,
                        a.current_active_tickets,
                        a.max_concurrent_tickets,
                        COUNT(t.ticket_id) FILTER (
                            WHERE t.created_at >= NOW() - INTERVAL '1 hour'
                        ) as new_tickets_last_hour,
                        AVG(t.time_to_resolution_minutes) as avg_resolution_time
                    FROM support_agents a
                    LEFT JOIN support_tickets t ON a.agent_id = t.assigned_agent_id
                    WHERE a.is_available = true
                    GROUP BY a.agent_id, a.agent_name, a.current_active_tickets, a.max_concurrent_tickets
                    HAVING a.current_active_tickets >= a.max_concurrent_tickets * 0.8
                    OR (COUNT(t.ticket_id) FILTER (WHERE t.created_at >= NOW() - INTERVAL '1 hour') > 3
                        AND AVG(t.time_to_resolution_minutes) > 120)
                """)
                
                for row in cur.fetchall():
                    alerts.append({
                        "type": "agent_overload_risk",
                        "agent_id": row[0],
                        "agent_name": row[1],
                        "current_tickets": row[2],
                        "max_tickets": row[3],
                        "new_tickets_last_hour": row[4] or 0,
                        "severity": "medium"
                    })
                
                # Predecir aumento de volumen
                cur.execute("""
                    WITH hourly_trend AS (
                        SELECT 
                            DATE_TRUNC('hour', created_at) as hour,
                            COUNT(*) as count
                        FROM support_tickets
                        WHERE created_at >= NOW() - INTERVAL '6 hours'
                        GROUP BY DATE_TRUNC('hour', created_at)
                        ORDER BY hour DESC
                        LIMIT 6
                    )
                    SELECT 
                        AVG(count) as avg_last_6h,
                        MAX(count) as max_last_6h,
                        (SELECT count FROM hourly_trend ORDER BY hour DESC LIMIT 1) as current_hour
                    FROM hourly_trend
                """)
                
                row = cur.fetchone()
                if row and row[2] and row[0]:
                    if row[2] > row[0] * 1.5:  # 50% más que el promedio
                        alerts.append({
                            "type": "volume_increase_prediction",
                            "current_hour_count": row[2],
                            "avg_last_6h": float(row[0]),
                            "increase_pct": ((row[2] - row[0]) / row[0] * 100) if row[0] > 0 else 0,
                            "severity": "medium"
                        })
        
        return {
            "alerts": alerts,
            "alert_count": len(alerts)
        }
    
    @task(task_id="send_alerts")
    def send_alerts(
        anomalies: Dict[str, Any],
        breaches: Dict[str, Any],
        predictive: Dict[str, Any]
    ) -> None:
        """Envía alertas consolidadas."""
        all_alerts = []
        
        # Agregar anomalías críticas
        for anomaly in anomalies.get("anomalies", []):
            if anomaly.get("severity") in ["high", "critical"]:
                all_alerts.append({
                    "type": "anomaly",
                    "data": anomaly
                })
        
        # Agregar violaciones de SLA críticas
        for breach in breaches.get("breaches", []):
            if breach.get("severity") == "critical":
                all_alerts.append({
                    "type": "sla_breach",
                    "data": breach
                })
        
        # Agregar alertas predictivas
        for alert in predictive.get("alerts", []):
            if alert.get("severity") in ["high", "critical"]:
                all_alerts.append({
                    "type": "predictive",
                    "data": alert
                })
        
        if not all_alerts:
            logger.info("No critical alerts to send")
            return
        
        # Enviar a Slack
        if SLACK_WEBHOOK_URL and REQUESTS_AVAILABLE:
            try:
                blocks = [{
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🚨 Alertas Avanzadas de Soporte"
                    }
                }]
                
                for alert in all_alerts[:10]:  # Máximo 10 alertas
                    alert_type = alert["type"]
                    data = alert["data"]
                    
                    if alert_type == "anomaly":
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Anomalía Detectada:* {data.get('type', 'unknown')}\n*Severidad:* {data.get('severity', 'unknown')}"
                            }
                        })
                    elif alert_type == "sla_breach":
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*SLA Breach:* Ticket {data.get('ticket_id')}\n*Tipo:* {data.get('sla_type')}\n*Tiempo abierto:* {data.get('minutes_open', 0):.0f} minutos"
                            }
                        })
                    elif alert_type == "predictive":
                        blocks.append({
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Alerta Predictiva:* {data.get('type', 'unknown')}\n*Severidad:* {data.get('severity', 'unknown')}"
                            }
                        })
                
                payload = {
                    "text": f"Alertas Avanzadas ({len(all_alerts)} alertas)",
                    "blocks": blocks
                }
                
                requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=10)
                logger.info(f"Sent {len(all_alerts)} alerts to Slack")
                
            except Exception as e:
                logger.error(f"Failed to send Slack alerts: {e}", exc_info=True)
        
        # Enviar a PagerDuty si hay alertas críticas
        critical_count = len([a for a in all_alerts if a.get("data", {}).get("severity") == "critical"])
        if critical_count > 0 and PAGERDUTY_INTEGRATION_KEY and REQUESTS_AVAILABLE:
            try:
                payload = {
                    "routing_key": PAGERDUTY_INTEGRATION_KEY,
                    "event_action": "trigger",
                    "payload": {
                        "summary": f"{critical_count} alertas críticas de soporte",
                        "severity": "critical",
                        "source": "support-automation",
                        "custom_details": {
                            "alert_count": len(all_alerts),
                            "critical_count": critical_count
                        }
                    }
                }
                
                requests.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json=payload,
                    timeout=10
                )
                logger.info(f"Sent {critical_count} critical alerts to PagerDuty")
                
            except Exception as e:
                logger.error(f"Failed to send PagerDuty alerts: {e}", exc_info=True)
    
    # Pipeline
    anomalies = detect_anomalies()
    breaches = check_sla_breaches()
    predictive = predictive_alerts()
    send_alerts(anomalies, breaches, predictive)


dag = support_tickets_alerts_advanced()


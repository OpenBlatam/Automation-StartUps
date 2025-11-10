"""
DAG de Automatización Completa de Tickets de Soporte

Funcionalidades:
1. Categorización automática de tickets
2. Asignación según expertise del equipo
3. Escalación automática de casos urgentes
4. Envío de actualizaciones de status
5. Solicitud automática de feedback post-resolución
"""
from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import sys
import os

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# Agregar ruta de módulos de soporte
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../workflow/kestra/flows/lib"))


@dag(
    dag_id="support_ticket_automation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="*/15 * * * *",  # Cada 15 minutos
    catchup=False,
    default_args={
        "owner": "support",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Automatización Completa de Tickets de Soporte
    
    Sistema completo que automatiza:
    1. **Categorización automática**: Clasifica tickets usando NLP y ML
    2. **Asignación por expertise**: Asigna tickets a agentes según su expertise y historial
    3. **Escalación de urgentes**: Escala automáticamente casos urgentes a supervisores
    4. **Notificaciones de status**: Envía actualizaciones automáticas a clientes
    5. **Feedback post-resolución**: Solicita feedback automáticamente después de resolver
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `enable_auto_categorization`: Habilitar categorización automática (default: true)
    - `enable_expertise_routing`: Habilitar asignación por expertise (default: true)
    - `enable_urgent_escalation`: Habilitar escalación de urgentes (default: true)
    - `enable_status_notifications`: Habilitar notificaciones de status (default: true)
    - `enable_feedback_automation`: Habilitar solicitud de feedback (default: true)
    - `max_tickets_per_run`: Máximo de tickets a procesar (default: 50)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "enable_auto_categorization": Param(True, type="boolean"),
        "enable_expertise_routing": Param(True, type="boolean"),
        "enable_urgent_escalation": Param(True, type="boolean"),
        "enable_status_notifications": Param(True, type="boolean"),
        "enable_feedback_automation": Param(True, type="boolean"),
        "max_tickets_per_run": Param(50, type="integer", minimum=1, maximum=200),
        "notification_email_enabled": Param(True, type="boolean"),
        "notification_sms_enabled": Param(False, type="boolean"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["support", "automation", "tickets", "categorization", "routing", "escalation"],
)
def support_ticket_automation() -> None:
    """
    DAG principal para automatización completa de tickets de soporte.
    """
    
    @task(task_id="auto_categorize_tickets")
    def auto_categorize_tickets() -> Dict[str, Any]:
        """Categoriza automáticamente tickets sin categoría."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_auto_categorization", True):
            return {"processed": 0, "categorized": 0}
        
        try:
            from support_auto_categorization import SupportAutoCategorizer
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Obtener tickets sin categoría o con categoría general
                    cur.execute("""
                        SELECT 
                            ticket_id,
                            subject,
                            description,
                            category,
                            customer_email
                        FROM support_tickets
                        WHERE (category IS NULL OR category = 'general')
                        AND status IN ('open', 'assigned')
                        AND created_at >= NOW() - INTERVAL '7 days'
                        ORDER BY created_at DESC
                        LIMIT %s
                    """, (params.get("max_tickets_per_run", 50),))
                    
                    tickets = cur.fetchall()
                    categorizer = SupportAutoCategorizer(db_connection=conn)
                    
                    categorized = 0
                    for row in tickets:
                        ticket_id, subject, description, category, customer_email = row
                        
                        result = categorizer.categorize(
                            subject=subject,
                            description=description,
                            existing_category=category,
                            customer_email=customer_email
                        )
                        
                        if result.confidence > 0.5:
                            # Actualizar categoría en BD
                            cur.execute("""
                                UPDATE support_tickets
                                SET category = %s,
                                    subcategory = %s,
                                    tags = COALESCE(tags, '{}') || %s::text[],
                                    updated_at = NOW()
                                WHERE ticket_id = %s
                            """, (
                                result.category,
                                result.subcategory,
                                result.keywords_matched[:5],  # Limitar a 5 tags
                                ticket_id
                            ))
                            categorized += 1
                            
                            logger.info(
                                f"Ticket {ticket_id} categorizado como {result.category} "
                                f"(subcategoría: {result.subcategory}, confianza: {result.confidence:.2f})"
                            )
                    
                    conn.commit()
                    logger.info(f"Categorizados {categorized} de {len(tickets)} tickets")
                    return {"processed": len(tickets), "categorized": categorized}
                    
        except Exception as e:
            logger.error(f"Error en categorización automática: {e}", exc_info=True)
            return {"processed": 0, "categorized": 0, "error": str(e)}
    
    @task(task_id="assign_by_expertise")
    def assign_by_expertise() -> Dict[str, Any]:
        """Asigna tickets a agentes según expertise."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_expertise_routing", True):
            return {"processed": 0, "assigned": 0}
        
        try:
            from support_expertise_routing import SupportExpertiseRouter
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Obtener tickets sin asignar o con asignación general
                    cur.execute("""
                        SELECT 
                            ticket_id,
                            category,
                            subcategory,
                            assigned_department,
                            priority
                        FROM support_tickets
                        WHERE status = 'open'
                        AND (assigned_agent_id IS NULL OR assigned_department IS NULL)
                        AND category IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '24 hours'
                        ORDER BY 
                            CASE priority
                                WHEN 'critical' THEN 1
                                WHEN 'urgent' THEN 2
                                WHEN 'high' THEN 3
                                ELSE 4
                            END,
                            created_at ASC
                        LIMIT %s
                    """, (params.get("max_tickets_per_run", 50),))
                    
                    tickets = cur.fetchall()
                    router = SupportExpertiseRouter(db_connection=conn)
                    
                    assigned = 0
                    for row in tickets:
                        ticket_id, category, subcategory, department, priority = row
                        
                        match = router.assign_by_expertise(
                            ticket_id=ticket_id,
                            category=category or "general",
                            subcategory=subcategory,
                            department=department,
                            priority=priority or "medium"
                        )
                        
                        if match:
                            assigned += 1
                            logger.info(
                                f"Ticket {ticket_id} asignado a {match.agent_name} "
                                f"(expertise score: {match.expertise_score:.2f})"
                            )
                    
                    logger.info(f"Asignados {assigned} de {len(tickets)} tickets por expertise")
                    return {"processed": len(tickets), "assigned": assigned}
                    
        except Exception as e:
            logger.error(f"Error en asignación por expertise: {e}", exc_info=True)
            return {"processed": 0, "assigned": 0, "error": str(e)}
    
    @task(task_id="escalate_urgent_tickets")
    def escalate_urgent_tickets() -> Dict[str, Any]:
        """Escala automáticamente tickets urgentes."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_urgent_escalation", True):
            return {"processed": 0, "escalated": 0}
        
        try:
            from support_urgent_escalation import SupportUrgentEscalation
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            with hook.get_conn() as conn:
                escalation = SupportUrgentEscalation(db_connection=conn)
                
                results = escalation.auto_escalate_urgent_tickets()
                
                escalated = sum(1 for r in results if r.escalated)
                
                for result in results:
                    if result.escalated:
                        logger.info(
                            f"Ticket escalado: {len(result.actions)} acciones aplicadas. "
                            f"Razón: {result.reason}"
                        )
                
                logger.info(f"Escalados {escalated} tickets urgentes")
                return {"processed": len(results), "escalated": escalated}
                
        except Exception as e:
            logger.error(f"Error en escalación de urgentes: {e}", exc_info=True)
            return {"processed": 0, "escalated": 0, "error": str(e)}
    
    @task(task_id="send_status_notifications")
    def send_status_notifications() -> Dict[str, Any]:
        """Envía notificaciones de cambios de status."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_status_notifications", True):
            return {"processed": 0, "sent": 0}
        
        try:
            from support_status_notifications import SupportStatusNotifier
            from support_notifications_multi import (
                SupportNotificationManager,
                NotificationChannel,
                NotificationConfig
            )
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Configurar notificaciones
            notification_configs = []
            if params.get("notification_email_enabled", True):
                notification_configs.append(
                    NotificationConfig(
                        channel=NotificationChannel.EMAIL,
                        enabled=True,
                        priority=1,
                        config={"api_url": os.getenv("EMAIL_API_URL")}
                    )
                )
            
            notification_manager = SupportNotificationManager(notification_configs) if notification_configs else None
            
            with hook.get_conn() as conn:
                notifier = SupportStatusNotifier(
                    db_connection=conn,
                    notification_manager=notification_manager
                )
                
                # Obtener cambios de status recientes sin notificar
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT DISTINCT
                            ticket_id,
                            status,
                            LAG(status) OVER (PARTITION BY ticket_id ORDER BY updated_at) as old_status
                        FROM support_tickets
                        WHERE updated_at >= NOW() - INTERVAL '1 hour'
                        AND status IN ('assigned', 'in_progress', 'waiting_customer', 'resolved', 'escalated')
                        ORDER BY updated_at DESC
                        LIMIT %s
                    """, (params.get("max_tickets_per_run", 50),))
                    
                    tickets = cur.fetchall()
                    sent = 0
                    
                    for row in tickets:
                        ticket_id, new_status, old_status = row
                        
                        if notifier.notify_on_status_change(ticket_id, old_status or "open", new_status):
                            sent += 1
                            logger.info(f"Notificación de status enviada para ticket {ticket_id}: {old_status} -> {new_status}")
                    
                    logger.info(f"Enviadas {sent} notificaciones de status")
                    return {"processed": len(tickets), "sent": sent}
                    
        except Exception as e:
            logger.error(f"Error enviando notificaciones de status: {e}", exc_info=True)
            return {"processed": 0, "sent": 0, "error": str(e)}
    
    @task(task_id="request_feedback")
    def request_feedback() -> Dict[str, Any]:
        """Solicita feedback automáticamente para tickets resueltos."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_feedback_automation", True):
            return {"processed": 0, "sent": 0}
        
        try:
            from support_feedback_automation import SupportFeedbackAutomation
            from support_notifications_multi import (
                SupportNotificationManager,
                NotificationChannel,
                NotificationConfig
            )
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Configurar notificaciones
            notification_configs = []
            if params.get("notification_email_enabled", True):
                notification_configs.append(
                    NotificationConfig(
                        channel=NotificationChannel.EMAIL,
                        enabled=True,
                        priority=1,
                        config={"api_url": os.getenv("EMAIL_API_URL")}
                    )
                )
            
            notification_manager = SupportNotificationManager(notification_configs) if notification_configs else None
            
            with hook.get_conn() as conn:
                feedback_automation = SupportFeedbackAutomation(
                    db_connection=conn,
                    notification_manager=notification_manager,
                    feedback_base_url=os.getenv("FEEDBACK_BASE_URL", "https://support.example.com/feedback")
                )
                
                processed = feedback_automation.auto_request_feedback_for_resolved_tickets()
                
                logger.info(f"Solicitado feedback para {len(processed)} tickets")
                return {"processed": len(processed), "sent": len(processed)}
                
        except Exception as e:
            logger.error(f"Error solicitando feedback: {e}", exc_info=True)
            return {"processed": 0, "sent": 0, "error": str(e)}
    
    # Ejecutar tareas en paralelo donde sea posible
    categorize_result = auto_categorize_tickets()
    assign_result = assign_by_expertise()
    escalate_result = escalate_urgent_tickets()
    notify_result = send_status_notifications()
    feedback_result = request_feedback()
    
    # Las tareas se ejecutan en paralelo, pero la asignación espera a la categorización
    assign_result.set_upstream(categorize_result)


# Ejecutar DAG
support_ticket_automation()


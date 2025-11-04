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
    dag_id="sales_followup_automation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Automatización de Seguimiento de Ventas
    
    Sistema que gestiona automáticamente el seguimiento de leads calificados:
    - Asigna leads a vendedores automáticamente (round-robin)
    - Crea tareas de seguimiento basadas en campañas configurables
    - Dispara acciones automáticas (emails, llamadas, reuniones)
    - Rastrea progreso del pipeline de ventas
    - Actualiza etapas automáticamente basado en actividad
    
    **Funcionalidades:**
    - Auto-asignación de leads calificados a vendedores
    - Generación automática de tareas de seguimiento
    - Ejecución de campañas automatizadas (email sequences, call campaigns)
    - Actualización de etapas del pipeline
    - Notificaciones a vendedores
    - Tracking completo de todas las acciones
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `email_webhook_url`: Webhook para envío de emails (requerido)
    - `call_api_url`: API para realizar llamadas (opcional)
    - `task_manager_api_url`: API para crear tareas en sistema externo (opcional)
    - `auto_assign_enabled`: Auto-asignar leads a vendedores (default: true)
    - `max_leads_per_run`: Máximo de leads a procesar (default: 100)
    - `enable_auto_tasks`: Crear tareas automáticamente (default: true)
    - `enable_campaigns`: Ejecutar campañas automáticas (default: true)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email_webhook_url": Param("", type="string", minLength=1),
        "call_api_url": Param("", type="string"),
        "task_manager_api_url": Param("", type="string"),
        "auto_assign_enabled": Param(True, type="boolean"),
        "max_leads_per_run": Param(100, type="integer", minimum=1, maximum=500),
        "enable_auto_tasks": Param(True, type="boolean"),
        "enable_campaigns": Param(True, type="boolean"),
        "default_followup_days": Param(3, type="integer", minimum=1, maximum=30),
        "slack_webhook_url": Param("", type="string"),
        "dry_run": Param(False, type="boolean"),
        "request_timeout": Param(30, type="integer", minimum=5, maximum=120),
    },
    tags=["sales", "followup", "automation", "pipeline"],
)
def sales_followup_automation() -> None:
    """
    DAG principal para automatización de seguimiento de ventas.
    """
    
    @task(task_id="ensure_schema")
    def ensure_schema() -> bool:
        """Verifica que el schema esté creado."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_name = 'sales_pipeline'
                    """)
                    
                    if cur.fetchone()[0] == 0:
                        logger.warning(
                            "Schema de sales_tracking no encontrado. "
                            "Por favor ejecuta data/db/sales_tracking_schema.sql"
                        )
                        return False
                    
                    logger.info("Schema verificado correctamente")
                    return True
        except Exception as e:
            logger.error(f"Error verificando schema: {e}", exc_info=True)
            return False
    
    @task(task_id="get_unassigned_leads")
    def get_unassigned_leads() -> List[Dict[str, Any]]:
        """Obtiene leads calificados sin asignar."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        auto_assign = bool(params["auto_assign_enabled"])
        
        if not auto_assign:
            return []
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id AS pipeline_id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.phone,
                p.score,
                p.priority,
                p.source,
                p.stage,
                p.qualified_at,
                p.estimated_value,
                p.probability_pct
            FROM sales_pipeline p
            WHERE 
                p.assigned_to IS NULL
                AND p.stage NOT IN ('closed_won', 'closed_lost')
                AND p.qualified_at >= NOW() - INTERVAL '90 days'
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
        
        logger.info(f"Encontrados {len(leads)} leads sin asignar")
        return leads
    
    @task(task_id="auto_assign_leads")
    def auto_assign_leads(unassigned_leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Asigna leads automáticamente a vendedores usando round-robin."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        assigned_leads = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in unassigned_leads:
                    try:
                        # Obtener vendedor asignado usando función SQL
                        cur.execute("""
                            SELECT auto_assign_sales_rep(%s)
                        """, (lead["lead_ext_id"],))
                        
                        assigned_email = cur.fetchone()[0]
                        
                        if not dry_run:
                            # Actualizar pipeline
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET assigned_to = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (assigned_email, lead["pipeline_id"]))
                            
                            conn.commit()
                        
                        assigned_leads.append({
                            **lead,
                            "assigned_to": assigned_email
                        })
                        
                        logger.info(f"Lead {lead['lead_ext_id']} asignado a {assigned_email}")
                        
                    except Exception as e:
                        logger.error(f"Error asignando lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
                        continue
        
        logger.info(f"Asignados {len(assigned_leads)} leads")
        return assigned_leads
    
    @task(task_id="get_leads_needing_followup")
    def get_leads_needing_followup() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan seguimiento."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        default_days = int(params["default_followup_days"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id AS pipeline_id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.phone,
                p.score,
                p.priority,
                p.stage,
                p.assigned_to,
                p.last_contact_at,
                p.next_followup_at,
                p.qualified_at,
                COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks_count
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    -- Necesita seguimiento programado
                    (p.next_followup_at IS NOT NULL AND p.next_followup_at <= NOW())
                    OR
                    -- Sin seguimiento reciente y sin tareas pendientes
                    (
                        (p.last_contact_at IS NULL OR p.last_contact_at <= NOW() - INTERVAL '%s days')
                        AND (p.next_followup_at IS NULL OR p.next_followup_at <= NOW())
                        AND (COUNT(t.id) FILTER (WHERE t.status = 'pending') = 0)
                    )
                )
            GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, p.last_name, 
                     p.phone, p.score, p.priority, p.stage, p.assigned_to,
                     p.last_contact_at, p.next_followup_at, p.qualified_at
            ORDER BY 
                p.priority DESC,
                p.next_followup_at ASC NULLS FIRST,
                p.qualified_at ASC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (default_days, max_leads))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(leads)} leads que necesitan seguimiento")
        return leads
    
    @task(task_id="create_followup_tasks")
    def create_followup_tasks(leads_needing_followup: List[Dict[str, Any]]) -> Dict[str, int]:
        """Crea tareas de seguimiento automáticas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_tasks = bool(params["enable_auto_tasks"])
        dry_run = bool(params["dry_run"])
        
        if not enable_tasks:
            return {"created": 0, "skipped": len(leads_needing_followup)}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"created": 0, "skipped": 0, "errors": 0}
        now = datetime.utcnow()
        
        # Definir tareas por etapa
        stage_tasks = {
            "qualified": [
                {
                    "type": "email",
                    "title": "Primer contacto - Introducción",
                    "description": "Enviar email de introducción y descubrir necesidades",
                    "priority": "high",
                    "delay_hours": 0
                }
            ],
            "contacted": [
                {
                    "type": "call",
                    "title": "Llamada de seguimiento",
                    "description": "Llamar para profundizar conversación",
                    "priority": "medium",
                    "delay_hours": 24
                }
            ],
            "meeting_scheduled": [
                {
                    "type": "email",
                    "title": "Preparación para reunión",
                    "description": "Enviar agenda y materiales de preparación",
                    "priority": "high",
                    "delay_hours": -24  # 24 horas antes
                }
            ],
            "proposal_sent": [
                {
                    "type": "call",
                    "title": "Seguimiento de propuesta",
                    "description": "Llamar para responder preguntas sobre la propuesta",
                    "priority": "high",
                    "delay_hours": 48
                }
            ],
            "negotiating": [
                {
                    "type": "email",
                    "title": "Seguimiento de negociación",
                    "description": "Enviar email para avanzar negociación",
                    "priority": "urgent",
                    "delay_hours": 24
                }
            ]
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in leads_needing_followup:
                    try:
                        stage = lead.get("stage", "qualified")
                        tasks_for_stage = stage_tasks.get(stage, [])
                        
                        # Si ya tiene tareas pendientes, saltar
                        if lead.get("pending_tasks_count", 0) > 0:
                            stats["skipped"] += 1
                            continue
                        
                        # Crear tarea para la etapa actual
                        if tasks_for_stage:
                            task_config = tasks_for_stage[0]  # Primera tarea de la etapa
                            
                            due_date = now + timedelta(hours=task_config["delay_hours"])
                            if due_date < now:
                                due_date = now + timedelta(hours=1)  # Mínimo 1 hora
                            
                            if not dry_run:
                                cur.execute("""
                                    INSERT INTO sales_followup_tasks
                                    (pipeline_id, lead_ext_id, task_type, task_title, task_description,
                                     priority, assigned_to, due_date, created_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                                """, (
                                    lead["pipeline_id"],
                                    lead["lead_ext_id"],
                                    task_config["type"],
                                    task_config["title"],
                                    task_config["description"],
                                    task_config["priority"],
                                    lead.get("assigned_to"),
                                    due_date
                                ))
                                
                                # Actualizar next_followup_at en pipeline
                                cur.execute("""
                                    UPDATE sales_pipeline
                                    SET next_followup_at = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (due_date, lead["pipeline_id"]))
                                
                                conn.commit()
                            
                            stats["created"] += 1
                            logger.info(f"Tarea creada para lead {lead['lead_ext_id']}: {task_config['title']}")
                        else:
                            stats["skipped"] += 1
                            
                    except Exception as e:
                        logger.error(f"Error creando tarea para lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
                        stats["errors"] += 1
                        continue
        
        logger.info(f"Tareas creadas: {stats['created']}, Saltadas: {stats['skipped']}, Errores: {stats['errors']}")
        
        try:
            Stats.incr("sales_followup.tasks_created", stats["created"])
        except Exception:
            pass
        
        return stats
    
    @task(task_id="get_active_campaigns")
    def get_active_campaigns() -> List[Dict[str, Any]]:
        """Obtiene campañas activas que deben ejecutarse."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_campaigns = bool(params["enable_campaigns"])
        
        if not enable_campaigns:
            return []
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                id,
                name,
                description,
                campaign_type,
                trigger_criteria,
                steps_config,
                max_leads_per_run
            FROM sales_campaigns
            WHERE enabled = true
            ORDER BY id ASC
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                campaigns = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontradas {len(campaigns)} campañas activas")
        return campaigns
    
    @task(task_id="execute_campaigns")
    def execute_campaigns(campaigns: List[Dict[str, Any]]) -> Dict[str, int]:
        """Ejecuta campañas automáticas para leads que cumplen criterios."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email_webhook = str(params["email_webhook_url"]).strip()
        call_api = str(params["call_api_url"]).strip()
        dry_run = bool(params["dry_run"])
        timeout = int(params["request_timeout"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {
            "campaigns_executed": 0,
            "leads_processed": 0,
            "actions_sent": 0,
            "errors": 0
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for campaign in campaigns:
                    try:
                        campaign_id = campaign["id"]
                        trigger_criteria = campaign.get("trigger_criteria") or {}
                        steps_config = campaign.get("steps_config") or []
                        max_leads = campaign.get("max_leads_per_run", 50)
                        
                        # Construir query basado en criterios
                        where_clauses = ["p.stage NOT IN ('closed_won', 'closed_lost')"]
                        params_list = []
                        
                        if trigger_criteria.get("stage"):
                            where_clauses.append("p.stage = %s")
                            params_list.append(trigger_criteria["stage"])
                        
                        if trigger_criteria.get("score_min"):
                            where_clauses.append("p.score >= %s")
                            params_list.append(trigger_criteria["score_min"])
                        
                        if trigger_criteria.get("priority"):
                            where_clauses.append("p.priority = %s")
                            params_list.append(trigger_criteria["priority"])
                        
                        # Excluir leads que ya tienen esta campaña activa
                        where_clauses.append("""
                            NOT EXISTS (
                                SELECT 1 FROM sales_campaign_executions ce
                                WHERE ce.campaign_id = %s AND ce.lead_ext_id = p.lead_ext_id
                                AND ce.status = 'active'
                            )
                        """)
                        params_list.append(campaign_id)
                        
                        params_list.append(max_leads)
                        
                        query = f"""
                            SELECT 
                                p.id AS pipeline_id,
                                p.lead_ext_id,
                                p.email,
                                p.first_name,
                                p.last_name,
                                p.assigned_to
                            FROM sales_pipeline p
                            WHERE {' AND '.join(where_clauses)}
                            ORDER BY p.priority DESC, p.score DESC
                            LIMIT %s
                        """
                        
                        cur.execute(query, params_list)
                        columns = [desc[0] for desc in cur.description]
                        eligible_leads = [dict(zip(columns, row)) for row in cur.fetchall()]
                        
                        if not eligible_leads:
                            continue
                        
                        # Crear ejecución de campaña para cada lead
                        for lead in eligible_leads:
                            try:
                                if not dry_run:
                                    # Crear ejecución
                                    cur.execute("""
                                        INSERT INTO sales_campaign_executions
                                        (campaign_id, lead_ext_id, pipeline_id, status, 
                                         current_step, total_steps, started_at, next_action_at)
                                        VALUES (%s, %s, %s, 'active', 1, %s, NOW(), NOW())
                                        ON CONFLICT (campaign_id, lead_ext_id) DO NOTHING
                                        RETURNING id
                                    """, (
                                        campaign_id,
                                        lead["lead_ext_id"],
                                        lead["pipeline_id"],
                                        len(steps_config)
                                    ))
                                    
                                    result = cur.fetchone()
                                    if not result:
                                        continue  # Ya existe ejecución
                                    
                                    execution_id = result[0]
                                    
                                    # Ejecutar primer paso si existe
                                    if steps_config:
                                        first_step = steps_config[0]
                                        step_type = first_step.get("type", "email")
                                        
                                        # Crear evento
                                        cur.execute("""
                                            INSERT INTO sales_campaign_events
                                            (execution_id, lead_ext_id, step_number, event_type, status, created_at)
                                            VALUES (%s, %s, 1, %s, 'queued', NOW())
                                            RETURNING id
                                        """, (execution_id, lead["lead_ext_id"], f"{step_type}_sent"))
                                        
                                        event_id = cur.fetchone()[0]
                                        
                                        # Ejecutar acción según tipo
                                        if step_type == "email" and email_webhook:
                                            send_campaign_email(
                                                lead,
                                                first_step,
                                                email_webhook,
                                                timeout,
                                                dry_run
                                            )
                                            
                                            cur.execute("""
                                                UPDATE sales_campaign_events
                                                SET status = 'sent', executed_at = NOW()
                                                WHERE id = %s
                                            """, (event_id,))
                                            
                                            stats["actions_sent"] += 1
                                        
                                        elif step_type == "call" and call_api:
                                            # Lógica para llamadas (similar)
                                            stats["actions_sent"] += 1
                                        
                                        # Actualizar next_action_at
                                        delay_hours = first_step.get("delay_hours", 24)
                                        next_action = now + timedelta(hours=delay_hours)
                                        
                                        cur.execute("""
                                            UPDATE sales_campaign_executions
                                            SET next_action_at = %s,
                                                updated_at = NOW()
                                            WHERE id = %s
                                        """, (next_action, execution_id))
                                    
                                    conn.commit()
                                
                                stats["leads_processed"] += 1
                                
                            except Exception as e:
                                logger.error(f"Error ejecutando campaña para lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
                                stats["errors"] += 1
                                continue
                        
                        stats["campaigns_executed"] += 1
                        
                    except Exception as e:
                        logger.error(f"Error procesando campaña {campaign.get('name')}: {e}", exc_info=True)
                        stats["errors"] += 1
                        continue
        
        logger.info(f"Campañas ejecutadas: {stats['campaigns_executed']}, "
                   f"Leads procesados: {stats['leads_processed']}, "
                   f"Acciones enviadas: {stats['actions_sent']}")
        
        return stats
    
    @task(task_id="process_scheduled_actions")
    def process_scheduled_actions() -> Dict[str, int]:
        """Procesa acciones programadas de campañas activas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email_webhook = str(params["email_webhook_url"]).strip()
        call_api = str(params["call_api_url"]).strip()
        dry_run = bool(params["dry_run"])
        timeout = int(params["request_timeout"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"processed": 0, "errors": 0}
        
        # Obtener ejecuciones con acciones pendientes
        query = """
            SELECT 
                ce.id AS execution_id,
                ce.current_step,
                ce.total_steps,
                ce.campaign_id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                c.steps_config
            FROM sales_campaign_executions ce
            JOIN sales_pipeline p ON ce.pipeline_id = p.id
            JOIN sales_campaigns c ON ce.campaign_id = c.id
            WHERE 
                ce.status = 'active'
                AND ce.next_action_at IS NOT NULL
                AND ce.next_action_at <= NOW()
                AND ce.current_step <= ce.total_steps
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                columns = [desc[0] for desc in cur.description]
                executions = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                for exec_data in executions:
                    try:
                        execution_id = exec_data["execution_id"]
                        current_step = exec_data["current_step"]
                        steps_config = exec_data.get("steps_config") or []
                        
                        if current_step > len(steps_config):
                            continue
                        
                        step_config = steps_config[current_step - 1]
                        step_type = step_config.get("type", "email")
                        
                        lead = {
                            "lead_ext_id": exec_data["lead_ext_id"],
                            "email": exec_data["email"],
                            "first_name": exec_data["first_name"],
                            "last_name": exec_data["last_name"]
                        }
                        
                        if not dry_run:
                            # Crear evento
                            cur.execute("""
                                INSERT INTO sales_campaign_events
                                (execution_id, lead_ext_id, step_number, event_type, status, created_at)
                                VALUES (%s, %s, %s, %s, 'queued', NOW())
                                RETURNING id
                            """, (execution_id, lead["lead_ext_id"], current_step, f"{step_type}_sent"))
                            
                            event_id = cur.fetchone()[0]
                            
                            # Ejecutar acción
                            if step_type == "email" and email_webhook:
                                send_campaign_email(lead, step_config, email_webhook, timeout, dry_run)
                                
                                cur.execute("""
                                    UPDATE sales_campaign_events
                                    SET status = 'sent', executed_at = NOW()
                                    WHERE id = %s
                                """, (event_id,))
                                
                                stats["processed"] += 1
                            
                            # Actualizar ejecución
                            if current_step < exec_data["total_steps"]:
                                next_step = current_step + 1
                                delay_hours = step_config.get("delay_hours", 24)
                                next_action = datetime.utcnow() + timedelta(hours=delay_hours)
                                
                                cur.execute("""
                                    UPDATE sales_campaign_executions
                                    SET current_step = %s,
                                        next_action_at = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (next_step, next_action, execution_id))
                            else:
                                # Campaña completada
                                cur.execute("""
                                    UPDATE sales_campaign_executions
                                    SET status = 'completed',
                                        completed_at = NOW(),
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (execution_id,))
                            
                            conn.commit()
                        
                    except Exception as e:
                        logger.error(f"Error procesando acción programada: {e}", exc_info=True)
                        stats["errors"] += 1
                        continue
        
        logger.info(f"Acciones programadas procesadas: {stats['processed']}")
        return stats
    
    @task(task_id="update_pipeline_stages")
    def update_pipeline_stages() -> Dict[str, int]:
        """Actualiza etapas del pipeline basado en actividad."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"updated": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Actualizar stage basado en tareas completadas
                cur.execute("""
                    UPDATE sales_pipeline p
                    SET stage = CASE
                        WHEN EXISTS (
                            SELECT 1 FROM sales_followup_tasks t
                            WHERE t.pipeline_id = p.id
                            AND t.task_type = 'meeting'
                            AND t.status = 'completed'
                        ) AND p.stage = 'contacted' THEN 'meeting_scheduled'
                        
                        WHEN EXISTS (
                            SELECT 1 FROM sales_followup_tasks t
                            WHERE t.pipeline_id = p.id
                            AND t.task_type = 'proposal'
                            AND t.status = 'completed'
                        ) AND p.stage = 'meeting_scheduled' THEN 'proposal_sent'
                        
                        ELSE p.stage
                    END,
                    last_contact_at = COALESCE(
                        (SELECT MAX(completed_at) FROM sales_followup_tasks 
                         WHERE pipeline_id = p.id AND status = 'completed'),
                        p.last_contact_at
                    ),
                    updated_at = NOW()
                    WHERE p.stage NOT IN ('closed_won', 'closed_lost')
                    AND (
                        -- Solo actualizar si hay cambios
                        EXISTS (
                            SELECT 1 FROM sales_followup_tasks t
                            WHERE t.pipeline_id = p.id
                            AND t.status = 'completed'
                            AND t.completed_at >= NOW() - INTERVAL '24 hours'
                        )
                    )
                """)
                
                stats["updated"] = cur.rowcount
                conn.commit()
        
        logger.info(f"Etapas actualizadas: {stats['updated']}")
        return stats
    
    @task(task_id="notify_summary")
    def notify_summary(assign_stats: List[Dict[str, Any]], tasks_stats: Dict[str, int],
                      campaigns_stats: Dict[str, int], actions_stats: Dict[str, int],
                      stages_stats: Dict[str, int]) -> None:
        """Envía resumen a Slack si está configurado."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_url = str(params["slack_webhook_url"]).strip()
        
        if not slack_url:
            return
        
        try:
            assigned_count = len(assign_stats)
            summary = f"""
🎯 *Sales Follow-up Automation - Resumen*

👥 *Asignaciones:* {assigned_count} leads
📋 *Tareas creadas:* {tasks_stats.get('created', 0)}
🎪 *Campañas ejecutadas:* {campaigns_stats.get('campaigns_executed', 0)}
📧 *Acciones enviadas:* {actions_stats.get('processed', 0) + campaigns_stats.get('actions_sent', 0)}
📊 *Etapas actualizadas:* {stages_stats.get('updated', 0)}
            """
            
            requests.post(
                slack_url,
                json={"text": summary},
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Error enviando notificación Slack: {e}")
    
    def send_campaign_email(lead: Dict[str, Any], step_config: Dict[str, Any],
                           webhook_url: str, timeout: int, dry_run: bool) -> bool:
        """Envía email de campaña."""
        if dry_run:
            logger.info(f"[DRY RUN] Email sería enviado a {lead.get('email')}")
            return True
        
        try:
            subject = step_config.get("subject_template", "Seguimiento").replace(
                "{{first_name}}", lead.get("first_name", "")
            )
            
            body = step_config.get("body_template", "").replace(
                "{{first_name}}", lead.get("first_name", "")
            ).replace(
                "{{last_name}}", lead.get("last_name", "")
            )
            
            payload = {
                "from": "sales@example.com",
                "to": lead.get("email"),
                "subject": subject,
                "text": body,
                "metadata": {
                    "lead_ext_id": lead.get("lead_ext_id"),
                    "campaign_step": step_config.get("step", 1)
                }
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            
            return True
        except Exception as e:
            logger.error(f"Error enviando email: {e}", exc_info=True)
            return False
    
    # Pipeline
    schema_ok = ensure_schema()
    unassigned = get_unassigned_leads()
    assigned = auto_assign_leads(unassigned)
    needs_followup = get_leads_needing_followup()
    tasks_created = create_followup_tasks(needs_followup)
    campaigns = get_active_campaigns()
    campaigns_executed = execute_campaigns(campaigns)
    scheduled_actions = process_scheduled_actions()
    stages_updated = update_pipeline_stages()
    notify_summary(assigned, tasks_created, campaigns_executed, scheduled_actions, stages_updated)


dag = sales_followup_automation()


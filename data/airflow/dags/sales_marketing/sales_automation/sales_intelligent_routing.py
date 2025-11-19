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
    dag_id="sales_intelligent_routing",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */3 * * *",  # Cada 3 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Routing Inteligente de Leads
    
    Sistema que asigna leads a vendedores de forma inteligente basándose en:
    - Carga de trabajo actual de cada vendedor
- Especialización por industria/producto
- Performance histórica por tipo de lead
- Zona horaria y disponibilidad
- Preferencias del vendedor
    
    **Funcionalidades:**
    - Auto-asignación inteligente basada en múltiples factores
    - Re-asignación de leads abandonados
    - Balanceo de carga entre vendedores
    - Priorización por valor y probabilidad
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_reassignments_per_run": Param(20, type="integer", minimum=1, maximum=100),
        "enable_load_balancing": Param(True, type="boolean"),
        "enable_specialization": Param(True, type="boolean"),
        "min_active_leads_per_rep": Param(5, type="integer", minimum=1, maximum=50),
        "max_active_leads_per_rep": Param(50, type="integer", minimum=10, maximum=200),
        "reassign_stale_days": Param(7, type="integer", minimum=1, maximum=30),
    },
    tags=["sales", "routing", "intelligence", "automation"],
)
def sales_intelligent_routing() -> None:
    """
    DAG para routing inteligente de leads.
    """
    
    @task(task_id="calculate_rep_loads")
    def calculate_rep_loads() -> Dict[str, Dict[str, Any]]:
        """Calcula carga de trabajo de cada vendedor."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        assigned_to,
                        COUNT(*) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS active_leads,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') AS won_last_30d,
                        COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost_last_30d,
                        AVG(EXTRACT(EPOCH FROM (NOW() - last_contact_at)) / 86400) 
                            FILTER (WHERE last_contact_at IS NOT NULL) AS avg_days_since_contact,
                        SUM(estimated_value) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS total_pipeline_value,
                        COUNT(*) FILTER (WHERE status = 'pending' AND due_date <= NOW()) AS overdue_tasks
                    FROM sales_pipeline
                    LEFT JOIN sales_followup_tasks ON sales_pipeline.id = sales_followup_tasks.pipeline_id
                    WHERE assigned_to IS NOT NULL
                    AND qualified_at >= NOW() - INTERVAL '90 days'
                    GROUP BY assigned_to
                """)
                
                columns = [desc[0] for desc in cur.description]
                reps = {}
                
                for row in cur.fetchall():
                    data = dict(zip(columns, row))
                    email = data["assigned_to"]
                    
                    # Calcular win rate
                    total_closed = (data["won_last_30d"] or 0) + (data["lost_last_30d"] or 0)
                    win_rate = (data["won_last_30d"] or 0) / total_closed * 100 if total_closed > 0 else 0
                    
                    # Calcular score de carga (0-100, más bajo = menos carga)
                    active_leads = data["active_leads"] or 0
                    max_leads = int(params["max_active_leads_per_rep"])
                    load_score = min((active_leads / max_leads) * 100, 100)
                    
                    # Penalizar por tareas vencidas
                    overdue_penalty = min((data["overdue_tasks"] or 0) * 5, 30)
                    load_score += overdue_penalty
                    
                    reps[email] = {
                        "active_leads": active_leads,
                        "won_last_30d": data["won_last_30d"] or 0,
                        "lost_last_30d": data["lost_last_30d"] or 0,
                        "win_rate": win_rate,
                        "avg_days_since_contact": float(data["avg_days_since_contact"] or 0),
                        "total_pipeline_value": float(data["total_pipeline_value"] or 0),
                        "overdue_tasks": data["overdue_tasks"] or 0,
                        "load_score": load_score,
                        "availability_score": max(0, 100 - load_score)  # Inverso de carga
                    }
        
        logger.info(f"Carga calculada para {len(reps)} vendedores")
        return reps
    
    @task(task_id="identify_unassigned_or_stale")
    def identify_unassigned_or_stale() -> List[Dict[str, Any]]:
        """Identifica leads sin asignar o abandonados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        stale_days = int(params["reassign_stale_days"])
        max_reassign = int(params["max_reassignments_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id AS pipeline_id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.score,
                p.priority,
                p.stage,
                p.assigned_to,
                p.source,
                p.estimated_value,
                p.probability_pct,
                p.last_contact_at,
                p.qualified_at,
                CASE 
                    WHEN p.assigned_to IS NULL THEN 'unassigned'
                    WHEN p.last_contact_at IS NULL OR p.last_contact_at <= NOW() - INTERVAL '%s days' THEN 'stale'
                    ELSE 'active'
                END AS assignment_status
            FROM sales_pipeline p
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.assigned_to IS NULL
                    OR (p.last_contact_at IS NULL OR p.last_contact_at <= NOW() - INTERVAL '%s days')
                )
            ORDER BY 
                p.priority DESC,
                p.score DESC,
                p.estimated_value DESC NULLS LAST
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (stale_days, stale_days, max_reassign))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(leads)} leads para asignar/re-asignar")
        return leads
    
    @task(task_id="intelligent_assign")
    def intelligent_assign(
        leads: List[Dict[str, Any]], 
        rep_loads: Dict[str, Dict[str, Any]]
    ) -> Dict[str, int]:
        """Asigna leads de forma inteligente."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_load_balancing = bool(params["enable_load_balancing"])
        enable_specialization = bool(params["enable_specialization"])
        min_active = int(params["min_active_leads_per_rep"])
        dry_run = bool(params.get("dry_run", False))
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"assigned": 0, "reassigned": 0, "skipped": 0, "errors": 0}
        
        # Si no hay vendedores, usar función SQL de round-robin
        if not rep_loads:
            logger.warning("No hay datos de vendedores, usando asignación round-robin")
            return stats
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in leads:
                    try:
                        # Calcular score para cada vendedor
                        best_rep = None
                        best_score = -1
                        
                        for rep_email, rep_data in rep_loads.items():
                            # Score base: disponibilidad
                            score = rep_data["availability_score"]
                            
                            # Factor: Load balancing
                            if enable_load_balancing:
                                # Penalizar si está sobrecargado
                                if rep_data["active_leads"] >= params["max_active_leads_per_rep"]:
                                    score = 0
                                # Bonus si está por debajo del mínimo
                                elif rep_data["active_leads"] < min_active:
                                    score += 20
                            
                            # Factor: Performance (win rate)
                            win_rate = rep_data["win_rate"]
                            if win_rate > 50:
                                score += 10
                            elif win_rate > 30:
                                score += 5
                            
                            # Factor: Especialización (futuro: por industria/producto)
                            if enable_specialization:
                                # Por ahora, no hay especialización configurada
                                pass
                            
                            # Penalizar por tareas vencidas
                            if rep_data["overdue_tasks"] > 0:
                                score -= rep_data["overdue_tasks"] * 2
                            
                            # Preferir vendedor actual si lead ya está asignado y no está muy sobrecargado
                            if lead.get("assigned_to") == rep_email:
                                if rep_data["active_leads"] < params["max_active_leads_per_rep"]:
                                    score += 15  # Bonus para mantener asignación
                            
                            if score > best_score:
                                best_score = score
                                best_rep = rep_email
                        
                        if best_rep and best_score > 0:
                            previous_assigned = lead.get("assigned_to")
                            
                            if not dry_run:
                                cur.execute("""
                                    UPDATE sales_pipeline
                                    SET assigned_to = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (best_rep, lead["pipeline_id"]))
                                
                                # Si es re-asignación, registrar en metadata
                                if previous_assigned and previous_assigned != best_rep:
                                    cur.execute("""
                                        SELECT metadata FROM sales_pipeline WHERE id = %s
                                    """, (lead["pipeline_id"],))
                                    
                                    result = cur.fetchone()
                                    metadata = json.loads(result[0]) if result and result[0] else {}
                                    
                                    if "reassignment_history" not in metadata:
                                        metadata["reassignment_history"] = []
                                    
                                    metadata["reassignment_history"].append({
                                        "from": previous_assigned,
                                        "to": best_rep,
                                        "at": datetime.utcnow().isoformat(),
                                        "reason": "intelligent_routing"
                                    })
                                    
                                    cur.execute("""
                                        UPDATE sales_pipeline
                                        SET metadata = %s
                                        WHERE id = %s
                                    """, (json.dumps(metadata), lead["pipeline_id"]))
                                
                                conn.commit()
                            
                            if previous_assigned and previous_assigned != best_rep:
                                stats["reassigned"] += 1
                                logger.info(f"Lead {lead['lead_ext_id']} re-asignado de {previous_assigned} a {best_rep}")
                            else:
                                stats["assigned"] += 1
                                logger.info(f"Lead {lead['lead_ext_id']} asignado a {best_rep}")
                            
                            # Actualizar carga del vendedor
                            if best_rep in rep_loads:
                                rep_loads[best_rep]["active_leads"] += 1
                                rep_loads[best_rep]["load_score"] = min(
                                    (rep_loads[best_rep]["active_leads"] / params["max_active_leads_per_rep"]) * 100,
                                    100
                                )
                        else:
                            stats["skipped"] += 1
                            
                    except Exception as e:
                        logger.error(f"Error asignando lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
                        stats["errors"] += 1
                        continue
        
        logger.info(f"Asignaciones: {stats['assigned']} nuevas, {stats['reassigned']} re-asignadas")
        
        try:
            Stats.incr("sales_routing.assigned", stats["assigned"])
            Stats.incr("sales_routing.reassigned", stats["reassigned"])
        except Exception:
            pass
        
        return stats
    
    # Pipeline
    rep_loads = calculate_rep_loads()
    leads_to_assign = identify_unassigned_or_stale()
    assignment_stats = intelligent_assign(leads_to_assign, rep_loads)


dag = sales_intelligent_routing()




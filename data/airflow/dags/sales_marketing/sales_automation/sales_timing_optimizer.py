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
    dag_id="sales_timing_optimizer",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 0 * * 1",  # Lunes 00:00 (semanal)
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    doc_md="""
    ### Optimizador de Timing de Seguimiento
    
    Analiza datos históricos para optimizar el timing de seguimiento:
    - Identifica mejores días/horas para contactar
    - Optimiza intervalos entre seguimientos
    - Ajusta automáticamente next_followup_at
    - Aprende de patrones de éxito
    - Personaliza timing por tipo de lead
    
    **Funcionalidades:**
    - Análisis de patrones de éxito por timing
    - Optimización de next_followup_at basada en datos
    - Recomendaciones de mejores horas/días
    - Ajuste automático de delays en campañas
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "analysis_days": Param(90, type="integer", minimum=30, maximum=365),
        "enable_auto_optimization": Param(True, type="boolean"),
        "min_data_points": Param(10, type="integer", minimum=5, maximum=100),
    },
    tags=["sales", "optimization", "timing", "analytics"],
)
def sales_timing_optimizer() -> None:
    """
    DAG para optimizar timing de seguimiento.
    """
    
    @task(task_id="analyze_success_patterns")
    def analyze_success_patterns() -> Dict[str, Any]:
        """Analiza patrones de éxito por timing."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        analysis_days = int(params["analysis_days"])
        min_data = int(params["min_data_points"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        patterns = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Análisis por día de la semana
                cur.execute("""
                    SELECT 
                        EXTRACT(DOW FROM t.completed_at) AS day_of_week,
                        COUNT(*) AS total_tasks,
                        COUNT(*) FILTER (WHERE p.stage = 'closed_won') AS won_after_task,
                        ROUND(
                            COUNT(*) FILTER (WHERE p.stage = 'closed_won')::NUMERIC / 
                            NULLIF(COUNT(*), 0) * 100,
                            2
                        ) AS win_rate_pct,
                        AVG(EXTRACT(EPOCH FROM (p.closed_at - t.completed_at) / 86400))
                            FILTER (WHERE p.stage = 'closed_won') AS avg_days_to_close
                    FROM sales_followup_tasks t
                    JOIN sales_pipeline p ON t.pipeline_id = p.id
                    WHERE 
                        t.completed_at >= NOW() - INTERVAL '%s days'
                        AND t.status = 'completed'
                    GROUP BY EXTRACT(DOW FROM t.completed_at)
                    HAVING COUNT(*) >= %s
                    ORDER BY win_rate_pct DESC
                """, (analysis_days, min_data))
                
                columns = [desc[0] for desc in cur.description]
                patterns["by_day_of_week"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
                
                # Análisis por hora del día
                cur.execute("""
                    SELECT 
                        EXTRACT(HOUR FROM t.completed_at) AS hour_of_day,
                        COUNT(*) AS total_tasks,
                        COUNT(*) FILTER (WHERE p.stage = 'closed_won') AS won_after_task,
                        ROUND(
                            COUNT(*) FILTER (WHERE p.stage = 'closed_won')::NUMERIC / 
                            NULLIF(COUNT(*), 0) * 100,
                            2
                        ) AS win_rate_pct
                    FROM sales_followup_tasks t
                    JOIN sales_pipeline p ON t.pipeline_id = p.id
                    WHERE 
                        t.completed_at >= NOW() - INTERVAL '%s days'
                        AND t.status = 'completed'
                    GROUP BY EXTRACT(HOUR FROM t.completed_at)
                    HAVING COUNT(*) >= %s
                    ORDER BY win_rate_pct DESC
                """, (analysis_days, min_data))
                
                columns = [desc[0] for desc in cur.description]
                patterns["by_hour"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
                
                # Análisis por intervalo entre contactos
                cur.execute("""
                    WITH contact_intervals AS (
                        SELECT 
                            p.id,
                            p.lead_ext_id,
                            EXTRACT(EPOCH FROM (
                                t2.completed_at - t1.completed_at
                            ) / 86400) AS days_between_contacts,
                            CASE WHEN p.stage = 'closed_won' THEN 1 ELSE 0 END AS won
                        FROM sales_followup_tasks t1
                        JOIN sales_followup_tasks t2 ON t1.pipeline_id = t2.pipeline_id
                        JOIN sales_pipeline p ON t1.pipeline_id = p.id
                        WHERE 
                            t1.completed_at < t2.completed_at
                            AND t1.completed_at >= NOW() - INTERVAL '%s days'
                            AND t1.status = 'completed'
                            AND t2.status = 'completed'
                    )
                    SELECT 
                        CASE 
                            WHEN days_between_contacts <= 1 THEN '0-1 days'
                            WHEN days_between_contacts <= 3 THEN '2-3 days'
                            WHEN days_between_contacts <= 7 THEN '4-7 days'
                            WHEN days_between_contacts <= 14 THEN '8-14 days'
                            ELSE '15+ days'
                        END AS interval_range,
                        COUNT(*) AS total_cases,
                        SUM(won) AS won_cases,
                        ROUND(SUM(won)::NUMERIC / NULLIF(COUNT(*), 0) * 100, 2) AS win_rate_pct,
                        AVG(days_between_contacts) AS avg_interval
                    FROM contact_intervals
                    GROUP BY interval_range
                    HAVING COUNT(*) >= %s
                    ORDER BY win_rate_pct DESC
                """, (analysis_days, min_data))
                
                columns = [desc[0] for desc in cur.description]
                patterns["by_interval"] = [
                    dict(zip(columns, row)) for row in cur.fetchall()
                ]
        
        logger.info(f"Patrones analizados: {len(patterns)} categorías")
        return patterns
    
    @task(task_id="optimize_followup_timing")
    def optimize_followup_timing(patterns: Dict[str, Any]) -> Dict[str, int]:
        """Optimiza next_followup_at basado en patrones."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_auto = bool(params["enable_auto_optimization"])
        
        if not enable_auto:
            return {"optimized": 0, "skipped": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Determinar mejor intervalo basado en patrones
        best_interval = 3  # Default
        if patterns.get("by_interval"):
            best_range = patterns["by_interval"][0]
            if best_range.get("interval_range") == "2-3 days":
                best_interval = 2
            elif best_range.get("interval_range") == "4-7 days":
                best_interval = 5
        
        stats = {"optimized": 0, "skipped": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Actualizar next_followup_at para leads que no tienen timing optimizado
                cur.execute("""
                    UPDATE sales_pipeline p
                    SET next_followup_at = CASE
                        WHEN p.last_contact_at IS NOT NULL THEN
                            p.last_contact_at + INTERVAL '%s days'
                        WHEN p.qualified_at IS NOT NULL THEN
                            p.qualified_at + INTERVAL '%s days'
                        ELSE
                            NOW() + INTERVAL '%s days'
                    END,
                    updated_at = NOW()
                    WHERE 
                        p.stage NOT IN ('closed_won', 'closed_lost')
                        AND (
                            p.next_followup_at IS NULL
                            OR p.next_followup_at < NOW()
                            OR p.metadata->>'timing_optimized' IS NULL
                        )
                    RETURNING id
                """, (best_interval, best_interval, best_interval))
                
                updated_ids = [row[0] for row in cur.fetchall()]
                
                # Marcar como optimizado en metadata
                for pipeline_id in updated_ids:
                    cur.execute("""
                        SELECT metadata FROM sales_pipeline WHERE id = %s
                    """, (pipeline_id,))
                    
                    result = cur.fetchone()
                    metadata = json.loads(result[0]) if result and result[0] else {}
                    
                    metadata["timing_optimized"] = {
                        "optimized_at": datetime.utcnow().isoformat(),
                        "optimal_interval_days": best_interval,
                        "based_on_patterns": True
                    }
                    
                    cur.execute("""
                        UPDATE sales_pipeline
                        SET metadata = %s
                        WHERE id = %s
                    """, (json.dumps(metadata), pipeline_id))
                
                conn.commit()
                stats["optimized"] = len(updated_ids)
        
        logger.info(f"Timing optimizado para {stats['optimized']} leads")
        
        try:
            Stats.incr("sales_timing.optimized", stats["optimized"])
        except Exception:
            pass
        
        return stats
    
    @task(task_id="update_campaign_delays")
    def update_campaign_delays(patterns: Dict[str, Any]) -> Dict[str, int]:
        """Actualiza delays en campañas basado en patrones óptimos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_auto = bool(params["enable_auto_optimization"])
        
        if not enable_auto:
            return {"updated": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Determinar delay óptimo
        best_interval = 3
        if patterns.get("by_interval"):
            best_range = patterns["by_interval"][0]
            if best_range.get("interval_range") == "2-3 days":
                best_interval = 2
            elif best_range.get("interval_range") == "4-7 days":
                best_interval = 5
        
        stats = {"updated": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Actualizar delays en campañas activas (solo si no tienen delays personalizados)
                cur.execute("""
                    UPDATE sales_campaigns
                    SET steps_config = jsonb_set(
                        steps_config,
                        '{0,delay_hours}',
                        to_jsonb((%s * 24)::int),
                        true
                    ),
                    updated_at = NOW()
                    WHERE enabled = true
                    AND steps_config->0->>'delay_hours' IS NULL
                    OR (steps_config->0->>'delay_hours')::int = 24  -- Default
                """, (best_interval,))
                
                stats["updated"] = cur.rowcount
                conn.commit()
        
        logger.info(f"Delays actualizados en {stats['updated']} campañas")
        return stats
    
    # Pipeline
    patterns = analyze_success_patterns()
    timing_optimized = optimize_followup_timing(patterns)
    campaigns_updated = update_campaign_delays(patterns)


dag = sales_timing_optimizer()




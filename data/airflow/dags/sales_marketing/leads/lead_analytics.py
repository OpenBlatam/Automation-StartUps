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
    dag_id="lead_analytics",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 0 * * *",  # Diario a medianoche
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Analytics y Reportes de Leads
    
    Genera analytics y reportes diarios del pipeline:
    - Conversión por etapa
    - Tiempo promedio en cada etapa
    - Velocidad de respuesta
    - Tasa de conversión
    - Pipeline value
    - Performance por vendedor
    - Performance por fuente
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `generate_daily_report`: Generar reporte diario (default: true)
    - `export_to_file`: Exportar a archivo (default: false)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "generate_daily_report": Param(True, type="boolean"),
        "export_to_file": Param(False, type="boolean"),
        "report_days": Param(30, type="integer", minimum=1, maximum=365),
    },
    tags=["sales", "leads", "analytics", "reporting"],
)
def lead_analytics() -> None:
    """
    DAG para analytics y reportes de leads.
    """
    
    @task(task_id="calculate_analytics")
    def calculate_analytics() -> Dict[str, Any]:
        """Calcula métricas y analytics."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        report_days = int(params["report_days"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        analytics = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Pipeline Overview
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE stage = 'qualified') AS qualified_count,
                        COUNT(*) FILTER (WHERE stage = 'contacted') AS contacted_count,
                        COUNT(*) FILTER (WHERE stage = 'meeting_scheduled') AS meeting_scheduled_count,
                        COUNT(*) FILTER (WHERE stage = 'proposal_sent') AS proposal_sent_count,
                        COUNT(*) FILTER (WHERE stage = 'negotiating') AS negotiating_count,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') AS closed_won_count,
                        COUNT(*) FILTER (WHERE stage = 'closed_lost') AS closed_lost_count,
                        AVG(score) AS avg_score,
                        SUM(estimated_value) FILTER (WHERE stage NOT IN ('closed_lost')) AS total_pipeline_value,
                        COUNT(*) FILTER (WHERE assigned_to IS NULL) AS unassigned_count
                    FROM sales_pipeline
                    WHERE stage NOT IN ('closed_won', 'closed_lost')
                        OR created_at >= NOW() - INTERVAL '%s days'
                """, (report_days,))
                
                columns = [desc[0] for desc in cur.description]
                pipeline_overview = dict(zip(columns, cur.fetchone()))
                
                # Conversión por etapa
                cur.execute("""
                    WITH stage_counts AS (
                        SELECT 
                            stage,
                            COUNT(*) as count
                        FROM sales_pipeline
                        WHERE created_at >= NOW() - INTERVAL '%s days'
                        GROUP BY stage
                    )
                    SELECT 
                        stage,
                        count,
                        ROUND(100.0 * count / SUM(count) OVER (), 2) as percentage
                    FROM stage_counts
                    ORDER BY 
                        CASE stage
                            WHEN 'qualified' THEN 1
                            WHEN 'contacted' THEN 2
                            WHEN 'meeting_scheduled' THEN 3
                            WHEN 'proposal_sent' THEN 4
                            WHEN 'negotiating' THEN 5
                            WHEN 'closed_won' THEN 6
                            WHEN 'closed_lost' THEN 7
                        END
                """, (report_days,))
                
                columns = [desc[0] for desc in cur.description]
                conversion_by_stage = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Performance por fuente
                cur.execute("""
                    SELECT 
                        source,
                        COUNT(*) as lead_count,
                        AVG(score) as avg_score,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') as won_count,
                        ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'closed_won') / COUNT(*), 2) as conversion_rate,
                        SUM(estimated_value) FILTER (WHERE stage = 'closed_won') as total_won_value
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY source
                    ORDER BY lead_count DESC
                """, (report_days,))
                
                columns = [desc[0] for desc in cur.description]
                performance_by_source = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Performance por vendedor
                cur.execute("""
                    SELECT 
                        assigned_to,
                        COUNT(*) as lead_count,
                        AVG(score) as avg_score,
                        COUNT(*) FILTER (WHERE stage = 'closed_won') as won_count,
                        ROUND(100.0 * COUNT(*) FILTER (WHERE stage = 'closed_won') / COUNT(*), 2) as conversion_rate,
                        SUM(estimated_value) FILTER (WHERE stage = 'closed_won') as total_won_value,
                        AVG(EXTRACT(EPOCH FROM (last_contact_at - qualified_at))/86400) as avg_days_to_contact
                    FROM sales_pipeline
                    WHERE assigned_to IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY assigned_to
                    ORDER BY won_count DESC
                """, (report_days,))
                
                columns = [desc[0] for desc in cur.description]
                performance_by_rep = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Tiempo promedio en cada etapa
                cur.execute("""
                    SELECT 
                        stage,
                        AVG(EXTRACT(EPOCH FROM (updated_at - created_at))/86400) as avg_days_in_stage
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                        AND stage NOT IN ('closed_won', 'closed_lost')
                    GROUP BY stage
                    ORDER BY 
                        CASE stage
                            WHEN 'qualified' THEN 1
                            WHEN 'contacted' THEN 2
                            WHEN 'meeting_scheduled' THEN 3
                            WHEN 'proposal_sent' THEN 4
                            WHEN 'negotiating' THEN 5
                        END
                """, (report_days,))
                
                columns = [desc[0] for desc in cur.description]
                time_in_stage = [dict(zip(columns, row)) for row in cur.fetchall()]
                
                # Trends (leads creados por día)
                cur.execute("""
                    SELECT 
                        DATE(created_at) as date,
                        COUNT(*) as lead_count,
                        COUNT(*) FILTER (WHERE priority = 'high') as high_priority_count
                    FROM sales_pipeline
                    WHERE created_at >= NOW() - INTERVAL '%s days'
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                """, (report_days,))
                
                columns = [desc[0] for desc in cur.description]
                daily_trends = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        analytics = {
            "pipeline_overview": pipeline_overview,
            "conversion_by_stage": conversion_by_stage,
            "performance_by_source": performance_by_source,
            "performance_by_rep": performance_by_rep,
            "time_in_stage": time_in_stage,
            "daily_trends": daily_trends,
            "report_date": datetime.utcnow().isoformat(),
            "report_period_days": report_days
        }
        
        logger.info(f"Analytics calculados para últimos {report_days} días")
        return analytics
    
    @task(task_id="save_analytics")
    def save_analytics(analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda analytics en base de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params.get("dry_run", False))
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Crear tabla de analytics si no existe
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS lead_analytics (
                        id SERIAL PRIMARY KEY,
                        report_date DATE NOT NULL,
                        report_data JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        UNIQUE(report_date)
                    )
                """)
                
                if not dry_run:
                    cur.execute("""
                        INSERT INTO lead_analytics (report_date, report_data)
                        VALUES (%s, %s::jsonb)
                        ON CONFLICT (report_date) DO UPDATE SET
                            report_data = EXCLUDED.report_data,
                            created_at = NOW()
                    """, (datetime.utcnow().date(), json.dumps(analytics)))
                    
                    conn.commit()
                    logger.info("Analytics guardados en base de datos")
                else:
                    logger.info("[DRY RUN] Analytics serían guardados")
        
        return {"saved": True}
    
    # Pipeline
    analytics = calculate_analytics()
    save_analytics(analytics)


dag = lead_analytics()


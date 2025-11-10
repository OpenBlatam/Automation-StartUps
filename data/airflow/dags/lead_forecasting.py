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
    dag_id="lead_forecasting",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 0 * * 1",  # Semanal (lunes)
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Forecasting y Predicciones
    
    Genera predicciones y forecasting:
    - Predicción de conversión por lead
    - Forecasting de pipeline value
    - Predicción de tiempo de cierre
    - Tendencias de pipeline
    - Predicción de necesidades de leads
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `forecast_days`: Días a predecir (default: 30)
    - `confidence_level`: Nivel de confianza (default: 0.8)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "forecast_days": Param(30, type="integer", minimum=7, maximum=90),
        "confidence_level": Param(0.8, type="number", minimum=0.5, maximum=0.99),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "forecasting", "analytics"],
)
def lead_forecasting() -> None:
    """
    DAG para forecasting y predicciones.
    """
    
    @task(task_id="calculate_forecasts")
    def calculate_forecasts() -> Dict[str, Any]:
        """Calcula predicciones y forecasting."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        forecast_days = int(params["forecast_days"])
        confidence = float(params["confidence_level"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        forecasts = {}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Pipeline Value Forecast
                cur.execute("""
                    WITH historical_conversion AS (
                        SELECT 
                            AVG(CASE WHEN stage = 'closed_won' THEN estimated_value ELSE 0 END) as avg_deal_value,
                            COUNT(*) FILTER (WHERE stage = 'closed_won')::float / NULLIF(COUNT(*), 0) as conversion_rate
                        FROM sales_pipeline
                        WHERE qualified_at >= NOW() - INTERVAL '90 days'
                    ),
                    current_pipeline AS (
                        SELECT 
                            COUNT(*) as total_leads,
                            SUM(estimated_value) as total_value,
                            AVG(score) as avg_score,
                            AVG(probability_pct) as avg_probability
                        FROM sales_pipeline
                        WHERE stage NOT IN ('closed_won', 'closed_lost')
                    )
                    SELECT 
                        cp.total_leads,
                        cp.total_value,
                        cp.avg_score,
                        cp.avg_probability,
                        hc.avg_deal_value,
                        hc.conversion_rate,
                        (cp.total_leads * hc.conversion_rate * hc.avg_deal_value) as forecasted_value
                    FROM current_pipeline cp
                    CROSS JOIN historical_conversion hc
                """)
                
                forecast_row = cur.fetchone()
                if forecast_row:
                    forecasts["pipeline_value"] = {
                        "current_pipeline_value": float(forecast_row[1] or 0),
                        "forecasted_value": float(forecast_row[6] or 0),
                        "conversion_rate": float(forecast_row[5] or 0),
                        "avg_deal_value": float(forecast_row[4] or 0),
                        "confidence": confidence
                    }
                
                # Time to Close Forecast
                cur.execute("""
                    SELECT 
                        AVG(EXTRACT(EPOCH FROM (updated_at - qualified_at))/86400) as avg_days_to_close,
                        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (updated_at - qualified_at))/86400) as median_days_to_close
                    FROM sales_pipeline
                    WHERE stage = 'closed_won'
                        AND qualified_at >= NOW() - INTERVAL '90 days'
                """)
                
                time_row = cur.fetchone()
                if time_row:
                    forecasts["time_to_close"] = {
                        "avg_days": float(time_row[0] or 0),
                        "median_days": float(time_row[1] or 0)
                    }
                
                # Lead Generation Forecast
                cur.execute("""
                    WITH daily_leads AS (
                        SELECT 
                            DATE(created_at) as date,
                            COUNT(*) as lead_count
                        FROM sales_pipeline
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                        GROUP BY DATE(created_at)
                    )
                    SELECT 
                        AVG(lead_count) as avg_daily_leads,
                        STDDEV(lead_count) as stddev_daily_leads
                    FROM daily_leads
                """)
                
                gen_row = cur.fetchone()
                if gen_row:
                    avg_daily = float(gen_row[0] or 0)
                    stddev_daily = float(gen_row[1] or 0)
                    
                    # Predicción con intervalo de confianza
                    from scipy import stats
                    try:
                        z_score = stats.norm.ppf((1 + confidence) / 2)
                        forecast_min = avg_daily * forecast_days - z_score * stddev_daily * (forecast_days ** 0.5)
                        forecast_max = avg_daily * forecast_days + z_score * stddev_daily * (forecast_days ** 0.5)
                    except:
                        forecast_min = avg_daily * forecast_days * 0.8
                        forecast_max = avg_daily * forecast_days * 1.2
                    
                    forecasts["lead_generation"] = {
                        "avg_daily_leads": avg_daily,
                        "forecast_min": forecast_min,
                        "forecast_max": forecast_max,
                        "forecast_days": forecast_days,
                        "confidence": confidence
                    }
        
        forecasts["calculated_at"] = datetime.utcnow().isoformat()
        
        logger.info(f"Forecasting calculado para {forecast_days} días")
        return forecasts
    
    @task(task_id="save_forecasts")
    def save_forecasts(forecasts: Dict[str, Any]) -> Dict[str, Any]:
        """Guarda forecasts en base de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla si no existe
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS lead_forecasts (
                        id SERIAL PRIMARY KEY,
                        forecast_date DATE NOT NULL,
                        forecast_data JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        UNIQUE(forecast_date)
                    )
                """)
                
                if not dry_run:
                    cur.execute("""
                        INSERT INTO lead_forecasts (forecast_date, forecast_data)
                        VALUES (%s, %s::jsonb)
                        ON CONFLICT (forecast_date) DO UPDATE SET
                            forecast_data = EXCLUDED.forecast_data,
                            created_at = NOW()
                    """, (datetime.utcnow().date(), json.dumps(forecasts)))
                    
                    conn.commit()
                    logger.info("Forecasts guardados en base de datos")
                else:
                    logger.info("[DRY RUN] Forecasts serían guardados")
        
        return {"saved": True}
    
    # Pipeline
    forecasts = calculate_forecasts()
    save_forecasts(forecasts)


dag = lead_forecasting()


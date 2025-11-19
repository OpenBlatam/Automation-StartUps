"""
DAG para Exportación de Datos de Tickets de Soporte

Exporta datos para análisis externo:
- CSV de tickets
- JSON de métricas
- Excel con reporte completo
- Envío a data warehouse
"""
import logging
import os
import csv
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from io import StringIO

try:
    from airflow import DAG
    from airflow.decorators import task, dag
    from airflow.utils.dates import days_ago
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    from airflow.providers.filesystem.hooks.filesystem import FSHook
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "support",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}

EXPORT_BASE_PATH = os.getenv("SUPPORT_EXPORT_PATH", "/tmp/support_exports")


@dag(
    dag_id="support_tickets_export",
    start_date=days_ago(1),
    schedule="0 2 * * *",  # Diario a las 2 AM
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Exportación diaria de datos de tickets de soporte",
    tags=["support", "export", "data-warehouse"],
)
def support_tickets_export():
    """DAG para exportar datos de tickets."""
    
    @task(task_id="export_tickets_csv")
    def export_tickets_csv() -> str:
        """Exporta tickets a CSV."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            # Exportar últimos 30 días
            query = """
                SELECT 
                    ticket_id,
                    source,
                    subject,
                    description,
                    customer_email,
                    customer_name,
                    category,
                    priority,
                    priority_score,
                    status,
                    assigned_department,
                    assigned_agent_name,
                    chatbot_resolved,
                    created_at,
                    resolved_at,
                    time_to_first_response_minutes,
                    time_to_resolution_minutes,
                    customer_satisfaction_score
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '30 days'
                ORDER BY created_at DESC
            """
            
            df = pd.read_sql_query(query, conn)
            
            # Crear directorio si no existe
            os.makedirs(EXPORT_BASE_PATH, exist_ok=True)
            
            # Exportar CSV
            csv_path = f"{EXPORT_BASE_PATH}/tickets_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Exported {len(df)} tickets to {csv_path}")
            return csv_path
    
    @task(task_id="export_metrics_json")
    def export_metrics_json() -> str:
        """Exporta métricas a JSON."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Métricas del día anterior
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_tickets,
                        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
                        COUNT(*) FILTER (WHERE status = 'resolved') as manually_resolved,
                        AVG(priority_score) as avg_priority_score,
                        AVG(time_to_first_response_minutes) as avg_first_response,
                        AVG(time_to_resolution_minutes) as avg_resolution,
                        AVG(customer_satisfaction_score) as avg_satisfaction
                    FROM support_tickets
                    WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
                """)
                
                row = cur.fetchone()
                metrics = {
                    "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
                    "total_tickets": row[0] or 0,
                    "chatbot_resolved": row[1] or 0,
                    "manually_resolved": row[2] or 0,
                    "avg_priority_score": float(row[3]) if row[3] else 0.0,
                    "avg_first_response_minutes": float(row[4]) if row[4] else None,
                    "avg_resolution_minutes": float(row[5]) if row[5] else None,
                    "avg_satisfaction": float(row[6]) if row[6] else None
                }
                
                # Distribución por prioridad
                cur.execute("""
                    SELECT priority, COUNT(*)
                    FROM support_tickets
                    WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
                    GROUP BY priority
                """)
                metrics["priority_distribution"] = {
                    row[0]: row[1] for row in cur.fetchall()
                }
                
                # Distribución por categoría
                cur.execute("""
                    SELECT category, COUNT(*)
                    FROM support_tickets
                    WHERE DATE(created_at) = CURRENT_DATE - INTERVAL '1 day'
                    AND category IS NOT NULL
                    GROUP BY category
                """)
                metrics["category_distribution"] = {
                    row[0]: row[1] for row in cur.fetchall()
                }
        
        # Guardar JSON
        os.makedirs(EXPORT_BASE_PATH, exist_ok=True)
        json_path = f"{EXPORT_BASE_PATH}/metrics_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(json_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Exported metrics to {json_path}")
        return json_path
    
    @task(task_id="export_feedback_data")
    def export_feedback_data() -> str:
        """Exporta datos de feedback."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            query = """
                SELECT 
                    f.ticket_id,
                    f.customer_email,
                    f.satisfaction_score,
                    f.response_time_rating,
                    f.resolution_quality_rating,
                    f.feedback_text,
                    f.would_recommend,
                    f.chatbot_was_helpful,
                    f.agent_was_helpful,
                    f.submitted_at,
                    t.assigned_agent_name,
                    t.category
                FROM support_ticket_feedback f
                INNER JOIN support_tickets t ON f.ticket_id = t.ticket_id
                WHERE f.submitted_at >= NOW() - INTERVAL '30 days'
                ORDER BY f.submitted_at DESC
            """
            
            df = pd.read_sql_query(query, conn)
            
            # Exportar CSV
            os.makedirs(EXPORT_BASE_PATH, exist_ok=True)
            csv_path = f"{EXPORT_BASE_PATH}/feedback_{datetime.now().strftime('%Y%m%d')}.csv"
            df.to_csv(csv_path, index=False)
            
            logger.info(f"Exported {len(df)} feedback entries to {csv_path}")
            return csv_path
    
    @task(task_id="upload_to_data_warehouse")
    def upload_to_data_warehouse(
        tickets_path: str,
        metrics_path: str,
        feedback_path: str
    ) -> Dict[str, Any]:
        """Sube archivos exportados a data warehouse (opcional)."""
        # Aquí se integraría con S3, GCS, Azure Blob, etc.
        # Por ahora solo retorna información
        
        result = {
            "tickets_exported": tickets_path,
            "metrics_exported": metrics_path,
            "feedback_exported": feedback_path,
            "uploaded_to_dw": False  # Implementar cuando haya data warehouse
        }
        
        logger.info(f"Export files ready for data warehouse: {result}")
        return result
    
    # Pipeline
    tickets_csv = export_tickets_csv()
    metrics_json = export_metrics_json()
    feedback_csv = export_feedback_data()
    upload_to_data_warehouse(tickets_csv, metrics_json, feedback_csv)


dag = support_tickets_export()


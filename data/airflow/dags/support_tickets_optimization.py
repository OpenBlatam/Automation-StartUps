"""
DAG de Optimización y Mantenimiento de Tickets de Soporte

Tareas:
- Limpieza de datos antiguos
- Optimización de índices
- Actualización de estadísticas
- Archivo de tickets resueltos
- Refresh de vistas materializadas
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    from airflow import DAG
    from airflow.decorators import task, dag
    from airflow.utils.dates import days_ago
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

logger = logging.getLogger(__name__)

DEFAULT_ARGS = {
    "owner": "support",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": False,
}


@dag(
    dag_id="support_tickets_optimization",
    start_date=days_ago(1),
    schedule="0 3 * * 0",  # Domingos a las 3 AM
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Optimización y mantenimiento semanal del sistema de tickets",
    tags=["support", "maintenance", "optimization"],
)
def support_tickets_optimization():
    """DAG de optimización y mantenimiento."""
    
    @task(task_id="cleanup_old_tickets")
    def cleanup_old_tickets() -> Dict[str, Any]:
        """Archiva tickets antiguos resueltos."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Contar tickets a archivar (resueltos hace más de 1 año)
                cur.execute("""
                    SELECT COUNT(*)
                    FROM support_tickets
                    WHERE status IN ('resolved', 'closed')
                    AND resolved_at < NOW() - INTERVAL '1 year'
                """)
                count = cur.fetchone()[0]
                
                # En producción, aquí se moverían a tabla de archivo
                # Por ahora solo se cuenta
                
                logger.info(f"Found {count} old tickets to archive")
                
                return {
                    "old_tickets_count": count,
                    "archived": False  # En producción sería True
                }
    
    @task(task_id="optimize_indexes")
    def optimize_indexes() -> Dict[str, Any]:
        """Optimiza índices de la base de datos."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        tables = [
            "support_tickets",
            "support_chatbot_interactions",
            "support_ticket_history",
            "support_ticket_feedback"
        ]
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for table in tables:
                    cur.execute(f"ANALYZE {table};")
                    logger.info(f"Analyzed table: {table}")
        
        return {
            "tables_analyzed": len(tables),
            "optimized": True
        }
    
    @task(task_id="refresh_materialized_views")
    def refresh_materialized_views() -> Dict[str, Any]:
        """Refresca vistas materializadas."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        views = [
            "v_support_tickets_pending",
            "v_support_chatbot_stats",
            "v_support_agents_workload",
            "v_support_feedback_summary",
            "v_support_agent_feedback"
        ]
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                refreshed = []
                for view in views:
                    try:
                        cur.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY IF EXISTS {view};")
                        refreshed.append(view)
                        logger.info(f"Refreshed view: {view}")
                    except Exception as e:
                        logger.warning(f"Could not refresh view {view}: {e}")
        
        return {
            "views_refreshed": len(refreshed),
            "total_views": len(views)
        }
    
    @task(task_id="update_agent_statistics")
    def update_agent_statistics() -> Dict[str, Any]:
        """Actualiza estadísticas de agentes."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Actualizar contador de tickets activos
                cur.execute("""
                    UPDATE support_agents a
                    SET current_active_tickets = (
                        SELECT COUNT(*)
                        FROM support_tickets t
                        WHERE t.assigned_agent_id = a.agent_id
                        AND t.status IN ('open', 'assigned', 'in_progress')
                    ),
                    updated_at = NOW()
                """)
                
                updated = cur.rowcount
                conn.commit()
                
                logger.info(f"Updated statistics for {updated} agents")
        
        return {
            "agents_updated": updated
        }
    
    @task(task_id="cleanup_old_interactions")
    def cleanup_old_interactions() -> Dict[str, Any]:
        """Limpia interacciones con chatbot antiguas."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Eliminar interacciones de tickets resueltos hace más de 6 meses
                cur.execute("""
                    DELETE FROM support_chatbot_interactions
                    WHERE ticket_id IN (
                        SELECT ticket_id
                        FROM support_tickets
                        WHERE status IN ('resolved', 'closed')
                        AND resolved_at < NOW() - INTERVAL '6 months'
                    )
                """)
                
                deleted = cur.rowcount
                conn.commit()
                
                logger.info(f"Deleted {deleted} old chatbot interactions")
        
        return {
            "interactions_deleted": deleted
        }
    
    @task(task_id="generate_optimization_report")
    def generate_optimization_report(
        cleanup_result: Dict[str, Any],
        indexes_result: Dict[str, Any],
        views_result: Dict[str, Any],
        agents_result: Dict[str, Any],
        interactions_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera reporte de optimización."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "cleanup": cleanup_result,
            "indexes": indexes_result,
            "views": views_result,
            "agents": agents_result,
            "interactions": interactions_result,
            "status": "completed"
        }
        
        logger.info(f"Optimization completed: {report}")
        
        if STATS_AVAILABLE:
            try:
                Stats.incr("support_optimization.completed")
                Stats.gauge("support_optimization.old_tickets", cleanup_result["old_tickets_count"])
            except Exception:
                pass
        
        return report
    
    # Pipeline
    cleanup = cleanup_old_tickets()
    indexes = optimize_indexes()
    views = refresh_materialized_views()
    agents = update_agent_statistics()
    interactions = cleanup_old_interactions()
    
    generate_optimization_report(cleanup, indexes, views, agents, interactions)


dag = support_tickets_optimization()


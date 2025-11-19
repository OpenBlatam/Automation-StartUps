"""
DAG de Análisis de ROI y Costos del Sistema de Soporte

Analiza:
- Costos de operación
- Ahorros por automatización
- ROI del chatbot
- Costo por ticket resuelto
- Comparación con sistema manual
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    from airflow import DAG
    from airflow.decorators import task, dag
    from airflow.utils.dates import days_ago
    from airflow.providers.postgres.hooks.postgres import PostgresHook
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

# Configuración de costos (ajustar según tu caso)
COST_PER_AGENT_HOUR = 25.0  # Costo por hora de agente
COST_CHATBOT_API_CALL = 0.001  # Costo por llamada a OpenAI
AVG_TICKETS_PER_HOUR = 5  # Tickets promedio que un agente puede manejar


@dag(
    dag_id="support_tickets_roi_analysis",
    start_date=days_ago(1),
    schedule="0 0 * * 1",  # Semanal, lunes a medianoche
    catchup=False,
    default_args=DEFAULT_ARGS,
    description="Análisis de ROI y costos del sistema de soporte",
    tags=["support", "analytics", "roi"],
)
def support_tickets_roi_analysis():
    """DAG de análisis de ROI."""
    
    @task(task_id="calculate_automation_savings")
    def calculate_automation_savings() -> Dict[str, Any]:
        """Calcula ahorros por automatización."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Tickets resueltos por chatbot
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
                        COUNT(*) FILTER (WHERE chatbot_attempted = true) as chatbot_attempted,
                        AVG(time_to_resolution_minutes) FILTER (WHERE chatbot_resolved = true) as avg_chatbot_resolution
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND chatbot_attempted = true
                """)
                
                row = cur.fetchone()
                chatbot_resolved = row[0] or 0
                chatbot_attempted = row[1] or 0
                avg_chatbot_resolution = float(row[2]) if row[2] else 0.0
                
                # Tickets resueltos manualmente
                cur.execute("""
                    SELECT 
                        COUNT(*) as manually_resolved,
                        AVG(time_to_resolution_minutes) as avg_manual_resolution
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND chatbot_resolved = false
                    AND status = 'resolved'
                """)
                
                row = cur.fetchone()
                manually_resolved = row[0] or 0
                avg_manual_resolution = float(row[1]) if row[1] else 0.0
                
                # Calcular costos
                # Costo chatbot: número de llamadas API
                chatbot_cost = chatbot_attempted * COST_CHATBOT_API_CALL
                
                # Costo manual: tiempo de agentes
                manual_hours = (manually_resolved * avg_manual_resolution) / 60.0
                manual_cost = manual_hours * COST_PER_AGENT_HOUR
                
                # Ahorro estimado (si chatbot no existiera, todos serían manuales)
                chatbot_resolution_hours = (chatbot_resolved * avg_chatbot_resolution) / 60.0
                saved_cost = chatbot_resolution_hours * COST_PER_AGENT_HOUR
                net_savings = saved_cost - chatbot_cost
                
                # ROI
                roi = (net_savings / chatbot_cost * 100) if chatbot_cost > 0 else 0.0
                
                return {
                    "period_days": 30,
                    "chatbot_resolved": chatbot_resolved,
                    "manually_resolved": manually_resolved,
                    "chatbot_cost": chatbot_cost,
                    "manual_cost": manual_cost,
                    "saved_cost": saved_cost,
                    "net_savings": net_savings,
                    "roi_percentage": roi,
                    "avg_chatbot_resolution_minutes": avg_chatbot_resolution,
                    "avg_manual_resolution_minutes": avg_manual_resolution
                }
    
    @task(task_id="calculate_cost_per_ticket")
    def calculate_cost_per_ticket() -> Dict[str, Any]:
        """Calcula costo por ticket resuelto."""
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Total de tickets resueltos
                cur.execute("""
                    SELECT 
                        COUNT(*) as total_resolved,
                        COUNT(*) FILTER (WHERE chatbot_resolved = true) as chatbot_resolved,
                        COUNT(*) FILTER (WHERE chatbot_resolved = false) as manually_resolved,
                        SUM(time_to_resolution_minutes) FILTER (WHERE chatbot_resolved = false) as total_manual_minutes
                    FROM support_tickets
                    WHERE created_at >= NOW() - INTERVAL '30 days'
                    AND status = 'resolved'
                """)
                
                row = cur.fetchone()
                total_resolved = row[0] or 0
                chatbot_resolved = row[1] or 0
                manually_resolved = row[2] or 0
                total_manual_minutes = float(row[3]) if row[3] else 0.0
                
                # Costos
                chatbot_cost = chatbot_resolved * COST_CHATBOT_API_CALL
                manual_hours = total_manual_minutes / 60.0
                manual_cost = manual_hours * COST_PER_AGENT_HOUR
                total_cost = chatbot_cost + manual_cost
                
                # Costo por ticket
                cost_per_ticket = total_cost / total_resolved if total_resolved > 0 else 0.0
                cost_per_chatbot_ticket = chatbot_cost / chatbot_resolved if chatbot_resolved > 0 else 0.0
                cost_per_manual_ticket = manual_cost / manually_resolved if manually_resolved > 0 else 0.0
                
                return {
                    "total_resolved": total_resolved,
                    "total_cost": total_cost,
                    "cost_per_ticket": cost_per_ticket,
                    "cost_per_chatbot_ticket": cost_per_chatbot_ticket,
                    "cost_per_manual_ticket": cost_per_manual_ticket,
                    "chatbot_vs_manual_savings": cost_per_manual_ticket - cost_per_chatbot_ticket
                }
    
    @task(task_id="generate_roi_report")
    def generate_roi_report(
        savings: Dict[str, Any],
        costs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera reporte completo de ROI."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "period_days": 30,
            "automation": {
                "chatbot_resolved": savings["chatbot_resolved"],
                "chatbot_cost": savings["chatbot_cost"],
                "saved_cost": savings["saved_cost"],
                "net_savings": savings["net_savings"],
                "roi_percentage": savings["roi_percentage"]
            },
            "costs": {
                "total_cost": costs["total_cost"],
                "cost_per_ticket": costs["cost_per_ticket"],
                "cost_per_chatbot_ticket": costs["cost_per_chatbot_ticket"],
                "cost_per_manual_ticket": costs["cost_per_manual_ticket"],
                "savings_per_ticket": costs["chatbot_vs_manual_savings"]
            },
            "recommendations": []
        }
        
        # Generar recomendaciones
        if savings["roi_percentage"] > 300:
            report["recommendations"].append("Excelente ROI - Considerar expandir uso del chatbot")
        elif savings["roi_percentage"] > 100:
            report["recommendations"].append("Buen ROI - Sistema funcionando eficientemente")
        elif savings["roi_percentage"] > 0:
            report["recommendations"].append("ROI positivo - Revisar optimizaciones")
        else:
            report["recommendations"].append("ROI negativo - Revisar configuración del chatbot")
        
        if costs["chatbot_vs_manual_savings"] > 5:
            report["recommendations"].append(f"Ahorro significativo por ticket: ${costs['chatbot_vs_manual_savings']:.2f}")
        
        logger.info(f"ROI Report generated: {report}")
        return report
    
    # Pipeline
    savings = calculate_automation_savings()
    costs = calculate_cost_per_ticket()
    generate_roi_report(savings, costs)


dag = support_tickets_roi_analysis()


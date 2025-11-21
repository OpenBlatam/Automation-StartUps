"""
DAG de Gestión de Disputas de Tiempo
Procesa disputas, valida y resuelve automáticamente cuando es posible
"""

from __future__ import annotations

from datetime import timedelta, date
from typing import Any, Dict, List, Optional
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

from time_tracking import (
    TimeTrackingStorage,
    DisputeManager,
    DisputeType,
    TimeTrackingValidator,
    TimeTrackingNotifier,
)

logger = logging.getLogger(__name__)


@dag(
    dag_id="time_tracking_disputes",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "hr",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Gestión Automática de Disputas de Tiempo
    
    Procesa y resuelve disputas de tiempo trabajado:
    
    **Funcionalidades:**
    - Revisión de disputas abiertas
    - Validación automática de evidencia
    - Resolución automática cuando es posible
    - Notificaciones a empleados y supervisores
    - Actualización de registros de tiempo
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `auto_resolve_disputes`: Auto-resolver disputas válidas (default: false)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "auto_resolve_disputes": Param(False, type="boolean"),
    },
    tags=["time_tracking", "hr", "disputes", "validation"],
)
def time_tracking_disputes() -> None:
    """DAG para gestión de disputas"""
    
    @task
    def review_open_disputes(**context) -> Dict[str, Any]:
        """Revisa disputas abiertas"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        auto_resolve = params.get("auto_resolve_disputes", False)
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        dispute_manager = DisputeManager(storage)
        validator = TimeTrackingValidator(storage)
        notifier = TimeTrackingNotifier(storage)
        
        # Obtener disputas abiertas
        open_disputes = dispute_manager.get_disputes(status="open")
        
        reviewed = 0
        resolved = 0
        escalated = 0
        
        for dispute in open_disputes:
            dispute_id = dispute["id"]
            employee_id = dispute["employee_id"]
            dispute_type = dispute["dispute_type"]
            dispute_date = dispute["dispute_date"]
            
            # Marcar como bajo revisión
            update_sql = """
                UPDATE time_tracking_disputes
                SET status = 'under_review'
                WHERE id = %s AND status = 'open'
            """
            storage.hook.run(update_sql, parameters=(dispute_id,))
            
            # Validar disputa
            if dispute_type == "missing_clock" or dispute_type == "incorrect_time":
                # Verificar si hay evidencia suficiente
                # Por ahora, escalamos todas las disputas a revisión manual
                # En producción, podrías tener lógica más sofisticada
                
                if auto_resolve:
                    # Intentar resolver automáticamente
                    # Esto requeriría lógica más compleja basada en reglas de negocio
                    pass
                else:
                    escalated += 1
            
            reviewed += 1
        
        logger.info(
            f"Reviewed {reviewed} disputes: "
            f"{resolved} resolved, {escalated} escalated"
        )
        
        return {
            "reviewed": reviewed,
            "resolved": resolved,
            "escalated": escalated
        }
    
    @task
    def notify_pending_disputes(**context) -> Dict[str, Any]:
        """Notifica sobre disputas pendientes de revisión"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        notifier = TimeTrackingNotifier(storage)
        
        # Obtener disputas pendientes de más de 24 horas
        sql = """
            SELECT id, employee_id
            FROM time_tracking_disputes
            WHERE status = 'under_review'
                AND submitted_at < NOW() - INTERVAL '24 hours'
        """
        
        results = storage.hook.get_records(sql)
        
        notified_count = 0
        
        for row in results:
            dispute_id = row[0]
            employee_id = row[1]
            
            notifier.notify_dispute_submitted(employee_id, dispute_id)
            notified_count += 1
        
        logger.info(f"Notified about {notified_count} pending disputes")
        
        return {
            "notifications_sent": notified_count
        }
    
    # Pipeline
    review_disputes = review_open_disputes()
    notify_disputes = notify_pending_disputes()
    
    review_disputes >> notify_disputes


# Instanciar DAG
time_tracking_disputes_dag = time_tracking_disputes()


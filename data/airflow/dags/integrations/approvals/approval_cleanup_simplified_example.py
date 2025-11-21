"""
Ejemplo simplificado del DAG approval_cleanup usando plugins modulares.
Este es un ejemplo de cómo debería verse el DAG después de la refactorización completa.

Este archivo NO reemplaza approval_cleanup.py todavía, es solo un ejemplo.
Para usar este DAG, renómbralo a approval_cleanup.py después de validar.
"""
from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context
from airflow.models.param import Param
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
from data.airflow.plugins.etl_notifications import notify_slack

# Importar plugins modulares
from data.airflow.plugins.approval_cleanup_config import (
    get_config,
    APPROVALS_DB_CONN,
    MAX_RETENTION_YEARS,
    MIN_RETENTION_YEARS,
)
from data.airflow.plugins.approval_cleanup_ops import (
    get_pg_hook,
    execute_query_with_timeout,
    calculate_optimal_batch_size,
    track_performance,
)
from data.airflow.plugins.approval_cleanup_queries import (
    check_table_exists,
    create_archive_table,
    get_old_requests_to_archive,
    archive_requests_batch,
    get_expired_notifications,
    delete_notifications_batch,
    get_stale_pending_requests,
    create_history_table,
    insert_cleanup_history,
    get_database_size,
    get_table_sizes,
    get_request_counts,
    get_cleanup_history,
)
from data.airflow.plugins.approval_cleanup_analytics import (
    detect_anomaly,
    analyze_table_sizes,
    analyze_trends,
    predict_capacity_need,
    calculate_percentiles,
)
from data.airflow.plugins.approval_cleanup_utils import (
    log_with_context,
    check_circuit_breaker,
    validate_params,
    format_duration_ms,
    format_bytes,
)

logger = logging.getLogger(__name__)


@dag(
    'approval_cleanup_simplified',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'retry_exponential_backoff': True,
        'max_retry_delay': timedelta(minutes=15),
    },
    description='Limpieza y mantenimiento del sistema de aprobaciones (versión simplificada)',
    schedule='0 2 * * 0',  # Domingos a las 2 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'maintenance', 'cleanup', 'simplified'],
    params={
        'archive_retention_years': Param(1, type='integer', minimum=1, maximum=10),
        'notification_retention_months': Param(6, type='integer', minimum=1, maximum=24),
        'dry_run': Param(False, type='boolean'),
        'notify_on_completion': Param(True, type='boolean'),
    },
    sla_miss_callback=sla_miss_callback,
    on_success_callback=lambda context: notify_slack("✅ approval_cleanup DAG completed successfully"),
    on_failure_callback=lambda context: notify_slack("❌ approval_cleanup DAG failed"),
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=2),
)
def approval_cleanup_simplified() -> None:
    """Pipeline simplificado de limpieza usando plugins modulares."""
    
    @task(task_id='health_check', on_failure_callback=on_task_failure)
    def health_check() -> Dict[str, Any]:
        """Verificar salud del sistema antes de comenzar."""
        try:
            pg_hook = get_pg_hook()
            
            # Verificar conexión
            result = pg_hook.get_first("SELECT 1")
            if not result:
                raise AirflowFailException("Database connection failed")
            
            # Verificar tablas principales
            tables_ok = check_table_exists('approval_requests', pg_hook=pg_hook)
            
            return {
                'status': 'healthy' if tables_ok else 'degraded',
                'database_connected': True,
                'tables_available': tables_ok,
            }
        except Exception as e:
            log_with_context('error', f'Health check failed: {e}', error=str(e))
            raise AirflowFailException(f"Health check failed: {e}")
    
    @task(task_id='check_circuit_breaker', on_failure_callback=on_task_failure)
    def check_circuit_breaker_task() -> Dict[str, Any]:
        """Verificar circuit breaker."""
        return check_circuit_breaker()
    
    @task(task_id='check_archive_table', on_failure_callback=on_task_failure)
    def check_archive_table() -> Dict[str, Any]:
        """Verificar y crear tabla de archivo si no existe."""
        context = get_current_context()
        params = context.get('params', {})
        dry_run = params.get('dry_run', False)
        
        validate_params(params)
        
        try:
            pg_hook = get_pg_hook()
            exists = check_table_exists('approval_requests_archive', pg_hook=pg_hook)
            
            if not exists and not dry_run:
                create_archive_table(pg_hook=pg_hook)
                log_with_context('info', 'Archive table created successfully')
            
            return {
                'archive_table_exists': exists,
                'archive_table_created': not exists and not dry_run
            }
        except Exception as e:
            log_with_context('error', f'Archive table check failed: {e}', error=str(e))
            raise AirflowFailException(f"Archive table check failed: {e}")
    
    @task(task_id='archive_old_requests', on_failure_callback=on_task_failure)
    def archive_old_requests(archive_info: Dict[str, Any]) -> Dict[str, Any]:
        """Archivar solicitudes completadas antiguas."""
        context = get_current_context()
        params = context.get('params', {})
        retention_years = params.get('archive_retention_years', 1)
        dry_run = params.get('dry_run', False)
        
        try:
            pg_hook = get_pg_hook()
            start_time = pendulum.now()
            
            # Obtener batch size óptimo
            estimated_count = 1000  # Estimación inicial
            batch_size = calculate_optimal_batch_size(
                estimated_count,
                'archive_old_requests',
                pg_hook=pg_hook
            )
            
            # Obtener requests a archivar
            old_requests = get_old_requests_to_archive(
                retention_years,
                batch_size=batch_size,
                pg_hook=pg_hook
            )
            
            if not old_requests:
                return {
                    'archived': 0,
                    'dry_run': dry_run
                }
            
            # Archivar en lotes
            total_archived = 0
            request_ids = [row[0] for row in old_requests]
            
            result = archive_requests_batch(
                request_ids,
                pg_hook=pg_hook,
                dry_run=dry_run
            )
            
            total_archived = result.get('archived', 0)
            duration_ms = (pendulum.now() - start_time).total_seconds() * 1000
            
            # Track performance
            track_performance(
                'archive_old_requests',
                duration_ms,
                total_archived,
                batch_size,
                pg_hook=pg_hook
            )
            
            # Detectar anomalías
            anomaly = detect_anomaly(total_archived, 'archived_count', pg_hook=pg_hook)
            if anomaly.get('is_anomaly'):
                log_with_context(
                    'warning',
                    f'Anomaly detected in archived count: {anomaly}',
                    **anomaly
                )
            
            log_with_context(
                'info',
                f'Archived {total_archived} requests',
                archived=total_archived,
                duration_ms=duration_ms,
                batch_size=batch_size
            )
            
            return {
                'archived': total_archived,
                'duration_ms': duration_ms,
                'batch_size': batch_size,
                'anomaly_detected': anomaly.get('is_anomaly', False),
                'dry_run': dry_run
            }
            
        except Exception as e:
            log_with_context('error', f'Archive failed: {e}', error=str(e))
            raise
    
    @task(task_id='cleanup_expired_notifications', on_failure_callback=on_task_failure)
    def cleanup_expired_notifications() -> Dict[str, Any]:
        """Limpiar notificaciones expiradas."""
        context = get_current_context()
        params = context.get('params', {})
        retention_months = params.get('notification_retention_months', 6)
        dry_run = params.get('dry_run', False)
        
        try:
            pg_hook = get_pg_hook()
            start_time = pendulum.now()
            
            # Obtener notificaciones expiradas
            expired_notifications = get_expired_notifications(
                retention_months,
                pg_hook=pg_hook
            )
            
            if not expired_notifications:
                return {
                    'deleted': 0,
                    'dry_run': dry_run
                }
            
            # Eliminar en lotes
            notification_ids = [row[0] for row in expired_notifications]
            batch_size = 1000
            total_deleted = 0
            
            for i in range(0, len(notification_ids), batch_size):
                batch = notification_ids[i:i + batch_size]
                result = delete_notifications_batch(
                    batch,
                    pg_hook=pg_hook,
                    dry_run=dry_run
                )
                total_deleted += result.get('deleted', 0)
            
            duration_ms = (pendulum.now() - start_time).total_seconds() * 1000
            
            log_with_context(
                'info',
                f'Deleted {total_deleted} expired notifications',
                deleted=total_deleted,
                duration_ms=duration_ms
            )
            
            return {
                'deleted': total_deleted,
                'duration_ms': duration_ms,
                'dry_run': dry_run
            }
            
        except Exception as e:
            log_with_context('error', f'Notification cleanup failed: {e}', error=str(e))
            raise
    
    @task(task_id='analyze_table_sizes', on_failure_callback=on_task_failure)
    def analyze_table_sizes_task() -> Dict[str, Any]:
        """Analizar tamaños de tablas."""
        return analyze_table_sizes()
    
    @task(task_id='store_metrics_history', on_failure_callback=on_task_failure)
    def store_metrics_history(
        archive_result: Dict[str, Any],
        notifications_result: Dict[str, Any],
        table_sizes_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Almacenar métricas en historial."""
        try:
            pg_hook = get_pg_hook()
            create_history_table(pg_hook=pg_hook)
            
            total_size = table_sizes_result.get('total_size_bytes', 0)
            
            history_data = {
                'archived_count': archive_result.get('archived', 0),
                'deleted_count': 0,  # Stale cleanup could go here
                'notifications_deleted': notifications_result.get('deleted', 0),
                'database_size_bytes': total_size,
                'execution_duration_ms': (
                    archive_result.get('duration_ms', 0) +
                    notifications_result.get('duration_ms', 0)
                ),
                'dry_run': archive_result.get('dry_run', False),
            }
            
            history_id = insert_cleanup_history(history_data, pg_hook=pg_hook)
            
            return {
                'history_id': history_id,
                'stored': True
            }
            
        except Exception as e:
            log_with_context('warning', f'Failed to store history: {e}', error=str(e))
            return {'stored': False, 'error': str(e)}
    
    @task(task_id='generate_report', on_failure_callback=on_task_failure)
    def generate_report(
        archive_result: Dict[str, Any],
        notifications_result: Dict[str, Any],
        table_sizes_result: Dict[str, Any],
        history_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generar reporte de limpieza."""
        try:
            # Obtener historial para comparación
            pg_hook = get_pg_hook()
            history = get_cleanup_history(days=30, pg_hook=pg_hook)
            
            # Analizar tendencias
            trends = analyze_trends(history, days=30) if history else {}
            
            # Predicción de capacidad
            capacity_prediction = predict_capacity_need(days_ahead=30, pg_hook=pg_hook)
            
            report = {
                'cleanup_date': pendulum.now().isoformat(),
                'archive': {
                    'archived': archive_result.get('archived', 0),
                    'duration_ms': archive_result.get('duration_ms', 0),
                    'duration_formatted': format_duration_ms(archive_result.get('duration_ms', 0)),
                },
                'notifications': {
                    'deleted': notifications_result.get('deleted', 0),
                    'duration_ms': notifications_result.get('duration_ms', 0),
                    'duration_formatted': format_duration_ms(notifications_result.get('duration_ms', 0)),
                },
                'database': {
                    'total_size_bytes': table_sizes_result.get('total_size_bytes', 0),
                    'total_size_formatted': format_bytes(table_sizes_result.get('total_size_bytes', 0)),
                    'table_count': table_sizes_result.get('table_count', 0),
                },
                'trends': trends,
                'capacity_prediction': capacity_prediction,
                'dry_run': archive_result.get('dry_run', False),
            }
            
            log_with_context('info', 'Cleanup report generated', **report)
            
            return report
            
        except Exception as e:
            log_with_context('error', f'Report generation failed: {e}', error=str(e))
            return {'error': str(e)}
    
    @task(task_id='send_notification', on_failure_callback=on_task_failure)
    def send_notification(report: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar notificación de finalización."""
        context = get_current_context()
        params = context.get('params', {})
        notify = params.get('notify_on_completion', True)
        
        if not notify:
            return {'sent': False, 'reason': 'notifications_disabled'}
        
        try:
            archive = report.get('archive', {})
            notifications = report.get('notifications', {})
            database = report.get('database', {})
            
            message = f"🧹 *Approval Cleanup Completed*\n\n"
            message += f"*Archived:* {archive.get('archived', 0)} requests ({archive.get('duration_formatted', 'N/A')})\n"
            message += f"*Deleted:* {notifications.get('deleted', 0)} notifications ({notifications.get('duration_formatted', 'N/A')})\n"
            message += f"*Database Size:* {database.get('total_size_formatted', 'N/A')}\n"
            
            if report.get('dry_run'):
                message += "\n⚠️ *DRY RUN MODE* - No changes were made"
            
            notify_slack(message)
            
            return {'sent': True}
            
        except Exception as e:
            log_with_context('warning', f'Notification failed: {e}', error=str(e))
            return {'sent': False, 'error': str(e)}
    
    # Pipeline principal
    health = health_check()
    circuit_breaker = check_circuit_breaker_task()
    
    # Si el circuit breaker está activo, fallar
    @task(task_id='check_circuit_breaker_status')
    def check_circuit_breaker_status(cb_result: Dict[str, Any]) -> None:
        if cb_result.get('active'):
            raise AirflowFailException(
                f"Circuit breaker is ACTIVE: {cb_result.get('reason')}. "
                f"Too many failures ({cb_result.get('failure_count', 0)}) in last "
                f"{CIRCUIT_BREAKER_CHECK_WINDOW_HOURS} hours."
            )
    
    # Operaciones de limpieza
    archive_info = check_archive_table()
    archive_result = archive_old_requests(archive_info)
    notifications_result = cleanup_expired_notifications()
    
    # Análisis
    table_sizes_result = analyze_table_sizes_task()
    
    # Historial
    history_result = store_metrics_history(
        archive_result,
        notifications_result,
        table_sizes_result
    )
    
    # Reporte
    report = generate_report(
        archive_result,
        notifications_result,
        table_sizes_result,
        history_result
    )
    
    # Notificación
    send_notification(report)
    
    # Dependencias
    check_circuit_breaker_status(circuit_breaker) >> archive_info
    health >> archive_info


# Crear instancia del DAG
approval_cleanup_simplified_dag = approval_cleanup_simplified()



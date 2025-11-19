"""
DAG de Mantenimiento para Nómina
Limpieza, archivado, optimización y mantenimiento periódico
"""

from __future__ import annotations

from datetime import timedelta
from typing import Dict, Any
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

import os

from payroll import (
    PayrollMaintenance,
    PayrollBackup,
    PayrollHealthChecker,
    PayrollNotifier,
    PayrollConfig,
)

logger = logging.getLogger(__name__)


@dag(
    dag_id="payroll_maintenance",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 2 * * 0",  # Domingos a las 2 AM
    catchup=False,
    default_args={
        "owner": "hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    doc_md="""
    ### Mantenimiento del Sistema de Nómina
    
    DAG de mantenimiento que ejecuta tareas de limpieza y optimización:
    
    **Funcionalidades:**
    - Archivado de períodos de pago antiguos
    - Limpieza de recibos procesados antiguos
    - Limpieza de OCR fallidos antiguos
    - Limpieza de aprobaciones pendientes antiguas
    - Optimización de tablas (VACUUM, ANALYZE)
    - Refresco de vistas materializadas
    - Backup de datos
    - Health checks
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `retention_days`: Días de retención para períodos (default: 365)
    - `expense_retention_days`: Días de retención para gastos (default: 730)
    - `dry_run`: Solo simular sin ejecutar cambios
    - `notify_on_completion`: Enviar notificación al completar
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "retention_days": Param(365, type="integer", minimum=30, maximum=1095),
        "expense_retention_days": Param(730, type="integer", minimum=90, maximum=2190),
        "dry_run": Param(False, type="boolean"),
        "notify_on_completion": Param(True, type="boolean"),
    },
    tags=["payroll", "maintenance", "cleanup", "hr"],
)
def payroll_maintenance() -> None:
    """DAG de mantenimiento para nómina"""
    
    @task
    def health_check(**context) -> Dict[str, Any]:
        """Verifica salud del sistema antes de mantenimiento"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        health_checker = PayrollHealthChecker(postgres_conn_id=config.postgres_conn_id)
        health = health_checker.comprehensive_health_check()
        
        logger.info(f"System health: {health['overall_status']}")
        
        return health
    
    @task
    def archive_old_pay_periods(**context) -> Dict[str, Any]:
        """Archiva períodos de pago antiguos"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        
        result = maintenance.archive_old_pay_periods(
            retention_days=params.get("retention_days", 365),
            dry_run=params.get("dry_run", False)
        )
        
        logger.info(
            f"Archive result: {result.get('archived', 0)} archived, "
            f"{result.get('deleted', 0)} deleted"
        )
        
        return result
    
    @task
    def cleanup_old_expenses(**context) -> Dict[str, Any]:
        """Limpia recibos de gastos antiguos"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        
        result = maintenance.cleanup_old_expense_receipts(
            retention_days=params.get("expense_retention_days", 730),
            dry_run=params.get("dry_run", False)
        )
        
        logger.info(f"Expense cleanup: {result.get('deleted', 0)} deleted")
        
        return result
    
    @task
    def cleanup_failed_ocr(**context) -> Dict[str, Any]:
        """Limpia recibos con OCR fallido antiguos"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        
        result = maintenance.cleanup_failed_ocr_receipts(
            days=90,
            dry_run=params.get("dry_run", False)
        )
        
        logger.info(f"OCR cleanup: {result.get('deleted', 0)} deleted")
        
        return result
    
    @task
    def cleanup_stale_approvals(**context) -> Dict[str, Any]:
        """Limpia aprobaciones pendientes antiguas"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        
        result = maintenance.cleanup_stale_approvals(
            days=90,
            dry_run=params.get("dry_run", False)
        )
        
        logger.info(f"Approval cleanup: {result.get('found', 0)} found")
        
        return result
    
    @task
    def optimize_tables(**context) -> Dict[str, Any]:
        """Optimiza tablas de nómina"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        
        result = maintenance.optimize_tables()
        
        logger.info(f"Optimized {result.get('optimized', 0)} tables")
        
        return result
    
    @task
    def refresh_views(**context) -> Dict[str, Any]:
        """Refresca vistas materializadas"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        
        result = maintenance.refresh_all_materialized_views()
        
        logger.info(f"Refreshed {result.get('refreshed', 0)} views")
        
        return result
    
    @task
    def create_backup(**context) -> Dict[str, Any]:
        """Crea backup de datos recientes"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        if params.get("dry_run", False):
            return {"backup_id": None, "skipped": True}
        
        from datetime import date, timedelta
        
        backup = PayrollBackup(postgres_conn_id=config.postgres_conn_id)
        
        # Backup del último mes
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        result = backup.backup_pay_periods(start_date, end_date)
        
        logger.info(f"Backup created: {result.get('backup_id')} with {result.get('count', 0)} records")
        
        return result
    
    @task
    def generate_maintenance_report(**context) -> Dict[str, Any]:
        """Genera reporte de mantenimiento"""
        params = context["params"]
        config = PayrollConfig.from_env()
        
        maintenance = PayrollMaintenance(postgres_conn_id=config.postgres_conn_id)
        stats = maintenance.get_maintenance_stats()
        
        logger.info(f"Maintenance stats: {stats}")
        
        # Notificar si está habilitado
        if params.get("notify_on_completion", True):
            notifier = PayrollNotifier(
                slack_webhook_url=os.getenv("SLACK_WEBHOOK_URL"),
                email_api_url=os.getenv("EMAIL_API_URL")
            )
            
            message = (
                f"🧹 Mantenimiento de Nómina Completado\n"
                f"Períodos: {stats.get('pay_periods', {}).get('total', 0)} total\n"
                f"Aprobaciones pendientes: {stats.get('approvals', {}).get('pending', 0)}\n"
                f"OCR fallidos: {stats.get('ocr', {}).get('failed', 0)}"
            )
            
            notifier._send_notification(
                message,
                "maintenance_completed",
                stats
            )
        
        return stats
    
    # Pipeline
    health = health_check()
    archive_result = archive_old_pay_periods()
    expense_cleanup = cleanup_old_expenses()
    ocr_cleanup = cleanup_failed_ocr()
    approval_cleanup = cleanup_stale_approvals()
    optimization = optimize_tables()
    views_refresh = refresh_views()
    backup_result = create_backup()
    report = generate_maintenance_report()
    
    health >> [
        archive_result,
        expense_cleanup,
        ocr_cleanup,
        approval_cleanup
    ] >> optimization >> views_refresh >> backup_result >> report


# Instanciar DAG
payroll_maintenance_dag = payroll_maintenance()


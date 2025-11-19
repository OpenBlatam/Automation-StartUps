"""
DAG de Gestión de Vacaciones y Permisos
Procesa solicitudes, calcula saldos, envía notificaciones
"""

from __future__ import annotations

from datetime import timedelta, date
from typing import Any, Dict, List, Optional
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

from time_tracking import (
    TimeTrackingStorage,
    VacationManager,
    VacationType,
    TimeTrackingNotifier,
)

logger = logging.getLogger(__name__)


@dag(
    dag_id="time_tracking_vacations",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 9 * * *",  # Diario a las 9 AM
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
    ### Gestión Automática de Vacaciones y Permisos
    
    Procesa solicitudes de vacaciones y permisos:
    
    **Funcionalidades:**
    - Procesamiento de solicitudes pendientes
    - Cálculo automático de saldos de vacaciones
    - Notificaciones de saldos bajos
    - Aprobación automática de solicitudes válidas
    - Actualización de saldos
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `auto_approve_vacations`: Auto-aprobar vacaciones válidas (default: false)
    - `notify_balance_threshold`: Días restantes para notificar (default: 5)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "auto_approve_vacations": Param(False, type="boolean"),
        "notify_balance_threshold": Param(5, type="integer", minimum=0),
    },
    tags=["time_tracking", "hr", "vacations", "leave_management"],
)
def time_tracking_vacations() -> None:
    """DAG para gestión de vacaciones"""
    
    @task
    def process_pending_requests(**context) -> Dict[str, Any]:
        """Procesa solicitudes de vacaciones pendientes"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        auto_approve = params.get("auto_approve_vacations", False)
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        vacation_manager = VacationManager(storage)
        
        # Obtener solicitudes pendientes
        pending_requests = vacation_manager.get_pending_requests()
        
        processed = 0
        approved = 0
        rejected = 0
        
        for request in pending_requests:
            # Validar solicitud
            from time_tracking.validators import TimeTrackingValidator
            validator = TimeTrackingValidator(storage)
            
            is_valid, error_msg, balance = validator.validate_vacation_request(
                employee_id=request["employee_id"],
                start_date=request["start_date"],
                end_date=request["end_date"],
                vacation_type=request["vacation_type"]
            )
            
            if is_valid and auto_approve:
                # Auto-aprobar
                vacation_manager.approve_vacation(
                    request_id=request["id"],
                    approved_by="system",
                    days_approved=None
                )
                approved += 1
            elif not is_valid:
                # Rechazar con razón
                vacation_manager.reject_vacation(
                    request_id=request["id"],
                    rejected_by="system",
                    reason=error_msg or "Invalid request"
                )
                rejected += 1
            
            processed += 1
        
        logger.info(
            f"Processed {processed} vacation requests: "
            f"{approved} approved, {rejected} rejected"
        )
        
        return {
            "processed": processed,
            "approved": approved,
            "rejected": rejected
        }
    
    @task
    def check_low_balances(**context) -> Dict[str, Any]:
        """Verifica y notifica sobre saldos bajos de vacaciones"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        threshold = params.get("notify_balance_threshold", 5)
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        notifier = TimeTrackingNotifier(storage)
        
        # Obtener todos los empleados activos
        sql = """
            SELECT employee_id FROM payroll_employees
            WHERE active = true
        """
        
        results = storage.hook.get_records(sql)
        employee_ids = [row[0] for row in results]
        
        notified_count = 0
        
        for employee_id in employee_ids:
            balance = storage.get_vacation_balance(employee_id)
            
            # Verificar saldo de vacaciones
            if balance["vacation_days"] <= threshold:
                notifier.notify_vacation_balance_low(
                    employee_id=employee_id,
                    vacation_type="vacation",
                    remaining_days=float(balance["vacation_days"])
                )
                notified_count += 1
            
            # Verificar saldo de días de enfermedad
            if balance["sick_days"] <= threshold:
                notifier.notify_vacation_balance_low(
                    employee_id=employee_id,
                    vacation_type="sick",
                    remaining_days=float(balance["sick_days"])
                )
                notified_count += 1
        
        logger.info(f"Checked balances for {len(employee_ids)} employees, notified {notified_count}")
        
        return {
            "employees_checked": len(employee_ids),
            "notifications_sent": notified_count
        }
    
    @task
    def update_vacation_accruals(**context) -> Dict[str, Any]:
        """Actualiza acumulación de días de vacaciones"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        
        # Obtener empleados activos
        sql = """
            SELECT employee_id, start_date
            FROM payroll_employees
            WHERE active = true
        """
        
        results = storage.hook.get_records(sql)
        current_year = date.today().year
        
        updated_count = 0
        
        for row in results:
            employee_id = row[0]
            start_date = row[1]
            
            # Calcular días acumulados (ejemplo: 1.25 días por mes)
            if start_date:
                months_worked = (date.today() - start_date).days / 30.0
                accrual_rate = 1.25  # Días por mes
                accrued_days = months_worked * accrual_rate
                
                # Actualizar o insertar saldo
                update_sql = """
                    INSERT INTO time_tracking_vacation_balances (
                        employee_id, year, vacation_days_accrued,
                        vacation_days_available, accrual_rate, accrual_period
                    ) VALUES (
                        %s, %s, %s, %s, %s, 'monthly'
                    )
                    ON CONFLICT (employee_id) DO UPDATE SET
                        vacation_days_accrued = EXCLUDED.vacation_days_accrued,
                        vacation_days_available = EXCLUDED.vacation_days_accrued - vacation_days_used,
                        last_accrual_date = CURRENT_DATE,
                        updated_at = NOW()
                """
                
                storage.hook.run(
                    update_sql,
                    parameters=(
                        employee_id,
                        current_year,
                        float(accrued_days),
                        float(accrued_days),
                        float(accrual_rate)
                    )
                )
                
                updated_count += 1
        
        logger.info(f"Updated vacation accruals for {updated_count} employees")
        
        return {
            "updated": updated_count
        }
    
    # Pipeline
    process_requests = process_pending_requests()
    check_balances = check_low_balances()
    update_accruals = update_vacation_accruals()
    
    [process_requests, check_balances, update_accruals]


# Instanciar DAG
time_tracking_vacations_dag = time_tracking_vacations()


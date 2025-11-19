"""
DAG de Automatización de Time Tracking
Registro automático de entradas/salidas, cálculo de horas, detección de anomalías
"""

from __future__ import annotations

from datetime import timedelta, datetime, date
from typing import Any, Dict, List, Optional
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

from time_tracking import (
    TimeTrackingStorage,
    ClockManager,
    SessionManager,
    TimeTrackingHourCalculator,
    TimeTrackingValidator,
    TimeTrackingNotifier,
    SessionStatus,
)

logger = logging.getLogger(__name__)


@dag(
    dag_id="time_tracking_automation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="*/15 * * * *",  # Cada 15 minutos
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
    ### Automatización de Time Tracking
    
    Sistema completo para gestión automática de tiempo y asistencia:
    
    **Funcionalidades:**
    - Detección automática de sesiones abiertas sin clock out
    - Cierre automático de sesiones antiguas
    - Cálculo automático de horas trabajadas
    - Detección de discrepancias y anomalías
    - Notificaciones automáticas
    - Sincronización con sistema de nómina
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `auto_close_stale_hours`: Horas después de las cuales cerrar sesiones automáticamente (default: 24)
    - `check_all_employees`: Verificar todos los empleados activos (default: true)
    - `employee_ids`: Lista de IDs específicos (opcional, formato: "id1,id2,id3")
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "auto_close_stale_hours": Param(24, type="integer", minimum=1, maximum=168),
        "check_all_employees": Param(True, type="boolean"),
        "employee_ids": Param("", type="string"),
    },
    tags=["time_tracking", "hr", "automation", "attendance"],
)
def time_tracking_automation() -> None:
    """DAG principal para automatización de time tracking"""
    
    @task
    def ensure_schema(**context) -> bool:
        """Verifica que el schema de time tracking esté creado"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        sql = """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'time_tracking_clock_events'
            );
        """
        
        result = hook.get_first(sql)
        exists = result[0] if result else False
        
        if not exists:
            logger.warning(
                "Time tracking schema not found. Please execute: "
                "psql $DATABASE_URL -f data/db/time_tracking_schema.sql"
            )
        
        return exists
    
    @task
    def get_active_employees(**context) -> List[str]:
        """Obtiene lista de empleados activos a procesar"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        check_all = params.get("check_all_employees", True)
        employee_ids_str = params.get("employee_ids", "")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        
        if not check_all and employee_ids_str:
            # Procesar solo IDs específicos
            employee_ids = [eid.strip() for eid in employee_ids_str.split(",") if eid.strip()]
            return employee_ids
        
        # Obtener todos los empleados activos
        sql = """
            SELECT employee_id
            FROM payroll_employees
            WHERE active = true
            ORDER BY employee_id
        """
        
        results = storage.hook.get_records(sql)
        employee_ids = [row[0] for row in results]
        
        logger.info(f"Found {len(employee_ids)} active employees to process")
        return employee_ids
    
    @task
    def auto_close_stale_sessions(**context) -> Dict[str, Any]:
        """Cierra automáticamente sesiones abiertas antiguas"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        max_hours = params.get("auto_close_stale_hours", 24)
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        clock_manager = ClockManager(storage)
        hour_calculator = TimeTrackingHourCalculator(storage)
        session_manager = SessionManager(storage, clock_manager, hour_calculator)
        
        closed_count = session_manager.auto_close_stale_sessions(max_hours_open=max_hours)
        
        logger.info(f"Auto-closed {closed_count} stale sessions")
        
        return {
            "closed_sessions": closed_count,
            "max_hours": max_hours
        }
    
    @task
    def detect_missing_clock_outs(**context) -> Dict[str, Any]:
        """Detecta empleados con clock out faltante"""
        ti = context["ti"]
        employee_ids = ti.xcom_pull(task_ids="get_active_employees")
        
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        validator = TimeTrackingValidator(storage)
        notifier = TimeTrackingNotifier(storage)
        
        missing_count = 0
        today = date.today()
        
        for employee_id in employee_ids:
            # Verificar si hay sesión abierta sin clock out
            open_session = storage.get_open_session(employee_id, today)
            if open_session:
                # Verificar si tiene más de 8 horas
                clock_in_time = open_session["clock_in_time"]
                hours_open = (datetime.now() - clock_in_time).total_seconds() / 3600.0
                
                if hours_open > 8:
                    # Crear notificación
                    notifier.notify_missing_clock_out(employee_id, today)
                    missing_count += 1
        
        logger.info(f"Detected {missing_count} employees with missing clock out")
        
        return {
            "missing_clock_outs": missing_count,
            "employees_checked": len(employee_ids)
        }
    
    @task
    def detect_time_discrepancies(**context) -> Dict[str, Any]:
        """Detecta discrepancias en registros de tiempo"""
        ti = context["ti"]
        employee_ids = ti.xcom_pull(task_ids="get_active_employees")
        
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        validator = TimeTrackingValidator(storage)
        
        today = date.today()
        week_start = today - timedelta(days=7)
        
        all_discrepancies = []
        
        for employee_id in employee_ids:
            discrepancies = validator.detect_time_discrepancies(
                employee_id=employee_id,
                start_date=week_start,
                end_date=today
            )
            
            for disc in discrepancies:
                disc["employee_id"] = employee_id
                all_discrepancies.append(disc)
        
        logger.info(f"Detected {len(all_discrepancies)} time discrepancies")
        
        return {
            "discrepancies_count": len(all_discrepancies),
            "discrepancies": all_discrepancies[:10]  # Limitar a 10 para el reporte
        }
    
    @task
    def sync_to_payroll(**context) -> Dict[str, Any]:
        """Sincroniza horas trabajadas con sistema de nómina"""
        ti = context["ti"]
        employee_ids = ti.xcom_pull(task_ids="get_active_employees")
        
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        
        today = date.today()
        week_start = today - timedelta(days=7)
        
        synced_count = 0
        
        for employee_id in employee_ids:
            # Obtener sesiones cerradas que no están sincronizadas
            sql = """
                SELECT ws.id, ws.work_date, ws.total_hours, ws.regular_hours,
                       ws.overtime_hours, ws.clock_in_time, ws.clock_out_time
                FROM time_tracking_work_sessions ws
                WHERE ws.employee_id = %s
                    AND ws.work_date BETWEEN %s AND %s
                    AND ws.status = 'closed'
                    AND ws.approved = true
                    AND NOT EXISTS (
                        SELECT 1 FROM payroll_time_entries pte
                        WHERE pte.employee_id = ws.employee_id
                            AND pte.work_date = ws.work_date
                            AND pte.hours_type = 'regular'
                    )
            """
            
            results = storage.hook.get_records(
                sql,
                parameters=(employee_id, week_start, today)
            )
            
            # Obtener hourly_rate del empleado
            emp_sql = """
                SELECT hourly_rate FROM payroll_employees
                WHERE employee_id = %s
            """
            emp_result = storage.hook.get_first(emp_sql, parameters=(employee_id,))
            if not emp_result:
                continue
            
            hourly_rate = emp_result[0]
            
            # Crear entradas en payroll_time_entries
            for row in results:
                session_id, work_date, total_hours, regular_hours, overtime_hours, clock_in, clock_out = row
                
                # Insertar horas regulares
                if regular_hours and regular_hours > 0:
                    insert_sql = """
                        INSERT INTO payroll_time_entries (
                            employee_id, work_date, clock_in, clock_out,
                            hours_worked, hours_type, hourly_rate, approved
                        ) VALUES (
                            %s, %s, %s, %s, %s, 'regular', %s, true
                        )
                        ON CONFLICT (employee_id, work_date, hours_type) DO NOTHING
                    """
                    storage.hook.run(
                        insert_sql,
                        parameters=(
                            employee_id, work_date, clock_in, clock_out,
                            float(regular_hours), float(hourly_rate)
                        )
                    )
                
                # Insertar horas overtime
                if overtime_hours and overtime_hours > 0:
                    insert_sql = """
                        INSERT INTO payroll_time_entries (
                            employee_id, work_date, clock_in, clock_out,
                            hours_worked, hours_type, hourly_rate, approved
                        ) VALUES (
                            %s, %s, %s, %s, %s, 'overtime', %s, true
                        )
                        ON CONFLICT (employee_id, work_date, hours_type) DO NOTHING
                    """
                    storage.hook.run(
                        insert_sql,
                        parameters=(
                            employee_id, work_date, clock_in, clock_out,
                            float(overtime_hours), float(hourly_rate)
                        )
                    )
                
                synced_count += 1
        
        logger.info(f"Synced {synced_count} work sessions to payroll")
        
        return {
            "synced_sessions": synced_count
        }
    
    @task
    def refresh_materialized_views(**context) -> bool:
        """Refresca vistas materializadas"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        try:
            hook.run("SELECT refresh_time_tracking_materialized_views();")
            logger.info("Materialized views refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Error refreshing materialized views: {e}")
            return False
    
    # Pipeline
    schema_check = ensure_schema()
    employees = get_active_employees()
    
    close_stale = auto_close_stale_sessions()
    detect_missing = detect_missing_clock_outs()
    detect_discrepancies = detect_time_discrepancies()
    sync_payroll = sync_to_payroll()
    refresh_views = refresh_materialized_views()
    
    schema_check >> employees >> [
        close_stale,
        detect_missing,
        detect_discrepancies
    ] >> sync_payroll >> refresh_views


# Instanciar DAG
time_tracking_automation_dag = time_tracking_automation()


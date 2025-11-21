"""
DAG de Analytics y Reportes Avanzados para Time Tracking
Genera análisis, predicciones y reportes consolidados
"""

from __future__ import annotations

from datetime import timedelta, date
from typing import Any, Dict, List
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

from time_tracking import (
    TimeTrackingStorage,
    TimeTrackingAnalytics,
    TimeTrackingReporter,
)

logger = logging.getLogger(__name__)


@dag(
    dag_id="time_tracking_analytics",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 8 * * *",  # Diario a las 8 AM
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
    ### Analytics y Reportes Avanzados de Time Tracking
    
    Genera análisis, predicciones y reportes:
    
    **Funcionalidades:**
    - Cálculo de puntuaciones de puntualidad
    - Análisis de patrones de trabajo
    - Predicción de ausentismo
    - Métricas de productividad
    - Comparación de equipos
    - Generación de reportes consolidados
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `generate_daily_reports`: Generar reportes diarios (default: true)
    - `generate_weekly_reports`: Generar reportes semanales (default: true)
    - `department`: Filtrar por departamento (opcional)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "generate_daily_reports": Param(True, type="boolean"),
        "generate_weekly_reports": Param(True, type="boolean"),
        "department": Param("", type="string"),
    },
    tags=["time_tracking", "hr", "analytics", "reports"],
)
def time_tracking_analytics() -> None:
    """DAG para analytics y reportes"""
    
    @task
    def calculate_punctuality_scores(**context) -> Dict[str, Any]:
        """Calcula puntuaciones de puntualidad para todos los empleados"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        department = params.get("department", "")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        analytics = TimeTrackingAnalytics(storage)
        
        # Obtener empleados
        if department:
            sql = """
                SELECT employee_id FROM payroll_employees
                WHERE department = %s AND active = true
            """
            employees = storage.hook.get_records(sql, parameters=(department,))
        else:
            sql = """
                SELECT employee_id FROM payroll_employees
                WHERE active = true
            """
            employees = storage.hook.get_records(sql)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        scores = []
        for row in employees:
            employee_id = row[0]
            score_data = analytics.calculate_punctuality_score(
                employee_id,
                start_date,
                end_date
            )
            scores.append(score_data)
        
        # Calcular promedio
        avg_score = sum(s["score"] for s in scores) / len(scores) if scores else 0
        
        logger.info(f"Calculated punctuality scores for {len(scores)} employees. Average: {avg_score:.2f}")
        
        return {
            "employees_processed": len(scores),
            "average_score": round(avg_score, 2),
            "scores": scores[:10]  # Limitar para el reporte
        }
    
    @task
    def generate_productivity_report(**context) -> Dict[str, Any]:
        """Genera reporte de productividad"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        department = params.get("department", "")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        analytics = TimeTrackingAnalytics(storage)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        team_comparison = analytics.generate_team_comparison(
            department=department if department else None,
            start_date=start_date,
            end_date=end_date
        )
        
        logger.info(f"Generated productivity report for {team_comparison['team_size']} employees")
        
        return {
            "report": team_comparison
        }
    
    @task
    def generate_daily_reports(**context) -> Dict[str, Any]:
        """Genera reportes diarios para empleados activos"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        generate = params.get("generate_daily_reports", True)
        
        if not generate:
            return {"skipped": True}
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        reporter = TimeTrackingReporter(storage)
        
        # Obtener empleados activos
        sql = """
            SELECT employee_id FROM payroll_employees
            WHERE active = true
        """
        employees = storage.hook.get_records(sql)
        
        report_date = date.today() - timedelta(days=1)  # Reporte del día anterior
        
        generated = 0
        for row in employees:
            employee_id = row[0]
            try:
                report = reporter.generate_daily_report(employee_id, report_date)
                generated += 1
            except Exception as e:
                logger.error(f"Error generating daily report for {employee_id}: {e}")
        
        logger.info(f"Generated {generated} daily reports")
        
        return {
            "reports_generated": generated,
            "report_date": report_date.isoformat()
        }
    
    @task
    def generate_weekly_reports(**context) -> Dict[str, Any]:
        """Genera reportes semanales"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        generate = params.get("generate_weekly_reports", True)
        
        if not generate:
            return {"skipped": True}
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        reporter = TimeTrackingReporter(storage)
        
        # Obtener empleados activos
        sql = """
            SELECT employee_id FROM payroll_employees
            WHERE active = true
        """
        employees = storage.hook.get_records(sql)
        
        # Calcular inicio de semana (lunes)
        today = date.today()
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday + 7)  # Semana anterior
        
        generated = 0
        for row in employees:
            employee_id = row[0]
            try:
                report = reporter.generate_weekly_report(employee_id, week_start)
                generated += 1
            except Exception as e:
                logger.error(f"Error generating weekly report for {employee_id}: {e}")
        
        logger.info(f"Generated {generated} weekly reports")
        
        return {
            "reports_generated": generated,
            "week_start": week_start.isoformat()
        }
    
    @task
    def predict_absenteeism(**context) -> Dict[str, Any]:
        """Predice ausentismo para los próximos 30 días"""
        params = context["params"]
        postgres_conn_id = params.get("postgres_conn_id", "postgres_default")
        
        storage = TimeTrackingStorage(postgres_conn_id=postgres_conn_id)
        analytics = TimeTrackingAnalytics(storage)
        
        # Obtener empleados activos
        sql = """
            SELECT employee_id FROM payroll_employees
            WHERE active = true
        """
        employees = storage.hook.get_records(sql)
        
        predictions = []
        for row in employees:
            employee_id = row[0]
            try:
                prediction = analytics.predict_absenteeism(employee_id, days_ahead=30)
                predictions.append(prediction)
            except Exception as e:
                logger.error(f"Error predicting absenteeism for {employee_id}: {e}")
        
        logger.info(f"Generated absenteeism predictions for {len(predictions)} employees")
        
        return {
            "predictions_generated": len(predictions),
            "predictions": predictions[:5]  # Limitar para el reporte
        }
    
    # Pipeline
    punctuality = calculate_punctuality_scores()
    productivity = generate_productivity_report()
    daily_reports = generate_daily_reports()
    weekly_reports = generate_weekly_reports()
    predictions = predict_absenteeism()
    
    [punctuality, productivity] >> [daily_reports, weekly_reports, predictions]


# Instanciar DAG
time_tracking_analytics_dag = time_tracking_analytics()


"""
Hiring Extended Automation DAG
==============================

DAG para funcionalidades extendidas:
- Background checks automatizados
- Análisis predictivo de abandono
- Sincronización con payroll/HRIS
- Procesamiento de chatbot
- Alertas automáticas
"""

from __future__ import annotations

from datetime import timedelta, datetime, timezone
import json
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.hiring_extended import (
    initiate_background_check,
    predict_process_abandonment,
    sync_new_hire_to_payroll,
    process_chatbot_message,
)

logger = logging.getLogger(__name__)


@dag(
    dag_id="hiring_extended_automation",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "hr-recruiting",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "on_failure_callback": on_task_failure,
    },
    tags=["hiring", "ats", "automation", "extended"],
)
def hiring_extended_automation():
    """Ejecuta automatizaciones extendidas de hiring"""
    
    @task
    def process_background_checks() -> Dict[str, Any]:
        """Procesa background checks para candidatos contratados"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener candidatos contratados sin background check
            cursor.execute("""
                SELECT DISTINCT c.candidate_id, a.application_id, a.job_id
                FROM ats_applications a
                JOIN ats_candidates c ON a.candidate_id = c.candidate_id
                LEFT JOIN ats_background_checks bc ON c.candidate_id = bc.candidate_id
                WHERE a.status = 'hired'
                  AND bc.check_id IS NULL
                  AND a.updated_at > NOW() - INTERVAL '30 days'
                LIMIT 20
            """)
            
            candidates = cursor.fetchall()
            processed = 0
            failed = 0
            
            for candidate in candidates:
                candidate_id = candidate[0]
                
                try:
                    result = initiate_background_check(
                        candidate_id=candidate_id,
                        check_type="standard",
                        provider="checkr"
                    )
                    processed += 1
                    logger.info(f"Background check initiated for {candidate_id}")
                    
                except Exception as e:
                    logger.error(f"Error initiating background check for {candidate_id}: {e}")
                    failed += 1
            
            cursor.close()
            conn.close()
            
            return {
                "total_candidates": len(candidates),
                "processed": processed,
                "failed": failed
            }
            
        except Exception as e:
            logger.error(f"Error processing background checks: {e}")
            raise
    
    @task
    def analyze_abandonment_risks() -> Dict[str, Any]:
        """Analiza riesgo de abandono del proceso"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener aplicaciones activas
            cursor.execute("""
                SELECT a.application_id
                FROM ats_applications a
                WHERE a.status IN ('applied', 'screening', 'interviewing')
                  AND a.updated_at > NOW() - INTERVAL '30 days'
                ORDER BY a.updated_at ASC
                LIMIT 50
            """)
            
            applications = cursor.fetchall()
            high_risk = 0
            medium_risk = 0
            low_risk = 0
            
            for app in applications:
                application_id = app[0]
                
                try:
                    prediction = predict_process_abandonment(application_id)
                    risk_level = prediction.get("risk_level")
                    
                    if risk_level == "high":
                        high_risk += 1
                    elif risk_level == "medium":
                        medium_risk += 1
                    else:
                        low_risk += 1
                        
                except Exception as e:
                    logger.error(f"Error predicting abandonment for {application_id}: {e}")
            
            cursor.close()
            conn.close()
            
            return {
                "total_analyzed": len(applications),
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk
            }
            
        except Exception as e:
            logger.error(f"Error analyzing abandonment risks: {e}")
            raise
    
    @task
    def sync_hires_to_payroll() -> Dict[str, Any]:
        """Sincroniza nuevos contratados con payroll"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener candidatos contratados sin sincronizar con payroll
            cursor.execute("""
                SELECT DISTINCT c.candidate_id, a.application_id, j.department,
                       o.start_date, o.salary
                FROM ats_applications a
                JOIN ats_candidates c ON a.candidate_id = c.candidate_id
                JOIN ats_job_postings j ON a.job_id = j.job_id
                LEFT JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
                LEFT JOIN ats_payroll_sync ps ON c.candidate_id = ps.candidate_id
                WHERE a.status = 'hired'
                  AND ps.sync_id IS NULL
                  AND a.updated_at > NOW() - INTERVAL '7 days'
                LIMIT 10
            """)
            
            hires = cursor.fetchall()
            synced = 0
            failed = 0
            
            for hire in hires:
                candidate_id = hire[0]
                start_date = hire[3] or "2024-01-01"
                salary = float(hire[4] or 0)
                department = hire[2] or "Unknown"
                
                try:
                    result = sync_new_hire_to_payroll(
                        candidate_id=candidate_id,
                        start_date=start_date,
                        salary=salary,
                        department=department
                    )
                    
                    if result.get("success"):
                        synced += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logger.error(f"Error syncing to payroll for {candidate_id}: {e}")
                    failed += 1
            
            cursor.close()
            conn.close()
            
            return {
                "total_hires": len(hires),
                "synced": synced,
                "failed": failed
            }
            
        except Exception as e:
            logger.error(f"Error syncing to payroll: {e}")
            raise
    
    @task
    def generate_alerts() -> Dict[str, Any]:
        """Genera alertas automáticas"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            import uuid
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            alerts_created = 0
            
            # Alerta: Tests expirando pronto
            cursor.execute("""
                SELECT DISTINCT a.application_id, a.job_id, a.candidate_id, t.test_id, t.due_date
                FROM ats_assessment_tests t
                JOIN ats_applications a ON t.application_id = a.application_id
                WHERE t.status IN ('pending', 'sent')
                  AND t.due_date < NOW() + INTERVAL '2 days'
                  AND t.due_date > NOW()
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_alerts al
                      WHERE al.application_id = a.application_id
                        AND al.alert_type = 'test_expiring'
                        AND al.status = 'active'
                  )
            """)
            
            expiring_tests = cursor.fetchall()
            for test in expiring_tests:
                cursor.execute("""
                    INSERT INTO ats_alerts
                    (alert_id, alert_type, severity, application_id, job_id, candidate_id,
                     title, message, status, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"alert_{uuid.uuid4().hex[:12]}",
                    "test_expiring",
                    "medium",
                    test[0],
                    test[1],
                    test[2],
                    "Test Expiring Soon",
                    f"Assessment test expires on {test[4].strftime('%Y-%m-%d')}",
                    "active",
                    json.dumps({"test_id": test[3], "due_date": test[4].isoformat()})
                ))
                alerts_created += 1
            
            # Alerta: Aplicaciones estancadas
            cursor.execute("""
                SELECT DISTINCT a.application_id, a.job_id, a.candidate_id, a.updated_at
                FROM ats_applications a
                WHERE a.status IN ('applied', 'screening')
                  AND a.updated_at < NOW() - INTERVAL '7 days'
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_alerts al
                      WHERE al.application_id = a.application_id
                        AND al.alert_type = 'stale_application'
                        AND al.status = 'active'
                  )
            """)
            
            stale_apps = cursor.fetchall()
            for app in stale_apps:
                cursor.execute("""
                    INSERT INTO ats_alerts
                    (alert_id, alert_type, severity, application_id, job_id, candidate_id,
                     title, message, status, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"alert_{uuid.uuid4().hex[:12]}",
                    "stale_application",
                    "low",
                    app[0],
                    app[1],
                    app[2],
                    "Stale Application",
                    f"Application has not been updated in {((datetime.now() - app[3]).days)} days",
                    "active",
                    json.dumps({"last_updated": app[3].isoformat()})
                ))
                alerts_created += 1
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "alerts_created": alerts_created,
                "expiring_tests": len(expiring_tests),
                "stale_applications": len(stale_apps)
            }
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            raise
    
    # Pipeline
    background_checks_result = process_background_checks()
    abandonment_analysis = analyze_abandonment_risks()
    payroll_sync_result = sync_hires_to_payroll()
    alerts_result = generate_alerts()


hiring_extended_automation_dag = hiring_extended_automation()


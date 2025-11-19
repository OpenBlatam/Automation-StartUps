"""
Hiring Workflows Automation DAG
================================

DAG para ejecutar workflows automáticos de hiring:
- Auto-reject basado en scores
- Auto-advance para candidatos top
- Auto-schedule de entrevistas
- Notificaciones automáticas
"""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.exceptions import AirflowFailException

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.hiring_advanced import (
    execute_auto_workflows,
    calculate_advanced_ml_score,
)
from data.airflow.plugins.hiring_integrations import filter_cv_by_keywords

logger = logging.getLogger(__name__)


@dag(
    dag_id="hiring_workflows_automation",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */4 * * *",  # Cada 4 horas
    catchup=False,
    default_args={
        "owner": "hr-recruiting",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "on_failure_callback": on_task_failure,
    },
    tags=["hiring", "ats", "automation", "workflows"],
)
def hiring_workflows_automation():
    """Ejecuta workflows automáticos de hiring"""
    
    @task
    def process_new_applications_with_ml() -> Dict[str, Any]:
        """Procesa nuevas aplicaciones con scoring ML avanzado"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener aplicaciones nuevas sin ML scoring
            cursor.execute("""
                SELECT a.application_id, a.candidate_id, a.job_id,
                       c.resume_text, c.cover_letter,
                       j.keywords, j.requirements
                FROM ats_applications a
                JOIN ats_candidates c ON a.candidate_id = c.candidate_id
                JOIN ats_job_postings j ON a.job_id = j.job_id
                WHERE a.status = 'applied'
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_ml_scoring ml 
                      WHERE ml.application_id = a.application_id
                  )
                ORDER BY a.applied_at DESC
                LIMIT 50
            """)
            
            applications = cursor.fetchall()
            processed = 0
            scored = []
            
            for app in applications:
                application_id = app[0]
                resume_text = app[3] or ""
                cover_letter = app[4] or ""
                keywords = app[5] or []
                
                try:
                    # Filtrado básico primero
                    filter_result = filter_cv_by_keywords(
                        application_id=application_id,
                        resume_text=resume_text,
                        keywords=keywords,
                        cover_letter=cover_letter
                    )
                    
                    # Si pasa el filtro básico, calcular ML score avanzado
                    if filter_result.get("passed"):
                        ml_score = calculate_advanced_ml_score(
                            application_id=application_id,
                            resume_text=resume_text,
                            keywords=keywords,
                            cover_letter=cover_letter,
                            use_ml_model=True
                        )
                        scored.append({
                            "application_id": application_id,
                            "overall_score": ml_score.get("overall_score"),
                            "hire_probability": ml_score.get("predicted_hire_probability")
                        })
                    
                    processed += 1
                    
                except Exception as e:
                    logger.error(f"Error processing {application_id}: {e}")
            
            cursor.close()
            conn.close()
            
            return {
                "processed": processed,
                "scored": len(scored),
                "applications": scored[:10]  # Top 10
            }
            
        except Exception as e:
            logger.error(f"Error processing applications: {e}")
            raise
    
    @task
    def execute_workflows() -> Dict[str, Any]:
        """Ejecuta workflows automáticos para aplicaciones procesadas"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener aplicaciones que necesitan workflows
            cursor.execute("""
                SELECT DISTINCT a.application_id
                FROM ats_applications a
                LEFT JOIN ats_workflow_executions we ON a.application_id = we.application_id
                WHERE a.status IN ('applied', 'screening')
                  AND a.applied_at > NOW() - INTERVAL '7 days'
                  AND we.execution_id IS NULL
                ORDER BY a.applied_at DESC
                LIMIT 100
            """)
            
            applications = cursor.fetchall()
            executed = 0
            failed = 0
            
            for app in applications:
                application_id = app[0]
                
                try:
                    result = execute_auto_workflows(application_id)
                    executed += result.get("executed", 0)
                    failed += result.get("failed", 0)
                    
                except Exception as e:
                    logger.error(f"Error executing workflows for {application_id}: {e}")
                    failed += 1
            
            cursor.close()
            conn.close()
            
            return {
                "total_applications": len(applications),
                "workflows_executed": executed,
                "workflows_failed": failed
            }
            
        except Exception as e:
            logger.error(f"Error executing workflows: {e}")
            raise
    
    @task
    def auto_advance_top_candidates() -> Dict[str, Any]:
        """Avanza automáticamente candidatos con scores altos"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Candidatos con ML score alto que aún están en 'applied'
            cursor.execute("""
                SELECT a.application_id, ml.overall_score, ml.predicted_hire_probability
                FROM ats_applications a
                JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
                WHERE a.status = 'applied'
                  AND ml.overall_score >= 80
                  AND ml.predicted_hire_probability >= 75
                  AND a.applied_at > NOW() - INTERVAL '3 days'
                ORDER BY ml.overall_score DESC
                LIMIT 20
            """)
            
            top_candidates = cursor.fetchall()
            advanced = 0
            
            for candidate in top_candidates:
                application_id = candidate[0]
                
                try:
                    cursor.execute("""
                        UPDATE ats_applications 
                        SET status = 'screening', updated_at = NOW()
                        WHERE application_id = %s
                    """, (application_id,))
                    advanced += 1
                    
                except Exception as e:
                    logger.error(f"Error advancing {application_id}: {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "top_candidates_found": len(top_candidates),
                "advanced": advanced
            }
            
        except Exception as e:
            logger.error(f"Error auto-advancing candidates: {e}")
            raise
    
    # Pipeline
    ml_result = process_new_applications_with_ml()
    workflows_result = execute_workflows()
    advance_result = auto_advance_top_candidates()


hiring_workflows_automation_dag = hiring_workflows_automation()


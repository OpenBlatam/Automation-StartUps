"""
Hiring ATS DAG - Sistema Completo de Reclutamiento Automatizado
================================================================

Automatiza todo el proceso de hiring:
- Publicación de vacantes en múltiples plataformas simultáneamente
- Filtrado automático de CVs por palabras clave
- Programación automática de entrevistas
- Envío de tests de evaluación
- Comunicación automatizada con candidatos
- Sincronización con Greenhouse y otros ATS
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from airflow.models.param import Param

# Shared callbacks and utilities
from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
from data.airflow.plugins.etl_notifications import notify_slack

# Hiring integration functions
from data.airflow.plugins.hiring_integrations import (
    publish_job_to_multiple_platforms,
    filter_cv_by_keywords,
    schedule_interview_automatically,
    send_assessment_test,
    send_communication_to_candidate,
    sync_with_greenhouse,
)

# Advanced hiring functions
from data.airflow.plugins.hiring_advanced import (
    calculate_advanced_ml_score,
    create_referral,
    submit_feedback,
    calculate_analytics_metrics,
    create_post_hire_onboarding,
)

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore


HIRING_POOL = os.getenv("HIRING_POOL", "etl_pool")
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))


def _validate_job_posting(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validación robusta de datos de la vacante"""
    required = ["job_id", "title", "description"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise AirflowFailException(f"Missing required params: {', '.join(missing)}")
    
    # Validar que hay plataformas especificadas
    platforms = payload.get("platforms", [])
    if not platforms:
        raise AirflowFailException("At least one platform must be specified")
    
    # Validar formato de job_id
    job_id = payload.get("job_id", "")
    if not job_id or len(job_id) < 3:
        raise AirflowFailException("job_id must be at least 3 characters")
    
    return payload


def _validate_application(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validación de datos de aplicación"""
    required = ["application_id", "candidate_id", "job_id", "resume_text"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise AirflowFailException(f"Missing required params: {', '.join(missing)}")
    
    return payload


@dag(
    dag_id="hiring_ats",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "hr-recruiting",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=15),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
        "on_failure_callback": on_task_failure,
        "sla": timedelta(hours=24),
        "sla_miss_callback": sla_miss_callback,
    },
    params={
        "job_id": Param(
            "",
            type="string",
            description="ID único de la vacante",
        ),
        "title": Param(
            "",
            type="string",
            description="Título de la vacante",
        ),
        "description": Param(
            "",
            type="string",
            description="Descripción completa de la vacante",
        ),
        "requirements": Param(
            "",
            type="string",
            description="Requisitos del puesto",
        ),
        "keywords": Param(
            [],
            type="array",
            description="Lista de palabras clave para filtrado",
        ),
        "platforms": Param(
            ["linkedin", "indeed"],
            type="array",
            description="Plataformas donde publicar (greenhouse, linkedin, indeed, glassdoor, monster)",
        ),
        "department": Param(
            "",
            type="string",
            description="Departamento",
        ),
        "location": Param(
            "",
            type="string",
            description="Ubicación del trabajo",
        ),
        "employment_type": Param(
            "full_time",
            type="string",
            enum=["full_time", "part_time", "contract", "internship"],
            description="Tipo de empleo",
        ),
        "remote_type": Param(
            "remote",
            type="string",
            enum=["remote", "hybrid", "onsite"],
            description="Tipo de trabajo remoto",
        ),
        "hiring_manager_email": Param(
            "",
            type="string",
            description="Email del hiring manager",
        ),
        "recruiter_email": Param(
            "",
            type="string",
            description="Email del reclutador",
        ),
    },
    doc_md="""
    ### Hiring ATS - Sistema Completo de Reclutamiento Automatizado
    
    Automatiza completamente el proceso de hiring:
    - ✅ Publicación simultánea en múltiples plataformas (Greenhouse, LinkedIn, Indeed, etc.)
    - ✅ Filtrado automático de CVs por palabras clave
    - ✅ Programación automática de entrevistas con integración de calendario
    - ✅ Envío automático de tests de evaluación (HackerRank, Codility, custom)
    - ✅ Comunicación automatizada con candidatos (email, SMS)
    - ✅ Sincronización bidireccional con Greenhouse y otros ATS
    - ✅ Tracking completo del proceso de hiring
    - ✅ Analytics y métricas de contratación
    
    **Workflow automatizado:**
    1. Publicación de vacante en múltiples plataformas
    2. Recepción y procesamiento de aplicaciones
    3. Filtrado automático de CVs por keywords
    4. Programación automática de entrevistas
    5. Envío de tests de evaluación
    6. Comunicación con candidatos
    7. Sincronización con ATS externos
    
    **Parámetros requeridos:**
    - `job_id`: ID único de la vacante
    - `title`: Título de la vacante
    - `description`: Descripción completa
    - `platforms`: Lista de plataformas donde publicar
    
    **Parámetros opcionales:**
    - `keywords`: Palabras clave para filtrado
    - `requirements`: Requisitos del puesto
    - `hiring_manager_email`: Email del hiring manager
    - `recruiter_email`: Email del reclutador
    """,
    tags=["hiring", "ats", "recruiting", "automation"],
)
def hiring_ats():
    """Orquesta todo el proceso de hiring automatizado"""
    
    @task
    def validate_and_prepare(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Valida parámetros y prepara datos"""
        context = get_current_context()
        params = context.get("params", {})
        
        # Construir payload desde params
        job_payload = {
            "job_id": params.get("job_id", ""),
            "title": params.get("title", ""),
            "description": params.get("description", ""),
            "requirements": params.get("requirements", ""),
            "keywords": params.get("keywords", []),
            "platforms": params.get("platforms", ["linkedin", "indeed"]),
            "department": params.get("department", ""),
            "location": params.get("location", ""),
            "employment_type": params.get("employment_type", "full_time"),
            "remote_type": params.get("remote_type", "remote"),
            "hiring_manager_email": params.get("hiring_manager_email", ""),
            "recruiter_email": params.get("recruiter_email", ""),
        }
        
        validated = _validate_job_posting(job_payload)
        
        logging.info(
            "job posting validated",
            extra={
                "job_id": validated.get("job_id"),
                "platforms": validated.get("platforms"),
                "platform_count": len(validated.get("platforms", [])),
            },
        )
        
        return validated
    
    @task
    def publish_job_postings(job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publica vacante en múltiples plataformas simultáneamente"""
        job_id = job_data.get("job_id")
        platforms = job_data.get("platforms", [])
        
        if not job_id or not platforms:
            raise AirflowFailException("job_id and platforms are required")
        
        results = publish_job_to_multiple_platforms(
            job_id=job_id,
            platforms=platforms,
            job_data=job_data
        )
        
        success_count = sum(1 for r in results.values() if r.get("success"))
        total_platforms = len(platforms)
        
        logging.info(
            "job published to platforms",
            extra={
                "job_id": job_id,
                "success_count": success_count,
                "total_platforms": total_platforms,
                "results": results,
            },
        )
        
        if success_count == 0:
            raise AirflowFailException(f"Failed to publish job to any platform")
        
        return {
            "job_id": job_id,
            "platforms_published": success_count,
            "total_platforms": total_platforms,
            "results": results,
        }
    
    @task
    def process_new_applications(job_id: str) -> Dict[str, Any]:
        """
        Procesa nuevas aplicaciones:
        - Extrae texto de CVs
        - Filtra por keywords
        - Actualiza scores
        """
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener aplicaciones nuevas sin filtrar
            cursor.execute("""
                SELECT a.application_id, a.candidate_id, a.job_id,
                       c.resume_text, c.cover_letter,
                       j.keywords
                FROM ats_applications a
                JOIN ats_candidates c ON a.candidate_id = c.candidate_id
                JOIN ats_job_postings j ON a.job_id = j.job_id
                WHERE a.job_id = %s
                  AND a.status = 'applied'
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_cv_filtering f 
                      WHERE f.application_id = a.application_id
                  )
                ORDER BY a.applied_at DESC
                LIMIT 50
            """, (job_id,))
            
            applications = cursor.fetchall()
            processed = []
            passed = []
            failed = []
            
            for app in applications:
                application_id = app[0]
                resume_text = app[3] or ""
                cover_letter = app[4] or ""
                keywords = app[5] or []
                
                try:
                    filter_result = filter_cv_by_keywords(
                        application_id=application_id,
                        resume_text=resume_text,
                        keywords=keywords,
                        cover_letter=cover_letter
                    )
                    
                    processed.append(application_id)
                    if filter_result.get("passed"):
                        passed.append(application_id)
                    else:
                        failed.append(application_id)
                        
                except Exception as e:
                    logging.error(f"Error filtering CV for {application_id}: {e}")
                    failed.append(application_id)
            
            cursor.close()
            conn.close()
            
            return {
                "processed": len(processed),
                "passed": len(passed),
                "failed": len(failed),
                "application_ids": processed,
            }
            
        except Exception as e:
            logging.error(f"Error processing applications: {e}")
            raise
    
    @task
    def schedule_interviews_for_shortlisted(job_id: str) -> Dict[str, Any]:
        """
        Programa entrevistas automáticamente para candidatos shortlisted
        """
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener aplicaciones que pasaron el filtro y están listas para entrevista
            cursor.execute("""
                SELECT a.application_id, a.candidate_id, j.hiring_manager_email, j.recruiter_email
                FROM ats_applications a
                JOIN ats_job_postings j ON a.job_id = j.job_id
                JOIN ats_cv_filtering f ON a.application_id = f.application_id
                WHERE a.job_id = %s
                  AND a.status IN ('screening', 'applied')
                  AND f.passed = true
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_interviews i 
                      WHERE i.application_id = a.application_id 
                        AND i.interview_type = 'phone_screen'
                  )
                ORDER BY a.match_score DESC
                LIMIT 10
            """, (job_id,))
            
            applications = cursor.fetchall()
            scheduled = []
            failed = []
            
            for app in applications:
                application_id = app[0]
                interviewer_email = app[2] or app[3]  # hiring_manager o recruiter
                
                if not interviewer_email:
                    logging.warning(f"No interviewer email for application {application_id}")
                    continue
                
                try:
                    interview_result = schedule_interview_automatically(
                        application_id=application_id,
                        interviewer_email=interviewer_email,
                        interview_type="phone_screen",
                        duration_minutes=30
                    )
                    
                    scheduled.append({
                        "application_id": application_id,
                        "interview_id": interview_result.get("interview_id"),
                    })
                    
                except Exception as e:
                    logging.error(f"Error scheduling interview for {application_id}: {e}")
                    failed.append(application_id)
            
            cursor.close()
            conn.close()
            
            return {
                "scheduled": len(scheduled),
                "failed": len(failed),
                "interviews": scheduled,
            }
            
        except Exception as e:
            logging.error(f"Error scheduling interviews: {e}")
            raise
    
    @task
    def send_tests_to_candidates(job_id: str) -> Dict[str, Any]:
        """
        Envía tests de evaluación a candidatos que pasaron entrevistas iniciales
        """
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener aplicaciones con entrevistas completadas que aún no tienen test
            cursor.execute("""
                SELECT DISTINCT a.application_id, j.department
                FROM ats_applications a
                JOIN ats_job_postings j ON a.job_id = j.job_id
                JOIN ats_interviews i ON a.application_id = i.application_id
                WHERE a.job_id = %s
                  AND i.status = 'completed'
                  AND i.interview_type = 'phone_screen'
                  AND i.rating >= 3
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_assessment_tests t 
                      WHERE t.application_id = a.application_id
                  )
                ORDER BY i.rating DESC
                LIMIT 20
            """, (job_id,))
            
            applications = cursor.fetchall()
            sent = []
            failed = []
            
            for app in applications:
                application_id = app[0]
                department = app[1] or ""
                
                # Determinar tipo de test según departamento
                test_type = "technical"
                test_platform = "custom"
                
                if "engineering" in department.lower() or "tech" in department.lower():
                    test_type = "coding"
                    test_platform = "hackerrank"
                elif "sales" in department.lower():
                    test_type = "personality"
                    test_platform = "custom"
                
                try:
                    test_result = send_assessment_test(
                        application_id=application_id,
                        test_type=test_type,
                        test_platform=test_platform,
                        due_date_days=7
                    )
                    
                    sent.append({
                        "application_id": application_id,
                        "test_id": test_result.get("test_id"),
                        "test_type": test_type,
                    })
                    
                except Exception as e:
                    logging.error(f"Error sending test for {application_id}: {e}")
                    failed.append(application_id)
            
            cursor.close()
            conn.close()
            
            return {
                "sent": len(sent),
                "failed": len(failed),
                "tests": sent,
            }
            
        except Exception as e:
            logging.error(f"Error sending tests: {e}")
            raise
    
    @task
    def sync_with_external_ats(job_id: str) -> Dict[str, Any]:
        """
        Sincroniza con Greenhouse u otros ATS externos
        """
        greenhouse_enabled = os.getenv("GREENHOUSE_ENABLED", "false").lower() == "true"
        
        if not greenhouse_enabled:
            logging.info("Greenhouse sync not enabled")
            return {"synced": False, "reason": "not_enabled"}
        
        try:
            sync_result = sync_with_greenhouse(
                job_id=job_id,
                direction="bidirectional"
            )
            
            return {
                "synced": sync_result.get("success", False),
                "results": sync_result.get("results", {}),
            }
            
        except Exception as e:
            logging.error(f"Error syncing with external ATS: {e}")
            return {"synced": False, "error": str(e)}
    
    @task
    def notify_summary(
        publish_result: Dict[str, Any],
        process_result: Dict[str, Any],
        interview_result: Dict[str, Any],
        test_result: Dict[str, Any],
        sync_result: Dict[str, Any],
    ) -> None:
        """Envía resumen del proceso de hiring"""
        job_id = publish_result.get("job_id", "unknown")
        
        summary = f"""
🎯 Hiring ATS Process Summary - Job: {job_id}

📊 Publishing:
- Platforms published: {publish_result.get('platforms_published', 0)}/{publish_result.get('total_platforms', 0)}

📝 CV Filtering:
- Applications processed: {process_result.get('processed', 0)}
- Passed filter: {process_result.get('passed', 0)}
- Failed filter: {process_result.get('failed', 0)}

📅 Interviews:
- Interviews scheduled: {interview_result.get('scheduled', 0)}
- Failed: {interview_result.get('failed', 0)}

🧪 Tests:
- Tests sent: {test_result.get('sent', 0)}
- Failed: {test_result.get('failed', 0)}

🔄 Sync:
- External ATS synced: {sync_result.get('synced', False)}
        """
        
        try:
            notify_slack(summary)
        except Exception as e:
            logging.warning(f"Could not send Slack notification: {e}")
    
    # Pipeline execution
    job_data = validate_and_prepare({})
    publish_result = publish_job_postings(job_data)
    
    # Procesar aplicaciones (se ejecuta después de publicar)
    job_id = publish_result["job_id"]
    process_result = process_new_applications(job_id)
    
    # Programar entrevistas para candidatos que pasaron el filtro
    interview_result = schedule_interviews_for_shortlisted(job_id)
    
    # Enviar tests a candidatos que pasaron entrevistas
    test_result = send_tests_to_candidates(job_id)
    
    # Sincronizar con ATS externos
    sync_result = sync_with_external_ats(job_id)
    
    # Notificar resumen
    notify_summary(
        publish_result,
        process_result,
        interview_result,
        test_result,
        sync_result,
    )


# Crear DAG
hiring_ats_dag = hiring_ats()


# ============================================================================
# DAG ADICIONAL: Procesamiento Continuo de Aplicaciones
# ============================================================================

@dag(
    dag_id="hiring_process_applications",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 */2 * * *",  # Cada 2 horas
    catchup=False,
    default_args={
        "owner": "hr-recruiting",
        "retries": 1,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    tags=["hiring", "ats", "automation"],
)
def hiring_process_applications():
    """Procesa aplicaciones nuevas cada 2 horas"""
    
    @task
    def process_all_new_applications() -> Dict[str, Any]:
        """Procesa todas las aplicaciones nuevas sin filtrar"""
        try:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            
            hook = PostgresHook(postgres_conn_id="postgres_default")
            conn = hook.get_conn()
            cursor = conn.cursor()
            
            # Obtener todas las aplicaciones nuevas
            cursor.execute("""
                SELECT a.application_id, a.candidate_id, a.job_id,
                       c.resume_text, c.cover_letter,
                       j.keywords
                FROM ats_applications a
                JOIN ats_candidates c ON a.candidate_id = c.candidate_id
                JOIN ats_job_postings j ON a.job_id = j.job_id
                WHERE a.status = 'applied'
                  AND NOT EXISTS (
                      SELECT 1 FROM ats_cv_filtering f 
                      WHERE f.application_id = a.application_id
                  )
                ORDER BY a.applied_at DESC
                LIMIT 100
            """)
            
            applications = cursor.fetchall()
            processed = 0
            passed = 0
            failed = 0
            
            for app in applications:
                application_id = app[0]
                resume_text = app[3] or ""
                cover_letter = app[4] or ""
                keywords = app[5] or []
                
                try:
                    filter_result = filter_cv_by_keywords(
                        application_id=application_id,
                        resume_text=resume_text,
                        keywords=keywords,
                        cover_letter=cover_letter
                    )
                    
                    processed += 1
                    if filter_result.get("passed"):
                        passed += 1
                    else:
                        failed += 1
                        
                except Exception as e:
                    logging.error(f"Error filtering CV for {application_id}: {e}")
                    failed += 1
            
            cursor.close()
            conn.close()
            
            logging.info(
                "applications processed",
                extra={
                    "processed": processed,
                    "passed": passed,
                    "failed": failed,
                },
            )
            
            return {
                "processed": processed,
                "passed": passed,
                "failed": failed,
            }
            
        except Exception as e:
            logging.error(f"Error processing applications: {e}")
            raise
    
    process_all_new_applications()


# Crear DAG
hiring_process_applications_dag = hiring_process_applications()


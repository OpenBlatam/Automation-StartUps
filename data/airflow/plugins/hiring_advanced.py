"""
Funcionalidades Avanzadas para Hiring ATS
=========================================

- Scoring avanzado con Machine Learning
- Workflows automáticos (auto-reject, auto-advance)
- Sistema de referidos
- Feedback avanzado
- Analytics y métricas
- Onboarding post-hire
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def _env(name: str, default: str = "") -> str:
    """Obtiene variable de entorno con fallback a Vault"""
    try:
        from data.airflow.plugins.vault_helpers import get_config_with_fallback, migrate_env_to_vault_format
        vault_config = migrate_env_to_vault_format(name)
        if vault_config:
            vault_value = get_config_with_fallback(
                vault_config.get("vault_path", ""),
                vault_config.get("vault_key"),
                name,
                default=default,
                required=False
            )
            if vault_value:
                return vault_value
    except Exception:
        pass
    return os.getenv(name, default)


def _get_db_connection(postgres_conn_id: str = "postgres_default"):
    """Obtiene conexión a base de datos"""
    if not POSTGRES_AVAILABLE:
        return None
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        return hook.get_conn()
    except Exception as e:
        logger.error(f"Failed to get DB connection: {e}")
        raise


# ============================================================================
# SCORING AVANZADO CON MACHINE LEARNING
# ============================================================================

def calculate_advanced_ml_score(
    application_id: str,
    resume_text: str,
    keywords: List[str],
    cover_letter: Optional[str] = None,
    use_ml_model: bool = True
) -> Dict[str, Any]:
    """
    Calcula score avanzado usando ML y múltiples factores.
    
    Args:
        application_id: ID de la aplicación
        resume_text: Texto del CV
        keywords: Palabras clave del job
        cover_letter: Carta de presentación (opcional)
        use_ml_model: Usar modelo ML si está disponible
    
    Returns:
        Dict con scores detallados y predicción de hire probability
    """
    logger.info("calculating advanced ML score", extra={"application_id": application_id})
    
    # Obtener información adicional de la aplicación
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT a.application_id, a.candidate_id, a.job_id,
                   c.resume_text, c.location, c.source,
                   j.title, j.department, j.requirements
            FROM ats_applications a
            JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            JOIN ats_job_postings j ON a.job_id = j.job_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        # Calcular scores por factor
        keyword_score = _calculate_keyword_score(resume_text, keywords, cover_letter)
        experience_score = _calculate_experience_score(resume_text)
        skill_score = _calculate_skill_score(resume_text, app_data[8] or "")  # requirements
        education_score = _calculate_education_score(resume_text)
        cultural_fit_score = _calculate_cultural_fit_score(resume_text, cover_letter)
        
        # Score general (promedio ponderado)
        overall_score = (
            keyword_score * 0.30 +
            experience_score * 0.25 +
            skill_score * 0.25 +
            education_score * 0.10 +
            cultural_fit_score * 0.10
        )
        
        # Predicción ML si está habilitada
        hire_probability = overall_score  # Default
        if use_ml_model:
            ml_prediction = _get_ml_prediction(application_id, {
                "keyword_score": keyword_score,
                "experience_score": experience_score,
                "skill_score": skill_score,
                "education_score": education_score,
                "cultural_fit_score": cultural_fit_score,
                "source": app_data[5],  # source
            })
            if ml_prediction:
                hire_probability = ml_prediction.get("hire_probability", overall_score)
        
        result = {
            "overall_score": round(overall_score, 2),
            "keyword_score": round(keyword_score, 2),
            "experience_score": round(experience_score, 2),
            "skill_score": round(skill_score, 2),
            "education_score": round(education_score, 2),
            "cultural_fit_score": round(cultural_fit_score, 2),
            "predicted_hire_probability": round(hire_probability, 2),
            "scoring_factors": {
                "keyword_match": keyword_score,
                "years_experience": _extract_years_experience(resume_text),
                "skill_match": skill_score,
                "education_level": _extract_education_level(resume_text),
            }
        }
        
        # Guardar en BD
        cursor.execute("""
            INSERT INTO ats_ml_scoring 
            (application_id, overall_score, keyword_score, experience_score,
             skill_score, education_score, cultural_fit_score,
             predicted_hire_probability, scoring_factors, model_features)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            application_id,
            result["overall_score"],
            result["keyword_score"],
            result["experience_score"],
            result["skill_score"],
            result["education_score"],
            result["cultural_fit_score"],
            result["predicted_hire_probability"],
            json.dumps(result["scoring_factors"]),
            json.dumps({"model_version": "v1.0", "use_ml": use_ml_model})
        ))
        
        # Actualizar match_score en application
        cursor.execute("""
            UPDATE ats_applications 
            SET match_score = %s, updated_at = NOW()
            WHERE application_id = %s
        """, (result["overall_score"], application_id))
        
        conn.commit()
        logger.info("advanced ML score calculated", extra={
            "application_id": application_id,
            "overall_score": result["overall_score"],
            "hire_probability": result["predicted_hire_probability"]
        })
        
        return result
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error calculating advanced ML score: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _calculate_keyword_score(resume_text: str, keywords: List[str], cover_letter: Optional[str]) -> float:
    """Calcula score basado en keywords"""
    if not keywords:
        return 100.0
    
    full_text = (resume_text or "").lower()
    if cover_letter:
        full_text += " " + cover_letter.lower()
    
    import re
    matched = 0
    for keyword in keywords:
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, full_text, re.IGNORECASE):
            matched += 1
    
    return (matched / len(keywords)) * 100


def _calculate_experience_score(resume_text: str) -> float:
    """Calcula score basado en años de experiencia"""
    years = _extract_years_experience(resume_text)
    
    # Scoring: 0-2 años = 40, 3-5 = 70, 6-10 = 90, 10+ = 100
    if years >= 10:
        return 100.0
    elif years >= 6:
        return 90.0
    elif years >= 3:
        return 70.0
    elif years >= 1:
        return 40.0
    else:
        return 20.0


def _calculate_skill_score(resume_text: str, requirements: str) -> float:
    """Calcula score basado en match de skills"""
    if not requirements:
        return 50.0
    
    # Extraer skills de requirements (simplificado)
    import re
    tech_skills = re.findall(r'\b(python|java|javascript|react|aws|docker|kubernetes|sql|postgresql|mongodb|redis)\b', 
                            requirements.lower())
    
    resume_lower = resume_text.lower()
    matched_skills = sum(1 for skill in tech_skills if skill in resume_lower)
    
    if not tech_skills:
        return 50.0
    
    return (matched_skills / len(tech_skills)) * 100


def _calculate_education_score(resume_text: str) -> float:
    """Calcula score basado en educación"""
    education_level = _extract_education_level(resume_text)
    
    # Scoring: PhD = 100, Master = 90, Bachelor = 70, Associate = 50, Other = 30
    scores = {
        "phd": 100.0,
        "doctorate": 100.0,
        "master": 90.0,
        "mba": 90.0,
        "bachelor": 70.0,
        "bachelor's": 70.0,
        "degree": 70.0,
        "associate": 50.0,
        "diploma": 30.0,
    }
    
    resume_lower = resume_text.lower()
    for level, score in scores.items():
        if level in resume_lower:
            return score
    
    return 30.0  # Default


def _calculate_cultural_fit_score(resume_text: str, cover_letter: Optional[str]) -> float:
    """Calcula score de cultural fit"""
    full_text = (resume_text or "").lower()
    if cover_letter:
        full_text += " " + cover_letter.lower()
    
    # Buscar palabras clave de cultural fit
    positive_keywords = ["team", "collaboration", "innovation", "passion", "growth", "learning", "impact"]
    negative_keywords = ["solo", "independent", "lone", "individual"]
    
    positive_count = sum(1 for kw in positive_keywords if kw in full_text)
    negative_count = sum(1 for kw in negative_keywords if kw in full_text)
    
    score = min(positive_count * 15, 100) - (negative_count * 10)
    return max(score, 0)


def _extract_years_experience(resume_text: str) -> int:
    """Extrae años de experiencia del CV"""
    import re
    
    # Buscar patrones como "5 years", "5+ years", "5 yeras of experience"
    patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'experience[:\s]+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*years?\s*in',
    ]
    
    years = 0
    for pattern in patterns:
        matches = re.findall(pattern, resume_text.lower())
        if matches:
            years = max(years, max(int(m) for m in matches))
    
    return years


def _extract_education_level(resume_text: str) -> str:
    """Extrae nivel de educación"""
    resume_lower = resume_text.lower()
    
    if "phd" in resume_lower or "doctorate" in resume_lower:
        return "phd"
    elif "master" in resume_lower or "mba" in resume_lower:
        return "master"
    elif "bachelor" in resume_lower or "degree" in resume_lower:
        return "bachelor"
    elif "associate" in resume_lower:
        return "associate"
    else:
        return "other"


def _get_ml_prediction(application_id: str, features: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Obtiene predicción desde modelo ML"""
    ml_endpoint = _env("ATS_ML_MODEL_ENDPOINT")
    
    if not ml_endpoint or not REQUESTS_AVAILABLE:
        return None
    
    try:
        response = requests.post(
            ml_endpoint,
            json={
                "application_id": application_id,
                "features": features
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Could not get ML prediction: {e}")
        return None


# ============================================================================
# WORKFLOWS AUTOMÁTICOS
# ============================================================================

def execute_auto_workflows(application_id: str) -> Dict[str, Any]:
    """
    Ejecuta workflows automáticos basados en condiciones.
    
    Tipos de workflows:
    - auto_reject: Rechaza automáticamente si no cumple criterios
    - auto_advance: Avanza automáticamente a siguiente etapa
    - auto_schedule: Programa entrevista automáticamente
    - auto_notify: Envía notificaciones automáticas
    """
    logger.info("executing auto workflows", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener workflows activos
        cursor.execute("""
            SELECT workflow_id, workflow_name, workflow_type, trigger_conditions, actions
            FROM ats_workflows
            WHERE enabled = true
            ORDER BY priority DESC
        """)
        
        workflows = cursor.fetchall()
        executed = []
        failed = []
        
        for workflow in workflows:
            workflow_id = workflow[0]
            workflow_type = workflow[2]
            trigger_conditions = workflow[3]
            actions = workflow[4]
            
            try:
                # Verificar condiciones
                if _check_workflow_conditions(application_id, trigger_conditions):
                    # Ejecutar acciones
                    result = _execute_workflow_actions(application_id, workflow_type, actions)
                    
                    # Registrar ejecución
                    execution_id = f"exec_{uuid.uuid4().hex[:12]}"
                    cursor.execute("""
                        INSERT INTO ats_workflow_executions
                        (execution_id, workflow_id, application_id, trigger_event,
                         status, actions_executed, executed_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        execution_id,
                        workflow_id,
                        application_id,
                        "auto_trigger",
                        "completed",
                        json.dumps(result),
                        datetime.now(timezone.utc)
                    ))
                    
                    executed.append(workflow_id)
                else:
                    logger.debug(f"Workflow conditions not met: {workflow_id}")
                    
            except Exception as e:
                logger.error(f"Error executing workflow {workflow_id}: {e}")
                failed.append(workflow_id)
        
        conn.commit()
        
        return {
            "executed": len(executed),
            "failed": len(failed),
            "workflows": executed
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error executing auto workflows: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _check_workflow_conditions(application_id: str, conditions: Dict[str, Any]) -> bool:
    """Verifica si se cumplen las condiciones del workflow"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos de la aplicación
        cursor.execute("""
            SELECT a.status, a.match_score, a.job_id,
                   ml.overall_score, ml.predicted_hire_probability
            FROM ats_applications a
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            return False
        
        status = app_data[0]
        match_score = app_data[1] or 0
        ml_score = app_data[3] or 0
        
        # Verificar condiciones
        if conditions.get("min_match_score") and match_score < conditions["min_match_score"]:
            return False
        
        if conditions.get("min_ml_score") and ml_score < conditions["min_ml_score"]:
            return False
        
        if conditions.get("status_equals") and status != conditions["status_equals"]:
            return False
        
        if conditions.get("status_not_equals") and status == conditions["status_not_equals"]:
            return False
        
        return True
        
    finally:
        cursor.close()
        conn.close()


def _execute_workflow_actions(application_id: str, workflow_type: str, actions: Dict[str, Any]) -> Dict[str, Any]:
    """Ejecuta acciones del workflow"""
    results = {}
    
    if workflow_type == "auto_reject":
        # Rechazar aplicación
        from data.airflow.plugins.hiring_integrations import send_communication_to_candidate
        
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE ats_applications 
                SET status = 'rejected',
                    rejection_reason = %s,
                    rejection_stage = 'auto_workflow',
                    updated_at = NOW()
                WHERE application_id = %s
            """, (actions.get("rejection_message", "Did not meet minimum requirements"), application_id))
            
            # Obtener candidate_id para enviar comunicación
            cursor.execute("""
                SELECT candidate_id FROM ats_applications WHERE application_id = %s
            """, (application_id,))
            candidate_data = cursor.fetchone()
            
            if candidate_data and actions.get("send_notification"):
                send_communication_to_candidate(
                    candidate_id=candidate_data[0],
                    communication_type="email",
                    subject="Update on Your Application",
                    body=actions.get("rejection_message", "Thank you for your interest...")
                )
            
            conn.commit()
            results["rejected"] = True
            
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    elif workflow_type == "auto_advance":
        # Avanzar a siguiente etapa
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        try:
            new_status = actions.get("advance_to", "screening")
            cursor.execute("""
                UPDATE ats_applications 
                SET status = %s, updated_at = NOW()
                WHERE application_id = %s
            """, (new_status, application_id))
            conn.commit()
            results["advanced"] = True
            results["new_status"] = new_status
            
        except Exception as e:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()
    
    elif workflow_type == "auto_schedule":
        # Programar entrevista automáticamente
        from data.airflow.plugins.hiring_integrations import schedule_interview_automatically
        
        interviewer_email = actions.get("interviewer_email")
        if interviewer_email:
            interview_result = schedule_interview_automatically(
                application_id=application_id,
                interviewer_email=interviewer_email,
                interview_type=actions.get("interview_type", "phone_screen"),
                duration_minutes=actions.get("duration_minutes", 30)
            )
            results["interview_scheduled"] = True
            results["interview_id"] = interview_result.get("interview_id")
    
    return results


# ============================================================================
# SISTEMA DE REFERIDOS
# ============================================================================

def create_referral(
    referrer_email: str,
    candidate_email: str,
    job_id: str,
    referrer_name: Optional[str] = None
) -> Dict[str, Any]:
    """Crea un referral y lo asocia con candidato y job"""
    logger.info("creating referral", extra={"referrer_email": referrer_email, "job_id": job_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Buscar candidato por email
        cursor.execute("""
            SELECT candidate_id, first_name, last_name 
            FROM ats_candidates 
            WHERE email = %s
        """, (candidate_email,))
        
        candidate_data = cursor.fetchone()
        if not candidate_data:
            raise ValueError(f"Candidate with email {candidate_email} not found")
        
        candidate_id = candidate_data[0]
        
        # Crear referral
        referral_id = f"ref_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_referrals
            (referral_id, referrer_email, referrer_name, candidate_id, job_id, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            referral_id,
            referrer_email,
            referrer_name,
            candidate_id,
            job_id,
            "pending"
        ))
        
        # Actualizar source del candidato si no está configurado
        cursor.execute("""
            UPDATE ats_candidates 
            SET source = 'referral', referral_email = %s, updated_at = NOW()
            WHERE candidate_id = %s AND (source IS NULL OR source = 'direct')
        """, (referrer_email, candidate_id))
        
        conn.commit()
        
        logger.info("referral created", extra={"referral_id": referral_id})
        
        return {
            "referral_id": referral_id,
            "candidate_id": candidate_id,
            "status": "pending"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating referral: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def process_referral_bonus(referral_id: str, bonus_amount: float) -> Dict[str, Any]:
    """Procesa pago de bono por referral"""
    logger.info("processing referral bonus", extra={"referral_id": referral_id, "bonus_amount": bonus_amount})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE ats_referrals
            SET bonus_amount = %s,
                bonus_paid = true,
                bonus_paid_at = NOW(),
                status = 'hired',
                updated_at = NOW()
            WHERE referral_id = %s
        """, (bonus_amount, referral_id))
        
        conn.commit()
        
        return {"success": True, "bonus_paid": True}
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error processing referral bonus: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# FEEDBACK AVANZADO
# ============================================================================

def submit_feedback(
    application_id: str,
    reviewer_email: str,
    overall_rating: int,
    feedback_text: str,
    interview_id: Optional[str] = None,
    technical_skills: Optional[int] = None,
    communication_skills: Optional[int] = None,
    cultural_fit: Optional[int] = None,
    recommendation: Optional[str] = None
) -> Dict[str, Any]:
    """Envía feedback avanzado sobre un candidato"""
    logger.info("submitting feedback", extra={"application_id": application_id, "reviewer_email": reviewer_email})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        feedback_id = f"feedback_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_feedback
            (feedback_id, application_id, interview_id, feedback_type,
             reviewer_email, overall_rating, technical_skills, communication_skills,
             cultural_fit, recommendation, feedback_text)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            feedback_id,
            application_id,
            interview_id,
            "interview" if interview_id else "application",
            reviewer_email,
            overall_rating,
            technical_skills,
            communication_skills,
            cultural_fit,
            recommendation,
            feedback_text
        ))
        
        # Actualizar rating en interview si aplica
        if interview_id:
            cursor.execute("""
                UPDATE ats_interviews
                SET rating = %s, feedback = %s, updated_at = NOW()
                WHERE interview_id = %s
            """, (overall_rating, feedback_text, interview_id))
        
        conn.commit()
        
        logger.info("feedback submitted", extra={"feedback_id": feedback_id})
        
        return {
            "feedback_id": feedback_id,
            "success": True
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error submitting feedback: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ANALYTICS Y MÉTRICAS
# ============================================================================

def calculate_analytics_metrics(job_id: Optional[str] = None) -> Dict[str, Any]:
    """Calcula métricas avanzadas de hiring"""
    logger.info("calculating analytics metrics", extra={"job_id": job_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Time to fill
        cursor.execute("""
            SELECT 
                j.job_id,
                AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) as avg_time_to_fill
            FROM ats_job_postings j
            JOIN ats_applications a ON j.job_id = a.job_id
            WHERE a.status = 'hired'
              AND j.posted_at IS NOT NULL
              AND (%s IS NULL OR j.job_id = %s)
            GROUP BY j.job_id
        """, (job_id, job_id))
        
        time_to_fill = cursor.fetchall()
        
        # Time to hire
        cursor.execute("""
            SELECT 
                job_id,
                AVG(EXTRACT(EPOCH FROM (updated_at - applied_at)) / 86400) as avg_time_to_hire
            FROM ats_applications
            WHERE status = 'hired'
              AND (%s IS NULL OR job_id = %s)
            GROUP BY job_id
        """, (job_id, job_id))
        
        time_to_hire = cursor.fetchall()
        
        # Conversion rates
        cursor.execute("""
            SELECT 
                job_id,
                COUNT(*) FILTER (WHERE status = 'hired')::DECIMAL / NULLIF(COUNT(*), 0) * 100 as hire_rate,
                COUNT(*) FILTER (WHERE status = 'interviewing')::DECIMAL / NULLIF(COUNT(*), 0) * 100 as interview_rate
            FROM ats_applications
            WHERE %s IS NULL OR job_id = %s
            GROUP BY job_id
        """, (job_id, job_id))
        
        conversion_rates = cursor.fetchall()
        
        # Guardar métricas
        metrics = []
        for metric_type, data in [
            ("time_to_fill", time_to_fill),
            ("time_to_hire", time_to_hire),
            ("conversion_rate", conversion_rates)
        ]:
            for row in data:
                metric_id = f"metric_{uuid.uuid4().hex[:12]}"
                cursor.execute("""
                    INSERT INTO ats_analytics
                    (metric_id, metric_name, metric_type, job_id, metric_value, calculated_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    metric_id,
                    f"{metric_type}_{row[0]}",
                    metric_type,
                    row[0],
                    float(row[1]) if row[1] else 0,
                    datetime.now(timezone.utc)
                ))
                metrics.append(metric_id)
        
        conn.commit()
        
        return {
            "metrics_calculated": len(metrics),
            "metric_ids": metrics
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error calculating analytics: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ONBOARDING POST-HIRE
# ============================================================================

def create_post_hire_onboarding(
    application_id: str,
    hire_date: str,
    start_date: str
) -> Dict[str, Any]:
    """Crea proceso de onboarding post-hire"""
    logger.info("creating post-hire onboarding", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información de la aplicación
        cursor.execute("""
            SELECT a.candidate_id, a.job_id, c.email, c.first_name, c.last_name
            FROM ats_applications a
            JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        candidate_id = app_data[0]
        job_id = app_data[1]
        
        # Crear onboarding
        onboarding_id = f"onboard_{uuid.uuid4().hex[:12]}"
        
        onboarding_tasks = {
            "welcome_email": {"status": "pending", "due_date": hire_date},
            "documents": {"status": "pending", "due_date": start_date},
            "background_check": {"status": "pending", "due_date": start_date},
            "equipment_setup": {"status": "pending", "due_date": start_date},
            "access_provisioning": {"status": "pending", "due_date": start_date},
        }
        
        cursor.execute("""
            INSERT INTO ats_post_hire_onboarding
            (onboarding_id, application_id, candidate_id, job_id,
             hire_date, start_date, onboarding_tasks, total_tasks)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            onboarding_id,
            application_id,
            candidate_id,
            job_id,
            hire_date,
            start_date,
            json.dumps(onboarding_tasks),
            len(onboarding_tasks)
        ))
        
        conn.commit()
        
        logger.info("post-hire onboarding created", extra={"onboarding_id": onboarding_id})
        
        return {
            "onboarding_id": onboarding_id,
            "candidate_id": candidate_id,
            "tasks": len(onboarding_tasks)
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating post-hire onboarding: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


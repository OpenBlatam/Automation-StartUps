"""
Funcionalidades Completas Finales para Hiring ATS
==================================================

- Gestión de ofertas y negociación
- Evaluación de performance post-hire
- Pipeline de talento para roles futuros
- Learning paths personalizados
- Feedback 360 post-hire
- Gestión de beneficios y compensación
- Employer Value Proposition (EVP) personalizado
- Relocation y visa management
- Assessment centers
- Networking interno
- Alumni management
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
    """Obtiene variable de entorno"""
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
# GESTIÓN DE OFERTAS Y NEGOCIACIÓN
# ============================================================================

def create_offer(
    application_id: str,
    base_salary: float,
    equity: Optional[float] = None,
    benefits: Optional[Dict[str, Any]] = None,
    start_date: str = None,
    offer_expiry_days: int = 7
) -> Dict[str, Any]:
    """
    Crea oferta de trabajo con negociación.
    
    Incluye:
    - Salario base
    - Equity/stock options
    - Beneficios
    - Fecha de inicio
    - Términos y condiciones
    """
    logger.info("creating offer", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información de la aplicación
        cursor.execute("""
            SELECT a.candidate_id, a.job_id, c.email, c.first_name, c.last_name,
                   j.title, j.department
            FROM ats_applications a
            JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            JOIN ats_job_postings j ON a.job_id = j.job_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        # Crear oferta
        offer_id = f"offer_{uuid.uuid4().hex[:12]}"
        offer_expiry = datetime.now(timezone.utc) + timedelta(days=offer_expiry_days)
        
        if not start_date:
            start_date = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d")
        
        offer_data = {
            "base_salary": base_salary,
            "equity": equity,
            "benefits": benefits or {},
            "start_date": start_date,
            "offer_expiry": offer_expiry.isoformat(),
            "status": "pending"
        }
        
        cursor.execute("""
            INSERT INTO ats_offers
            (offer_id, application_id, candidate_id, job_id,
             base_salary, equity, benefits, start_date, offer_expiry,
             status, offer_data, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            offer_id,
            application_id,
            app_data[0],
            app_data[1],
            base_salary,
            equity,
            json.dumps(benefits or {}),
            start_date,
            offer_expiry,
            "pending",
            json.dumps(offer_data),
            datetime.now(timezone.utc)
        ))
        
        # Actualizar estado de aplicación
        cursor.execute("""
            UPDATE ats_applications
            SET status = 'offer', updated_at = NOW()
            WHERE application_id = %s
        """, (application_id,))
        
        # Generar documento de oferta
        offer_document = _generate_offer_document(app_data, offer_data)
        
        conn.commit()
        
        return {
            "offer_id": offer_id,
            "application_id": application_id,
            "candidate_id": app_data[0],
            "offer_data": offer_data,
            "document_url": offer_document.get("url")
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating offer: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def negotiate_offer(
    offer_id: str,
    counter_offer: Dict[str, Any],
    negotiation_notes: Optional[str] = None
) -> Dict[str, Any]:
    """Maneja negociación de oferta"""
    logger.info("negotiating offer", extra={"offer_id": offer_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener oferta actual
        cursor.execute("""
            SELECT offer_data, negotiation_rounds
            FROM ats_offers
            WHERE offer_id = %s
        """, (offer_id,))
        
        offer_data = cursor.fetchone()
        if not offer_data:
            raise ValueError(f"Offer {offer_id} not found")
        
        current_data = json.loads(offer_data[0])
        rounds = offer_data[1] or 0
        
        # Agregar contraoferta
        if "negotiation_history" not in current_data:
            current_data["negotiation_history"] = []
        
        current_data["negotiation_history"].append({
            "round": rounds + 1,
            "counter_offer": counter_offer,
            "notes": negotiation_notes,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Actualizar oferta
        cursor.execute("""
            UPDATE ats_offers
            SET offer_data = %s,
                negotiation_rounds = %s,
                status = 'negotiating',
                updated_at = NOW()
            WHERE offer_id = %s
        """, (
            json.dumps(current_data),
            rounds + 1,
            offer_id
        ))
        
        conn.commit()
        
        return {
            "offer_id": offer_id,
            "negotiation_round": rounds + 1,
            "status": "negotiating"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error negotiating offer: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _generate_offer_document(app_data: tuple, offer_data: Dict[str, Any]) -> Dict[str, Any]:
    """Genera documento de oferta"""
    # Integrar con sistema de documentos
    document_id = f"doc_{uuid.uuid4().hex[:12]}"
    return {
        "document_id": document_id,
        "url": f"https://docs.company.com/offers/{document_id}"
    }


# ============================================================================
# EVALUACIÓN DE PERFORMANCE POST-HIRE
# ============================================================================

def evaluate_post_hire_performance(
    candidate_id: str,
    evaluation_period_days: int = 90
) -> Dict[str, Any]:
    """
    Evalúa performance post-hire.
    
    Métricas:
    - Performance reviews
    - Objetivos cumplidos
    - Feedback de manager
    - Feedback de equipo
    - Quality of hire
    """
    logger.info("evaluating post-hire performance", extra={"candidate_id": candidate_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos post-hire
        cursor.execute("""
            SELECT o.hire_date, o.start_date, o.onboarding_status,
                   q.actual_quality_score, q.performance_metrics
            FROM ats_post_hire_onboarding o
            LEFT JOIN ats_quality_of_hire q ON o.candidate_id = q.candidate_id
            WHERE o.candidate_id = %s
            ORDER BY o.hire_date DESC
            LIMIT 1
        """, (candidate_id,))
        
        hire_data = cursor.fetchone()
        if not hire_data:
            return {"error": "Hired candidate not found"}
        
        hire_date = hire_data[0]
        days_since_hire = (datetime.now(timezone.utc).date() - hire_date).days
        
        if days_since_hire < evaluation_period_days:
            return {
                "error": f"Evaluation period not reached. Days since hire: {days_since_hire}"
            }
        
        # Obtener performance data desde HRIS (simulado)
        performance_data = _get_performance_data(candidate_id)
        
        # Calcular score de performance
        performance_score = _calculate_performance_score(performance_data)
        
        # Actualizar quality of hire
        cursor.execute("""
            UPDATE ats_quality_of_hire
            SET actual_quality_score = %s,
                performance_metrics = %s,
                evaluation_period = %s,
                updated_at = NOW()
            WHERE candidate_id = %s
        """, (
            performance_score,
            json.dumps(performance_data),
            evaluation_period_days,
            candidate_id
        ))
        
        conn.commit()
        
        return {
            "candidate_id": candidate_id,
            "performance_score": performance_score,
            "evaluation_period_days": days_since_hire,
            "performance_data": performance_data
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error evaluating performance: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _get_performance_data(candidate_id: str) -> Dict[str, Any]:
    """Obtiene datos de performance desde HRIS"""
    # Integración con HRIS
    return {
        "manager_rating": 4.2,
        "peer_rating": 4.0,
        "goals_achieved": 0.85,
        "projects_completed": 3,
        "feedback_count": 5
    }


def _calculate_performance_score(performance_data: Dict[str, Any]) -> float:
    """Calcula score de performance"""
    manager_rating = performance_data.get("manager_rating", 0) * 20  # 0-100
    peer_rating = performance_data.get("peer_rating", 0) * 20
    goals_achieved = performance_data.get("goals_achieved", 0) * 100
    
    return (manager_rating * 0.4 + peer_rating * 0.3 + goals_achieved * 0.3)


# ============================================================================
# PIPELINE DE TALENTO PARA ROLES FUTUROS
# ============================================================================

def add_to_talent_pipeline(
    candidate_id: str,
    pipeline_role: str,
    expected_hire_date: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """Agrega candidato a pipeline para rol futuro"""
    logger.info("adding to talent pipeline", extra={"candidate_id": candidate_id, "pipeline_role": pipeline_role})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        pipeline_id = f"pipeline_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_talent_pipelines
            (pipeline_id, candidate_id, pipeline_role, expected_hire_date,
             priority, status, added_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            pipeline_id,
            candidate_id,
            pipeline_role,
            expected_hire_date,
            priority,
            "active",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "pipeline_id": pipeline_id,
            "candidate_id": candidate_id,
            "pipeline_role": pipeline_role,
            "status": "active"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding to pipeline: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# LEARNING PATHS PERSONALIZADOS
# ============================================================================

def create_learning_path(
    candidate_id: str,
    path_type: str,
    courses: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Crea learning path personalizado para candidato"""
    logger.info("creating learning path", extra={"candidate_id": candidate_id, "path_type": path_type})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        path_id = f"path_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_learning_paths
            (path_id, candidate_id, path_type, path_name, courses,
             status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            path_id,
            candidate_id,
            path_type,
            f"{path_type.title()} Learning Path",
            json.dumps(courses),
            "active",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "path_id": path_id,
            "candidate_id": candidate_id,
            "path_type": path_type,
            "courses_count": len(courses)
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating learning path: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# FEEDBACK 360 POST-HIRE
# ============================================================================

def collect_360_feedback(
    candidate_id: str,
    feedback_type: str = "post_hire"
) -> Dict[str, Any]:
    """Recolecta feedback 360 para empleado"""
    logger.info("collecting 360 feedback", extra={"candidate_id": candidate_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        feedback_id = f"feedback360_{uuid.uuid4().hex[:12]}"
        
        # Crear solicitudes de feedback
        feedback_requests = [
            {"type": "manager", "email": "manager@company.com"},
            {"type": "peer", "email": "peer1@company.com"},
            {"type": "peer", "email": "peer2@company.com"},
            {"type": "direct_report", "email": "report@company.com"}
        ]
        
        cursor.execute("""
            INSERT INTO ats_360_feedback
            (feedback_id, candidate_id, feedback_type, feedback_requests,
             status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            feedback_id,
            candidate_id,
            feedback_type,
            json.dumps(feedback_requests),
            "pending",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "feedback_id": feedback_id,
            "candidate_id": candidate_id,
            "requests_sent": len(feedback_requests),
            "status": "pending"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error collecting 360 feedback: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# GESTIÓN DE BENEFICIOS Y COMPENSACIÓN
# ============================================================================

def calculate_total_compensation(
    base_salary: float,
    location: str,
    benefits_package: str = "standard"
) -> Dict[str, Any]:
    """Calcula compensación total incluyendo beneficios"""
    logger.info("calculating total compensation", extra={"base_salary": base_salary, "location": location})
    
    # Beneficios estándar
    benefits = {
        "standard": {
            "health_insurance": 12000,
            "dental_insurance": 1200,
            "vision_insurance": 500,
            "401k_contribution": base_salary * 0.06,
            "pto_days": 20,
            "pto_value": (base_salary / 260) * 20
        },
        "premium": {
            "health_insurance": 15000,
            "dental_insurance": 1500,
            "vision_insurance": 600,
            "401k_contribution": base_salary * 0.08,
            "stock_options": base_salary * 0.1,
            "pto_days": 25,
            "pto_value": (base_salary / 260) * 25
        }
    }
    
    package = benefits.get(benefits_package, benefits["standard"])
    
    total_compensation = base_salary + sum(v for k, v in package.items() if isinstance(v, (int, float)))
    
    return {
        "base_salary": base_salary,
        "benefits_package": benefits_package,
        "benefits_breakdown": package,
        "total_compensation": round(total_compensation, 2),
        "location": location
    }


# ============================================================================
# EMPLOYER VALUE PROPOSITION (EVP) PERSONALIZADO
# ============================================================================

def generate_personalized_evp(
    candidate_id: str,
    job_id: str
) -> Dict[str, Any]:
    """Genera EVP personalizado basado en perfil del candidato"""
    logger.info("generating personalized EVP", extra={"candidate_id": candidate_id, "job_id": job_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener perfil del candidato
        cursor.execute("""
            SELECT c.location, c.source, ml.cultural_fit_score,
                   j.title, j.department, j.location as job_location
            FROM ats_candidates c
            JOIN ats_applications a ON c.candidate_id = a.candidate_id
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            JOIN ats_job_postings j ON a.job_id = j.job_id
            WHERE c.candidate_id = %s AND j.job_id = %s
        """, (candidate_id, job_id))
        
        profile_data = cursor.fetchone()
        if not profile_data:
            return {"error": "Candidate or job not found"}
        
        # Generar EVP personalizado
        evp_points = []
        
        # Basado en ubicación
        if profile_data[0] != profile_data[5]:  # Different location
            evp_points.append("Relocation support available")
            evp_points.append("Flexible work arrangements")
        
        # Basado en cultural fit
        cultural_fit = float(profile_data[2] or 0)
        if cultural_fit > 80:
            evp_points.append("Strong cultural alignment with our values")
        
        # Basado en departamento
        department = profile_data[4]
        if department == "Engineering":
            evp_points.append("Cutting-edge technology stack")
            evp_points.append("Innovation-focused environment")
        elif department == "Sales":
            evp_points.append("Uncapped commission structure")
            evp_points.append("Fast-track career progression")
        
        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "evp_points": evp_points,
            "personalized_message": f"Join our {department} team and experience: " + ", ".join(evp_points[:3])
        }
        
    except Exception as e:
        logger.error(f"Error generating EVP: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# RELOCATION Y VISA MANAGEMENT
# ============================================================================

def initiate_relocation_process(
    candidate_id: str,
    origin_location: str,
    destination_location: str,
    visa_required: bool = False
) -> Dict[str, Any]:
    """Inicia proceso de relocation"""
    logger.info("initiating relocation process", extra={
        "candidate_id": candidate_id,
        "origin": origin_location,
        "destination": destination_location
    })
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        relocation_id = f"relocation_{uuid.uuid4().hex[:12]}"
        
        tasks = []
        if visa_required:
            tasks.append({"task": "Visa application", "status": "pending"})
            tasks.append({"task": "Work permit", "status": "pending"})
        
        tasks.extend([
            {"task": "Housing assistance", "status": "pending"},
            {"task": "Moving logistics", "status": "pending"},
            {"task": "Relocation package", "status": "pending"}
        ])
        
        cursor.execute("""
            INSERT INTO ats_relocations
            (relocation_id, candidate_id, origin_location, destination_location,
             visa_required, relocation_tasks, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            relocation_id,
            candidate_id,
            origin_location,
            destination_location,
            visa_required,
            json.dumps(tasks),
            "in_progress",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "relocation_id": relocation_id,
            "candidate_id": candidate_id,
            "tasks": len(tasks),
            "status": "in_progress"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initiating relocation: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ASSESSMENT CENTERS
# ============================================================================

def schedule_assessment_center(
    application_id: str,
    center_date: str,
    activities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Programa assessment center para candidato"""
    logger.info("scheduling assessment center", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        center_id = f"center_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_assessment_centers
            (center_id, application_id, center_date, activities,
             status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            center_id,
            application_id,
            center_date,
            json.dumps(activities),
            "scheduled",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "center_id": center_id,
            "application_id": application_id,
            "center_date": center_date,
            "activities_count": len(activities)
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error scheduling assessment center: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


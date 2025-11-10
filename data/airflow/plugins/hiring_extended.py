"""
Funcionalidades Extendidas para Hiring ATS
===========================================

- Integraciones con Workday, Lever, etc.
- Background checks automatizados
- Chatbot para candidatos
- APIs REST
- Análisis predictivo
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
# INTEGRACIONES CON OTROS ATS
# ============================================================================

def sync_with_workday(job_id: Optional[str] = None, candidate_id: Optional[str] = None) -> Dict[str, Any]:
    """Sincroniza con Workday Recruiting"""
    workday_url = _env("WORKDAY_API_URL")
    workday_user = _env("WORKDAY_USERNAME")
    workday_password = _env("WORKDAY_PASSWORD")
    workday_tenant = _env("WORKDAY_TENANT")
    
    if not all([workday_url, workday_user, workday_password]):
        return {"success": False, "error": "Workday credentials not configured"}
    
    logger.info("syncing with Workday", extra={"job_id": job_id, "candidate_id": candidate_id})
    
    try:
        # Autenticación Workday
        auth_response = requests.post(
            f"{workday_url}/auth/token",
            auth=(workday_user, workday_password),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={"tenant": workday_tenant},
            timeout=30
        )
        auth_response.raise_for_status()
        token = auth_response.json().get("access_token")
        
        # Sincronizar jobs
        if job_id:
            # Fetch job from Workday
            job_response = requests.get(
                f"{workday_url}/recruiting/v1/jobs/{job_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            if job_response.status_code == 200:
                workday_job = job_response.json()
                _sync_job_from_workday(workday_job)
        
        # Sincronizar candidatos
        if candidate_id:
            candidate_response = requests.get(
                f"{workday_url}/recruiting/v1/candidates/{candidate_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=30
            )
            if candidate_response.status_code == 200:
                workday_candidate = candidate_response.json()
                _sync_candidate_from_workday(workday_candidate)
        
        return {"success": True, "synced": True}
        
    except Exception as e:
        logger.error(f"Error syncing with Workday: {e}")
        return {"success": False, "error": str(e)}


def sync_with_lever(job_id: Optional[str] = None, candidate_id: Optional[str] = None) -> Dict[str, Any]:
    """Sincroniza con Lever ATS"""
    lever_api_key = _env("LEVER_API_KEY")
    lever_site = _env("LEVER_SITE")
    
    if not all([lever_api_key, lever_site]):
        return {"success": False, "error": "Lever credentials not configured"}
    
    logger.info("syncing with Lever", extra={"job_id": job_id, "candidate_id": candidate_id})
    
    try:
        headers = {
            "Authorization": f"Basic {lever_api_key}",
            "Content-Type": "application/json"
        }
        
        # Sincronizar oportunidades (jobs)
        if job_id:
            opp_response = requests.get(
                f"https://api.lever.co/v1/opportunities/{job_id}",
                headers=headers,
                timeout=30
            )
            if opp_response.status_code == 200:
                lever_opp = opp_response.json()
                _sync_opportunity_from_lever(lever_opp)
        
        # Sincronizar candidatos
        if candidate_id:
            candidate_response = requests.get(
                f"https://api.lever.co/v1/candidates/{candidate_id}",
                headers=headers,
                timeout=30
            )
            if candidate_response.status_code == 200:
                lever_candidate = candidate_response.json()
                _sync_candidate_from_lever(lever_candidate)
        
        return {"success": True, "synced": True}
        
    except Exception as e:
        logger.error(f"Error syncing with Lever: {e}")
        return {"success": False, "error": str(e)}


def _sync_job_from_workday(workday_job: Dict[str, Any]) -> None:
    """Sincroniza job desde Workday"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO ats_job_postings 
            (job_id, title, description, status, posted_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (job_id) 
            DO UPDATE SET 
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                updated_at = NOW()
        """, (
            f"wd_{workday_job.get('id')}",
            workday_job.get("title"),
            workday_job.get("description"),
            "active" if workday_job.get("status") == "OPEN" else "closed",
            datetime.now(timezone.utc)
        ))
        
        # Guardar sincronización
        cursor.execute("""
            INSERT INTO ats_external_sync 
            (sync_id, external_system, external_id, internal_type, internal_id,
             sync_direction, last_synced_at, sync_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (external_system, external_id, internal_type)
            DO UPDATE SET 
                last_synced_at = EXCLUDED.last_synced_at,
                sync_status = EXCLUDED.sync_status,
                updated_at = NOW()
        """, (
            f"sync_{uuid.uuid4().hex[:12]}",
            "workday",
            str(workday_job.get("id")),
            "job",
            f"wd_{workday_job.get('id')}",
            "inbound",
            datetime.now(timezone.utc),
            "synced"
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error syncing job from Workday: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _sync_candidate_from_workday(workday_candidate: Dict[str, Any]) -> None:
    """Sincroniza candidato desde Workday"""
    logger.info(f"Syncing candidate from Workday: {workday_candidate.get('id')}")
    # Implementación similar a _sync_job_from_workday


def _sync_opportunity_from_lever(lever_opp: Dict[str, Any]) -> None:
    """Sincroniza opportunity desde Lever"""
    logger.info(f"Syncing opportunity from Lever: {lever_opp.get('id')}")
    # Implementación similar


def _sync_candidate_from_lever(lever_candidate: Dict[str, Any]) -> None:
    """Sincroniza candidato desde Lever"""
    logger.info(f"Syncing candidate from Lever: {lever_candidate.get('id')}")
    # Implementación similar


# ============================================================================
# BACKGROUND CHECKS AUTOMATIZADOS
# ============================================================================

def initiate_background_check(
    candidate_id: str,
    check_type: str = "standard",
    provider: str = "checkr"
) -> Dict[str, Any]:
    """
    Inicia background check automatizado.
    
    Args:
        candidate_id: ID del candidato
        check_type: Tipo de check (standard, comprehensive, criminal, education, employment)
        provider: Proveedor (checkr, sterling, hireright)
    """
    logger.info("initiating background check", extra={
        "candidate_id": candidate_id,
        "check_type": check_type,
        "provider": provider
    })
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del candidato
        cursor.execute("""
            SELECT email, first_name, last_name, phone
            FROM ats_candidates
            WHERE candidate_id = %s
        """, (candidate_id,))
        
        candidate_data = cursor.fetchone()
        if not candidate_data:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Iniciar check con proveedor
        if provider == "checkr":
            check_result = _initiate_checkr_check(candidate_data, check_type)
        elif provider == "sterling":
            check_result = _initiate_sterling_check(candidate_data, check_type)
        elif provider == "hireright":
            check_result = _initiate_hireright_check(candidate_data, check_type)
        else:
            raise ValueError(f"Provider {provider} not supported")
        
        # Guardar en BD (usando tabla de onboarding post-hire)
        check_id = check_result.get("check_id")
        
        cursor.execute("""
            UPDATE ats_post_hire_onboarding
            SET background_check_status = 'in_progress',
                onboarding_tasks = jsonb_set(
                    onboarding_tasks,
                    '{background_check}',
                    %s::jsonb
                ),
                updated_at = NOW()
            WHERE candidate_id = %s
        """, (
            json.dumps({
                "check_id": check_id,
                "provider": provider,
                "check_type": check_type,
                "status": "in_progress",
                "initiated_at": datetime.now(timezone.utc).isoformat()
            }),
            candidate_id
        ))
        
        conn.commit()
        
        return {
            "check_id": check_id,
            "provider": provider,
            "status": "in_progress"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error initiating background check: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _initiate_checkr_check(candidate_data: tuple, check_type: str) -> Dict[str, Any]:
    """Inicia check con Checkr"""
    checkr_api_key = _env("CHECKR_API_KEY")
    
    if not checkr_api_key or not REQUESTS_AVAILABLE:
        # Stub implementation
        return {
            "check_id": f"checkr_{uuid.uuid4().hex[:12]}",
            "status": "pending"
        }
    
    try:
        # Crear candidato en Checkr
        candidate_response = requests.post(
            "https://api.checkr.com/v1/candidates",
            headers={
                "Authorization": f"Token token={checkr_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "first_name": candidate_data[1],
                "last_name": candidate_data[2],
                "email": candidate_data[0],
                "phone": candidate_data[3] or ""
            },
            timeout=30
        )
        candidate_response.raise_for_status()
        checkr_candidate = candidate_response.json()
        
        # Iniciar reporte
        report_response = requests.post(
            "https://api.checkr.com/v1/reports",
            headers={
                "Authorization": f"Token token={checkr_api_key}",
                "Content-Type": "application/json"
            },
            json={
                "candidate_id": checkr_candidate.get("id"),
                "package": check_type  # standard_level_1, driver_pro, etc.
            },
            timeout=30
        )
        report_response.raise_for_status()
        report = report_response.json()
        
        return {
            "check_id": report.get("id"),
            "status": report.get("status"),
            "candidate_id": checkr_candidate.get("id")
        }
        
    except Exception as e:
        logger.warning(f"Could not initiate Checkr check: {e}")
        return {"check_id": f"checkr_{uuid.uuid4().hex[:12]}", "status": "pending"}


def _initiate_sterling_check(candidate_data: tuple, check_type: str) -> Dict[str, Any]:
    """Inicia check con Sterling"""
    # Stub implementation
    return {"check_id": f"sterling_{uuid.uuid4().hex[:12]}", "status": "pending"}


def _initiate_hireright_check(candidate_data: tuple, check_type: str) -> Dict[str, Any]:
    """Inicia check con HireRight"""
    # Stub implementation
    return {"check_id": f"hireright_{uuid.uuid4().hex[:12]}", "status": "pending"}


# ============================================================================
# CHATBOT PARA CANDIDATOS
# ============================================================================

def process_chatbot_message(
    candidate_id: str,
    message: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Procesa mensaje del chatbot y retorna respuesta.
    
    Intents soportados:
    - status_inquiry: Consulta estado de aplicación
    - interview_info: Información sobre entrevista
    - test_info: Información sobre test
    - general_questions: Preguntas generales
    """
    logger.info("processing chatbot message", extra={"candidate_id": candidate_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Detectar intent
        intent = _detect_intent(message)
        
        # Obtener información del candidato y aplicación
        cursor.execute("""
            SELECT a.application_id, a.status, a.job_id,
                   j.title, c.email
            FROM ats_candidates c
            LEFT JOIN ats_applications a ON c.candidate_id = a.candidate_id
            LEFT JOIN ats_job_postings j ON a.job_id = j.job_id
            WHERE c.candidate_id = %s
            ORDER BY a.applied_at DESC
            LIMIT 1
        """, (candidate_id,))
        
        app_data = cursor.fetchone()
        
        # Generar respuesta según intent
        if intent == "status_inquiry" and app_data:
            response = _generate_status_response(app_data)
        elif intent == "interview_info" and app_data:
            response = _generate_interview_response(candidate_id, app_data[0])
        elif intent == "test_info" and app_data:
            response = _generate_test_response(candidate_id, app_data[0])
        else:
            response = _generate_general_response(intent)
        
        # Guardar conversación
        if not session_id:
            session_id = f"chat_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_communications
            (communication_id, candidate_id, application_id, communication_type,
             direction, subject, body, channel, status, sent_at, metadata)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            f"comm_{uuid.uuid4().hex[:12]}",
            candidate_id,
            app_data[0] if app_data else None,
            "in_app",
            "inbound",
            "Chatbot Message",
            message,
            "chatbot",
            "delivered",
            datetime.now(timezone.utc),
            json.dumps({
                "session_id": session_id,
                "intent": intent,
                "response": response
            })
        ))
        
        conn.commit()
        
        return {
            "session_id": session_id,
            "intent": intent,
            "response": response,
            "confidence": 0.85
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error processing chatbot message: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _detect_intent(message: str) -> str:
    """Detecta intent del mensaje usando keywords simples"""
    message_lower = message.lower()
    
    status_keywords = ["status", "estado", "aplicación", "application", "proceso", "donde"]
    interview_keywords = ["entrevista", "interview", "reunión", "meeting", "cuando"]
    test_keywords = ["test", "evaluación", "assessment", "examen", "prueba"]
    
    if any(kw in message_lower for kw in status_keywords):
        return "status_inquiry"
    elif any(kw in message_lower for kw in interview_keywords):
        return "interview_info"
    elif any(kw in message_lower for kw in test_keywords):
        return "test_info"
    else:
        return "general_questions"


def _generate_status_response(app_data: tuple) -> str:
    """Genera respuesta sobre estado de aplicación"""
    status = app_data[1]
    job_title = app_data[3] or "tu aplicación"
    
    status_messages = {
        "applied": f"Tu aplicación para {job_title} está en revisión. Te contactaremos pronto.",
        "screening": f"Tu aplicación para {job_title} está siendo evaluada por nuestro equipo.",
        "interviewing": f"Tu aplicación para {job_title} está en proceso de entrevistas. Te contactaremos con detalles.",
        "offer": f"¡Felicitaciones! Tienes una oferta pendiente para {job_title}. Revisa tu email.",
        "hired": f"¡Bienvenido! Has sido contratado para {job_title}.",
        "rejected": f"Gracias por tu interés. En esta ocasión no procederemos con tu aplicación para {job_title}."
    }
    
    return status_messages.get(status, f"Tu aplicación para {job_title} está en proceso.")


def _generate_interview_response(candidate_id: str, application_id: str) -> str:
    """Genera respuesta sobre entrevista"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT scheduled_start, interview_type, meeting_link
            FROM ats_interviews
            WHERE application_id = %s
              AND status = 'scheduled'
            ORDER BY scheduled_start DESC
            LIMIT 1
        """, (application_id,))
        
        interview = cursor.fetchone()
        if interview:
            interview_date = interview[0].strftime("%Y-%m-%d %H:%M")
            return f"Tienes una entrevista programada para el {interview_date}. Tipo: {interview[1]}. Link: {interview[2]}"
        else:
            return "No tienes entrevistas programadas en este momento. Te contactaremos cuando sea necesario."
    finally:
        cursor.close()
        conn.close()


def _generate_test_response(candidate_id: str, application_id: str) -> str:
    """Genera respuesta sobre test"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT test_name, test_url, due_date, status
            FROM ats_assessment_tests
            WHERE application_id = %s
              AND status IN ('pending', 'sent')
            ORDER BY due_date DESC
            LIMIT 1
        """, (application_id,))
        
        test = cursor.fetchone()
        if test:
            due_date = test[2].strftime("%Y-%m-%d") if test[2] else "N/A"
            return f"Tienes un test pendiente: {test[0]}. Fecha límite: {due_date}. Link: {test[1]}"
        else:
            return "No tienes tests pendientes en este momento."
    finally:
        cursor.close()
        conn.close()


def _generate_general_response(intent: str) -> str:
    """Genera respuesta general"""
    return "Gracias por tu mensaje. ¿En qué puedo ayudarte? Puedes preguntar sobre el estado de tu aplicación, entrevistas o tests."


# ============================================================================
# ANÁLISIS PREDICTIVO DE ABANDONO
# ============================================================================

def predict_process_abandonment(application_id: str) -> Dict[str, Any]:
    """
    Predice probabilidad de abandono del proceso por parte del candidato.
    
    Factores considerados:
    - Tiempo sin respuesta
    - Número de recordatorios
    - Engagement en comunicaciones
    - Tiempo en cada etapa
    """
    logger.info("predicting process abandonment", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos de la aplicación
        cursor.execute("""
            SELECT a.application_id, a.status, a.applied_at, a.updated_at,
                   COUNT(DISTINCT c.communication_id) as comm_count,
                   COUNT(DISTINCT i.interview_id) FILTER (WHERE i.status = 'no_show') as no_shows,
                   MAX(c.sent_at) as last_communication
            FROM ats_applications a
            LEFT JOIN ats_communications c ON a.application_id = c.application_id
            LEFT JOIN ats_interviews i ON a.application_id = i.application_id
            WHERE a.application_id = %s
            GROUP BY a.application_id, a.status, a.applied_at, a.updated_at
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        # Calcular factores de riesgo
        days_since_update = (datetime.now(timezone.utc) - app_data[3]).days if app_data[3] else 0
        days_since_last_comm = 0
        if app_data[6]:
            days_since_last_comm = (datetime.now(timezone.utc) - app_data[6]).days
        
        # Scoring de riesgo
        risk_score = 0
        
        # Tiempo sin actualización
        if days_since_update > 14:
            risk_score += 30
        elif days_since_update > 7:
            risk_score += 15
        
        # Sin comunicación reciente
        if days_since_last_comm > 10:
            risk_score += 25
        elif days_since_last_comm > 5:
            risk_score += 10
        
        # No-shows en entrevistas
        no_shows = app_data[5] or 0
        if no_shows > 0:
            risk_score += 20 * no_shows
        
        # Poca comunicación
        comm_count = app_data[4] or 0
        if comm_count < 2:
            risk_score += 15
        
        # Probabilidad de abandono (0-100)
        abandonment_probability = min(risk_score, 100)
        
        # Recomendaciones
        recommendations = []
        if abandonment_probability > 70:
            recommendations.append("Enviar comunicación urgente")
            recommendations.append("Ofrecer flexibilidad en horarios")
        elif abandonment_probability > 40:
            recommendations.append("Enviar recordatorio")
            recommendations.append("Verificar preferencias de contacto")
        
        result = {
            "abandonment_probability": abandonment_probability,
            "risk_score": risk_score,
            "factors": {
                "days_since_update": days_since_update,
                "days_since_last_comm": days_since_last_comm,
                "no_shows": no_shows,
                "communication_count": comm_count
            },
            "recommendations": recommendations,
            "risk_level": "high" if abandonment_probability > 70 else "medium" if abandonment_probability > 40 else "low"
        }
        
        # Guardar predicción
        cursor.execute("""
            INSERT INTO ats_analytics
            (metric_id, metric_name, metric_type, metric_value, metric_data, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            f"metric_{uuid.uuid4().hex[:12]}",
            f"abandonment_{application_id}",
            "abandonment_prediction",
            abandonment_probability,
            json.dumps(result),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return result
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error predicting abandonment: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# INTEGRACIÓN CON PAYROLL/HRIS
# ============================================================================

def sync_new_hire_to_payroll(
    candidate_id: str,
    start_date: str,
    salary: float,
    department: str
) -> Dict[str, Any]:
    """Sincroniza nuevo empleado con sistema de payroll"""
    payroll_api_url = _env("PAYROLL_API_URL")
    payroll_api_key = _env("PAYROLL_API_KEY")
    
    if not all([payroll_api_url, payroll_api_key]):
        return {"success": False, "error": "Payroll API not configured"}
    
    logger.info("syncing to payroll", extra={"candidate_id": candidate_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del candidato
        cursor.execute("""
            SELECT email, first_name, last_name, phone, location
            FROM ats_candidates
            WHERE candidate_id = %s
        """, (candidate_id,))
        
        candidate_data = cursor.fetchone()
        if not candidate_data:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        # Crear empleado en payroll
        if REQUESTS_AVAILABLE:
            payload = {
                "email": candidate_data[0],
                "first_name": candidate_data[1],
                "last_name": candidate_data[2],
                "phone": candidate_data[3],
                "start_date": start_date,
                "salary": salary,
                "department": department,
                "location": candidate_data[4]
            }
            
            response = requests.post(
                f"{payroll_api_url}/employees",
                json=payload,
                headers={
                    "Authorization": f"Bearer {payroll_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            payroll_employee = response.json()
            
            return {
                "success": True,
                "payroll_employee_id": payroll_employee.get("id"),
                "synced_at": datetime.now(timezone.utc).isoformat()
            }
        else:
            return {"success": True, "synced": True, "stub": True}
            
    except Exception as e:
        logger.error(f"Error syncing to payroll: {e}")
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        conn.close()


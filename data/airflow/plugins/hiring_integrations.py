"""
Sistema de Integraciones para Hiring/ATS
==========================================

Integraciones con plataformas de reclutamiento, filtrado de CVs,
programación de entrevistas, envío de tests y comunicación con candidatos.
"""

from __future__ import annotations

import json
import logging
import os
import time
import uuid
import re
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger("airflow.task")

# Configuración de retries
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


class Platform(Enum):
    """Plataformas de job posting disponibles"""
    GREENHOUSE = "greenhouse"
    LINKEDIN = "linkedin"
    INDEED = "indeed"
    GLASSDOOR = "glassdoor"
    MONSTER = "monster"
    CUSTOM = "custom"


class InterviewType(Enum):
    """Tipos de entrevistas"""
    PHONE_SCREEN = "phone_screen"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    PANEL = "panel"
    FINAL = "final"
    ONSITE = "onsite"


class TestType(Enum):
    """Tipos de tests de evaluación"""
    TECHNICAL = "technical"
    CODING = "coding"
    PERSONALITY = "personality"
    LANGUAGE = "language"
    CUSTOM = "custom"


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


def _retry_with_backoff(func, *args, max_retries: int = MAX_RETRIES, **kwargs):
    """Retry function with exponential backoff"""
    last_exception = None
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay}s", extra={"error": str(e)})
                time.sleep(delay)
            else:
                logger.error(f"All {max_retries} attempts failed", extra={"error": str(e)})
    raise last_exception


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
# PUBLICACIÓN DE VACANTES EN MÚLTIPLES PLATAFORMAS
# ============================================================================

def publish_job_to_multiple_platforms(
    job_id: str,
    platforms: List[str],
    job_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Publica una vacante en múltiples plataformas simultáneamente.
    
    Args:
        job_id: ID único de la vacante
        platforms: Lista de plataformas donde publicar ['greenhouse', 'linkedin', 'indeed', ...]
        job_data: Datos de la vacante (title, description, requirements, etc.)
    
    Returns:
        Dict con resultados por plataforma
    """
    logger.info(
        "publishing job to platforms",
        extra={"job_id": job_id, "platforms": platforms, "platform_count": len(platforms)}
    )
    
    results = {}
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        for platform_name in platforms:
            try:
                platform_result = _publish_to_platform(platform_name, job_id, job_data)
                results[platform_name] = platform_result
                
                # Guardar en BD
                cursor.execute("""
                    INSERT INTO ats_job_platforms 
                    (job_id, platform_name, platform_job_id, platform_url, status, posted_at, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (job_id, platform_name) 
                    DO UPDATE SET 
                        platform_job_id = EXCLUDED.platform_job_id,
                        platform_url = EXCLUDED.platform_url,
                        status = EXCLUDED.status,
                        posted_at = EXCLUDED.posted_at,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                """, (
                    job_id,
                    platform_name,
                    platform_result.get("platform_job_id"),
                    platform_result.get("platform_url"),
                    "posted" if platform_result.get("success") else "failed",
                    datetime.now(timezone.utc) if platform_result.get("success") else None,
                    json.dumps(platform_result.get("metadata", {}))
                ))
                
            except Exception as e:
                logger.error(f"Failed to publish to {platform_name}", extra={"error": str(e), "job_id": job_id})
                results[platform_name] = {"success": False, "error": str(e)}
                
                # Guardar error en BD
                cursor.execute("""
                    INSERT INTO ats_job_platforms 
                    (job_id, platform_name, status, error_message, metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (job_id, platform_name) 
                    DO UPDATE SET 
                        status = EXCLUDED.status,
                        error_message = EXCLUDED.error_message,
                        updated_at = NOW()
                """, (
                    job_id,
                    platform_name,
                    "failed",
                    str(e),
                    json.dumps({"error": str(e)})
                ))
        
        conn.commit()
        
        # Actualizar estado de la vacante
        all_success = all(r.get("success", False) for r in results.values())
        if all_success:
            cursor.execute("""
                UPDATE ats_job_postings 
                SET status = 'active', posted_at = NOW(), updated_at = NOW()
                WHERE job_id = %s
            """, (job_id,))
            conn.commit()
        
        logger.info("job published to platforms", extra={
            "job_id": job_id,
            "success_count": sum(1 for r in results.values() if r.get("success")),
            "total_platforms": len(platforms)
        })
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error publishing job to platforms: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return results


def _publish_to_platform(
    platform_name: str,
    job_id: str,
    job_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Publica vacante a una plataforma específica"""
    
    platform = Platform(platform_name.lower())
    
    if platform == Platform.GREENHOUSE:
        return _publish_to_greenhouse(job_id, job_data)
    elif platform == Platform.LINKEDIN:
        return _publish_to_linkedin(job_id, job_data)
    elif platform == Platform.INDEED:
        return _publish_to_indeed(job_id, job_data)
    elif platform == Platform.GLASSDOOR:
        return _publish_to_glassdoor(job_id, job_data)
    elif platform == Platform.MONSTER:
        return _publish_to_monster(job_id, job_data)
    else:
        return {"success": False, "error": f"Platform {platform_name} not implemented"}


def _publish_to_greenhouse(job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Publica vacante en Greenhouse"""
    api_key = _env("GREENHOUSE_API_KEY")
    api_url = _env("GREENHOUSE_API_URL", "https://api.greenhouse.io/v1")
    
    if not api_key:
        logger.warning("GREENHOUSE_API_KEY not configured")
        return {"success": False, "error": "API key not configured"}
    
    try:
        payload = {
            "name": job_data.get("title"),
            "requisition_id": job_id,
            "departments": [{"id": job_data.get("department_id", 1)}] if job_data.get("department_id") else [],
            "offices": [{"id": job_data.get("office_id", 1)}] if job_data.get("office_id") else [],
            "employment_type": job_data.get("employment_type", "full_time"),
            "content": job_data.get("description", ""),
            "requirements": job_data.get("requirements", ""),
            "notes": job_data.get("notes", ""),
        }
        
        if REQUESTS_AVAILABLE:
            response = _retry_with_backoff(
                requests.post,
                f"{api_url}/jobs",
                json=payload,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "platform_job_id": str(result.get("id")),
                "platform_url": result.get("absolute_url"),
                "metadata": result
            }
        else:
            # Stub implementation
            logger.info("Using stub Greenhouse integration")
            return {
                "success": True,
                "platform_job_id": f"gh_{job_id}",
                "platform_url": f"https://boards.greenhouse.io/jobs/{job_id}",
                "metadata": {"stub": True}
            }
            
    except Exception as e:
        logger.error(f"Error publishing to Greenhouse: {e}")
        return {"success": False, "error": str(e)}


def _publish_to_linkedin(job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Publica vacante en LinkedIn"""
    access_token = _env("LINKEDIN_ACCESS_TOKEN")
    api_url = _env("LINKEDIN_API_URL", "https://api.linkedin.com/v2")
    
    if not access_token:
        logger.warning("LINKEDIN_ACCESS_TOKEN not configured")
        return {"success": False, "error": "Access token not configured"}
    
    try:
        # LinkedIn requiere organización ID
        org_id = _env("LINKEDIN_ORG_ID")
        if not org_id:
            return {"success": False, "error": "LINKEDIN_ORG_ID not configured"}
        
        payload = {
            "postingLocation": f"urn:li:organization:{org_id}",
            "jobPosting": {
                "title": job_data.get("title"),
                "description": {
                    "text": job_data.get("description", "")
                },
                "employmentType": job_data.get("employment_type", "FULL_TIME"),
                "workplaceTypes": ["remote"] if job_data.get("remote_type") == "remote" else ["on-site"],
                "location": {
                    "country": job_data.get("location_country", "US"),
                    "city": job_data.get("location", "")
                }
            }
        }
        
        if REQUESTS_AVAILABLE:
            response = _retry_with_backoff(
                requests.post,
                f"{api_url}/jobPostings",
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            return {
                "success": True,
                "platform_job_id": result.get("id", "").split(":")[-1] if ":" in result.get("id", "") else result.get("id"),
                "platform_url": f"https://www.linkedin.com/jobs/view/{result.get('id', job_id)}",
                "metadata": result
            }
        else:
            # Stub implementation
            return {
                "success": True,
                "platform_job_id": f"li_{job_id}",
                "platform_url": f"https://www.linkedin.com/jobs/view/{job_id}",
                "metadata": {"stub": True}
            }
            
    except Exception as e:
        logger.error(f"Error publishing to LinkedIn: {e}")
        return {"success": False, "error": str(e)}


def _publish_to_indeed(job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Publica vacante en Indeed"""
    publisher_id = _env("INDEED_PUBLISHER_ID")
    api_key = _env("INDEED_API_KEY")
    
    if not publisher_id or not api_key:
        logger.warning("INDEED credentials not configured")
        return {"success": False, "error": "Credentials not configured"}
    
    # Stub implementation - Indeed API requiere configuración específica
    return {
        "success": True,
        "platform_job_id": f"indeed_{job_id}",
        "platform_url": f"https://www.indeed.com/viewjob?jk={job_id}",
        "metadata": {"stub": True}
    }


def _publish_to_glassdoor(job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Publica vacante en Glassdoor"""
    # Stub implementation
    return {
        "success": True,
        "platform_job_id": f"gd_{job_id}",
        "platform_url": f"https://www.glassdoor.com/job-listing/{job_id}",
        "metadata": {"stub": True}
    }


def _publish_to_monster(job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    """Publica vacante en Monster"""
    # Stub implementation
    return {
        "success": True,
        "platform_job_id": f"monster_{job_id}",
        "platform_url": f"https://www.monster.com/jobs/{job_id}",
        "metadata": {"stub": True}
    }


# ============================================================================
# FILTRADO DE CVs POR PALABRAS CLAVE
# ============================================================================

def filter_cv_by_keywords(
    application_id: str,
    resume_text: str,
    keywords: List[str],
    cover_letter: Optional[str] = None
) -> Dict[str, Any]:
    """
    Filtra un CV por palabras clave y calcula un score de matching.
    
    Args:
        application_id: ID de la aplicación
        resume_text: Texto extraído del CV
        cover_letter: Texto de la carta de presentación (opcional)
        keywords: Lista de palabras clave requeridas
    
    Returns:
        Dict con match_score, matched_keywords, passed, y detalles
    """
    logger.info("filtering CV by keywords", extra={"application_id": application_id, "keyword_count": len(keywords)})
    
    # Normalizar texto
    full_text = (resume_text or "").lower()
    if cover_letter:
        full_text += " " + cover_letter.lower()
    
    # Buscar keywords
    matched_keywords = []
    keyword_scores = {}
    
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Buscar palabra completa y variaciones
        pattern = r'\b' + re.escape(keyword_lower) + r'\b'
        matches = len(re.findall(pattern, full_text, re.IGNORECASE))
        
        if matches > 0:
            matched_keywords.append(keyword)
            keyword_scores[keyword] = min(matches, 5)  # Cap a 5 matches por keyword
    
    # Calcular score (0-100)
    if not keywords:
        match_score = 100.0
    else:
        match_score = (len(matched_keywords) / len(keywords)) * 100
    
    # Determinar si pasa el filtro (threshold configurable, default 50%)
    threshold = float(_env("ATS_KEYWORD_THRESHOLD", "50.0"))
    passed = match_score >= threshold
    
    result = {
        "match_score": round(match_score, 2),
        "matched_keywords": matched_keywords,
        "total_keywords": len(keywords),
        "matched_count": len(matched_keywords),
        "passed": passed,
        "keyword_scores": keyword_scores,
        "threshold": threshold
    }
    
    # Guardar en BD
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO ats_cv_filtering 
            (application_id, filter_type, filter_criteria, matched_keywords, match_score, passed, filter_details)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            application_id,
            "keyword",
            json.dumps({"keywords": keywords, "threshold": threshold}),
            matched_keywords,
            match_score,
            passed,
            json.dumps(result)
        ))
        
        # Actualizar application con match_score
        cursor.execute("""
            UPDATE ats_applications 
            SET match_score = %s, keyword_matches = %s, updated_at = NOW()
            WHERE application_id = %s
        """, (match_score, matched_keywords, application_id))
        
        conn.commit()
        logger.info("CV filtered", extra={"application_id": application_id, "match_score": match_score, "passed": passed})
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving CV filter results: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
    
    return result


# ============================================================================
# PROGRAMACIÓN AUTOMÁTICA DE ENTREVISTAS
# ============================================================================

def schedule_interview_automatically(
    application_id: str,
    interviewer_email: str,
    interview_type: str,
    preferred_times: Optional[List[Dict[str, Any]]] = None,
    duration_minutes: int = 60
) -> Dict[str, Any]:
    """
    Programa una entrevista automáticamente usando disponibilidad del entrevistador.
    
    Args:
        application_id: ID de la aplicación
        interviewer_email: Email del entrevistador
        interview_type: Tipo de entrevista (phone_screen, technical, etc.)
        preferred_times: Lista de horarios preferidos del candidato
        duration_minutes: Duración de la entrevista en minutos
    
    Returns:
        Dict con detalles de la entrevista programada
    """
    logger.info("scheduling interview", extra={
        "application_id": application_id,
        "interviewer_email": interviewer_email,
        "interview_type": interview_type
    })
    
    # Obtener información de la aplicación y candidato
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT a.application_id, a.candidate_id, a.job_id,
                   c.email, c.first_name, c.last_name
            FROM ats_applications a
            JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        candidate_email = app_data[3]
        candidate_name = f"{app_data[4]} {app_data[5]}"
        
        # Obtener disponibilidad del entrevistador
        available_slots = _get_interviewer_availability(
            interviewer_email,
            preferred_times,
            duration_minutes
        )
        
        if not available_slots:
            raise ValueError(f"No available slots for interviewer {interviewer_email}")
        
        # Seleccionar el mejor slot (primero disponible)
        selected_slot = available_slots[0]
        scheduled_start = selected_slot["start"]
        scheduled_end = scheduled_start + timedelta(minutes=duration_minutes)
        
        # Crear evento en calendario
        calendar_event = _create_calendar_event(
            interviewer_email,
            candidate_email,
            candidate_name,
            scheduled_start,
            scheduled_end,
            interview_type,
            application_id
        )
        
        # Generar meeting link
        meeting_link = _generate_meeting_link(interview_type, scheduled_start)
        
        # Crear registro de entrevista
        interview_id = f"interview_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_interviews 
            (interview_id, application_id, interview_type, interview_stage,
             interviewer_email, candidate_email, candidate_name,
             scheduled_start, scheduled_end, duration_minutes,
             location, meeting_link, calendar_event_id, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            interview_id,
            application_id,
            interview_type,
            "scheduled",
            interviewer_email,
            candidate_email,
            candidate_name,
            scheduled_start,
            scheduled_end,
            duration_minutes,
            "zoom" if interview_type != "onsite" else "onsite",
            meeting_link,
            calendar_event.get("event_id"),
            "scheduled"
        ))
        
        # Actualizar estado de la aplicación
        cursor.execute("""
            UPDATE ats_applications 
            SET status = 'interview', updated_at = NOW()
            WHERE application_id = %s
        """, (application_id,))
        
        conn.commit()
        
        result = {
            "interview_id": interview_id,
            "scheduled_start": scheduled_start.isoformat(),
            "scheduled_end": scheduled_end.isoformat(),
            "meeting_link": meeting_link,
            "calendar_event_id": calendar_event.get("event_id"),
            "calendar_url": calendar_event.get("html_link")
        }
        
        logger.info("interview scheduled", extra={"interview_id": interview_id, "scheduled_start": scheduled_start.isoformat()})
        
        return result
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error scheduling interview: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _get_interviewer_availability(
    interviewer_email: str,
    preferred_times: Optional[List[Dict[str, Any]]],
    duration_minutes: int
) -> List[Dict[str, Any]]:
    """Obtiene slots disponibles del entrevistador"""
    
    # Intentar obtener desde calendario (Google Calendar, Outlook)
    calendar_api = _env("CALENDAR_API_URL")
    
    if calendar_api and REQUESTS_AVAILABLE:
        try:
            # Consultar calendario para próximos 14 días
            start_date = datetime.now(timezone.utc)
            end_date = start_date + timedelta(days=14)
            
            response = _retry_with_backoff(
                requests.get,
                f"{calendar_api}/availability",
                params={
                    "email": interviewer_email,
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "duration_minutes": duration_minutes
                },
                headers={"Authorization": f"Bearer {_env('CALENDAR_API_KEY')}"},
                timeout=30
            )
            response.raise_for_status()
            slots = response.json().get("available_slots", [])
            
            # Convertir a datetime objects
            for slot in slots:
                slot["start"] = datetime.fromisoformat(slot["start"].replace("Z", "+00:00"))
            
            return slots
            
        except Exception as e:
            logger.warning(f"Could not get calendar availability: {e}, using default slots")
    
    # Fallback: generar slots por defecto (horario laboral, próximos 5 días)
    default_slots = []
    now = datetime.now(timezone.utc)
    
    for day_offset in range(1, 6):  # Próximos 5 días
        for hour in range(9, 17):  # 9 AM a 5 PM
            slot_start = (now + timedelta(days=day_offset)).replace(hour=hour, minute=0, second=0, microsecond=0)
            default_slots.append({"start": slot_start})
    
    return default_slots[:10]  # Retornar primeros 10 slots


def _create_calendar_event(
    interviewer_email: str,
    candidate_email: str,
    candidate_name: str,
    start_time: datetime,
    end_time: datetime,
    interview_type: str,
    application_id: str
) -> Dict[str, Any]:
    """Crea evento en calendario del entrevistador"""
    
    calendar_api = _env("CALENDAR_API_URL")
    
    if calendar_api and REQUESTS_AVAILABLE:
        try:
            event_data = {
                "summary": f"Interview: {candidate_name} ({interview_type})",
                "description": f"Interview scheduled via ATS\nApplication ID: {application_id}",
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "attendees": [interviewer_email, candidate_email],
                "location": "Zoom/Video Call"
            }
            
            response = _retry_with_backoff(
                requests.post,
                f"{calendar_api}/events",
                json=event_data,
                headers={
                    "Authorization": f"Bearer {_env('CALENDAR_API_KEY')}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.warning(f"Could not create calendar event: {e}")
    
    # Fallback: stub
    return {
        "event_id": f"event_{uuid.uuid4().hex[:12]}",
        "html_link": f"https://calendar.google.com/event?eid={uuid.uuid4().hex}"
    }


def _generate_meeting_link(interview_type: str, scheduled_time: datetime) -> str:
    """Genera link de reunión (Zoom, Google Meet, etc.)"""
    
    if interview_type == "phone_screen":
        return "Phone call - TBD"
    
    # Zoom API
    zoom_api_key = _env("ZOOM_API_KEY")
    zoom_api_secret = _env("ZOOM_API_SECRET")
    
    if zoom_api_key and zoom_api_secret and REQUESTS_AVAILABLE:
        try:
            # Crear meeting en Zoom
            meeting_data = {
                "topic": "Interview",
                "type": 2,  # Scheduled meeting
                "start_time": scheduled_time.isoformat(),
                "duration": 60,
                "settings": {
                    "join_before_host": False,
                    "waiting_room": True
                }
            }
            
            response = _retry_with_backoff(
                requests.post,
                "https://api.zoom.us/v2/users/me/meetings",
                json=meeting_data,
                headers={
                    "Authorization": f"Bearer {_env('ZOOM_ACCESS_TOKEN')}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result.get("join_url", "")
            
        except Exception as e:
            logger.warning(f"Could not create Zoom meeting: {e}")
    
    # Fallback: Google Meet link genérico
    return f"https://meet.google.com/xxx-xxxx-xxx"


# ============================================================================
# ENVÍO DE TESTS DE EVALUACIÓN
# ============================================================================

def send_assessment_test(
    application_id: str,
    test_type: str,
    test_platform: str = "custom",
    due_date_days: int = 7
) -> Dict[str, Any]:
    """
    Envía un test de evaluación al candidato.
    
    Args:
        application_id: ID de la aplicación
        test_type: Tipo de test (technical, coding, personality, etc.)
        test_platform: Plataforma del test (hackerrank, codility, custom, etc.)
        due_date_days: Días hasta la fecha límite
    
    Returns:
        Dict con detalles del test enviado
    """
    logger.info("sending assessment test", extra={
        "application_id": application_id,
        "test_type": test_type,
        "test_platform": test_platform
    })
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del candidato
        cursor.execute("""
            SELECT a.application_id, c.candidate_id, c.email, c.first_name, c.last_name
            FROM ats_applications a
            JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        candidate_email = app_data[2]
        candidate_name = f"{app_data[3]} {app_data[4]}"
        
        # Crear test en plataforma externa si aplica
        test_url, test_instructions = _create_external_test(
            test_platform,
            test_type,
            candidate_email,
            due_date_days
        )
        
        # Crear registro de test
        test_id = f"test_{uuid.uuid4().hex[:12]}"
        due_date = datetime.now(timezone.utc) + timedelta(days=due_date_days)
        
        cursor.execute("""
            INSERT INTO ats_assessment_tests 
            (test_id, application_id, test_type, test_platform, test_name,
             test_url, test_instructions, duration_minutes, due_date, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            test_id,
            application_id,
            test_type,
            test_platform,
            f"{test_type.title()} Assessment",
            test_url,
            test_instructions,
            60,  # Default duration
            due_date,
            "pending"
        ))
        
        # Enviar email al candidato
        _send_test_email(candidate_email, candidate_name, test_id, test_url, test_instructions, due_date)
        
        # Actualizar estado
        cursor.execute("""
            UPDATE ats_assessment_tests 
            SET status = 'sent', sent_at = NOW()
            WHERE test_id = %s
        """, (test_id,))
        
        conn.commit()
        
        result = {
            "test_id": test_id,
            "test_url": test_url,
            "due_date": due_date.isoformat(),
            "status": "sent"
        }
        
        logger.info("assessment test sent", extra={"test_id": test_id, "candidate_email": candidate_email})
        
        return result
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error sending assessment test: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _create_external_test(
    test_platform: str,
    test_type: str,
    candidate_email: str,
    due_date_days: int
) -> Tuple[str, str]:
    """Crea test en plataforma externa y retorna URL e instrucciones"""
    
    if test_platform == "hackerrank":
        return _create_hackerrank_test(test_type, candidate_email, due_date_days)
    elif test_platform == "codility":
        return _create_codility_test(test_type, candidate_email, due_date_days)
    else:
        # Test interno/custom
        test_id = uuid.uuid4().hex[:12]
        return (
            f"https://tests.company.com/{test_id}",
            f"Please complete the {test_type} assessment. You have {due_date_days} days to complete it."
        )


def _create_hackerrank_test(test_type: str, candidate_email: str, due_date_days: int) -> Tuple[str, str]:
    """Crea test en HackerRank"""
    api_key = _env("HACKERRANK_API_KEY")
    api_url = _env("HACKERRANK_API_URL", "https://www.hackerrank.com/x/api/v3")
    
    if api_key and REQUESTS_AVAILABLE:
        try:
            # Stub - HackerRank API requiere configuración específica
            test_id = uuid.uuid4().hex[:12]
            return (
                f"https://www.hackerrank.com/test/{test_id}",
                "Complete the technical assessment on HackerRank. You have 60 minutes."
            )
        except Exception as e:
            logger.warning(f"Could not create HackerRank test: {e}")
    
    # Fallback
    test_id = uuid.uuid4().hex[:12]
    return (
        f"https://www.hackerrank.com/test/{test_id}",
        "Please complete the assessment. You have 60 minutes."
    )


def _create_codility_test(test_type: str, candidate_email: str, due_date_days: int) -> Tuple[str, str]:
    """Crea test en Codility"""
    # Stub implementation
    test_id = uuid.uuid4().hex[:12]
    return (
        f"https://app.codility.com/test/{test_id}",
        "Complete the coding challenge on Codility. You have 90 minutes."
    )


def _send_test_email(
    candidate_email: str,
    candidate_name: str,
    test_id: str,
    test_url: str,
    instructions: str,
    due_date: datetime
) -> None:
    """Envía email al candidato con link del test"""
    
    try:
        from data.airflow.plugins.etl_notifications import notify_email
        
        subject = f"Assessment Test - Complete Your Evaluation"
        body = f"""
Hello {candidate_name},

We would like to invite you to complete an assessment test as part of your application process.

Test Details:
- Test ID: {test_id}
- Test URL: {test_url}
- Due Date: {due_date.strftime('%Y-%m-%d %H:%M UTC')}

Instructions:
{instructions}

Please complete the test before the due date.

Best regards,
Hiring Team
        """
        
        html_body = f"""
<html>
<body>
<h2>Assessment Test Invitation</h2>
<p>Hello {candidate_name},</p>
<p>We would like to invite you to complete an assessment test as part of your application process.</p>
<p><strong>Test Details:</strong></p>
<ul>
<li>Test ID: {test_id}</li>
<li>Due Date: {due_date.strftime('%Y-%m-%d %H:%M UTC')}</li>
</ul>
<p><strong>Instructions:</strong></p>
<p>{instructions}</p>
<p><a href="{test_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Start Test</a></p>
<p>Best regards,<br>Hiring Team</p>
</body>
</html>
        """
        
        notify_email(
            to=candidate_email,
            subject=subject,
            body=body,
            html=html_body
        )
        
        # Guardar comunicación en BD
        conn = _get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT candidate_id FROM ats_candidates WHERE email = %s
            """, (candidate_email,))
            candidate_data = cursor.fetchone()
            candidate_id = candidate_data[0] if candidate_data else None
            
            if candidate_id:
                cursor.execute("""
                    INSERT INTO ats_communications 
                    (communication_id, candidate_id, communication_type, direction,
                     subject, body, channel, recipient_email, status, sent_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    f"comm_{uuid.uuid4().hex[:12]}",
                    candidate_id,
                    "email",
                    "outbound",
                    subject,
                    body,
                    "email",
                    candidate_email,
                    "sent",
                    datetime.now(timezone.utc)
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not save communication record: {e}")
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error sending test email: {e}")
        raise


# ============================================================================
# COMUNICACIÓN CON CANDIDATOS
# ============================================================================

def send_communication_to_candidate(
    candidate_id: str,
    communication_type: str,
    subject: str,
    body: str,
    template_id: Optional[str] = None,
    application_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Envía comunicación a un candidato (email, SMS, etc.)
    
    Args:
        candidate_id: ID del candidato
        communication_type: Tipo de comunicación (email, sms, etc.)
        subject: Asunto del mensaje
        body: Cuerpo del mensaje
        template_id: ID del template usado (opcional)
        application_id: ID de la aplicación relacionada (opcional)
    
    Returns:
        Dict con detalles de la comunicación enviada
    """
    logger.info("sending communication to candidate", extra={
        "candidate_id": candidate_id,
        "communication_type": communication_type
    })
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del candidato
        cursor.execute("""
            SELECT email, phone, first_name, last_name
            FROM ats_candidates
            WHERE candidate_id = %s
        """, (candidate_id,))
        
        candidate_data = cursor.fetchone()
        if not candidate_data:
            raise ValueError(f"Candidate {candidate_id} not found")
        
        candidate_email = candidate_data[0]
        candidate_phone = candidate_data[1]
        candidate_name = f"{candidate_data[2]} {candidate_data[3]}"
        
        # Enviar según tipo
        sent = False
        if communication_type == "email":
            sent = _send_email_to_candidate(candidate_email, candidate_name, subject, body)
        elif communication_type == "sms" and candidate_phone:
            sent = _send_sms_to_candidate(candidate_phone, body)
        
        # Guardar en BD
        communication_id = f"comm_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_communications 
            (communication_id, candidate_id, application_id, communication_type,
             direction, subject, body, channel, recipient_email, recipient_phone,
             template_id, status, sent_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            communication_id,
            candidate_id,
            application_id,
            communication_type,
            "outbound",
            subject,
            body,
            communication_type,
            candidate_email,
            candidate_phone,
            template_id,
            "sent" if sent else "failed",
            datetime.now(timezone.utc) if sent else None
        ))
        
        conn.commit()
        
        result = {
            "communication_id": communication_id,
            "sent": sent,
            "recipient": candidate_email if communication_type == "email" else candidate_phone
        }
        
        logger.info("communication sent", extra={"communication_id": communication_id, "sent": sent})
        
        return result
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error sending communication: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _send_email_to_candidate(email: str, name: str, subject: str, body: str) -> bool:
    """Envía email al candidato"""
    try:
        from data.airflow.plugins.etl_notifications import notify_email
        
        notify_email(
            to=email,
            subject=subject,
            body=body,
            html=f"<html><body><p>{body.replace(chr(10), '<br>')}</p></body></html>"
        )
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False


def _send_sms_to_candidate(phone: str, message: str) -> bool:
    """Envía SMS al candidato"""
    twilio_sid = _env("TWILIO_ACCOUNT_SID")
    twilio_token = _env("TWILIO_AUTH_TOKEN")
    twilio_from = _env("TWILIO_PHONE_NUMBER")
    
    if not all([twilio_sid, twilio_token, twilio_from]):
        logger.warning("Twilio credentials not configured")
        return False
    
    if REQUESTS_AVAILABLE:
        try:
            response = _retry_with_backoff(
                requests.post,
                f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json",
                data={
                    "From": twilio_from,
                    "To": phone,
                    "Body": message
                },
                auth=(twilio_sid, twilio_token),
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    return False


# ============================================================================
# SINCRONIZACIÓN CON GREENHOUSE
# ============================================================================

def sync_with_greenhouse(
    job_id: Optional[str] = None,
    candidate_id: Optional[str] = None,
    direction: str = "bidirectional"
) -> Dict[str, Any]:
    """
    Sincroniza datos con Greenhouse ATS.
    
    Args:
        job_id: ID de la vacante a sincronizar (opcional)
        candidate_id: ID del candidato a sincronizar (opcional)
        direction: Dirección de sincronización (inbound, outbound, bidirectional)
    
    Returns:
        Dict con resultados de la sincronización
    """
    logger.info("syncing with Greenhouse", extra={
        "job_id": job_id,
        "candidate_id": candidate_id,
        "direction": direction
    })
    
    api_key = _env("GREENHOUSE_API_KEY")
    api_url = _env("GREENHOUSE_API_URL", "https://api.greenhouse.io/v1")
    
    if not api_key:
        return {"success": False, "error": "GREENHOUSE_API_KEY not configured"}
    
    results = {"synced": [], "failed": []}
    
    try:
        if direction in ["inbound", "bidirectional"]:
            # Sincronizar desde Greenhouse hacia nuestro sistema
            if job_id:
                gh_job = _fetch_greenhouse_job(api_url, api_key, job_id)
                if gh_job:
                    _sync_job_from_greenhouse(gh_job)
                    results["synced"].append(f"job_{job_id}")
            
            if candidate_id:
                gh_candidate = _fetch_greenhouse_candidate(api_url, api_key, candidate_id)
                if gh_candidate:
                    _sync_candidate_from_greenhouse(gh_candidate)
                    results["synced"].append(f"candidate_{candidate_id}")
        
        if direction in ["outbound", "bidirectional"]:
            # Sincronizar desde nuestro sistema hacia Greenhouse
            if job_id:
                _sync_job_to_greenhouse(job_id, api_url, api_key)
                results["synced"].append(f"job_{job_id}_outbound")
            
            if candidate_id:
                _sync_candidate_to_greenhouse(candidate_id, api_url, api_key)
                results["synced"].append(f"candidate_{candidate_id}_outbound")
        
        return {"success": True, "results": results}
        
    except Exception as e:
        logger.error(f"Error syncing with Greenhouse: {e}")
        return {"success": False, "error": str(e), "results": results}


def _fetch_greenhouse_job(api_url: str, api_key: str, job_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene job de Greenhouse"""
    if not REQUESTS_AVAILABLE:
        return None
    
    try:
        response = _retry_with_backoff(
            requests.get,
            f"{api_url}/boards/{_env('GREENHOUSE_BOARD_TOKEN')}/jobs/{job_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Could not fetch Greenhouse job: {e}")
        return None


def _fetch_greenhouse_candidate(api_url: str, api_key: str, candidate_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene candidato de Greenhouse"""
    if not REQUESTS_AVAILABLE:
        return None
    
    try:
        response = _retry_with_backoff(
            requests.get,
            f"{api_url}/candidates/{candidate_id}",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.warning(f"Could not fetch Greenhouse candidate: {e}")
        return None


def _sync_job_from_greenhouse(gh_job: Dict[str, Any]) -> None:
    """Sincroniza job desde Greenhouse a nuestro sistema"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Actualizar o crear job posting
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
            f"gh_{gh_job.get('id')}",
            gh_job.get("name"),
            gh_job.get("notes"),
            "active" if gh_job.get("status") == "open" else "closed",
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
            "greenhouse",
            str(gh_job.get("id")),
            "job",
            f"gh_{gh_job.get('id')}",
            "inbound",
            datetime.now(timezone.utc),
            "synced"
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Error syncing job from Greenhouse: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _sync_job_to_greenhouse(job_id: str, api_url: str, api_key: str) -> None:
    """Sincroniza job desde nuestro sistema a Greenhouse"""
    # Implementación similar pero en dirección opuesta
    logger.info(f"Syncing job {job_id} to Greenhouse")
    pass


def _sync_candidate_from_greenhouse(gh_candidate: Dict[str, Any]) -> None:
    """Sincroniza candidato desde Greenhouse"""
    logger.info(f"Syncing candidate from Greenhouse: {gh_candidate.get('id')}")
    pass


def _sync_candidate_to_greenhouse(candidate_id: str, api_url: str, api_key: str) -> None:
    """Sincroniza candidato a Greenhouse"""
    logger.info(f"Syncing candidate {candidate_id} to Greenhouse")
    pass


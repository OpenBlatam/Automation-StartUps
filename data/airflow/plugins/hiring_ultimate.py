"""
Funcionalidades Ultimate para Hiring ATS
==========================================

- Reporting avanzado y dashboards
- Evaluación de candidatos por IA (video, transcripciones)
- Market intelligence
- Candidate experience scoring
- Employer reputation management
- Retención predictiva
- HR analytics avanzado
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
# EVALUACIÓN DE CANDIDATOS POR IA (VIDEO, TRANSCRIPCIONES)
# ============================================================================

def analyze_video_interview_ai(
    interview_id: str,
    video_url: Optional[str] = None,
    transcription: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analiza entrevista de video usando IA.
    
    Análisis:
    - Sentimiento
    - Keywords y temas
    - Fluidez verbal
    - Coherencia
    - Nivel de energía
    - Engagement
    """
    logger.info("analyzing video interview with AI", extra={"interview_id": interview_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información de la entrevista
        cursor.execute("""
            SELECT interview_id, application_id, interview_type, scheduled_start
            FROM ats_interviews
            WHERE interview_id = %s
        """, (interview_id,))
        
        interview_data = cursor.fetchone()
        if not interview_data:
            raise ValueError(f"Interview {interview_id} not found")
        
        # Si no hay transcripción, obtenerla
        if not transcription:
            transcription = _transcribe_video(video_url) if video_url else None
        
        if not transcription:
            return {"error": "No transcription available"}
        
        # Análisis con IA
        ai_analysis = _analyze_transcription_ai(transcription)
        video_analysis = _analyze_video_ai(video_url) if video_url else {}
        
        # Combinar análisis
        combined_analysis = {
            "sentiment_score": ai_analysis.get("sentiment_score", 0),
            "fluency_score": ai_analysis.get("fluency_score", 0),
            "coherence_score": ai_analysis.get("coherence_score", 0),
            "energy_level": video_analysis.get("energy_level", "medium"),
            "engagement_score": video_analysis.get("engagement_score", 0),
            "keywords": ai_analysis.get("keywords", []),
            "topics": ai_analysis.get("topics", []),
            "recommendations": ai_analysis.get("recommendations", []),
            "overall_ai_score": _calculate_ai_score(ai_analysis, video_analysis)
        }
        
        # Guardar análisis
        cursor.execute("""
            UPDATE ats_video_interviews
            SET transcription = %s,
                analysis = %s,
                status = 'completed',
                updated_at = NOW()
            WHERE interview_id = %s
        """, (
            transcription,
            json.dumps(combined_analysis),
            interview_id
        ))
        
        # Actualizar rating de entrevista basado en AI
        ai_rating = min(5, max(1, combined_analysis["overall_ai_score"] / 20))
        cursor.execute("""
            UPDATE ats_interviews
            SET rating = %s,
                feedback = jsonb_set(
                    COALESCE(feedback::jsonb, '{}'::jsonb),
                    '{ai_analysis}',
                    %s::jsonb
                )::text,
                updated_at = NOW()
            WHERE interview_id = %s
        """, (
            int(ai_rating),
            json.dumps(combined_analysis),
            interview_id
        ))
        
        conn.commit()
        
        return {
            "interview_id": interview_id,
            "analysis": combined_analysis,
            "ai_rating": ai_rating
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error analyzing video interview: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _transcribe_video(video_url: str) -> Optional[str]:
    """Transcribe video usando API de transcripción"""
    transcription_api = _env("TRANSCRIPTION_API_URL")
    
    if not transcription_api or not REQUESTS_AVAILABLE:
        return None
    
    try:
        response = requests.post(
            f"{transcription_api}/transcribe",
            json={"video_url": video_url},
            headers={"Authorization": f"Bearer {_env('TRANSCRIPTION_API_KEY')}"},
            timeout=120
        )
        response.raise_for_status()
        return response.json().get("transcription")
    except Exception as e:
        logger.warning(f"Error transcribing video: {e}")
        return None


def _analyze_transcription_ai(transcription: str) -> Dict[str, Any]:
    """Analiza transcripción con IA"""
    ai_api = _env("AI_ANALYSIS_API_URL")
    
    if ai_api and REQUESTS_AVAILABLE:
        try:
            response = requests.post(
                f"{ai_api}/analyze",
                json={"text": transcription},
                headers={"Authorization": f"Bearer {_env('AI_ANALYSIS_API_KEY')}"},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error analyzing transcription: {e}")
    
    # Fallback: análisis básico
    words = len(transcription.split())
    sentences = len(transcription.split('.'))
    
    return {
        "sentiment_score": 70,  # Neutral
        "fluency_score": min(100, words / 100 * 100),
        "coherence_score": 75,
        "keywords": ["experience", "skills", "team"],
        "topics": ["work experience", "technical skills"],
        "recommendations": ["Good communication"]
    }


def _analyze_video_ai(video_url: str) -> Dict[str, Any]:
    """Analiza video con IA (sentimiento facial, energía, etc.)"""
    video_ai_api = _env("VIDEO_AI_API_URL")
    
    if video_ai_api and REQUESTS_AVAILABLE:
        try:
            response = requests.post(
                f"{video_ai_api}/analyze",
                json={"video_url": video_url},
                headers={"Authorization": f"Bearer {_env('VIDEO_AI_API_KEY')}"},
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Error analyzing video: {e}")
    
    return {
        "energy_level": "medium",
        "engagement_score": 70,
        "facial_sentiment": "neutral"
    }


def _calculate_ai_score(ai_analysis: Dict[str, Any], video_analysis: Dict[str, Any]) -> float:
    """Calcula score general basado en análisis de IA"""
    sentiment = ai_analysis.get("sentiment_score", 0)
    fluency = ai_analysis.get("fluency_score", 0)
    coherence = ai_analysis.get("coherence_score", 0)
    engagement = video_analysis.get("engagement_score", 0)
    
    return (sentiment * 0.3 + fluency * 0.3 + coherence * 0.2 + engagement * 0.2)


# ============================================================================
# MARKET INTELLIGENCE
# ============================================================================

def get_market_intelligence(
    job_title: str,
    location: str
) -> Dict[str, Any]:
    """
    Obtiene inteligencia de mercado para un puesto.
    
    Datos:
    - Competencia (otras empresas contratando)
    - Salarios promedio del mercado
    - Disponibilidad de talento
    - Tendencias de contratación
    """
    logger.info("getting market intelligence", extra={"job_title": job_title, "location": location})
    
    # Análisis de competencia
    competition_data = _analyze_competition(job_title, location)
    
    # Análisis de talento disponible
    talent_availability = _analyze_talent_availability(job_title, location)
    
    # Tendencias
    trends = _analyze_hiring_trends(job_title, location)
    
    return {
        "job_title": job_title,
        "location": location,
        "competition": competition_data,
        "talent_availability": talent_availability,
        "trends": trends,
        "market_score": _calculate_market_score(competition_data, talent_availability),
        "recommendations": _generate_market_recommendations(competition_data, talent_availability)
    }


def _analyze_competition(job_title: str, location: str) -> Dict[str, Any]:
    """Analiza competencia en el mercado"""
    # Simulación - en producción usaría APIs de job boards
    return {
        "active_postings": 45,
        "companies_hiring": ["Google", "Microsoft", "Amazon"],
        "average_time_to_fill": 28,
        "competition_level": "high"  # low, medium, high
    }


def _analyze_talent_availability(job_title: str, location: str) -> Dict[str, Any]:
    """Analiza disponibilidad de talento"""
    return {
        "available_candidates": 1200,
        "talent_pool_size": "large",  # small, medium, large
        "average_response_rate": 15.5,
        "skills_availability": {
            "python": "high",
            "aws": "medium",
            "kubernetes": "low"
        }
    }


def _analyze_hiring_trends(job_title: str, location: str) -> Dict[str, Any]:
    """Analiza tendencias de contratación"""
    return {
        "trend": "increasing",  # increasing, stable, decreasing
        "growth_rate": 12.5,
        "seasonal_patterns": {
            "q1": "high",
            "q2": "medium",
            "q3": "low",
            "q4": "high"
        }
    }


def _calculate_market_score(competition: Dict[str, Any], talent: Dict[str, Any]) -> float:
    """Calcula score de mercado (0-100)"""
    competition_level = {"low": 80, "medium": 60, "high": 40}.get(competition.get("competition_level", "medium"), 60)
    talent_pool = {"small": 40, "medium": 60, "large": 80}.get(talent.get("talent_pool_size", "medium"), 60)
    
    return (competition_level + talent_pool) / 2


def _generate_market_recommendations(
    competition: Dict[str, Any],
    talent: Dict[str, Any]
) -> List[str]:
    """Genera recomendaciones basadas en mercado"""
    recommendations = []
    
    if competition.get("competition_level") == "high":
        recommendations.append("Considerar aumentar rango salarial para ser competitivo")
        recommendations.append("Acelerar proceso de hiring para no perder candidatos")
    
    if talent.get("talent_pool_size") == "small":
        recommendations.append("Expandir búsqueda a ubicaciones remotas")
        recommendations.append("Considerar training interno")
    
    return recommendations


# ============================================================================
# CANDIDATE EXPERIENCE SCORING
# ============================================================================

def calculate_candidate_experience_score(
    application_id: str
) -> Dict[str, Any]:
    """
    Calcula score de experiencia del candidato.
    
    Factores:
    - Tiempo de respuesta
    - Claridad de comunicación
    - Facilidad del proceso
    - Feedback recibido
    - Transparencia
    """
    logger.info("calculating candidate experience score", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos de la aplicación
        cursor.execute("""
            SELECT a.application_id, a.applied_at, a.status,
                   COUNT(DISTINCT c.communication_id) as comm_count,
                   AVG(CASE WHEN c.direction = 'outbound' THEN 
                       EXTRACT(EPOCH FROM (c.read_at - c.sent_at)) / 3600 END) as avg_response_hours,
                   COUNT(DISTINCT i.interview_id) as interview_count,
                   COUNT(DISTINCT CASE WHEN i.status = 'cancelled' THEN i.interview_id END) as cancelled_interviews
            FROM ats_applications a
            LEFT JOIN ats_communications c ON a.application_id = c.application_id
            LEFT JOIN ats_interviews i ON a.application_id = i.application_id
            WHERE a.application_id = %s
            GROUP BY a.application_id, a.applied_at, a.status
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            raise ValueError(f"Application {application_id} not found")
        
        # Calcular factores
        factors = {}
        total_score = 0
        
        # Factor 1: Tiempo de respuesta (30%)
        avg_response = float(app_data[4] or 48)  # horas
        if avg_response < 24:
            response_score = 100
        elif avg_response < 48:
            response_score = 80
        elif avg_response < 72:
            response_score = 60
        else:
            response_score = 40
        
        factors["response_time_score"] = response_score
        total_score += response_score * 0.3
        
        # Factor 2: Comunicación (25%)
        comm_count = app_data[3] or 0
        if comm_count >= 5:
            comm_score = 100
        elif comm_count >= 3:
            comm_score = 80
        elif comm_count >= 1:
            comm_score = 60
        else:
            comm_score = 40
        
        factors["communication_score"] = comm_score
        total_score += comm_score * 0.25
        
        # Factor 3: Estabilidad del proceso (25%)
        cancelled = app_data[6] or 0
        if cancelled == 0:
            stability_score = 100
        elif cancelled == 1:
            stability_score = 70
        else:
            stability_score = 40
        
        factors["stability_score"] = stability_score
        total_score += stability_score * 0.25
        
        # Factor 4: Transparencia (20%)
        # Basado en si recibió feedback y updates
        if app_data[2] != "applied":  # Si avanzó, hay transparencia
            transparency_score = 80
        else:
            transparency_score = 50
        
        factors["transparency_score"] = transparency_score
        total_score += transparency_score * 0.2
        
        overall_score = round(total_score, 2)
        
        # Guardar score
        cursor.execute("""
            INSERT INTO ats_candidate_experience
            (experience_id, application_id, overall_score, response_time_score,
             communication_score, stability_score, transparency_score, factors, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (application_id) 
            DO UPDATE SET 
                overall_score = EXCLUDED.overall_score,
                response_time_score = EXCLUDED.response_time_score,
                communication_score = EXCLUDED.communication_score,
                stability_score = EXCLUDED.stability_score,
                transparency_score = EXCLUDED.transparency_score,
                factors = EXCLUDED.factors,
                calculated_at = EXCLUDED.calculated_at
        """, (
            f"exp_{uuid.uuid4().hex[:12]}",
            application_id,
            overall_score,
            response_score,
            comm_score,
            stability_score,
            transparency_score,
            json.dumps(factors),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "application_id": application_id,
            "overall_score": overall_score,
            "factors": factors,
            "experience_level": "excellent" if overall_score >= 90 else "good" if overall_score >= 70 else "fair" if overall_score >= 50 else "poor"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error calculating candidate experience: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# EMPLOYER REPUTATION MANAGEMENT
# ============================================================================

def monitor_employer_reputation(
    company_name: str
) -> Dict[str, Any]:
    """
    Monitorea reputación del empleador.
    
    Fuentes:
    - Glassdoor reviews
    - Indeed reviews
    - LinkedIn company page
    - Social media mentions
    """
    logger.info("monitoring employer reputation", extra={"company_name": company_name})
    
    reputation_data = {
        "glassdoor": _get_glassdoor_reviews(company_name),
        "indeed": _get_indeed_reviews(company_name),
        "linkedin": _get_linkedin_ratings(company_name),
        "social_mentions": _get_social_mentions(company_name)
    }
    
    # Calcular score general
    scores = []
    for source, data in reputation_data.items():
        if isinstance(data, dict) and "rating" in data:
            scores.append(data["rating"])
    
    overall_rating = sum(scores) / len(scores) if scores else 0
    
    return {
        "company_name": company_name,
        "overall_rating": round(overall_rating, 2),
        "sources": reputation_data,
        "trend": "improving",  # improving, stable, declining
        "recommendations": _generate_reputation_recommendations(overall_rating)
    }


def _get_glassdoor_reviews(company_name: str) -> Dict[str, Any]:
    """Obtiene reviews de Glassdoor"""
    # Stub implementation
    return {
        "rating": 4.2,
        "review_count": 150,
        "recent_reviews": 5
    }


def _get_indeed_reviews(company_name: str) -> Dict[str, Any]:
    """Obtiene reviews de Indeed"""
    # Stub implementation
    return {
        "rating": 4.0,
        "review_count": 200,
        "recent_reviews": 8
    }


def _get_linkedin_ratings(company_name: str) -> Dict[str, Any]:
    """Obtiene ratings de LinkedIn"""
    # Stub implementation
    return {
        "rating": 4.3,
        "follower_count": 5000
    }


def _get_social_mentions(company_name: str) -> Dict[str, Any]:
    """Obtiene menciones en redes sociales"""
    # Stub implementation
    return {
        "positive_mentions": 45,
        "negative_mentions": 5,
        "neutral_mentions": 20,
        "sentiment_score": 75
    }


def _generate_reputation_recommendations(rating: float) -> List[str]:
    """Genera recomendaciones basadas en rating"""
    recommendations = []
    
    if rating < 3.5:
        recommendations.append("Mejorar proceso de hiring y onboarding")
        recommendations.append("Responder a reviews negativas")
        recommendations.append("Implementar programas de engagement")
    elif rating < 4.0:
        recommendations.append("Mantener estándares actuales")
        recommendations.append("Solicitar feedback de empleados")
    
    return recommendations


# ============================================================================
# RETENCIÓN PREDICTIVA
# ============================================================================

def predict_retention_risk(
    candidate_id: str,
    hire_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Predice riesgo de retención para nuevo empleado.
    
    Factores:
    - Score de matching
    - Experiencia previa
    - Salario vs mercado
    - Cultural fit
    - Onboarding experience
    """
    logger.info("predicting retention risk", extra={"candidate_id": candidate_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos del candidato y aplicación
        cursor.execute("""
            SELECT a.application_id, a.match_score, ml.overall_score,
                   ml.cultural_fit_score, j.salary_range_min, j.salary_range_max,
                   o.onboarding_status, o.completed_tasks, o.total_tasks
            FROM ats_candidates c
            JOIN ats_applications a ON c.candidate_id = a.candidate_id
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            LEFT JOIN ats_job_postings j ON a.job_id = j.job_id
            LEFT JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
            WHERE c.candidate_id = %s
              AND a.status = 'hired'
            ORDER BY a.updated_at DESC
            LIMIT 1
        """, (candidate_id,))
        
        candidate_data = cursor.fetchone()
        if not candidate_data:
            return {"error": "Hired candidate not found"}
        
        # Calcular factores de riesgo
        risk_factors = {}
        risk_score = 0
        
        # Factor 1: Matching (30%)
        ml_score = float(candidate_data[2] or candidate_data[1] or 0)
        if ml_score < 60:
            risk_score += 30
            risk_factors["low_matching"] = True
        
        # Factor 2: Cultural fit (25%)
        cultural_fit = float(candidate_data[3] or 0)
        if cultural_fit < 50:
            risk_score += 25
            risk_factors["low_cultural_fit"] = True
        
        # Factor 3: Onboarding (25%)
        onboarding_status = candidate_data[6]
        completed_tasks = candidate_data[7] or 0
        total_tasks = candidate_data[8] or 0
        
        if onboarding_status != "completed":
            if total_tasks > 0:
                completion_rate = completed_tasks / total_tasks
                if completion_rate < 0.7:
                    risk_score += 25
                    risk_factors["poor_onboarding"] = True
        
        # Factor 4: Salario (20%)
        salary_min = float(candidate_data[4] or 0)
        salary_max = float(candidate_data[5] or 0)
        # Comparar con mercado (simplificado)
        if salary_max < 50000:  # Ejemplo
            risk_score += 20
            risk_factors["below_market_salary"] = True
        
        # Risk level
        if risk_score >= 70:
            risk_level = "high"
        elif risk_score >= 40:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Guardar predicción
        cursor.execute("""
            INSERT INTO ats_retention_predictions
            (prediction_id, candidate_id, risk_score, risk_level, risk_factors, predicted_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            f"retention_{uuid.uuid4().hex[:12]}",
            candidate_id,
            risk_score,
            risk_level,
            json.dumps(risk_factors),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "candidate_id": candidate_id,
            "risk_score": round(risk_score, 2),
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": _generate_retention_recommendations(risk_level, risk_factors)
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error predicting retention: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _generate_retention_recommendations(risk_level: str, factors: Dict[str, Any]) -> List[str]:
    """Genera recomendaciones para mejorar retención"""
    recommendations = []
    
    if risk_level == "high":
        recommendations.append("Implementar plan de retención inmediato")
        recommendations.append("Asignar mentor para nuevo empleado")
        recommendations.append("Revisar paquete de compensación")
    
    if factors.get("low_matching"):
        recommendations.append("Proporcionar training adicional")
        recommendations.append("Clarificar expectativas del rol")
    
    if factors.get("poor_onboarding"):
        recommendations.append("Acelerar proceso de onboarding")
        recommendations.append("Asignar buddy/mentor")
    
    return recommendations


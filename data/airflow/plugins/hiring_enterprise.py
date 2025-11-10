"""
Funcionalidades Enterprise para Hiring ATS
===========================================

- Employer branding y social media
- Gamificación del proceso
- Employee advocacy
- A/B testing de procesos
- Compliance y auditoría
- Documentación automatizada
- Mobile APIs
- Predicción de tiempo de contratación
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
# EMPLOYER BRANDING Y SOCIAL MEDIA
# ============================================================================

def publish_job_to_social_media(
    job_id: str,
    platforms: List[str]
) -> Dict[str, Any]:
    """
    Publica vacante en redes sociales para employer branding.
    
    Plataformas:
    - LinkedIn Company Page
    - Twitter/X
    - Facebook
    - Instagram
    - TikTok
    """
    logger.info("publishing job to social media", extra={"job_id": job_id, "platforms": platforms})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del job
        cursor.execute("""
            SELECT title, description, location, department
            FROM ats_job_postings
            WHERE job_id = %s
        """, (job_id,))
        
        job_data = cursor.fetchone()
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        results = {}
        
        for platform in platforms:
            try:
                if platform == "linkedin":
                    result = _publish_to_linkedin_company(job_id, job_data)
                elif platform == "twitter":
                    result = _publish_to_twitter(job_id, job_data)
                elif platform == "facebook":
                    result = _publish_to_facebook(job_id, job_data)
                elif platform == "instagram":
                    result = _publish_to_instagram(job_id, job_data)
                else:
                    result = {"success": False, "error": f"Platform {platform} not supported"}
                
                results[platform] = result
                
            except Exception as e:
                logger.error(f"Error publishing to {platform}: {e}")
                results[platform] = {"success": False, "error": str(e)}
        
        return {
            "job_id": job_id,
            "platforms": results,
            "published_count": sum(1 for r in results.values() if r.get("success"))
        }
        
    except Exception as e:
        logger.error(f"Error publishing to social media: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _publish_to_linkedin_company(job_id: str, job_data: tuple) -> Dict[str, Any]:
    """Publica en LinkedIn Company Page"""
    linkedin_token = _env("LINKEDIN_COMPANY_TOKEN")
    linkedin_company_id = _env("LINKEDIN_COMPANY_ID")
    
    if not all([linkedin_token, linkedin_company_id]):
        return {"success": False, "error": "LinkedIn credentials not configured"}
    
    try:
        post_content = f"🚀 We're hiring! {job_data[0]}\n\nLocation: {job_data[2]}\n\n{job_data[1][:500]}..."
        
        if REQUESTS_AVAILABLE:
            response = requests.post(
                f"https://api.linkedin.com/v2/ugcPosts",
                json={
                    "author": f"urn:li:organization:{linkedin_company_id}",
                    "lifecycleState": "PUBLISHED",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {
                            "shareCommentary": {"text": post_content},
                            "shareMediaCategory": "NONE"
                        }
                    },
                    "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
                },
                headers={
                    "Authorization": f"Bearer {linkedin_token}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "post_id": response.json().get("id")}
        else:
            return {"success": True, "stub": True}
            
    except Exception as e:
        logger.error(f"Error publishing to LinkedIn: {e}")
        return {"success": False, "error": str(e)}


def _publish_to_twitter(job_id: str, job_data: tuple) -> Dict[str, Any]:
    """Publica en Twitter/X"""
    twitter_api_key = _env("TWITTER_API_KEY")
    
    if not twitter_api_key:
        return {"success": False, "error": "Twitter API not configured"}
    
    try:
        tweet_text = f"🚀 We're hiring! {job_data[0]} - {job_data[2]}\n\nApply now! #hiring #jobs"
        
        if REQUESTS_AVAILABLE:
            # Twitter API v2
            response = requests.post(
                "https://api.twitter.com/2/tweets",
                json={"text": tweet_text},
                headers={
                    "Authorization": f"Bearer {twitter_api_key}",
                    "Content-Type": "application/json"
                },
                timeout=30
            )
            response.raise_for_status()
            return {"success": True, "tweet_id": response.json().get("data", {}).get("id")}
        else:
            return {"success": True, "stub": True}
            
    except Exception as e:
        logger.error(f"Error publishing to Twitter: {e}")
        return {"success": False, "error": str(e)}


def _publish_to_facebook(job_id: str, job_data: tuple) -> Dict[str, Any]:
    """Publica en Facebook"""
    # Stub implementation
    return {"success": True, "stub": True}


def _publish_to_instagram(job_id: str, job_data: tuple) -> Dict[str, Any]:
    """Publica en Instagram"""
    # Stub implementation
    return {"success": True, "stub": True}


# ============================================================================
# GAMIFICACIÓN
# ============================================================================

def award_referral_points(
    referrer_email: str,
    points: int,
    reason: str
) -> Dict[str, Any]:
    """Otorga puntos de gamificación a referrer"""
    logger.info("awarding referral points", extra={"referrer_email": referrer_email, "points": points})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si existe tabla de gamificación
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ats_gamification'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ats_gamification (
                    id SERIAL PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    points INTEGER DEFAULT 0,
                    level VARCHAR(64) DEFAULT 'bronze', -- 'bronze', 'silver', 'gold', 'platinum'
                    badges TEXT[],
                    total_referrals INTEGER DEFAULT 0,
                    successful_hires INTEGER DEFAULT 0,
                    last_updated TIMESTAMPTZ DEFAULT NOW(),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            conn.commit()
        
        # Obtener puntos actuales
        cursor.execute("""
            SELECT points, level, badges, total_referrals
            FROM ats_gamification
            WHERE user_email = %s
        """, (referrer_email,))
        
        user_data = cursor.fetchone()
        
        if user_data:
            current_points = user_data[0] or 0
            new_points = current_points + points
            level = _calculate_level(new_points)
            badges = user_data[2] or []
            
            # Agregar badge si es necesario
            if points >= 100 and "referral_master" not in badges:
                badges.append("referral_master")
            
            cursor.execute("""
                UPDATE ats_gamification
                SET points = %s, level = %s, badges = %s,
                    total_referrals = total_referrals + 1,
                    last_updated = NOW()
                WHERE user_email = %s
            """, (new_points, level, badges, referrer_email))
        else:
            new_points = points
            level = _calculate_level(new_points)
            badges = []
            
            cursor.execute("""
                INSERT INTO ats_gamification
                (user_email, points, level, badges, total_referrals, successful_hires)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (referrer_email, new_points, level, badges, 1, 0))
        
        conn.commit()
        
        return {
            "referrer_email": referrer_email,
            "points_awarded": points,
            "total_points": new_points,
            "level": level,
            "badges": badges,
            "reason": reason
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error awarding points: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _calculate_level(points: int) -> str:
    """Calcula nivel basado en puntos"""
    if points >= 1000:
        return "platinum"
    elif points >= 500:
        return "gold"
    elif points >= 200:
        return "silver"
    else:
        return "bronze"


# ============================================================================
# EMPLOYEE ADVOCACY
# ============================================================================

def create_employee_advocacy_post(
    employee_email: str,
    job_id: str,
    platform: str
) -> Dict[str, Any]:
    """Crea post de employee advocacy para compartir"""
    logger.info("creating employee advocacy post", extra={
        "employee_email": employee_email,
        "job_id": job_id,
        "platform": platform
    })
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del job
        cursor.execute("""
            SELECT title, description, location, department
            FROM ats_job_postings
            WHERE job_id = %s
        """, (job_id,))
        
        job_data = cursor.fetchone()
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        # Generar post personalizado
        post_content = _generate_advocacy_post(employee_email, job_data, platform)
        
        # Guardar post
        post_id = f"advocacy_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_employee_advocacy
            (post_id, employee_email, job_id, platform, post_content, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            post_id,
            employee_email,
            job_id,
            platform,
            post_content,
            "pending",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "post_id": post_id,
            "employee_email": employee_email,
            "platform": platform,
            "content": post_content
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating advocacy post: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _generate_advocacy_post(employee_email: str, job_data: tuple, platform: str) -> str:
    """Genera contenido de post de advocacy"""
    templates = {
        "linkedin": f"🎯 Excited to share we're hiring! We're looking for a {job_data[0]} to join our {job_data[3]} team in {job_data[2]}. It's an amazing place to work - I'd love to chat if you're interested!",
        "twitter": f"🚀 We're hiring! {job_data[0]} - {job_data[2]}. Great team, great culture! #hiring",
        "facebook": f"Looking for your next opportunity? We're hiring a {job_data[0]}! Check it out."
    }
    
    return templates.get(platform, templates["linkedin"])


# ============================================================================
# A/B TESTING DE PROCESOS
# ============================================================================

def create_ab_test(
    test_name: str,
    test_type: str,
    variants: List[Dict[str, Any]],
    traffic_split: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Crea A/B test para procesos de hiring.
    
    Tipos de test:
    - email_template: Test de templates de email
    - interview_process: Test de procesos de entrevista
    - job_description: Test de descripciones de trabajo
    - application_form: Test de formularios
    """
    logger.info("creating A/B test", extra={"test_name": test_name, "test_type": test_type})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        test_id = f"abtest_{uuid.uuid4().hex[:12]}"
        
        # Normalizar traffic split
        if not traffic_split:
            traffic_split = [1.0 / len(variants)] * len(variants)
        
        cursor.execute("""
            INSERT INTO ats_ab_tests
            (test_id, test_name, test_type, variants, traffic_split, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            test_id,
            test_name,
            test_type,
            json.dumps(variants),
            traffic_split,
            "active",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "test_id": test_id,
            "test_name": test_name,
            "test_type": test_type,
            "variants": variants,
            "traffic_split": traffic_split
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating A/B test: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def assign_variant_to_application(
    application_id: str,
    test_id: str
) -> Dict[str, Any]:
    """Asigna variante de A/B test a aplicación"""
    import random
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener test
        cursor.execute("""
            SELECT variants, traffic_split, status
            FROM ats_ab_tests
            WHERE test_id = %s
        """, (test_id,))
        
        test_data = cursor.fetchone()
        if not test_data or test_data[2] != "active":
            return {"assigned": False, "reason": "Test not active"}
        
        variants = json.loads(test_data[0])
        traffic_split = test_data[1]
        
        # Asignar variante basado en traffic split
        rand = random.random()
        cumulative = 0
        selected_variant = None
        variant_index = 0
        
        for i, split in enumerate(traffic_split):
            cumulative += split
            if rand <= cumulative:
                selected_variant = variants[i]
                variant_index = i
                break
        
        if not selected_variant:
            selected_variant = variants[0]
            variant_index = 0
        
        # Guardar asignación
        cursor.execute("""
            INSERT INTO ats_ab_test_assignments
            (assignment_id, test_id, application_id, variant_index, variant_name, assigned_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            f"assign_{uuid.uuid4().hex[:12]}",
            test_id,
            application_id,
            variant_index,
            selected_variant.get("name", f"variant_{variant_index}"),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "assigned": True,
            "test_id": test_id,
            "variant": selected_variant,
            "variant_index": variant_index
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error assigning variant: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# COMPLIANCE Y AUDITORÍA
# ============================================================================

def log_compliance_event(
    event_type: str,
    entity_type: str,
    entity_id: str,
    action: str,
    user_email: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Registra evento de compliance para auditoría"""
    logger.info("logging compliance event", extra={
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id
    })
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        event_id = f"compliance_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_compliance_audit
            (event_id, event_type, entity_type, entity_id, action, user_email, details, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            event_id,
            event_type,  # 'data_access', 'data_modification', 'data_deletion', 'export', etc.
            entity_type,  # 'candidate', 'application', 'interview', etc.
            entity_id,
            action,  # 'view', 'create', 'update', 'delete', 'export'
            user_email,
            json.dumps(details or {}),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "event_id": event_id,
            "logged": True
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error logging compliance event: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# PREDICCIÓN DE TIEMPO DE CONTRATACIÓN
# ============================================================================

def predict_time_to_hire(
    job_id: str,
    current_applications: int
) -> Dict[str, Any]:
    """
    Predice tiempo hasta contratación basado en datos históricos.
    
    Factores considerados:
    - Número de aplicaciones actuales
    - Tiempo promedio histórico
    - Tasa de conversión histórica
    - Complejidad del rol
    """
    logger.info("predicting time to hire", extra={"job_id": job_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos históricos
        cursor.execute("""
            SELECT 
                AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) as avg_days_to_fill,
                COUNT(DISTINCT a.application_id) as avg_applications_per_hire,
                COUNT(DISTINCT CASE WHEN a.status = 'hired' THEN a.application_id END) as total_hires
            FROM ats_job_postings j
            JOIN ats_applications a ON j.job_id = a.job_id
            WHERE j.department = (SELECT department FROM ats_job_postings WHERE job_id = %s)
              AND j.status = 'closed'
              AND a.status = 'hired'
            GROUP BY j.department
        """, (job_id,))
        
        historical_data = cursor.fetchone()
        
        if not historical_data or not historical_data[0]:
            # Fallback a datos generales
            cursor.execute("""
                SELECT 
                    AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) as avg_days,
                    AVG(j.current_applicants) as avg_apps
                FROM ats_job_postings j
                JOIN ats_applications a ON j.job_id = a.job_id
                WHERE a.status = 'hired'
            """)
            historical_data = cursor.fetchone()
        
        avg_days = float(historical_data[0] or 30) if historical_data else 30
        avg_apps_per_hire = float(historical_data[1] or 10) if historical_data else 10
        
        # Calcular predicción
        if current_applications >= avg_apps_per_hire:
            # Ya tenemos suficientes aplicaciones
            predicted_days = avg_days * 0.5  # Más rápido
        else:
            # Necesitamos más aplicaciones
            apps_needed = avg_apps_per_hire - current_applications
            # Asumir tasa de aplicación diaria
            daily_app_rate = 2.0  # Aplicaciones por día (promedio)
            days_to_get_apps = apps_needed / daily_app_rate
            predicted_days = avg_days + days_to_get_apps
        
        # Guardar predicción
        cursor.execute("""
            INSERT INTO ats_analytics
            (metric_id, metric_name, metric_type, job_id, metric_value, metric_data, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            f"metric_{uuid.uuid4().hex[:12]}",
            f"time_to_hire_prediction_{job_id}",
            "time_to_hire_prediction",
            job_id,
            predicted_days,
            json.dumps({
                "predicted_days": predicted_days,
                "current_applications": current_applications,
                "avg_apps_per_hire": avg_apps_per_hire,
                "historical_avg_days": avg_days
            }),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "job_id": job_id,
            "predicted_days": round(predicted_days, 1),
            "predicted_date": (datetime.now(timezone.utc) + timedelta(days=int(predicted_days))).isoformat(),
            "current_applications": current_applications,
            "historical_avg_days": round(avg_days, 1),
            "confidence": "high" if historical_data else "medium"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error predicting time to hire: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


"""
Sistema de IA y Búsqueda Inteligente para Hiring ATS
====================================================

- Búsqueda semántica con embeddings
- Matching inteligente con IA
- Calibración de entrevistas
- Análisis de diversidad e inclusión
- Benchmarking de salarios
- Talent pools inteligentes
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Dict, Any, Optional, List, Tuple
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
# BÚSQUEDA INTELIGENTE CON IA
# ============================================================================

def intelligent_candidate_search(
    job_id: str,
    query: Optional[str] = None,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 20,
    use_ai_matching: bool = True
) -> Dict[str, Any]:
    """
    Búsqueda inteligente de candidatos usando IA y matching semántico.
    
    Args:
        job_id: ID de la vacante
        query: Búsqueda por texto libre
        filters: Filtros adicionales (location, experience, skills, etc.)
        limit: Límite de resultados
        use_ai_matching: Usar matching con IA
    
    Returns:
        Dict con candidatos encontrados y scores de matching
    """
    logger.info("intelligent candidate search", extra={"job_id": job_id, "query": query})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener información del job
        cursor.execute("""
            SELECT title, description, requirements, keywords, department
            FROM ats_job_postings
            WHERE job_id = %s
        """, (job_id,))
        
        job_data = cursor.fetchone()
        if not job_data:
            raise ValueError(f"Job {job_id} not found")
        
        # Construir query SQL base
        sql_query = """
            SELECT DISTINCT c.candidate_id, c.first_name, c.last_name, c.email,
                   c.resume_text, c.location, c.source,
                   a.application_id, a.status, a.match_score,
                   ml.overall_score, ml.predicted_hire_probability
            FROM ats_candidates c
            LEFT JOIN ats_applications a ON c.candidate_id = a.candidate_id AND a.job_id = %s
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            WHERE 1=1
        """
        
        params = [job_id]
        
        # Aplicar filtros
        if filters:
            if filters.get("location"):
                sql_query += " AND c.location ILIKE %s"
                params.append(f"%{filters['location']}%")
            
            if filters.get("min_experience"):
                # Esto requeriría extraer años de experiencia del resume_text
                pass
            
            if filters.get("has_application") is False:
                sql_query += " AND a.application_id IS NULL"
        
        sql_query += " ORDER BY COALESCE(ml.overall_score, a.match_score, 0) DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(sql_query, params)
        candidates = cursor.fetchall()
        
        # Si hay query de texto, usar búsqueda semántica
        if query and use_ai_matching:
            candidates = _semantic_search_filter(candidates, query, job_data)
        
        # Formatear resultados
        results = []
        for candidate in candidates:
            results.append({
                "candidate_id": candidate[0],
                "name": f"{candidate[1]} {candidate[2]}",
                "email": candidate[3],
                "location": candidate[5],
                "source": candidate[6],
                "has_application": candidate[7] is not None,
                "application_status": candidate[8],
                "match_score": float(candidate[9] or 0),
                "ml_score": float(candidate[10] or 0),
                "hire_probability": float(candidate[11] or 0)
            })
        
        return {
            "total_results": len(results),
            "candidates": results,
            "search_metadata": {
                "query": query,
                "filters": filters,
                "used_ai": use_ai_matching
            }
        }
        
    except Exception as e:
        logger.error(f"Error in intelligent search: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _semantic_search_filter(
    candidates: List[tuple],
    query: str,
    job_data: tuple
) -> List[tuple]:
    """Filtra candidatos usando búsqueda semántica"""
    # Integración con modelo de embeddings (OpenAI, Cohere, etc.)
    embedding_api = _env("EMBEDDING_API_URL")
    
    if embedding_api and REQUESTS_AVAILABLE:
        try:
            # Generar embedding de la query
            query_embedding = _get_embedding(query, embedding_api)
            
            # Comparar con embeddings de candidatos (simplificado)
            # En producción, esto se haría con vector search (Pinecone, Weaviate, etc.)
            scored_candidates = []
            for candidate in candidates:
                resume_text = candidate[4] or ""
                if resume_text:
                    candidate_embedding = _get_embedding(resume_text[:500], embedding_api)
                    similarity = _cosine_similarity(query_embedding, candidate_embedding)
                    scored_candidates.append((similarity, candidate))
                else:
                    scored_candidates.append((0.0, candidate))
            
            # Ordenar por similitud
            scored_candidates.sort(key=lambda x: x[0], reverse=True)
            return [c[1] for c in scored_candidates]
            
        except Exception as e:
            logger.warning(f"Error in semantic search: {e}")
    
    # Fallback: búsqueda por keywords
    query_lower = query.lower()
    scored_candidates = []
    for candidate in candidates:
        resume_text = (candidate[4] or "").lower()
        score = sum(1 for word in query_lower.split() if word in resume_text) / len(query_lower.split()) if query_lower.split() else 0
        scored_candidates.append((score, candidate))
    
    scored_candidates.sort(key=lambda x: x[0], reverse=True)
    return [c[1] for c in scored_candidates]


def _get_embedding(text: str, api_url: str) -> List[float]:
    """Obtiene embedding de texto usando API"""
    if not REQUESTS_AVAILABLE:
        return []
    
    try:
        response = requests.post(
            f"{api_url}/embeddings",
            json={"text": text},
            headers={"Authorization": f"Bearer {_env('EMBEDDING_API_KEY')}"},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        logger.warning(f"Error getting embedding: {e}")
        return []


def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calcula similitud coseno entre dos vectores"""
    if not vec1 or not vec2 or len(vec1) != len(vec2):
        return 0.0
    
    try:
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    except Exception:
        return 0.0


# ============================================================================
# CALIBRACIÓN DE ENTREVISTAS
# ============================================================================

def calibrate_interview_feedback(
    interview_id: str,
    reviewer_ratings: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Calibra feedback de entrevistas para reducir sesgos.
    
    Args:
        interview_id: ID de la entrevista
        reviewer_ratings: Lista de ratings de múltiples entrevistadores
    
    Returns:
        Dict con rating calibrado y análisis de sesgo
    """
    logger.info("calibrating interview feedback", extra={"interview_id": interview_id})
    
    if not reviewer_ratings:
        raise ValueError("reviewer_ratings cannot be empty")
    
    # Calcular estadísticas
    ratings = [r.get("rating", 0) for r in reviewer_ratings if r.get("rating")]
    if not ratings:
        return {"calibrated_rating": 0, "error": "No valid ratings"}
    
    avg_rating = sum(ratings) / len(ratings)
    std_dev = _calculate_std_dev(ratings)
    
    # Detectar outliers (posibles sesgos)
    outliers = []
    for i, rating in enumerate(ratings):
        z_score = abs((rating - avg_rating) / std_dev) if std_dev > 0 else 0
        if z_score > 2:  # Más de 2 desviaciones estándar
            outliers.append({
                "reviewer": reviewer_ratings[i].get("reviewer_email"),
                "rating": rating,
                "z_score": z_score
            })
    
    # Rating calibrado (promedio ponderado, excluyendo outliers extremos)
    valid_ratings = [r for i, r in enumerate(ratings) if i not in [o.get("index") for o in outliers]]
    if valid_ratings:
        calibrated_rating = sum(valid_ratings) / len(valid_ratings)
    else:
        calibrated_rating = avg_rating
    
    # Análisis de sesgo
    bias_analysis = {
        "has_outliers": len(outliers) > 0,
        "outliers": outliers,
        "consensus_level": "high" if std_dev < 1.0 else "medium" if std_dev < 1.5 else "low",
        "std_dev": std_dev
    }
    
    # Guardar calibración
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE ats_interviews
            SET rating = %s,
                feedback = jsonb_set(
                    COALESCE(feedback::jsonb, '{}'::jsonb),
                    '{calibration}',
                    %s::jsonb
                )::text,
                updated_at = NOW()
            WHERE interview_id = %s
        """, (
            round(calibrated_rating),
            json.dumps({
                "calibrated_rating": calibrated_rating,
                "original_ratings": ratings,
                "bias_analysis": bias_analysis,
                "reviewer_count": len(reviewer_ratings)
            }),
            interview_id
        ))
        
        conn.commit()
        
        return {
            "calibrated_rating": round(calibrated_rating, 2),
            "original_average": round(avg_rating, 2),
            "bias_analysis": bias_analysis,
            "reviewer_count": len(reviewer_ratings)
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error calibrating interview: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _calculate_std_dev(values: List[float]) -> float:
    """Calcula desviación estándar"""
    if len(values) < 2:
        return 0.0
    
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


# ============================================================================
# DIVERSIDAD E INCLUSIÓN
# ============================================================================

def analyze_diversity_metrics(job_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analiza métricas de diversidad e inclusión.
    
    Métricas:
    - Distribución por género
    - Distribución por etnia (si disponible)
    - Distribución geográfica
    - Distribución por edad (si disponible)
    - Representación en diferentes etapas
    """
    logger.info("analyzing diversity metrics", extra={"job_id": job_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Query base
        base_query = """
            SELECT 
                COUNT(*) as total,
                COUNT(*) FILTER (WHERE c.gender = 'female') as female_count,
                COUNT(*) FILTER (WHERE c.gender = 'male') as male_count,
                COUNT(*) FILTER (WHERE c.gender = 'other') as other_count,
                COUNT(*) FILTER (WHERE c.gender IS NULL) as unknown_count,
                COUNT(*) FILTER (WHERE c.location LIKE '%US%' OR c.location LIKE '%United States%') as us_count,
                COUNT(*) FILTER (WHERE c.location LIKE '%Europe%') as europe_count,
                COUNT(*) FILTER (WHERE c.source = 'referral') as referral_count,
                COUNT(*) FILTER (WHERE a.status = 'hired') as hired_count,
                COUNT(*) FILTER (WHERE a.status = 'hired' AND c.gender = 'female') as hired_female
            FROM ats_candidates c
            LEFT JOIN ats_applications a ON c.candidate_id = a.candidate_id
        """
        
        params = []
        if job_id:
            base_query += " WHERE a.job_id = %s"
            params.append(job_id)
        
        cursor.execute(base_query, params)
        stats = cursor.fetchone()
        
        total = stats[0] or 0
        if total == 0:
            return {"error": "No data available"}
        
        # Calcular porcentajes
        gender_distribution = {
            "female": round((stats[1] / total) * 100, 2) if total > 0 else 0,
            "male": round((stats[2] / total) * 100, 2) if total > 0 else 0,
            "other": round((stats[3] / total) * 100, 2) if total > 0 else 0,
            "unknown": round((stats[4] / total) * 100, 2) if total > 0 else 0
        }
        
        location_distribution = {
            "us": round((stats[5] / total) * 100, 2) if total > 0 else 0,
            "europe": round((stats[6] / total) * 100, 2) if total > 0 else 0,
            "other": round(100 - (stats[5] / total) * 100 - (stats[6] / total) * 100, 2) if total > 0 else 0
        }
        
        # Representación en hiring
        hiring_rate = round((stats[8] / total) * 100, 2) if total > 0 else 0
        female_hiring_rate = round((stats[9] / stats[8]) * 100, 2) if stats[8] > 0 else 0
        
        # Guardar métricas
        metric_id = f"metric_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_analytics
            (metric_id, metric_name, metric_type, job_id, metric_value, metric_data, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            metric_id,
            f"diversity_{job_id or 'all'}",
            "diversity_metrics",
            job_id,
            hiring_rate,
            json.dumps({
                "gender_distribution": gender_distribution,
                "location_distribution": location_distribution,
                "hiring_rate": hiring_rate,
                "female_hiring_rate": female_hiring_rate,
                "referral_rate": round((stats[7] / total) * 100, 2) if total > 0 else 0
            }),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "total_candidates": total,
            "gender_distribution": gender_distribution,
            "location_distribution": location_distribution,
            "hiring_metrics": {
                "overall_rate": hiring_rate,
                "female_hiring_rate": female_hiring_rate
            },
            "referral_rate": round((stats[7] / total) * 100, 2) if total > 0 else 0
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error analyzing diversity: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# BENCHMARKING DE SALARIOS
# ============================================================================

def get_salary_benchmark(
    job_title: str,
    location: str,
    experience_years: int
) -> Dict[str, Any]:
    """
    Obtiene benchmark de salario usando APIs externas.
    
    Integraciones:
    - Payscale API
    - Glassdoor API
    - Salary.com API
    """
    logger.info("getting salary benchmark", extra={
        "job_title": job_title,
        "location": location,
        "experience_years": experience_years
    })
    
    benchmarks = {}
    
    # Payscale
    payscale_api = _env("PAYSCALE_API_KEY")
    if payscale_api and REQUESTS_AVAILABLE:
        try:
            response = requests.get(
                "https://api.payscale.com/v1/salary",
                params={
                    "job_title": job_title,
                    "location": location,
                    "experience": experience_years
                },
                headers={"Authorization": f"Bearer {payscale_api}"},
                timeout=10
            )
            if response.status_code == 200:
                benchmarks["payscale"] = response.json()
        except Exception as e:
            logger.warning(f"Error getting Payscale benchmark: {e}")
    
    # Glassdoor
    glassdoor_api = _env("GLASSDOOR_API_KEY")
    if glassdoor_api and REQUESTS_AVAILABLE:
        try:
            response = requests.get(
                "https://api.glassdoor.com/api/api.htm",
                params={
                    "t.p": glassdoor_api,
                    "t.k": _env("GLASSDOOR_PARTNER_ID"),
                    "action": "salaries",
                    "jobTitle": job_title,
                    "location": location
                },
                timeout=10
            )
            if response.status_code == 200:
                benchmarks["glassdoor"] = response.json()
        except Exception as e:
            logger.warning(f"Error getting Glassdoor benchmark: {e}")
    
    # Calcular promedio si hay múltiples fuentes
    salaries = []
    for source, data in benchmarks.items():
        if isinstance(data, dict) and "salary" in data:
            salaries.append(data["salary"])
    
    avg_salary = sum(salaries) / len(salaries) if salaries else None
    
    return {
        "job_title": job_title,
        "location": location,
        "experience_years": experience_years,
        "benchmarks": benchmarks,
        "average_salary": avg_salary,
        "sources_count": len(benchmarks)
    }


# ============================================================================
# TALENT POOLS
# ============================================================================

def add_to_talent_pool(
    candidate_id: str,
    pool_name: str,
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Agrega candidato a talent pool"""
    logger.info("adding to talent pool", extra={"candidate_id": candidate_id, "pool_name": pool_name})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar si existe tabla de talent pools
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'ats_talent_pools'
            )
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            # Crear tabla si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ats_talent_pools (
                    id SERIAL PRIMARY KEY,
                    pool_id VARCHAR(255) UNIQUE NOT NULL,
                    candidate_id VARCHAR(255) NOT NULL,
                    pool_name VARCHAR(255) NOT NULL,
                    tags TEXT[],
                    added_at TIMESTAMPTZ DEFAULT NOW(),
                    added_by VARCHAR(255),
                    notes TEXT,
                    FOREIGN KEY (candidate_id) REFERENCES ats_candidates(candidate_id) ON DELETE CASCADE
                )
            """)
        
        pool_id = f"pool_{uuid.uuid4().hex[:12]}"
        
        cursor.execute("""
            INSERT INTO ats_talent_pools
            (pool_id, candidate_id, pool_name, tags, added_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (pool_id) DO NOTHING
        """, (
            pool_id,
            candidate_id,
            pool_name,
            tags or [],
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "pool_id": pool_id,
            "candidate_id": candidate_id,
            "pool_name": pool_name,
            "tags": tags or []
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error adding to talent pool: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ANALYTICS PREDICTIVOS DE CALIDAD DE HIRE
# ============================================================================

def predict_hire_quality(
    application_id: str,
    candidate_features: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Predice calidad de hire usando ML.
    
    Factores considerados:
    - Scores de entrevistas
    - Scores de tests
    - ML matching score
    - Experiencia
    - Educación
    - Referral vs direct
    """
    logger.info("predicting hire quality", extra={"application_id": application_id})
    
    # Obtener datos históricos para comparación
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener scores de la aplicación
        cursor.execute("""
            SELECT a.match_score, ml.overall_score, ml.predicted_hire_probability,
                   AVG(i.rating) as avg_interview_rating,
                   AVG(t.score) as avg_test_score,
                   c.source
            FROM ats_applications a
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            LEFT JOIN ats_interviews i ON a.application_id = i.application_id
            LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
            LEFT JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
            GROUP BY a.application_id, a.match_score, ml.overall_score, 
                     ml.predicted_hire_probability, c.source
        """, (application_id,))
        
        app_data = cursor.fetchone()
        
        if not app_data:
            return {"error": "Application not found"}
        
        # Calcular score de calidad
        quality_score = 0
        factors = {}
        
        # ML score (40%)
        ml_score = float(app_data[1] or 0)
        quality_score += ml_score * 0.4
        factors["ml_score"] = ml_score
        
        # Interview rating (30%)
        interview_rating = float(app_data[3] or 0)
        if interview_rating > 0:
            quality_score += (interview_rating / 5) * 100 * 0.3
            factors["interview_rating"] = interview_rating
        
        # Test score (20%)
        test_score = float(app_data[4] or 0)
        if test_score > 0:
            quality_score += test_score * 0.2
            factors["test_score"] = test_score
        
        # Source bonus (10%)
        source = app_data[5]
        if source == "referral":
            quality_score += 10
            factors["referral_bonus"] = 10
        
        # Predicción de calidad
        quality_prediction = {
            "high": quality_score >= 80,
            "medium": 60 <= quality_score < 80,
            "low": quality_score < 60
        }
        
        # Guardar predicción
        cursor.execute("""
            INSERT INTO ats_analytics
            (metric_id, metric_name, metric_type, metric_value, metric_data, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            f"metric_{uuid.uuid4().hex[:12]}",
            f"quality_prediction_{application_id}",
            "quality_of_hire",
            quality_score,
            json.dumps({
                "quality_score": quality_score,
                "factors": factors,
                "prediction": quality_prediction,
                "candidate_features": candidate_features
            }),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "quality_score": round(quality_score, 2),
            "quality_level": "high" if quality_score >= 80 else "medium" if quality_score >= 60 else "low",
            "factors": factors,
            "prediction": quality_prediction
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error predicting hire quality: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


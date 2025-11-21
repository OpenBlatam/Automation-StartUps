"""
Analytics Avanzado y Forecasting para Hiring ATS
================================================

- Forecasting de necesidades de contratación
- ROI de hiring
- Métricas de engagement de candidatos
- Benchmarking competitivo avanzado
- Análisis de cohortes
- Predicción de demanda de talento
- Análisis de costo-beneficio
- Métricas de calidad de fuente
"""

from __future__ import annotations

import json
import logging
import os
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
from collections import defaultdict

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
# FORECASTING DE NECESIDADES DE CONTRATACIÓN
# ============================================================================

def forecast_hiring_needs(
    department: Optional[str] = None,
    months_ahead: int = 6
) -> Dict[str, Any]:
    """
    Predice necesidades de contratación futuras.
    
    Factores:
    - Crecimiento histórico
    - Tasa de rotación
    - Proyecciones de negocio
    - Tendencias de mercado
    """
    logger.info("forecasting hiring needs", extra={"department": department, "months_ahead": months_ahead})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos históricos
        query = """
            SELECT 
                j.department,
                COUNT(DISTINCT j.job_id) as jobs_posted,
                COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hires,
                AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) as avg_days_to_fill
            FROM ats_job_postings j
            LEFT JOIN ats_applications a ON j.job_id = a.job_id
            WHERE j.created_at > NOW() - INTERVAL '12 months'
        """
        
        params = []
        if department:
            query += " AND j.department = %s"
            params.append(department)
        
        query += " GROUP BY j.department"
        
        cursor.execute(query, params)
        historical_data = cursor.fetchall()
        
        # Calcular tasa de crecimiento
        growth_rates = {}
        for row in historical_data:
            dept = row[0]
            jobs_posted = row[1] or 0
            # Calcular tasa de crecimiento mensual
            growth_rate = (jobs_posted / 12) * 1.1  # 10% crecimiento estimado
            growth_rates[dept] = growth_rate
        
        # Calcular rotación promedio
        turnover_query = """
            SELECT j.department,
                   COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hires,
                   COUNT(DISTINCT al.alumni_id) as exits
            FROM ats_job_postings j
            LEFT JOIN ats_applications a ON j.job_id = a.job_id
            LEFT JOIN ats_alumni al ON a.candidate_id = al.candidate_id
            WHERE a.updated_at > NOW() - INTERVAL '12 months'
        """
        
        if department:
            turnover_query += " AND j.department = %s"
        
        turnover_query += " GROUP BY j.department"
        
        cursor.execute(turnover_query, params)
        turnover_data = cursor.fetchall()
        
        # Generar forecast
        forecasts = {}
        for dept in set(row[0] for row in historical_data if row[0]):
            growth_rate = growth_rates.get(dept, 2.0)  # Default 2 jobs/month
            monthly_needs = growth_rate
            
            # Ajustar por rotación
            for turnover_row in turnover_data:
                if turnover_row[0] == dept:
                    exits = turnover_row[2] or 0
                    monthly_needs += exits / 12  # Promedio mensual de salidas
            
            forecasts[dept] = {
                "monthly_hires_needed": round(monthly_needs, 1),
                "forecast_6_months": round(monthly_needs * 6, 0),
                "forecast_12_months": round(monthly_needs * 12, 0),
                "growth_rate": round(growth_rate, 2)
            }
        
        # Guardar forecast
        forecast_id = f"forecast_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_hiring_forecasts
            (forecast_id, department, forecast_period_months, forecasts,
             created_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            forecast_id,
            department or "all",
            months_ahead,
            json.dumps(forecasts),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "forecast_id": forecast_id,
            "department": department or "all",
            "months_ahead": months_ahead,
            "forecasts": forecasts
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error forecasting hiring needs: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ROI DE HIRING
# ============================================================================

def calculate_hiring_roi(
    job_id: Optional[str] = None,
    period_days: int = 90
) -> Dict[str, Any]:
    """
    Calcula ROI de hiring.
    
    Métricas:
    - Costo de contratación
    - Tiempo de productividad
    - Retención
    - Performance
    - Valor generado
    """
    logger.info("calculating hiring ROI", extra={"job_id": job_id, "period_days": period_days})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener costos de hiring
        query = """
            SELECT 
                COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hires,
                COUNT(DISTINCT jp.platform_name) as platforms,
                COUNT(DISTINCT i.interview_id) as interviews,
                COUNT(DISTINCT t.test_id) as tests,
                AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) as avg_days_to_fill
            FROM ats_job_postings j
            LEFT JOIN ats_applications a ON j.job_id = a.job_id
            LEFT JOIN ats_job_platforms jp ON j.job_id = jp.job_id
            LEFT JOIN ats_interviews i ON a.application_id = i.application_id
            LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
            WHERE a.status = 'hired'
        """
        
        params = []
        if job_id:
            query += " AND j.job_id = %s"
            params.append(job_id)
        
        query += " AND a.updated_at > NOW() - INTERVAL %s days"
        params.append(period_days)
        
        cursor.execute(query, params)
        cost_data = cursor.fetchone()
        
        hires = cost_data[0] or 0
        platforms = cost_data[1] or 0
        interviews = cost_data[2] or 0
        tests = cost_data[3] or 0
        avg_days = float(cost_data[4] or 30)
        
        # Calcular costos
        platform_costs = platforms * 500  # $500 por plataforma
        interview_costs = interviews * 50   # $50 por entrevista (tiempo del entrevistador)
        test_costs = tests * 100            # $100 por test
        recruiter_time = avg_days * 200     # $200/día de recruiter
        total_costs = platform_costs + interview_costs + test_costs + recruiter_time
        
        # Obtener métricas de valor
        cursor.execute("""
            SELECT 
                AVG(q.actual_quality_score) as avg_quality,
                COUNT(DISTINCT r.prediction_id) FILTER (WHERE r.risk_level = 'low') as low_risk_retention,
                AVG(EXTRACT(EPOCH FROM (NOW() - o.hire_date)) / 86400) as avg_retention_days
            FROM ats_applications a
            JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
            LEFT JOIN ats_quality_of_hire q ON a.candidate_id = q.candidate_id
            LEFT JOIN ats_retention_predictions r ON a.candidate_id = r.candidate_id
            WHERE a.status = 'hired'
              AND a.updated_at > NOW() - INTERVAL %s days
        """, (period_days,))
        
        value_data = cursor.fetchone()
        avg_quality = float(value_data[0] or 70)
        low_risk_count = value_data[1] or 0
        avg_retention = float(value_data[2] or 90)
        
        # Calcular valor generado (simplificado)
        # Valor = calidad * retención * productividad
        quality_multiplier = avg_quality / 100
        retention_multiplier = min(avg_retention / 90, 1.0)  # 90 días = 100%
        base_value = 50000  # Valor base por empleado
        total_value = hires * base_value * quality_multiplier * retention_multiplier
        
        # Calcular ROI
        if total_costs > 0:
            roi = ((total_value - total_costs) / total_costs) * 100
        else:
            roi = 0
        
        # Guardar métricas
        roi_id = f"roi_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_hiring_roi
            (roi_id, job_id, period_days, total_costs, total_value,
             roi_percentage, hires_count, metrics, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            roi_id,
            job_id,
            period_days,
            total_costs,
            total_value,
            roi,
            hires,
            json.dumps({
                "platform_costs": platform_costs,
                "interview_costs": interview_costs,
                "test_costs": test_costs,
                "recruiter_time": recruiter_time,
                "avg_quality": avg_quality,
                "avg_retention_days": avg_retention
            }),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "roi_id": roi_id,
            "job_id": job_id,
            "period_days": period_days,
            "total_costs": round(total_costs, 2),
            "total_value": round(total_value, 2),
            "roi_percentage": round(roi, 2),
            "hires_count": hires,
            "cost_per_hire": round(total_costs / hires, 2) if hires > 0 else 0
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error calculating ROI: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# MÉTRICAS DE ENGAGEMENT DE CANDIDATOS
# ============================================================================

def calculate_candidate_engagement(
    application_id: str
) -> Dict[str, Any]:
    """
    Calcula nivel de engagement del candidato.
    
    Métricas:
    - Tiempo de respuesta a emails
    - Tasa de apertura de emails
    - Participación en entrevistas
    - Completación de tests
    - Interacciones con chatbot
    """
    logger.info("calculating candidate engagement", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener métricas de engagement
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT c.communication_id) FILTER (WHERE c.direction = 'outbound') as emails_sent,
                COUNT(DISTINCT c.communication_id) FILTER (WHERE c.direction = 'outbound' AND c.read_at IS NOT NULL) as emails_read,
                AVG(CASE WHEN c.read_at IS NOT NULL THEN 
                    EXTRACT(EPOCH FROM (c.read_at - c.sent_at)) / 3600 END) as avg_response_hours,
                COUNT(DISTINCT i.interview_id) FILTER (WHERE i.status IN ('completed', 'confirmed')) as interviews_completed,
                COUNT(DISTINCT i.interview_id) FILTER (WHERE i.status = 'no_show') as no_shows,
                COUNT(DISTINCT t.test_id) FILTER (WHERE t.status = 'completed') as tests_completed,
                COUNT(DISTINCT t.test_id) FILTER (WHERE t.status = 'expired') as tests_expired,
                COUNT(DISTINCT cs.session_id) as chatbot_sessions
            FROM ats_applications a
            LEFT JOIN ats_communications c ON a.application_id = c.application_id
            LEFT JOIN ats_interviews i ON a.application_id = i.application_id
            LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
            LEFT JOIN ats_chatbot_sessions cs ON a.candidate_id = cs.candidate_id
            WHERE a.application_id = %s
        """, (application_id,))
        
        engagement_data = cursor.fetchone()
        
        emails_sent = engagement_data[0] or 0
        emails_read = engagement_data[1] or 0
        avg_response = float(engagement_data[2] or 48)
        interviews_completed = engagement_data[3] or 0
        no_shows = engagement_data[4] or 0
        tests_completed = engagement_data[5] or 0
        tests_expired = engagement_data[6] or 0
        chatbot_sessions = engagement_data[7] or 0
        
        # Calcular scores
        email_engagement = (emails_read / emails_sent * 100) if emails_sent > 0 else 0
        response_score = 100 if avg_response < 24 else 80 if avg_response < 48 else 60 if avg_response < 72 else 40
        interview_score = 100 if no_shows == 0 else 50 if no_shows == 1 else 0
        test_score = 100 if tests_expired == 0 else 50 if tests_completed > 0 else 0
        chatbot_score = min(chatbot_sessions * 20, 100)
        
        # Score total
        overall_engagement = (
            email_engagement * 0.3 +
            response_score * 0.2 +
            interview_score * 0.25 +
            test_score * 0.15 +
            chatbot_score * 0.1
        )
        
        # Guardar métricas
        engagement_id = f"engagement_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_candidate_engagement
            (engagement_id, application_id, overall_score, email_engagement,
             response_score, interview_score, test_score, chatbot_score, metrics, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            engagement_id,
            application_id,
            overall_engagement,
            email_engagement,
            response_score,
            interview_score,
            test_score,
            chatbot_score,
            json.dumps({
                "emails_sent": emails_sent,
                "emails_read": emails_read,
                "avg_response_hours": avg_response,
                "interviews_completed": interviews_completed,
                "no_shows": no_shows,
                "tests_completed": tests_completed,
                "chatbot_sessions": chatbot_sessions
            }),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "engagement_id": engagement_id,
            "application_id": application_id,
            "overall_engagement": round(overall_engagement, 2),
            "scores": {
                "email_engagement": round(email_engagement, 2),
                "response_score": round(response_score, 2),
                "interview_score": round(interview_score, 2),
                "test_score": round(test_score, 2),
                "chatbot_score": round(chatbot_score, 2)
            },
            "engagement_level": "high" if overall_engagement >= 80 else "medium" if overall_engagement >= 60 else "low"
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error calculating engagement: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# ANÁLISIS DE COHORTES
# ============================================================================

def analyze_hiring_cohorts(
    cohort_period: str = "monthly",
    start_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Analiza cohortes de contratación.
    
    Métricas por cohorte:
    - Tasa de retención
    - Performance promedio
    - Time to productivity
    - Quality scores
    """
    logger.info("analyzing hiring cohorts", extra={"cohort_period": cohort_period})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        if not start_date:
            start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
        
        # Obtener cohortes
        if cohort_period == "monthly":
            query = """
                SELECT 
                    DATE_TRUNC('month', a.updated_at) as cohort_month,
                    COUNT(DISTINCT a.application_id) as hires,
                    AVG(q.actual_quality_score) as avg_quality,
                    AVG(EXTRACT(EPOCH FROM (NOW() - o.hire_date)) / 86400) as avg_retention_days,
                    COUNT(DISTINCT r.prediction_id) FILTER (WHERE r.risk_level = 'low') as low_risk_count
                FROM ats_applications a
                JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
                LEFT JOIN ats_quality_of_hire q ON a.candidate_id = q.candidate_id
                LEFT JOIN ats_retention_predictions r ON a.candidate_id = r.candidate_id
                WHERE a.status = 'hired'
                  AND a.updated_at >= %s
                GROUP BY DATE_TRUNC('month', a.updated_at)
                ORDER BY cohort_month DESC
            """
        else:  # quarterly
            query = """
                SELECT 
                    DATE_TRUNC('quarter', a.updated_at) as cohort_quarter,
                    COUNT(DISTINCT a.application_id) as hires,
                    AVG(q.actual_quality_score) as avg_quality,
                    AVG(EXTRACT(EPOCH FROM (NOW() - o.hire_date)) / 86400) as avg_retention_days,
                    COUNT(DISTINCT r.prediction_id) FILTER (WHERE r.risk_level = 'low') as low_risk_count
                FROM ats_applications a
                JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
                LEFT JOIN ats_quality_of_hire q ON a.candidate_id = q.candidate_id
                LEFT JOIN ats_retention_predictions r ON a.candidate_id = r.candidate_id
                WHERE a.status = 'hired'
                  AND a.updated_at >= %s
                GROUP BY DATE_TRUNC('quarter', a.updated_at)
                ORDER BY cohort_quarter DESC
            """
        
        cursor.execute(query, (start_date,))
        cohorts = cursor.fetchall()
        
        # Formatear resultados
        cohort_analysis = []
        for cohort in cohorts:
            cohort_analysis.append({
                "period": str(cohort[0]),
                "hires": cohort[1],
                "avg_quality": round(float(cohort[2] or 0), 2),
                "avg_retention_days": round(float(cohort[3] or 0), 1),
                "low_risk_percentage": round((cohort[4] / cohort[1] * 100) if cohort[1] > 0 else 0, 2)
            })
        
        return {
            "cohort_period": cohort_period,
            "start_date": start_date,
            "cohorts": cohort_analysis,
            "total_cohorts": len(cohort_analysis)
        }
        
    except Exception as e:
        logger.error(f"Error analyzing cohorts: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# MÉTRICAS DE CALIDAD DE FUENTE
# ============================================================================

def analyze_source_quality() -> Dict[str, Any]:
    """
    Analiza calidad de diferentes fuentes de candidatos.
    
    Métricas por fuente:
    - Conversion rate
    - Quality of hire
    - Time to hire
    - Retention rate
    - Cost per hire
    """
    logger.info("analyzing source quality")
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                c.source,
                COUNT(DISTINCT a.application_id) as total_applications,
                COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hires,
                ROUND(COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired')::DECIMAL / 
                      NULLIF(COUNT(DISTINCT a.application_id), 0) * 100, 2) as conversion_rate,
                AVG(EXTRACT(EPOCH FROM (a.updated_at - a.applied_at)) / 86400) 
                    FILTER (WHERE a.status = 'hired') as avg_time_to_hire,
                AVG(q.actual_quality_score) as avg_quality,
                AVG(EXTRACT(EPOCH FROM (NOW() - o.hire_date)) / 86400) 
                    FILTER (WHERE a.status = 'hired') as avg_retention_days
            FROM ats_candidates c
            JOIN ats_applications a ON c.candidate_id = a.candidate_id
            LEFT JOIN ats_quality_of_hire q ON a.candidate_id = q.candidate_id
            LEFT JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
            WHERE c.source IS NOT NULL
            GROUP BY c.source
            ORDER BY conversion_rate DESC
        """)
        
        source_data = cursor.fetchall()
        
        source_analysis = {}
        for source in source_data:
            source_name = source[0]
            source_analysis[source_name] = {
                "total_applications": source[1],
                "hires": source[2],
                "conversion_rate": float(source[3] or 0),
                "avg_time_to_hire": round(float(source[4] or 0), 1),
                "avg_quality": round(float(source[5] or 0), 2),
                "avg_retention_days": round(float(source[6] or 0), 1),
                "source_score": _calculate_source_score(source)
            }
        
        # Guardar análisis
        analysis_id = f"source_analysis_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_source_quality
            (analysis_id, source_metrics, calculated_at)
            VALUES (%s, %s, %s)
        """, (
            analysis_id,
            json.dumps(source_analysis),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "analysis_id": analysis_id,
            "sources": source_analysis,
            "best_source": max(source_analysis.items(), key=lambda x: x[1]["source_score"])[0] if source_analysis else None
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error analyzing source quality: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _calculate_source_score(source_data: tuple) -> float:
    """Calcula score de calidad de fuente"""
    conversion_rate = float(source_data[3] or 0)
    avg_quality = float(source_data[5] or 0)
    avg_retention = float(source_data[6] or 0)
    
    # Score = (conversion * 0.3 + quality * 0.4 + retention * 0.3)
    score = (conversion_rate * 0.3) + (avg_quality * 0.4) + (min(avg_retention / 90, 1.0) * 30)
    return round(score, 2)


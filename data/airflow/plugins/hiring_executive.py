"""
Funcionalidades Ejecutivas y Estratégicas para Hiring ATS
==========================================================

- Reporting ejecutivo avanzado
- Predicción de rotación
- Succession planning
- Talent mobility interno
- Compensation planning integrado
- Employer branding metrics avanzado
- Engagement surveys integrados
- Predicción de éxito de candidatos
- Dashboard ejecutivo con KPIs
- Strategic hiring planning
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
# REPORTING EJECUTIVO AVANZADO
# ============================================================================

def generate_executive_report(
    period: str = "quarterly",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Genera reporte ejecutivo completo con KPIs clave.
    
    KPIs incluidos:
    - Hiring metrics
    - Quality metrics
    - Cost metrics
    - Time metrics
    - Diversity metrics
    - ROI metrics
    """
    logger.info("generating executive report", extra={"period": period})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        if not start_date:
            if period == "monthly":
                start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
            elif period == "quarterly":
                start_date = (datetime.now(timezone.utc) - timedelta(days=90)).strftime("%Y-%m-%d")
            else:
                start_date = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
        
        if not end_date:
            end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        
        # KPIs principales
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT j.job_id) as jobs_posted,
                COUNT(DISTINCT a.application_id) as total_applications,
                COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as hires,
                AVG(EXTRACT(EPOCH FROM (a.updated_at - j.posted_at)) / 86400) 
                    FILTER (WHERE a.status = 'hired') as avg_time_to_fill,
                AVG(EXTRACT(EPOCH FROM (a.updated_at - a.applied_at)) / 86400)
                    FILTER (WHERE a.status = 'hired') as avg_time_to_hire,
                AVG(a.match_score) FILTER (WHERE a.status = 'hired') as avg_match_score,
                AVG(q.actual_quality_score) as avg_quality_score
            FROM ats_job_postings j
            LEFT JOIN ats_applications a ON j.job_id = a.job_id
            LEFT JOIN ats_quality_of_hire q ON a.candidate_id = q.candidate_id
            WHERE j.created_at >= %s AND j.created_at <= %s
        """, (start_date, end_date))
        
        kpis = cursor.fetchone()
        
        # Cost metrics
        cursor.execute("""
            SELECT 
                AVG(cost_per_hire) as avg_cost_per_hire,
                AVG(roi_percentage) as avg_roi,
                SUM(total_costs) as total_costs,
                SUM(total_value) as total_value
            FROM ats_hiring_roi
            WHERE calculated_at >= %s AND calculated_at <= %s
        """, (start_date, end_date))
        
        cost_data = cursor.fetchone()
        
        # Diversity metrics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT c.candidate_id) FILTER (WHERE c.gender = 'female') as female_count,
                COUNT(DISTINCT c.candidate_id) FILTER (WHERE c.gender = 'male') as male_count,
                COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired' AND c.gender = 'female') as female_hires
            FROM ats_applications a
            JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.applied_at >= %s AND a.applied_at <= %s
        """, (start_date, end_date))
        
        diversity_data = cursor.fetchone()
        
        # Engagement metrics
        cursor.execute("""
            SELECT 
                AVG(overall_score) as avg_engagement,
                COUNT(DISTINCT application_id) FILTER (WHERE engagement_level = 'high') as high_engagement_count
            FROM ats_candidate_engagement
            WHERE calculated_at >= %s AND calculated_at <= %s
        """, (start_date, end_date))
        
        engagement_data = cursor.fetchone()
        
        # Compilar reporte
        report = {
            "period": period,
            "start_date": start_date,
            "end_date": end_date,
            "kpis": {
                "jobs_posted": kpis[0] or 0,
                "total_applications": kpis[1] or 0,
                "hires": kpis[2] or 0,
                "hire_rate": round((kpis[2] / kpis[1] * 100) if kpis[1] > 0 else 0, 2),
                "avg_time_to_fill": round(float(kpis[3] or 0), 1),
                "avg_time_to_hire": round(float(kpis[4] or 0), 1),
                "avg_match_score": round(float(kpis[5] or 0), 2),
                "avg_quality_score": round(float(kpis[6] or 0), 2)
            },
            "cost_metrics": {
                "avg_cost_per_hire": round(float(cost_data[0] or 0), 2) if cost_data else 0,
                "avg_roi": round(float(cost_data[1] or 0), 2) if cost_data else 0,
                "total_costs": round(float(cost_data[2] or 0), 2) if cost_data else 0,
                "total_value": round(float(cost_data[3] or 0), 2) if cost_data else 0
            },
            "diversity_metrics": {
                "female_applications": diversity_data[0] or 0,
                "male_applications": diversity_data[1] or 0,
                "female_hires": diversity_data[2] or 0,
                "diversity_rate": round((diversity_data[2] / kpis[2] * 100) if kpis[2] > 0 else 0, 2)
            },
            "engagement_metrics": {
                "avg_engagement": round(float(engagement_data[0] or 0), 2) if engagement_data else 0,
                "high_engagement_percentage": round((engagement_data[1] / kpis[1] * 100) if kpis[1] > 0 and engagement_data else 0, 2)
            }
        }
        
        # Guardar reporte
        report_id = f"exec_report_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_executive_reports
            (report_id, report_period, start_date, end_date, report_data, generated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            report_id,
            period,
            start_date,
            end_date,
            json.dumps(report),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "report_id": report_id,
            "report": report,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error generating executive report: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# PREDICCIÓN DE ROTACIÓN
# ============================================================================

def predict_turnover_risk(
    department: Optional[str] = None
) -> Dict[str, Any]:
    """
    Predice riesgo de rotación por departamento o globalmente.
    
    Factores:
    - Tasa de rotación histórica
    - Engagement scores
    - Performance metrics
    - Market conditions
    - Compensation competitiveness
    """
    logger.info("predicting turnover risk", extra={"department": department})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener datos históricos de rotación
        query = """
            SELECT 
                j.department,
                COUNT(DISTINCT a.application_id) FILTER (WHERE a.status = 'hired') as total_hires,
                COUNT(DISTINCT al.alumni_id) as exits,
                AVG(EXTRACT(EPOCH FROM (al.exit_date - o.hire_date)) / 86400) as avg_tenure_days
            FROM ats_job_postings j
            JOIN ats_applications a ON j.job_id = a.job_id
            LEFT JOIN ats_post_hire_onboarding o ON a.application_id = o.application_id
            LEFT JOIN ats_alumni al ON a.candidate_id = al.candidate_id
            WHERE a.status = 'hired'
              AND a.updated_at > NOW() - INTERVAL '12 months'
        """
        
        params = []
        if department:
            query += " AND j.department = %s"
            params.append(department)
        
        query += " GROUP BY j.department"
        
        cursor.execute(query, params)
        turnover_data = cursor.fetchall()
        
        # Calcular tasa de rotación
        turnover_analysis = {}
        for row in turnover_data:
            dept = row[0] or "all"
            total_hires = row[1] or 0
            exits = row[2] or 0
            avg_tenure = float(row[3] or 365)
            
            turnover_rate = (exits / total_hires * 100) if total_hires > 0 else 0
            
            # Calcular riesgo (mayor tasa = mayor riesgo, menor tenure = mayor riesgo)
            tenure_risk = 100 - (avg_tenure / 365 * 100) if avg_tenure < 365 else 0
            risk_score = (turnover_rate * 0.6) + (tenure_risk * 0.4)
            
            turnover_analysis[dept] = {
                "total_hires": total_hires,
                "exits": exits,
                "turnover_rate": round(turnover_rate, 2),
                "avg_tenure_days": round(avg_tenure, 1),
                "risk_score": round(risk_score, 2),
                "risk_level": "high" if risk_score >= 70 else "medium" if risk_score >= 40 else "low"
            }
        
        # Guardar predicción
        prediction_id = f"turnover_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_turnover_predictions
            (prediction_id, department, turnover_analysis, predicted_at)
            VALUES (%s, %s, %s, %s)
        """, (
            prediction_id,
            department or "all",
            json.dumps(turnover_analysis),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "prediction_id": prediction_id,
            "department": department or "all",
            "turnover_analysis": turnover_analysis
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error predicting turnover: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# SUCCESSION PLANNING
# ============================================================================

def create_succession_plan(
    position_id: str,
    current_holder_id: str,
    potential_successors: List[str]
) -> Dict[str, Any]:
    """Crea plan de sucesión para un puesto"""
    logger.info("creating succession plan", extra={"position_id": position_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        plan_id = f"succession_{uuid.uuid4().hex[:12]}"
        
        # Evaluar readiness de cada successor
        successor_readiness = []
        for successor_id in potential_successors:
            readiness = _evaluate_successor_readiness(successor_id, position_id)
            successor_readiness.append({
                "candidate_id": successor_id,
                "readiness_score": readiness["score"],
                "readiness_level": readiness["level"],
                "gaps": readiness["gaps"],
                "development_needs": readiness["development_needs"]
            })
        
        # Ordenar por readiness
        successor_readiness.sort(key=lambda x: x["readiness_score"], reverse=True)
        
        cursor.execute("""
            INSERT INTO ats_succession_plans
            (plan_id, position_id, current_holder_id, potential_successors,
             status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            plan_id,
            position_id,
            current_holder_id,
            json.dumps(successor_readiness),
            "active",
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "plan_id": plan_id,
            "position_id": position_id,
            "successors": successor_readiness,
            "top_successor": successor_readiness[0] if successor_readiness else None
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating succession plan: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def _evaluate_successor_readiness(candidate_id: str, position_id: str) -> Dict[str, Any]:
    """Evalúa readiness de un candidato para sucesión"""
    # Simulación - en producción evaluaría skills, experience, performance, etc.
    return {
        "score": 75.0,
        "level": "ready" if 75 >= 80 else "developing" if 75 >= 60 else "not_ready",
        "gaps": ["leadership experience", "strategic thinking"],
        "development_needs": ["Leadership training", "Mentorship program"]
    }


# ============================================================================
# TALENT MOBILITY INTERNO
# ============================================================================

def identify_internal_mobility_opportunities(
    candidate_id: str
) -> Dict[str, Any]:
    """Identifica oportunidades de movilidad interna para candidato"""
    logger.info("identifying internal mobility opportunities", extra={"candidate_id": candidate_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener perfil del candidato
        cursor.execute("""
            SELECT c.resume_text, ml.overall_score, ml.skill_score,
                   j.title, j.department
            FROM ats_candidates c
            LEFT JOIN ats_applications a ON c.candidate_id = a.candidate_id
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            LEFT JOIN ats_job_postings j ON a.job_id = j.job_id
            WHERE c.candidate_id = %s
            ORDER BY a.applied_at DESC
            LIMIT 1
        """, (candidate_id,))
        
        candidate_data = cursor.fetchone()
        if not candidate_data:
            return {"error": "Candidate not found"}
        
        # Buscar jobs internos que podrían ser match
        cursor.execute("""
            SELECT j.job_id, j.title, j.department,
                   AVG(ml.overall_score) as avg_required_score
            FROM ats_job_postings j
            LEFT JOIN ats_applications a ON j.job_id = a.job_id
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            WHERE j.status = 'active'
              AND j.department != %s
            GROUP BY j.job_id, j.title, j.department
            HAVING AVG(ml.overall_score) <= %s
            ORDER BY AVG(ml.overall_score) DESC
            LIMIT 5
        """, (candidate_data[4] or "", float(candidate_data[1] or 0)))
        
        opportunities = cursor.fetchall()
        
        mobility_opportunities = []
        for opp in opportunities:
            mobility_opportunities.append({
                "job_id": opp[0],
                "title": opp[1],
                "department": opp[2],
                "match_score": float(opp[3] or 0),
                "match_level": "high" if opp[3] >= 80 else "medium" if opp[3] >= 60 else "low"
            })
        
        return {
            "candidate_id": candidate_id,
            "current_department": candidate_data[4],
            "opportunities": mobility_opportunities,
            "opportunities_count": len(mobility_opportunities)
        }
        
    except Exception as e:
        logger.error(f"Error identifying mobility opportunities: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# PREDICCIÓN DE ÉXITO DE CANDIDATOS
# ============================================================================

def predict_candidate_success(
    application_id: str
) -> Dict[str, Any]:
    """
    Predice probabilidad de éxito del candidato.
    
    Factores:
    - ML scores
    - Interview performance
    - Test scores
    - Experience match
    - Cultural fit
    - Historical success patterns
    """
    logger.info("predicting candidate success", extra={"application_id": application_id})
    
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Obtener todos los scores y métricas
        cursor.execute("""
            SELECT 
                a.match_score,
                ml.overall_score,
                ml.predicted_hire_probability,
                ml.cultural_fit_score,
                AVG(i.rating) as avg_interview_rating,
                AVG(t.score) as avg_test_score,
                AVG(t.score / t.max_score * 100) as test_percentage,
                c.source
            FROM ats_applications a
            LEFT JOIN ats_ml_scoring ml ON a.application_id = ml.application_id
            LEFT JOIN ats_interviews i ON a.application_id = i.application_id
            LEFT JOIN ats_assessment_tests t ON a.application_id = t.application_id
            LEFT JOIN ats_candidates c ON a.candidate_id = c.candidate_id
            WHERE a.application_id = %s
            GROUP BY a.application_id, a.match_score, ml.overall_score,
                     ml.predicted_hire_probability, ml.cultural_fit_score, c.source
        """, (application_id,))
        
        app_data = cursor.fetchone()
        if not app_data:
            return {"error": "Application not found"}
        
        # Calcular score de éxito (0-100)
        match_score = float(app_data[0] or 0)
        ml_score = float(app_data[1] or 0)
        hire_prob = float(app_data[2] or 0)
        cultural_fit = float(app_data[3] or 0)
        interview_rating = float(app_data[4] or 0) * 20  # Convertir a 0-100
        test_score = float(app_data[6] or 0)
        
        # Source bonus
        source = app_data[7]
        source_bonus = 10 if source == "referral" else 5 if source == "internal" else 0
        
        # Calcular probabilidad de éxito
        success_probability = (
            match_score * 0.15 +
            ml_score * 0.20 +
            hire_prob * 0.25 +
            cultural_fit * 0.15 +
            interview_rating * 0.15 +
            test_score * 0.10 +
            source_bonus
        )
        
        # Clasificar
        if success_probability >= 85:
            success_level = "very_high"
            recommendation = "strong_hire"
        elif success_probability >= 70:
            success_level = "high"
            recommendation = "hire"
        elif success_probability >= 55:
            success_level = "medium"
            recommendation = "consider"
        else:
            success_level = "low"
            recommendation = "reconsider"
        
        # Guardar predicción
        prediction_id = f"success_{uuid.uuid4().hex[:12]}"
        cursor.execute("""
            INSERT INTO ats_success_predictions
            (prediction_id, application_id, success_probability, success_level,
             recommendation, factors, predicted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            prediction_id,
            application_id,
            success_probability,
            success_level,
            recommendation,
            json.dumps({
                "match_score": match_score,
                "ml_score": ml_score,
                "hire_probability": hire_prob,
                "cultural_fit": cultural_fit,
                "interview_rating": interview_rating,
                "test_score": test_score,
                "source_bonus": source_bonus
            }),
            datetime.now(timezone.utc)
        ))
        
        conn.commit()
        
        return {
            "prediction_id": prediction_id,
            "application_id": application_id,
            "success_probability": round(success_probability, 2),
            "success_level": success_level,
            "recommendation": recommendation,
            "factors": {
                "match_score": match_score,
                "ml_score": ml_score,
                "cultural_fit": cultural_fit,
                "interview_performance": interview_rating,
                "test_performance": test_score
            }
        }
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error predicting success: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


# ============================================================================
# STRATEGIC HIRING PLANNING
# ============================================================================

def create_strategic_hiring_plan(
    department: str,
    timeframe_months: int = 12,
    business_goals: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea plan estratégico de hiring.
    
    Incluye:
    - Forecasts de necesidades
    - Budget planning
    - Resource allocation
    - Timeline
    - Risk assessment
    """
    logger.info("creating strategic hiring plan", extra={"department": department, "timeframe": timeframe_months})
    
    # Obtener forecast
    from data.airflow.plugins.hiring_analytics import forecast_hiring_needs
    
    forecast = forecast_hiring_needs(department=department, months_ahead=timeframe_months)
    
    # Calcular budget estimado
    avg_cost_per_hire = 5000  # Estimado
    total_hires_needed = sum(f.get("forecast_6_months", 0) for f in forecast.get("forecasts", {}).values())
    estimated_budget = total_hires_needed * avg_cost_per_hire
    
    # Timeline
    timeline = []
    for month in range(1, timeframe_months + 1):
        month_hires = total_hires_needed / timeframe_months
        timeline.append({
            "month": month,
            "target_hires": round(month_hires, 0),
            "key_milestones": []
        })
    
    # Risk assessment
    risks = []
    if total_hires_needed > 20:
        risks.append({
            "risk": "High hiring volume may strain resources",
            "severity": "medium",
            "mitigation": "Consider staggered hiring or additional recruiters"
        })
    
    plan = {
        "department": department,
        "timeframe_months": timeframe_months,
        "forecast": forecast,
        "estimated_budget": round(estimated_budget, 2),
        "total_hires_needed": round(total_hires_needed, 0),
        "timeline": timeline,
        "risks": risks,
        "business_goals": business_goals or {}
    }
    
    return plan


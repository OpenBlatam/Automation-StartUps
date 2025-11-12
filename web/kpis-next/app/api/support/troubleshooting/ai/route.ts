"""
API Endpoints para Predicción y Recomendaciones Inteligentes
"""

import json
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from pydantic import BaseModel, EmailStr
import psycopg2
from psycopg2.extras import RealDictCursor

from data.integrations.support_troubleshooting_ai import (
    TroubleshootingPredictor,
    TroubleshootingRecommender,
    TroubleshootingLearningEngine
)

router = APIRouter(prefix="/api/support/troubleshooting/ai", tags=["troubleshooting-ai"])


def get_db_connection():
    """Obtener conexión a base de datos"""
    # TODO: Implementar pool de conexiones
    return psycopg2.connect(
        host="localhost",
        database="your_db",
        user="your_user",
        password="your_password"
    )


class PredictionRequest(BaseModel):
    customer_email: EmailStr
    context: Optional[dict] = None


class RecommendationRequest(BaseModel):
    problem_description: str
    customer_email: Optional[EmailStr] = None
    context: Optional[dict] = None


@router.post("/predict")
async def predict_next_problem(
    request: PredictionRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Predice el siguiente problema probable del usuario
    """
    # TODO: Validar autenticación
    
    db = get_db_connection()
    try:
        predictor = TroubleshootingPredictor(db)
        prediction = predictor.predict_next_problem(
            request.customer_email,
            request.context
        )
        
        if not prediction:
            return {
                "prediction": None,
                "message": "No hay suficiente historial para hacer una predicción"
            }
        
        # Registrar predicción en BD
        cursor = db.cursor()
        cursor.execute("""
            SELECT register_prediction(
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """, (
            request.customer_email,
            prediction.problem_id,
            prediction.problem_title,
            prediction.probability,
            prediction.confidence,
            json.dumps(prediction.reasons),
            json.dumps(prediction.recommended_actions),
            prediction.estimated_impact
        ))
        
        prediction_id = cursor.fetchone()[0]
        db.commit()
        cursor.close()
        
        return {
            "prediction_id": str(prediction_id),
            "problem_id": prediction.problem_id,
            "problem_title": prediction.problem_title,
            "probability": prediction.probability,
            "confidence": prediction.confidence,
            "reasons": prediction.reasons,
            "recommended_actions": prediction.recommended_actions,
            "estimated_impact": prediction.estimated_impact
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/recommendations/{customer_email}")
async def get_proactive_recommendations(
    customer_email: EmailStr,
    authorization: Optional[str] = Header(None)
):
    """
    Obtiene recomendaciones proactivas para el usuario
    """
    db = get_db_connection()
    try:
        predictor = TroubleshootingPredictor(db)
        recommendations = predictor.get_proactive_recommendations(customer_email)
        
        return {
            "customer_email": customer_email,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/recommend-solutions")
async def recommend_solutions(
    request: RecommendationRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Recomienda soluciones basadas en descripción y contexto
    """
    db = get_db_connection()
    try:
        recommender = TroubleshootingRecommender(db)
        recommendations = recommender.recommend_solutions(
            request.problem_description,
            request.customer_email,
            request.context
        )
        
        return {
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/personalized-guide/{problem_id}/{customer_email}")
async def get_personalized_guide(
    problem_id: str,
    customer_email: EmailStr,
    authorization: Optional[str] = Header(None)
):
    """
    Obtiene una guía personalizada basada en el historial del usuario
    """
    db = get_db_connection()
    try:
        recommender = TroubleshootingRecommender(db)
        guide = recommender.get_personalized_guide(problem_id, customer_email)
        
        if not guide:
            return {
                "personalized": False,
                "message": "No hay suficiente historial para personalizar la guía"
            }
        
        return guide
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/step-effectiveness/{problem_id}")
async def get_step_effectiveness(
    problem_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Analiza la efectividad de cada paso de una guía
    """
    db = get_db_connection()
    try:
        engine = TroubleshootingLearningEngine(db)
        analysis = engine.analyze_step_effectiveness(problem_id)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"No se encontraron datos para el problema {problem_id}"
            )
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/improvement-suggestions/{problem_id}")
async def get_improvement_suggestions(
    problem_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Obtiene sugerencias de mejora para una guía
    """
    db = get_db_connection()
    try:
        engine = TroubleshootingLearningEngine(db)
        suggestions = engine.suggest_guide_improvements(problem_id)
        
        return {
            "problem_id": problem_id,
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.post("/verify-prediction/{prediction_id}")
async def verify_prediction(
    prediction_id: str,
    actual_problem_id: str,
    authorization: Optional[str] = Header(None)
):
    """
    Verifica si una predicción fue correcta
    """
    db = get_db_connection()
    try:
        cursor = db.cursor()
        cursor.execute("""
            SELECT verify_prediction(%s::UUID, %s)
        """, (prediction_id, actual_problem_id))
        
        was_correct = cursor.fetchone()[0]
        db.commit()
        cursor.close()
        
        return {
            "prediction_id": prediction_id,
            "was_correct": was_correct,
            "actual_problem_id": actual_problem_id
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()


@router.get("/user-patterns/{customer_email}")
async def get_user_patterns(
    customer_email: EmailStr,
    authorization: Optional[str] = Header(None)
):
    """
    Obtiene patrones de comportamiento del usuario
    """
    db = get_db_connection()
    try:
        predictor = TroubleshootingPredictor(db)
        pattern = predictor.analyze_user_history(customer_email)
        
        if not pattern:
            return {
                "customer_email": customer_email,
                "pattern": None,
                "message": "No hay suficiente historial para analizar patrones"
            }
        
        return {
            "customer_email": customer_email,
            "pattern": {
                "common_problems": pattern.common_problems,
                "avg_resolution_time": pattern.avg_resolution_time,
                "success_rate": pattern.success_rate,
                "escalation_rate": pattern.escalation_rate
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()




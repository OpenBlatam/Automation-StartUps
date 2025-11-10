"""
Análisis predictivo para descripciones de puesto.

Características:
- Predicción de éxito de descripciones
- Estimación de aplicaciones esperadas
- Predicción de tiempo de contratación
- Recomendaciones de optimización
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def predict_job_success(**context) -> Dict:
    """Predice el éxito de una descripción de puesto."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener datos históricos similares
        query = """
            SELECT 
                jd.role,
                jd.level,
                jd.department,
                COUNT(DISTINCT jp.posting_id) as postings,
                COUNT(DISTINCT ja.application_id) as applications,
                AVG(ja.ai_score) as avg_score,
                COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END) as qualified
            FROM job_descriptions jd
            LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
            LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
            WHERE jd.role = (SELECT role FROM job_descriptions WHERE job_description_id = %s)
                AND jd.job_description_id != %s
            GROUP BY jd.role, jd.level, jd.department
        """
        
        result = pg_hook.get_first(query, parameters=(job_description_id, job_description_id))
        
        if result:
            # Basado en datos históricos
            historical_apps = result[4] or 0
            historical_qualified = result[6] or 0
            
            # Predicción simple (en producción, usar modelo ML)
            predicted_applications = int(historical_apps * 0.9)  # 90% del histórico
            predicted_qualified = int(historical_qualified * 0.9)
            predicted_time_to_hire = 30  # días estimados
            
            # Score de éxito (0-100)
            success_score = min(100, (
                (predicted_applications / 50) * 30 +  # Aplicaciones esperadas
                (predicted_qualified / predicted_applications * 100 if predicted_applications > 0 else 0) * 0.4 +  # Tasa de calificación
                30  # Base score
            ))
            
            prediction = {
                "job_description_id": job_description_id,
                "predicted_applications": predicted_applications,
                "predicted_qualified": predicted_qualified,
                "predicted_time_to_hire_days": predicted_time_to_hire,
                "success_score": round(success_score, 2),
                "confidence": 0.7,
                "based_on_historical_data": True,
                "prediction_date": datetime.utcnow().isoformat()
            }
            
            # Guardar predicción
            pg_hook.run("""
                INSERT INTO job_predictions (
                    job_description_id, prediction_data, created_at
                ) VALUES (%s, %s, NOW())
                ON CONFLICT (job_description_id) DO UPDATE SET
                    prediction_data = EXCLUDED.prediction_data,
                    updated_at = NOW()
            """, parameters=(job_description_id, json.dumps(prediction)))
            
            logger.info(f"Predicción generada: {predicted_applications} aplicaciones esperadas")
            return prediction
        else:
            # Sin datos históricos - predicción conservadora
            prediction = {
                "job_description_id": job_description_id,
                "predicted_applications": 10,
                "predicted_qualified": 3,
                "predicted_time_to_hire_days": 45,
                "success_score": 50,
                "confidence": 0.3,
                "based_on_historical_data": False,
                "prediction_date": datetime.utcnow().isoformat()
            }
            
            return prediction
        
    except Exception as e:
        logger.error(f"Error generando predicción: {str(e)}")
        raise


def generate_optimization_recommendations(**context) -> List[Dict]:
    """Genera recomendaciones de optimización basadas en predicciones."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener predicción
        query = """
            SELECT prediction_data FROM job_predictions
            WHERE job_description_id = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            return []
        
        prediction = json.loads(result[0])
        recommendations = []
        
        # Generar recomendaciones basadas en predicción
        if prediction.get('success_score', 0) < 60:
            recommendations.append({
                "type": "low_success_score",
                "priority": "high",
                "message": "El score de éxito predicho es bajo. Considera optimizar la descripción.",
                "suggestions": [
                    "Revisar palabras clave",
                    "Mejorar el tono y sentimiento",
                    "Agregar más detalles sobre beneficios"
                ]
            })
        
        if prediction.get('predicted_applications', 0) < 15:
            recommendations.append({
                "type": "low_applications",
                "priority": "medium",
                "message": "Se esperan pocas aplicaciones. Considera publicar en más portales.",
                "suggestions": [
                    "Publicar en LinkedIn, Indeed y Glassdoor",
                    "Compartir en redes sociales",
                    "Considerar anuncios pagados"
                ]
            })
        
        if prediction.get('predicted_time_to_hire_days', 0) > 40:
            recommendations.append({
                "type": "long_time_to_hire",
                "priority": "medium",
                "message": "El tiempo estimado de contratación es alto.",
                "suggestions": [
                    "Optimizar el proceso de selección",
                    "Mejorar la descripción para atraer más candidatos",
                    "Considerar agencias de reclutamiento"
                ]
            })
        
        # Guardar recomendaciones
        pg_hook.run("""
            INSERT INTO job_recommendations (
                job_description_id, recommendations, created_at
            ) VALUES (%s, %s, NOW())
            ON CONFLICT (job_description_id) DO UPDATE SET
                recommendations = EXCLUDED.recommendations,
                updated_at = NOW()
        """, parameters=(job_description_id, json.dumps(recommendations)))
        
        logger.info(f"Generadas {len(recommendations)} recomendaciones")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generando recomendaciones: {str(e)}")
        return []


# DAG para análisis predictivo
with DAG(
    'job_description_predictive_analytics',
    default_args=default_args,
    description='Análisis predictivo para descripciones de puesto',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'predictive', 'analytics', 'ml'],
) as dag:
    
    predict_success = PythonOperator(
        task_id='predict_job_success',
        python_callable=predict_job_success,
    )
    
    generate_recommendations = PythonOperator(
        task_id='generate_optimization_recommendations',
        python_callable=generate_optimization_recommendations,
    )
    
    predict_success >> generate_recommendations


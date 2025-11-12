"""
Sistema de feedback de candidatos para descripciones de puesto.

Características:
- Recolección de feedback
- Análisis de sentimiento
- Mejoras sugeridas
- Métricas de satisfacción
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def collect_candidate_feedback(**context) -> Dict:
    """Recolecta feedback de candidatos."""
    application_id = context['dag_run'].conf.get('application_id')
    feedback_data = context['dag_run'].conf.get('feedback', {})
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Guardar feedback
        pg_hook.run("""
            INSERT INTO candidate_feedback (
                application_id, feedback_data, created_at
            ) VALUES (%s, %s, NOW())
        """, parameters=(application_id, json.dumps(feedback_data)))
        
        # Analizar sentimiento del feedback
        sentiment = analyze_feedback_sentiment(feedback_data.get('comments', ''))
        
        # Guardar análisis
        pg_hook.run("""
            UPDATE candidate_feedback
            SET sentiment_score = %s, sentiment_category = %s
            WHERE application_id = %s
        """, parameters=(
            sentiment['score'],
            sentiment['category'],
            application_id
        ))
        
        logger.info(f"Feedback recolectado para aplicación {application_id}")
        return {"status": "collected", "sentiment": sentiment}
        
    except Exception as e:
        logger.error(f"Error recolectando feedback: {str(e)}")
        raise


def analyze_feedback_sentiment(text: str) -> Dict:
    """Analiza el sentimiento del feedback."""
    # Análisis básico (en producción usar IA)
    positive_words = ['claro', 'bueno', 'excelente', 'útil', 'completo']
    negative_words = ['confuso', 'malo', 'incompleto', 'poco claro']
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    score = (positive_count - negative_count) * 20
    score = max(-1, min(1, score))
    
    if score > 0.3:
        category = "positive"
    elif score < -0.3:
        category = "negative"
    else:
        category = "neutral"
    
    return {"score": score, "category": category}


def generate_improvement_suggestions(**context) -> List[Dict]:
    """Genera sugerencias de mejora basadas en feedback."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener feedback negativo
        feedback = pg_hook.get_records("""
            SELECT feedback_data, sentiment_category
            FROM candidate_feedback cf
            JOIN job_applications ja ON cf.application_id = ja.application_id
            WHERE ja.job_description_id = %s
            AND sentiment_category = 'negative'
        """, parameters=(job_description_id,))
        
        suggestions = []
        for row in feedback:
            feedback_text = json.loads(row[0]).get('comments', '')
            # Generar sugerencias basadas en feedback
            if 'confuso' in feedback_text.lower():
                suggestions.append({
                    "type": "clarity",
                    "suggestion": "Mejorar claridad de requisitos",
                    "priority": "high"
                })
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generando sugerencias: {str(e)}")
        return []


# DAG para feedback
with DAG(
    'job_description_candidate_feedback',
    default_args=default_args,
    description='Sistema de feedback de candidatos',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'feedback', 'candidates'],
) as dag:
    
    collect_feedback = PythonOperator(
        task_id='collect_candidate_feedback',
        python_callable=collect_candidate_feedback,
    )
    
    generate_suggestions = PythonOperator(
        task_id='generate_improvement_suggestions',
        python_callable=generate_improvement_suggestions,
    )
    
    collect_feedback >> generate_suggestions







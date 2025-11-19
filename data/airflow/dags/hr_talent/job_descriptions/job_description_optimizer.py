"""
DAG para optimización automática de descripciones de puesto basada en métricas.

Características:
- A/B testing de descripciones
- Análisis de sentimiento
- Optimización automática basada en performance
- Generación de variantes
- Análisis de palabras clave
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
import requests
from typing import Dict, List, Optional
import re
from collections import Counter

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


class SentimentAnalyzer:
    """Analizador de sentimiento para descripciones de puesto."""
    
    # Palabras positivas y negativas
    POSITIVE_WORDS = [
        'oportunidad', 'crecimiento', 'innovación', 'desafío', 'impacto',
        'colaboración', 'aprendizaje', 'desarrollo', 'flexibilidad', 'equilibrio',
        'moderno', 'vanguardia', 'excelente', 'único', 'dinámico', 'motivador'
    ]
    
    NEGATIVE_WORDS = [
        'exigente', 'estresante', 'presión', 'urgente', 'crítico',
        'obligatorio', 'necesario', 'requerido', 'debe', 'obligado'
    ]
    
    def analyze(self, text: str) -> Dict:
        """Analiza el sentimiento de un texto."""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.POSITIVE_WORDS if word in text_lower)
        negative_count = sum(1 for word in self.NEGATIVE_WORDS if word in text_lower)
        
        total_words = len(text.split())
        positive_ratio = positive_count / total_words if total_words > 0 else 0
        negative_ratio = negative_count / total_words if total_words > 0 else 0
        
        # Score de -1 (muy negativo) a 1 (muy positivo)
        sentiment_score = (positive_ratio - negative_ratio) * 10
        sentiment_score = max(-1, min(1, sentiment_score))
        
        # Categoría
        if sentiment_score > 0.3:
            category = "muy_positivo"
        elif sentiment_score > 0.1:
            category = "positivo"
        elif sentiment_score > -0.1:
            category = "neutral"
        elif sentiment_score > -0.3:
            category = "negativo"
        else:
            category = "muy_negativo"
        
        return {
            "score": round(sentiment_score, 3),
            "category": category,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "positive_ratio": round(positive_ratio, 4),
            "negative_ratio": round(negative_ratio, 4)
        }


class KeywordAnalyzer:
    """Analizador de palabras clave en descripciones."""
    
    def extract_keywords(self, text: str, top_n: int = 20) -> List[Dict]:
        """Extrae palabras clave importantes."""
        # Remover stopwords comunes
        stopwords = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'en', 'a', 'al', 'con', 'por', 'para',
            'es', 'son', 'ser', 'estar', 'tener', 'hacer', 'poder',
            'que', 'cual', 'como', 'cuando', 'donde', 'este', 'esta',
            'y', 'o', 'pero', 'si', 'no', 'también', 'más', 'muy'
        }
        
        # Extraer palabras (mínimo 4 caracteres)
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text.lower())
        words = [w for w in words if w not in stopwords]
        
        # Contar frecuencia
        word_freq = Counter(words)
        
        # Retornar top N
        keywords = []
        for word, count in word_freq.most_common(top_n):
            keywords.append({
                "keyword": word,
                "frequency": count,
                "importance": count / len(words) if words else 0
            })
        
        return keywords


def generate_variants(**context) -> List[Dict]:
    """Genera variantes de una descripción para A/B testing."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    num_variants = context['dag_run'].conf.get('num_variants', 3)
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener descripción original
        query = "SELECT description, role, level FROM job_descriptions WHERE job_description_id = %s"
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        original_description, role, level = result
        
        # Importar LLMClient del otro DAG
        import sys
        import os
        sys.path.insert(0, os.path.dirname(__file__))
        from job_description_ai_generator import LLMClient
        
        llm_client = LLMClient()
        
        variants = []
        for i in range(num_variants):
            # Generar variante con diferentes enfoques
            approaches = [
                "Enfócate en beneficios y cultura de la empresa",
                "Enfócate en desafíos técnicos y tecnologías",
                "Enfócate en crecimiento profesional y oportunidades"
            ]
            
            prompt = f"""
            Genera una variante de esta descripción de puesto, pero con un enfoque diferente.
            
            Descripción original:
            {original_description[:1000]}
            
            Enfoque para esta variante: {approaches[i % len(approaches)]}
            
            Mantén la misma información esencial pero cambia el tono, estructura o énfasis.
            """
            
            try:
                result = llm_client.generate(
                    prompt=prompt,
                    system_prompt="Eres un experto en redacción de descripciones de puesto. Genera variantes creativas.",
                    temperature=0.8,
                    max_tokens=3000
                )
                
                variant_description = result['content'].strip()
                
                # Guardar variante
                variant_id = pg_hook.get_first("""
                    INSERT INTO job_description_variants (
                        job_description_id, variant_number, description, 
                        approach, created_at
                    ) VALUES (%s, %s, %s, %s, NOW())
                    RETURNING variant_id
                """, parameters=(
                    job_description_id, i + 1, variant_description, approaches[i % len(approaches)]
                ))[0]
                
                variants.append({
                    "variant_id": variant_id,
                    "variant_number": i + 1,
                    "approach": approaches[i % len(approaches)],
                    "description": variant_description
                })
                
                logger.info(f"Variante {i+1} generada: variant_id={variant_id}")
                
            except Exception as e:
                logger.error(f"Error generando variante {i+1}: {str(e)}")
                continue
        
        return variants
        
    except Exception as e:
        logger.error(f"Error generando variantes: {str(e)}")
        raise


def analyze_sentiment(**context) -> Dict:
    """Analiza el sentimiento de descripciones."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        analyzer = SentimentAnalyzer()
        
        # Obtener descripción
        query = "SELECT description FROM job_descriptions WHERE job_description_id = %s"
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        description = result[0]
        sentiment = analyzer.analyze(description)
        
        # Guardar análisis
        pg_hook.run("""
            INSERT INTO job_description_analytics (
                job_description_id, analysis_type, analysis_data, created_at
            ) VALUES (%s, 'sentiment', %s, NOW())
            ON CONFLICT (job_description_id, analysis_type) 
            DO UPDATE SET analysis_data = EXCLUDED.analysis_data
        """, parameters=(job_description_id, json.dumps(sentiment)))
        
        logger.info(f"Análisis de sentimiento: {sentiment['category']} (score: {sentiment['score']})")
        return sentiment
        
    except Exception as e:
        logger.error(f"Error analizando sentimiento: {str(e)}")
        raise


def analyze_keywords(**context) -> List[Dict]:
    """Analiza palabras clave en descripciones."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        analyzer = KeywordAnalyzer()
        
        # Obtener descripción
        query = "SELECT description FROM job_descriptions WHERE job_description_id = %s"
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        description = result[0]
        keywords = analyzer.extract_keywords(description, top_n=20)
        
        # Guardar análisis
        pg_hook.run("""
            INSERT INTO job_description_analytics (
                job_description_id, analysis_type, analysis_data, created_at
            ) VALUES (%s, 'keywords', %s, NOW())
            ON CONFLICT (job_description_id, analysis_type) 
            DO UPDATE SET analysis_data = EXCLUDED.analysis_data
        """, parameters=(job_description_id, json.dumps(keywords)))
        
        logger.info(f"Extraídas {len(keywords)} palabras clave")
        return keywords
        
    except Exception as e:
        logger.error(f"Error analizando keywords: {str(e)}")
        raise


def compare_performance(**context) -> Dict:
    """Compara performance de diferentes variantes."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener métricas de todas las variantes
        query = """
            SELECT 
                v.variant_id,
                v.variant_number,
                v.approach,
                COUNT(DISTINCT jp.posting_id) as postings_count,
                COUNT(DISTINCT ja.application_id) as applications_count,
                AVG(ja.ai_score) as avg_score,
                COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END) as qualified_count
            FROM job_description_variants v
            LEFT JOIN job_postings jp ON v.variant_id = jp.variant_id
            LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
            WHERE v.job_description_id = %s
            GROUP BY v.variant_id, v.variant_number, v.approach
            ORDER BY applications_count DESC
        """
        
        results = pg_hook.get_records(query, parameters=(job_description_id,))
        
        comparison = {
            "job_description_id": job_description_id,
            "variants": [],
            "best_variant": None,
            "total_applications": 0
        }
        
        best_score = 0
        for row in results:
            variant_id, variant_number, approach, postings, applications, avg_score, qualified = row
            
            variant_data = {
                "variant_id": variant_id,
                "variant_number": variant_number,
                "approach": approach,
                "postings_count": postings or 0,
                "applications_count": applications or 0,
                "avg_application_score": float(avg_score) if avg_score else 0,
                "qualified_count": qualified or 0,
                "conversion_rate": (qualified or 0) / (applications or 1) * 100
            }
            
            comparison["variants"].append(variant_data)
            comparison["total_applications"] += applications or 0
            
            # Calcular score compuesto
            composite_score = (
                (applications or 0) * 0.3 +
                (float(avg_score) if avg_score else 0) * 0.4 +
                (qualified or 0) * 0.3
            )
            
            if composite_score > best_score:
                best_score = composite_score
                comparison["best_variant"] = variant_data
        
        # Guardar comparación
        pg_hook.run("""
            INSERT INTO job_description_analytics (
                job_description_id, analysis_type, analysis_data, created_at
            ) VALUES (%s, 'performance_comparison', %s, NOW())
            ON CONFLICT (job_description_id, analysis_type) 
            DO UPDATE SET analysis_data = EXCLUDED.analysis_data
        """, parameters=(job_description_id, json.dumps(comparison)))
        
        logger.info(f"Mejor variante: {comparison['best_variant']['variant_number']} "
                   f"({comparison['best_variant']['applications_count']} aplicaciones)")
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparando performance: {str(e)}")
        raise


def optimize_description(**context) -> Dict:
    """Optimiza una descripción basada en métricas."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener análisis previos
        sentiment_query = """
            SELECT analysis_data FROM job_description_analytics
            WHERE job_description_id = %s AND analysis_type = 'sentiment'
        """
        sentiment_result = pg_hook.get_first(sentiment_query, parameters=(job_description_id,))
        sentiment = json.loads(sentiment_result[0]) if sentiment_result else None
        
        keywords_result = pg_hook.get_first("""
            SELECT analysis_data FROM job_description_analytics
            WHERE job_description_id = %s AND analysis_type = 'keywords'
        """, parameters=(job_description_id,))
        keywords = json.loads(keywords_result[0]) if keywords_result else []
        
        # Obtener descripción original
        desc_result = pg_hook.get_first("""
            SELECT description, role FROM job_descriptions WHERE job_description_id = %s
        """, parameters=(job_description_id,))
        
        if not desc_result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        original_description, role = desc_result
        
        # Generar recomendaciones
        recommendations = []
        
        if sentiment and sentiment['score'] < 0.2:
            recommendations.append({
                "type": "sentiment",
                "priority": "high",
                "message": "El sentimiento es demasiado negativo. Agrega más palabras positivas.",
                "suggestions": [
                    "Menciona oportunidades de crecimiento",
                    "Destaca beneficios y cultura",
                    "Usa un tono más entusiasta"
                ]
            })
        
        if keywords and len(keywords) < 10:
            recommendations.append({
                "type": "keywords",
                "priority": "medium",
                "message": "Faltan palabras clave importantes. Considera agregar más términos técnicos.",
                "suggestions": [
                    "Incluye tecnologías específicas",
                    "Menciona metodologías relevantes",
                    "Agrega términos de la industria"
                ]
            })
        
        # Guardar recomendaciones
        optimization_data = {
            "recommendations": recommendations,
            "sentiment_score": sentiment['score'] if sentiment else None,
            "keywords_count": len(keywords) if keywords else 0,
            "optimization_date": datetime.now().isoformat()
        }
        
        pg_hook.run("""
            INSERT INTO job_description_analytics (
                job_description_id, analysis_type, analysis_data, created_at
            ) VALUES (%s, 'optimization', %s, NOW())
            ON CONFLICT (job_description_id, analysis_type) 
            DO UPDATE SET analysis_data = EXCLUDED.analysis_data
        """, parameters=(job_description_id, json.dumps(optimization_data)))
        
        logger.info(f"Generadas {len(recommendations)} recomendaciones de optimización")
        
        return optimization_data
        
    except Exception as e:
        logger.error(f"Error optimizando descripción: {str(e)}")
        raise


# Definición del DAG
with DAG(
    'job_description_optimizer',
    default_args=default_args,
    description='Optimiza descripciones de puesto con A/B testing y análisis',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'ai', 'optimization', 'ab-testing'],
) as dag:
    
    # Grupo 1: Análisis
    with TaskGroup('analysis_group') as analysis_group:
        analyze_sentiment_task = PythonOperator(
            task_id='analyze_sentiment',
            python_callable=analyze_sentiment,
        )
        
        analyze_keywords_task = PythonOperator(
            task_id='analyze_keywords',
            python_callable=analyze_keywords,
        )
    
    # Grupo 2: Generación de variantes
    with TaskGroup('variants_group') as variants_group:
        generate_variants_task = PythonOperator(
            task_id='generate_variants',
            python_callable=generate_variants,
        )
    
    # Grupo 3: Comparación y optimización
    with TaskGroup('optimization_group') as optimization_group:
        compare_performance_task = PythonOperator(
            task_id='compare_performance',
            python_callable=compare_performance,
        )
        
        optimize_description_task = PythonOperator(
            task_id='optimize_description',
            python_callable=optimize_description,
        )
    
    # Flujo
    analysis_group >> generate_variants_task >> compare_performance_task
    analysis_group >> optimize_description_task







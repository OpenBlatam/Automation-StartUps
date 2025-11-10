"""
API REST para el sistema de descripciones de puesto.

Endpoints:
- GET /api/job-descriptions - Listar descripciones
- POST /api/job-descriptions - Crear nueva descripción
- GET /api/job-descriptions/{id} - Obtener descripción
- PUT /api/job-descriptions/{id} - Actualizar descripción
- POST /api/job-descriptions/{id}/publish - Publicar descripción
- POST /api/job-descriptions/{id}/optimize - Optimizar descripción
- GET /api/job-descriptions/{id}/analytics - Obtener analytics
- POST /api/job-descriptions/{id}/variants - Generar variantes
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Flask app para API (se ejecuta como servicio separado)
app = Flask(__name__)
CORS(app)


@app.route('/api/job-descriptions', methods=['GET'])
def list_job_descriptions():
    """Lista todas las descripciones de puesto."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Parámetros de query
        status = request.args.get('status', 'all')
        industry = request.args.get('industry')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        query = """
            SELECT 
                job_description_id, role, level, department, 
                status, created_at, published_at
            FROM job_descriptions
            WHERE 1=1
        """
        params = []
        
        if status != 'all':
            query += " AND status = %s"
            params.append(status)
        
        if industry:
            query += " AND department = %s"
            params.append(industry)
        
        query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        results = pg_hook.get_records(query, parameters=tuple(params))
        
        descriptions = []
        for row in results:
            descriptions.append({
                "id": row[0],
                "role": row[1],
                "level": row[2],
                "department": row[3],
                "status": row[4],
                "created_at": row[5].isoformat() if row[5] else None,
                "published_at": row[6].isoformat() if row[6] else None
            })
        
        return jsonify({
            "success": True,
            "data": descriptions,
            "count": len(descriptions)
        })
        
    except Exception as e:
        logger.error(f"Error listando descripciones: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/job-descriptions', methods=['POST'])
def create_job_description():
    """Crea una nueva descripción de puesto."""
    try:
        data = request.json
        
        # Validar datos requeridos
        if not data.get('role'):
            return jsonify({"success": False, "error": "role es requerido"}), 400
        
        # Trigger del DAG de generación
        from airflow.api.client.local_client import Client
        client = Client(None, None)
        
        dag_run = client.trigger_dag(
            dag_id='job_description_ai_generator',
            conf=data
        )
        
        return jsonify({
            "success": True,
            "message": "Descripción en proceso de generación",
            "dag_run_id": dag_run.run_id
        }), 202
        
    except Exception as e:
        logger.error(f"Error creando descripción: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/job-descriptions/<int:job_id>', methods=['GET'])
def get_job_description(job_id):
    """Obtiene una descripción específica."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        query = """
            SELECT 
                job_description_id, role, level, department, description,
                required_skills, preferred_skills, location, salary_range,
                status, created_at, published_at
            FROM job_descriptions
            WHERE job_description_id = %s
        """
        
        result = pg_hook.get_first(query, parameters=(job_id,))
        
        if not result:
            return jsonify({"success": False, "error": "Descripción no encontrada"}), 404
        
        description = {
            "id": result[0],
            "role": result[1],
            "level": result[2],
            "department": result[3],
            "description": result[4],
            "required_skills": json.loads(result[5]) if result[5] else [],
            "preferred_skills": json.loads(result[6]) if result[6] else [],
            "location": result[7],
            "salary_range": result[8],
            "status": result[9],
            "created_at": result[10].isoformat() if result[10] else None,
            "published_at": result[11].isoformat() if result[11] else None
        }
        
        return jsonify({"success": True, "data": description})
        
    except Exception as e:
        logger.error(f"Error obteniendo descripción: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/job-descriptions/<int:job_id>/analytics', methods=['GET'])
def get_analytics(job_id):
    """Obtiene analytics de una descripción."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener todos los análisis
        query = """
            SELECT analysis_type, analysis_data, created_at
            FROM job_description_analytics
            WHERE job_description_id = %s
            ORDER BY created_at DESC
        """
        
        results = pg_hook.get_records(query, parameters=(job_id,))
        
        analytics = {}
        for row in results:
            analytics[row[0]] = {
                "data": json.loads(row[1]) if isinstance(row[1], str) else row[1],
                "created_at": row[2].isoformat() if row[2] else None
            }
        
        # Obtener métricas de performance
        perf_query = """
            SELECT 
                COUNT(DISTINCT jp.posting_id) as postings,
                COUNT(DISTINCT ja.application_id) as applications,
                AVG(ja.ai_score) as avg_score,
                COUNT(DISTINCT CASE WHEN ja.status = 'qualified' THEN ja.application_id END) as qualified
            FROM job_descriptions jd
            LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
            LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
            WHERE jd.job_description_id = %s
        """
        
        perf_result = pg_hook.get_first(perf_query, parameters=(job_id,))
        
        if perf_result:
            analytics['performance'] = {
                "postings_count": perf_result[0] or 0,
                "applications_count": perf_result[1] or 0,
                "avg_application_score": float(perf_result[2]) if perf_result[2] else 0,
                "qualified_count": perf_result[3] or 0
            }
        
        return jsonify({"success": True, "data": analytics})
        
    except Exception as e:
        logger.error(f"Error obteniendo analytics: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/job-descriptions/<int:job_id>/optimize', methods=['POST'])
def optimize_job_description(job_id):
    """Optimiza una descripción existente."""
    try:
        from airflow.api.client.local_client import Client
        client = Client(None, None)
        
        dag_run = client.trigger_dag(
            dag_id='job_description_optimizer',
            conf={"job_description_id": job_id}
        )
        
        return jsonify({
            "success": True,
            "message": "Optimización iniciada",
            "dag_run_id": dag_run.run_id
        }), 202
        
    except Exception as e:
        logger.error(f"Error optimizando: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/job-descriptions/<int:job_id>/variants', methods=['POST'])
def generate_variants(job_id):
    """Genera variantes para A/B testing."""
    try:
        data = request.json or {}
        num_variants = data.get('num_variants', 3)
        
        from airflow.api.client.local_client import Client
        client = Client(None, None)
        
        dag_run = client.trigger_dag(
            dag_id='job_description_optimizer',
            conf={
                "job_description_id": job_id,
                "num_variants": num_variants
            }
        )
        
        return jsonify({
            "success": True,
            "message": f"Generando {num_variants} variantes",
            "dag_run_id": dag_run.run_id
        }), 202
        
    except Exception as e:
        logger.error(f"Error generando variantes: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/templates', methods=['GET'])
def list_templates():
    """Lista templates disponibles."""
    try:
        industry = request.args.get('industry')
        
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        if industry:
            query = """
                SELECT template_id, industry, role, level, usage_count, created_at
                FROM job_description_templates
                WHERE industry = %s
                ORDER BY usage_count DESC
            """
            results = pg_hook.get_records(query, parameters=(industry,))
        else:
            query = """
                SELECT template_id, industry, role, level, usage_count, created_at
                FROM job_description_templates
                ORDER BY industry, usage_count DESC
            """
            results = pg_hook.get_records(query)
        
        templates = []
        for row in results:
            templates.append({
                "id": row[0],
                "industry": row[1],
                "role": row[2],
                "level": row[3],
                "usage_count": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            })
        
        return jsonify({"success": True, "data": templates})
        
    except Exception as e:
        logger.error(f"Error listando templates: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check del API."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        pg_hook.get_first("SELECT 1")
        
        return jsonify({
            "success": True,
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "status": "unhealthy",
            "error": str(e)
        }), 503


def start_api_server(**context):
    """Inicia el servidor API."""
    port = Variable.get("JOB_DESCRIPTION_API_PORT", default_var=5000)
    host = Variable.get("JOB_DESCRIPTION_API_HOST", default_var="0.0.0.0")
    
    logger.info(f"Iniciando API en {host}:{port}")
    app.run(host=host, port=int(port), debug=False)


# DAG para mantener el API corriendo
with DAG(
    'job_description_api_server',
    default_args=default_args,
    description='Servidor API REST para descripciones de puesto',
    schedule_interval='@once',  # Se ejecuta manualmente
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'api', 'rest'],
) as dag:
    
    start_api = PythonOperator(
        task_id='start_api_server',
        python_callable=start_api_server,
    )







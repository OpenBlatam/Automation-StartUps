"""
Sistema de versionado para descripciones de puesto.

Características:
- Historial de versiones
- Comparación entre versiones
- Rollback a versiones anteriores
- Diferencias visuales
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
from typing import Dict, List, Optional
import difflib

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def create_version(**context) -> int:
    """Crea una nueva versión de una descripción."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    version_notes = context['dag_run'].conf.get('version_notes', '')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener descripción actual
        query = """
            SELECT description, role, level, department, 
                   required_skills, preferred_skills, location
            FROM job_descriptions
            WHERE job_description_id = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        # Obtener última versión
        version_query = """
            SELECT MAX(version_number) FROM job_description_versions
            WHERE job_description_id = %s
        """
        version_result = pg_hook.get_first(version_query, parameters=(job_description_id,))
        next_version = (version_result[0] or 0) + 1
        
        # Crear nueva versión
        version_id = pg_hook.get_first("""
            INSERT INTO job_description_versions (
                job_description_id, version_number, description,
                role, level, department, required_skills, preferred_skills,
                location, version_notes, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            RETURNING version_id
        """, parameters=(
            job_description_id, next_version, result[0], result[1], result[2],
            result[3], result[4], result[5], result[6], version_notes
        ))[0]
        
        logger.info(f"Versión {next_version} creada para descripción {job_description_id}")
        return version_id
        
    except Exception as e:
        logger.error(f"Error creando versión: {str(e)}")
        raise


def compare_versions(**context) -> Dict:
    """Compara dos versiones de una descripción."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    version1 = context['dag_run'].conf.get('version1')
    version2 = context['dag_run'].conf.get('version2')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener versiones
        query = """
            SELECT version_number, description, version_notes, created_at
            FROM job_description_versions
            WHERE job_description_id = %s AND version_number IN (%s, %s)
            ORDER BY version_number
        """
        results = pg_hook.get_records(query, parameters=(job_description_id, version1, version2))
        
        if len(results) != 2:
            raise Exception("Una o ambas versiones no encontradas")
        
        v1_data = results[0]
        v2_data = results[1]
        
        # Calcular diferencias
        diff = list(difflib.unified_diff(
            v1_data[1].splitlines(keepends=True),
            v2_data[1].splitlines(keepends=True),
            fromfile=f"Versión {v1_data[0]}",
            tofile=f"Versión {v2_data[0]}",
            lineterm=''
        ))
        
        comparison = {
            "version1": {
                "number": v1_data[0],
                "created_at": v1_data[3].isoformat() if v1_data[3] else None,
                "notes": v1_data[2]
            },
            "version2": {
                "number": v2_data[0],
                "created_at": v2_data[3].isoformat() if v2_data[3] else None,
                "notes": v2_data[2]
            },
            "diff": ''.join(diff),
            "changes_count": len([l for l in diff if l.startswith('+') or l.startswith('-')])
        }
        
        logger.info(f"Comparadas versiones {version1} y {version2}")
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparando versiones: {str(e)}")
        raise


def rollback_to_version(**context) -> bool:
    """Hace rollback a una versión anterior."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    target_version = context['dag_run'].conf.get('target_version')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener versión target
        query = """
            SELECT description, role, level, department,
                   required_skills, preferred_skills, location
            FROM job_description_versions
            WHERE job_description_id = %s AND version_number = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id, target_version))
        
        if not result:
            raise Exception(f"Versión {target_version} no encontrada")
        
        # Actualizar descripción actual
        pg_hook.run("""
            UPDATE job_descriptions
            SET description = %s,
                role = %s,
                level = %s,
                department = %s,
                required_skills = %s,
                preferred_skills = %s,
                location = %s,
                updated_at = NOW()
            WHERE job_description_id = %s
        """, parameters=(
            result[0], result[1], result[2], result[3],
            result[4], result[5], result[6], job_description_id
        ))
        
        # Crear nueva versión con el rollback
        create_version.__wrapped__(**{
            'dag_run': type('obj', (object,), {
                'conf': {
                    'job_description_id': job_description_id,
                    'version_notes': f'Rollback a versión {target_version}'
                }
            })()
        })
        
        logger.info(f"Rollback a versión {target_version} completado")
        return True
        
    except Exception as e:
        logger.error(f"Error en rollback: {str(e)}")
        raise


def list_versions(**context) -> List[Dict]:
    """Lista todas las versiones de una descripción."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        query = """
            SELECT version_id, version_number, version_notes, created_at
            FROM job_description_versions
            WHERE job_description_id = %s
            ORDER BY version_number DESC
        """
        results = pg_hook.get_records(query, parameters=(job_description_id,))
        
        versions = []
        for row in results:
            versions.append({
                "version_id": row[0],
                "version_number": row[1],
                "notes": row[2],
                "created_at": row[3].isoformat() if row[3] else None
            })
        
        logger.info(f"Encontradas {len(versions)} versiones")
        return versions
        
    except Exception as e:
        logger.error(f"Error listando versiones: {str(e)}")
        return []


# DAG para versionado
with DAG(
    'job_description_versioning',
    default_args=default_args,
    description='Sistema de versionado para descripciones de puesto',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'versioning'],
) as dag:
    
    create_version_task = PythonOperator(
        task_id='create_version',
        python_callable=create_version,
    )
    
    compare_versions_task = PythonOperator(
        task_id='compare_versions',
        python_callable=compare_versions,
    )
    
    rollback_task = PythonOperator(
        task_id='rollback_to_version',
        python_callable=rollback_to_version,
    )
    
    list_versions_task = PythonOperator(
        task_id='list_versions',
        python_callable=list_versions,
    )







"""
Integraciones avanzadas para descripciones de puesto.

Integraciones:
- LinkedIn Jobs API
- Indeed API
- Glassdoor API
- Greenhouse ATS
- Lever ATS
- Workday
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


class LinkedInJobsIntegration:
    """Integración con LinkedIn Jobs API."""
    
    def __init__(self):
        self.api_key = Variable.get("LINKEDIN_API_KEY", default_var=None)
        self.company_id = Variable.get("LINKEDIN_COMPANY_ID", default_var=None)
        self.base_url = "https://api.linkedin.com/v2"
    
    def publish_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publica un trabajo en LinkedIn."""
        if not self.api_key or not self.company_id:
            raise ValueError("LinkedIn API credentials no configuradas")
        
        try:
            # LinkedIn Jobs API requiere formato específico
            payload = {
                "jobPosting": {
                    "company": f"urn:li:organization:{self.company_id}",
                    "title": job_data.get("role"),
                    "description": {
                        "text": job_data.get("description")
                    },
                    "location": {
                        "country": job_data.get("location", {}).get("country", "US"),
                        "city": job_data.get("location", {}).get("city")
                    }
                }
            }
            
            response = requests.post(
                f"{self.base_url}/jobPostings",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                logger.info(f"Trabajo publicado en LinkedIn: {result.get('id')}")
                return {
                    "success": True,
                    "job_id": result.get("id"),
                    "platform": "linkedin"
                }
            else:
                raise Exception(f"Error en LinkedIn API: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error publicando en LinkedIn: {str(e)}")
            raise


class GreenhouseIntegration:
    """Integración con Greenhouse ATS."""
    
    def __init__(self):
        self.api_key = Variable.get("GREENHOUSE_API_KEY", default_var=None)
        self.base_url = "https://api.greenhouse.io/v1"
    
    def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crea un trabajo en Greenhouse."""
        if not self.api_key:
            raise ValueError("Greenhouse API key no configurada")
        
        try:
            payload = {
                "name": job_data.get("role"),
                "notes": job_data.get("description"),
                "job_post_id": None,  # Se crea después
                "status": "open"
            }
            
            response = requests.post(
                f"{self.base_url}/jobs",
                headers={
                    "Authorization": f"Basic {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )
            
            if response.ok:
                result = response.json()
                logger.info(f"Trabajo creado en Greenhouse: {result.get('id')}")
                return {
                    "success": True,
                    "job_id": result.get("id"),
                    "platform": "greenhouse"
                }
            else:
                raise Exception(f"Error en Greenhouse API: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error creando en Greenhouse: {str(e)}")
            raise
    
    def sync_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sincroniza aplicación con Greenhouse."""
        # Implementar sincronización de aplicaciones
        pass


class IndeedIntegration:
    """Integración con Indeed API."""
    
    def __init__(self):
        self.publisher_id = Variable.get("INDEED_PUBLISHER_ID", default_var=None)
        self.api_key = Variable.get("INDEED_API_KEY", default_var=None)
    
    def publish_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Publica trabajo en Indeed."""
        # Implementar publicación en Indeed
        pass


def integrate_with_linkedin(**context) -> Dict:
    """Integra con LinkedIn Jobs."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener descripción
        query = """
            SELECT role, description, location, level, department
            FROM job_descriptions
            WHERE job_description_id = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        job_data = {
            "role": result[0],
            "description": result[1],
            "location": {"city": result[2]} if result[2] else {},
            "level": result[3],
            "department": result[4]
        }
        
        linkedin = LinkedInJobsIntegration()
        result = linkedin.publish_job(job_data)
        
        # Guardar publicación
        pg_hook.run("""
            INSERT INTO job_postings (job_description_id, board, external_job_id, status)
            VALUES (%s, 'linkedin', %s, 'published')
        """, parameters=(job_description_id, result.get('job_id')))
        
        return result
        
    except Exception as e:
        logger.error(f"Error integrando con LinkedIn: {str(e)}")
        raise


def integrate_with_greenhouse(**context) -> Dict:
    """Integra con Greenhouse ATS."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        query = """
            SELECT role, description, location, level
            FROM job_descriptions
            WHERE job_description_id = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        job_data = {
            "role": result[0],
            "description": result[1],
            "location": result[2],
            "level": result[3]
        }
        
        greenhouse = GreenhouseIntegration()
        result = greenhouse.create_job(job_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error integrando con Greenhouse: {str(e)}")
        raise


# DAG para integraciones
with DAG(
    'job_description_integrations',
    default_args=default_args,
    description='Integraciones con portales y ATS',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'integrations', 'ats'],
) as dag:
    
    linkedin_integration = PythonOperator(
        task_id='integrate_with_linkedin',
        python_callable=integrate_with_linkedin,
    )
    
    greenhouse_integration = PythonOperator(
        task_id='integrate_with_greenhouse',
        python_callable=integrate_with_greenhouse,
    )







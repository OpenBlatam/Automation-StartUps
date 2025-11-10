"""
DAG para gestionar templates predefinidos de descripciones de puesto por industria.

Incluye templates para:
- Fintech
- Healthcare
- E-commerce
- SaaS
- Consultoría
- Startups
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Templates por industria
INDUSTRY_TEMPLATES = {
    'fintech': {
        'name': 'Fintech',
        'description': 'Template para roles en empresas fintech',
        'required_skills': ['Python', 'Machine Learning', 'Risk Modeling', 'Fraud Detection', 'SQL'],
        'preferred_skills': ['Time Series Analysis', 'Anomaly Detection', 'Regulatory Compliance', 'Blockchain'],
        'keywords': ['fintech', 'financial', 'risk', 'compliance', 'security', 'payment'],
        'benefits_focus': ['Seguridad', 'Compliance', 'Innovación financiera', 'Impacto en millones de usuarios']
    },
    'healthcare': {
        'name': 'Healthcare',
        'description': 'Template para roles en healthcare y biotech',
        'required_skills': ['Python', 'Medical Imaging', 'NLP', 'Clinical Data', 'SQL'],
        'preferred_skills': ['HIPAA Compliance', 'Medical AI', 'Research Publications', 'FDA Regulations'],
        'keywords': ['healthcare', 'medical', 'clinical', 'patient', 'diagnosis', 'treatment'],
        'benefits_focus': ['Impacto en vidas', 'Investigación', 'Innovación médica', 'Ética y compliance']
    },
    'ecommerce': {
        'name': 'E-commerce',
        'description': 'Template para roles en e-commerce y retail',
        'required_skills': ['Python', 'Recommendation Systems', 'Collaborative Filtering', 'SQL'],
        'preferred_skills': ['Real-time ML', 'A/B Testing', 'Personalization', 'Supply Chain'],
        'keywords': ['ecommerce', 'retail', 'recommendation', 'personalization', 'conversion', 'customer'],
        'benefits_focus': ['Escala masiva', 'Impacto en conversión', 'Datos de millones de usuarios', 'Innovación']
    },
    'saas': {
        'name': 'SaaS',
        'description': 'Template para roles en empresas SaaS',
        'required_skills': ['Python', 'Machine Learning', 'APIs', 'Cloud', 'SQL'],
        'preferred_skills': ['MLOps', 'Microservices', 'Scalability', 'Product Analytics'],
        'keywords': ['saas', 'cloud', 'scalability', 'product', 'customer success', 'growth'],
        'benefits_focus': ['Crecimiento rápido', 'Impacto en producto', 'Escalabilidad', 'Innovación']
    },
    'consulting': {
        'name': 'Consultoría',
        'description': 'Template para roles en consultoría',
        'required_skills': ['Python', 'Data Analysis', 'Business Intelligence', 'SQL'],
        'preferred_skills': ['Strategy', 'Client Management', 'Industry Knowledge', 'Presentations'],
        'keywords': ['consulting', 'strategy', 'client', 'business', 'analysis', 'insights'],
        'benefits_focus': ['Variedad de proyectos', 'Aprendizaje continuo', 'Networking', 'Impacto estratégico']
    },
    'startup': {
        'name': 'Startup',
        'description': 'Template para roles en startups',
        'required_skills': ['Python', 'Full Stack', 'Rapid Prototyping', 'SQL'],
        'preferred_skills': ['Entrepreneurship', 'Product Development', 'Growth Hacking', 'Equity'],
        'keywords': ['startup', 'fast-paced', 'impact', 'ownership', 'growth', 'innovation'],
        'benefits_focus': ['Equity', 'Impacto directo', 'Crecimiento rápido', 'Autonomía']
    }
}


def load_industry_template(**context) -> Dict:
    """Carga un template por industria."""
    industry = context['dag_run'].conf.get('industry', 'saas')
    role = context['dag_run'].conf.get('role')
    level = context['dag_run'].conf.get('level', 'Senior')
    
    if industry not in INDUSTRY_TEMPLATES:
        raise ValueError(f"Industria '{industry}' no soportada. Opciones: {list(INDUSTRY_TEMPLATES.keys())}")
    
    template = INDUSTRY_TEMPLATES[industry].copy()
    template['role'] = role
    template['level'] = level
    template['industry'] = industry
    
    logger.info(f"Template cargado para industria: {industry}, rol: {role}")
    return template


def save_template_to_db(**context) -> int:
    """Guarda un template en la base de datos."""
    template = context['ti'].xcom_pull(task_ids='load_industry_template')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Verificar si existe
        existing = pg_hook.get_first("""
            SELECT template_id FROM job_description_templates
            WHERE industry = %s AND role = %s AND level = %s
        """, parameters=(template['industry'], template['role'], template['level']))
        
        if existing:
            # Actualizar
            pg_hook.run("""
                UPDATE job_description_templates
                SET template_data = %s, updated_at = NOW()
                WHERE template_id = %s
            """, parameters=(json.dumps(template), existing[0]))
            template_id = existing[0]
            logger.info(f"Template actualizado: {template_id}")
        else:
            # Crear nuevo
            template_id = pg_hook.get_first("""
                INSERT INTO job_description_templates (
                    industry, role, level, template_data, created_at
                ) VALUES (%s, %s, %s, %s, NOW())
                RETURNING template_id
            """, parameters=(
                template['industry'],
                template['role'],
                template['level'],
                json.dumps(template)
            ))[0]
            logger.info(f"Template creado: {template_id}")
        
        return template_id
        
    except Exception as e:
        logger.error(f"Error guardando template: {str(e)}")
        raise


def list_available_templates(**context) -> List[Dict]:
    """Lista todos los templates disponibles."""
    industry_filter = context['dag_run'].conf.get('industry')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        if industry_filter:
            query = """
                SELECT template_id, industry, role, level, created_at
                FROM job_description_templates
                WHERE industry = %s
                ORDER BY created_at DESC
            """
            results = pg_hook.get_records(query, parameters=(industry_filter,))
        else:
            query = """
                SELECT template_id, industry, role, level, created_at
                FROM job_description_templates
                ORDER BY industry, created_at DESC
            """
            results = pg_hook.get_records(query)
        
        templates = []
        for row in results:
            templates.append({
                "template_id": row[0],
                "industry": row[1],
                "role": row[2],
                "level": row[3],
                "created_at": row[4].isoformat() if row[4] else None
            })
        
        logger.info(f"Encontrados {len(templates)} templates")
        return templates
        
    except Exception as e:
        logger.error(f"Error listando templates: {str(e)}")
        return []


# Definición del DAG
with DAG(
    'job_description_templates',
    default_args=default_args,
    description='Gestiona templates de descripciones por industria',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'templates', 'industries'],
) as dag:
    
    load_template = PythonOperator(
        task_id='load_industry_template',
        python_callable=load_industry_template,
    )
    
    save_template = PythonOperator(
        task_id='save_template_to_db',
        python_callable=save_template_to_db,
    )
    
    list_templates = PythonOperator(
        task_id='list_available_templates',
        python_callable=list_available_templates,
    )
    
    load_template >> save_template







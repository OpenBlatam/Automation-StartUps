"""
Sistema de aprobación y workflow para descripciones de puesto.

Características:
- Workflow de aprobación multi-nivel
- Notificaciones a aprobadores
- Tracking de estado
- Historial de aprobaciones
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


def initiate_approval_workflow(**context) -> Dict:
    """Inicia el workflow de aprobación."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    approvers = context['dag_run'].conf.get('approvers', [])
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Crear workflow de aprobación
        workflow_id = pg_hook.get_first("""
            INSERT INTO approval_workflows (
                job_description_id, status, approvers, created_at
            ) VALUES (%s, 'pending', %s, NOW())
            RETURNING workflow_id
        """, parameters=(job_description_id, json.dumps(approvers)))[0]
        
        # Notificar a primer aprobador
        if approvers:
            notify_approver(workflow_id, approvers[0], job_description_id)
        
        logger.info(f"Workflow de aprobación iniciado: {workflow_id}")
        return {"workflow_id": workflow_id, "status": "pending"}
        
    except Exception as e:
        logger.error(f"Error iniciando workflow: {str(e)}")
        raise


def approve_description(**context) -> Dict:
    """Aprueba una descripción."""
    workflow_id = context['dag_run'].conf.get('workflow_id')
    approver_email = context['dag_run'].conf.get('approver_email')
    comments = context['dag_run'].conf.get('comments', '')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Registrar aprobación
        pg_hook.run("""
            INSERT INTO approval_history (
                workflow_id, approver_email, action, comments, created_at
            ) VALUES (%s, %s, 'approved', %s, NOW())
        """, parameters=(workflow_id, approver_email, comments))
        
        # Verificar si todos aprobaron
        workflow = pg_hook.get_first("""
            SELECT approvers, status FROM approval_workflows WHERE workflow_id = %s
        """, parameters=(workflow_id,))
        
        if workflow:
            approvers = json.loads(workflow[0])
            approved = pg_hook.get_records("""
                SELECT DISTINCT approver_email FROM approval_history
                WHERE workflow_id = %s AND action = 'approved'
            """, parameters=(workflow_id,))
            
            approved_emails = [a[0] for a in approved]
            
            if len(approved_emails) >= len(approvers):
                # Todos aprobaron
                pg_hook.run("""
                    UPDATE approval_workflows SET status = 'approved', approved_at = NOW()
                    WHERE workflow_id = %s
                """, parameters=(workflow_id,))
                
                # Actualizar descripción
                job_desc_id = pg_hook.get_first("""
                    SELECT job_description_id FROM approval_workflows WHERE workflow_id = %s
                """, parameters=(workflow_id,))[0]
                
                pg_hook.run("""
                    UPDATE job_descriptions SET status = 'approved' WHERE job_description_id = %s
                """, parameters=(job_desc_id,))
                
                logger.info(f"Descripción {job_desc_id} aprobada completamente")
        
        return {"status": "approved", "workflow_id": workflow_id}
        
    except Exception as e:
        logger.error(f"Error aprobando: {str(e)}")
        raise


def notify_approver(workflow_id: int, approver_email: str, job_description_id: int) -> None:
    """Notifica a un aprobador."""
    # En producción, enviar email/Slack
    logger.info(f"Notificando aprobador {approver_email} para workflow {workflow_id}")


# DAG para aprobaciones
with DAG(
    'job_description_approval_workflow',
    default_args=default_args,
    description='Workflow de aprobación para descripciones',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'approval', 'workflow'],
) as dag:
    
    initiate_workflow = PythonOperator(
        task_id='initiate_approval_workflow',
        python_callable=initiate_approval_workflow,
    )
    
    approve = PythonOperator(
        task_id='approve_description',
        python_callable=approve_description,
    )

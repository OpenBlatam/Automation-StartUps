"""
Sistema de aprobación y workflow para descripciones de puesto.

Características:
- Workflow de aprobación multi-nivel
- Notificaciones a aprobadores
- Historial de aprobaciones
- Rechazo con comentarios
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
        
        # Obtener descripción
        query = """
            SELECT role, level, department, description
            FROM job_descriptions
            WHERE job_description_id = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            raise Exception(f"Descripción {job_description_id} no encontrada")
        
        # Si no hay aprobadores, usar configuración por defecto
        if not approvers:
            approvers = Variable.get("DEFAULT_APPROVERS", default_var='[]', deserialize_json=True)
            if not approvers:
                approvers = ["hr-manager@empresa.com", "department-head@empresa.com"]
        
        # Crear workflow de aprobación
        workflow_data = {
            "job_description_id": job_description_id,
            "approvers": approvers,
            "current_step": 0,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Guardar workflow
        workflow_id = pg_hook.get_first("""
            INSERT INTO approval_workflows (
                job_description_id, workflow_data, status, created_at
            ) VALUES (%s, %s, 'pending', NOW())
            RETURNING workflow_id
        """, parameters=(job_description_id, json.dumps(workflow_data)))[0]
        
        # Notificar primer aprobador
        notify_approver(approvers[0], job_description_id, workflow_id)
        
        logger.info(f"Workflow de aprobación iniciado: {workflow_id}")
        return {"workflow_id": workflow_id, "status": "pending"}
        
    except Exception as e:
        logger.error(f"Error iniciando workflow: {str(e)}")
        raise


def notify_approver(approver_email: str, job_description_id: int, workflow_id: int) -> None:
    """Notifica a un aprobador."""
    try:
        # En producción, enviar email real
        logger.info(f"Notificando aprobador: {approver_email}")
        
        # Aquí se enviaría el email con link de aprobación
        # approval_link = f"https://app.empresa.com/approve/{workflow_id}"
        
    except Exception as e:
        logger.error(f"Error notificando aprobador: {str(e)}")


def process_approval(**context) -> Dict:
    """Procesa una aprobación."""
    workflow_id = context['dag_run'].conf.get('workflow_id')
    approver_email = context['dag_run'].conf.get('approver_email')
    decision = context['dag_run'].conf.get('decision')  # 'approve' or 'reject'
    comments = context['dag_run'].conf.get('comments', '')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Obtener workflow
        query = """
            SELECT workflow_data, status FROM approval_workflows
            WHERE workflow_id = %s
        """
        result = pg_hook.get_first(query, parameters=(workflow_id,))
        
        if not result:
            raise Exception(f"Workflow {workflow_id} no encontrado")
        
        workflow_data = json.loads(result[0])
        current_status = result[1]
        
        if current_status != 'pending':
            raise Exception(f"Workflow ya procesado: {current_status}")
        
        # Registrar decisión
        approval_record = {
            "workflow_id": workflow_id,
            "approver_email": approver_email,
            "decision": decision,
            "comments": comments,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        pg_hook.run("""
            INSERT INTO approval_records (
                workflow_id, approver_email, decision, comments, created_at
            ) VALUES (%s, %s, %s, %s, NOW())
        """, parameters=(workflow_id, approver_email, decision, comments))
        
        if decision == 'reject':
            # Rechazado - finalizar workflow
            pg_hook.run("""
                UPDATE approval_workflows
                SET status = 'rejected', updated_at = NOW()
                WHERE workflow_id = %s
            """, parameters=(workflow_id,))
            
            # Actualizar descripción
            pg_hook.run("""
                UPDATE job_descriptions
                SET status = 'rejected', updated_at = NOW()
                WHERE job_description_id = %s
            """, parameters=(workflow_data['job_description_id'],))
            
            return {"status": "rejected", "workflow_id": workflow_id}
        
        else:
            # Aprobado - pasar al siguiente aprobador
            current_step = workflow_data.get('current_step', 0)
            approvers = workflow_data.get('approvers', [])
            
            if current_step + 1 >= len(approvers):
                # Todos aprobaron - finalizar
                pg_hook.run("""
                    UPDATE approval_workflows
                    SET status = 'approved', updated_at = NOW()
                    WHERE workflow_id = %s
                """, parameters=(workflow_id,))
                
                # Actualizar descripción
                pg_hook.run("""
                    UPDATE job_descriptions
                    SET status = 'approved', updated_at = NOW()
                    WHERE job_description_id = %s
                """, parameters=(workflow_data['job_description_id'],))
                
                return {"status": "approved", "workflow_id": workflow_id}
            else:
                # Siguiente aprobador
                workflow_data['current_step'] = current_step + 1
                pg_hook.run("""
                    UPDATE approval_workflows
                    SET workflow_data = %s, updated_at = NOW()
                    WHERE workflow_id = %s
                """, parameters=(json.dumps(workflow_data), workflow_id))
                
                # Notificar siguiente aprobador
                next_approver = approvers[current_step + 1]
                notify_approver(next_approver, workflow_data['job_description_id'], workflow_id)
                
                return {"status": "pending", "next_approver": next_approver}
        
    except Exception as e:
        logger.error(f"Error procesando aprobación: {str(e)}")
        raise


# DAG para workflow de aprobación
with DAG(
    'job_description_approval_workflow',
    default_args=default_args,
    description='Workflow de aprobación para descripciones de puesto',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'approval', 'workflow'],
) as dag:
    
    initiate_workflow = PythonOperator(
        task_id='initiate_approval_workflow',
        python_callable=initiate_approval_workflow,
    )
    
    process_approval_task = PythonOperator(
        task_id='process_approval',
        python_callable=process_approval,
    )


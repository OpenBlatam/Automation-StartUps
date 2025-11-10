"""
Sistema avanzado de notificaciones para descripciones de puesto.

Soporta:
- Email
- Slack
- Webhooks
- SMS (opcional)
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
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}


def send_email_notification(**context) -> bool:
    """Envía notificación por email."""
    notification_data = context['dag_run'].conf.get('notification', {})
    
    try:
        recipients = notification_data.get('recipients', [])
        subject = notification_data.get('subject', 'Notificación del Sistema')
        body = notification_data.get('body', '')
        html_body = notification_data.get('html_body')
        
        # En producción, usar servicio de email real (SendGrid, SES, etc.)
        email_api_key = Variable.get("EMAIL_API_KEY", default_var=None)
        email_service = Variable.get("EMAIL_SERVICE", default_var="smtp")
        
        if email_service == "sendgrid" and email_api_key:
            # SendGrid
            response = requests.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={
                    "Authorization": f"Bearer {email_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "personalizations": [{"to": [{"email": r} for r in recipients]}],
                    "from": {"email": Variable.get("EMAIL_FROM", default_var="noreply@empresa.com")},
                    "subject": subject,
                    "content": [
                        {"type": "text/plain", "value": body},
                        {"type": "text/html", "value": html_body or body}
                    ]
                },
                timeout=10
            )
            
            if response.ok:
                logger.info(f"Email enviado a {len(recipients)} destinatarios")
                return True
            else:
                logger.error(f"Error enviando email: {response.status_code}")
                return False
        else:
            # Fallback: solo log
            logger.info(f"[EMAIL] Para: {recipients}, Asunto: {subject}")
            return True
            
    except Exception as e:
        logger.error(f"Error enviando email: {str(e)}")
        return False


def send_slack_notification(**context) -> bool:
    """Envía notificación a Slack."""
    notification_data = context['dag_run'].conf.get('notification', {})
    
    try:
        webhook_url = Variable.get("SLACK_WEBHOOK_URL", default_var=None)
        channel = notification_data.get('channel', '#hr-notifications')
        message = notification_data.get('message', '')
        attachments = notification_data.get('attachments', [])
        
        if not webhook_url:
            logger.warning("Slack webhook no configurado")
            return False
        
        payload = {
            "channel": channel,
            "text": message,
            "attachments": attachments
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        
        if response.ok:
            logger.info(f"Notificación enviada a Slack: {channel}")
            return True
        else:
            logger.error(f"Error enviando a Slack: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error enviando a Slack: {str(e)}")
        return False


def send_webhook_notification(**context) -> bool:
    """Envía notificación a webhook personalizado."""
    notification_data = context['dag_run'].conf.get('notification', {})
    
    try:
        webhook_url = notification_data.get('webhook_url')
        payload = notification_data.get('payload', {})
        headers = notification_data.get('headers', {'Content-Type': 'application/json'})
        
        if not webhook_url:
            logger.warning("Webhook URL no proporcionada")
            return False
        
        response = requests.post(
            webhook_url,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.ok:
            logger.info(f"Webhook notificado: {webhook_url}")
            return True
        else:
            logger.error(f"Error en webhook: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error enviando webhook: {str(e)}")
        return False


def notify_job_description_created(**context) -> None:
    """Notifica cuando se crea una nueva descripción."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        query = """
            SELECT role, level, department, status
            FROM job_descriptions
            WHERE job_description_id = %s
        """
        result = pg_hook.get_first(query, parameters=(job_description_id,))
        
        if not result:
            logger.warning(f"Descripción {job_description_id} no encontrada")
            return
        
        role, level, department, status = result
        
        # Email
        email_config = {
            "recipients": Variable.get("HR_TEAM_EMAIL", default_var="hr@empresa.com").split(','),
            "subject": f"Nueva descripción de puesto: {role}",
            "body": f"""
            Se ha creado una nueva descripción de puesto:
            
            Rol: {role}
            Nivel: {level}
            Departamento: {department}
            Estado: {status}
            
            ID: {job_description_id}
            """,
            "html_body": f"""
            <h2>Nueva Descripción de Puesto</h2>
            <p><strong>Rol:</strong> {role}</p>
            <p><strong>Nivel:</strong> {level}</p>
            <p><strong>Departamento:</strong> {department}</p>
            <p><strong>Estado:</strong> {status}</p>
            <p><strong>ID:</strong> {job_description_id}</p>
            """
        }
        
        # Slack
        slack_config = {
            "channel": "#hr-notifications",
            "message": f"✅ Nueva descripción de puesto: *{role}* ({level})",
            "attachments": [{
                "color": "good",
                "fields": [
                    {"title": "Rol", "value": role, "short": True},
                    {"title": "Nivel", "value": level, "short": True},
                    {"title": "Departamento", "value": department or "N/A", "short": True},
                    {"title": "Estado", "value": status, "short": True}
                ]
            }]
        }
        
        # Enviar notificaciones
        send_email_notification.__wrapped__(**{'dag_run': type('obj', (object,), {'conf': {'notification': email_config}})()})
        send_slack_notification.__wrapped__(**{'dag_run': type('obj', (object,), {'conf': {'notification': slack_config}})()})
        
    except Exception as e:
        logger.error(f"Error notificando creación: {str(e)}")


def notify_application_received(**context) -> None:
    """Notifica cuando se recibe una nueva aplicación."""
    application_data = context['dag_run'].conf.get('application', {})
    
    try:
        candidate_name = application_data.get('name', 'N/A')
        role = application_data.get('role', 'N/A')
        score = application_data.get('score', 0)
        
        # Slack
        slack_config = {
            "channel": "#hr-applications",
            "message": f"📥 Nueva aplicación: *{candidate_name}* para {role}",
            "attachments": [{
                "color": "good" if score >= 70 else "warning",
                "fields": [
                    {"title": "Candidato", "value": candidate_name, "short": True},
                    {"title": "Rol", "value": role, "short": True},
                    {"title": "Score", "value": str(score), "short": True}
                ]
            }]
        }
        
        send_slack_notification.__wrapped__(**{'dag_run': type('obj', (object,), {'conf': {'notification': slack_config}})()})
        
    except Exception as e:
        logger.error(f"Error notificando aplicación: {str(e)}")


# DAG para notificaciones
with DAG(
    'job_description_notifications',
    default_args=default_args,
    description='Sistema de notificaciones para descripciones de puesto',
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'notifications'],
) as dag:
    
    notify_created = PythonOperator(
        task_id='notify_job_description_created',
        python_callable=notify_job_description_created,
    )
    
    notify_application = PythonOperator(
        task_id='notify_application_received',
        python_callable=notify_application_received,
    )







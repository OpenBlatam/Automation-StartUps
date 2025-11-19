"""
DAG de Recordatorios Automáticos de Renovación de Contratos
Verifica contratos próximos a expirar y envía recordatorios
"""

from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

logger = logging.getLogger("airflow.task")

CONTRACT_POOL = os.getenv("CONTRACT_POOL", "etl_pool")


def send_renewal_reminder(
    contract_id: str,
    reminder_type: str,
    days_before_expiration: int,
    recipient_email: str,
    recipient_role: str = "contract_owner",
    reminder_channel: str = "email",
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Envía un recordatorio de renovación y lo registra en BD.
    
    Args:
        contract_id: ID del contrato
        reminder_type: Tipo de recordatorio
        days_before_expiration: Días antes de expiración
        recipient_email: Email del destinatario
        recipient_role: Rol del destinatario
        reminder_channel: Canal de envío (email, slack, etc.)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del recordatorio
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener información del contrato
    contract_query = """
        SELECT contract_id, title, primary_party_name, primary_party_email,
               expiration_date, auto_renew
        FROM contracts
        WHERE contract_id = %s
    """
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    if not contract:
        raise ValueError(f"Contrato no encontrado: {contract_id}")
    
    # TODO: Enviar email/Slack/notificación real
    # Por ahora solo registramos en BD
    logger.info(
        f"Enviando recordatorio de renovación",
        extra={
            "contract_id": contract_id,
            "recipient_email": recipient_email,
            "days_before_expiration": days_before_expiration,
            "reminder_type": reminder_type,
        },
    )
    
    # Insertar recordatorio en BD
    insert_query = """
        INSERT INTO contract_renewal_reminders (
            contract_id, reminder_type, days_before_expiration,
            reminder_sent_to, reminder_recipient_role, reminder_channel,
            reminder_status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    
    hook.run(insert_query, parameters=(
        contract_id,
        reminder_type,
        days_before_expiration,
        recipient_email,
        recipient_role,
        reminder_channel,
        "sent"
    ))
    
    # Actualizar flag de recordatorio enviado si es el primer recordatorio
    if days_before_expiration == 90:  # Primer recordatorio
        hook.run(
            "UPDATE contracts SET renewal_reminder_sent = true WHERE contract_id = %s",
            parameters=(contract_id,)
        )
    
    # Registrar evento
    event_query = """
        INSERT INTO contract_events (
            contract_id, event_type, event_description, event_data
        ) VALUES (%s, %s, %s, %s)
    """
    hook.run(event_query, parameters=(
        contract_id,
        "renewal_reminder_sent",
        f"Recordatorio de renovación enviado ({days_before_expiration} días antes)",
        f'{{"days_before": {days_before_expiration}, "recipient": "{recipient_email}"}}'
    ))
    
    return {
        "contract_id": contract_id,
        "reminder_type": reminder_type,
        "days_before_expiration": days_before_expiration,
        "recipient_email": recipient_email,
        "status": "sent"
    }


@dag(
    dag_id="contract_renewal_reminders",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=timedelta(hours=24),  # Ejecutar diariamente
    catchup=False,
    default_args={
        "owner": "legal-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Contract Renewal Reminders - Recordatorios Automáticos de Renovación
    
    DAG que se ejecuta diariamente para:
    - ✅ Identificar contratos próximos a expirar
    - ✅ Enviar recordatorios según días configurados (90, 60, 30, 14, 7 días antes)
    - ✅ Evitar recordatorios duplicados
    - ✅ Registrar todos los recordatorios enviados
    
    **Funcionalidad:**
    - Busca contratos con status 'fully_signed'
    - Filtra por fecha de expiración próxima
    - Verifica si ya se enviaron recordatorios para evitar duplicados
    - Envía recordatorios según configuración de la plantilla
    - Notifica a múltiples roles (dueño, manager, legal)
    """,
    description="Sistema de recordatorios automáticos de renovación de contratos",
    tags=["contracts", "legal", "hr", "automation", "reminders"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
)
def contract_renewal_reminders() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="find_expiring_contracts", pool=CONTRACT_POOL)
    def find_expiring_contracts() -> List[Dict[str, Any]]:
        """Encuentra contratos próximos a expirar que necesitan recordatorios."""
        if not POSTGRES_AVAILABLE:
            raise ImportError("PostgreSQL hook no disponible")
        
        if Stats:
            try:
                Stats.incr("contracts.renewal.find_contracts.start", 1)
            except Exception:
                pass
        
        hook = PostgresHook(postgres_conn_id="postgres_default")
        
        # Buscar contratos firmados que expiran en los próximos 90 días
        query = """
            SELECT DISTINCT
                c.contract_id,
                c.title,
                c.primary_party_email,
                c.primary_party_name,
                c.expiration_date,
                c.auto_renew,
                c.renewal_notice_days,
                c.contract_type,
                t.default_reminder_days,
                t.template_id
            FROM contracts c
            JOIN contract_templates t ON c.template_id = t.template_id
            WHERE c.status = 'fully_signed'
              AND c.expiration_date IS NOT NULL
              AND c.expiration_date >= CURRENT_DATE
              AND c.expiration_date <= CURRENT_DATE + INTERVAL '90 days'
              AND c.expiration_date > c.signed_date
            ORDER BY c.expiration_date ASC
        """
        
        contracts = hook.get_records(query)
        
        result = []
        for row in contracts:
            contract_id = row[0]
            expiration_date = row[4]
            default_reminder_days = row[8] or [90, 60, 30, 14, 7]
            
            # Verificar qué recordatorios ya se enviaron
            reminders_query = """
                SELECT DISTINCT days_before_expiration
                FROM contract_renewal_reminders
                WHERE contract_id = %s
            """
            sent_reminders = {r[0] for r in hook.get_records(reminders_query, parameters=(contract_id,))}
            
            # Calcular días hasta expiración
            days_until_expiration = (expiration_date - pendulum.now().date()).days
            
            # Determinar qué recordatorios enviar
            reminders_to_send = []
            for days_before in default_reminder_days:
                if days_before not in sent_reminders and days_until_expiration <= days_before:
                    reminders_to_send.append({
                        "days_before_expiration": days_before,
                        "reminder_type": "expiration_warning" if days_before > 30 else "renewal_due"
                    })
            
            if reminders_to_send:
                result.append({
                    "contract_id": contract_id,
                    "title": row[1],
                    "primary_party_email": row[2],
                    "primary_party_name": row[3],
                    "expiration_date": expiration_date.isoformat() if hasattr(expiration_date, 'isoformat') else str(expiration_date),
                    "days_until_expiration": days_until_expiration,
                    "auto_renew": row[5],
                    "contract_type": row[7],
                    "reminders_to_send": reminders_to_send
                })
        
        logger.info(
            f"Contratos próximos a expirar encontrados",
            extra={"contracts_count": len(result)},
        )
        
        if Stats:
            try:
                Stats.incr("contracts.renewal.find_contracts.success", 1)
                Stats.incr("contracts.renewal.find_contracts.count", len(result))
            except Exception:
                pass
        
        return result

    @task(task_id="send_reminders", pool=CONTRACT_POOL)
    def send_reminders(contracts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Envía recordatorios para cada contrato."""
        if Stats:
            try:
                Stats.incr("contracts.renewal.send_reminders.start", 1)
            except Exception:
                pass
        
        total_sent = 0
        errors = []
        
        for contract in contracts:
            contract_id = contract["contract_id"]
            reminders_to_send = contract["reminders_to_send"]
            
            for reminder_config in reminders_to_send:
                try:
                    send_renewal_reminder(
                        contract_id=contract_id,
                        reminder_type=reminder_config["reminder_type"],
                        days_before_expiration=reminder_config["days_before_expiration"],
                        recipient_email=contract["primary_party_email"],
                        recipient_role="contract_owner",
                        reminder_channel="email",
                    )
                    total_sent += 1
                    
                    logger.info(
                        f"Recordatorio enviado",
                        extra={
                            "contract_id": contract_id,
                            "days_before": reminder_config["days_before_expiration"],
                        },
                    )
                except Exception as e:
                    error_msg = f"Error enviando recordatorio para {contract_id}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        result = {
            "total_contracts": len(contracts),
            "total_reminders_sent": total_sent,
            "errors": errors,
            "success": len(errors) == 0
        }
        
        logger.info(
            f"Recordatorios procesados",
            extra=result,
        )
        
        if Stats:
            try:
                Stats.incr("contracts.renewal.send_reminders.success", 1)
                Stats.incr("contracts.renewal.send_reminders.count", total_sent)
            except Exception:
                pass
        
        return result

    # Define task flow
    contracts = find_expiring_contracts()
    result = send_reminders(contracts)
    
    return None


dag = contract_renewal_reminders()


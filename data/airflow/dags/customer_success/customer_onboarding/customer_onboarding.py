from __future__ import annotations

from datetime import timedelta
import logging
import os
import hashlib
from typing import Dict, Any, List
import json

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

# Shared callbacks and utilities
from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
from data.airflow.plugins.etl_notifications import notify_slack

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore

# Customer onboarding integrations
from data.airflow.plugins.customer_onboarding_integrations import (
    collect_customer_info,
    verify_customer_identity,
    activate_customer_accounts,
    send_welcome_email,
    persist_onboarding_data,
)

logger = logging.getLogger(__name__)

ONBOARDING_POOL = os.getenv("CUSTOMER_ONBOARDING_POOL", "etl_pool")
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))


def _validate_customer_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validación robusta de datos del cliente."""
    required = ["customer_email", "first_name", "last_name"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise AirflowFailException(f"Missing required params: {', '.join(missing)}")
    
    # Validación de formato de email
    email = payload.get("customer_email", "")
    if "@" not in email or "." not in email.split("@")[1]:
        raise AirflowFailException(f"Invalid email format: {email}")
    
    # Validación de servicios a activar
    services = payload.get("services_to_activate", [])
    if not services:
        logger.warning("No services specified for activation", extra={"customer_email": email})
    
    return payload


def _generate_idempotency_key(payload: Dict[str, Any]) -> str:
    """Genera clave de idempotencia única."""
    email = payload.get("customer_email", "")
    source = payload.get("source", "api")
    key_base = f"{email}:{source}"
    
    # Si hay un idempotency_key personalizado, usarlo
    if payload.get("idempotency_key"):
        return payload["idempotency_key"]
    
    # Generar hash para clave única
    return hashlib.sha256(key_base.encode()).hexdigest()[:32]


@dag(
    dag_id="customer_onboarding",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "sales-operations",
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Customer Onboarding
    
    Sistema automatizado completo para onboarding de nuevos clientes que incluye:
    - ✅ Recolección automática de información
    - ✅ Verificación de identidad (email, SMS, documentos, KYC)
    - ✅ Activación automática de cuentas y servicios
    - ✅ Envío de emails de bienvenida
    - ✅ Persistencia completa en base de datos
    - ✅ Tracking y auditoría de todo el proceso
    
    **Flujo del proceso:**
    1. Validación y preparación de datos
    2. Creación de registro en BD
    3. Recolección de información adicional (si es necesaria)
    4. Verificación de identidad
    5. Activación de cuentas y servicios
    6. Envío de email de bienvenida
    7. Persistencia y notificaciones
    
    Dispara manualmente con parámetros del cliente o desde webhook/API.
    """,
    params={
        "customer_email": Param("", type="string", description="Email del cliente (requerido)"),
        "first_name": Param("", type="string", description="Nombre (requerido)"),
        "last_name": Param("", type="string", description="Apellido (requerido)"),
        "company_name": Param("", type="string", description="Nombre de empresa"),
        "phone": Param("", type="string", description="Teléfono"),
        "country": Param("", type="string", description="País"),
        "service_plan": Param("", type="string", description="Plan de servicio"),
        "service_tier": Param("", type="string", description="Nivel de servicio"),
        "services_to_activate": Param([], type="array", description="Lista de servicios a activar (array)"),
        "source": Param("api", type="string", description="Origen del cliente: website, sales, api, import"),
        "utm_source": Param("", type="string", description="UTM source"),
        "utm_campaign": Param("", type="string", description="UTM campaign"),
        "sales_rep_email": Param("", type="string", description="Email del representante de ventas"),
        "identity_verification_method": Param("email", type="string", description="Método de verificación: email, sms, document, kyc_provider"),
        "auto_activate_services": Param(True, type="boolean", description="Activar servicios automáticamente después de verificación"),
        "send_welcome_email": Param(True, type="boolean", description="Enviar email de bienvenida"),
        "idempotency_key": Param("", type="string", description="Clave de idempotencia personalizada"),
        "metadata": Param({}, type="object", description="Metadatos adicionales (JSON)"),
    },
    description="Automated customer onboarding with identity verification and service activation",
    tags=["onboarding", "customer", "sales", "automation", "kyc"],
    dagrun_timeout=timedelta(minutes=45),
    max_active_runs=5,
    max_active_tasks=MAX_ACTIVE_TASKS,
    concurrency=10,
    sla_miss_callback=sla_miss_callback,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: notify_slack(":white_check_mark: customer_onboarding DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: customer_onboarding DAG failed"),
)
def customer_onboarding() -> None:
    logger = logging.getLogger("airflow.task")
    context = get_current_context()
    params = context.get("params", {})
    
    @task(task_id="validate_and_prepare", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def validate_and_prepare() -> Dict[str, Any]:
        """Validación inicial y preparación de datos."""
        logger.info("Validating customer data", extra={"params": params})
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.validate.start", 1)
            except Exception:
                pass
        
        payload = dict(params)
        
        # Validar datos
        validated = _validate_customer_data(payload)
        
        # Generar idempotency key
        idempotency_key = _generate_idempotency_key(validated)
        validated["idempotency_key"] = idempotency_key
        
        # Asegurar que services_to_activate es una lista
        if isinstance(validated.get("services_to_activate"), str):
            try:
                validated["services_to_activate"] = json.loads(validated["services_to_activate"])
            except Exception:
                validated["services_to_activate"] = [validated["services_to_activate"]]
        
        if not validated.get("services_to_activate"):
            # Servicios por defecto si no se especifican
            validated["services_to_activate"] = ["platform", "dashboard", "api"]
        
        logger.info("Validation successful", extra={"customer_email": validated.get("customer_email")})
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.validate.success", 1)
            except Exception:
                pass
        
        return validated

    @task(task_id="create_onboarding_record", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def create_onboarding_record(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Crear registro inicial en base de datos."""
        customer_email = payload.get("customer_email")
        logger.info("Creating onboarding record", extra={"customer_email": customer_email})
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.create_record.start", 1)
            except Exception:
                pass
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=os.getenv("POSTGRES_CONN_ID", "postgres_default"))
            
            # Verificar si ya existe un onboarding activo
            check_sql = """
                SELECT id, status FROM customer_onboarding 
                WHERE idempotency_key = %s OR customer_email = %s
                ORDER BY created_at DESC LIMIT 1
            """
            
            existing = pg_hook.get_first(check_sql, parameters=(payload["idempotency_key"], customer_email))
            
            if existing:
                existing_id, existing_status = existing
                if existing_status in ["completed", "failed", "rejected"]:
                    logger.info("Existing record found but completed, creating new one")
                else:
                    logger.warning("Active onboarding already exists", extra={
                        "existing_id": existing_id,
                        "existing_status": existing_status
                    })
                    # Retornar el registro existente
                    payload["onboarding_id"] = existing_id
                    return payload
            
            # Insertar nuevo registro
            insert_sql = """
                INSERT INTO customer_onboarding (
                    customer_email, first_name, last_name, company_name, phone, country,
                    service_plan, service_tier, services_to_activate,
                    source, utm_source, utm_campaign, sales_rep_email,
                    identity_verification_method, idempotency_key, metadata, status
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s::text[], %s, %s, %s, %s, %s, %s, %s::jsonb, 'collecting_info'
                ) RETURNING id
            """
            
            onboarding_id = pg_hook.get_first(insert_sql, parameters=(
                customer_email,
                payload.get("first_name"),
                payload.get("last_name"),
                payload.get("company_name"),
                payload.get("phone"),
                payload.get("country"),
                payload.get("service_plan"),
                payload.get("service_tier"),
                payload.get("services_to_activate", []),
                payload.get("source", "api"),
                payload.get("utm_source"),
                payload.get("utm_campaign"),
                payload.get("sales_rep_email"),
                payload.get("identity_verification_method", "email"),
                payload["idempotency_key"],
                json.dumps(payload.get("metadata", {}))
            ))[0]
            
            payload["onboarding_id"] = onboarding_id
            
            # Registrar evento
            event_sql = """
                INSERT INTO customer_onboarding_events (customer_email, event_type, event_details)
                VALUES (%s, 'onboarding_started', %s::jsonb)
            """
            pg_hook.run(event_sql, parameters=(
                customer_email,
                json.dumps({"onboarding_id": onboarding_id, "source": payload.get("source")})
            ))
            
            logger.info("Onboarding record created", extra={"onboarding_id": onboarding_id})
            
            if Stats:
                try:
                    Stats.incr("customer_onboarding.create_record.success", 1)
                except Exception:
                    pass
            
            return payload
            
        except Exception as e:
            logger.error("Failed to create onboarding record", exc_info=True, extra={"customer_email": customer_email})
            if Stats:
                try:
                    Stats.incr("customer_onboarding.create_record.failed", 1)
                except Exception:
                    pass
            raise

    @task(task_id="collect_customer_info", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def collect_customer_info_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Recolectar información adicional del cliente si es necesaria."""
        if Stats:
            try:
                Stats.incr("customer_onboarding.collect_info.start", 1)
            except Exception:
                pass
        
        result = collect_customer_info(payload)
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.collect_info.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="verify_identity", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def verify_identity_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Verificar identidad del cliente."""
        if Stats:
            try:
                Stats.incr("customer_onboarding.verify_identity.start", 1)
            except Exception:
                pass
        
        result = verify_customer_identity(payload)
        
        if Stats:
            try:
                if result.get("identity_verified"):
                    Stats.incr("customer_onboarding.verify_identity.success", 1)
                else:
                    Stats.incr("customer_onboarding.verify_identity.failed", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="activate_accounts", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def activate_accounts_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Activar cuentas y servicios para el cliente."""
        # Solo activar si la identidad está verificada
        if not payload.get("identity_verified"):
            logger.warning("Identity not verified, skipping account activation", extra={
                "customer_email": payload.get("customer_email")
            })
            return payload
        
        auto_activate = payload.get("auto_activate_services", True)
        if not auto_activate:
            logger.info("Auto-activation disabled, skipping", extra={
                "customer_email": payload.get("customer_email")
            })
            return payload
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.activate_accounts.start", 1)
            except Exception:
                pass
        
        result = activate_customer_accounts(payload)
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.activate_accounts.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="send_welcome", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def send_welcome_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enviar email de bienvenida."""
        if not payload.get("send_welcome_email", True):
            logger.info("Welcome email disabled, skipping")
            return payload
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.send_welcome.start", 1)
            except Exception:
                pass
        
        result = send_welcome_email(payload)
        
        if Stats:
            try:
                Stats.incr("customer_onboarding.send_welcome.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="complete_onboarding", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def complete_onboarding_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Completar onboarding y persistir datos finales."""
        if Stats:
            try:
                Stats.incr("customer_onboarding.complete.start", 1)
            except Exception:
                pass
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=os.getenv("POSTGRES_CONN_ID", "postgres_default"))
            customer_email = payload.get("customer_email")
            
            # Actualizar estado a completado
            update_sql = """
                UPDATE customer_onboarding
                SET status = 'completed',
                    onboarding_completed_at = NOW(),
                    updated_at = NOW()
                WHERE customer_email = %s AND status != 'completed'
                RETURNING id
            """
            
            updated = pg_hook.get_first(update_sql, parameters=(customer_email,))
            
            if updated:
                onboarding_id = updated[0]
                
                # Registrar evento de completado
                event_sql = """
                    INSERT INTO customer_onboarding_events (customer_email, event_type, event_details)
                    VALUES (%s, 'onboarding_completed', %s::jsonb)
                """
                
                event_details = {
                    "onboarding_id": onboarding_id,
                    "identity_verified": payload.get("identity_verified", False),
                    "accounts_activated": payload.get("accounts_activated", []),
                    "services_activated": payload.get("services_to_activate", [])
                }
                
                pg_hook.run(event_sql, parameters=(
                    customer_email,
                    json.dumps(event_details)
                ))
                
                logger.info("Onboarding completed", extra={
                    "onboarding_id": onboarding_id,
                    "customer_email": customer_email
                })
                
                # Persistir datos adicionales si existe la función
                persist_onboarding_data(payload)
            
            if Stats:
                try:
                    Stats.incr("customer_onboarding.complete.success", 1)
                except Exception:
                    pass
            
            return payload
            
        except Exception as e:
            logger.error("Failed to complete onboarding", exc_info=True, extra={
                "customer_email": payload.get("customer_email")
            })
            if Stats:
                try:
                    Stats.incr("customer_onboarding.complete.failed", 1)
                except Exception:
                    pass
            raise

    # Pipeline flow
    validated = validate_and_prepare()
    record = create_onboarding_record(validated)
    info_collected = collect_customer_info_task(record)
    identity_verified = verify_identity_task(info_collected)
    accounts_activated = activate_accounts_task(identity_verified)
    welcome_sent = send_welcome_task(accounts_activated)
    complete_onboarding_task(welcome_sent)


# Export DAG
customer_onboarding_dag = customer_onboarding()






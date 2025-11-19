from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Dict, Any

import pendulum
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context
from airflow.exceptions import AirflowFailException
from airflow.models import Variable
from airflow.models.param import Param

# Shared callbacks and utilities (mirrors etl_example setup)
from data.airflow.plugins.etl_callbacks import on_task_failure, sla_miss_callback
from data.airflow.plugins.etl_notifications import notify_slack

# Onboarding integration functions
from data.airflow.plugins.onboarding_integrations import (
    hris_prefetch,
    create_idp_and_workspace_accounts,
    assign_project_and_it_tasks,
    send_welcome_and_docs,
    record_progress_and_notify,
    create_onboarding_checklist,
    assign_trainings,
    provision_accesses,
)

# Contract management integration
try:
    from data.airflow.plugins.contract_integrations import (
        create_contract_for_employee_onboarding,
    )
    CONTRACT_MANAGEMENT_AVAILABLE = True
except ImportError:
    CONTRACT_MANAGEMENT_AVAILABLE = False

try:
    from airflow.stats import Stats  # type: ignore
except Exception:
    Stats = None  # type: ignore


ONBOARDING_POOL = os.getenv("ONBOARDING_POOL", "etl_pool")
MAX_ACTIVE_TASKS = int(os.getenv("MAX_ACTIVE_TASKS", "32"))


def _validate_employee(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validación robusta de datos del empleado."""
    required = ["employee_email", "full_name", "start_date", "manager_email"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise AirflowFailException(f"Missing required params: {', '.join(missing)}")
    
    # Validación de formato de email
    email = payload.get("employee_email", "")
    if "@" not in email or "." not in email.split("@")[1]:
        raise AirflowFailException(f"Invalid email format: {email}")
    
    # Validación de fecha (formato YYYY-MM-DD)
    start_date = payload.get("start_date", "")
    try:
        pendulum.parse(start_date)
    except Exception:
        raise AirflowFailException(f"Invalid date format (expected YYYY-MM-DD): {start_date}")
    
    # Prevención de auto-asignación
    if payload.get("employee_email") == payload.get("manager_email"):
        raise AirflowFailException("Employee cannot be their own manager")
    
    return payload


@dag(
    dag_id="employee_onboarding",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,  # Manual trigger only
    catchup=False,
    default_args={
        "owner": "it-hr",
        "retries": 1,
        "retry_delay": timedelta(minutes=2),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    doc_md="""
    ### Employee Onboarding - Sistema Completo Automatizado
    
    Automatiza completamente el proceso de onboarding de nuevos empleados:
    - ✅ Checklist automatizada con tareas categorizadas
    - ✅ Asignación automática de capacitaciones
    - ✅ Provisionamiento de accesos basado en departamento/rol
    - ✅ Creación de cuentas (IdP, email, workspace)
    - ✅ Emails de bienvenida personalizados con HTML
    - ✅ Validación robusta de datos
    - ✅ Idempotencia con TTL configurable
    - ✅ Persistencia en base de datos PostgreSQL
    - ✅ Tracking completo de progreso
    
    **Workflow automatizado:**
    1. Validación de datos de entrada
    2. Verificación de idempotencia
    3. Enriquecimiento desde HRIS (opcional)
    4. Creación de checklist automatizada
    5. Asignación de capacitaciones
    6. Provisionamiento de accesos
    7. Creación de cuentas (IdP, email, workspace)
    8. Creación de tareas en tracker
    9. Envío de email de bienvenida
    10. Registro de progreso y notificaciones
    
    **Parámetros:**
    - `employee_email`: Email del empleado (requerido)
    - `full_name`: Nombre completo (requerido)
    - `start_date`: Fecha de inicio YYYY-MM-DD (requerido)
    - `manager_email`: Email del manager (requerido)
    - `department`: Departamento (opcional, para personalización)
    - `role`: Rol/Cargo (opcional)
    
    **Base de datos:**
    Requiere que el esquema `employee_onboarding_schema.sql` esté ejecutado.
    
    **Disparo automático:**
    Puede dispararse manualmente desde Airflow UI o automáticamente vía webhook/API cuando se contrata un nuevo empleado.
    """,
    params={
        "employee_email": Param("", type="string", description="Email del empleado (requerido)"),
        "full_name": Param("", type="string", description="Nombre completo (requerido)"),
        "start_date": Param("", type="string", description="Fecha de inicio YYYY-MM-DD (requerido)"),
        "manager_email": Param("", type="string", description="Email del manager (requerido)"),
        "department": Param("", type="string", description="Departamento"),
        "role": Param("", type="string", description="Rol/Cargo"),
        "location": Param("", type="string", description="Ubicación/Oficina"),
        "phone": Param("", type="string", description="Teléfono"),
        "send_welcome": Param(True, type="boolean", description="Enviar email de bienvenida"),
        "create_issue_tracker_tasks": Param(True, type="boolean", description="Crear tareas en tracker"),
        "hris_lookup": Param(True, type="boolean", description="Buscar datos adicionales en HRIS"),
        "idempotency_key": Param("", type="string", description="Clave de idempotencia personalizada"),
        "idempotency_ttl_hours": Param(24, type="integer", minimum=1, maximum=168, description="TTL del lock de idempotencia (horas)"),
        "create_contract": Param(True, type="boolean", description="Crear contrato laboral automáticamente"),
        "contract_template_id": Param("employment_contract_v1", type="string", description="ID de plantilla de contrato"),
        "contract_esignature_provider": Param("docusign", type="string", description="Proveedor de firma: docusign, pandadoc, manual"),
    },
    description="Automated onboarding orchestration with HRIS integration and robust validation",
    tags=["onboarding", "it", "hr", "automation"],
    dagrun_timeout=timedelta(minutes=30),
    max_active_runs=1,
    max_active_tasks=MAX_ACTIVE_TASKS,
    concurrency=8,
    sla_miss_callback=sla_miss_callback,
    render_template_as_native_obj=True,
    on_success_callback=lambda context: notify_slack(":white_check_mark: employee_onboarding DAG succeeded"),
    on_failure_callback=lambda context: notify_slack(":x: employee_onboarding DAG failed"),
)
def employee_onboarding() -> None:
    logger = logging.getLogger("airflow.task")

    @task(task_id="validate_input", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def validate_input() -> Dict[str, Any]:
        """Validación robusta de parámetros de entrada."""
        ctx = get_current_context()
        params = dict(ctx.get("params", {}))
        
        logger.info(
            "validating onboarding params",
            extra={
                "params": {k: v for k, v in params.items() if k not in ["idempotency_key", "idempotency_ttl_hours"]},
                "dag_run_id": ctx.get("run_id"),
            },
        )
        
        if Stats:
            try:
                Stats.incr("onboarding.validate_input.start", 1)
            except Exception:
                pass
        
        validated = _validate_employee(params)
        
        if Stats:
            try:
                Stats.incr("onboarding.validate_input.success", 1)
            except Exception:
                pass
        
        return validated

    @task(task_id="idempotency_lock", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL)
    def idempotency_lock(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Bloqueo idempotente con TTL configurable."""
        ctx = get_current_context()
        dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "employee_onboarding"
        run_id = ctx.get("run_id")
        
        # Generar clave estable de idempotencia
        idem = str(
            payload.get("idempotency_key")
            or f"{payload['employee_email']}:{payload.get('start_date', '')}"
        )
        lock_key = f"idemp:{dag_id}:{idem}"
        ttl_h = int(payload.get("idempotency_ttl_hours", 24))
        
        existing = Variable.get(lock_key, default_var=None)
        if existing:
            logger.warning(
                "idempotency lock hit; skipping run",
                extra={
                    "key": lock_key,
                    "employee_email": payload.get("employee_email"),
                    "ttl_hours": ttl_h,
                },
            )
            if Stats:
                try:
                    Stats.incr("onboarding.idempotency_lock.hit", 1)
                except Exception:
                    pass
            raise AirflowFailException("Duplicate onboarding run detected (idempotency lock active)")
        
        Variable.set(lock_key, str(ttl_h))
        logger.info(
            "idempotency lock acquired",
            extra={"key": lock_key, "ttl_hours": ttl_h, "employee_email": payload.get("employee_email")},
        )
        
        if Stats:
            try:
                Stats.incr("onboarding.idempotency_lock.success", 1)
            except Exception:
                pass
        
        return payload

    @task(task_id="hris_prefetch", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=0)
    def hris_prefetch_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquecimiento opcional de datos desde HRIS."""
        if not bool(payload.get("hris_lookup", True)):
            logger.info("hris_lookup disabled, skipping HRIS prefetch", extra={"employee_email": payload.get("employee_email")})
            return payload
        
        if Stats:
            try:
                Stats.incr("onboarding.hris_prefetch.start", 1)
            except Exception:
                pass
        
        result = hris_prefetch(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.hris_prefetch.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="create_checklist", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=1)
    def create_checklist(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Crea checklist automatizada de tareas de onboarding."""
        if Stats:
            try:
                Stats.incr("onboarding.create_checklist.start", 1)
            except Exception:
                pass
        
        result = create_onboarding_checklist(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.create_checklist.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="create_contract", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=1)
    def create_contract_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Crea contrato laboral automáticamente si está habilitado."""
        if not bool(payload.get("create_contract", True)):
            logger.info("contract creation disabled, skipping", extra={"employee_email": payload.get("employee_email")})
            return payload
        
        if not CONTRACT_MANAGEMENT_AVAILABLE:
            logger.warning("contract management not available, skipping", extra={"employee_email": payload.get("employee_email")})
            return payload
        
        if Stats:
            try:
                Stats.incr("onboarding.create_contract.start", 1)
            except Exception:
                pass
        
        try:
            result = create_contract_for_employee_onboarding(
                employee_email=payload.get("employee_email"),
                employee_name=payload.get("full_name"),
                start_date=payload.get("start_date"),
                manager_email=payload.get("manager_email"),
                department=payload.get("department"),
                position=payload.get("role"),
                template_id=payload.get("contract_template_id", "employment_contract_v1"),
                auto_send_for_signature=bool(payload.get("create_contract", True)),
                esignature_provider=payload.get("contract_esignature_provider", "docusign")
            )
            
            if Stats:
                try:
                    Stats.incr("onboarding.create_contract.success", 1)
                except Exception:
                    pass
            
            return {**payload, "contract_id": result.get("contract_id"), "contract_created": True}
        except Exception as e:
            logger.error(f"Error creando contrato durante onboarding: {e}", extra={"employee_email": payload.get("employee_email")})
            if Stats:
                try:
                    Stats.incr("onboarding.create_contract.failed", 1)
                except Exception:
                    pass
            # No fallar el onboarding completo si falla el contrato
            return {**payload, "contract_created": False, "contract_error": str(e)}

    @task(task_id="assign_trainings", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=1)
    def assign_trainings_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Asigna capacitaciones automáticamente."""
        if Stats:
            try:
                Stats.incr("onboarding.assign_trainings.start", 1)
            except Exception:
                pass
        
        result = assign_trainings(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.assign_trainings.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="provision_accesses", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=1)
    def provision_accesses_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Provisiona accesos automáticamente."""
        if Stats:
            try:
                Stats.incr("onboarding.provision_accesses.start", 1)
            except Exception:
                pass
        
        result = provision_accesses(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.provision_accesses.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="create_accounts", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def create_accounts(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creación de cuentas en IdP, email y workspace."""
        if Stats:
            try:
                Stats.incr("onboarding.create_accounts.start", 1)
            except Exception:
                pass
        
        result = create_idp_and_workspace_accounts(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.create_accounts.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="assign_tasks", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def assign_tasks(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Asignación de tareas en tracker de proyectos."""
        if not bool(payload.get("create_issue_tracker_tasks", True)):
            logger.info("task creation disabled, skipping", extra={"employee_email": payload.get("employee_email")})
            return payload
        
        if Stats:
            try:
                Stats.incr("onboarding.assign_tasks.start", 1)
            except Exception:
                pass
        
        result = assign_project_and_it_tasks(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.assign_tasks.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="send_docs", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=2)
    def send_docs(payload: Dict[str, Any]) -> Dict[str, Any]:
        """Envío de email de bienvenida y documentación."""
        if not bool(payload.get("send_welcome", True)):
            logger.info("welcome email disabled, skipping", extra={"employee_email": payload.get("employee_email")})
            return payload
        
        if Stats:
            try:
                Stats.incr("onboarding.send_docs.start", 1)
            except Exception:
                pass
        
        result = send_welcome_and_docs(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.send_docs.success", 1)
            except Exception:
                pass
        
        return {**payload, **result}

    @task(task_id="track_progress", on_failure_callback=on_task_failure, pool=ONBOARDING_POOL, retries=0)
    def track_progress(payload: Dict[str, Any]) -> None:
        """Registro de progreso y notificaciones."""
        record_progress_and_notify(payload)
        
        if Stats:
            try:
                Stats.incr("onboarding.completed", 1)
            except Exception:
                pass
        
        logger.info(
            "onboarding completed successfully",
            extra={
                "employee_email": payload.get("employee_email"),
                "accounts_created": bool(payload.get("idp_user_id")),
                "tasks_created": bool(payload.get("tasks")),
                "welcome_sent": bool(payload.get("welcome_sent")),
            },
        )
        
        return None

    # Define task flow
    validated = validate_input()
    locked = idempotency_lock(validated)
    enriched = hris_prefetch_task(locked)
    
    # Crear checklist, crear contrato y asignar capacitaciones (pueden ejecutarse en paralelo)
    checklist_result = create_checklist(enriched)
    contract_result = create_contract_task(enriched)
    trainings_result = assign_trainings_task(enriched)
    accesses_result = provision_accesses_task(enriched)
    
    # Combinar resultados para siguiente paso
    @task(task_id="merge_checklist_contract_trainings_accesses", pool=ONBOARDING_POOL)
    def merge_results(checklist: Dict[str, Any], contract: Dict[str, Any], trainings: Dict[str, Any], accesses: Dict[str, Any]) -> Dict[str, Any]:
        """Combina resultados de checklist, contract, trainings y accesses."""
        merged = {**checklist}
        merged.update({k: v for k, v in contract.items() if k not in merged})
        merged.update({k: v for k, v in trainings.items() if k not in merged})
        merged.update({k: v for k, v in accesses.items() if k not in merged})
        return merged
    
    merged = merge_results(checklist_result, contract_result, trainings_result, accesses_result)
    
    # Crear cuentas después de que se hayan creado las estructuras base
    accounts = create_accounts(merged)
    
    # Crear tareas en tracker y enviar docs
    tasks = assign_tasks(accounts)
    docs = send_docs(tasks)
    
    # Tracking final
    track_progress(docs)
    
    return None


dag = employee_onboarding()
